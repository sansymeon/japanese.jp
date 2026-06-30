"""Collect exhibition scenes from lesson HTML by primitive (kanji-part) match."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT.parents[1] / "contents" / "books" / "book_01" / "lessons"
ASSETS_DIR = ROOT.parents[1] / "assets" / "studies"

_KANJI_PART_RE = re.compile(r'<span class="kanji-part"[^>]*>([^<]+)</span>')
_DATA_PART_RE = re.compile(r'data-part="([^"]+)"')
_DATA_FAMILY_RE = re.compile(r'data-family="([^"]+)"')


def extract_parts(section: str) -> set[str]:
    parts = set(_KANJI_PART_RE.findall(section))
    parts.update(_DATA_PART_RE.findall(section))
    return parts


def extract_families(section: str) -> set[str]:
    return set(_DATA_FAMILY_RE.findall(section))


def match_primitive(
    section: str,
    kanji: str,
    *,
    primitive_parts: frozenset[str],
    family_kanji: frozenset[str] | None = None,
    family_ids: frozenset[str] | None = None,
) -> str | None:
    """Return primitivePart label if section matches, else None."""
    parts = extract_parts(section)
    matched = sorted(parts & primitive_parts)
    if kanji in primitive_parts:
        return "/".join(matched) if matched else kanji
    if matched:
        return "/".join(matched)
    if family_kanji and kanji in family_kanji:
        return kanji
    if family_ids:
        hit = sorted(extract_families(section) & family_ids)
        if hit:
            return hit[0]
    return None


def parse_section(
    section: str,
    lesson_num: int,
    *,
    primitive_parts: frozenset[str],
    family_kanji: frozenset[str] | None = None,
    family_ids: frozenset[str] | None = None,
) -> dict | None:
    kanji_m = re.search(r'data-kanji="([^"]+)"', section)
    if not kanji_m:
        return None
    kanji = kanji_m.group(1)
    if kanji == "Closing Reflection":
        return None

    primitive_part = match_primitive(
        section,
        kanji,
        primitive_parts=primitive_parts,
        family_kanji=family_kanji,
        family_ids=family_ids,
    )
    if not primitive_part:
        return None

    slug_m = re.search(r'data-slug="([^"]+)"', section)
    slug = slug_m.group(1) if slug_m else ""
    keyword_m = re.search(r'<span class="kanji-keyword">([^<]+)</span>', section)
    keyword = keyword_m.group(1) if keyword_m else ""

    img_m = re.search(r'assets/studies/([^"]+\.png)', section)
    image_file = img_m.group(1).split("/")[-1] if img_m else f"{slug}.png"
    if not (ASSETS_DIR / image_file).exists():
        return None

    jp_m = re.search(r'<p class="jp-verse[^"]*">(.*?)</p>', section, re.DOTALL)
    en_m = re.search(r'<p class="en-verse">(.*?)</p>', section, re.DOTALL)
    if not jp_m or not en_m:
        return None

    en_text = re.sub(r"<br\s*/?>", "\n", en_m.group(1)).strip()
    en_text = re.sub(r"<[^>]+>", "", en_text)

    return {
        "id": f"L{lesson_num:02d}_{slug or kanji}",
        "lesson": lesson_num,
        "kanji": kanji,
        "keyword": keyword,
        "primitivePart": primitive_part,
        "image": f"studies/{image_file}",
        "video": None,
        "verse": {"jpHtml": jp_m.group(1).strip(), "en": en_text},
    }


def collect_scenes(
    *,
    primitive_parts: frozenset[str],
    family_kanji: frozenset[str] | None = None,
    family_ids: frozenset[str] | None = None,
    lesson_max: int | None = None,
) -> list[dict]:
    scenes: list[dict] = []
    seen: set[str] = set()

    paths = sorted(LESSONS_DIR.glob("lesson_*.html"), key=lambda p: int(p.stem.split("_")[1]))
    for path in paths:
        n = int(path.stem.split("_")[1])
        if lesson_max is not None and n > lesson_max:
            break
        text = path.read_text(encoding="utf-8")
        for section in re.split(r'<section class="kanji-entry"', text)[1:]:
            entry = parse_section(
                section,
                n,
                primitive_parts=primitive_parts,
                family_kanji=family_kanji,
                family_ids=family_ids,
            )
            if not entry or entry["kanji"] in seen:
                continue
            seen.add(entry["kanji"])
            scenes.append(entry)

    return scenes


def list_gaps(
    *,
    primitive_parts: frozenset[str],
    family_kanji: frozenset[str] | None = None,
    family_ids: frozenset[str] | None = None,
    lesson_max: int | None = None,
) -> list[dict]:
    """Kanji matching rules but missing artwork and/or verses."""
    gaps: list[dict] = []
    seen: set[str] = set()

    paths = sorted(LESSONS_DIR.glob("lesson_*.html"), key=lambda p: int(p.stem.split("_")[1]))
    for path in paths:
        n = int(path.stem.split("_")[1])
        if lesson_max is not None and n > lesson_max:
            break
        text = path.read_text(encoding="utf-8")
        for section in re.split(r'<section class="kanji-entry"', text)[1:]:
            kanji_m = re.search(r'data-kanji="([^"]+)"', section)
            if not kanji_m:
                continue
            kanji = kanji_m.group(1)
            if kanji == "Closing Reflection" or kanji in seen:
                continue

            primitive_part = match_primitive(
                section,
                kanji,
                primitive_parts=primitive_parts,
                family_kanji=family_kanji,
                family_ids=family_ids,
            )
            if not primitive_part:
                continue
            seen.add(kanji)

            slug_m = re.search(r'data-slug="([^"]+)"', section)
            slug = slug_m.group(1) if slug_m else ""
            img_m = re.search(r'assets/studies/([^"]+\.png)', section)
            image_file = img_m.group(1).split("/")[-1] if img_m else f"{slug}.png"
            has_art = (ASSETS_DIR / image_file).exists()
            has_jp = bool(re.search(r'<p class="jp-verse', section))
            has_en = bool(re.search(r'<p class="en-verse">', section))
            if has_art and has_jp and has_en:
                continue

            missing: list[str] = []
            if not has_art:
                missing.append("artwork")
            if not has_jp or not has_en:
                missing.append("verses")
            gaps.append(
                {
                    "lesson": n,
                    "kanji": kanji,
                    "slug": slug,
                    "primitivePart": primitive_part,
                    "imageFile": image_file,
                    "missing": missing,
                }
            )

    return gaps
