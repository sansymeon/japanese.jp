#!/usr/bin/env python3
"""Record Ambient Japan 4h playback prototype MP4 via Playwright.

Usage:
  python scripts/record_ambient_japan_4h_prototype.py
  python scripts/record_ambient_japan_4h_prototype.py --rebuild

Output: collections/ambient_japan_4h_scenery/ambient_japan_4h_prototype.mp4

Same capture/mux pipeline as Four Seasons and Ambient Movies.
Does not render the full four-hour film.
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
COLLECTION_ID = "ambient_japan_4h_prototype"
OUTPUT_NAME = "ambient_japan_4h_prototype.mp4"
DEFAULT_PORT = 9086

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    LONG_CAPTURE_CHROMIUM_ARGS,
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


def record(*, port: int, rebuild: bool) -> Path:
    if rebuild:
        subprocess.check_call(
            [sys.executable, str(ROOT / "scripts" / "build_ambient_japan_4h_prototype.py")],
            cwd=str(ROOT),
        )

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

    out_dir = ROOT / "collections" / "ambient_japan_4h_scenery"
    out_path = out_dir / OUTPUT_NAME
    tmp_dir = out_dir / ".tmp_ambient_japan_4h_prototype"
    out_dir.mkdir(parents=True, exist_ok=True)
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    meta = collection.get("meta") or {}
    print(f"Recording {COLLECTION_ID} → {out_path}")
    print(f"  Slice: {meta.get('prototypeSlice')}")
    print(f"  Hold: {meta.get('holdMs')} ms")
    print(f"  Soundtrack: {soundtrack_rel}")
    print(f"  Soundtrack @ {soundtrack_start_ms} ms")
    print(f"  Max wait: {timeout_ms // 1000}s ({timeout_ms / 60000:.1f} min)")
    print(f"  URL: {url}")
    print("  Chromium: long-capture flags (software compositor)")

    webm = capture_exhibition_webm(
        url=url,
        tmp_dir=tmp_dir,
        timeout_ms=timeout_ms,
        chromium_extra_args=LONG_CAPTURE_CHROMIUM_ARGS,
    )

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
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild collection JSON before recording",
    )
    args = parser.parse_args()

    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    ensure_deps()
    server = start_server(ROOT, args.port)
    try:
        record(port=args.port, rebuild=args.rebuild)
    finally:
        stop_server(server)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
