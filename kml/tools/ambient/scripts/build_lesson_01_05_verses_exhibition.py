#!/usr/bin/env python3
"""Build Lessons 1–5 verse-reading exhibition (hiragana → mixed → natural → optional EN)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from verse_reading_stages import reading_stages

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"
LESSONS = (1, 2, 3, 4, 5)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import write_collection_path  # noqa: E402

OUT_PATH = write_collection_path(ROOT, "lesson_01-05_verses")

INTRO_AUDIO = "audio/fifty_minute_intro.mp3"
OUTRO_AUDIO = "audio/fifty_minute_outro.mp3"
SOUNDTRACK = "audio/-3db_fifty_minutes.mp3"
SOUNDTRACK_NORMAL = "audio/fifty_minutes.mp3"
GALLERY_CREST = "images/gold_closing.png"
CLOSING_TITLE_HTML = "Ambient Kanji Gallery<br>Lessons 1–5 Verses"

IMAGE_OVERRIDES: dict[str, dict] = {
    "pop_song": {"imageScale": 1.14, "imageFocus": "50% 48%"},
}

# Comfortable reading pace — per-stage timing (total duration not tuned yet)
DEFAULT_EXHIBITION = {
    "artworkArrivalMs": 0,
    "artworkAloneMs": 0,
    "readingHiraganaRevealMs": 1000,
    "readingHiraganaHoldMs": 11000,
    "readingHiraganaFadeMs": 1000,
    "readingMixedRevealMs": 1000,
    "readingMixedHoldMs": 8000,
    "readingMixedFadeMs": 1000,
    "readingNaturalRevealMs": 1000,
    "readingNaturalHoldMs": 5500,
    "readingNaturalFadeMs": 1000,
    "readingEnRevealMs": 1000,
    "readingEnHoldMs": 3500,
    "readingEnFadeMs": 1000,
    "exhibitTransitionMs": 4000,
    "exhibitBlackHoldMs": 0,
    "kenBurnsDurationMs": 30000,
    "openingBlackBeforeMs": 2500,
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

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)


def image_rev(relative: str) -> int | None:
    path = ASSETS / relative
    if path.is_file():
        return int(path.stat().st_mtime)
    return None


def parse_lesson_scenes(lesson: int) -> list[dict]:
    html_path = REPO / "contents/books/book_01/lessons" / f"lesson_{lesson:02d}.html"
    html = html_path.read_text(encoding="utf-8")
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
        stages = reading_stages(jp_inner, f"L{lesson:02d}_{slug}")

        scene = {
            "id": f"L{lesson:02d}_{slug}",
            "kanji": kanji,
            "keyword": keyword,
            "image": image,
            "verse": {
                "hiragana": stages["hiragana"],
                "mixed": stages["mixed"],
                "natural": stages["natural"],
                "en": en,
            },
            "meta": {"lesson": lesson},
        }
        if slug in IMAGE_OVERRIDES:
            scene.update(IMAGE_OVERRIDES[slug])
        rev = image_rev(image)
        if rev is not None:
            scene["imageRev"] = rev
        scenes.append(scene)
    return scenes


def build(*, show_english: bool = True) -> dict:
    scenes: list[dict] = []
    for lesson in LESSONS:
        scenes.extend(parse_lesson_scenes(lesson))

    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": "lesson_01-05_verses",
        "title": "Japanese Reflections — Lessons 1–5 Verses",
        "notes": (
            "Reading fluency exhibition: hiragana → comfort mixed kanji → natural Japanese "
            "→ optional English reflection. Mixed stage reveals iconic nouns and imagery only."
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
            "showKanji": False,
            "showEnglish": show_english,
            "exhibitProfile": "verseReading",
            "verseMode": "sequential",
            "typography": "mobile-refine",
            "typographyStyle": "foundations",
            "bookendStyle": "galleryCrest",
        },
        "meta": {
            "family": "japaneseReflections",
            "lessons": list(LESSONS),
            "sceneCount": len(scenes),
            "soundtrackNormal": SOUNDTRACK_NORMAL,
            "readingStages": ["hiragana", "mixed", "natural", "en"],
            "showEnglish": show_english,
        },
        "scenes": scenes,
    }


def main() -> int:
    show_english = "--no-english" not in sys.argv
    config = build(show_english=show_english)
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} exhibits → {OUT_PATH}")
    print(f"  showEnglish: {show_english}")
    for lesson in LESSONS:
        n = sum(1 for s in config["scenes"] if s["meta"]["lesson"] == lesson)
        print(f"  Lesson {lesson}: {n} exhibits")

    sample = config["scenes"][0]
    print("\nSample (L01 one):")
    for key in ("hiragana", "mixed", "natural"):
        print(f"  {key}: {sample['verse'][key][:60]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
