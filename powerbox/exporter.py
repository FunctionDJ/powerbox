from __future__ import annotations

import json
import logging
import os
import subprocess
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING

from .config import load_config
from .discovery import discover_playlists
from .manifest import get_track_signature, load_manifest
from .models import MANIFEST_NAME, ManifestData, PlaylistManifestEntry, TrackManifestEntry
from .output_ops import remove_stale_managed_files, transcode_track, write_playlist_file

if TYPE_CHECKING:
	from pathlib import Path


def run_export(dry_run: bool) -> None:
	config = load_config()

	subprocess.run(
		["ffmpeg", "-version"],
		check=True,
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	)

	manifest_path = config.export_root / MANIFEST_NAME
	previous_manifest = load_manifest(manifest_path)
	previous_managed = previous_manifest.get("managed_files", {"audio": [], "playlists": []})

	playlist_plans, skipped_smart = discover_playlists(config)
	logging.info("Discovered playlists: %d", len(playlist_plans))

	current_track_manifest: dict[str, TrackManifestEntry] = {}
	managed_audio: set[str] = set()

	unique_tracks: dict[Path, Path] = {}
	output_owners: dict[Path, Path] = {}
	for playlist in playlist_plans:
		for track in playlist.tracks:
			owner = output_owners.get(track.output_relpath)
			if owner is not None and owner != track.source_path:
				raise RuntimeError(
					f"Output path conflict while processing: {track.output_relpath} "
					f"for {owner} and {track.source_path}"
				)
			output_owners[track.output_relpath] = track.source_path
			unique_tracks.setdefault(track.source_path, track.output_relpath)

	logging.debug("Unique source tracks to process: %d", len(unique_tracks))

	encoded_count = 0
	skipped_unchanged_count = 0
	skipped_missing_source_count = 0

	# Pre-pass: determine which tracks need encoding and populate the manifest.
	# Tracks that are missing or unchanged are handled immediately; encode tasks
	# are collected for parallel execution below.
	encode_tasks: list[tuple[Path, Path]] = []  # (source_path, output_path)

	for source_path, output_relpath in sorted(unique_tracks.items(), key=lambda item: str(item[0])):
		if not source_path.exists():
			logging.debug("Source file missing, skipping: %s", source_path)
			skipped_missing_source_count += 1
			continue

		signature = get_track_signature(source_path)
		output_path = config.export_root / output_relpath

		# If the destination file is already present, treat it as completed.
		needs_encode = not output_path.exists()

		current_track_manifest[str(source_path)] = {
			**signature,
			"encoder_fingerprint": config.encoder.fingerprint,
			"output_path": str(output_relpath),
		}
		managed_audio.add(str(output_relpath))

		if needs_encode:
			encode_tasks.append((source_path, output_path))
		else:
			logging.debug("Destination exists, skipping encode: %s", output_path)
			skipped_unchanged_count += 1

	# Parallel encoding pass.
	workers = os.cpu_count() or 1
	logging.info("Encoding %d track(s) with %d parallel worker(s)", len(encode_tasks), workers)

	if encode_tasks:
		total = len(encode_tasks)
		width = len(str(total))
		done = 0
		errors: list[str] = []
		with ThreadPoolExecutor(max_workers=workers) as executor:
			future_to_src: dict[Future[None], Path] = {
				executor.submit(transcode_track, config, src, out, dry_run): src
				for src, out in encode_tasks
			}
			for future in as_completed(future_to_src):
				src = future_to_src[future]
				done += 1
				pct = done * 100 // total
				try:
					future.result()
					encoded_count += 1
					logging.debug("[%*d/%d (%3d%%)] Encoded: %s", width, done, total, pct, src.name)
				except Exception as exc:
					logging.error(
						"[%*d/%d (%3d%%)] FAILED: %s: %s", width, done, total, pct, src, exc
					)
					errors.append(f"{src}: {exc}")
		if errors:
			raise RuntimeError(f"{len(errors)} track(s) failed to encode:\n" + "\n".join(errors))

	current_playlist_manifest: dict[str, PlaylistManifestEntry] = {}
	managed_playlists: set[str] = set()
	playlists_written_count = 0
	playlists_unchanged_count = 0

	for playlist in playlist_plans:
		playlist_path = config.export_root / playlist.output_relpath
		entries: list[str] = []

		for track in playlist.tracks:
			track_entry = current_track_manifest.get(str(track.source_path))
			if track_entry is None:
				continue
			output_abs = config.export_root / track_entry["output_path"]
			rel = os.path.relpath(output_abs, start=playlist_path.parent)
			entries.append(rel.replace("\\", "/"))

		if write_playlist_file(playlist_path, entries, dry_run=dry_run):
			playlists_written_count += 1
		else:
			playlists_unchanged_count += 1

		current_playlist_manifest[playlist.playlist_id] = {
			"name": playlist.name,
			"output_path": str(playlist.output_relpath),
			"track_count": len(entries),
		}
		managed_playlists.add(str(playlist.output_relpath))

	previous_audio = set(previous_managed.get("audio", []))
	previous_playlists = set(previous_managed.get("playlists", []))

	stale_audio = previous_audio - managed_audio
	stale_playlists = previous_playlists - managed_playlists

	logging.info(
		"Stale files to remove: audio=%d playlists=%d",
		len(stale_audio),
		len(stale_playlists),
	)
	removed_audio_count = remove_stale_managed_files(
		config.export_root,
		stale_audio,
		dry_run=dry_run,
	)
	removed_playlist_count = remove_stale_managed_files(
		config.export_root,
		stale_playlists,
		dry_run=dry_run,
	)

	next_manifest: ManifestData = {
		"version": 1,
		"encoder_fingerprint": config.encoder.fingerprint,
		"tracks": current_track_manifest,
		"playlists": current_playlist_manifest,
		"managed_files": {
			"audio": sorted(managed_audio),
			"playlists": sorted(managed_playlists),
		},
		"skipped_smart_playlists": sorted(skipped_smart),
	}

	if dry_run:
		logging.info("Dry run complete. Manifest not written.")
	else:
		if not config.export_root.exists():
			logging.info("Create folder: %s", config.export_root)
		config.export_root.mkdir(parents=True, exist_ok=True)
		manifest_path.write_text(
			json.dumps(next_manifest, indent=2, sort_keys=True) + "\n",
			encoding="utf-8",
		)
		logging.info("Manifest updated: %s", manifest_path)

	logging.info(
		"Export summary: encoded=%d unchanged=%d missing_source=%d playlists_written=%d "
		"playlists_unchanged=%d removed_audio=%d removed_playlists=%d",
		encoded_count,
		skipped_unchanged_count,
		skipped_missing_source_count,
		playlists_written_count,
		playlists_unchanged_count,
		removed_audio_count,
		removed_playlist_count,
	)
