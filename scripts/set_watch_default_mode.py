#!/usr/bin/env python3
"""Default Start Here dual-mode rooms to Watch & Listen."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START_HERE = ROOT / "start-here"

OLD_TOGGLE = """          aria-label="How to take this room"
        >
          <button type="button" data-watch-select="read" aria-pressed="true">Read</button>
          <button type="button" data-watch-select="watch" aria-pressed="false">
            Watch &amp; Listen
          </button>"""

NEW_TOGGLE = """          aria-label="Watch &amp; Listen or Read"
        >
          <button type="button" data-watch-select="watch" aria-pressed="true">
            Watch &amp; Listen
          </button>
          <button type="button" data-watch-select="read" aria-pressed="false">Read</button>"""


def update_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    if OLD_TOGGLE not in text:
        return False

    text = text.replace(OLD_TOGGLE, NEW_TOGGLE)
    text = text.replace('class="museum-page is-read-mode"', 'class="museum-page is-watch-mode"')
    if 'is-watch-mode' not in text and 'is-read-mode' not in text:
        text = text.replace(
            '<body class="museum-page" data-beginner-lesson=',
            '<body class="museum-page is-watch-mode" data-beginner-lesson=',
            1,
        )
    text = re.sub(
        r'<div data-watch-read(?!\s+hidden)(?=>|\s)',
        '<div data-watch-read hidden',
        text,
        count=1,
    )
    text = text.replace('<div data-watch-watch hidden>', '<div data-watch-watch>', 1)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for html_path in sorted(START_HERE.glob("lesson-*/index.html")):
        if update_html(html_path):
            changed += 1
            print(html_path.relative_to(ROOT))
    print(f"Updated {changed} lesson pages.")


if __name__ == "__main__":
    main()
