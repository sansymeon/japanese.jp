#!/usr/bin/env python3
"""Record Grade 5 Compounds school edition MP4 via Playwright.

Output: collections/grade_5/grade_5_jukugo_{part}.mp4
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8774
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    compounds_school_soundtrack_start_ms,
    ensure_deps,
    load_collection,
    mux_exhibition_soundtrack,
    presentation_timeout_ms,
    start_server,
)
from grade5_compounds_school_common import PART_COUNT, collection_id  # noqa: E402


def record(*, part: int, port: int) -> Path:
    cid = collection_id(part)
    collection = load_collection(ROOT, cid)
    soundtrack_start_ms = compounds_school_soundtrack_start_ms(collection)
    timeout_ms = presentation_timeout_ms(collection, ROOT)

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    url = f"http://127.0.0.1:{port}/exhibition.html?collection={cid}"
    out_path = ROOT / "collections" / "grade_5" / f"grade_5_jukugo_{part}.mp4"
    tmp_dir = out_path.parent / f".tmp_grade_5_jukugo_{part}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {cid} → {out_path.name}")
    print(f"  soundtrack @ {soundtrack_start_ms}ms")

    webm = capture_exhibition_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    tmp_mux = tmp_dir / "muxed.mp4"
    mux_exhibition_soundtrack(
        webm=webm,
        output_mp4=tmp_mux,
        soundtrack=soundtrack,
        soundtrack_start_ms=soundtrack_start_ms,
    )
    shutil.move(str(tmp_mux), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()

    print(f"  → {out_path}")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", type=int, choices=range(1, PART_COUNT + 1))
    parser.add_argument("--all", action="store_true", help=f"Record parts 1–{PART_COUNT}")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()

    if not args.part and not args.all:
        parser.error("Specify --part N or --all")

    ensure_deps()

    if PLAYWRIGHT_BROWSERS.is_dir():
        import os

        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    parts = list(range(1, PART_COUNT + 1)) if args.all else [args.part]

    if args.rebuild:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_grade_5_compounds_school.py"), "--all"],
            check=True,
            cwd=ROOT,
        )

    server = start_server(ROOT, args.port)
    try:
        for part in parts:
            record(part=part, port=args.port)
    finally:
        server.terminate()
        server.wait(timeout=5)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
