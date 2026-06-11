#!/usr/bin/env python3
"""Build heart_v2 ambient collection from lesson HTML (lessons 1–40).

Collects kanji entries whose component-box includes 心, 㣺, or 忄,
or whose kanji character is 心 itself.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HEART_PARTS = frozenset({"心", "㣺", "忄"})
LESSON_MAX = 40

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT.parents[1] / "contents" / "books" / "book_01" / "lessons"
ASSETS_DIR = ROOT.parents[1] / "assets" / "studies"
OUT_PATH = ROOT / "collections" / "heart_v2.json"


def parse_section(section: str, lesson_num: int) -> dict | None:
    kanji_m = re.search(r'data-kanji="([^"]+)"', section)
    if not kanji_m:
        return None
    kanji = kanji_m.group(1)
    if kanji == "Closing Reflection":
        return None

    slug_m = re.search(r'data-slug="([^"]+)"', section)
    slug = slug_m.group(1) if slug_m else ""
    keyword_m = re.search(r'<span class="kanji-keyword">([^<]+)</span>', section)
    keyword = keyword_m.group(1) if keyword_m else ""

    parts = set(re.findall(r'<span class="kanji-part">([^<]+)</span>', section))
    heart_parts = sorted(parts & HEART_PARTS)
    if kanji not in HEART_PARTS and not heart_parts:
        return None

    img_m = re.search(r'assets/studies/([^"]+\.png)', section)
    image_file = img_m.group(1).split("/")[-1] if img_m else f"{slug}.png"
    if not (ASSETS_DIR / image_file).exists():
        return None

    jp_m = re.search(r'<p class="jp-verse[^"]*">(.*?)</p>', section, re.DOTALL)
    en_m = re.search(r'<p class="en-verse">(.*?)</p>', section, re.DOTALL)
    if not jp_m or not en_m:
        return None

    en_text = re.sub(r"<br\s*/?>", "\n", en_m.group(1)).strip()
    en_text = re.sub(r"<[^>]+>", "", en_text)

    return {
        "id": f"L{lesson_num:02d}_{slug or kanji}",
        "lesson": lesson_num,
        "kanji": kanji,
        "keyword": keyword,
        "heartPart": heart_parts[0] if heart_parts else kanji,
        "image": f"studies/{image_file}",
        "video": None,
        "verse": {"jpHtml": jp_m.group(1).strip(), "en": en_text},
    }


def collect_scenes(lesson_max: int = LESSON_MAX) -> list[dict]:
    scenes: list[dict] = []
    seen: set[str] = set()

    for n in range(1, lesson_max + 1):
        path = LESSONS_DIR / f"lesson_{n:02d}.html"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for section in re.split(r'<section class="kanji-entry"', text)[1:]:
            entry = parse_section(section, n)
            if not entry or entry["kanji"] in seen:
                continue
            seen.add(entry["kanji"])
            scenes.append(entry)

    return scenes


def build_config(scenes: list[dict], lesson_max: int = LESSON_MAX) -> dict:
    return {
        "id": "heart_v2",
        "title": "KML Ambient – Heart 心・㣺・忄",
        "notes": (
            "Auto-collected from lessons 1–40 where kanji-part is 心, 㣺, or 忄 "
            "(or kanji is 心). Set scene.video when MP4s are ready."
        ),
        "assetsBase": "../../assets",
        "timing": {
            "fadeMs": 4000,
            "kanjiLeadMs": 2000,
            "imageLeadMs": 6000,
            "verseLeadMs": 12000,
            "holdMs": 35000,
            "crossfadeMs": 5000,
            "kenBurnsDurationMs": 180000,
        },
        "background": {
            "mode": "auto",
            "kenBurns": True,
            "overlayOpacity": 0.55,
            "blurPx": 0,
        },
        "display": {
            "showKeyword": True,
            "showFurigana": False,
            "loop": True,
            "autoAdvance": True,
        },
        "meta": {
            "theme": "heart",
            "heartParts": ["心", "㣺", "忄"],
            "lessonRange": [1, lesson_max],
            "sceneCount": len(scenes),
            "lessonsRepresented": sorted({s["lesson"] for s in scenes}),
        },
        "scenes": scenes,
    }


def main() -> int:
    lesson_max = int(sys.argv[1]) if len(sys.argv) > 1 else LESSON_MAX
    scenes = collect_scenes(lesson_max)
    config = build_config(scenes, lesson_max)
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(scenes)} scenes → {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
