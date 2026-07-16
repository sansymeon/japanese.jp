"""Grade 2 Compounds — school edition shared build helpers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from grade2_kanji_common import COLOR_PALETTE, DEFAULT_EXHIBITION as GRADE2_EXHIBITION  # noqa: E402

SERIES_ID = "grade_2"
COLLECTION_PREFIX = "grade_2_compounds_school"
SERIES_SCOPE = "elementary_grade_2"
SERIES_TITLE = "Grade 2 Compounds"
CONTENT_TYPE = "compounds"
EDITION = "school"
GRADE = 2

# 161 kanji → 7 × 20 + 1 × 21
KANJI_PER_PART = 20
PART_COUNT = 8
LAST_PART_KANJI = 21

SOUNDTRACK = "audio/grade2_3_number_1_minus3db.mp3"
SOUNDTRACK_FULL = "audio/grade2_3_number_1_minus3db.mp3"

BOOKEND_IMAGE_PART1 = "images/grade_2_jukugo_1.png"
BOOKEND_IMAGE_PART2 = "images/grade_2_jukugo_2.png"
BOOKEND_IMAGE_PART3 = "images/grade_2_jukugo_3.png"
BOOKEND_IMAGE_PART4 = "images/grade_2_jukugo_4.png"
BOOKEND_IMAGE_PART5 = "images/grade_2_jukugo_5.png"
BOOKEND_IMAGE_PART6 = "images/grade_2_jukugo_6.png"
BOOKEND_IMAGE_PART7 = "images/grade_2_jukugo_7.png"
BOOKEND_IMAGE_PART8 = "images/grade_2_jukugo_8.png"

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

DEFAULT_EXHIBITION: dict[str, int | str | float] = {
    **GRADE2_EXHIBITION,
    "exhibitionBlackBeforeMs": 1500,
    "anchorWordFadeInMs": 700,
    "anchorWordHoldMs": 2500,
    "anchorReadingFadeInMs": 450,
    "anchorTransitionMs": 600,
    "anchorReadingHoldMs": 1400,
    "anchorCardFadeOutMs": 500,
    "anchorCardGapMs": 300,
    "anchorStackedWordSoftOpacity": 0.82,
    "anchorCrossfadeGhostOpacity": 0.25,
    "closingHoldMs": 3500,
    "closingSilenceHoldMs": 0,
    "closingFadeToBlackMs": 4500,
}

PART_EXHIBITION_OVERRIDES: dict[int, dict[str, int | str | float]] = {
    8: {
        "recordingLeadMs": 0,
        "openingBlackBeforeMs": 1000,
        "openingRevealMs": 3000,
        "openingHoldMs": 2500,
        "openingExhaleMs": 2200,
        "openingSoundtrackDelayMs": 1800,
        "exhibitionBlackBeforeMs": 800,
        "anchorReadingHoldMs": 1800,
    },
}


def exhibition_timing_for_part(part: int) -> dict[str, int | str | float]:
    timing = dict(DEFAULT_EXHIBITION)
    timing.update(PART_EXHIBITION_OVERRIDES.get(part, {}))
    return timing


def collection_id(part: int) -> str:
    return f"{COLLECTION_PREFIX}_{part:02d}"


def bookend_image_for_part(part: int) -> str:
    return _BOOKEND_IMAGE_BY_PART.get(part, BOOKEND_IMAGE_PART1)


def card_runtime_ms(timing: dict | None = None) -> int:
    t = timing or DEFAULT_EXHIBITION
    return sum(
        int(t[k])
        for k in (
            "anchorWordFadeInMs",
            "anchorWordHoldMs",
            "anchorReadingFadeInMs",
            "anchorReadingHoldMs",
            "anchorCardFadeOutMs",
            "anchorCardGapMs",
        )
    )


def collection_runtime_ms(scene_count: int, timing: dict | None = None) -> int:
    if scene_count <= 0:
        return 0
    t = timing or DEFAULT_EXHIBITION
    return scene_count * card_runtime_ms(t) + int(t.get("exhibitionBlackBeforeMs", 0))


def plan_batches(entries: list) -> list[tuple[int, int, int]]:
    """Return (part, start_index, end_index_exclusive) — last part holds remainder."""
    batches: list[tuple[int, int, int]] = []
    for part in range(1, PART_COUNT + 1):
        start = (part - 1) * KANJI_PER_PART
        if part < PART_COUNT:
            end = min(start + KANJI_PER_PART, len(entries))
        else:
            end = len(entries)
        if start < len(entries):
            batches.append((part, start, end))
    return batches


def part_and_index_for_display_order(display_order: int) -> tuple[int, int]:
    """Map displayOrder (1-based) to part number and 0-based indexInPart."""
    part = min((display_order - 1) // KANJI_PER_PART + 1, PART_COUNT)
    index_in_part = display_order - 1 - (part - 1) * KANJI_PER_PART
    return part, index_in_part


def batching_meta() -> dict[str, int]:
    return {
        "kanjiPerPart": KANJI_PER_PART,
        "partCount": PART_COUNT,
        "lastPartKanji": LAST_PART_KANJI,
    }


def probe_duration_ms(path: Path) -> int | None:
    if not path.is_file():
        return None
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
        ).strip()
        return int(float(out) * 1000)
    except (subprocess.CalledProcessError, OSError, ValueError):
        return None


def format_duration(ms: int) -> str:
    seconds = max(0, ms) // 1000
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def kanji_color(display_order: int) -> str:
    return COLOR_PALETTE[(display_order - 1) % len(COLOR_PALETTE)]
