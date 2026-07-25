#!/usr/bin/env python3
"""Build Lesson N Compounds Exhibition (Lesson 5 timing/display; auto from compounds HTML).

Usage:
  python3 scripts/build_lesson_compounds.py --lesson 33
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_lesson_05_compounds_exhibition import (  # noqa: E402
    DEFAULT_EXHIBITION,
    SILENT_CREST_BOOKENDS,
    collection_runtime_ms,
    format_duration,
)
from build_lesson_05_gallery import (  # noqa: E402
    IMAGE_OVERRIDES,
    gallery_camera,
    image_rev,
    soundtrack_duration_ms,
)
from collection_paths import write_collection_path  # noqa: E402
from compounds_page_data import lesson_compounds  # noqa: E402

COMPOUNDS_SOUNDTRACK = "audio/compounds_minus3db.mp3"
SECTION_RE = re.compile(r'<section class="kanji-entry"(.*?)</section>', re.DOTALL)
MAX_COMPOUNDS = 4


def parse_lesson_scenes(lesson: int) -> list[dict]:
    html_path = REPO / "contents/books/book_01/lessons" / f"lesson_{lesson:02d}.html"
    html = html_path.read_text(encoding="utf-8")
    by_kanji = lesson_compounds(lesson)
    scenes: list[dict] = []

    for block in SECTION_RE.findall(html):
        kanji_m = re.search(r'data-kanji="([^"]+)"', block)
        slug_m = re.search(r'data-slug="([^"]+)"', block)
        keyword_m = re.search(r'<span class="kanji-keyword">([^<]+)</span>', block)
        img_m = re.search(r"assets/studies/([^\"']+\.png)", block)
        if not (kanji_m and slug_m):
            continue

        slug = slug_m.group(1)
        kanji = kanji_m.group(1)
        keyword = keyword_m.group(1).strip() if keyword_m else slug.replace("_", " ")
        image = f"studies/{img_m.group(1)}" if img_m else f"studies/{slug}.png"
        steps = [dict(item) for item in by_kanji.get(kanji, [])[:MAX_COMPOUNDS]]
        if not steps:
            raise KeyError(f"No compounds found for kanji {kanji} ({slug})")

        cam = gallery_camera(slug)
        scene = {
            "id": f"L{lesson:02d}_{slug}",
            "kanji": kanji,
            "keyword": keyword,
            "image": image,
            "galleryCamera": cam,
            "compounds": {"steps": steps},
            "meta": {"lesson": lesson, "slug": slug, "prototype": True},
        }
        if cam.get("focus"):
            scene["imageFocus"] = cam["focus"]
        if slug in IMAGE_OVERRIDES:
            scene.update(IMAGE_OVERRIDES[slug])
        rev = image_rev(image)
        if rev is not None:
            scene["imageRev"] = rev
        scenes.append(scene)
    return scenes


def build(lesson: int) -> dict:
    collection_id = f"lesson_{lesson:02d}_compounds"
    scenes = parse_lesson_scenes(lesson)
    if not scenes:
        raise SystemExit(f"No compound scenes for lesson {lesson}")
    step_counts = [len(s["compounds"]["steps"]) for s in scenes]
    soundtrack_ms = soundtrack_duration_ms(COMPOUNDS_SOUNDTRACK)
    timing = dict(DEFAULT_EXHIBITION)
    content_ms = collection_runtime_ms(scenes, timing)
    source = f"kml/contents/books/book_01/compounds/lesson_{lesson:02d}.html"
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": collection_id,
        "title": f"Lesson {lesson} — Compounds",
        "notes": (
            "Gallery artwork per kanji: target kanji → familiar compounds with furigana. "
            f"Auto-curated from {source} (Lesson 5 exhibition timing + mobile-refine). "
            f"~{sum(step_counts) / len(step_counts):.0f} compounds per exhibit. "
            f"Soundtrack {format_duration(soundtrack_ms)}; crest syncs to bed end."
        ),
        "soundtrack": {"main": COMPOUNDS_SOUNDTRACK},
        "bookends": dict(SILENT_CREST_BOOKENDS),
        "exhibition": timing,
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "japaneseReflections",
            "showKeyword": False,
            "showKanji": False,
            "showEnglish": True,
            "exhibitProfile": "compoundsExhibition",
            "verseMode": "sequential",
            "typography": "mobile-refine",
            "typographyStyle": "foundations",
            "bookendStyle": "galleryCrest",
        },
        "meta": {
            "family": "japaneseReflections",
            "lesson": lesson,
            "stage": "compounds",
            "sceneCount": len(scenes),
            "prototype": True,
            "avgCompoundCount": round(sum(step_counts) / len(step_counts), 1),
            "totalCompounds": sum(step_counts),
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
            "compoundSource": source,
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
    print(f"Wrote {len(config['scenes'])} exhibits → {path}")
    print(f"  compounds: {config['meta']['totalCompounds']} total")
    print(f"  source: {config['meta']['compoundSource']}")
    print(f"  soundtrack: {COMPOUNDS_SOUNDTRACK} ({format_duration(soundtrack_ms)})")
    print(f"  estimated runtime: {format_duration(content_ms)}")
    print(f"  exhibition.html?collection={cid}")
    print(f"  sample: {sample['id']} → {sample['compounds']['steps'][0]['jp']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
