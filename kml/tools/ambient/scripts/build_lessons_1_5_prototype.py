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

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)

# All timing values configurable in collection JSON (milliseconds)
DEFAULT_EXHIBITION = {
    "artworkArrivalMs": 0,
    "artworkAloneMs": 8000,
    "verseJpRevealMs": 1000,
    "verseJpHoldMs": 7000,
    "verseJpFadeMs": 1000,
    "verseEnRevealMs": 1000,
    "verseEnHoldMs": 7000,
    "verseEnFadeMs": 1000,
    "exhibitTransitionMs": 4000,
    "exhibitBlackHoldMs": 0,
    "kenBurnsDurationMs": 30000,
    "openingBlackBeforeMs": 0,
    "openingRevealMs": 3000,
    "openingHoldMs": 12000,
    "openingExhaleMs": 3000,
    "openingBlackAfterMs": 0,
    "closingRevealMs": 3000,
    "closingHoldMs": 12000,
    "closingExhaleMs": 3000,
    "closingBlackAfterMs": 0,
    "closingSilenceHoldMs": 0,
    "closingFadeToBlackMs": 3000,
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
        scenes.append(
            {
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
        )
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
            "Japanese Reflections family: image → JP verse → EN verse → crossfade. "
            "No kanji, keywords, or lesson numbers. 30s per exhibit."
        ),
        "bookends": {
            "opening": {
                "image": "covers/lesson_01.png",
                "holdUntilAudioEnds": False,
            },
            "closing": {
                "image": "covers/lesson_05.png",
                "holdUntilSoundtrackEnds": False,
            },
        },
        "exhibition": dict(DEFAULT_EXHIBITION),
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "japaneseReflections",
            "showKeyword": False,
            "showKanji": False,
            "exhibitProfile": "imageVerse",
            "verseMode": "sequential",
            "typography": "placard",
        },
        "meta": {
            "family": "japaneseReflections",
            "prototype": True,
            "lessons": list(LESSONS),
            "sceneCount": len(scenes),
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
