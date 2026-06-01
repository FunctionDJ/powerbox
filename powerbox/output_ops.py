from __future__ import annotations

import logging
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pathlib import Path

	from .models import AppConfig


def transcode_track(
	config: AppConfig,
	source_path: Path,
	output_path: Path,
	dry_run: bool,
) -> None:
	logging.debug("Convert via ffmpeg: %s -> %s", source_path, output_path)
	if dry_run:
		return

	if not output_path.parent.exists():
		logging.debug("Create folder: %s", output_path.parent)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	command = [
		"ffmpeg",
		"-y",
		"-threads",
		"1",
		"-i",
		str(source_path),
		"-c:a",
		"aac",
		"-c:v",
		"copy",
		"-b:a",
		f"{config.encoder.bitrate_kbps}k",
		str(output_path),
	]

	ffmpeg_timeout_seconds = 30 * 60
	try:
		subprocess.run(
			command,
			check=True,
			stdin=subprocess.DEVNULL,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.PIPE,
			text=True,
			timeout=ffmpeg_timeout_seconds,
		)
	except subprocess.TimeoutExpired as exc:
		stderr = (exc.stderr or "").strip()
		details = f"\n{stderr}" if stderr else ""
		raise RuntimeError(
			f"ffmpeg timed out after {ffmpeg_timeout_seconds}s for {source_path}{details}"
		) from exc
	except subprocess.CalledProcessError as exc:
		stderr = (exc.stderr or "").strip()
		raise RuntimeError(
			f"ffmpeg failed for {source_path}:\n{stderr or 'No stderr output'}"
		) from exc


def write_playlist_file(path: Path, lines: list[str], dry_run: bool) -> bool:
	payload = "\n".join(lines) + "\n"
	path_exists = path.exists()
	existing = None
	if path_exists:
		existing = path.read_text(encoding="utf-8")

	if existing == payload:
		return False

	logging.debug("%s playlist file: %s", "Update" if path_exists else "Create", path)
	if not dry_run:
		if not path.parent.exists():
			logging.info("Create folder: %s", path.parent)
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(payload, encoding="utf-8")
	return True


def remove_stale_managed_files(export_root: Path, stale_files: set[str], dry_run: bool) -> int:
	removed = 0
	export_root_resolved = export_root.resolve()
	for relpath in sorted(stale_files):
		absolute = (export_root / relpath).resolve()
		try:
			absolute.relative_to(export_root_resolved)
		except ValueError:
			logging.warning(
				"Refusing to remove path outside export root: %s (root: %s)",
				absolute,
				export_root_resolved,
			)
			continue
		if not absolute.exists():
			continue
		logging.info("Removing stale managed file: %s", absolute)
		if not dry_run:
			absolute.unlink()
		removed += 1
	return removed
