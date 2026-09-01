#!/usr/bin/env python3
"""Remove Hiragana puzzle sections from Start Here room pages (0–40)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START_HERE = ROOT / "start-here"

PUZZLE_SECTION = re.compile(
    r"\n[ \t]*<section class=\"kana-puzzle-section[^\"]*\"[\s\S]*?</section>\n",
    re.MULTILINE,
)

ROOM40_CHART = re.compile(
    r"\n[ \t]*<section class=\"kana-complete kana-reference-section\"[\s\S]*?</section>\n",
    re.MULTILINE,
)

ARIA_PUZZLE = re.compile(r'\n[ \t]*aria-labelledby="puzzle-heading"\n')

BLANK_RUNS = re.compile(r"\n{4,}")


def clean_html(html: str) -> str:
    html = PUZZLE_SECTION.sub("\n", html)
    html = ROOM40_CHART.sub("\n", html)
    html = ARIA_PUZZLE.sub("\n", html)
    html = BLANK_RUNS.sub("\n\n\n", html)
    return html


def main() -> None:
    changed = 0
    for n in range(41):
        path = START_HERE / f"lesson-{n}" / "index.html"
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        updated = clean_html(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"Updated {changed} lesson pages.")


if __name__ == "__main__":
    main()
