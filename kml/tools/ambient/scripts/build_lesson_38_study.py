#!/usr/bin/env python3
"""Build lesson_38_study.json from lesson_38 HTML. Pair first, Further last."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
LESSON_HTML = REPO / "contents/books/book_01/lessons/lesson_38.html"
OUT_PATH = ROOT / "collections" / "lesson_38_study.json"

STUDY_LESSON = "audio/study_lesson.mp3"
INTRO_HOLD_MS = 1000
INTRO_DURATION_MS = 9000

FIRST_SCENE = "pair"
LAST_SCENE = "further"

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)


def parse_scenes(html: str) -> list[dict]:
    scenes: list[dict] = []
    for block in SECTION_RE.findall(html):
        kanji_m = re.search(r'data-kanji="([^"]+)"', block)
        slug_m = re.search(r'data-slug="([^"]+)"', block)
        jp_m = re.search(r'<p class="jp-verse[^"]*">(.*?)</p>', block, re.DOTALL)
        en_m = re.search(r'<p class="en-verse">(.*?)</p>', block, re.DOTALL)
        if not (kanji_m and slug_m and jp_m and en_m):
            continue

        slug = slug_m.group(1)
        en = re.sub(r"<br\s*/?>", "\n", en_m.group(1), flags=re.IGNORECASE).strip()
        scenes.append(
            {
                "id": slug,
                "kanji": kanji_m.group(1),
                "keyword": slug,
                "image": f"studies/{slug}.png",
                "video": None,
                "verse": {
                    "jpHtml": jp_m.group(1).strip(),
                    "en": en,
                },
            }
        )
    return scenes


def reorder_scenes(scenes: list[dict]) -> list[dict]:
    by_id = {s["id"]: s for s in scenes}
    original = [s["id"] for s in scenes]
    middle = [sid for sid in original if sid not in (FIRST_SCENE, LAST_SCENE)]
    order = [FIRST_SCENE] + middle + [LAST_SCENE]
    missing = [sid for sid in order if sid not in by_id]
    if missing:
        raise ValueError(f"Missing scenes for reorder: {missing}")
    return [by_id[sid] for sid in order]


def study_config(*, lesson: int, title: str, scenes: list[dict]) -> dict:
    return {
        "id": f"lesson_{lesson}_study",
        "title": title,
        "presentation": "study",
        "assetsBase": "../../assets",
        "notes": (
            f"Study template (~8 min loop). Silent hero, lesson bed with cards. "
            f"{FIRST_SCENE.title()} opens; {LAST_SCENE.title()} closes with concert fade."
        ),
        "intro": {
            "image": f"covers/lesson_{lesson}.png",
            "title": f"Lesson {lesson}",
            "holdBeforeMs": INTRO_HOLD_MS,
            "durationMs": INTRO_DURATION_MS,
        },
        "soundtrack": {"main": STUDY_LESSON},
        "timing": {
            "fadeMs": 1800,
            "kanjiLeadMs": 2000,
            "keywordLeadMs": 5000,
            "verseJpLeadMs": 8500,
            "sceneDurationMs": 22000,
            "studyExitFadeMs": 1800,
            "studyEmptyBeatMs": 500,
            "studyKanjiGapMs": 350,
            "introExitFadeMs": 1200,
            "studyLoopConcertFadeMs": 2500,
            "studyLoopFadeMs": 2500,
            "crossfadeMs": 2500,
            "kenBurnsDurationMs": 60000,
        },
        "background": {
            "mode": "image",
            "kenBurns": True,
            "overlayOpacity": 0.45,
            "blurPx": 0,
        },
        "display": {
            "showKeyword": True,
            "showFurigana": False,
            "loop": True,
            "autoAdvance": True,
        },
        "scenes": scenes,
    }


def build() -> dict:
    html = LESSON_HTML.read_text(encoding="utf-8")
    scenes = reorder_scenes(parse_scenes(html))
    return study_config(
        lesson=38,
        title="KML Ambient Study — Lesson 38",
        scenes=scenes,
    )


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    print(f"  First: {config['scenes'][0]['kanji']} ({config['scenes'][0]['id']})")
    print(f"  Last:  {config['scenes'][-1]['kanji']} ({config['scenes'][-1]['id']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
