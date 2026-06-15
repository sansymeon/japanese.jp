#!/usr/bin/env python3
"""Build heart_v5 exhibition: gold foil bookends, 愛 first, soundtrack sync."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEART_V4 = ROOT / "collections" / "heart_v4.json"
OUT_PATH = ROOT / "collections" / "heart_v5.json"

BOOKEND_IMAGE = "bookends/lesson_32.png"
FLUTE_AUDIO = "audio/flute_intro.mp3"
SOUNDTRACK = "audio/ambient_kanji_exhibition.mp3"

# Per-scene Ken Burns framing (object-position + scale)
IMAGE_FRAMING_OVERRIDES: dict[str, dict[str, str | float]] = {
    "L34_melancholy": {
        # Shift away from top-left wind chime; show rainy mountain through window
        "imageFocus": "56% 54%",
        "imageScale": 0.9,
    },
}


def swap_love_and_heart(scenes: list[dict]) -> list[dict]:
    """First exhibit becomes 愛; 心 exhibit stays in collection at former 愛 position."""
    scenes = list(scenes)
    heart_idx = next(i for i, s in enumerate(scenes) if s.get("id") == "L32_heart")
    love_idx = next(i for i, s in enumerate(scenes) if s.get("id") == "L40_love")
    scenes[heart_idx], scenes[love_idx] = scenes[love_idx], scenes[heart_idx]
    return scenes


def build() -> dict:
    heart_v4 = json.loads(HEART_V4.read_text(encoding="utf-8"))
    exhibition = {
        **heart_v4["exhibition"],
        "keywordDelayMs": 3000,
        "keywordFadeMs": 5000,
        "essenceKanjiRevealMs": 2500,
        "essenceHoldMs": 0,
        "openingBlackBeforeMs": 2000,
        "openingFluteMs": 16000,
        "openingRevealMs": 6000,
        "openingHoldMs": 4000,
        "openingExhaleMs": 6000,
        "openingBlackAfterMs": 0,
        "closingRevealMs": 8000,
        "closingHoldMs": 0,
        "closingExhaleMs": 20000,
        "closingSilenceHoldMs": 5000,
        "closingFadeToBlackMs": 12000,
        "closingBlackAfterMs": 2000,
    }
    scenes = swap_love_and_heart(heart_v4["scenes"])
    for scene in scenes:
        override = IMAGE_FRAMING_OVERRIDES.get(scene.get("id", ""))
        if override:
            scene.update(override)

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
            "returns and holds until soundtrack ends, then silent hold and fade to black."
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
        },
        "meta": {
            **heart_v4.get("meta", {}),
            "sourceCollection": "heart_v4",
            "bookendArtwork": BOOKEND_IMAGE,
            "sceneOrder": "愛 first after opening; 心 exhibit at index 43",
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
