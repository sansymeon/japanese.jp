"""Musical pacing for Grade 1 Kanji Soundtrack — relaxed cheerful edition.

~6.35 s per kanji: slower fades, brief crossfade overlap only.
"""

from __future__ import annotations

import math

MS_PER_KANJI = 6350
KANJI_PER_MINUTE = max(1, 60_000 // MS_PER_KANJI)
KANJI_FADE_IN_MS = 3000
KANJI_HOLD_MS = 1600
KANJI_FADE_OUT_MS = 2200
CROSSFADE_MS = 450
DEFAULT_BPM = 60.0


def musical_scene_runtime_ms(musical: dict) -> int:
    fade_in = int(musical.get("kanjiFadeInMs", KANJI_FADE_IN_MS))
    hold = int(musical.get("kanjiHoldMs", KANJI_HOLD_MS))
    fade_out = int(musical.get("kanjiFadeOutMs", KANJI_FADE_OUT_MS))
    crossfade = int(musical.get("crossfadeMs", CROSSFADE_MS))
    if crossfade > 0 and fade_out > 0:
        return fade_in + hold + fade_out - crossfade
    return fade_in + hold + fade_out


def musical_collection_runtime_ms(scenes: list[dict]) -> int:
    if not scenes:
        return 0
    total = musical_scene_runtime_ms(scenes[0].get("musical", {}))
    for scene in scenes[1:]:
        total += musical_scene_runtime_ms(scene.get("musical", {}))
    return total


def _energy_for_index(index: int, total: int) -> float:
    return 1.0 + 0.03 * math.sin(math.pi * index / max(1, total - 1))


def layout_scene_continuous(scene: dict, *, index: int, total: int) -> dict:
    musical = {
        "kanjiFadeInMs": KANJI_FADE_IN_MS,
        "kanjiHoldMs": KANJI_HOLD_MS,
        "kanjiFadeOutMs": KANJI_FADE_OUT_MS,
        "crossfadeMs": CROSSFADE_MS,
        "segmentDurationMs": MS_PER_KANJI,
        "bpm": DEFAULT_BPM,
        "energy": round(_energy_for_index(index, total), 3),
    }
    scene = dict(scene)
    scene["musical"] = musical
    return scene


def layout_musical_scenes(scenes: list[dict]) -> list[dict]:
    n = len(scenes)
    return [layout_scene_continuous(scene, index=i, total=n) for i, scene in enumerate(scenes)]


def max_kanji_for_budget(budget_ms: int) -> int:
    if budget_ms <= 0:
        return 0
    return max(1, budget_ms // MS_PER_KANJI)


def fit_musical_entries(
    entries: list,
    budget_ms: int,
    *,
    scene_for_entry,
) -> tuple[list, list[dict]]:
    limit = min(len(entries), max_kanji_for_budget(budget_ms))
    chunk = list(entries[:limit])
    while chunk:
        scenes = [scene_for_entry(e, index=i) for i, e in enumerate(chunk)]
        scenes = layout_musical_scenes(scenes)
        if musical_collection_runtime_ms(scenes) <= budget_ms:
            return chunk, scenes
        chunk = chunk[:-1]
    return [], []
