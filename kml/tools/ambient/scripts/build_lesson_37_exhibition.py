#!/usr/bin/env python3
"""Build exhibition/lesson_37_foundations.json — original order, Gallery Seal Ending."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDY_PATH = ROOT / "collections" / "lesson_37_foundations.json"
OUT_PATH = ROOT / "exhibition" / "lesson_37_foundations.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from foundations_exhibition_common import exhibition_foundations_config  # noqa: E402


def build() -> dict:
    if not STUDY_PATH.is_file():
        raise FileNotFoundError(
            f"Missing {STUDY_PATH}. Run: python3 scripts/build_lesson_37_foundations.py"
        )
    study = json.loads(STUDY_PATH.read_text(encoding="utf-8"))
    config = exhibition_foundations_config(
        lesson=37,
        title="KML Ambient Foundations — Lesson 37 (Exhibition)",
        notes=(
            "Exhibition / presentation build. Original lesson order; "
            "Remain closes with Gallery Seal Ending "
            "(image hold, fade to black, gold 漢 seal, music resolves, end on seal). "
            "Soundtrack: Study Version 2."
        ),
        scenes=study["scenes"],
        assets_base=study["assetsBase"],
    )
    config["soundtrack"] = study["soundtrack"]
    return config


def main() -> int:
    config = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    print(f"  First: {config['scenes'][0]['kanji']} ({config['scenes'][0]['id']})")
    print(f"  Last:  {config['scenes'][-1]['kanji']} ({config['scenes'][-1]['id']})")
    print(f"  Audio: {config['soundtrack']['main']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
