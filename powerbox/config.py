from __future__ import annotations

from pathlib import Path

from .models import AppConfig, EncoderConfig
from .user_settings import (
	AAC_BITRATE_KBPS,
	EXPORT_ROOT,
	MASTER_DB_PATH,
	SOURCE_CODECS_TO_SKIP_REENCODE,
	SOURCE_PATH_MAPPINGS,
	SQLCIPHER_KEY,
)


def _required_value(name: str, value: str) -> str:
	stripped = value.strip()
	if not stripped:
		raise ValueError(f"Missing required config value: {name}")
	return stripped


def _parse_source_path_mappings() -> tuple[tuple[str, Path], ...]:
	mappings: list[tuple[str, Path]] = []
	for index, (source_prefix, mirror_root) in enumerate(SOURCE_PATH_MAPPINGS):
		prefix = source_prefix.strip()
		root = mirror_root.strip()
		if not prefix or not root:
			raise ValueError(
				f"Invalid SOURCE_PATH_MAPPINGS entry at index {index}: both values are required"
			)
		mappings.append((prefix, Path(root)))

	return tuple(mappings)


def _parse_source_codecs_to_skip_reencode() -> tuple[str, ...]:
	codecs: list[str] = []
	for index, value in enumerate(SOURCE_CODECS_TO_SKIP_REENCODE):
		if not isinstance(value, str):
			raise ValueError(
				"Invalid SOURCE_CODECS_TO_SKIP_REENCODE entry at "
				f"index {index}: value must be a string"
			)
		normalized = value.strip().lower()
		if not normalized:
			raise ValueError(
				"Invalid SOURCE_CODECS_TO_SKIP_REENCODE entry at "
				f"index {index}: value cannot be empty"
			)
		codecs.append(normalized)

	# Preserve declaration order while deduplicating.
	return tuple(dict.fromkeys(codecs))


def load_config() -> AppConfig:
	sqlcipher_key = _required_value("SQLCIPHER_KEY", SQLCIPHER_KEY)
	master_db_path = Path(_required_value("MASTER_DB_PATH", MASTER_DB_PATH))
	source_path_mappings = _parse_source_path_mappings()
	export_root = Path(_required_value("EXPORT_ROOT", EXPORT_ROOT))
	source_codecs_to_skip_reencode = _parse_source_codecs_to_skip_reencode()

	bitrate_kbps = int(AAC_BITRATE_KBPS)

	encoder = EncoderConfig(
		bitrate_kbps=bitrate_kbps,
	)
	return AppConfig(
		sqlcipher_key=sqlcipher_key,
		master_db_path=master_db_path,
		source_path_mappings=source_path_mappings,
		export_root=export_root,
		encoder=encoder,
		source_codecs_to_skip_reencode=source_codecs_to_skip_reencode,
	)
