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
# Strong-tag format used by most lesson compounds pages:
#   <li><strong>河川</strong>【かせん】– rivers</li>
ITEM_STRONG_RE = re.compile(
    r"<li><strong>([^<]+)</strong>【([^】]+)】[–-]\s*([^<]+?)(?:\s*\([^)]*\))?\s*</li>",
)
# Plain + <br> format used by later Lesson 7 entries:
#   <li>九州【きゅうしゅう】<br>– Kyushu (island of Japan)</li>
ITEM_PLAIN_RE = re.compile(
    r"<li>([^<【]+)【([^】]+)】\s*<br\s*/?>\s*[–-]\s*([^<]+?)(?:\s*\([^)]*\))?\s*</li>",
    re.IGNORECASE,
)


def _clean_reading(raw: str) -> str:
    return raw.split("／")[0].split("/")[0].strip()


def _clean_en(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip().rstrip("."))


def _parse_ul_items(ul: str) -> list[dict]:
    items: list[dict] = []
    matches = ITEM_STRONG_RE.findall(ul) or ITEM_PLAIN_RE.findall(ul)
    for jp, reading, en in matches:
        items.append(
            {
                "jp": jp.strip(),
                "reading": _clean_reading(reading),
                "en": _clean_en(en),
            }
        )
    return items


def parse_compounds_html(path: Path) -> dict[str, list[dict]]:
    html = path.read_text(encoding="utf-8")
    out: dict[str, list[dict]] = {}
    for kanji, ul in BLOCK_RE.findall(html):
        kanji = kanji.strip()
        out[kanji] = _parse_ul_items(ul)
    return out


def lesson_compounds(lesson: int) -> dict[str, list[dict]]:
    path = COMPOUNDS_DIR / f"lesson_{lesson:02d}.html"
    if not path.is_file():
        raise FileNotFoundError(path)
    return parse_compounds_html(path)
