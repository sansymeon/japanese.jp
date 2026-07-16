"""Grade 6 Stroke Order — timing, batching, and scene helpers."""

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
STROKE_SOUNDTRACK_GAIN_DB = 0.0

# Final MP4: content ends ~9 min; music continues on grade_6_1 (~12:30), then fade out.
STROKE_OUTPUT_FADE_START_S = 12 * 60 + 20  # 12:20
STROKE_OUTPUT_FADE_DURATION_S = 10
STROKE_OUTPUT_DURATION_S = 12 * 60 + 30  # 12:30

DEFAULT_EXHIBITION: dict[str, int | str] = {
    **_GRADE1_STROKE_EXHIBITION,
    "openingBlackBeforeMs": OPENING_BLACK_BEFORE_MS,
    "openingSoundtrackDelayMs": OPENING_SOUNDTRACK_DELAY_MS,
}

SERIES_ID = "grade_6"
COLLECTION_PREFIX = "grade_6_strokes"
SERIES_SCOPE = "elementary_grade_6"
SERIES_TITLE = "Grade 6 Stroke Order"

# 191 kanji → 8 parts: 25×7 + 16.
KANJI_PER_PART = 25
PART_COUNT = 8
BOOKEND_IMAGE_COUNT = 8
PART_KANJI_COUNTS: dict[int, int] = {
    **{p: 25 for p in range(1, 8)},
    8: 16,
}

SOUNDTRACK = "audio/grade_6_1_minus3db.mp3"

_BOOKEND_IMAGE_BY_PART: dict[int, str] = {
    part: f"images/grade_6_stroke_orders_{part}.png"
    for part in range(1, BOOKEND_IMAGE_COUNT + 1)
}


def collection_id(part: int) -> str:
    return f"{COLLECTION_PREFIX}_{part:02d}"


def bookend_image_for_part(part: int) -> str:
    return _BOOKEND_IMAGE_BY_PART.get(part, _BOOKEND_IMAGE_BY_PART[1])


def soundtrack_path_for_part(part: int) -> str:
    return SOUNDTRACK


def kanji_color(index: int) -> str:
    return COLOR_PALETTE[index % len(COLOR_PALETTE)]


def scene_for_entry(entry, *, part: int, index: int) -> dict:
    stroke = stroke_metadata(entry.slug, entry.kanji)
    return {
        "id": f"G6S{part:02d}_{entry.slug}",
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
            "grade": 6,
        },
    }


def plan_batches(entries: list, timing: dict) -> list[tuple[int, int, int]]:
    """Return (part, start_index, end_index_exclusive).

    Parts 1–7: 25 kanji; part 8: 16 kanji (191 total, 8 bookends).
    """
    batches: list[tuple[int, int, int]] = []
    start = 0
    for part in range(1, PART_COUNT + 1):
        n = PART_KANJI_COUNTS[part]
        end = min(start + n, len(entries))
        if start >= len(entries):
            break
        batches.append((part, start, end))
        start = end
    return batches
