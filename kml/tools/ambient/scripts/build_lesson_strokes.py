#!/usr/bin/env python3
"""Build Lesson N Stroke Order Exhibition (Lesson 5 standard).

Usage:
  python3 scripts/build_lesson_strokes.py --lesson 33
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_lesson_01_stroke_order_exhibition import (  # noqa: E402
    DEFAULT_EXHIBITION,
    collection_runtime_ms,
    format_duration,
    soundtrack_duration_ms,
)
from build_lesson_05_stroke_order_exhibition import parse_lesson_scenes  # noqa: E402
from collection_paths import write_collection_path  # noqa: E402

STROKE_ORDER_SOUNDTRACK = "audio/stroke_order_extended_minus3db.mp3"


def build(lesson: int) -> dict:
    collection_id = f"lesson_{lesson:02d}_strokes"
    scenes = parse_lesson_scenes(lesson)
    if not scenes:
        raise SystemExit(f"No stroke scenes for lesson {lesson}")
    soundtrack_ms = soundtrack_duration_ms(STROKE_ORDER_SOUNDTRACK)
    timing = dict(DEFAULT_EXHIBITION)
    content_ms = collection_runtime_ms(scenes, timing)
    stroke_counts = [s["strokeOrder"]["strokeCount"] for s in scenes]
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": collection_id,
        "title": f"Lesson {lesson} — Stroke Order",
        "notes": (
            "Quiet calligraphy studio: matte black, kanji only — no labels or readings. "
            "Recognition → stroke animation → recognition → fade to black per kanji. "
            "Stroke SVG from kml/tools/strokes/pages at runtime. "
            f"No crest — soundtrack {format_duration(soundtrack_ms)} with jazz outro after exhibits."
        ),
        "soundtrack": {"main": STROKE_ORDER_SOUNDTRACK},
        "exhibition": timing,
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "japaneseReflections",
            "showKeyword": False,
            "showKanji": False,
            "showEnglish": False,
            "exhibitProfile": "strokeOrder",
        },
        "meta": {
            "family": "japaneseReflections",
            "lesson": lesson,
            "stage": "strokes",
            "sceneCount": len(scenes),
            "prototype": True,
            "avgStrokeCount": round(sum(stroke_counts) / len(stroke_counts), 1),
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
            "strokeDataRoot": "kml/tools/strokes",
        },
        "scenes": scenes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, required=True)
    args = parser.parse_args()

    config = build(args.lesson)
    cid = config["id"]
    path = write_collection_path(ROOT, cid)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    sample = config["scenes"][0]
    soundtrack_ms = config["meta"]["soundtrackDurationMs"]
    content_ms = config["meta"]["estimatedContentRuntimeMs"]
    outro_ms = max(0, soundtrack_ms - content_ms)
    print(f"Wrote {len(config['scenes'])} exhibits → {path}")
    print(f"  avg strokes: {config['meta']['avgStrokeCount']}")
    print(f"  soundtrack: {STROKE_ORDER_SOUNDTRACK} ({format_duration(soundtrack_ms)})")
    print(f"  exhibit runtime: {format_duration(content_ms)}")
    print(f"  outro pad after last kanji: ~{format_duration(outro_ms)}")
    print(f"  exhibition.html?collection={cid}")
    print(f"  sample: {sample['id']} → {sample['strokeOrder']['strokePage']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
