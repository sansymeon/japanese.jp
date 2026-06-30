"""Shared helpers for Grade 1 Kanji Soundtrack exhibitions."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS))

SERIES_ID = "grade_1"
COLLECTION_PREFIX = "grade_1"
SERIES_SCOPE = "elementary_grade_1"
SERIES_TITLE = "Grade 1 Kanji Soundtrack"
TRACK_A = "audio/grade_1_kanji_1.mp3"
TRACK_B = "audio/grade_1_kanji_2.mp3"
SOUNDTRACK_MAIN = "audio/grade_1_kanji_minus3db.mp3"
# Legacy looped renders (optional --render-soundtrack)
SOUNDTRACK_RENDERED_PART1 = "audio/grade_1_kanji_soundtrack_01.mp3"
SOUNDTRACK_RENDERED_PART2 = "audio/grade_1_kanji_soundtrack_02.mp3"

PART_KANJI_OFFSET: dict[int, int] = {1: 0, 2: 40}

_SOUNDTRACK_BY_PART = {
    1: SOUNDTRACK_MAIN,
    2: SOUNDTRACK_MAIN,
}
_TRACK_BY_PART = {
    1: TRACK_A,
    2: TRACK_B,
}


def collection_id(part: int) -> str:
    return f"{COLLECTION_PREFIX}_{part:02d}"


def soundtrack_paths_for_part(part: int) -> tuple[str, str]:
    return _TRACK_BY_PART[part], _SOUNDTRACK_BY_PART[part]

# Cheerful palette — rotated per kanji in build script.
COLOR_PALETTE: tuple[str, ...] = (
    "#E53935",  # red
    "#FB8C00",  # orange
    "#F9A825",  # yellow
    "#43A047",  # green
    "#29B6F6",  # sky blue
    "#1E88E5",  # blue
    "#8E24AA",  # purple
    "#EC407A",  # pink
)

OPENING_IMAGE = "images/grade_1.png"
CLOSING_IMAGE = "images/grade_1.png"
BOOKEND_IMAGE_PART2 = "images/grade_1_part_2.png"

_BOOKEND_IMAGE_BY_PART: dict[int, str] = {
    1: OPENING_IMAGE,
    2: BOOKEND_IMAGE_PART2,
}


def bookend_image_for_part(part: int) -> str:
    return _BOOKEND_IMAGE_BY_PART.get(part, OPENING_IMAGE)

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

OPENING_OVERHEAD_MS = (
    int(DEFAULT_EXHIBITION["openingBlackBeforeMs"])
    + int(DEFAULT_EXHIBITION["openingRevealMs"])
    + int(DEFAULT_EXHIBITION["openingHoldMs"])
    + int(DEFAULT_EXHIBITION["openingExhaleMs"])
    + int(DEFAULT_EXHIBITION["openingBlackAfterMs"])
)
CLOSING_OVERHEAD_MS = (
    int(DEFAULT_EXHIBITION["closingBlackBeforeMs"])
    + int(DEFAULT_EXHIBITION["closingRevealMs"])
    + int(DEFAULT_EXHIBITION["closingHoldMs"])
    + int(DEFAULT_EXHIBITION["closingExhaleMs"])
    + int(DEFAULT_EXHIBITION["closingBlackAfterMs"])
)
CONTENT_TAIL_PAD_MS = 4000
MILESTONE_EVERY = 10


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
    # Bookend timing is wall-clock over the looped soundtrack; kanji slots use musical budget only.
    return max(0, soundtrack_ms - CONTENT_TAIL_PAD_MS)


def scene_for_entry(entry, *, part: int, index: int) -> dict:
    color_index = (part * 100 + index) % len(COLOR_PALETTE)
    return {
        "id": f"G1{part:02d}_{entry.slug}",
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
