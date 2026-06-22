#!/usr/bin/env python3
"""Build Lessons 1–5 image+verse prototype exhibition collection."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
LESSONS = (1, 2, 3, 4, 5)
OUT_PATH = ROOT / "collections" / "lessons_1_5_prototype.json"

INTRO_AUDIO = "audio/fifty_minute_intro.mp3"
OUTRO_AUDIO = "audio/fifty_minute_outro.mp3"
SOUNDTRACK = "audio/-3db_fifty_minutes.mp3"
SOUNDTRACK_NORMAL = "audio/fifty_minutes.mp3"
# Swap to images/gold_closing_hanko.png when the hanko seal variant is ready.
GALLERY_CREST = "images/gold_closing.png"
CLOSING_TITLE_HTML = "Ambient Kanji Gallery<br>Lessons 1–5"

# slug → imageScale / imageFocus tweaks (imageScale < 1 zooms out; > 1 crops letterboxing)
IMAGE_OVERRIDES: dict[str, dict] = {
    "concave": {"imageScale": 0.88},
    "convex": {"imageScale": 0.88},
    "pop_song": {
        # Baked-in horizontal letterbox bars — zoom to full cover
        "imageScale": 1.14,
        "imageFocus": "50% 48%",
    },
}

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)

# Image → kanji (quick) → JP → EN → crossfade; 30s per exhibit
DEFAULT_EXHIBITION = {
    "artworkArrivalMs": 0,
    "artworkAloneMs": 4800,
    "kanjiRevealMs": 1600,
    "imageVerseKanjiHoldMs": 2000,
    "imageVerseKanjiFadeMs": 1600,
    "titleFadeMs": 1600,
    "verseJpRevealMs": 1000,
    "verseJpHoldMs": 6000,
    "verseJpFadeMs": 1000,
    "verseEnRevealMs": 1000,
    "verseEnHoldMs": 6000,
    "verseEnFadeMs": 1000,
    "exhibitTransitionMs": 4000,
    "exhibitBlackHoldMs": 0,
    "kenBurnsDurationMs": 30000,
    "openingBlackBeforeMs": 0,
    "openingRevealMs": 8000,
    "openingHoldMs": 0,
    "openingExhaleMs": 3500,
    "openingBlackAfterMs": 1200,
    "closingRevealMs": 3000,
    "closingHoldMs": 0,
    "closingExhaleMs": 3000,
    "closingTitleRevealMs": 2500,
    "closingTitleFadeMs": 3500,
    "closingBlackAfterMs": 0,
    "closingSilenceHoldMs": 0,
    "closingFadeToBlackMs": 3500,
    "blackHoldMs": 0,
}


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
        scene = {
            "id": f"L{lesson:02d}_{slug}",
            "kanji": kanji_m.group(1),
            "keyword": keyword,
            "image": image,
            "verse": {
                "jpHtml": jp_m.group(1).strip(),
                "en": en,
            },
            "meta": {"lesson": lesson},
        }
        if slug in IMAGE_OVERRIDES:
            scene.update(IMAGE_OVERRIDES[slug])
        scenes.append(scene)
    return scenes


def build() -> dict:
    scenes: list[dict] = []
    for lesson in LESSONS:
        scenes.extend(parse_lesson_scenes(lesson))

    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": "lessons_1_5_prototype",
        "title": "Japanese Reflections — Lessons 1–5 (Prototype)",
        "notes": (
            "Japanese Reflections family: image → kanji → JP verse → EN verse → crossfade. "
            "30s per exhibit; kanji is a brief reference only."
        ),
        "soundtrack": {"main": SOUNDTRACK},
        "bookends": {
            "opening": {
                "image": GALLERY_CREST,
                "bookendSize": "large",
                "audio": INTRO_AUDIO,
                "holdUntilAudioEnds": True,
            },
            "closing": {
                "image": GALLERY_CREST,
                "bookendSize": "small",
                "holdUntilSoundtrackEnds": True,
                "titleHtml": CLOSING_TITLE_HTML,
                "audio": OUTRO_AUDIO,
            },
        },
        "exhibition": dict(DEFAULT_EXHIBITION),
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "japaneseReflections",
            "showKeyword": False,
            "showKanji": True,
            "exhibitProfile": "imageVerse",
            "verseMode": "sequential",
            "typography": "placard",
            "bookendStyle": "galleryCrest",
        },
        "meta": {
            "family": "japaneseReflections",
            "prototype": True,
            "lessons": list(LESSONS),
            "sceneCount": len(scenes),
            "soundtrackNormal": SOUNDTRACK_NORMAL,
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} exhibits → {OUT_PATH}")
    for lesson in LESSONS:
        n = sum(1 for s in config["scenes"] if s["meta"]["lesson"] == lesson)
        print(f"  Lesson {lesson}: {n} exhibits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
