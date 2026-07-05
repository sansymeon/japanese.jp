"""Shared helpers for Grade 6 Kanji Soundtrack exhibitions."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS))

from grade6_gojuon import pigment_for_section  # noqa: E402

SERIES_ID = "grade_6"
COLLECTION_PREFIX = "grade_6"
SERIES_SCOPE = "elementary_grade_6"
SERIES_TITLE = "Grade 6 Kanji Soundtrack"
SOUNDTRACK_PART_1 = "audio/grade_6_1_minus3db.mp3"
SOUNDTRACK_PARTS_2_4 = "audio/grade_6_1_minus3db.mp3"
SOUNDTRACK_PART_3 = "audio/grade_6_2_minus12db.mp3"

_SOUNDTRACK_BY_PART: dict[int, str] = {
    1: SOUNDTRACK_PART_1,
    2: SOUNDTRACK_PARTS_2_4,
    3: SOUNDTRACK_PART_3,
    4: SOUNDTRACK_PARTS_2_4,
}

PART_COUNT = 4

DEFAULT_EXHIBITION: dict[str, int | str] = {
    "exhibitionBlackBeforeMs": 0,
    "recordingLeadMs": 3000,
    "openingBlackBeforeMs": 0,
    "openingRevealMs": 0,
    "openingHoldMs": 0,
    "openingExhaleMs": 0,
    "openingBlackAfterMs": 0,
    "openingSoundtrackDelayMs": 0,
    "closingBlackBeforeMs": 1200,
    "closingRevealMs": 3800,
    "closingHoldMs": 0,
    "closingExhaleMs": 4500,
    "closingSilenceHoldMs": 2800,
    "closingBlackAfterMs": 1200,
}

OPENING_BOOKEND_EXHIBITION: dict[str, int] = {
    "openingBlackBeforeMs": 1800,
    "openingRevealMs": 4000,
    "openingHoldMs": 5000,
    "openingExhaleMs": 2800,
    "openingBlackAfterMs": 0,
    "openingSoundtrackDelayMs": 2500,
}

PART1_OPENING_EXHIBITION: dict[str, int] = {
    "recordingLeadMs": 5000,
    "openingBlackBeforeMs": 2200,
    "openingSoundtrackDelayMs": 3500,
}

CONTENT_TAIL_PAD_MS = 4000
MILESTONE_EVERY = 10

BOOKEND_IMAGE_PART1 = "images/grade_6_part_1.png"
BOOKEND_IMAGE_PART2 = "images/grade_6_part_2.png"
BOOKEND_IMAGE_PART3 = "images/grade_6_part_3.png"
BOOKEND_IMAGE_PART4 = "images/grade_6_part_4.png"

_BOOKEND_IMAGE_BY_PART: dict[int, str] = {
    1: BOOKEND_IMAGE_PART1,
    2: BOOKEND_IMAGE_PART2,
    3: BOOKEND_IMAGE_PART3,
    4: BOOKEND_IMAGE_PART4,
}


def collection_id(part: int) -> str:
    return f"{COLLECTION_PREFIX}_{part:02d}"


def bookend_image_for_part(part: int) -> str | None:
    return _BOOKEND_IMAGE_BY_PART.get(part)


def soundtrack_path_for_part(part: int) -> str:
    return _SOUNDTRACK_BY_PART.get(part, SOUNDTRACK_PART_1)


def exhibition_for_part(part: int, *, has_bookend: bool) -> dict[str, int | str]:
    exhibition = dict(DEFAULT_EXHIBITION)
    if part == 1:
        exhibition.update(PART1_OPENING_EXHIBITION)
    if has_bookend:
        exhibition.update(OPENING_BOOKEND_EXHIBITION)
    return exhibition


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
    return {
        "id": f"G6{part:02d}_{entry.slug}",
        "kanji": entry.kanji,
        "meta": {
            "part": part,
            "slug": entry.slug,
            "gojuonSection": entry.gojuon,
            "joyoIndex": entry.joyo_index,
            "heisigNumber": entry.heisig_number,
            "indexInPart": index,
            "kanjiColor": pigment_for_section(entry.gojuon),
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
