#!/usr/bin/env python3
"""Build Quiet Cinematic Japan — Lessons 31–35 exhibition.

Source: Lessons 21–40 keeper shortlist (73 images). Holds fit
audio/-3db_fifty_minutes.mp3; min hold is lowered so the full shortlist fits.
"""

from __future__ import annotations

import json
from pathlib import Path

import build_lessons_21_25_quiet_cinematic as shared
import quiet_cinematic_keepers as keepers

ROOT = Path(__file__).resolve().parents[1]
COLLECTION_ID = "lessons_31_35_quiet_cinematic"
START, END = 31, 35
DRAFT_PATH = ROOT / "quiet_cinematic_review" / "data" / "lessons_31_35_draft.json"
OUT_PATH = shared.write_collection_path(ROOT, COLLECTION_ID)
SEED = 20260820
# 73 keepers cannot hold at 70s on a 50.7 min bed; ~39s average.
HOLD_MIN_MS = 35_000


def build() -> dict:
    items = keepers.keeper_items(START, END)
    keepers.write_draft(
        DRAFT_PATH,
        collection_id=COLLECTION_ID,
        title="Quiet Cinematic Japan — Lessons 31–35 (draft)",
        start=START,
        end=END,
        items=items,
    )

    shared.COLLECTION_ID = COLLECTION_ID
    shared.DRAFT_PATH = DRAFT_PATH
    shared.OUT_PATH = OUT_PATH
    shared.SEED = SEED
    shared.HOLD_MIN_MS = HOLD_MIN_MS

    config = shared.build()
    scene_count = len(config["scenes"])
    soundtrack_ms = config["meta"]["soundtrackDurationMs"]
    avg_hold_ms = config["meta"]["avgHoldMs"]

    config["title"] = "Quiet Cinematic Japan — Lessons 31–35"
    config["notes"] = (
        "Textless Quiet Cinematic Japan from Lessons 31–35. "
        "Full 21–40 keeper shortlist for this block "
        f"({scene_count} images; denser than 21–25 because more keepers were marked). "
        f"Ken Burns gallery profile, ~{avg_hold_ms / 1000:.0f}s holds, "
        f"silent gold crest after soundtrack. Soundtrack "
        f"{soundtrack_ms / 60000:.1f} min."
    )
    config["meta"].update(
        {
            "edition": "Lessons 31–35",
            "lessons": list(range(START, END + 1)),
            "draftPath": str(DRAFT_PATH.relative_to(ROOT)),
            "keeperSource": str(keepers.KEEPERS_PATH.relative_to(ROOT.parent.parent)),
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
