"""Quiet Cinematic draft for Lessons 41–45.

Visual shortlist from the lesson study images: landscape and atmosphere
first; solitary figures only when they serve mood. Target 30–38 stills
so holds stay at the usual ~70s+ Quiet Cinematic pacing.
"""

from __future__ import annotations

from pathlib import Path

import quiet_cinematic_l1_20 as l1_20

ROOT = Path(__file__).resolve().parents[1]
START, END = 41, 45
COLLECTION_ID = "lessons_41_45_quiet_cinematic"
DRAFT_PATH = ROOT / "quiet_cinematic_review" / "data" / "lessons_41_45_draft.json"
SEED = 20260828

# Explicit keepers after a visual pass of all 100 study images.
# Duplicates (wink/pocket, utmost/daring) and still-life / diagrams omitted.
KEEPERS_BY_LESSON: dict[int, tuple[str, ...]] = {
    41: (
        "capture",
        "broaden",
        "valve",
        "neglect",
        "window",
        "climax",
        "room",
        "arrival",
    ),
    42: (
        "allot",
        "current",
        "tempt",
        "mountain",
        "boulder",
        "mountain_pass",
        "crumble",
        "storm",
        "secrecy",
    ),
    43: (
        "promontory",
        "cliff",
        "pine_tree",
        "valley",
        "bathe",
        "melt",
        "run_alongside",
    ),
    44: (
        "public_hall",
        "usual",
        "waves",
        "remainder",
        "martyrdom",
        "augment",
        "split",
        "ardent",
    ),
    45: (
        "utmost",
        "snapshot",
        "holy",
        "cartoon",
        "voiced",
        "wink",
    ),
}


def keeper_slugs() -> set[str]:
    return {slug for slugs in KEEPERS_BY_LESSON.values() for slug in slugs}


def curator_items(start: int = START, end: int = END) -> list[dict]:
    wanted = {
        slug
        for lesson, slugs in KEEPERS_BY_LESSON.items()
        if start <= lesson <= end
        for slug in slugs
    }
    pool: list[dict] = []
    found: set[str] = set()
    for lesson in range(start, end + 1):
        for item in l1_20.parse_lesson(lesson):
            if item["slug"] not in wanted:
                continue
            if not l1_20.image_ok(item):
                raise SystemExit(f"Missing study image: {item['image']}")
            item["note"] = "Visual keep (Lessons 41–45 Quiet Cinematic shortlist)"
            pool.append(item)
            found.add(item["slug"])
    missing = sorted(wanted - found)
    if missing:
        raise SystemExit(f"Keepers not found in lesson HTML: {', '.join(missing)}")
    extra = sorted(found - wanted)
    if extra:
        raise SystemExit(f"Unexpected keepers: {', '.join(extra)}")
    rng = l1_20.random.Random(SEED)
    return l1_20.interleave(pool, rng)


def write_draft(items: list[dict]) -> Path:
    DRAFT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DRAFT_PATH.write_text(
        l1_20.json.dumps(
            {
                "id": COLLECTION_ID,
                "title": "Quiet Cinematic Japan — Lessons 41–45 (draft)",
                "theme": "Quiet Cinematic Japan",
                "status": "draft-review",
                "notes": (
                    "Textless Quiet Cinematic Japan from Lessons 41–45. "
                    "Visual shortlist: landscape and atmosphere first; "
                    "solitary figures only when they serve mood."
                ),
                "lessons": list(range(START, END + 1)),
                "targetFinalCount": 30,
                "candidateCount": len(items),
                "assetsBase": "../../../assets",
                "source": "visual shortlist of kml/contents/books/book_01/lessons/lesson_41.html–lesson_45.html",
                "itemCount": len(items),
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return DRAFT_PATH
