#!/usr/bin/env python3
"""Preflight self-hosted recording fonts before an overnight capture queue.

Loads one exhibition page and runs the Noto Serif JP + Yuji Syuku gates.
Exits non-zero on any load / fallback failure so the batch can abort cleanly.

Usage:
  python3 scripts/preflight_recording_fonts.py --collection lesson_26_strokes --port 8770
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    preflight_recording_fonts,
    preflight_recording_png_pipeline,
    start_server,
    stop_server,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--collection",
        default="lesson_26_strokes",
        help="Collection id to load for the font gate (default: lesson_26_strokes)",
    )
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--no-server", action="store_true", help="Assume a server is already up")
    parser.add_argument(
        "--png-pipeline",
        action="store_true",
        help="Also assert recordPipeline rewrites study JPEGs to PNG masters",
    )
    args = parser.parse_args()

    server = None
    if not args.no_server:
        server = start_server(ROOT, args.port)
    try:
        preflight_recording_fonts(
            root=ROOT,
            port=args.port,
            collection=args.collection,
        )
        if args.png_pipeline:
            preflight_recording_png_pipeline(
                root=ROOT,
                port=args.port,
                collection=args.collection,
            )
    except Exception as exc:
        print(f"PREFLIGHT FAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        if server is not None:
            stop_server(server)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
