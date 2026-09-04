#!/usr/bin/env python3
"""Generate minimal foundations JSON from lesson HTML (canonical order + keywords).

Does not invent verses or artwork. Use for Kanji Components builds and other
pipelines that need lesson order without a full exhibition foundations file.

Usage:
  python3 scripts/build_foundations_from_html.py --lessons 31-35
  python3 scripts/build_foundations_from_html.py --lessons 21,22,23 --force
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from lib.html_component_parser import parse_lesson_html  # noqa: E402

LESSONS_DIR = BASE / "contents" / "books" / "book_01" / "lessons"
OUT_DIR = BASE / "tools" / "ambient" / "exhibition"


def parse_lesson_spec(spec: str) -> list[int]:
    out: list[int] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(chunk))
    return sorted(set(out))


def make_foundations(lesson: int, scenes: list[dict]) -> dict:
    pad = f"{lesson:02d}"
    return {
        "id": f"lesson_{lesson}_foundations",
        "title": f"KML Ambient Foundations — Lesson {lesson} (Exhibition)",
        "presentation": "foundations",
        "assetsBase": "../../assets",
        "notes": (
            "Generated from lesson HTML (canonical order + keywords). "
            "Full exhibition verses/images not included."
        ),
        "source": "lesson_html",
        "ending": {"type": "gallerySeal", "sealImage": "images/gold_closing.png"},
        "intro": {
            "image": f"covers/lesson_{pad}.jpg",
            "title": f"Lesson {lesson}",
            "holdBeforeMs": 1000,
            "durationMs": 9000,
        },
        "soundtrack": {"main": "audio/study_version_2_minus3db.mp3"},
        "timing": {
            "fadeMs": 1800,
            "kanjiLeadMs": 2000,
            "keywordLeadMs": 5000,
            "verseJpLeadMs": 8500,
            "sceneDurationMs": 22000,
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
            "loop": False,
            "autoAdvance": True,
            "typography": "mobile-refine",
        },
        "scenes": scenes,
    }


def build_lesson(lesson: int, force: bool) -> Path | None:
    path = OUT_DIR / f"lesson_{lesson}_foundations.json"
    if path.exists() and not force:
        print(f"skip {path.relative_to(BASE)} (exists; use --force)")
        return None

    html_path = LESSONS_DIR / f"lesson_{lesson:02d}.html"
    if not html_path.exists():
        raise FileNotFoundError(html_path)

    decomps = parse_lesson_html(html_path, lesson)
    scenes = []
    for d in decomps:
        slug = d.slug or "_".join(d.keyword.lower().replace("'", "").split())
        scenes.append(
            {
                "id": slug,
                "kanji": d.kanji,
                "keyword": d.keyword,
                "image": f"studies/{slug}.jpg",
                "video": None,
                "verse": {"jpHtml": "", "en": ""},
            }
        )

    data = make_foundations(lesson, scenes)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(BASE)} ({len(scenes)} scenes)")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lessons", required=True, help="e.g. 31-35 or 21,22,23")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    for n in parse_lesson_spec(args.lessons):
        build_lesson(n, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
