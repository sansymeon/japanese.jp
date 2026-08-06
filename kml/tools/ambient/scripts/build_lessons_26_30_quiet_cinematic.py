#!/usr/bin/env python3
"""Build Quiet Cinematic Japan — Lessons 26–30 exhibition."""

from __future__ import annotations

import json
from pathlib import Path

import build_lessons_21_25_quiet_cinematic as shared

ROOT = Path(__file__).resolve().parents[1]
COLLECTION_ID = "lessons_26_30_quiet_cinematic"
DRAFT_PATH = (
    ROOT / "quiet_cinematic_review" / "data" / "lessons_26_30_draft.json"
)
OUT_PATH = shared.write_collection_path(ROOT, COLLECTION_ID)
SEED = 20260806


def build() -> dict:
    shared.COLLECTION_ID = COLLECTION_ID
    shared.DRAFT_PATH = DRAFT_PATH
    shared.OUT_PATH = OUT_PATH
    shared.SEED = SEED

    config = shared.build()
    scene_count = len(config["scenes"])
    soundtrack_ms = config["meta"]["soundtrackDurationMs"]
    avg_hold_ms = config["meta"]["avgHoldMs"]

    config["title"] = "Quiet Cinematic Japan — Lessons 26–30"
    config["notes"] = (
        "Curated textless journey: Quiet Cinematic Japan from Lessons 26–30. "
        "Landscape and atmosphere first; solitary figures only when they serve mood. "
        f"Ken Burns gallery profile, ~{avg_hold_ms / 1000:.0f}s holds, "
        f"silent gold crest after soundtrack. {scene_count} images · soundtrack "
        f"{soundtrack_ms / 60000:.1f} min. Draft: quiet_cinematic_review."
    )
    config["meta"].update(
        {
            "edition": "Lessons 26–30",
            "lessons": list(range(26, 31)),
            "draftPath": str(DRAFT_PATH.relative_to(ROOT)),
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
    for lesson in range(26, 31):
        count = sum(
            1 for scene in config["scenes"]
            if scene["meta"]["lesson"] == lesson
        )
        print(f"  Lesson {lesson}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
