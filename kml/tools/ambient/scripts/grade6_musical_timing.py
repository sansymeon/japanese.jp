"""Musical pacing for Grade 6 — snappier kanji holds, beds tuned per part length."""

from __future__ import annotations

import math

from grade1_musical_timing import (  # noqa: F401
    CROSSFADE_MS,
    DEFAULT_BPM,
    KANJI_FADE_IN_MS,
    fit_musical_entries as _fit_musical_entries,
    musical_collection_runtime_ms,
    musical_scene_runtime_ms,
)

# Snappier center hold; on long beds the fade-out absorbs the time (same ~6.35 s bar).
KANJI_HOLD_MS = 1000
KANJI_FADE_OUT_MS = 2800
MS_PER_KANJI = KANJI_FADE_IN_MS + KANJI_HOLD_MS + KANJI_FADE_OUT_MS - CROSSFADE_MS

KANJI_PER_MINUTE = max(1, 60_000 // MS_PER_KANJI)


def musical_params_for_part(part: int) -> dict[str, int]:
    return {
        "kanjiFadeInMs": KANJI_FADE_IN_MS,
        "kanjiHoldMs": KANJI_HOLD_MS,
        "kanjiFadeOutMs": KANJI_FADE_OUT_MS,
        "crossfadeMs": CROSSFADE_MS,
        "segmentDurationMs": MS_PER_KANJI,
    }


def ms_per_kanji_for_part(part: int) -> int:
    return musical_params_for_part(part)["segmentDurationMs"]


def _energy_for_index(index: int, total: int) -> float:
    return 1.0 + 0.03 * math.sin(math.pi * index / max(1, total - 1))


def layout_scene_continuous(scene: dict, *, index: int, total: int, part: int) -> dict:
    params = musical_params_for_part(part)
    musical = {
        **params,
        "bpm": DEFAULT_BPM,
        "energy": round(_energy_for_index(index, total), 3),
    }
    scene = dict(scene)
    scene["musical"] = musical
    return scene


def layout_musical_scenes(scenes: list[dict], *, part: int) -> list[dict]:
    n = len(scenes)
    return [layout_scene_continuous(scene, index=i, total=n, part=part) for i, scene in enumerate(scenes)]


def max_kanji_for_budget(budget_ms: int, *, part: int) -> int:
    if budget_ms <= 0:
        return 0
    return max(1, budget_ms // ms_per_kanji_for_part(part))


def fit_musical_entries(
    entries: list,
    budget_ms: int,
    *,
    part: int,
    scene_for_entry,
) -> tuple[list, list[dict]]:
    slot_ms = ms_per_kanji_for_part(part)
    limit = min(len(entries), max_kanji_for_budget(budget_ms, part=part))
    chunk = list(entries[:limit])
    while chunk:
        scenes = [scene_for_entry(e, index=i) for i, e in enumerate(chunk)]
        scenes = layout_musical_scenes(scenes, part=part)
        if musical_collection_runtime_ms(scenes) <= budget_ms:
            scenes = tune_scenes_to_budget(scenes, budget_ms, part=part)
            return chunk, scenes
        chunk = chunk[:-1]
    return [], []


def tune_scenes_to_budget(scenes: list[dict], budget_ms: int, *, part: int) -> list[dict]:
    """Spread leftover bed time into per-kanji holds."""
    if not scenes:
        return scenes
    runtime = musical_collection_runtime_ms(scenes)
    slack = budget_ms - runtime
    if slack <= 0:
        return scenes
    extra_hold = slack // len(scenes)
    if extra_hold <= 0:
        return scenes
    tuned: list[dict] = []
    for scene in scenes:
        scene = dict(scene)
        musical = dict(scene.get("musical") or {})
        musical["kanjiHoldMs"] = int(musical.get("kanjiHoldMs", KANJI_HOLD_MS)) + extra_hold
        musical["segmentDurationMs"] = musical_scene_runtime_ms(musical)
        scene["musical"] = musical
        tuned.append(scene)
    return tuned
