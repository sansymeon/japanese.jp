#!/usr/bin/env python3
"""Build per-lesson Reading exhibition.

Flow: pause → natural Japanese → furigana fade in → hold → furigana fade out → English.

Usage:
  python3 scripts/build_lesson_01_assisted_reading_experimental.py
  python3 scripts/build_lesson_01_assisted_reading_experimental.py --lesson 2
  python3 scripts/build_lesson_01_assisted_reading_experimental.py --all
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from verse_reading_stages import normalize_two_lines

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"

SILENT_CREST_BOOKENDS = {
    "mode": "silentCrest",
    "closing": {
        "image": "images/gold_closing.png",
        "bookendSize": "small",
        # End at content + short crest — do not pad to the reading bed.
        "holdUntilSoundtrackEnds": False,
        "fadeWithSoundtrackEnd": True,
    },
}

# Main tracks live in tools/ambient/audio/ (resolved via localUrl, not assetsBase).
# Odd lessons → v1; even lessons → v2.
READING_SOUNDTRACKS = {
    "v1": {
        "main": "audio/12_minutes_minus3db.mp3",
        "target": "12:51",
        "durationSec": 771.29,
    },
    "v2": {
        "main": "audio/reading_v2_minus3db.mp3",
        "target": "12:41",
        "durationSec": 760.97,
    },
}


def soundtrack_for_lesson(lesson: int) -> dict:
    key = "v2" if lesson % 2 == 0 else "v1"
    return {**READING_SOUNDTRACKS[key], "version": key}

# imageScale < 1 zooms out and leaves gaps on full-bleed landscape art.
IMAGE_OVERRIDES: dict[str, dict] = {
    "pop_song": {"imageScale": 1.14, "imageFocus": "50% 48%"},
}

DEFAULT_EXHIBITION = {
    "artworkArrivalMs": 0,
    "artworkArrivalFadeMs": 800,
    "artworkAloneMs": 0,
    "exhibitionBlackBeforeMs": 1500,
    "readingPauseBeforeMs": 5000,
    "readingAssistedRevealMs": 1800,
    "readingFuriganaEnterDelayMs": 3000,
    "readingFuriganaEnterMs": 3000,
    "readingAssistedHoldMs": 9000,
    "readingFuriganaFadeMs": 2500,
    "readingNativeHoldMs": 3500,
    "readingJpFadeMs": 1000,
    "readingEnRevealMs": 1000,
    "readingEnHoldMs": 5500,
    "readingEnFadeMs": 1000,
    "exhibitTransitionMs": 4000,
    "exhibitBlackHoldMs": 0,
    "kenBurnsDurationMs": 45000,
    "openingBlackBeforeMs": 0,
    "openingRevealMs": 0,
    "openingHoldMs": 0,
    "openingExhaleMs": 0,
    "openingBlackAfterMs": 0,
    "closingBlackBeforeMs": 800,
    "closingRevealMs": 2500,
    "closingHoldMs": 1500,
    "closingExhaleMs": 4000,
    "closingTitleRevealMs": 0,
    "closingTitleFadeMs": 0,
    "closingBlackAfterMs": 1200,
    "closingSilenceHoldMs": 0,
    "closingFadeToBlackMs": 0,
    "blackHoldMs": 0,
}

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)


def collection_id(lesson: int) -> str:
    return f"lesson_{lesson:02d}_reading"


def out_path(lesson: int) -> Path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from collection_paths import write_collection_path  # noqa: E402

    return write_collection_path(ROOT, collection_id(lesson))


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
        scene_id = f"L{lesson:02d}_{slug}"
        jp_inner = jp_m.group(1).strip()
        en = re.sub(r"<br\s*/?>", "\n", en_m.group(1), flags=re.IGNORECASE).strip()

        scene = {
            "id": scene_id,
            "kanji": kanji_m.group(1),
            "keyword": keyword_m.group(1).strip() if keyword_m else slug.replace("_", " "),
            "image": f"studies/{(img_m.group(1).rsplit('.', 1)[0] if img_m else slug)}.jpg",
            "verse": {
                "jpHtml": normalize_two_lines(jp_inner),
                "en": en,
            },
            "meta": {"lesson": lesson, "experimental": True},
        }
        if slug in IMAGE_OVERRIDES:
            scene.update(IMAGE_OVERRIDES[slug])
        rev = image_rev(scene["image"])
        if rev is not None:
            scene["imageRev"] = rev
        scenes.append(scene)
    return scenes


def build(lesson: int, *, show_english: bool = True) -> dict:
    scenes = parse_lesson_scenes(lesson)
    cid = collection_id(lesson)
    st = soundtrack_for_lesson(lesson)
    return {
        "presentation": "exhibition",
        "assetsBase": "./assets",
        "id": cid,
        "title": f"Lesson {lesson} — Reading",
        "notes": (
            "Reading: pause → natural Japanese → furigana in/out → English on gallery artwork. "
            "skipBookends=1 skips crest only (music still plays after gate)."
        ),
        "soundtrack": {"main": st["main"]},
        "bookends": dict(SILENT_CREST_BOOKENDS),
        "exhibition": dict(DEFAULT_EXHIBITION),
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "japaneseReflections",
            "showKeyword": False,
            "showKanji": False,
            "showEnglish": show_english,
            "showFurigana": True,
            "exhibitProfile": "assistedReading",
            "verseMode": "sequential",
            "verseLayout": "authored",
            "typography": "mobile-refine",
            "typographyStyle": "foundations",
            "bookendStyle": "galleryCrest",
        },
        "meta": {
            "family": "japaneseReflections",
            "lesson": lesson,
            "stage": "reading",
            "sceneCount": len(scenes),
            "readingStages": ["pause", "assisted", "furiganaEnter", "furiganaFade", "native", "en"],
            "showEnglish": show_english,
            "soundtrackVersion": st["version"],
            "soundtrackTarget": st["target"],
            "soundtrackDurationSec": st["durationSec"],
            "bookendMode": "silentCrest",
        },
        "scenes": scenes,
    }


def write_collection(lesson: int, *, show_english: bool = True) -> tuple[Path, dict]:
    config = build(lesson, show_english=show_english)
    path = out_path(lesson)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    return path, config


SUPPORTED_LESSONS = list(range(1, 25)) + list(range(33, 39)) + [41]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, choices=SUPPORTED_LESSONS)
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build lessons 1–10 (use --lesson for 11–15, 33–38, 41)",
    )
    parser.add_argument("--no-english", action="store_true")
    args = parser.parse_args()

    if args.all:
        lessons = list(range(1, 11))
    elif args.lesson is not None:
        lessons = [args.lesson]
    else:
        lessons = [1]

    show_english = not args.no_english
    for lesson in lessons:
        path, config = write_collection(lesson, show_english=show_english)
        cid = collection_id(lesson)
        sample = config["scenes"][0]

        print(f"Wrote {len(config['scenes'])} exhibits → {path}")
        print(f"  soundtrack: {config['meta']['soundtrackVersion']} ({config['soundtrack']['main']}, {config['meta']['soundtrackTarget']})")
        print(f"  showEnglish: {show_english}")
        print(f"  exhibition.html?collection={cid}")
        print(f"  OBS → verse_exhibitions/ambient_verses_lesson_{lesson}.mp4")
        print(f"  sample: {sample['id']}")
        if lesson != lessons[-1]:
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
