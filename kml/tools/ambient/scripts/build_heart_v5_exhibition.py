#!/usr/bin/env python3
"""Build heart_v5 exhibition: gold foil bookends, 愛 first, soundtrack sync."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ASSETS = ROOT.parents[1] / "assets" / "studies"
HEART_V4 = ROOT / "collections" / "heart_v4.json"
OUT_PATH = ROOT / "collections" / "heart_v5.json"

BOOKEND_IMAGE = "bookends/lesson_32.png"
FLUTE_AUDIO = "audio/exhibition_flute_intro.mp3"
SOUNDTRACK = "audio/ambient_kanji_exhibition.mp3"

# Editorial swaps in the heart exhibition lineup.
EXHIBIT_REPLACEMENTS = {
    "L38_angry": (35, "invariably"),
    "L39_suspicious": (42, "honey"),
}

# Guardian framingScale < 1 pulls back; love is portrait — extra zoom-out.
SCENE_FRAMING: dict[str, dict[str, str | float]] = {
    "L40_love": {"imageScale": 0.74, "imageFocus": "50% 48%"},
}


def _load_heart_collection():
    script = ROOT / "scripts" / "build_heart_collection.py"
    spec = importlib.util.spec_from_file_location("build_heart_collection", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_heart_collection"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def swap_love_and_heart(scenes: list[dict]) -> list[dict]:
    """First exhibit becomes 愛; 心 exhibit stays in collection at former 愛 position."""
    scenes = list(scenes)
    heart_idx = next(i for i, s in enumerate(scenes) if s.get("id") == "L32_heart")
    love_idx = next(i for i, s in enumerate(scenes) if s.get("id") == "L40_love")
    scenes[heart_idx], scenes[love_idx] = scenes[love_idx], scenes[heart_idx]
    return scenes


def swap_exhibit_replacements(scenes: list[dict]) -> list[dict]:
    heart_collection = _load_heart_collection()
    scenes = list(scenes)
    for old_id, (lesson_num, slug) in EXHIBIT_REPLACEMENTS.items():
        idx = next((i for i, s in enumerate(scenes) if s.get("id") == old_id), None)
        if idx is None:
            raise KeyError(f"Missing exhibit id {old_id!r} in heart scenes")
        replacement = heart_collection.load_scene(lesson_num, slug, require_heart=False)
        if replacement is None:
            raise FileNotFoundError(
                f"Could not load replacement scene lesson {lesson_num:02d} slug {slug!r}"
            )
        scenes[idx] = replacement
    return scenes


def attach_image_rev(scenes: list[dict]) -> list[dict]:
    out: list[dict] = []
    for scene in scenes:
        scene = dict(scene)
        image = scene.get("image", "")
        if image.startswith("studies/"):
            path = REPO_ASSETS / Path(image).name
            if path.exists():
                scene["imageRev"] = int(path.stat().st_mtime)
        sid = scene.get("id", "")
        if sid in SCENE_FRAMING:
            scene.update(SCENE_FRAMING[sid])
        out.append(scene)
    return out


def build() -> dict:
    heart_v4 = json.loads(HEART_V4.read_text(encoding="utf-8"))
    exhibition = {
        **heart_v4["exhibition"],
        "keywordDelayMs": 3000,
        "keywordFadeMs": 5000,
        "essenceKanjiRevealMs": 7000,
        "essenceHoldMs": 12000,
        "reflectionHoldMs": 11000,
        # Gallery bridge: A exhale → B arrival; kanji bridges (no black hold).
        "imageHandoffExhaleMs": 20000,
        "imageHandoffArrivalMs": 18000,
        "kanjiBridgeFadeMs": 10000,
        "kanjiAloneHoldMs": 0,
        "finalKanjiAloneHoldMs": 6000,
        "kanjiHandoffFadeMs": 10000,
        "openingBlackBeforeMs": 2000,
        "openingFluteMs": 16000,
        "openingRevealMs": 6000,
        "openingHoldMs": 4000,
        "openingExhaleMs": 6000,
        "openingBlackAfterMs": 0,
        "closingBlackBeforeMs": 4500,
        "closingRevealMs": 9000,
        "closingHoldMs": 0,
        # Music ends with gold-heart fade — no post-soundtrack silence.
        "closingPostSoundtrackHoldMs": 0,
        "closingExhaleMs": 20000,
        "closingSilenceHoldMs": 0,
        "closingFadeToBlackMs": 13000,
        "closingBlackAfterMs": 1000,
        "exhibitBlackHoldMs": 0,
        "seamlessExhibitHandoff": True,
        # Legacy alias; imageHandoffArrivalMs drives B fade-in during gallery bridge.
        "exhibitTransitionMs": 18000,
    }
    scenes = swap_love_and_heart(heart_v4["scenes"])
    scenes = swap_exhibit_replacements(scenes)
    scenes = attach_image_rev(scenes)

    return {
        **{
            k: v
            for k, v in heart_v4.items()
            if k
            not in (
                "id",
                "title",
                "notes",
                "exhibition",
                "display",
                "meta",
                "scenes",
                "bookends",
                "soundtrack",
            )
        },
        "id": "heart_v5",
        "title": "Digital Art Exhibition – Heart 心・㣺・忄 (v5)",
        "notes": (
            "Gold foil lesson_32.png marks gallery entrance and exit. Flute intro holds on hero "
            "until audio ends; main soundtrack plays through 44 exhibits (~96 min). Closing hero "
            "holds until soundtrack ends, extra beat on closing hero, then silent hold and fade to black. "
            "Exhibits 42–43: invariably (必) and honey (蜜) replace angry and suspicious."
        ),
        "soundtrack": {"main": SOUNDTRACK},
        "bookends": {
            "opening": {
                "image": BOOKEND_IMAGE,
                "audio": FLUTE_AUDIO,
                "holdUntilAudioEnds": True,
            },
            "closing": {
                "image": BOOKEND_IMAGE,
                "holdUntilSoundtrackEnds": True,
            },
        },
        "exhibition": exhibition,
        "display": {
            **heart_v4.get("display", {}),
            "showKeyword": True,
            "verseMode": "sequential",
            "typography": "mobile-refine",
            "typographyStyle": "foundations",
        },
        "meta": {
            **heart_v4.get("meta", {}),
            "sourceCollection": "heart_v4",
            "bookendArtwork": BOOKEND_IMAGE,
            "sceneOrder": "愛 first after opening; 心 exhibit at index 43; invariably/honey at 42–43",
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    print(f"  Bookend: {BOOKEND_IMAGE}")
    print(f"  Flute: {FLUTE_AUDIO}")
    print(f"  Soundtrack: {SOUNDTRACK}")
    print(f"  First exhibit: {config['scenes'][0]['kanji']} ({config['scenes'][0]['id']})")
    heart_scene = next(s for s in config["scenes"] if s["id"] == "L32_heart")
    print(f"  Heart exhibit: index {config['scenes'].index(heart_scene)}")
    for idx in (41, 42):
        s = config["scenes"][idx]
        print(f"  Exhibit {idx}: {s['kanji']} {s['keyword']} ({s['id']}) → {s['image']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
