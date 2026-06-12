#!/usr/bin/env python3
"""Build exhibition/lesson_40_study.json — Love first, Wide last, Gallery Seal Ending."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSON_40 = ROOT / "collections" / "archive" / "lesson_40.json"
OUT_PATH = ROOT / "exhibition" / "lesson_40_study.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_exhibition_common import exhibition_study_config, reorder_scenes  # noqa: E402

FIRST_SCENE = "love"
LAST_SCENE = "wide"


def build() -> dict:
    base = json.loads(LESSON_40.read_text(encoding="utf-8"))
    scenes = reorder_scenes(base["scenes"], first=FIRST_SCENE, last=LAST_SCENE)
    return exhibition_study_config(
        lesson=40,
        title="KML Ambient Study — Lesson 40 (Exhibition)",
        notes=(
            "Exhibition / presentation build. Love opens; Wide closes with Gallery Seal Ending "
            "(image hold, fade to black, gold 漢 seal, music resolves, end on seal)."
        ),
        scenes=scenes,
        assets_base=base["assetsBase"],
    )


def main() -> int:
    config = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    print(f"  First: {config['scenes'][0]['kanji']} ({config['scenes'][0]['id']})")
    print(f"  Last:  {config['scenes'][-1]['kanji']} ({config['scenes'][-1]['id']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
