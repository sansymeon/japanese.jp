"""Shared helpers for Grade 2 Kanji Soundtrack exhibitions."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS))

SERIES_ID = "grade_2"
COLLECTION_PREFIX = "grade_2"
SERIES_SCOPE = "elementary_grade_2"
SERIES_TITLE = "Grade 2 Kanji Soundtrack"
SOUNDTRACK_MAIN = "audio/grade2_3_number_1_minus3db.mp3"

PART_KANJI_OFFSET: dict[int, int] = {1: 0, 2: 40, 3: 80, 4: 120}
PART_KANJI_COUNT: dict[int, int] = {1: 40, 2: 40, 3: 40, 4: 41}

BOOKEND_IMAGE_PART1 = "images/grade_2_part_1.png"
BOOKEND_IMAGE_PART2 = "images/grade_2_part_2.png"
BOOKEND_IMAGE_PART3 = "images/grade_2_part_3.png"
BOOKEND_IMAGE_PART4 = "images/grade_2_part_4.png"

_BOOKEND_IMAGE_BY_PART: dict[int, str] = {
    1: BOOKEND_IMAGE_PART1,
    2: BOOKEND_IMAGE_PART2,
    3: BOOKEND_IMAGE_PART3,
    4: BOOKEND_IMAGE_PART4,
}

DEFAULT_EXHIBITION: dict[str, int | str] = {
    "exhibitionBlackBeforeMs": 0,
    "recordingLeadMs": 3000,
    "openingBlackBeforeMs": 1800,
    "openingRevealMs": 4000,
    "openingHoldMs": 5000,
    "openingExhaleMs": 2800,
    "openingBlackAfterMs": 0,
    "openingSoundtrackDelayMs": 2500,
    "closingBlackBeforeMs": 1200,
    "closingRevealMs": 3800,
    "closingHoldMs": 0,
    "closingExhaleMs": 4500,
    "closingSilenceHoldMs": 2800,
    "closingBlackAfterMs": 1200,
}

CONTENT_TAIL_PAD_MS = 4000
MILESTONE_EVERY = 10

COLOR_PALETTE: tuple[str, ...] = (
    "#E53935",
    "#FB8C00",
    "#F9A825",
    "#43A047",
    "#29B6F6",
    "#1E88E5",
    "#8E24AA",
    "#EC407A",
)


def collection_id(part: int) -> str:
    return f"{COLLECTION_PREFIX}_{part:02d}"


def bookend_image_for_part(part: int) -> str:
    return _BOOKEND_IMAGE_BY_PART.get(part, BOOKEND_IMAGE_PART1)


def soundtrack_path_for_part(part: int) -> str:
    return SOUNDTRACK_MAIN


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


def content_budget_ms(soundtrack_ms: int) -> int:
    return max(0, soundtrack_ms - CONTENT_TAIL_PAD_MS)


def scene_for_entry(entry, *, part: int, index: int) -> dict:
    color_index = (part * 100 + index) % len(COLOR_PALETTE)
    return {
        "id": f"G2{part:02d}_{entry.slug}",
        "kanji": entry.kanji,
        "meta": {
            "part": part,
            "slug": entry.slug,
            "joyoIndex": entry.joyo_index,
            "heisigNumber": entry.heisig_number,
            "indexInPart": index,
            "colorIndex": color_index,
            "kanjiColor": COLOR_PALETTE[color_index],
            "milestone": (index + 1) % MILESTONE_EVERY == 0,
        },
    }


def format_duration(ms: int) -> str:
    seconds = max(0, ms) // 1000
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"
