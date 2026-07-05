"""Grade 2 Stroke Order — timing, batching, and scene helpers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parents[1]

sys.path.insert(0, str(REPO / "tools/strokes"))
from stroke_page_data import stroke_metadata  # noqa: E402

sys.path.insert(0, str(SCRIPTS))
from grade1_stroke_order_common import (  # noqa: E402
    DEFAULT_EXHIBITION,
    collection_runtime_ms,
    exhibit_runtime_ms,
    format_duration,
    probe_duration_ms,
    stroke_animation_ms,
)
from grade2_kanji_common import COLOR_PALETTE  # noqa: E402

SERIES_ID = "grade_2"
COLLECTION_PREFIX = "grade_2_strokes"
SERIES_SCOPE = "elementary_grade_2"
SERIES_TITLE = "Grade 2 Stroke Order"

# 161 kanji → 7 × 20 + 1 × 21
KANJI_PER_PART = 20
PART_COUNT = 8

SOUNDTRACK = "audio/grade_2_stroke_order.mp3"

BOOKEND_IMAGE_PART1 = "images/grade_2_stroke_orders_1.png"
BOOKEND_IMAGE_PART2 = "images/grade_2_kakijun_2.png"
BOOKEND_IMAGE_PART3 = "images/grade_2_stroke_orders_3.png"
BOOKEND_IMAGE_PART4 = "images/grade_2_stroke_orders_4.png"
BOOKEND_IMAGE_PART5 = "images/grade_2_stroke_orders_5.png"
BOOKEND_IMAGE_PART6 = "images/grade_2_stroke_orders_6.png"
BOOKEND_IMAGE_PART7 = "images/grade_2_stroke_orders_7.png"
BOOKEND_IMAGE_PART8 = "images/grade_2_stroke_orders_8.png"

_BOOKEND_IMAGE_BY_PART: dict[int, str] = {
    1: BOOKEND_IMAGE_PART1,
    2: BOOKEND_IMAGE_PART2,
    3: BOOKEND_IMAGE_PART3,
    4: BOOKEND_IMAGE_PART4,
    5: BOOKEND_IMAGE_PART5,
    6: BOOKEND_IMAGE_PART6,
    7: BOOKEND_IMAGE_PART7,
    8: BOOKEND_IMAGE_PART8,
}


def collection_id(part: int) -> str:
    return f"{COLLECTION_PREFIX}_{part:02d}"


def bookend_image_for_part(part: int) -> str:
    return _BOOKEND_IMAGE_BY_PART.get(part, BOOKEND_IMAGE_PART1)


def soundtrack_path_for_part(part: int) -> str:
    return SOUNDTRACK


def kanji_color(index: int) -> str:
    return COLOR_PALETTE[index % len(COLOR_PALETTE)]


def scene_for_entry(entry, *, part: int, index: int) -> dict:
    stroke = stroke_metadata(entry.slug, entry.kanji)
    return {
        "id": f"G2S{part:02d}_{entry.slug}",
        "kanji": entry.kanji,
        "strokeOrder": stroke,
        "meta": {
            "part": part,
            "slug": entry.slug,
            "joyoIndex": entry.joyo_index,
            "heisigNumber": entry.heisig_number,
            "strokeCount": entry.strokes,
            "indexInPart": index,
            "kanjiColor": kanji_color(index),
            "grade": 2,
        },
    }


def plan_batches(entries: list, timing: dict) -> list[tuple[int, int, int]]:
    """Return (part, start_index, end_index_exclusive) — last part holds remainder."""
    batches: list[tuple[int, int, int]] = []
    for part in range(1, PART_COUNT + 1):
        start = (part - 1) * KANJI_PER_PART
        if part < PART_COUNT:
            end = start + KANJI_PER_PART
        else:
            end = len(entries)
        if start < len(entries):
            batches.append((part, start, end))
    return batches
