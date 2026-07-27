#!/usr/bin/env python3
"""Apply the approved three-scene Ambient Gallery Film refinement."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "collections" / "ambient_gallery_film" / "ambient_gallery_film.json"
EXCLUDES = ROOT / "collections" / "ambient_gallery_film" / "scenic_exclude.json"
REMOVE = {"gallbladder", "convex", "concave"}


def scene_slug(scene: dict) -> str:
    return (scene.get("meta") or {}).get("slug") or Path(scene.get("image", "")).stem


def distribute_bonus(total_ms: int, count: int) -> list[int]:
    base, remainder = divmod(total_ms, count)
    return [base + (1 if i < remainder else 0) for i in range(count)]


def main() -> int:
    collection = json.loads(COLLECTION.read_text(encoding="utf-8"))
    scenes = collection["scenes"]
    found = {scene_slug(scene) for scene in scenes} & REMOVE
    if found != REMOVE:
        raise RuntimeError(f"Expected exactly {sorted(REMOVE)}, found {sorted(found)}")

    transition_ms = int(collection["exhibition"]["exhibitTransitionMs"])
    old_scene_runtime_ms = sum(int(s["artworkAloneMs"]) for s in scenes)
    old_scene_runtime_ms += max(0, len(scenes) - 1) * transition_ms

    remaining = [dict(scene) for scene in scenes if scene_slug(scene) not in REMOVE]
    new_transition_total_ms = max(0, len(remaining) - 1) * transition_ms
    new_hold_total_ms = old_scene_runtime_ms - new_transition_total_ms
    existing_hold_total_ms = sum(int(s["artworkAloneMs"]) for s in remaining)
    bonuses = distribute_bonus(
        new_hold_total_ms - existing_hold_total_ms, len(remaining)
    )
    holds = [
        int(scene["artworkAloneMs"]) + bonus
        for scene, bonus in zip(remaining, bonuses)
    ]
    for scene, hold_ms in zip(remaining, holds):
        scene["artworkAloneMs"] = hold_ms

    avg_hold_ms = new_hold_total_ms / len(remaining)
    collection["scenes"] = remaining
    collection["exhibition"]["artworkAloneMs"] = int(avg_hold_ms)
    collection["exhibition"]["kenBurnsDurationMs"] = int(avg_hold_ms + transition_ms)
    collection["meta"]["sceneCount"] = len(remaining)
    collection["meta"]["scenicExcludedCount"] = len(
        json.loads(EXCLUDES.read_text(encoding="utf-8"))["excludeSlugs"]
    )
    collection["meta"]["avgHoldMs"] = int(avg_hold_ms)
    collection["meta"]["holdMinMs"] = min(holds)
    collection["meta"]["holdMaxMs"] = max(holds)
    collection["notes"] = (
        collection["notes"]
        .replace("187 images", f"{len(remaining)} images")
        .replace("avg hold 41.6s", f"avg hold {avg_hold_ms / 1000:.1f}s")
    )

    new_scene_runtime_ms = sum(holds) + new_transition_total_ms
    if new_scene_runtime_ms != old_scene_runtime_ms:
        raise RuntimeError(
            f"Runtime changed: {old_scene_runtime_ms} → {new_scene_runtime_ms} ms"
        )

    COLLECTION.write_text(
        json.dumps(collection, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"Refined {len(scenes)} → {len(remaining)} scenes; "
        f"scene runtime unchanged at {new_scene_runtime_ms} ms; "
        f"holds {min(holds)}–{max(holds)} ms"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
