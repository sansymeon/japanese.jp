#!/usr/bin/env python3
"""Build Lesson 10 Compounds Exhibition."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
LESSON = 10
COLLECTION_ID = "lesson_10_compounds"

import sys

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

OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)
COMPOUNDS_SOUNDTRACK = "audio/compounds_minus3db.mp3"
SECTION_RE = re.compile(r'<section class="kanji-entry"(.*?)</section>', re.DOTALL)


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
        steps = [dict(item) for item in by_kanji.get(kanji, [])[:4]]
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


def build() -> dict:
    scenes = parse_lesson_scenes(LESSON)
    step_counts = [len(s["compounds"]["steps"]) for s in scenes]
    soundtrack_ms = soundtrack_duration_ms(COMPOUNDS_SOUNDTRACK)
    timing = dict(DEFAULT_EXHIBITION)
    content_ms = collection_runtime_ms(scenes, timing)
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": COLLECTION_ID,
        "title": "Lesson 10 — Compounds",
        "notes": (
            "Gallery artwork per kanji: target kanji → familiar compounds with furigana. "
            "Auto-curated from kml/contents/books/book_01/compounds/lesson_10.html. "
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
            "lesson": LESSON,
            "stage": "compounds",
            "sceneCount": len(scenes),
            "prototype": True,
            "avgCompoundCount": round(sum(step_counts) / len(step_counts), 1),
            "totalCompounds": sum(step_counts),
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
            "compoundSource": "kml/contents/books/book_01/compounds/lesson_10.html",
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    sample = config["scenes"][0]
    soundtrack_ms = config["meta"]["soundtrackDurationMs"]
    content_ms = config["meta"]["estimatedContentRuntimeMs"]
    print(f"Wrote {len(config['scenes'])} exhibits → {OUT_PATH}")
    print(f"  compounds: {config['meta']['totalCompounds']} total")
    print(f"  source: {config['meta']['compoundSource']}")
    print(f"  soundtrack: {COMPOUNDS_SOUNDTRACK} ({format_duration(soundtrack_ms)})")
    print(f"  estimated runtime: {format_duration(content_ms)}")
    print(f"  exhibition.html?collection={COLLECTION_ID}")
    print(f"  sample: {sample['id']} → {sample['compounds']['steps'][0]['jp']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
