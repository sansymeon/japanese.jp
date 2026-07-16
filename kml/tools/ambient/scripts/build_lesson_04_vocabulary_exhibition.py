#!/usr/bin/env python3
"""Build Lesson 4 Vocabulary Exhibition.

Flow per exhibit: vocabulary steps → full JP verse → full EN verse.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from lesson_04_vocabulary_steps import VOCABULARY_BY_SLUG

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"
LESSON = 4
COLLECTION_ID = "lesson_04_vocabulary"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import write_collection_path  # noqa: E402
from vocabulary_phrase_ruby import enrich_vocabulary_steps  # noqa: E402
from build_lesson_04_gallery import (  # noqa: E402
    ARTWORK_ARRIVAL_FADE_MS,
    CLOSING_TIMING_MS,
    GALLERY_CAMERA_BY_SLUG,
    IMAGE_OVERRIDES,
    RECORDING_BLACK_BEFORE_MS,
    gallery_camera,
    image_rev,
    soundtrack_duration_ms,
)

OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)

VOCABULARY_SOUNDTRACK = "audio/vocabulary_extended_minus3db.mp3"

INTRO_LEAD_MS = RECORDING_BLACK_BEFORE_MS + ARTWORK_ARRIVAL_FADE_MS

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
    "vocabularyPauseBeforeMs": 4000,
    "vocabularyStepRevealMs": 1400,
    "vocabularyStepHoldMs": 3500,
    "vocabularyStepFadeMs": 1400,
    "vocabularyFuriganaEnterDelayMs": 700,
    "vocabularyFuriganaEnterMs": 2200,
    "vocabularyFuriganaHoldMs": 3500,
    "vocabularyFuriganaFadeMs": 2200,
    "vocabularyNativeHoldMs": 2000,
    "vocabularyVerseJpRevealMs": 1600,
    "vocabularyVerseKanjiHoldMs": 3500,
    "vocabularyVerseFuriganaEnterDelayMs": 900,
    "vocabularyVerseFuriganaEnterMs": 2500,
    "vocabularyVerseFuriganaHoldMs": 4500,
    "vocabularyVerseFuriganaFadeMs": 2500,
    "vocabularyVerseNativeHoldMs": 3000,
    "vocabularyVerseJpFadeMs": 1400,
    "vocabularyVerseEnRevealMs": 1400,
    "vocabularyVerseEnHoldMs": 6000,
    "vocabularyVerseEnFadeMs": 1400,
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
    scenes: list[dict] = []
    for block in SECTION_RE.findall(html):
        kanji_m = re.search(r'data-kanji="([^"]+)"', block)
        slug_m = re.search(r'data-slug="([^"]+)"', block)
        keyword_m = re.search(r'<span class="kanji-keyword">([^<]+)</span>', block)
        img_m = re.search(r"assets/studies/([^\"']+\.png)", block)
        jp_m = re.search(r'<p class="jp-verse[^"]*">(.*?)</p>', block, re.DOTALL)
        en_m = re.search(r'<p class="en-verse">(.*?)</p>', block, re.DOTALL)
        if not (kanji_m and slug_m and jp_m and en_m):
            continue

        slug = slug_m.group(1)
        keyword = keyword_m.group(1).strip() if keyword_m else slug.replace("_", " ")
        image = f"studies/{img_m.group(1)}" if img_m else f"studies/{slug}.png"
        en = re.sub(r"<br\s*/?>", "\n", en_m.group(1), flags=re.IGNORECASE).strip()
        cam = gallery_camera(slug)
        steps_raw = VOCABULARY_BY_SLUG.get(slug)
        if not steps_raw:
            raise KeyError(f"Missing vocabulary steps for slug: {slug}")
        jp_inner = jp_m.group(1).strip()
        steps = enrich_vocabulary_steps(steps_raw, jp_inner)

        scene = {
            "id": f"L{lesson:02d}_{slug}",
            "kanji": kanji_m.group(1),
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


def vocabulary_step_ms(step: dict, timing: dict) -> int:
    reveal = timing.get("vocabularyStepRevealMs", 1400)
    hold = timing.get("vocabularyStepHoldMs", 3500)
    fade = timing.get("vocabularyStepFadeMs", 1400)
    uses_furigana = bool(step.get("furigana") or step.get("jpHtml"))
    total = reveal
    if uses_furigana:
        total += timing.get("vocabularyFuriganaEnterDelayMs", 700)
        total += timing.get("vocabularyFuriganaEnterMs", 2200)
        total += timing.get("vocabularyFuriganaHoldMs", 3500)
        total += timing.get("vocabularyFuriganaFadeMs", 2200)
        total += timing.get("vocabularyNativeHoldMs", 2000)
    else:
        total += hold
    return total + fade


def vocabulary_verse_ms(timing: dict) -> int:
    return sum(
        timing.get(k, default)
        for k, default in (
            ("vocabularyVerseJpRevealMs", 1600),
            ("vocabularyVerseKanjiHoldMs", 3500),
            ("vocabularyVerseFuriganaEnterDelayMs", 900),
            ("vocabularyVerseFuriganaEnterMs", 2500),
            ("vocabularyVerseFuriganaHoldMs", 4500),
            ("vocabularyVerseFuriganaFadeMs", 2500),
            ("vocabularyVerseNativeHoldMs", 3000),
            ("vocabularyVerseJpFadeMs", 1400),
            ("vocabularyVerseEnRevealMs", 1400),
            ("vocabularyVerseEnHoldMs", 6000),
            ("vocabularyVerseEnFadeMs", 1400),
        )
    )


def vocabulary_content_runtime_ms(scenes: list[dict], timing: dict) -> int:
    transition_ms = timing.get("exhibitTransitionMs", 3500)
    intro_ms = (
        timing.get("exhibitionBlackBeforeMs", RECORDING_BLACK_BEFORE_MS)
        + timing.get("artworkArrivalFadeMs", ARTWORK_ARRIVAL_FADE_MS)
        + timing.get("vocabularyPauseBeforeMs", 4000)
    )
    total = intro_ms
    for index, scene in enumerate(scenes):
        for step in scene["vocabulary"]["steps"]:
            total += vocabulary_step_ms(step, timing)
        total += vocabulary_verse_ms(timing)
        if index < len(scenes) - 1:
            total += transition_ms
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
    step_counts = [len(s["vocabulary"]["steps"]) for s in scenes]
    avg_steps = sum(step_counts) / len(step_counts)
    soundtrack_ms = soundtrack_duration_ms(VOCABULARY_SOUNDTRACK)
    timing = dict(DEFAULT_EXHIBITION)
    content_ms = vocabulary_content_runtime_ms(scenes, timing)
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": COLLECTION_ID,
        "title": "Lesson 4 — Vocabulary Exhibition",
        "notes": (
            "Intro: 3s black → 2s artwork fade-in (gallery style); no opening crest. "
            "Outro: gold gallery crest hold, fades with soundtrack end. "
            "Rebuild each verse from vocabulary and phrases; same gallery atmosphere. "
            f"~{avg_steps:.0f} steps per exhibit. "
            f"Soundtrack {format_duration(soundtrack_ms)}; crest exhale syncs to bed end."
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
            "lesson": LESSON,
            "stage": "vocabulary",
            "sceneCount": len(scenes),
            "prototype": True,
            "avgVocabularySteps": round(avg_steps, 1),
            "introLeadMs": INTRO_LEAD_MS,
            "introBlackMs": RECORDING_BLACK_BEFORE_MS,
            "artworkArrivalFadeMs": ARTWORK_ARRIVAL_FADE_MS,
            "bookendMode": "silentCrest",
            "galleryCameraSlugs": list(GALLERY_CAMERA_BY_SLUG.keys()),
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    sample = config["scenes"][0]
    soundtrack_ms = config["meta"]["soundtrackDurationMs"]
    content_ms = config["meta"]["estimatedContentRuntimeMs"]
    soundtrack_start_ms = (
        config["exhibition"].get("exhibitionBlackBeforeMs", RECORDING_BLACK_BEFORE_MS)
        + config["exhibition"].get("artworkArrivalFadeMs", ARTWORK_ARRIVAL_FADE_MS)
    )
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
    exhibit_ms = content_ms - closing_ms
    crest_pad_ms = (
        soundtrack_ms
        - (exhibit_ms - soundtrack_start_ms)
        - closing_ms
    )
    print(f"Wrote {len(config['scenes'])} exhibits → {OUT_PATH}")
    print(f"  avg steps: {config['meta']['avgVocabularySteps']}")
    print(f"  intro: {RECORDING_BLACK_BEFORE_MS}ms black + {ARTWORK_ARRIVAL_FADE_MS}ms fade-in")
    print(f"  soundtrack: {VOCABULARY_SOUNDTRACK} ({format_duration(soundtrack_ms)})")
    print(f"  estimated content + closing: {format_duration(content_ms)}")
    print(f"  crest + bed joint fade; ~{format_duration(max(0, crest_pad_ms))} music under crest")
    print(f"  exhibition.html?collection={COLLECTION_ID}")
    print(f"  sample: {sample['id']} ({len(sample['vocabulary']['steps'])} steps)")

    import subprocess

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_lesson_04_vocabulary.py")],
        cwd=ROOT,
    )
    if result.returncode != 0:
        return result.returncode

    from framing_policy import run_fill_safety_audit

    return run_fill_safety_audit(COLLECTION_ID)


if __name__ == "__main__":
    raise SystemExit(main())
