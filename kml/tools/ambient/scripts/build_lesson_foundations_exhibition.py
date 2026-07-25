#!/usr/bin/env python3
"""Build exhibition/lesson_N_foundations.json — L5 standard (Gallery Seal, mobile-refine).

Usage:
  python3 scripts/build_lesson_foundations_exhibition.py --lesson 33
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from foundations_exhibition_common import exhibition_foundations_config  # noqa: E402

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)

# Same Foundations beds as gallery lessons 33–37.
DEFAULT_TRACK_BY_LESSON = {
    33: "study_version_1",
    34: "study_version_2",
    35: "study_version_2",
    36: "study_version_3",
    37: "study_version_2",
}


def soundtrack_for(lesson: int) -> str:
    key = DEFAULT_TRACK_BY_LESSON.get(lesson) or f"study_version_{(lesson % 3) or 3}"
    return f"audio/{key}_minus3db.mp3"


def image_rev(relative: str) -> int | None:
    path = ASSETS / relative
    if path.is_file():
        return int(path.stat().st_mtime)
    return None


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
        rev = image_rev(image)
        if rev is not None:
            scene["imageRev"] = rev
        scenes.append(scene)
    return scenes


def build(lesson: int) -> dict:
    html_path = REPO / "contents/books/book_01/lessons" / f"lesson_{lesson:02d}.html"
    html = html_path.read_text(encoding="utf-8")
    scenes = parse_scenes(html)
    if not scenes:
        raise SystemExit(f"No scenes parsed for lesson {lesson}")
    soundtrack = soundtrack_for(lesson)
    track_label = Path(soundtrack).stem.replace("_minus3db", "").replace("_", " ").title()
    last_kw = scenes[-1]["keyword"]
    config = exhibition_foundations_config(
        lesson=lesson,
        title=f"KML Ambient Foundations — Lesson {lesson} (Exhibition)",
        notes=(
            "Exhibition / presentation build (Lesson 5 standard). "
            f"Original lesson order; {last_kw} closes with Gallery Seal Ending. "
            f"Soundtrack: {track_label}."
        ),
        scenes=scenes,
    )
    config["intro"]["image"] = f"covers/lesson_{lesson:02d}.png"
    config["soundtrack"] = {"main": soundtrack}
    return config


def out_path(lesson: int) -> Path:
    return ROOT / "exhibition" / f"lesson_{lesson}_foundations.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, required=True)
    args = parser.parse_args()

    config = build(args.lesson)
    path = out_path(args.lesson)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {path}")
    print(f"  First: {config['scenes'][0]['kanji']} ({config['scenes'][0]['id']})")
    print(f"  Last:  {config['scenes'][-1]['kanji']} ({config['scenes'][-1]['id']})")
    print(f"  Audio: {config['soundtrack']['main']}")
    print(f"  typography: {config['display'].get('typography')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
