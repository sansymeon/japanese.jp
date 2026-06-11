#!/usr/bin/env python3
"""Build heart_v3 exhibition collection from heart_v2 scenes (unchanged content)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEART_V2 = ROOT / "collections" / "heart_v2.json"
LESSON_40_EXHIBITION = ROOT / "collections" / "archive" / "lesson_40_exhibition.json"
OUT_PATH = ROOT / "collections" / "heart_v3.json"


def build() -> dict:
    heart = json.loads(HEART_V2.read_text(encoding="utf-8"))
    lesson_ex = json.loads(LESSON_40_EXHIBITION.read_text(encoding="utf-8"))

    exhibition = {
        **lesson_ex["exhibition"],
        "openingBlackBeforeMs": 3000,
        "openingRevealMs": 9000,
        "openingHoldMs": 14000,
        "openingExhaleMs": 16000,
        "closingRevealMs": 10000,
        "closingHoldMs": 18000,
        "closingExhaleMs": 26000,
        "closingBlackAfterMs": 6000,
    }

    return {
        "id": "heart_v3",
        "title": "Digital Art Exhibition – Heart 心・㣺・忄",
        "presentation": "exhibition",
        "notes": (
            "Gallery presentation of heart_v2 scenes. Opening and closing bookends: 心 on black. "
            "Scenes are identical to heart_v2; only exhibition timing and bookends differ."
        ),
        "assetsBase": heart["assetsBase"],
        "exhibition": exhibition,
        "bookends": {
            "opening": {"kanji": "心"},
            "closing": {"kanji": "心"},
        },
        "display": {
            "loop": False,
            "hideChrome": True,
        },
        "meta": {
            **heart.get("meta", {}),
            "sourceCollection": "heart_v2",
            "presentation": "exhibition",
        },
        "scenes": heart["scenes"],
    }


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
