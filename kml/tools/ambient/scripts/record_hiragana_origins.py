#!/usr/bin/env python3
"""Record Hiragana Origins (full gojūon) MP4 via Playwright.

Output: collections/hiragana_origins/hiragana_origins.mp4

Uses exhibition.html?collection=hiragana_origins
Soundtrack: ambient_kanji_exhibition_original.mp3 (cut at crest fade).
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8820
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
COLLECTION_ID = "hiragana_origins"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    ensure_deps,
    exhibition_record_url,
    load_collection,
    mux_video_with_audio,
    start_server,
    stop_server,
)


def soundtrack_start_ms_for_collection(collection: dict) -> int:
    t = collection.get("exhibition") or {}
    return int(t.get("exhibitionBlackBeforeMs", 0))


def capture_timeout_ms(collection: dict) -> int:
    """Content-driven timeout — do not wait on the full long ambient bed."""
    meta = collection.get("meta") or {}
    t = collection.get("exhibition") or {}
    estimated = int(meta.get("estimatedContentRuntimeMs") or 0)
    if estimated <= 0:
        # Fallback: rough gojūon estimate if meta missing.
        estimated = 20 * 60 * 1000
    closing = (
        int(t.get("closingBlackBeforeMs", 400))
        + int(t.get("closingRevealMs", 1600))
        + int(t.get("closingHoldMs", 1500))
        + int(t.get("closingExhaleMs", 2000))
        + int(t.get("closingBlackAfterMs", 400))
    )
    # Extra margin for Playwright finish + crest.
    return estimated + closing + 180_000


def record(*, port: int) -> Path:
    collection = load_collection(ROOT, COLLECTION_ID)
    soundtrack_start_ms = soundtrack_start_ms_for_collection(collection)
    timeout_ms = capture_timeout_ms(collection)

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    url = exhibition_record_url(port=port, collection_id=COLLECTION_ID)

    out_dir = ROOT / "collections" / "hiragana_origins"
    out_path = out_dir / f"{COLLECTION_ID}.mp4"
    tmp_dir = out_dir / f".tmp_{COLLECTION_ID}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {COLLECTION_ID} → {out_path.name}")
    print(f"  Soundtrack @ {soundtrack_start_ms} ms")
    print(f"  Max wait: {timeout_ms // 1000}s (~{timeout_ms // 60000} min)")
    print(f"  Est. content: {(collection.get('meta') or {}).get('estimatedContentRuntimeMs', 0) // 60000} min")

    webm = capture_exhibition_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    # Delay music to match exhibition black; -shortest trims to video (crest cuts bed).
    filter_complex = (
        f"[1:a]adelay={soundtrack_start_ms}|{soundtrack_start_ms}[m];"
        f"[m]asetpts=PTS-STARTPTS[a]"
    )
    tmp_mux = tmp_dir / "muxed.mp4"
    mux_video_with_audio(
        webm=webm,
        output_mp4=tmp_mux,
        filter_complex=filter_complex,
        audio_inputs=[soundtrack],
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
    args = parser.parse_args()

    ensure_deps()

    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    server = start_server(ROOT, args.port)
    try:
        record(port=args.port)
    finally:
        stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
