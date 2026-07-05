#!/usr/bin/env python3
"""Build Lesson 3 Reading Exhibition.

Flow per exhibit: pause → natural Japanese → furigana in/out → English on artwork.
Soundtrack: 12 Minutes v1 (odd lessons).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSON = 3
COLLECTION_ID = "lesson_03_reading"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_lesson_01_assisted_reading_experimental import (  # noqa: E402
    collection_id,
    write_collection,
)
from framing_policy import run_fill_safety_audit  # noqa: E402


def main() -> int:
    path, config = write_collection(LESSON)
    meta = config["meta"]
    sample = config["scenes"][0]

    print(f"Wrote {len(config['scenes'])} exhibits → {path}")
    print(
        f"  soundtrack: {meta['soundtrackVersion']} "
        f"({config['soundtrack']['main']}, {meta['soundtrackTarget']})"
    )
    print(f"  exhibition.html?collection={collection_id(LESSON)}")
    print(f"  sample: {sample['id']} ({sample['kanji']})")

    return run_fill_safety_audit(COLLECTION_ID)


if __name__ == "__main__":
    raise SystemExit(main())
