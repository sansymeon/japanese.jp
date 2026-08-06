#!/usr/bin/env python3
"""Record Quiet Cinematic Japan — Lessons 21–25 via Playwright.

Usage:
  python scripts/record_lessons_21_25_quiet_cinematic.py
  python scripts/record_lessons_21_25_quiet_cinematic.py --rebuild

Output: extended_exhibitions/lessons_21_25_quiet_cinematic.mp4
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
COLLECTION_ID = "lessons_21_25_quiet_cinematic"
OUTPUT_DIR = ROOT / "extended_exhibitions"
DEFAULT_PORT = 8771

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    ensure_deps,
    exhibition_record_url,
    load_collection,
    mux_exhibition_soundtrack,
    presentation_timeout_ms,
    start_server,
    stop_server,
    vocabulary_exhibition_soundtrack_start_ms,
)


def record(*, port: int, output_dir: Path) -> Path:
    collection = load_collection(ROOT, COLLECTION_ID)
    soundtrack_start_ms = vocabulary_exhibition_soundtrack_start_ms(collection)
    timeout_ms = presentation_timeout_ms(collection, ROOT, extra_ms=300_000)

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    display = dict(collection.get("display") or {})
    display.setdefault("typography", "mobile-refine")
    display.setdefault("verseMode", "sequential")
    url = exhibition_record_url(port=port, collection_id=COLLECTION_ID, display=display)

    out_path = output_dir / f"{COLLECTION_ID}.mp4"
    tmp_dir = output_dir / f".tmp_{COLLECTION_ID}"
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {COLLECTION_ID} → {out_path.name}")
    print(f"  Soundtrack: {soundtrack_rel}")
    print(f"  Soundtrack @ {soundtrack_start_ms} ms")
    print(f"  Scenes: {len(collection.get('scenes') or [])}")
    print(f"  Max wait: {timeout_ms // 1000}s ({timeout_ms / 60000:.1f} min)")
    print(f"  URL: {url}")

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
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()

    ensure_deps()

    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    if args.rebuild:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_lessons_21_25_quiet_cinematic.py"),
            ],
            check=True,
            cwd=ROOT,
        )

    server = start_server(ROOT, args.port)
    try:
        record(port=args.port, output_dir=args.output_dir)
    finally:
        stop_server(server)

    print(f"\nDone. MP4 in {args.output_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
