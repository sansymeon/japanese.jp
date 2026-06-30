"""Musical pacing for KML Kanji Soundtrack — calligraphy edition.

Four half-time counts per kanji (60 BPM vs 120 BPM soundtrack):
  1 fade in → 2 kanji → 3 kanji → 4 fade out to black — repeat.
"""

from __future__ import annotations

import math

SOUNDTRACK_BPM = 120.0
VISUAL_BPM = 60.0  # half-time relative to soundtrack
DEFAULT_BPM = VISUAL_BPM
COUNT_MS = int(60_000 / VISUAL_BPM)  # 1000 — one count per half-note
COUNTS_PER_KANJI = 4
MS_PER_KANJI = 4000  # four half-time counts — total unchanged
KANJI_PER_MINUTE = 60_000 // MS_PER_KANJI  # 15
KANJI_FADE_IN_MS = 2600
KANJI_HOLD_MS = 0
KANJI_FADE_OUT_MS = 1400
DEFAULT_CROSSFADE_MS = 0  # no overlap — full black between kanji


def musical_scene_runtime_ms(musical: dict) -> int:
    return (
        int(musical.get("kanjiFadeInMs", KANJI_FADE_IN_MS))
        + int(musical.get("kanjiHoldMs", KANJI_HOLD_MS))
        + int(musical.get("kanjiFadeOutMs", KANJI_FADE_OUT_MS))
    )


def musical_collection_runtime_ms(scenes: list[dict]) -> int:
    return sum(musical_scene_runtime_ms(s.get("musical", {})) for s in scenes)


def _energy_for_index(index: int, total: int) -> float:
    return 1.0 + 0.04 * math.sin(math.pi * index / max(1, total - 1))


def layout_scene_continuous(
    scene: dict,
    *,
    index: int,
    total: int,
) -> dict:
    musical = {
        "countMs": COUNT_MS,
        "countsPerKanji": COUNTS_PER_KANJI,
        "kanjiFadeInMs": KANJI_FADE_IN_MS,
        "kanjiHoldMs": KANJI_HOLD_MS,
        "kanjiFadeOutMs": KANJI_FADE_OUT_MS,
        "segmentDurationMs": MS_PER_KANJI,
        "visualBpm": VISUAL_BPM,
        "soundtrackBpm": SOUNDTRACK_BPM,
        "bpm": VISUAL_BPM,
        "energy": round(_energy_for_index(index, total), 3),
    }
    scene = dict(scene)
    scene["musical"] = musical
    return scene


def layout_musical_scenes(
    scenes: list[dict],
    content_duration_ms: int,
    *,
    bpm: float = DEFAULT_BPM,
    kanji_per_minute: int = KANJI_PER_MINUTE,
    crossfade_ms: int = DEFAULT_CROSSFADE_MS,
) -> list[dict]:
    if not scenes or content_duration_ms <= 0:
        return scenes

    n = len(scenes)
    return [layout_scene_continuous(scene, index=i, total=n) for i, scene in enumerate(scenes)]


def max_kanji_for_budget(
    budget_ms: int,
    *,
    kanji_per_minute: int = KANJI_PER_MINUTE,
    crossfade_ms: int = DEFAULT_CROSSFADE_MS,
    avg_scene_ms: int | None = None,
) -> int:
    if budget_ms <= 0:
        return 0
    scene_ms = avg_scene_ms or MS_PER_KANJI
    return max(1, budget_ms // scene_ms)


def fit_musical_part_entries(
    entries: list,
    part: int,
    budget_ms: int,
    *,
    bpm: float,
    scene_for_entry,
    kanji_per_minute: int = KANJI_PER_MINUTE,
    crossfade_ms: int = DEFAULT_CROSSFADE_MS,
) -> tuple[list, list[dict]]:
    limit = min(
        len(entries),
        max_kanji_for_budget(
            budget_ms, kanji_per_minute=kanji_per_minute, crossfade_ms=crossfade_ms
        ),
    )
    chunk = list(entries[:limit])
    while chunk:
        scenes = [scene_for_entry(e, part=part, index=i) for i, e in enumerate(chunk)]
        scenes = layout_musical_scenes(
            scenes,
            budget_ms,
            bpm=bpm,
            kanji_per_minute=kanji_per_minute,
            crossfade_ms=crossfade_ms,
        )
        if musical_collection_runtime_ms(scenes) <= budget_ms:
            return chunk, scenes
        chunk = chunk[:-1]
    return [], []


def estimate_kanji_per_part(
    entries: list,
    budget_ms: int,
    *,
    bpm: float,
    scene_for_entry,
    kanji_per_minute: int = KANJI_PER_MINUTE,
) -> int:
    if budget_ms <= 0 or not entries:
        return 0
    limit = min(
        len(entries),
        max_kanji_for_budget(budget_ms, kanji_per_minute=kanji_per_minute),
    )
    for n in range(limit, 0, -1):
        chunk, scenes = fit_musical_part_entries(
            entries[:n],
            1,
            budget_ms,
            bpm=bpm,
            scene_for_entry=scene_for_entry,
            kanji_per_minute=kanji_per_minute,
        )
        if len(chunk) == n:
            return n
    return 0
