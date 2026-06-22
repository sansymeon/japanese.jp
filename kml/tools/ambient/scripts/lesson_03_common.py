"""Shared scene parsing and image framing for Lesson 3 ambient study builds."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2].parent
ASSETS = REPO / "assets"
LESSON_HTML = REPO / "contents/books/book_01/lessons/lesson_03.html"

# imageScale < 1 zooms out and leaves gaps on full-bleed landscape art.
# Only keep overrides for baked-in letterboxing (scale > 1) or rare composition tweaks.
IMAGE_FRAMING_OVERRIDES: dict[str, dict[str, str | float]] = {
    "pop_song": {
        # Baked-in horizontal letterbox bars — zoom to full cover
        "imageScale": 1.14,
        "imageFocus": "50% 48%",
    },
}

SECTION_RE = re.compile(
    r'<section class="kanji-entry"(.*?)</section>',
    re.DOTALL,
)


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
            **IMAGE_FRAMING_OVERRIDES.get(slug, {}),
        }
        rev = image_rev(image)
        if rev is not None:
            scene["imageRev"] = rev
        scenes.append(scene)
    return scenes


def load_scenes() -> list[dict]:
    return parse_scenes(LESSON_HTML.read_text(encoding="utf-8"))
