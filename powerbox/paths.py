from __future__ import annotations

import re
import unicodedata
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from .models import MUSIC_SUBDIR

if TYPE_CHECKING:
	from collections.abc import Sequence


def sanitize_name(name: str) -> str:
	# Canonicalize Unicode to avoid filesystem/sync issues caused by equivalent UTF-8 forms.
	normalized = unicodedata.normalize("NFC", name)
	# Replace slash separators with comma-space before applying filesystem-safe sanitization.
	normalized = normalized.replace("/", ", ").replace("\\", ", ")
	sanitized = re.sub(r'[<>:"|?*\x00-\x1F]', "_", normalized).strip(" .")
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


def build_track_output_relpath(
	source_path: Path,
	content_id: str,
	artist: str | None,
	title: str | None,
) -> Path:
	if artist and title:
		base = f"{sanitize_name(artist)} - {sanitize_name(title)}"
	else:
		base = sanitize_name(source_path.stem)

	return Path(MUSIC_SUBDIR, f"{base} - {content_id}.m4a")
