#!/usr/bin/env python3
"""Build Lesson 1 Stroke Order Exhibition (prototype).

Recognition → stroke animation → recognition on matte black.
Stroke SVG loaded from kml/tools/strokes/pages at runtime.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
LESSON = 1
COLLECTION_ID = "lesson_01_strokes"

sys.path.insert(0, str(REPO / "tools/strokes"))
from stroke_page_data import stroke_metadata  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import write_collection_path  # noqa: E402
from build_lesson_01_gallery import soundtrack_duration_ms  # noqa: E402

OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)

STROKE_ORDER_SOUNDTRACK = "audio/stroke_order_minus3db.mp3"

DEFAULT_EXHIBITION = {
    "exhibitionBlackBeforeMs": 2500,
    "strokeOrderRecognitionRevealMs": 2200,
    "strokeOrderRecognitionHoldMs": 2800,
    "strokeOrderKanjiFadeOutMs": 3200,
    "strokeOrderStrokeFadeMs": 1600,
    "strokeOrderPreDrawPauseMs": 500,
    "strokeOrderDrawMs": 1200,
    "strokeOrderStrokeGapMs": 1500,
    "strokeOrderPostDrawPauseMs": 1600,
    "strokeOrderCompletionRevealMs": 1400,
    "strokeOrderCompletionHoldMs": 3000,
    "strokeOrderExhibitFadeMs": 3200,
    "strokeOrderDrawColor": "rgba(232, 224, 212, 0.92)",
    "strokeOrderFinalColor": "rgba(245, 240, 232, 0.96)",
    "exhibitTransitionMs": 0,
    "exhibitBlackHoldMs": 0,
    "artworkArrivalMs": 0,
    "artworkArrivalFadeMs": 0,
    "artworkAloneMs": 0,
    "openingBlackBeforeMs": 0,
    "openingRevealMs": 0,
    "openingHoldMs": 0,
    "openingExhaleMs": 0,
    "openingBlackAfterMs": 0,
}

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)


def parse_lesson_scenes(lesson: int) -> list[dict]:
    html_path = REPO / "contents/books/book_01/lessons" / f"lesson_{lesson:02d}.html"
    html = html_path.read_text(encoding="utf-8")
    scenes: list[dict] = []
    for block in SECTION_RE.findall(html):
        kanji_m = re.search(r'data-kanji="([^"]+)"', block)
        slug_m = re.search(r'data-slug="([^"]+)"', block)
        if not (kanji_m and slug_m):
            continue
        slug = slug_m.group(1)
        stroke = stroke_metadata(slug, kanji_m.group(1))
        scenes.append(
            {
                "id": f"L{lesson:02d}_{slug}",
                "kanji": kanji_m.group(1),
                "strokeOrder": stroke,
                "meta": {"lesson": lesson, "slug": slug, "prototype": True},
            }
        )
    return scenes


def stroke_animation_ms(stroke_count: int, timing: dict) -> int:
    if stroke_count <= 0:
        return 0
    draw = timing.get("strokeOrderDrawMs", 900)
    gap = timing.get("strokeOrderStrokeGapMs", 1100)
    return (stroke_count - 1) * gap + draw


def exhibit_runtime_ms(scene: dict, timing: dict, *, include_intro: bool) -> int:
    stroke_count = scene.get("strokeOrder", {}).get("strokeCount", 0)
    total = 0
    if include_intro:
        total += timing.get("exhibitionBlackBeforeMs", 0)
    total += sum(
        timing.get(k, 0)
        for k in (
            "strokeOrderRecognitionRevealMs",
            "strokeOrderRecognitionHoldMs",
            "strokeOrderKanjiFadeOutMs",
            "strokeOrderStrokeFadeMs",
            "strokeOrderPreDrawPauseMs",
            "strokeOrderPostDrawPauseMs",
            "strokeOrderCompletionRevealMs",
            "strokeOrderCompletionHoldMs",
            "strokeOrderExhibitFadeMs",
        )
    )
    total += stroke_animation_ms(stroke_count, timing)
    return total


def collection_runtime_ms(scenes: list[dict], timing: dict) -> int:
    if not scenes:
        return 0
    total = exhibit_runtime_ms(scenes[0], timing, include_intro=True)
    for scene in scenes[1:]:
        total += exhibit_runtime_ms(scene, timing, include_intro=False)
    return total


def format_duration(ms: int) -> str:
    seconds = max(0, ms) // 1000
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def build() -> dict:
    scenes = parse_lesson_scenes(LESSON)
    soundtrack_ms = soundtrack_duration_ms(STROKE_ORDER_SOUNDTRACK)
    timing = dict(DEFAULT_EXHIBITION)
    content_ms = collection_runtime_ms(scenes, timing)
    stroke_counts = [s["strokeOrder"]["strokeCount"] for s in scenes]
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": COLLECTION_ID,
        "title": "Lesson 1 — Stroke Order (Prototype)",
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
            "lesson": LESSON,
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
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    sample = config["scenes"][0]
    soundtrack_ms = config["meta"]["soundtrackDurationMs"]
    content_ms = config["meta"]["estimatedContentRuntimeMs"]
    outro_ms = max(0, soundtrack_ms - content_ms)
    print(f"Wrote {len(config['scenes'])} exhibits → {OUT_PATH}")
    print(f"  avg strokes: {config['meta']['avgStrokeCount']}")
    print(f"  stroke pages: kml/tools/strokes/pages/")
    print(f"  soundtrack: {STROKE_ORDER_SOUNDTRACK} ({format_duration(soundtrack_ms)})")
    print(f"  exhibit runtime: {format_duration(content_ms)}")
    print(f"  outro pad after last kanji: ~{format_duration(outro_ms)}")
    print(f"  exhibition.html?collection={COLLECTION_ID}")
    print(f"  sample: {sample['id']} → {sample['strokeOrder']['strokePage']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
