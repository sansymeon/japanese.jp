#!/usr/bin/env python3
"""Two-scene Heart prototype: 愛 → 忘 loop for handoff + verse-plate QA."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEART_V5 = ROOT / "collections" / "heart_v5.json"
OUT_PATH = ROOT / "collections" / "heart_v5_transition_prototype.json"

# Optional ?timingScale= on URL for fast passes; prototype uses production heart_v5 pacing.


def build() -> dict:
    heart = json.loads(HEART_V5.read_text(encoding="utf-8"))
    scenes = heart["scenes"][:2]
    return {
        **heart,
        "id": "heart_v5_transition_prototype",
        "title": "Heart — transition QA (愛 → 忘)",
        "notes": (
            "Two-scene loop: love → forget gallery-bridge handoff. Same pacing as heart_v5. "
            "Preview with music: exhibition.html?collection=heart_v5_transition_prototype&skipBookends=1 "
            "(add &timingScale=0.1 for a quick pass)."
        ),
        "soundtrack": dict(heart.get("soundtrack") or {}),
        "bookends": {},
        "exhibition": dict(heart["exhibition"]),
        "display": {
            **heart["display"],
            "loop": True,
        },
        "meta": {
            **heart["meta"],
            "prototype": True,
            "sceneCount": len(scenes),
            "sourceCollection": "heart_v5",
            "qa": "handoff + verse shadow fade",
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    print("  Preview (production pacing — ~3.5 min per exhibit):")
    print("    exhibition.html?collection=heart_v5_transition_prototype&skipBookends=1")
    print("  Quick pass:")
    print("    …&timingScale=0.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
