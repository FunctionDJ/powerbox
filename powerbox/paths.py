from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from .models import MUSIC_SUBDIR

if TYPE_CHECKING:
	from collections.abc import Sequence


def sanitize_name(name: str) -> str:
	sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", name).strip(" .")
	return sanitized or "unnamed"


def normalize_windows_path(path: str) -> str:
	return path.replace("\\", "/")


def map_source_path(db_path: str, source_path_mappings: Sequence[tuple[str, Path]]) -> Path:
	normalized = normalize_windows_path(db_path)

	for source_prefix, mirror_root in source_path_mappings:
		normalized_prefix = normalize_windows_path(source_prefix).rstrip("/")
		if not normalized_prefix:
			continue

		if normalized.lower() == normalized_prefix.lower():
			return mirror_root

		prefix_with_sep = normalized_prefix + "/"
		if normalized.lower().startswith(prefix_with_sep.lower()):
			relative = normalized[len(prefix_with_sep) :].lstrip("/")
			return mirror_root.joinpath(*PurePosixPath(relative).parts)

	if normalized.startswith("/"):
		return Path(normalized)

	return Path(normalized)


def build_track_output_relpath(source_path: Path, content_id: str) -> Path:
	stem = sanitize_name(source_path.stem)
	return Path(MUSIC_SUBDIR, f"{stem}__{content_id}.m4a")
