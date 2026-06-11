#!/usr/bin/env python3
"""Build lesson_40_study.json from lesson_40 ambient collection."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSON_40 = ROOT / "collections" / "archive" / "lesson_40.json"
OUT_PATH = ROOT / "collections" / "lesson_40_study.json"


STUDY_LESSON = "audio/study_lesson.mp3"
INTRO_HOLD_MS = 1000
INTRO_DURATION_MS = 9000


def build() -> dict:
    base = json.loads(LESSON_40.read_text(encoding="utf-8"))

    return {
        "id": "lesson_40_study",
        "title": "KML Ambient Study — Lesson 40",
        "presentation": "study",
        "assetsBase": base["assetsBase"],
        "notes": (
            "Study template (~8 min loop). Silent hero, lesson bed with cards. Last card: "
            "kanji/verse fade to image-only concert until music ends, then fade to black and loop."
        ),
        "intro": {
            "image": "covers/lesson_40.png",
            "title": "Lesson 40",
            "holdBeforeMs": INTRO_HOLD_MS,
            "durationMs": INTRO_DURATION_MS,
        },
        "soundtrack": {"main": STUDY_LESSON},
        "timing": {
            "fadeMs": 1800,
            "kanjiLeadMs": 2000,
            "keywordLeadMs": 5000,
            "verseJpLeadMs": 8500,
            "sceneDurationMs": 22000,
            "studyExitFadeMs": 1800,
            "studyEmptyBeatMs": 500,
            "studyKanjiGapMs": 350,
            "introExitFadeMs": 1200,
            "studyLoopConcertFadeMs": 2500,
            "studyLoopFadeMs": 2500,
            "crossfadeMs": 2500,
            "kenBurnsDurationMs": 60000,
        },
        "background": {
            "mode": "image",
            "kenBurns": True,
            "overlayOpacity": 0.45,
            "blurPx": 0,
        },
        "display": {
            "showKeyword": True,
            "showFurigana": False,
            "loop": True,
            "autoAdvance": True,
        },
        "scenes": base["scenes"],
    }


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
