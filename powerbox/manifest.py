from __future__ import annotations

import json
from typing import TYPE_CHECKING, TypeGuard

if TYPE_CHECKING:
	from collections.abc import Mapping
	from pathlib import Path

	from .models import ManifestData, PlaylistManifestEntry, TrackManifestEntry, TrackSignature


def _is_object_dict(value: object) -> TypeGuard[dict[object, object]]:
	return isinstance(value, dict)


def _is_object_list(value: object) -> TypeGuard[list[object]]:
	return isinstance(value, list)


def _as_str_object_mapping(value: object) -> Mapping[str, object] | None:
	if not _is_object_dict(value):
		return None

	mapped: dict[str, object] = {}
	for key, item in value.items():
		if isinstance(key, str):
			mapped[key] = item
	return mapped


def _as_str_list(value: object) -> list[str]:
	if not _is_object_list(value):
		return []
	return [item for item in value if isinstance(item, str)]


def load_manifest(path: Path) -> ManifestData:
	if not path.exists():
		return {
			"version": 1,
			"tracks": {},
			"playlists": {},
			"managed_files": {"audio": [], "playlists": []},
		}

	with path.open("r", encoding="utf-8") as handle:
		raw_data = json.load(handle)

	raw = _as_str_object_mapping(raw_data)
	if raw is None:
		raise ValueError(f"Manifest must be a JSON object: {path}")

	version_raw = raw.get("version")
	version = version_raw if isinstance(version_raw, int) else 1

	tracks: dict[str, TrackManifestEntry] = {}
	tracks_raw = _as_str_object_mapping(raw.get("tracks"))
	if tracks_raw is not None:
		for key, value in tracks_raw.items():
			entry = _as_str_object_mapping(value)
			if entry is None:
				continue

			source_path = entry.get("source_path")
			size = entry.get("size")
			mtime_ns = entry.get("mtime_ns")
			encoder_fingerprint = entry.get("encoder_fingerprint")
			output_path = entry.get("output_path")
			if (
				isinstance(source_path, str)
				and isinstance(size, int)
				and isinstance(mtime_ns, int)
				and isinstance(encoder_fingerprint, str)
				and isinstance(output_path, str)
			):
				tracks[key] = {
					"source_path": source_path,
					"size": size,
					"mtime_ns": mtime_ns,
					"encoder_fingerprint": encoder_fingerprint,
					"output_path": output_path,
				}

	playlists: dict[str, PlaylistManifestEntry] = {}
	playlists_raw = _as_str_object_mapping(raw.get("playlists"))
	if playlists_raw is not None:
		for key, value in playlists_raw.items():
			entry = _as_str_object_mapping(value)
			if entry is None:
				continue

			name = entry.get("name")
			output_path = entry.get("output_path")
			track_count = entry.get("track_count")
			if (
				isinstance(name, str)
				and isinstance(output_path, str)
				and isinstance(track_count, int)
			):
				playlists[key] = {
					"name": name,
					"output_path": output_path,
					"track_count": track_count,
				}

	managed_raw = _as_str_object_mapping(raw.get("managed_files"))
	audio_values = _as_str_list(
		managed_raw.get("audio") if managed_raw is not None else None,
	)
	playlist_values = _as_str_list(
		managed_raw.get("playlists") if managed_raw is not None else None,
	)

	manifest: ManifestData = {
		"version": version,
		"tracks": tracks,
		"playlists": playlists,
		"managed_files": {
			"audio": audio_values,
			"playlists": playlist_values,
		},
	}
	return manifest


def get_track_signature(path: Path) -> TrackSignature:
	stat_result = path.stat()
	return {
		"source_path": str(path),
		"size": stat_result.st_size,
		"mtime_ns": stat_result.st_mtime_ns,
	}
