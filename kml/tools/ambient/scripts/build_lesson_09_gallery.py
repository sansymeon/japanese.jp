#!/usr/bin/env python3
"""Build Lesson 9 Gallery — image and music only (final learning stage)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSON = 9
COLLECTION_ID = "lesson_09_gallery"

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_lesson_05_gallery import (  # noqa: E402
    SILENT_CREST_BOOKENDS,
    exhibit_runtime_ms,
    gallery_exhibition_timing,
    parse_lesson_scenes,
    soundtrack_duration_ms,
)
from collection_paths import write_collection_path  # noqa: E402

OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)
FOUNDATIONS_SOUNDTRACK = "audio/study_version_1_minus3db.mp3"


def build() -> dict:
    scenes = parse_lesson_scenes(LESSON)
    soundtrack_ms = soundtrack_duration_ms(FOUNDATIONS_SOUNDTRACK)
    exhibition = gallery_exhibition_timing(len(scenes), soundtrack_ms)
    runtime_ms = exhibit_runtime_ms(exhibition, len(scenes))
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": COLLECTION_ID,
        "title": "KML Gallery — Lesson 9 (Foundations)",
        "notes": (
            "Final learning stage: artwork and Foundations music only (~8 min). "
            f"Exhibit pacing fits the soundtrack ({runtime_ms // 1000}s runtime, "
            f"{exhibition['artworkAloneMs'] // 1000}s image hold per scene); "
            "composition-aware camera drift (~3–5% per exhibit)."
        ),
        "soundtrack": {"main": FOUNDATIONS_SOUNDTRACK},
        "bookends": dict(SILENT_CREST_BOOKENDS),
        "exhibition": exhibition,
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "gallery",
            "showKeyword": False,
            "showKanji": False,
            "exhibitProfile": "gallery",
            "verseMode": "sequential",
            "bookendStyle": "galleryCrest",
        },
        "meta": {
            "family": "gallery",
            "lesson": LESSON,
            "stage": "gallery",
            "foundationsTrack": "study_version_1",
            "sceneCount": len(scenes),
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    timing = config["exhibition"]
    runtime_s = exhibit_runtime_ms(timing, len(config["scenes"])) / 1000
    print(
        f"Wrote {len(config['scenes'])} exhibits → {OUT_PATH} "
        f"({runtime_s:.0f}s runtime, {timing['artworkAloneMs'] / 1000:.1f}s image hold)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
