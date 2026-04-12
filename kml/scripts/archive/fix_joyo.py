#!/usr/bin/env python3

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "tools/strokes/template/stroke_template.html"
OUTPUT_DIR = ROOT / "tools/strokes/pages"
CSV_FILE = ROOT / "data/kanji/kanji_master.csv"

template = TEMPLATE.read_text(encoding="utf-8")

rows = []
with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

KATAKANA_RE = re.compile(r"[ァ-ヴー]")
HIRAGANA_RE = re.compile(r"[ぁ-ゖ]")
CATEGORY_VALUES = {"joyo", "heisig_extra"}


def _clean_separators(value: str) -> str:
    if not value:
        return ""
    return (
        value.replace("、", ",")
        .replace("､", ",")
        .replace("・", ",")
        .replace("･", ",")
        .strip()
    )


def _select_tokens(value: str, script_re: re.Pattern) -> list[str]:
    if not value:
        return []

    cleaned = _clean_separators(value)
    tokens = re.split(r"[,\s/]+", cleaned)

    result = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if script_re.search(token):
            result.append(token)
    return result


def _sanitize_readings(idx, kanji, raw_on, raw_kun, raw_category):
    category = (raw_category or "").strip().lower()

    raw_on = (raw_on or "").strip()
    raw_kun = (raw_kun or "").strip()

    lower_on = raw_on.lower()
    lower_kun = raw_kun.lower()

    if not category:
        if "joyo" in lower_on:
            category = "joyo"
            raw_on = ""
        elif "joyo" in lower_kun:
            category = "joyo"
            raw_kun = ""

    for label in CATEGORY_VALUES:
        if label in lower_on:
            raw_on = ""
        if label in lower_kun:
            raw_kun = ""

    on_tokens = _select_tokens(raw_on, KATAKANA_RE)
    kun_tokens = _select_tokens(raw_kun, HIRAGANA_RE)

    on_reading = "、".join(on_tokens)
    kun_readings = "、".join(kun_tokens)

    return on_reading, kun_readings, category


def _normalize_row(idx, row):
    kanji = (row.get("kanji") or "").strip()

    slug_source = (row.get("slug") or row.get("keyword_id") or "").strip()
    slug = slug_source.replace('"', "").replace(",", "").strip() or kanji

    strokes_raw = (row.get("strokes") or "").strip()
    try:
        stroke_count = int(strokes_raw)
    except:
        print(f"[WARN] Row {idx} ({kanji}): invalid strokes '{strokes_raw}', defaulting to 1")
        stroke_count = 1

    raw_on = row.get("on_reading") or ""
    raw_kun = row.get("kun_readings") or ""
    raw_category = row.get("category") or ""

    on_reading, kun_readings, category = _sanitize_readings(
        idx, kanji, raw_on, raw_kun, raw_category
    )

    keyword_raw = (row.get("keyword") or "").split(";")[0].strip()
    keyword = keyword_raw or slug

    return {
        "kanji": kanji,
        "slug": slug,
        "stroke_count": stroke_count,
        "on_reading": on_reading,
        "kun_readings": kun_readings,
        "category": category,
        "keyword": keyword,
    }


def make_stroke_layers(kanji, stroke_count):
    parts = ['<div class="stroke-order">']

    for i in range(1, stroke_count + 1):
        parts.append(
            f'<img id="color{i}" class="fade-in" '
            f'src="tools/strokes/images/{kanji}/color{i:02}.png" '
            f'alt="Stroke {i} Color" loading="lazy" decoding="async" />'
        )

        parts.append(
            f'<img id="black{i}" class="fade-in" '
            f'src="tools/strokes/images/{kanji}/black{i:02}.png" '
            f'alt="Stroke {i} Black" loading="lazy" decoding="async" />'
        )

    parts.append("</div>")
    return "\n".join(parts)


normalized_rows = [_normalize_row(idx, row) for idx, row in enumerate(rows)]


for idx, row in enumerate(normalized_rows):
    kanji = row["kanji"]
    slug = row["slug"]
    stroke_count = row["stroke_count"]

    # ✅ Reading fallback (ON → KUN)
    reading = (
        (row["on_reading"] or row["kun_readings"] or "")
        .split("、")[0]
        .strip()
    )

    keyword = row["keyword"]

    # NEXT link
    if idx < len(normalized_rows) - 1:
        next_slug = normalized_rows[idx + 1]["slug"]
    else:
        next_slug = "contents/books/book_01/lessons/index"

    html = template
    html = html.replace("{{KANJI}}", kanji)
    html = html.replace("{{SLUG}}", slug)
    html = html.replace("{{KEYWORD}}", keyword.capitalize())
    html = html.replace("{{READING}}", reading)
    html = html.replace("{{NEXT}}", next_slug)

    # ✅ Correct placeholder
    html = html.replace(
        "{{STROKE_ORDER_CONTENT}}",
        make_stroke_layers(kanji, stroke_count)
    )

    out = OUTPUT_DIR / f"{slug}.html"
    out.write_text(html, encoding="utf-8")

    print(f"Created {out.name}")