"""Read KanjiVG stroke data from Different Strokes HTML pages."""

from __future__ import annotations

import re
from pathlib import Path

STROKES_ROOT = Path(__file__).resolve().parent
PAGES_DIR = STROKES_ROOT / "pages"
# Relative to kml/tools/ambient/ when served locally (requires strokes symlink).
PAGE_URL_BASE = "strokes/pages"

KANJI_FONT_RE = re.compile(r'<span class="kanji-main-font">([^<]+)</span>')
STROKE_SVG_RE = re.compile(
    r'<div class="stroke-order">[\s\S]*?(<svg[\s\S]*?</svg>)',
    re.DOTALL,
)


def stroke_page_path(slug: str) -> Path:
    return PAGES_DIR / f"{slug}.html"


def stroke_page_url(slug: str) -> str:
    return f"{PAGE_URL_BASE}/{slug}.html"


def extract_stroke_page(slug: str, fallback_kanji: str = "") -> dict:
    path = stroke_page_path(slug)
    if not path.is_file():
        raise FileNotFoundError(f"Missing stroke page: {path}")
    html = path.read_text(encoding="utf-8")
    kanji_m = KANJI_FONT_RE.search(html)
    svg_m = STROKE_SVG_RE.search(html)
    if not svg_m:
        raise ValueError(f"Could not parse stroke page: {slug}")
    svg = svg_m.group(1).strip()
    kanji = kanji_m.group(1) if kanji_m else ""
    if not kanji:
        elem_m = re.search(r'kvg:element="([^"]+)"', svg)
        kanji = elem_m.group(1) if elem_m else fallback_kanji
    if not kanji:
        raise ValueError(f"Could not resolve kanji for stroke page: {slug}")
    stroke_count = len(re.findall(r"<path\b", svg))
    return {
        "kanji": kanji,
        "svg": svg,
        "strokeCount": stroke_count,
        "strokePage": stroke_page_url(slug),
    }


def stroke_metadata(slug: str, fallback_kanji: str = "") -> dict:
    """Lightweight metadata for exhibition collections (no embedded SVG)."""
    data = extract_stroke_page(slug, fallback_kanji)
    return {
        "strokePage": data["strokePage"],
        "strokeCount": data["strokeCount"],
        "kanji": data["kanji"],
    }
