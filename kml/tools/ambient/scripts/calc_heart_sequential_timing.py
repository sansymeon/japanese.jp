#!/usr/bin/env python3
"""Print Heart v5 timing impact when switching to sequential verses."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "collections" / "heart_v5.json"
SOUNDTRACK = ROOT / "audio" / "ambient_kanji_exhibition.mp3"
FLUTE = ROOT / "audio" / "flute_intro.mp3"


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


def exhibit_ms(t: dict, *, sequential: bool) -> int:
    ms = (
        t["artworkArrivalMs"]
        + t["artworkAloneMs"]
        + t["kanjiRevealMs"]
        + t["keywordDelayMs"]
        + t["keywordFadeMs"]
        + t["titleHoldMs"]
        + t["titleFadeMs"]
        + t["essenceKanjiRevealMs"]
        + t.get("essenceHoldMs", 0)
        + t["imageExhaleFadeMs"]
        + t["kanjiAloneHoldMs"]
        + t["kanjiExhaleFadeMs"]
    )
    ms += sequential_phase_ms(t) if sequential else simultaneous_phase_ms(t)
    return ms


def main() -> int:
    if not COLLECTION.is_file():
        print(f"Missing {COLLECTION}", file=sys.stderr)
        return 1

    collection = json.loads(COLLECTION.read_text(encoding="utf-8"))
    t = collection["exhibition"]
    scenes = len(collection["scenes"])

    sim_exhibit = exhibit_ms(t, sequential=False)
    seq_exhibit = exhibit_ms(t, sequential=True)
    delta = seq_exhibit - sim_exhibit
    total_delta = delta * scenes

    opening = (
        t["openingBlackBeforeMs"]
        + int(probe_duration(FLUTE) * 1000)
        + t["openingExhaleMs"]
        + t.get("openingBlackAfterMs", 0)
    )
    closing_min = (
        t["blackHoldMs"]
        + t["closingRevealMs"]
        + t.get("closingSilenceHoldMs", 0)
        + t.get("closingFadeToBlackMs", t["closingExhaleMs"])
        + t.get("closingBlackAfterMs", 0)
    )

    sim_total = opening + sim_exhibit * scenes + closing_min
    seq_total = opening + seq_exhibit * scenes + closing_min
    black_saved = (t.get("blackHoldMs", 3500) - t.get("exhibitBlackHoldMs", 500)) * max(
        0, scenes - 1
    )
    seq_total -= black_saved
    soundtrack_s = probe_duration(SOUNDTRACK)

    print("Heart v5 sequential verse timing")
    print(f"  Per exhibit: {sim_exhibit/1000:.1f}s → {seq_exhibit/1000:.1f}s (+{delta/1000:.1f}s)")
    print(f"  44 exhibits: +{total_delta/1000:.0f}s ({total_delta/60000:.1f} min)")
    print(f"  Black corridor savings: {black_saved/1000:.0f}s ({black_saved/60000:.1f} min)")
    print(f"  Est. presentation (exhibits+bookends): {sim_total/60000:.1f} → {seq_total/60000:.1f} min")
    print(f"  Soundtrack length: {soundtrack_s/60:.2f} min")
    print()
    gap = seq_total / 1000 - soundtrack_s
    if gap > 0:
        print(f"  MP3 extension recommended: ~{gap:.0f}s ({gap/60:.1f} min) to keep music through closing.")
    else:
        print(f"  No MP3 extension required (headroom ~{-gap:.0f}s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
