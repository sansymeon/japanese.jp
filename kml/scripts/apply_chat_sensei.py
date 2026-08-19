#!/usr/bin/env python3
"""Insert Ask Chat-Sensei CSS/JS includes into Heisig lesson pages.

Does not regenerate kanji entries or verses. The flourish is injected at
runtime by chat-sensei.js from existing .kanji-entry markup.

Usage:
  python3 kml/scripts/apply_chat_sensei.py --lesson 1
  python3 kml/scripts/apply_chat_sensei.py --all
"""

from __future__ import annotations

import argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LESSONS = BASE / "contents/books/book_01/lessons"
TEMPLATE = BASE / "templates/lesson_template.html"

CSS_HREF = "../../../../assets/site/css/chat-sensei.css"
JS_SRC = "../../../../assets/site/js/chat-sensei.js"

CSS_TAG = f'<link rel="stylesheet" href="{CSS_HREF}">'
JS_TAG = f'<script src="{JS_SRC}"></script>'
STYLE_MARKER = '<link rel="stylesheet" href="../../../../assets/site/css/kml_style.css">'
SCRIPT_MARKER = '<script src="../../../../assets/site/js/kml.js"></script>'


def apply_text(html: str) -> tuple[str, bool]:
    changed = False
    if CSS_TAG not in html and STYLE_MARKER in html:
        html = html.replace(STYLE_MARKER, STYLE_MARKER + "\n" + CSS_TAG, 1)
        changed = True
    if JS_TAG not in html and SCRIPT_MARKER in html:
        html = html.replace(SCRIPT_MARKER, SCRIPT_MARKER + "\n" + JS_TAG, 1)
        changed = True
    return html, changed


def apply_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    updated, changed = apply_text(original)
    if changed:
        path.write_text(updated, encoding="utf-8")
    return changed


def lesson_path(number: int) -> Path:
    return LESSONS / f"lesson_{number:02d}.html"


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--lesson", type=int, help="Prototype a single lesson, e.g. 1")
    group.add_argument("--all", action="store_true", help="Apply to every Heisig lesson page")
    parser.add_argument("--template", action="store_true", help="Also update templates/lesson_template.html")
    args = parser.parse_args()

    paths: list[Path] = []
    if args.lesson is not None:
        path = lesson_path(args.lesson)
        if not path.exists():
            raise SystemExit(f"Not found: {path}")
        paths.append(path)
    else:
        paths = sorted(LESSONS.glob("lesson_*.html"))

    if args.template:
        paths.append(TEMPLATE)

    updated = 0
    for path in paths:
        if apply_file(path):
            updated += 1
            print(f"updated {path.relative_to(BASE.parent)}")
        else:
            print(f"unchanged {path.relative_to(BASE.parent)}")
    print(f"{updated} file(s) updated")


if __name__ == "__main__":
    main()
