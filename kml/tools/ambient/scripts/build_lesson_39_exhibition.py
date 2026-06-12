#!/usr/bin/env python3
"""Build exhibition/lesson_39_study.json — Friend first, Uncle last, Gallery Seal Ending."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
LESSON_HTML = REPO / "contents/books/book_01/lessons/lesson_39.html"
OUT_PATH = ROOT / "exhibition" / "lesson_39_study.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_exhibition_common import exhibition_study_config, reorder_scenes  # noqa: E402

FIRST_SCENE = "friend"
LAST_SCENE = "uncle"

# Presentation-only background framing (object-position in ambient player).
IMAGE_FOCUS_OVERRIDES = {
    "light_weight": "42% 48%",
}

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)


def parse_scenes(html: str) -> list[dict]:
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
            "id": slug,
            "kanji": kanji_m.group(1),
            "keyword": keyword,
            "image": image,
            "video": None,
            "verse": {
                "jpHtml": jp_m.group(1).strip(),
                "en": en,
            },
        }
        if slug in IMAGE_FOCUS_OVERRIDES:
            scene["imageFocus"] = IMAGE_FOCUS_OVERRIDES[slug]
        scenes.append(scene)
    return scenes


def build() -> dict:
    html = LESSON_HTML.read_text(encoding="utf-8")
    scenes = reorder_scenes(parse_scenes(html), first=FIRST_SCENE, last=LAST_SCENE)
    return exhibition_study_config(
        lesson=39,
        title="KML Ambient Study — Lesson 39 (Exhibition)",
        notes=(
            "Exhibition / presentation build. Friend opens; Uncle closes with Gallery Seal Ending "
            "(image hold, fade to black, gold 漢 seal, music resolves, end on seal)."
        ),
        scenes=scenes,
    )


def main() -> int:
    config = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    print(f"  First: {config['scenes'][0]['kanji']} ({config['scenes'][0]['id']})")
    print(f"  Last:  {config['scenes'][-1]['kanji']} ({config['scenes'][-1]['id']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
