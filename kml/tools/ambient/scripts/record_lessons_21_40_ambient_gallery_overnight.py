#!/usr/bin/env python3
"""Overnight: record Ambient Movie — Lessons 21–40 (single long film).

Usage:
  cd kml/tools/ambient
  nohup .venv/bin/python scripts/record_lessons_21_40_ambient_gallery_overnight.py \\
    > extended_exhibitions/lessons_21_40_overnight.log 2>&1 &

  # rebuild JSON first:
  nohup .venv/bin/python scripts/record_lessons_21_40_ambient_gallery_overnight.py --rebuild \\
    > extended_exhibitions/lessons_21_40_overnight.log 2>&1 &
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "extended_exhibitions" / "lessons_21_40_overnight.log"
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
DEFAULT_PORT = 8772


def log(msg: str, log_file) -> None:
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    log_file.write(line + "\n")
    log_file.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log("=== Lessons 21–40 Ambient Movie (single film) overnight start ===", log_file)

        if args.rebuild:
            log("Rebuilding collection JSON…", log_file)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_lessons_21_40_ambient_gallery.py"),
                ],
                check=True,
                cwd=ROOT,
            )

        try:
            log(f"Starting record_lessons_21_40_ambient_gallery.py (port {args.port})", log_file)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_lessons_21_40_ambient_gallery.py"),
                    "--port",
                    str(args.port),
                ],
                check=True,
                cwd=ROOT,
            )
            log("OK lessons_21_40_ambient_gallery", log_file)
        except Exception:
            log(f"FAILED\n{traceback.format_exc()}", log_file)
            log("=== Overnight stopped with errors ===", log_file)
            return 1

        log("=== Overnight complete ===", log_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
