#!/usr/bin/env python3
"""Build collections/lesson_03/lesson_3_foundations.json — YouTube loop ambient study."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import write_collection_path  # noqa: E402
from lesson_03_common import load_scenes  # noqa: E402
from foundations_exhibition_common import youtube_foundations_config  # noqa: E402

OUT_PATH = write_collection_path(ROOT, "lesson_3_foundations")

STUDY_LESSON = "audio/study_version_2_minus3db.mp3"


def build() -> dict:
    config = youtube_foundations_config(
        lesson=3,
        title="KML Ambient Foundations — Lesson 3",
        notes=(
            "Study template (~8 min loop). Original lesson order; "
            "Employee closes with concert fade. Soundtrack: Study Version 2."
        ),
        scenes=load_scenes(),
    )
    config["soundtrack"] = {"main": STUDY_LESSON}
    return config


def main() -> int:
    config = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    print(f"  First: {config['scenes'][0]['kanji']} ({config['scenes'][0]['id']})")
    print(f"  Last:  {config['scenes'][-1]['kanji']} ({config['scenes'][-1]['id']})")
    print(f"  Audio: {config['soundtrack']['main']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
