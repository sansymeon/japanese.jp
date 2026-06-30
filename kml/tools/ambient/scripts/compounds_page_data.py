"""Parse compound word lists from KML compounds lesson HTML."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
COMPOUNDS_DIR = REPO / "contents/books/book_01/compounds"

BLOCK_RE = re.compile(
    r'<span class="kanji-compound-font">([^<]+)</span>.*?<ul>(.*?)</ul>',
    re.DOTALL,
)
ITEM_RE = re.compile(
    r"<li><strong>([^<]+)</strong>【([^】]+)】[–-]\s*([^<]+?)(?:\s*\([^)]*\))?\s*</li>",
)


def _clean_reading(raw: str) -> str:
    return raw.split("／")[0].split("/")[0].strip()


def _clean_en(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip().rstrip("."))


def parse_compounds_html(path: Path) -> dict[str, list[dict]]:
    html = path.read_text(encoding="utf-8")
    out: dict[str, list[dict]] = {}
    for kanji, ul in BLOCK_RE.findall(html):
        kanji = kanji.strip()
        items: list[dict] = []
        for jp, reading, en in ITEM_RE.findall(ul):
            items.append(
                {
                    "jp": jp.strip(),
                    "reading": _clean_reading(reading),
                    "en": _clean_en(en),
                }
            )
        out[kanji] = items
    return out


def lesson_compounds(lesson: int) -> dict[str, list[dict]]:
    path = COMPOUNDS_DIR / f"lesson_{lesson:02d}.html"
    if not path.is_file():
        raise FileNotFoundError(path)
    return parse_compounds_html(path)
