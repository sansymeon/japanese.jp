#!/usr/bin/env python3
"""Build Lesson 5 Compounds Exhibition.

Target kanji → curated compounds from compounds/lesson_05.html on gallery artwork.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"
LESSON = 5
COLLECTION_ID = "lesson_05_compounds"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import write_collection_path  # noqa: E402
from compounds_page_data import lesson_compounds  # noqa: E402
from lesson_05_compounds_curation import SELECTED_BY_SLUG  # noqa: E402
from build_lesson_05_gallery import (  # noqa: E402
    ARTWORK_ARRIVAL_FADE_MS,
    CLOSING_TIMING_MS,
    IMAGE_OVERRIDES,
    RECORDING_BLACK_BEFORE_MS,
    gallery_camera,
    image_rev,
    soundtrack_duration_ms,
)

OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)

COMPOUNDS_SOUNDTRACK = "audio/compounds_minus3db.mp3"

SILENT_CREST_BOOKENDS = {
    "mode": "silentCrest",
    "closing": {
        "image": "images/gold_closing.png",
        "bookendSize": "small",
        "fadeWithSoundtrackEnd": True,
    },
}

DEFAULT_EXHIBITION = {
    "artworkArrivalMs": 0,
    "artworkArrivalFadeMs": ARTWORK_ARRIVAL_FADE_MS,
    "artworkAloneMs": 0,
    "exhibitionBlackBeforeMs": RECORDING_BLACK_BEFORE_MS,
    "compoundsPauseBeforeMs": 2400,
    "compoundsKanjiRevealMs": 1600,
    "compoundsKanjiHoldMs": 2800,
    "compoundsKanjiFadeMs": 1400,
    "compoundsStepRevealMs": 1400,
    "compoundsFuriganaEnterDelayMs": 900,
    "compoundsFuriganaEnterMs": 2200,
    "compoundsFuriganaHoldMs": 3000,
    "compoundsFuriganaFadeMs": 2200,
    "compoundsNativeHoldMs": 1600,
    "compoundsReadingRevealMs": 1200,
    "compoundsReadingHoldMs": 1800,
    "compoundsHintRevealMs": 1000,
    "compoundsEnRevealMs": 1200,
    "compoundsEnHoldMs": 3000,
    "compoundsEnFadeMs": 1400,
    "compoundsStepFadeMs": 1400,
    "compoundsKanjiReturnRevealMs": 1400,
    "compoundsKanjiReturnHoldMs": 2200,
    "compoundsKanjiReturnFadeMs": 1400,
    "exhibitTransitionMs": 3500,
    "exhibitBlackHoldMs": 0,
    "kenBurnsDurationMs": 90000,
    "openingBlackBeforeMs": 0,
    "openingRevealMs": 0,
    "openingHoldMs": 0,
    "openingExhaleMs": 0,
    "openingBlackAfterMs": 0,
    **CLOSING_TIMING_MS,
}

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)


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
        selected = SELECTED_BY_SLUG.get(slug)
        if not selected:
            raise KeyError(f"Missing compound curation for slug: {slug}")

        pool = {item["jp"]: item for item in by_kanji.get(kanji, [])}
        steps: list[dict] = []
        for jp in selected:
            base = pool.get(jp)
            if not base:
                raise KeyError(f"Compound {jp!r} not found for kanji {kanji} ({slug})")
            steps.append(dict(base))

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


def compound_step_ms(step: dict, timing: dict) -> int:
    total = timing.get("compoundsStepRevealMs", 1400)
    if step.get("jpHtml"):
        total += timing.get("compoundsFuriganaEnterDelayMs", 900)
        total += timing.get("compoundsFuriganaEnterMs", 2200)
        total += timing.get("compoundsFuriganaHoldMs", 3000)
        total += timing.get("compoundsFuriganaFadeMs", 2200)
        total += timing.get("compoundsNativeHoldMs", 1600)
    total += timing.get("compoundsReadingRevealMs", 1200)
    total += timing.get("compoundsReadingHoldMs", 1800)
    if step.get("hint"):
        total += timing.get("compoundsHintRevealMs", 1000)
    total += timing.get("compoundsEnRevealMs", 1200)
    total += timing.get("compoundsEnHoldMs", 3000)
    total += timing.get("compoundsEnFadeMs", 1400)
    return total + timing.get("compoundsStepFadeMs", 1400)


def exhibit_runtime_ms(scene: dict, timing: dict, *, include_intro: bool) -> int:
    total = 0
    if include_intro:
        total += timing.get("exhibitionBlackBeforeMs", 0)
        total += timing.get("artworkArrivalFadeMs", 0)
        total += timing.get("compoundsPauseBeforeMs", 0)
    total += (
        timing.get("compoundsKanjiRevealMs", 1600)
        + timing.get("compoundsKanjiHoldMs", 2800)
        + timing.get("compoundsKanjiFadeMs", 1400)
    )
    for step in scene.get("compounds", {}).get("steps", []):
        total += compound_step_ms(step, timing)
    total += (
        timing.get("compoundsKanjiReturnRevealMs", 1400)
        + timing.get("compoundsKanjiReturnHoldMs", 2200)
        + timing.get("compoundsKanjiReturnFadeMs", 1400)
    )
    return total


def collection_runtime_ms(scenes: list[dict], timing: dict) -> int:
    if not scenes:
        return 0
    transition_ms = timing.get("exhibitTransitionMs", 3500)
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
    total = exhibit_runtime_ms(scenes[0], timing, include_intro=True)
    for scene in scenes[1:]:
        total += exhibit_runtime_ms(scene, timing, include_intro=False)
        total += transition_ms
    return total + closing_ms


def format_duration(ms: int) -> str:
    seconds = max(0, ms) // 1000
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


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
        "title": "Lesson 5 — Compounds",
        "notes": (
            "Gallery artwork per kanji: target kanji → familiar compounds with furigana. "
            "Curated from kml/contents/books/book_01/compounds/lesson_05.html. "
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
            "compoundSource": "kml/contents/books/book_01/compounds/lesson_05.html",
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

    from framing_policy import run_fill_safety_audit

    return run_fill_safety_audit(COLLECTION_ID)


if __name__ == "__main__":
    raise SystemExit(main())
