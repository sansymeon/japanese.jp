#!/usr/bin/env python3
"""Build a Heisig lesson Gallery — image and music only (same profile as Lessons 1–10).

Usage:
  python3 scripts/build_lesson_gallery.py --lesson 33
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_lesson_05_gallery import (  # noqa: E402
    SILENT_CREST_BOOKENDS,
    exhibit_runtime_ms,
    gallery_exhibition_timing,
    parse_lesson_scenes,
    soundtrack_duration_ms,
)
from collection_paths import write_collection_path  # noqa: E402

# Cycle Foundations beds like Lessons 1–10 (v1 / v2 / v3).
DEFAULT_TRACK_BY_LESSON = {
    33: "study_version_1",
    34: "study_version_2",
    35: "study_version_2",
    36: "study_version_3",
    37: "study_version_2",
}


def soundtrack_for(lesson: int, track: str | None = None) -> tuple[str, str]:
    key = track or DEFAULT_TRACK_BY_LESSON.get(lesson) or f"study_version_{(lesson % 3) or 3}"
    return key, f"audio/{key}_minus3db.mp3"


def build(lesson: int, *, track: str | None = None) -> dict:
    collection_id = f"lesson_{lesson:02d}_gallery"
    track_key, soundtrack = soundtrack_for(lesson, track)
    scenes = parse_lesson_scenes(lesson)
    if not scenes:
        raise SystemExit(f"No scenes parsed for lesson {lesson}")
    soundtrack_ms = soundtrack_duration_ms(soundtrack)
    exhibition = gallery_exhibition_timing(len(scenes), soundtrack_ms)
    runtime_ms = exhibit_runtime_ms(exhibition, len(scenes))
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": collection_id,
        "title": f"KML Gallery — Lesson {lesson} (Foundations)",
        "notes": (
            "Final learning stage: artwork and Foundations music only (~8 min). "
            f"Exhibit pacing fits the soundtrack ({runtime_ms // 1000}s runtime, "
            f"{exhibition['artworkAloneMs'] // 1000}s image hold per scene); "
            "composition-aware camera drift (~3–5% per exhibit). "
            "Same gallery display profile as Lessons 1–10."
        ),
        "soundtrack": {"main": soundtrack},
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
            "lesson": lesson,
            "stage": "gallery",
            "foundationsTrack": track_key,
            "sceneCount": len(scenes),
        },
        "scenes": scenes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, required=True)
    parser.add_argument(
        "--track",
        choices=("study_version_1", "study_version_2", "study_version_3"),
        default=None,
        help="Override Foundations soundtrack bed",
    )
    args = parser.parse_args()

    config = build(args.lesson, track=args.track)
    out_path = write_collection_path(ROOT, config["id"])
    out_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    timing = config["exhibition"]
    runtime_s = exhibit_runtime_ms(timing, len(config["scenes"])) / 1000
    print(
        f"Wrote {len(config['scenes'])} exhibits → {out_path} "
        f"({runtime_s:.0f}s runtime, {timing['artworkAloneMs'] / 1000:.1f}s image hold)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
