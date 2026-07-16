"""Grade 3 Stroke Order — timing, batching, and scene helpers."""

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
    DEFAULT_EXHIBITION as _GRADE1_STROKE_EXHIBITION,
    collection_runtime_ms,
    format_duration,
    probe_duration_ms,
    stroke_animation_ms,
)
from grade3_kanji_common import COLOR_PALETTE  # noqa: E402

# Soundtrack ~3s from start (opening black + delay), aligned with jukugo pacing.
STROKE_SOUNDTRACK_START_MS = 3000
OPENING_BLACK_BEFORE_MS = 400
OPENING_SOUNDTRACK_DELAY_MS = STROKE_SOUNDTRACK_START_MS - OPENING_BLACK_BEFORE_MS
# Playwright mux uses the source MP3 directly; trim 2 dB to sit under jukugo/kanji levels.
STROKE_SOUNDTRACK_GAIN_DB = -2.0

# Final MP4: fade audio + video to black from 9:15, then cut.
STROKE_OUTPUT_FADE_START_S = 9 * 60 + 15
STROKE_OUTPUT_FADE_DURATION_S = 10
STROKE_OUTPUT_DURATION_S = STROKE_OUTPUT_FADE_START_S + STROKE_OUTPUT_FADE_DURATION_S

DEFAULT_EXHIBITION: dict[str, int | str] = {
    **_GRADE1_STROKE_EXHIBITION,
    "openingBlackBeforeMs": OPENING_BLACK_BEFORE_MS,
    "openingSoundtrackDelayMs": OPENING_SOUNDTRACK_DELAY_MS,
}

SERIES_ID = "grade_3"
COLLECTION_PREFIX = "grade_3_strokes"
SERIES_SCOPE = "elementary_grade_3"
SERIES_TITLE = "Grade 3 Stroke Order"

# 200 kanji → 8 × 25
KANJI_PER_PART = 25
PART_COUNT = 8

SOUNDTRACK = "audio/grade_3_kanji_extended_minus3db.mp3"

# One dedicated stroke-order bookend image per part (25 kanji each).
BOOKEND_IMAGE_PART1 = "images/grade_3_stroke_orders_1.png"
BOOKEND_IMAGE_PART2 = "images/grade_3_stroke_orders_2.png"
BOOKEND_IMAGE_PART3 = "images/grade_3_stroke_orders_3.png"
BOOKEND_IMAGE_PART4 = "images/grade_3_stroke_orders_4.png"
BOOKEND_IMAGE_PART5 = "images/grade_3_stroke_orders_5.png"
BOOKEND_IMAGE_PART6 = "images/grade_3_stroke_orders_6.png"
BOOKEND_IMAGE_PART7 = "images/grade_3_stroke_orders_7.png"
BOOKEND_IMAGE_PART8 = "images/grade_3_stroke_orders_8.png"

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
        "id": f"G3S{part:02d}_{entry.slug}",
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
            "grade": 3,
        },
    }


def plan_batches(entries: list, timing: dict) -> list[tuple[int, int, int]]:
    """Return (part, start_index, end_index_exclusive) in fixed 25-kanji parts."""
    batches: list[tuple[int, int, int]] = []
    for part in range(1, PART_COUNT + 1):
        start = (part - 1) * KANJI_PER_PART
        end = min(start + KANJI_PER_PART, len(entries))
        if start < len(entries):
            batches.append((part, start, end))
    return batches
