from __future__ import annotations

import argparse
import logging
import time

from .exporter import run_export


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Minimal Rekordbox to Poweramp exporter")
	parser.add_argument("--dry-run", action="store_true", help="Plan work without writing files")
	parser.add_argument(
		"--log-level",
		default="INFO",
		choices=["DEBUG", "INFO", "WARNING", "ERROR"],
		help="Log verbosity",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	logging.basicConfig(
		level=getattr(logging, args.log_level),
	)
	started = time.monotonic()
	try:
		run_export(dry_run=args.dry_run)
	finally:
		elapsed_seconds = time.monotonic() - started
		logging.info("Total execution time: %.1f seconds", elapsed_seconds)
