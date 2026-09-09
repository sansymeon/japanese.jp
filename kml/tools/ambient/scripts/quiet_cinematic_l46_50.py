"""Quiet Cinematic draft for Lessons 46–50.

Visual shortlist from the lesson study images: landscape and atmosphere
first; solitary figures only when they serve mood. Target 30–38 stills
so holds stay at the usual ~70s+ Quiet Cinematic pacing.
"""

from __future__ import annotations

from pathlib import Path

import quiet_cinematic_l1_20 as l1_20

ROOT = Path(__file__).resolve().parents[1]
START, END = 46, 50
COLLECTION_ID = "lessons_46_50_quiet_cinematic"
DRAFT_PATH = ROOT / "quiet_cinematic_review" / "data" / "lessons_46_50_draft.json"
SEED = 20260904

# Explicit keepers after a visual pass of the 100 study images.
# Still-life / diagrams / close interiors omitted; harvest-family duplicates trimmed.
KEEPERS_BY_LESSON: dict[int, tuple[str, ...]] = {
    46: (
        "send_back",
        "mountain_stream",
        "submerge",
        "exchange",
        "lose",
        "storehouse",
        "look_to",
    ),
    47: (
        "gigantic",
        "power",
        "labor",
        "going",
        "man",
    ),
    48: (
        "restore",
        "journey",
        "wait",
        "boulevard",
        "delicate",
        "acquire",
    ),
    49: (
        "autumn",
        "rice_plant",
        "seasons",
        "harmony",
        "shift",
        "secret",
        "incense",
        "pear_tree",
    ),
    50: (
        "watchtower",
        "inner",
        "astray",
        "transparent",
        "chrysanthemum",
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
            item["note"] = "Visual keep (Lessons 46–50 Quiet Cinematic shortlist)"
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
                "title": "Quiet Cinematic Japan — Lessons 46–50 (draft)",
                "theme": "Quiet Cinematic Japan",
                "status": "draft-review",
                "notes": (
                    "Textless Quiet Cinematic Japan from Lessons 46–50. "
                    "Visual shortlist: landscape and atmosphere first; "
                    "solitary figures only when they serve mood."
                ),
                "lessons": list(range(START, END + 1)),
                "targetFinalCount": 30,
                "candidateCount": len(items),
                "assetsBase": "../../../assets",
                "source": "visual shortlist of kml/contents/books/book_01/lessons/lesson_46.html–lesson_50.html",
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
