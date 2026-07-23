#!/usr/bin/env python3
"""Record Hiragana Song Typography Edition MP4 via Playwright.

Output: collections/hiragana_song/hiragana_song_typography.mp4

Uses exhibition.html?collection=hiragana_song_typography
Soundtrack: audio/hiragana_ambient_version.mp3 (~3:35) + silent crest.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8791
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
COLLECTION_ID = "hiragana_song_typography"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    ensure_deps,
    exhibition_record_url,
    load_collection,
    mux_video_with_audio,
    presentation_timeout_ms,
    start_server,
    stop_server,
)


def typography_soundtrack_start_ms(collection: dict) -> int:
    """Music begins after initial exhibition black on scene 0."""
    t = collection.get("exhibition") or {}
    return int(t.get("exhibitionBlackBeforeMs", 0))


def closing_silence_pad_s(collection: dict) -> float:
    """Silent crest after soundtrack — pad so -shortest does not clip the logo."""
    t = collection.get("exhibition") or {}
    ms = (
        int(t.get("closingBlackBeforeMs", 400))
        + int(t.get("closingRevealMs", 1600))
        + int(t.get("closingHoldMs", 2200))
        + int(t.get("closingExhaleMs", 1600))
        + int(t.get("closingBlackAfterMs", 400))
        + 1000
    )
    return max(8.0, ms / 1000.0)


def record(*, port: int) -> Path:
    collection = load_collection(ROOT, COLLECTION_ID)
    soundtrack_start_ms = typography_soundtrack_start_ms(collection)
    timeout_ms = presentation_timeout_ms(collection, ROOT, extra_ms=120_000)
    pad_s = closing_silence_pad_s(collection)

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    url = exhibition_record_url(port=port, collection_id=COLLECTION_ID)

    out_dir = ROOT / "collections" / "hiragana_song"
    out_path = out_dir / f"{COLLECTION_ID}.mp4"
    tmp_dir = out_dir / f".tmp_{COLLECTION_ID}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {COLLECTION_ID} → {out_path.name}")
    print(f"  Soundtrack @ {soundtrack_start_ms} ms")
    print(f"  Closing pad: {pad_s:.1f}s")
    print(f"  Max wait: {timeout_ms // 1000}s")

    webm = capture_exhibition_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    filter_complex = (
        f"[1:a]adelay={soundtrack_start_ms}|{soundtrack_start_ms},"
        f"apad=pad_dur={pad_s:.3f}[m];"
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
