from __future__ import annotations

import json
import logging
import os
import subprocess
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING

from .config import load_config
from .discovery import discover_playlists
from .manifest import get_track_signature
from .models import (
	MANIFEST_NAME,
	MUSIC_SUBDIR,
	PLAYLISTS_SUBDIR,
	ManifestData,
	PlaylistManifestEntry,
	TrackManifestEntry,
)
from .output_ops import (
	copy_track_file,
	detect_audio_codec,
	remove_stale_managed_files,
	set_file_mtime_from_date,
	transcode_track,
	write_playlist_file,
)

if TYPE_CHECKING:
	from pathlib import Path


def _list_existing_files_under_subdir(export_root: Path, subdir: str) -> set[str]:
	base = export_root / subdir
	if not base.exists():
		return set()

	results: set[str] = set()
	for path in base.rglob("*"):
		if not path.is_file():
			continue
		results.add(path.relative_to(export_root).as_posix())
	return results


def run_export(dry_run: bool) -> None:
	config = load_config()

	subprocess.run(
		["ffmpeg", "-version"],
		check=True,
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	)

	manifest_path = config.export_root / MANIFEST_NAME

	playlist_plans, skipped_smart = discover_playlists(config)
	logging.info("Discovered playlists: %d", len(playlist_plans))

	current_track_manifest: dict[str, TrackManifestEntry] = {}
	managed_audio: set[str] = set()

	unique_tracks: dict[Path, Path] = {}
	track_stock_dates: dict[Path, str] = {}
	output_owners: dict[Path, Path] = {}
	for playlist in playlist_plans:
		for track in playlist.tracks:
			unique_tracks.setdefault(track.source_path, track.output_relpath)
			track_stock_dates.setdefault(track.source_path, track.stock_date)

	logging.debug("Unique source tracks to process: %d", len(unique_tracks))

	encoded_count = 0
	skipped_unchanged_count = 0
	skipped_missing_source_count = 0

	# Pre-pass: determine which tracks need work and populate the manifest.
	# Tracks that are missing or unchanged are handled immediately; encode tasks
	# are collected for parallel execution below.
	encode_tasks: list[tuple[Path, Path, str]] = []  # (source_path, output_path, stock_date)
	copy_tasks: list[tuple[Path, Path, str]] = []  # (source_path, output_path, stock_date)
	source_codecs_to_skip = set(config.source_codecs_to_skip_reencode)
	if source_codecs_to_skip:
		logging.info(
			"Configured to skip re-encode for source codec(s): %s",
			", ".join(sorted(source_codecs_to_skip)),
		)

	for source_path, output_relpath in sorted(unique_tracks.items(), key=lambda item: str(item[0])):
		if not source_path.exists():
			logging.debug("Source file missing, skipping: %s", source_path)
			skipped_missing_source_count += 1
			continue

		source_codec = detect_audio_codec(source_path)
		effective_output_relpath = output_relpath
		if source_codec is not None and source_codec in source_codecs_to_skip:
			effective_output_relpath = output_relpath.with_suffix(source_path.suffix.lower())

		owner = output_owners.get(effective_output_relpath)
		if owner is not None and owner != source_path:
			raise RuntimeError(
				f"Output path conflict while processing: {effective_output_relpath} "
				f"for {owner} and {source_path}"
			)
		output_owners[effective_output_relpath] = source_path

		signature = get_track_signature(source_path)
		output_path = config.export_root / effective_output_relpath
		stock_date = track_stock_dates.get(source_path, "")

		# If the destination file is already present, treat it as completed.
		needs_encode = not output_path.exists()

		current_track_manifest[str(source_path)] = {
			**signature,
			"encoder_fingerprint": config.encoder.fingerprint,
			"output_path": str(effective_output_relpath),
		}
		managed_audio.add(str(effective_output_relpath))

		if needs_encode:
			if source_codec is not None and source_codec in source_codecs_to_skip:
				copy_tasks.append((source_path, output_path, stock_date))
			else:
				encode_tasks.append((source_path, output_path, stock_date))
		else:
			logging.debug("Destination exists, skipping write: %s", output_path)
			skipped_unchanged_count += 1
			if not dry_run:
				set_file_mtime_from_date(output_path, stock_date)

	# Parallel encoding pass.
	workers = os.cpu_count() or 1
	logging.info(
		"Writing tracks with %d parallel worker(s): encode=%d copy_without_reencode=%d",
		workers,
		len(encode_tasks),
		len(copy_tasks),
	)

	work_tasks: list[tuple[str, Path, Path, str]] = []
	for src, out, stock_date in encode_tasks:
		work_tasks.append(("encode", src, out, stock_date))
	for src, out, stock_date in copy_tasks:
		work_tasks.append(("copy", src, out, stock_date))

	if work_tasks:
		total = len(work_tasks)
		width = len(str(total))
		done = 0
		errors: list[str] = []
		with ThreadPoolExecutor(max_workers=workers) as executor:
			future_to_task: dict[Future[None], tuple[str, Path, Path, str]] = {}
			for mode, src, out, stock_date in work_tasks:
				if mode == "copy":
					future = executor.submit(copy_track_file, src, out, dry_run)
				else:
					future = executor.submit(transcode_track, config, src, out, dry_run)
				future_to_task[future] = (mode, src, out, stock_date)
			for future in as_completed(future_to_task):
				mode, src, out, stock_date = future_to_task[future]
				done += 1
				pct = done * 100 // total
				try:
					future.result()
					encoded_count += 1
					if not dry_run:
						set_file_mtime_from_date(out, stock_date)
					if mode == "copy":
						logging.debug(
							"[%*d/%d (%3d%%)] Copied without re-encode: %s",
							width,
							done,
							total,
							pct,
							src.name,
						)
					else:
						logging.debug(
							"[%*d/%d (%3d%%)] Encoded: %s",
							width,
							done,
							total,
							pct,
							src.name,
						)
				except Exception as exc:
					logging.error(
						"[%*d/%d (%3d%%)] FAILED (%s): %s: %s",
						width,
						done,
						total,
						pct,
						mode,
						src,
						exc,
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

	existing_audio = _list_existing_files_under_subdir(config.export_root, MUSIC_SUBDIR)
	existing_playlists = _list_existing_files_under_subdir(config.export_root, PLAYLISTS_SUBDIR)

	stale_audio = existing_audio - managed_audio
	stale_playlists = existing_playlists - managed_playlists

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
