#!/usr/bin/env python3
"""Build exhibition/lesson_3_study.json — original order, Gallery Seal Ending."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
LESSON_HTML = REPO / "contents/books/book_01/lessons/lesson_03.html"
OUT_PATH = ROOT / "exhibition" / "lesson_3_study.json"

STUDY_LESSON = "audio/study_version_2_minus3db.mp3"

IMAGE_FRAMING_OVERRIDES: dict[str, dict[str, str | float]] = {
    "round": {
        # Full moon upper-right — pull back so the round light stays in frame
        "imageFocus": "62% 28%",
        "imageScale": 0.82,
    },
    "up": {
        # Kite climbing — keep kite, boy, and village in frame
        "imageFocus": "54% 38%",
        "imageScale": 0.84,
    },
    "rise": {
        # Sky lantern above village — pull back to keep kite in frame
        "imageFocus": "55% 32%",
        "imageScale": 0.82,
    },
    "signal": {
        # 卜 — divination stick on mountain cairn
        "imageScale": 0.85,
    },
    "below": {
        # Cat under shrine step — pull back to show full cat
        "imageFocus": "42% 55%",
        "imageScale": 0.85,
    },
    "eminent": {
        # 卓 — tokonoma ikebana and stand
        "imageScale": 0.85,
    },
    "pop_song": {
        "imageScale": 0.88,
    },
    "only": {
        # Tea master — keep head and raised finger in frame during Ken Burns drift
        "imageFocus": "50% 32%",
        "imageScale": 0.88,
    },
    "elbow": {
        # Woman at railing — keep face in frame during Ken Burns drift
        "imageFocus": "48% 32%",
        "imageScale": 0.88,
    },
    "virtue": {
        # Samurai profile — pan to left shoulder and face
        "imageFocus": "32% 30%",
        "imageScale": 0.88,
    },
    "employee": {
        # Group portrait — keep all four faces in frame
        "imageFocus": "50% 34%",
        "imageScale": 0.85,
    },
}

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_exhibition_common import exhibition_study_config  # noqa: E402

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
        scenes.append(
            {
                "id": slug,
                "kanji": kanji_m.group(1),
                "keyword": keyword,
                "image": image,
                "video": None,
                "verse": {
                    "jpHtml": jp_m.group(1).strip(),
                    "en": en,
                },
                **IMAGE_FRAMING_OVERRIDES.get(slug, {}),
            }
        )
    return scenes


def build() -> dict:
    html = LESSON_HTML.read_text(encoding="utf-8")
    config = exhibition_study_config(
        lesson=3,
        title="KML Ambient Study — Lesson 3 (Exhibition)",
        notes=(
            "Exhibition / presentation build. Original lesson order; "
            "Employee closes with Gallery Seal Ending. Soundtrack: Study Version 2."
        ),
        scenes=parse_scenes(html),
    )
    config["intro"]["image"] = "covers/lesson_03.png"
    config["soundtrack"] = {"main": STUDY_LESSON}
    return config


def main() -> int:
    config = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    print(f"  First: {config['scenes'][0]['kanji']} ({config['scenes'][0]['id']})")
    print(f"  Last:  {config['scenes'][-1]['kanji']} ({config['scenes'][-1]['id']})")
    print(f"  Audio: {config['soundtrack']['main']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
