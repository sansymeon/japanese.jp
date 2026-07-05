"""Grade 1 Stroke Order — timing, runtime estimation, and scene helpers.

Card length is driven by stroke count, not a fixed per-kanji slot:

  intro + transition + stroke animation + final hold + transition out
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parents[1]

sys.path.insert(0, str(REPO / "tools/strokes"))
from stroke_page_data import stroke_metadata  # noqa: E402

sys.path.insert(0, str(SCRIPTS))
from grade1_kanji_common import COLOR_PALETTE  # noqa: E402

SERIES_ID = "grade_1"
COLLECTION_PREFIX = "grade_1_strokes"
SERIES_SCOPE = "elementary_grade_1"
SERIES_TITLE = "Grade 1 Stroke Order"

# Fixed beats (ms) — same for every kanji card.
INTRO_REVEAL_MS = 1200
INTRO_HOLD_MS = 2200
TRANSITION_IN_MS = 600
STROKE_LAYER_FADE_MS = 500
PRE_DRAW_MS = 700
DRAW_MS = 1300
STROKE_GAP_MS = 900
POST_DRAW_MS = 350
COMPLETION_REVEAL_MS = 2200
FINAL_HOLD_MS = 600
TRANSITION_OUT_MS = 2400
PAGE_TURN_TRANSITION_MS = 800
PAGE_TURN_BLACK_HOLD_MS = 350

# Fixed batching: 80 grade-1 kanji → 4 parts × 20 kanji.
KANJI_PER_PART = 20
PART_COUNT = 4

DEFAULT_EXHIBITION: dict[str, int | str] = {
    "exhibitionBlackBeforeMs": 0,
    "strokeOrderRecognitionRevealMs": INTRO_REVEAL_MS,
    "strokeOrderRecognitionHoldMs": INTRO_HOLD_MS,
    "strokeOrderKanjiFadeOutMs": TRANSITION_IN_MS,
    "strokeOrderStrokeFadeMs": STROKE_LAYER_FADE_MS,
    "strokeOrderPreDrawPauseMs": PRE_DRAW_MS,
    "strokeOrderDrawMs": DRAW_MS,
    "strokeOrderStrokeGapMs": STROKE_GAP_MS,
    "strokeOrderPostDrawPauseMs": POST_DRAW_MS,
    "strokeOrderCompletionRevealMs": COMPLETION_REVEAL_MS,
    "strokeOrderCompletionHoldMs": FINAL_HOLD_MS,
    "strokeOrderExhibitFadeMs": TRANSITION_OUT_MS,
    # Grade 1 stroke profile uses scene meta color at runtime.
    "strokeOrderDrawColor": "rgba(44, 40, 36, 0.9)",
    "strokeOrderFinalColor": "rgba(44, 40, 36, 0.96)",
    "exhibitTransitionMs": PAGE_TURN_TRANSITION_MS,
    "exhibitBlackHoldMs": PAGE_TURN_BLACK_HOLD_MS,
    "artworkArrivalMs": 0,
    "artworkArrivalFadeMs": 0,
    "artworkAloneMs": 0,
    "openingBlackBeforeMs": 400,
    "openingRevealMs": 1200,
    "openingHoldMs": 1400,
    "openingExhaleMs": 700,
    "openingBlackAfterMs": 0,
    # Start soundtrack just before first stroke animation begins.
    "openingSoundtrackDelayMs": 10000,
}

SOUNDTRACK = "audio/grade_1_stroke_orders.mp3"

BOOKEND_IMAGE_PART1 = "images/grade_one_stroke_orders_1.png"
BOOKEND_IMAGE_PART2 = "images/grade_one_kakijun_2.png"
BOOKEND_IMAGE_PART3 = "images/grade_one_stroke_orders_3.png"
BOOKEND_IMAGE_PART4 = "images/grade_one_stroke_orders_4.png"

_BOOKEND_IMAGE_BY_PART: dict[int, str] = {
    1: BOOKEND_IMAGE_PART1,
    2: BOOKEND_IMAGE_PART2,
    3: BOOKEND_IMAGE_PART3,
    4: BOOKEND_IMAGE_PART4,
}


def collection_id(part: int) -> str:
    return f"{COLLECTION_PREFIX}_{part:02d}"


def bookend_image_for_part(part: int) -> str:
    return _BOOKEND_IMAGE_BY_PART.get(part, BOOKEND_IMAGE_PART1)


def soundtrack_path_for_part(part: int) -> str:
    return SOUNDTRACK


def entries_for_part(part: int, entries: list) -> list:
    start = (part - 1) * KANJI_PER_PART
    end = start + KANJI_PER_PART
    return entries[start:end]


def kanji_color(index: int) -> str:
    return COLOR_PALETTE[index % len(COLOR_PALETTE)]


def stroke_animation_ms(stroke_count: int, timing: dict | None = None) -> int:
    if stroke_count <= 0:
        return 0
    t = timing or DEFAULT_EXHIBITION
    draw = int(t.get("strokeOrderDrawMs", DRAW_MS))
    gap = int(t.get("strokeOrderStrokeGapMs", STROKE_GAP_MS))
    return (stroke_count - 1) * gap + draw


def exhibit_runtime_ms(scene: dict, timing: dict, *, include_intro: bool = False) -> int:
    stroke_count = scene.get("strokeOrder", {}).get("strokeCount", 0)
    total = 0
    if include_intro:
        total += int(timing.get("exhibitionBlackBeforeMs", 0))
    total += sum(
        int(timing.get(k, 0))
        for k in (
            "strokeOrderRecognitionRevealMs",
            "strokeOrderRecognitionHoldMs",
            "strokeOrderKanjiFadeOutMs",
            "strokeOrderStrokeFadeMs",
            "strokeOrderPreDrawPauseMs",
            "strokeOrderPostDrawPauseMs",
            "strokeOrderCompletionRevealMs",
            "strokeOrderCompletionHoldMs",
            "strokeOrderExhibitFadeMs",
            "exhibitTransitionMs",
            "exhibitBlackHoldMs",
        )
    )
    total += stroke_animation_ms(stroke_count, timing)
    return total


def collection_runtime_ms(scenes: list[dict], timing: dict) -> int:
    if not scenes:
        return 0
    total = exhibit_runtime_ms(scenes[0], timing, include_intro=True)
    for scene in scenes[1:]:
        total += exhibit_runtime_ms(scene, timing, include_intro=False)
    return total


def scene_for_entry(entry, *, part: int, index: int) -> dict:
    stroke = stroke_metadata(entry.slug, entry.kanji)
    return {
        "id": f"G1S{part:02d}_{entry.slug}",
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
            "grade": 1,
        },
    }


def plan_batches(entries: list, timing: dict) -> list[tuple[int, int, int]]:
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
