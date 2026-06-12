#!/usr/bin/env python3
"""Build collections/lesson_40_study.json — YouTube (original order, concert ending, loops)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSON_40 = ROOT / "collections" / "archive" / "lesson_40.json"
OUT_PATH = ROOT / "collections" / "lesson_40_study.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_exhibition_common import youtube_study_config  # noqa: E402


def build() -> dict:
    base = json.loads(LESSON_40.read_text(encoding="utf-8"))
    return youtube_study_config(
        lesson=40,
        title="KML Ambient Study — Lesson 40",
        notes=(
            "YouTube / loop build. Original lesson order. Last card: kanji/verse fade to "
            "image-only concert until music ends, then fade to black and loop."
        ),
        scenes=base["scenes"],
        assets_base=base["assetsBase"],
    )


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
