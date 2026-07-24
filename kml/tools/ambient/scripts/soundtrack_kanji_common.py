"""Shared timing and soundtrack helpers for kanji soundtrack exhibitions."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

sys.path.insert(0, str(ROOT.parents[1] / "tools/strokes"))
SERIES_ID = "post_elementary"
COLLECTION_PREFIX = "post_elementary"
SERIES_SCOPE = "post_elementary_through_joyo"  # grade S; post-joyo is a separate series
SERIES_TITLE = "Jōyō Kanji Soundtrack"
TRACK_A = "audio/jr_high_1.mp3"
TRACK_B = "audio/jr_high_2.mp3"
SOUNDTRACK_RENDERED = "audio/jr_high_soundtrack.mp3"
TRACK_A_PART2 = "audio/jr_high_03.mp3"
TRACK_B_PART2 = "audio/jr_high_4.mp3"
SOUNDTRACK_RENDERED_PART2 = "audio/jr_high_soundtrack_02.mp3"
SOUNDTRACK_RENDERED_PART3 = "audio/jr_high_soundtrack_03.mp3"
SOUNDTRACK_RENDERED_PART4 = "audio/jr_high_soundtrack_04.mp3"
SOUNDTRACK_RENDERED_PART5 = "audio/jr_high_soundtrack_05.mp3"
SOUNDTRACK_RENDERED_PART6 = "audio/jr_high_soundtrack_06.mp3"
SOUNDTRACK_RENDERED_PART7 = "audio/jr_high_soundtrack_07.mp3"
SOUNDTRACK_RENDERED_PART8 = "audio/jr_high_soundtrack_08.mp3"
SOUNDTRACK_RENDERED_PART9 = "audio/jr_high_soundtrack_09.mp3"
SOUNDTRACK_RENDERED_PART10 = "audio/jr_high_soundtrack_10.mp3"
SOUNDTRACK_RENDERED_PART11 = "audio/jr_high_soundtrack_11.mp3"

# Cumulative kanji offsets when parts are 100 kanji each (after splitting the old 200-kanji part 2).
PART_KANJI_OFFSET: dict[int, int] = {
    1: 0, 2: 100, 3: 200, 4: 300, 5: 400, 6: 500, 7: 600, 8: 700, 9: 800, 10: 900, 11: 1000,
}

_PART2_TRACKS = (2, 3, 5, 7, 9, 11)
_SOUNDTRACK_BY_PART = {
    2: SOUNDTRACK_RENDERED_PART2,
    3: SOUNDTRACK_RENDERED_PART3,
    4: SOUNDTRACK_RENDERED_PART4,
    5: SOUNDTRACK_RENDERED_PART5,
    6: SOUNDTRACK_RENDERED_PART6,
    7: SOUNDTRACK_RENDERED_PART7,
    8: SOUNDTRACK_RENDERED_PART8,
    9: SOUNDTRACK_RENDERED_PART9,
    10: SOUNDTRACK_RENDERED_PART10,
    11: SOUNDTRACK_RENDERED_PART11,
}


def soundtrack_paths_for_part(part: int) -> tuple[str, str, str]:
    if part in _PART2_TRACKS:
        return TRACK_A_PART2, TRACK_B_PART2, _SOUNDTRACK_BY_PART[part]
    soundtrack = _SOUNDTRACK_BY_PART.get(part, SOUNDTRACK_RENDERED)
    return TRACK_A, TRACK_B, soundtrack
OPENING_IMAGE = "images/joyo_kanji.png"
CLOSING_IMAGE = "images/joyo_kanji.png"

# Continuous music-video flow — no black or slideshow holds between kanji.
DEFAULT_EXHIBITION: dict[str, int | str] = {
    "exhibitionBlackBeforeMs": 0,
    "recordingLeadMs": 3000,  # OBS lead-in (black) before opening bookend
    "strokeOrderDrawColor": "rgba(255, 255, 255, 0.88)",
    "strokeOrderFinalColor": "rgba(255, 255, 255, 0.98)",
    "openingBlackBeforeMs": 1800,
    "openingRevealMs": 4200,
    "openingHoldMs": 5300,  # hero hold before kanji animation (was 6800)
    "openingExhaleMs": 3200,
    "openingBlackAfterMs": 0,
    "openingTitleRevealMs": 2800,
    "openingTitleFadeMs": 2000,
    "openingSoundtrackDelayMs": 4400,  # 1.4s after hero + 3s recording sync
    "closingBlackBeforeMs": 1200,
    "closingRevealMs": 3800,
    "closingHoldMs": 0,
    "closingExhaleMs": 4500,
    "closingTitleRevealMs": 3200,
    "closingTitleFadeMs": 4200,
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

CONTENT_TAIL_PAD_MS = 6000


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


def chain_duration_ms(durations: tuple[int, int], segments: int, crossfade_ms: int) -> int:
    total = durations[0]
    for i in range(1, segments):
        total += durations[i % 2] - crossfade_ms
    return total


def estimate_looped_soundtrack_ms(
    track_a_ms: int,
    track_b_ms: int,
    *,
    cycles: int = 1,
    crossfade_ms: int = 5000,
    end_fade_ms: int = 4000,
) -> int:
    segments = 2 * max(1, cycles)
    body = chain_duration_ms((track_a_ms, track_b_ms), segments, crossfade_ms)
    return body


def stroke_animation_ms(stroke_count: int, timing: dict) -> int:
    if stroke_count <= 0:
        return 0
    draw = int(timing.get("strokeOrderDrawMs", 1100))
    gap = int(timing.get("strokeOrderStrokeGapMs", 1400))
    return (stroke_count - 1) * gap + draw


def exhibit_runtime_ms(scene: dict, timing: dict, *, include_intro: bool) -> int:
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


def hold_runtime_ms(timing: dict, scene_count: int) -> int:
    per_scene = sum(
        int(timing.get(k, 0))
        for k in HOLD_KEYS
        if k != "exhibitionBlackBeforeMs"
    )
    intro = int(timing.get("exhibitionBlackBeforeMs", 0)) if scene_count else 0
    return intro + per_scene * scene_count


def scale_holds_to_target(timing: dict, scenes: list[dict], target_ms: int) -> dict:
    """Adjust hold beats to land near the soundtrack content window."""
    scaled = dict(timing)
    scene_count = len(scenes)
    if scene_count <= 0 or target_ms <= 0:
        return scaled

    base = collection_runtime_ms(scenes, scaled)
    if base <= 0:
        return scaled

    fixed_ms = base - hold_runtime_ms(scaled, scene_count)
    target_holds = max(0, target_ms - fixed_ms)
    current_holds = hold_runtime_ms(scaled, scene_count)
    if current_holds <= 0:
        return scaled

    ratio = target_holds / current_holds
    per_scene_keys = [k for k in HOLD_KEYS if k != "exhibitionBlackBeforeMs"]
    for key in per_scene_keys:
        floor = 400
        scaled[key] = max(floor, int(round(int(scaled[key]) * ratio)))
    if scene_count:
        floor = 400
        scaled["exhibitionBlackBeforeMs"] = max(
            floor, int(round(int(scaled.get("exhibitionBlackBeforeMs", 0)) * ratio))
        )
    return scaled


def kanji_fit_count(
    entries: list,
    timing: dict,
    content_budget_ms: int,
) -> int:
    """How many kanji fit in the content window (real stroke SVG counts)."""
    if content_budget_ms <= 0 or not entries:
        return 0
    for n in range(len(entries), 0, -1):
        chunk, _, _ = fit_part_entries(entries[:n], 1, timing, content_budget_ms)
        if len(chunk) == n:
            return n
    return 0


def fit_part_entries(
    entries: list,
    part: int,
    timing: dict,
    budget_ms: int,
) -> tuple[list, dict, list[dict]]:
    """Return kanji slice, scaled timing, and scenes that fit the content budget."""
    chunk = list(entries)
    while chunk:
        scenes = [scene_for_entry(e, part=part, index=i) for i, e in enumerate(chunk)]
        scaled = scale_holds_to_target(timing, scenes, budget_ms)
        if collection_runtime_ms(scenes, scaled) <= budget_ms:
            return chunk, scaled, scenes
        chunk = chunk[:-1]
    return [], dict(timing), []


def scene_for_entry(entry, *, part: int, index: int) -> dict:
    return {
        "id": f"PE{part:02d}_{entry.slug}",
        "kanji": entry.kanji,
        "meta": {
            "part": part,
            "slug": entry.slug,
            "heisigNumber": entry.heisig_number,
            "indexInPart": index,
        },
    }


def format_duration(ms: int) -> str:
    seconds = max(0, ms) // 1000
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"
