#!/usr/bin/env python3
"""Calculate runtime for lessons_1_5_prototype exhibition."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "collections" / "lessons_1_5_prototype.json"


def probe_duration_seconds(path: Path) -> float | None:
    if not path.is_file():
        return None
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
    ).strip()
    return float(out)


def exhibit_ms(t: dict, *, image_verse: bool = False) -> int:
    if image_verse:
        return (
            t["artworkAloneMs"]
            + t["kanjiRevealMs"]
            + t.get("imageVerseKanjiHoldMs", 2000)
            + t.get("imageVerseKanjiFadeMs", t.get("titleFadeMs", 1600))
            + t["verseJpRevealMs"]
            + t["verseJpHoldMs"]
            + t["verseJpFadeMs"]
            + t["verseEnRevealMs"]
            + t["verseEnHoldMs"]
            + t["verseEnFadeMs"]
            + t.get("exhibitTransitionMs", 4000)
        )
    return (
        t["artworkAloneMs"]
        + t["verseJpRevealMs"]
        + t["verseJpHoldMs"]
        + t["verseJpFadeMs"]
        + t["verseEnRevealMs"]
        + t["verseEnHoldMs"]
        + t["verseEnFadeMs"]
        + t.get("exhibitTransitionMs", 4000)
    )


def opening_ms(t: dict, *, intro_s: float | None, hold_until_audio: bool) -> int:
    base = (
        t.get("openingBlackBeforeMs", 0)
        + t.get("openingRevealMs", 0)
        + t.get("openingExhaleMs", 0)
        + t.get("openingBlackAfterMs", 0)
    )
    hold = int(intro_s * 1000) if hold_until_audio and intro_s else t.get("openingHoldMs", 0)
    return base + hold


def closing_ms(t: dict, *, outro_s: float | None, closing: dict) -> int:
    crest = (
        t.get("closingRevealMs", 0)
        + t.get("closingExhaleMs", t.get("closingFadeToBlackMs", 3000))
        + t.get("closingTitleRevealMs", 2500)
        + t.get("closingTitleFadeMs", t.get("closingFadeToBlackMs", 3000))
        + t.get("closingBlackAfterMs", 0)
    )
    if closing.get("titleHtml") and closing.get("audio") and outro_s:
        return crest + int(outro_s * 1000)
    if closing.get("audio") and outro_s:
        return crest + int(outro_s * 1000)
    return crest + t.get("closingHoldMs", 0)


def fmt(seconds: float) -> str:
    m, s = divmod(int(round(seconds)), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def main() -> int:
    if not COLLECTION.is_file():
        print(f"Missing {COLLECTION}. Run: python3 scripts/build_lessons_1_5_prototype.py", file=sys.stderr)
        return 1

    data = json.loads(COLLECTION.read_text(encoding="utf-8"))
    t = data["exhibition"]
    scenes = data["scenes"]
    bookends = data.get("bookends") or {}
    soundtrack = data.get("soundtrack") or {}

    per = exhibit_ms(
        t,
        image_verse=(data.get("display") or {}).get("exhibitProfile") == "imageVerse",
    )
    body = per * len(scenes)

    intro_path = ROOT / (bookends.get("opening", {}).get("audio") or "")
    outro_path = ROOT / (bookends.get("closing", {}).get("audio") or "")
    main_path = ROOT / (soundtrack.get("main") or "")

    intro_s = probe_duration_seconds(intro_path)
    outro_s = probe_duration_seconds(outro_path)
    main_s = probe_duration_seconds(main_path)

    opening = opening_ms(
        t,
        intro_s=intro_s,
        hold_until_audio=bool(bookends.get("opening", {}).get("holdUntilAudioEnds")),
    )
    closing = closing_ms(
        t,
        outro_s=outro_s,
        closing=bookends.get("closing") or {},
    )
    video_total = body + opening + closing

    print("Lessons 1–5 prototype runtime")
    print(f"  Exhibit count:     {len(scenes)}")
    print(f"  Per exhibit:       {per / 1000:.1f}s ({fmt(per / 1000)})")
    print(f"  Exhibits only:     {body / 1000:.1f}s ({fmt(body / 1000)})")
    print(f"  Opening bookend:   {opening / 1000:.1f}s")
    print(f"  Closing bookend:   {closing / 1000:.1f}s")
    print(f"  Video total:       {video_total / 1000:.1f}s ({fmt(video_total / 1000)})")
    print()
    print("  Audio tracks:")
    if intro_path.name:
        print(f"    Intro:  {intro_path.name} — {fmt(intro_s or 0)}")
    if main_path.name:
        print(f"    Main:   {main_path.name} — {fmt(main_s or 0)}")
    if outro_path.name:
        print(f"    Outro:  {outro_path.name} — {fmt(outro_s or 0)}")
    if intro_s and main_s and outro_s:
        audio_total = intro_s + main_s + outro_s
        print(f"    Combined audio:  {fmt(audio_total)} ({audio_total / 60:.1f} min)")
        gap = video_total / 1000 - audio_total
        print(f"    vs video total:  {gap:+.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
