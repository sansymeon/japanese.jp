#!/usr/bin/env python3
"""Record Hiragana Song MP4 via Playwright.

Output: collections/hiragana_song/hiragana_song.mp4

Uses exhibition.html?collection=hiragana_song
Kana groups follow data/hiragana_song_captions.sbv.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8790
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
COLLECTION_ID = "hiragana_song"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    calibrate_soundtrack_start_ms_from_webm,
    capture_exhibition_webm,
    ensure_deps,
    exhibition_record_url,
    load_collection,
    mux_video_with_audio,
    presentation_timeout_ms,
    probe_duration_seconds,
    resolve_soundtrack_start_ms,
    start_server,
    stop_server,
)


def soundtrack_start_ms(collection: dict) -> int:
    t = collection.get("exhibition") or {}
    return int(t.get("exhibitionBlackBeforeMs", 0))


def closing_silence_pad_s(collection: dict) -> float:
    t = collection.get("exhibition") or {}
    ms = int(t.get("fujiExhaleMs", 2800)) * 2 + 1500
    return max(8.0, ms / 1000.0)


def first_caption_sbv_ms(root: Path, collection: dict) -> int:
    """Read the first cue start time from the collection SBV (preview clock)."""
    meta = collection.get("meta") or {}
    scenes = collection.get("scenes") or []
    rel = ""
    if scenes:
        rel = scenes[0].get("captionsFile") or ""
    rel = rel or meta.get("captionsFile") or ""
    path = root / rel
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    for block in text.strip().split("\n\n"):
        lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
        if len(lines) < 2 or "," not in lines[0]:
            continue
        start = lines[0].split(",", 1)[0].strip()
        # SBV: H:MM:SS.mmm
        parts = start.split(":")
        if len(parts) != 3:
            continue
        h, m = int(parts[0]), int(parts[1])
        sec = float(parts[2])
        return int(round(((h * 60) + m) * 1000 + sec * 1000))
    return 0


def record(*, port: int) -> Path:
    collection = load_collection(ROOT, COLLECTION_ID)
    fallback_ms = soundtrack_start_ms(collection)
    timeout_ms = presentation_timeout_ms(collection, ROOT, extra_ms=120_000)
    pad_s = closing_silence_pad_s(collection)
    sbv0 = first_caption_sbv_ms(ROOT, collection)

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
    print(f"  Soundtrack fallback @ {fallback_ms} ms (measuring actual start)")
    print(f"  First caption SBV @ {sbv0} ms")
    print(f"  Closing pad: {pad_s:.1f}s")
    print(f"  Max wait: {timeout_ms // 1000}s")

    capture_timing: dict = {}
    webm = capture_exhibition_webm(
        url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms, timing=capture_timing
    )
    estimate_ms = resolve_soundtrack_start_ms(
        timing=capture_timing, fallback_ms=fallback_ms
    )
    calibrated = calibrate_soundtrack_start_ms_from_webm(
        webm, first_caption_sbv_ms=sbv0 or 13480, estimate_start_ms=estimate_ms
    )
    start_ms = calibrated if calibrated is not None else estimate_ms
    print(
        f"  Mux adelay: {start_ms} ms "
        f"(webm-calibrated={calibrated} estimate={estimate_ms})"
    )

    webm_s = probe_duration_seconds(webm)
    mp3_s = probe_duration_seconds(soundtrack)
    covered_s = start_ms / 1000.0 + mp3_s
    pad_s = max(pad_s, webm_s - covered_s + 1.0)
    print(f"  Video: {webm_s:.1f}s, soundtrack covers {covered_s:.1f}s, pad {pad_s:.1f}s")

    filter_complex = (
        f"[1:a]adelay={start_ms}|{start_ms},"
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
