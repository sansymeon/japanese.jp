#!/usr/bin/env python3
"""Record Kana for Foreign Learners prototype MP4s (hiragana & katakana).

Same pipeline as Japanese Vocabulary Lesson 1 (record_vocabulary_01.py):
1920x1080 @ 25fps, libx264 crf18, soundtrack delayed to match the intro black,
AAC 192k. The soundtrack (vocabulary_1.mp3) is longer than the lesson, so the
audio is faded out with the final fade-to-black; the 漢 crest close is silent.

Usage:
    .venv/bin/python scripts/record_hiragana_lesson.py --scope test
    .venv/bin/python scripts/record_hiragana_lesson.py --scope full
    .venv/bin/python scripts/record_hiragana_lesson.py --collection katakana_lesson --scope full

Output: collections/<collection>/<collection>_<scope>.mp4
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8791
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    ensure_deps,
    load_collection,
    mux_video_with_audio,
    probe_duration_seconds,
    start_server,
    stop_server,
)

# Kana per teaching row (あ か さ た な は ま や ら わ)
ROW_SIZES = [5, 5, 5, 5, 5, 5, 5, 3, 5, 3]
AUDIO_END_FADE_S = 4.0


def per_kana_ms(t: dict) -> int:
    return (
        t["kanaFadeInMs"]
        + t["kanaAloneMs"]
        + t["romajiFadeInMs"]
        + t["kanaRomajiHoldMs"]
        + t["romajiFadeOutMs"]
        + t["kanaAloneAfterMs"]
        + t["kanaFadeOutMs"]
        + t["kanaGapMs"]
    )


def per_review_ms(t: dict) -> int:
    return (
        t["reviewBeforeMs"]
        + t["reviewFadeInMs"]
        + t["reviewHoldMs"]
        + t["reviewFadeOutMs"]
        + t["reviewAfterMs"]
    )


def opening_ms(t: dict) -> int:
    return (
        t["recordingBlackBeforeMs"]
        + t["backgroundFadeInMs"]
        + t["backgroundAloneMs"]
        + t["titleFadeInMs"]
        + t["titleHoldMs"]
        + t["titleFadeOutMs"]
        + t["titleAfterMs"]
    )


def chart_ms(t: dict) -> int:
    highlight_pass = len(ROW_SIZES) * (t["chartHighlightFadeMs"] + t["chartHighlightHoldMs"])
    return (
        t["chartBeforeMs"]
        + t["chartFadeInMs"]
        + t["chartHoldMs"]
        + highlight_pass
        + t["chartHighlightFadeMs"]
        + t["chartUnhighlightHoldMs"]
        + t["chartFadeOutMs"]
    )


def crest_ms(t: dict) -> int:
    return (
        t.get("crestBlackBeforeMs", 800)
        + t.get("crestFadeInMs", 3200)
        + t.get("crestHoldMs", 2800)
        + t.get("crestFadeOutMs", 3500)
        + t.get("crestBlackAfterMs", 800)
    )


def estimated_runtime_ms(t: dict, scope: str, *, has_crest: bool) -> int:
    total = opening_ms(t)
    if scope == "test":
        total += 5 * per_kana_ms(t) + per_review_ms(t)
        total += per_kana_ms(t)  # transition into か
    else:
        total += sum(ROW_SIZES) * per_kana_ms(t)
        total += len(ROW_SIZES) * per_review_ms(t)
        total += chart_ms(t)
    total += t["endBackgroundHoldMs"] + t["endFadeToBlackMs"]
    if has_crest:
        total += crest_ms(t)
    total += 400
    return total


def soundtrack_start_ms(t: dict) -> int:
    """Music starts under the background fade-in, as in Vocabulary Lesson 1."""
    return t["recordingBlackBeforeMs"] + t.get("soundtrackDelayAfterImageMs", 0)


def fade_audio_tail(mp4: Path, *, silent_tail_ms: int = 0) -> None:
    """Re-encode audio only so the soundtrack fades with the final black.

    silent_tail_ms: portion at the end of the video that must stay silent
    (the 漢 crest segment) — the fade completes just before it begins.
    """
    duration = probe_duration_seconds(mp4)
    fade_start = max(0.0, duration - silent_tail_ms / 1000 - AUDIO_END_FADE_S)
    tmp = mp4.with_name(f"{mp4.stem}.afade.tmp{mp4.suffix}")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp4),
            "-c:v",
            "copy",
            "-af",
            f"afade=t=out:st={fade_start:.2f}:d={AUDIO_END_FADE_S}",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(tmp),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    tmp.replace(mp4)


def record(*, port: int, scope: str, collection_id: str) -> Path:
    collection = load_collection(ROOT, collection_id)
    t = collection["timing"]
    has_crest = bool((collection.get("crest") or {}).get("image"))
    start_ms = soundtrack_start_ms(t)
    runtime_ms = estimated_runtime_ms(t, scope, has_crest=has_crest)
    timeout_ms = runtime_ms + 120_000

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    url = f"http://127.0.0.1:{port}/{collection_id}.html?scope={scope}"

    out_dir = ROOT / "collections" / collection_id
    out_path = out_dir / f"{collection_id}_{scope}.mp4"
    tmp_dir = out_dir / f".tmp_{collection_id}_{scope}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {collection_id} ({scope}) → {out_path.name}")
    print(f"  Estimated runtime: {runtime_ms // 1000}s")
    print(f"  Soundtrack @ {start_ms} ms")

    webm = capture_exhibition_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    filter_complex = (
        f"[1:a]adelay={start_ms}|{start_ms}[m];"
        f"[m]asetpts=PTS-STARTPTS[a]"
    )
    tmp_mux = tmp_dir / "muxed.mp4"
    mux_video_with_audio(
        webm=webm,
        output_mp4=tmp_mux,
        filter_complex=filter_complex,
        audio_inputs=[soundtrack],
    )
    # Music fades out with the background fade-to-black; the crest is silent.
    # Tail: crest segment + 400ms engine settle + 1500ms capture padding.
    silent_tail_ms = (crest_ms(t) + 400 + 1500) if has_crest else 0
    fade_audio_tail(tmp_mux, silent_tail_ms=silent_tail_ms)
    shutil.move(str(tmp_mux), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()

    print(f"  → {out_path}")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--scope", choices=("test", "full"), default="test")
    parser.add_argument(
        "--collection",
        choices=("hiragana_lesson", "katakana_lesson"),
        default="hiragana_lesson",
    )
    args = parser.parse_args()

    ensure_deps()

    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    server = start_server(ROOT, args.port)
    try:
        record(port=args.port, scope=args.scope, collection_id=args.collection)
    finally:
        stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
