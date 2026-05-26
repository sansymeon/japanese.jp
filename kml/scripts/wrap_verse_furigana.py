#!/usr/bin/env python3
"""Wrap kanji in jp-verse blocks with ruby placeholders for manual furigana."""

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LESSONS_DIR = BASE / "contents/books/book_01/lessons"

KANJI_RE = re.compile(
    r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3005\u3006]"
)

JP_VERSE_RE = re.compile(
    r'<p class="jp-verse([^"]*)">(.*?)</p>',
    re.DOTALL,
)


def wrap_kanji_text(text: str) -> str:
    return KANJI_RE.sub(lambda m: f"<ruby>{m.group(0)}<rt>?</rt></ruby>", text)


def wrap_kanji_in_html(fragment: str) -> str:
    parts = re.split(r"(<[^>]+>)", fragment)
    return "".join(
        wrap_kanji_text(p) if p and not p.startswith("<") else p for p in parts
    )


def process_jp_verse(match: re.Match) -> str:
    classes, inner = match.group(1), match.group(2)
    if "<ruby>" not in inner:
        inner = wrap_kanji_in_html(inner)
    if "toggle-reading" not in classes:
        classes = f"{classes} toggle-reading"
    return f'<p class="jp-verse{classes}">{inner}</p>'


def process_file(path: Path) -> int:
    html = path.read_text(encoding="utf-8")
    verses = JP_VERSE_RE.findall(html)
    if not verses:
        return 0
    new_html = JP_VERSE_RE.sub(process_jp_verse, html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
    return len(verses)


def main() -> None:
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 27
    total = 0
    for n in range(start, end + 1):
        path = LESSONS_DIR / f"lesson_{n:02d}.html"
        if not path.exists():
            print(f"skip (missing): {path.name}")
            continue
        count = process_file(path)
        if count:
            print(f"{path.name}: {count} jp-verse blocks")
            total += count
    print(f"done — {total} verses processed")


if __name__ == "__main__":
    main()
