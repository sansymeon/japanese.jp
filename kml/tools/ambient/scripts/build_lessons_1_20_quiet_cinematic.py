#!/usr/bin/env python3
"""Build Quiet Cinematic Japan collections for Lessons 1–5, 6–10, 11–15, 16–20."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_lessons_21_25_quiet_cinematic as shared
import quiet_cinematic_l1_20 as l1_20

from collection_paths import write_collection_path

BLOCKS = l1_20.BLOCKS


def build_block(start: int, end: int) -> dict:
    cid = l1_20.collection_id(start, end)
    items = l1_20.curator_items(start, end)
    draft = l1_20.write_draft(start, end, items)
    out_path = write_collection_path(ROOT, cid)

    shared.COLLECTION_ID = cid
    shared.DRAFT_PATH = draft
    shared.OUT_PATH = out_path
    shared.SEED = l1_20.SEEDS[(start, end)]

    config = shared.build()
    scene_count = len(config["scenes"])
    soundtrack_ms = config["meta"]["soundtrackDurationMs"]
    avg_hold_ms = config["meta"]["avgHoldMs"]

    config["title"] = f"Quiet Cinematic Japan — Lessons {start}–{end}"
    config["notes"] = (
        f"Curated textless journey: Quiet Cinematic Japan from Lessons {start}–{end}. "
        "Ambient Revised keepers, still-life dropped; landscape fill where needed. "
        f"Ken Burns gallery profile, ~{avg_hold_ms / 1000:.0f}s holds, "
        f"silent gold crest after soundtrack. {scene_count} images · soundtrack "
        f"{soundtrack_ms / 60000:.1f} min."
    )
    config["meta"].update(
        {
            "edition": f"Lessons {start}–{end}",
            "lessons": list(range(start, end + 1)),
            "draftPath": str(draft.relative_to(ROOT)),
            "keeperSource": "collections/ambient_gallery_film/ambient_gallery_film.json",
        }
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {scene_count} exhibits → {out_path}")
    print(
        f"  avg hold {avg_hold_ms / 1000:.1f}s · soundtrack {soundtrack_ms / 60000:.1f} min"
    )
    for lesson in range(start, end + 1):
        count = sum(1 for scene in config["scenes"] if scene["meta"]["lesson"] == lesson)
        print(f"  Lesson {lesson}: {count}")
    return config


def main() -> int:
    blocks = BLOCKS
    if len(sys.argv) == 2:
        start_s, end_s = sys.argv[1].split("-")
        start, end = int(start_s), int(end_s)
        blocks = ((start, end),)
    for start, end in blocks:
        build_block(start, end)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
