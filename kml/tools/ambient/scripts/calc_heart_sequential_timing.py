#!/usr/bin/env python3
"""Print Heart v5 runtime vs ambient_kanji_exhibition.mp3 (engine-accurate)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "collections" / "heart_v5.json"
SOUNDTRACK = ROOT / "audio" / "ambient_kanji_exhibition.mp3"


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        text=True,
    )
    return float(out.strip())


def sequential_phase_ms(t: dict) -> int:
    hold_pool = t["verseEnDelayMs"] + t["reflectionHoldMs"]
    jp_hold = t.get("verseJpHoldMs") or round(hold_pool * 0.42)
    en_hold = t.get("verseEnHoldMs") or (hold_pool - round(hold_pool * 0.42))
    return (
        t["verseJpRevealMs"]
        + jp_hold
        + (t.get("verseJpFadeMs") or t["titleFadeMs"])
        + (t.get("verseEnRevealMs") or t["verseEnFadeMs"])
        + en_hold
        + (t.get("verseEnFadeMs") or t["versesFadeMs"])
    )


def simultaneous_phase_ms(t: dict) -> int:
    return (
        t["verseJpRevealMs"]
        + t["verseEnDelayMs"]
        + t["verseEnFadeMs"]
        + t["reflectionHoldMs"]
        + t["versesFadeMs"]
    )


def gallery_bridge_ms(t: dict) -> int:
    exhale = int(t.get("imageHandoffExhaleMs") or t["imageExhaleFadeMs"])
    arrival = int(
        t.get("imageHandoffArrivalMs")
        or t.get("exhibitTransitionMs")
        or (t["artworkArrivalMs"] + t.get("blackHoldMs", 0))
    )
    return exhale + arrival


def exhibit_body_ms(t: dict, *, sequential: bool) -> int:
    ms = (
        t["kanjiRevealMs"]
        + t["keywordDelayMs"]
        + t["keywordFadeMs"]
        + t["titleHoldMs"]
        + t["titleFadeMs"]
        + t["essenceKanjiRevealMs"]
        + t.get("essenceHoldMs", 0)
    )
    ms += sequential_phase_ms(t) if sequential else simultaneous_phase_ms(t)
    return ms


def handoff_exit_ms(t: dict) -> int:
    if t.get("seamlessExhibitHandoff"):
        return gallery_bridge_ms(t)
    crossfade = int(
        t.get("exhibitTransitionMs") or (t["artworkArrivalMs"] + t.get("blackHoldMs", 0))
    )
    handoff_fade = int(
        t.get("kanjiBridgeFadeMs")
        or t.get("kanjiHandoffFadeMs")
        or min(4500, t["kanjiExhaleFadeMs"])
    )
    return handoff_fade + crossfade


def final_exit_ms(t: dict) -> int:
    hold = int(t.get("finalKanjiAloneHoldMs") or t.get("kanjiAloneHoldMs") or 0)
    return t["imageExhaleFadeMs"] + hold + t["kanjiExhaleFadeMs"]


def engine_exhibits_ms(t: dict, scene_count: int, *, sequential: bool) -> int:
    """Mirror playExhibit(): first full arrival, gallery-bridge handoffs thereafter."""
    body = exhibit_body_ms(t, sequential=sequential)
    first_intro = 80 + t["artworkArrivalMs"] + t["artworkAloneMs"]
    handoff_exit = handoff_exit_ms(t)
    handoff_intro = t["artworkAloneMs"]
    final_exit = final_exit_ms(t)
    if scene_count <= 0:
        return 0
    if scene_count == 1:
        return first_intro + body + final_exit
    return (
        first_intro
        + body
        + handoff_exit
        + (scene_count - 2) * (handoff_intro + body + handoff_exit)
        + handoff_intro
        + body
        + final_exit
    )


def main() -> int:
    if not COLLECTION.is_file():
        print(f"Missing {COLLECTION}", file=sys.stderr)
        return 1

    collection = json.loads(COLLECTION.read_text(encoding="utf-8"))
    t = collection["exhibition"]
    scenes = len(collection["scenes"])
    bookends = collection.get("bookends") or {}
    sequential = (collection.get("display") or {}).get("verseMode") == "sequential"

    flute_rel = (bookends.get("opening") or {}).get("audio") or "audio/exhibition_flute_intro.mp3"
    flute_path = ROOT / flute_rel

    opening = (
        t["openingBlackBeforeMs"]
        + int(probe_duration(flute_path) * 1000)
        + t["openingExhaleMs"]
        + t.get("openingBlackAfterMs", 0)
    )
    exhibits = engine_exhibits_ms(t, scenes, sequential=sequential)
    closing_before_wait = t.get("closingBlackBeforeMs", t["blackHoldMs"]) + t["closingRevealMs"]
    # Fade runs in parallel with soundtrack tail; only closingBlackAfter remains after music ends.
    closing_after_soundtrack = t.get("closingBlackAfterMs", 0)
    soundtrack_s = probe_duration(SOUNDTRACK)

    soundtrack_to_wait_ms = exhibits + closing_before_wait
    gap_s = soundtrack_to_wait_ms / 1000 - soundtrack_s

    print("Heart v5 engine-accurate timing")
    print(f"  Verse mode: {'sequential' if sequential else 'staggered'}")
    print(f"  Exhibit body: {exhibit_body_ms(t, sequential=sequential) / 1000:.1f}s")
    print(f"  Gallery bridge (handoff): {gallery_bridge_ms(t) / 1000:.1f}s")
    print(f"  Final exhibit exit: {final_exit_ms(t) / 1000:.1f}s")
    print(f"  {scenes} exhibits: {exhibits / 60000:.2f} min")
    print(f"  Opening (pre-soundtrack): {opening / 1000:.1f}s")
    print(f"  Soundtrack start → waitForSoundtrackEnd: {soundtrack_to_wait_ms / 60000:.2f} min")
    print(f"  Soundtrack length: {soundtrack_s / 60:.2f} min")
    print(f"  Visual tail after soundtrack ends: {closing_after_soundtrack / 1000:.1f}s")
    print()
    if gap_s > 1:
        print(f"  ⚠ Visuals reach closing ~{gap_s:.0f}s before music ends (extend MP3 or shorten timing).")
    elif gap_s < -5:
        print(f"  Closing hero will hold ~{-gap_s:.0f}s on music after last exhibit.")
    else:
        print("  Sync OK (music and closing hero align within a few seconds).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
