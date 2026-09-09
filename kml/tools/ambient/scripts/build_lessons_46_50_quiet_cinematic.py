#!/usr/bin/env python3
"""Build Quiet Cinematic Japan — Lessons 46–50 exhibition.

Source: visual shortlist of lesson study images. Holds fit
audio/-3db_fifty_minutes.mp3 at the usual ~70s+ Quiet Cinematic pacing.
"""

from __future__ import annotations

import json
from pathlib import Path

import build_lessons_21_25_quiet_cinematic as shared
import quiet_cinematic_l46_50 as l46_50

ROOT = Path(__file__).resolve().parents[1]
COLLECTION_ID = l46_50.COLLECTION_ID
START, END = l46_50.START, l46_50.END
DRAFT_PATH = l46_50.DRAFT_PATH
OUT_PATH = shared.write_collection_path(ROOT, COLLECTION_ID)
SEED = l46_50.SEED


def build() -> dict:
    items = l46_50.curator_items(START, END)
    l46_50.write_draft(items)

    shared.COLLECTION_ID = COLLECTION_ID
    shared.DRAFT_PATH = DRAFT_PATH
    shared.OUT_PATH = OUT_PATH
    shared.SEED = SEED

    config = shared.build()
    scene_count = len(config["scenes"])
    soundtrack_ms = config["meta"]["soundtrackDurationMs"]
    avg_hold_ms = config["meta"]["avgHoldMs"]

    config["title"] = "Quiet Cinematic Japan — Lessons 46–50"
    config["notes"] = (
        "Textless Quiet Cinematic Japan from Lessons 46–50. "
        "Visual shortlist: landscape and atmosphere first. "
        f"Ken Burns gallery profile, ~{avg_hold_ms / 1000:.0f}s holds, "
        f"silent gold crest after soundtrack. {scene_count} images · soundtrack "
        f"{soundtrack_ms / 60000:.1f} min."
    )
    config["meta"].update(
        {
            "edition": "Lessons 46–50",
            "lessons": list(range(START, END + 1)),
            "draftPath": str(DRAFT_PATH.relative_to(ROOT)),
            "keeperSource": "scripts/quiet_cinematic_l46_50.py",
        }
    )
    return config


def main() -> int:
    config = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(config['scenes'])} exhibits → {OUT_PATH}")
    print(
        f"  avg hold {config['meta']['avgHoldMs'] / 1000:.1f}s · "
        f"soundtrack {config['meta']['soundtrackDurationMs'] / 60000:.1f} min"
    )
    for lesson in range(START, END + 1):
        count = sum(
            1 for scene in config["scenes"] if scene["meta"]["lesson"] == lesson
        )
        print(f"  Lesson {lesson}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
