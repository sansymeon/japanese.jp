#!/usr/bin/env python3
"""Record a Quiet Cinematic Japan five-lesson film via Playwright.

Usage:
  python scripts/record_quiet_cinematic.py lessons_1_5_quiet_cinematic
  python scripts/record_quiet_cinematic.py lessons_6_10_quiet_cinematic --rebuild
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import record_lessons_21_25_quiet_cinematic as shared
from ambient_video_paths import QUIET_CINEMATIC

ROOT = Path(__file__).resolve().parents[1]
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
OUTPUT_DIR = QUIET_CINEMATIC

BUILDERS = {
    "lessons_1_5_quiet_cinematic": ("build_lessons_1_20_quiet_cinematic.py", "1-5"),
    "lessons_6_10_quiet_cinematic": ("build_lessons_1_20_quiet_cinematic.py", "6-10"),
    "lessons_11_15_quiet_cinematic": ("build_lessons_1_20_quiet_cinematic.py", "11-15"),
    "lessons_16_20_quiet_cinematic": ("build_lessons_1_20_quiet_cinematic.py", "16-20"),
}

DEFAULT_PORTS = {
    "lessons_1_5_quiet_cinematic": 8791,
    "lessons_6_10_quiet_cinematic": 8792,
    "lessons_11_15_quiet_cinematic": 8793,
    "lessons_16_20_quiet_cinematic": 8794,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection", choices=sorted(BUILDERS))
    parser.add_argument("--port", type=int)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()

    shared.COLLECTION_ID = args.collection
    shared.OUTPUT_DIR = args.output_dir
    shared.ensure_deps()

    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    if args.rebuild:
        script, block = BUILDERS[args.collection]
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script), block],
            check=True,
            cwd=ROOT,
        )

    port = args.port or DEFAULT_PORTS[args.collection]
    server = shared.start_server(ROOT, port)
    try:
        shared.record(port=port, output_dir=args.output_dir)
    finally:
        shared.stop_server(server)

    print(f"\nDone. MP4 in {args.output_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
