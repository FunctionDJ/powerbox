from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
	from pathlib import Path

MUSIC_SUBDIR = "music"
PLAYLISTS_SUBDIR = "playlists"
MANIFEST_NAME = ".powerbox-manifest.json"


# TODO replace this class with a variable
@dataclass(frozen=True)
class EncoderConfig:
	bitrate_kbps: int

	@property
	def fingerprint(self) -> str:
		payload: dict[str, str | int] = {
			"bitrate_kbps": self.bitrate_kbps,
		}
		encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
		return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class AppConfig:
	sqlcipher_key: str
	master_db_path: Path
	source_path_mappings: tuple[tuple[str, Path], ...]
	export_root: Path
	encoder: EncoderConfig


@dataclass
class TrackPlan:
	content_id: str
	source_path: Path
	output_relpath: Path


@dataclass
class PlaylistPlan:
	playlist_id: str
	name: str
	output_relpath: Path
	tracks: list[TrackPlan]


class TrackSignature(TypedDict):
	source_path: str
	size: int
	mtime_ns: int


class TrackManifestEntry(TrackSignature):
	encoder_fingerprint: str
	output_path: str


class PlaylistManifestEntry(TypedDict):
	name: str
	output_path: str
	track_count: int


class ManagedFilesManifest(TypedDict):
	audio: list[str]
	playlists: list[str]


class ManifestData(TypedDict, total=False):
	version: int
	encoder_fingerprint: str
	tracks: dict[str, TrackManifestEntry]
	playlists: dict[str, PlaylistManifestEntry]
	managed_files: ManagedFilesManifest
	skipped_smart_playlists: list[str]
