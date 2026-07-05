"""Grade 1 Compounds — school edition shared build helpers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from grade1_kanji_common import COLOR_PALETTE, DEFAULT_EXHIBITION as GRADE1_EXHIBITION  # noqa: E402

SERIES_ID = "grade_1"
COLLECTION_PREFIX = "grade_1_compounds_school"
SERIES_SCOPE = "elementary_grade_1"
SERIES_TITLE = "Grade 1 Compounds"
CONTENT_TYPE = "compounds"
EDITION = "school"
GRADE = 1

KANJI_PER_PART = 20
PART_COUNT = 4

# ~5:07 bed — comfortable headroom for ~2:00 of cards per part.
SOUNDTRACK = "audio/grade_1_kanji_minus3db.mp3"
SOUNDTRACK_FULL = "audio/grade_1_kanji_soundtrack.mp3"

BOOKEND_IMAGE_PART1 = "images/grade_1_jukugo_1.png"
BOOKEND_IMAGE_PART2 = "images/grade_1_jukugo_2.png"
BOOKEND_IMAGE_PART3 = "images/grade_1_jukugo_3.png"
BOOKEND_IMAGE_PART4 = "images/grade_1_jukugo_4.png"

_BOOKEND_IMAGE_BY_PART: dict[int, str] = {
    1: BOOKEND_IMAGE_PART1,
    2: BOOKEND_IMAGE_PART2,
    3: BOOKEND_IMAGE_PART3,
    4: BOOKEND_IMAGE_PART4,
}

DEFAULT_EXHIBITION: dict[str, int | str | float] = {
    **GRADE1_EXHIBITION,
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

# Per-part timing tweaks (e.g. shorter intro, longer reading confirmation).
PART_EXHIBITION_OVERRIDES: dict[int, dict[str, int | str | float]] = {
    4: {
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
    """Return (part, start_index, end_index_exclusive) in fixed 20-kanji parts."""
    batches: list[tuple[int, int, int]] = []
    for part in range(1, PART_COUNT + 1):
        start = (part - 1) * KANJI_PER_PART
        end = min(start + KANJI_PER_PART, len(entries))
        if start < len(entries):
            batches.append((part, start, end))
    return batches


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
