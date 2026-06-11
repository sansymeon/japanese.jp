#!/usr/bin/env python3
"""Build heart_v4 exhibition from heart_v3 with fixed kanji (opacity-only text motion)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEART_V3 = ROOT / "collections" / "heart_v3.json"
OUT_PATH = ROOT / "collections" / "heart_v4.json"


def build() -> dict:
    heart_v3 = json.loads(HEART_V3.read_text(encoding="utf-8"))

    return {
        **{k: v for k, v in heart_v3.items() if k not in ("id", "title", "notes", "display", "meta")},
        "id": "heart_v4",
        "title": "Digital Art Exhibition – Heart 心・㣺・忄 (Fixed Kanji)",
        "notes": (
            "heart_v3 exhibition with fixed kanji: no drift, floating, or slide transitions on text. "
            "Motion comes only from image Ken Burns and opacity fades. Scenes unchanged from heart_v2."
        ),
        "display": {
            **heart_v3.get("display", {}),
            "fixedKanji": True,
        },
        "meta": {
            **heart_v3.get("meta", {}),
            "sourceCollection": "heart_v3",
            "fixedKanji": True,
        },
        "scenes": heart_v3["scenes"],
    }


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
