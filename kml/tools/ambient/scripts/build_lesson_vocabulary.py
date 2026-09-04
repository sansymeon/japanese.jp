#!/usr/bin/env python3
"""Build Lesson N Vocabulary Exhibition (Lessons 6–10 auto standard).

Steps per exhibit: target kanji (when the verse gives a reading) → up to 4 lesson
compounds → first and last verse lines as furigana phrases. No hand-authored
curation module required; everything comes from the lesson + compounds HTML.

Usage:
  python3 scripts/build_lesson_vocabulary.py --lesson 33
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
from build_lesson_05_gallery import (  # noqa: E402
    ARTWORK_ARRIVAL_FADE_MS,
    CLOSING_TIMING_MS,
    IMAGE_OVERRIDES,
    RECORDING_BLACK_BEFORE_MS,
    gallery_camera,
    image_rev,
    soundtrack_duration_ms,
)
from build_lesson_05_vocabulary_exhibition import (  # noqa: E402
    DEFAULT_EXHIBITION,
    SILENT_CREST_BOOKENDS,
    format_duration,
    vocabulary_content_runtime_ms,
)
from collection_paths import write_collection_path  # noqa: E402
from compounds_page_data import lesson_compounds  # noqa: E402
from vocabulary_phrase_ruby import enrich_vocabulary_steps, reading_map_from_verse  # noqa: E402

VOCABULARY_SOUNDTRACK = "audio/vocabulary_extended_minus3db.mp3"
INTRO_LEAD_MS = RECORDING_BLACK_BEFORE_MS + ARTWORK_ARRIVAL_FADE_MS
SECTION_RE = re.compile(r'<section class="kanji-entry"(.*?)</section>', re.DOTALL)
MAX_COMPOUNDS = 4


def _plain_lines(jp_html: str) -> list[str]:
    txt = re.sub(r"<ruby>([^<]+)<rt>[^<]*</rt></ruby>", r"\1", jp_html)
    txt = re.sub(r"<br\s*/?>", "\n", txt, flags=re.I)
    txt = re.sub(r"<[^>]+>", "", txt)
    return [line.strip() for line in txt.split("\n") if line.strip()]


def _auto_steps(
    kanji: str, keyword: str, jp_html: str, compounds_for_kanji: list[dict]
) -> list[dict]:
    readings = reading_map_from_verse(jp_html)
    steps: list[dict] = []
    kanji_reading = readings.get(kanji)
    if kanji_reading:
        # Use the lesson keyword — never meta-labels like "target kanji".
        steps.append({"jp": kanji, "reading": kanji_reading, "en": keyword})
    for item in compounds_for_kanji[:MAX_COMPOUNDS]:
        steps.append({"jp": item["jp"], "reading": item["reading"], "en": item["en"]})
    lines = _plain_lines(jp_html)
    # Verse phrases stay Japanese-only (full EN verse follows later).
    if lines:
        steps.append({"jp": lines[0], "phrase": True})
    if len(lines) > 1:
        steps.append({"jp": lines[-1], "phrase": True})
    return enrich_vocabulary_steps(steps, jp_html)


def parse_lesson_scenes(lesson: int) -> list[dict]:
    html_path = REPO / "contents/books/book_01/lessons" / f"lesson_{lesson:02d}.html"
    html = html_path.read_text(encoding="utf-8")
    by_kanji = lesson_compounds(lesson)
    scenes: list[dict] = []
    for block in SECTION_RE.findall(html):
        kanji_m = re.search(r'data-kanji="([^"]+)"', block)
        slug_m = re.search(r'data-slug="([^"]+)"', block)
        keyword_m = re.search(r'<span class="kanji-keyword">([^<]+)</span>', block)
        img_m = re.search(r"assets/studies/([^\"']+\.(?:png|jpe?g))", block)
        jp_m = re.search(r'<p class="jp-verse[^"]*">(.*?)</p>', block, re.DOTALL)
        en_m = re.search(r'<p class="en-verse">(.*?)</p>', block, re.DOTALL)
        if not (kanji_m and slug_m and jp_m and en_m):
            continue

        slug = slug_m.group(1)
        kanji = kanji_m.group(1)
        keyword = keyword_m.group(1).strip() if keyword_m else slug.replace("_", " ")
        image = f"studies/{(img_m.group(1).rsplit('.', 1)[0] if img_m else slug)}.jpg"
        jp_inner = jp_m.group(1).strip()
        en = re.sub(r"<br\s*/?>", "\n", en_m.group(1), flags=re.IGNORECASE).strip()
        cam = gallery_camera(slug)
        steps = _auto_steps(kanji, keyword, jp_inner, by_kanji.get(kanji, []))
        if not steps:
            raise KeyError(f"No vocabulary steps for {slug} ({kanji})")

        scene = {
            "id": f"L{lesson:02d}_{slug}",
            "kanji": kanji,
            "keyword": keyword,
            "image": image,
            "galleryCamera": cam,
            "verse": {
                "jpHtml": jp_inner,
                "en": en,
            },
            "vocabulary": {"steps": steps},
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
    collection_id = f"lesson_{lesson:02d}_vocabulary"
    scenes = parse_lesson_scenes(lesson)
    if not scenes:
        raise SystemExit(f"No vocabulary scenes for lesson {lesson}")
    step_counts = [len(s["vocabulary"]["steps"]) for s in scenes]
    avg_steps = sum(step_counts) / len(step_counts)
    soundtrack_ms = soundtrack_duration_ms(VOCABULARY_SOUNDTRACK)
    timing = dict(DEFAULT_EXHIBITION)
    content_ms = vocabulary_content_runtime_ms(scenes, timing)
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": collection_id,
        "title": f"Lesson {lesson} — Vocabulary Exhibition",
        "notes": (
            "Intro: 3s black → 2s artwork fade-in (gallery style); no opening crest. "
            "Outro: short gold gallery crest; soundtrack fades with crest (no bed pad). "
            "Vocabulary auto-prepared from lesson compounds plus verse phrases. "
            f"~{avg_steps:.0f} steps per exhibit. "
            f"Soundtrack bed {format_duration(soundtrack_ms)}; runtime follows content."
        ),
        "soundtrack": {"main": VOCABULARY_SOUNDTRACK},
        "bookends": dict(SILENT_CREST_BOOKENDS),
        "exhibition": timing,
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "japaneseReflections",
            "showKeyword": False,
            "showKanji": False,
            "showEnglish": True,
            "exhibitProfile": "vocabularyExhibition",
            "verseMode": "sequential",
            "verseLayout": "authored",
            "typography": "mobile-refine",
            "typographyStyle": "foundations",
            "bookendStyle": "galleryCrest",
        },
        "meta": {
            "family": "japaneseReflections",
            "lesson": lesson,
            "stage": "vocabulary",
            "sceneCount": len(scenes),
            "prototype": True,
            "avgVocabularySteps": round(avg_steps, 1),
            "introLeadMs": INTRO_LEAD_MS,
            "introBlackMs": RECORDING_BLACK_BEFORE_MS,
            "artworkArrivalFadeMs": ARTWORK_ARRIVAL_FADE_MS,
            "bookendMode": "silentCrest",
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
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
    closing_ms = sum(
        CLOSING_TIMING_MS[k]
        for k in (
            "closingBlackBeforeMs",
            "closingRevealMs",
            "closingHoldMs",
            "closingExhaleMs",
            "closingBlackAfterMs",
        )
    )
    print(f"Wrote {len(config['scenes'])} exhibits → {path}")
    print(f"  avg steps: {config['meta']['avgVocabularySteps']}")
    print(f"  intro: {RECORDING_BLACK_BEFORE_MS}ms black + {ARTWORK_ARRIVAL_FADE_MS}ms fade-in")
    print(f"  soundtrack: {VOCABULARY_SOUNDTRACK} ({format_duration(soundtrack_ms)})")
    print(f"  estimated content + closing: {format_duration(content_ms + closing_ms)}")
    print(f"  exhibition.html?collection={cid}")
    print(f"  sample: {sample['id']} ({len(sample['vocabulary']['steps'])} steps)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
