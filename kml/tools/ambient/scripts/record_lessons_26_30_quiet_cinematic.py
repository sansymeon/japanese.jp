#!/usr/bin/env python3
"""Record Quiet Cinematic Japan — Lessons 26–30 via Playwright."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import record_lessons_21_25_quiet_cinematic as shared

ROOT = Path(__file__).resolve().parents[1]
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
COLLECTION_ID = "lessons_26_30_quiet_cinematic"
OUTPUT_DIR = ROOT / "extended_exhibitions"
DEFAULT_PORT = 8772


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()

    shared.COLLECTION_ID = COLLECTION_ID
    shared.OUTPUT_DIR = args.output_dir
    shared.ensure_deps()

    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    if args.rebuild:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_lessons_26_30_quiet_cinematic.py"),
            ],
            check=True,
            cwd=ROOT,
        )

    server = shared.start_server(ROOT, args.port)
    try:
        shared.record(port=args.port, output_dir=args.output_dir)
    finally:
        shared.stop_server(server)

    print(f"\nDone. MP4 in {args.output_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
