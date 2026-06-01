from __future__ import annotations

import logging
from pathlib import Path

from pyrekordbox.db6.database import Rekordbox6Database  # pyright: ignore[reportMissingTypeStubs]
from pyrekordbox.db6.tables import (  # pyright: ignore[reportMissingTypeStubs]
	DjmdContent,
	DjmdPlaylist,
	DjmdSongPlaylist,
)

from .models import PLAYLISTS_SUBDIR, AppConfig, PlaylistPlan, TrackPlan
from .paths import build_track_output_relpath, map_source_path, sanitize_name


def _is_deleted_row(row: object) -> bool:
	# Rekordbox keeps soft-deleted rows and marks them with rb_local_deleted.
	return bool(getattr(row, "rb_local_deleted", 0))


def discover_playlists(config: AppConfig) -> tuple[list[PlaylistPlan], set[str]]:
	playlist_plans: list[PlaylistPlan] = []
	skipped_smart: set[str] = set()
	skipped_deleted_playlist_songs = 0
	skipped_deleted_content = 0

	with Rekordbox6Database(path=str(config.master_db_path), key=config.sqlcipher_key) as db:
		all_playlists_raw: list[DjmdPlaylist] = list(db.get_playlist().all())
		all_playlists = [
			playlist for playlist in all_playlists_raw if not _is_deleted_row(playlist)
		]
		by_id = {playlist.ID: playlist for playlist in all_playlists}
		playlist_output_owner: dict[Path, str] = {}

		track_output_by_source: dict[Path, Path] = {}

		sorted_playlists = sorted(
			all_playlists,
			key=lambda item: (item.Seq or 0, item.Name or "", item.ID),
		)

		for playlist in sorted_playlists:
			if playlist.is_folder:
				continue

			folder_parts = playlist_folder_parts(playlist, by_id)
			playlist_name = sanitize_name(playlist.Name)
			playlist_file = Path(PLAYLISTS_SUBDIR, *folder_parts, f"{playlist_name}.m3u8")
			owner = playlist_output_owner.get(playlist_file)
			if owner is not None and owner != playlist.ID:
				playlist_file = Path(
					PLAYLISTS_SUBDIR,
					*folder_parts,
					f"{playlist_name}__{playlist.ID}.m3u8",
				)
			playlist_output_owner[playlist_file] = playlist.ID

			tracks: list[TrackPlan] = []
			try:
				if playlist.is_smart_playlist:
					contents_raw = list(
						db.get_playlist_contents(playlist)
						.order_by(DjmdContent.Title, DjmdContent.ID)
						.all()
					)
					contents = [content for content in contents_raw if not _is_deleted_row(content)]
					skipped_deleted_content += len(contents_raw) - len(contents)
				else:
					playlist_songs_raw = list(
						db.get_playlist_songs(PlaylistID=playlist.ID)
						.order_by(DjmdSongPlaylist.TrackNo, DjmdSongPlaylist.ID)
						.all()
					)
					playlist_songs = [
						item for item in playlist_songs_raw if not _is_deleted_row(item)
					]
					skipped_deleted_playlist_songs += len(playlist_songs_raw) - len(playlist_songs)
					contents: list[DjmdContent] = []
					for item in playlist_songs:
						content = item.Content
						if content is None:
							continue
						if _is_deleted_row(content):
							skipped_deleted_content += 1
							continue
						contents.append(content)
			except Exception as exc:
				if playlist.is_smart_playlist:
					skipped_smart.add(f"{playlist.ID}:{playlist.Name}")
					logging.warning(
						"Skipping smart playlist %s (%s): %s",
						playlist.Name,
						playlist.ID,
						exc,
					)
					continue
				raise

			for content in contents:
				source = map_source_path(
					content.FolderPath,
					config.source_path_mappings,
				)
				output_relpath = track_output_by_source.get(source)
				if output_relpath is None:
					output_relpath = build_track_output_relpath(source, content.ID)
					track_output_by_source[source] = output_relpath

				tracks.append(
					TrackPlan(
						content_id=content.ID,
						source_path=source,
						output_relpath=output_relpath,
					)
				)

			playlist_plans.append(
				PlaylistPlan(
					playlist_id=playlist.ID,
					name=playlist.Name,
					output_relpath=playlist_file,
					tracks=tracks,
				)
			)

	return playlist_plans, skipped_smart


def playlist_folder_parts(playlist: DjmdPlaylist, by_id: dict[str, DjmdPlaylist]) -> list[str]:
	parts: list[str] = []
	parent_id = playlist.ParentID

	while parent_id and parent_id in by_id:
		parent = by_id[parent_id]
		if parent.is_folder:
			parts.append(sanitize_name(parent.Name))
		parent_id = parent.ParentID

	parts.reverse()
	return parts
