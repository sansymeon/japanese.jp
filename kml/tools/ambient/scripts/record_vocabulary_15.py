#!/usr/bin/env python3
"""Record Japanese Vocabulary Lesson 15 MP4 via Playwright.

Output: collections/vocabulary/vocabulary_15.mp4
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8796
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
COLLECTION_ID = "vocabulary_15"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    apply_mp4_end_fade,
    capture_exhibition_webm,
    ensure_deps,
    exhibition_record_url,
    load_collection,
    mux_video_with_audio,
    presentation_timeout_ms,
    start_server,
    stop_server,
)


def japanese_vocabulary_soundtrack_start_ms(collection: dict) -> int:
    """Music begins under the tea-room intro (black → image ready → delay)."""
    t = collection.get("exhibition") or {}
    opening = (collection.get("bookends") or {}).get("opening") or {}
    before = int(
        opening.get("blackBeforeMs")
        if opening.get("blackBeforeMs") is not None
        else t.get("openingBlackBeforeMs", 0)
    )
    delay = int(
        opening.get("startSoundtrackAfterImageMs")
        or t.get("openingSoundtrackDelayMs", 0)
    )
    if opening.get("startSoundtrackWithImage") or opening.get("jp") or opening.get("images"):
        return before + delay
    return before


def record(*, port: int) -> Path:
    collection = load_collection(ROOT, COLLECTION_ID)
    soundtrack_start_ms = japanese_vocabulary_soundtrack_start_ms(collection)
    timeout_ms = presentation_timeout_ms(collection, ROOT, extra_ms=180_000)

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    display = dict(collection.get("display") or {})
    display.setdefault("typography", "mobile-refine")
    display.setdefault("verseMode", "sequential")
    url = exhibition_record_url(port=port, collection_id=COLLECTION_ID, display=display)

    out_dir = ROOT / "collections" / "vocabulary"
    out_path = out_dir / "vocabulary_15.mp4"
    tmp_dir = out_dir / ".tmp_vocabulary_15"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {COLLECTION_ID} → {out_path.name}")
    print(f"  Soundtrack @ {soundtrack_start_ms} ms")
    print(f"  Max wait: {timeout_ms // 1000}s")

    webm = capture_exhibition_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    # apad keeps video past the music's end so the silent 漢 crest survives
    # (-shortest then cuts at video end, not audio end).
    filter_complex = (
        f"[1:a]adelay={soundtrack_start_ms}|{soundtrack_start_ms}[m];"
        f"[m]asetpts=PTS-STARTPTS,apad[a]"
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

    # Standard series ending: music ends → fade to black → crest reveal →
    # crest holds a few seconds → fade out → cut.
    t = collection.get("exhibition") or {}
    audio_end_s = (soundtrack_start_ms + soundtrack_duration_ms(soundtrack)) / 1000
    crest_visible_s = (
        t.get("closingFadeToBlackMs", 3500)
        + t.get("closingBlackBeforeMs", 800)
        + t.get("closingRevealMs", 3200)
        + t.get("closingHoldMs", 2800)
    ) / 1000
    fade_start_s = int(audio_end_s + crest_visible_s)
    fade_s = 3
    print(f"  End fade: crest hold → fade @ {fade_start_s}s (+{fade_s}s) → cut")
    apply_mp4_end_fade(out_path, fade_start_s=fade_start_s, fade_duration_s=fade_s)

    print(f"  → {out_path}")
    return out_path


def soundtrack_duration_ms(path: Path) -> int:
    import subprocess

    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    )
    return int(float(out.strip()) * 1000)


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
