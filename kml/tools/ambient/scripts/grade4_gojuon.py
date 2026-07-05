"""Grade 4 gojūon ordering, pigments, and part boundaries."""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MASTER_CSV = REPO / "data/kanji/kanji_master.csv"

KATAKANA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
HIRAGANA = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"

# Traditional pigment accents per gojūon key
PIGMENT_HEX: dict[str, str] = {
    "あ": "#ad3318",
    "い": "#264a6e",
    "う": "#3d5c3a",
    "え": "#b8860b",
    "お": "#2a6b6b",
    "か": "#6b3a5c",
    "き": "#4a6741",
    "く": "#5c4a6e",
    "け": "#8b6914",
    "こ": "#3d5a6b",
    "さ": "#9b4a3c",
    "し": "#2e5a6e",
    "せ": "#6b5344",
    "そ": "#4a5c3a",
    "た": "#7a4a3a",
    "ち": "#3a5c5c",
    "つ": "#5c4a5a",
    "て": "#6b5a2a",
    "と": "#3a4a6b",
    "な": "#5a4a6b",
    "に": "#4a6b5a",
    "ぬ": "#6b4a4a",
    "ね": "#5a5a3a",
    "の": "#4a5a4a",
    "は": "#8b3a2a",
    "ひ": "#2a4a6b",
    "ふ": "#3a5a4a",
    "へ": "#6b5a3a",
    "ほ": "#2a5a5a",
    "ま": "#5a3a4a",
    "み": "#3a4a5a",
    "む": "#4a3a5a",
    "め": "#6b4a2a",
    "も": "#3a5a3a",
    "や": "#6b3a3a",
    "ゆ": "#2a4a5a",
    "よ": "#5a4a3a",
    "ら": "#4a3a4a",
    "り": "#3a4a4a",
    "る": "#5a3a3a",
    "れ": "#4a4a3a",
    "ろ": "#3a3a4a",
    "わ": "#5a4a4a",
    "を": "#4a3a3a",
    "ん": "#3a3a3a",
    "—": "#6b6358",
}

# Inclusive section ranges per part (~50 kanji each, natural section boundaries).
PART_SECTION_RANGES: dict[int, tuple[str, str]] = {
    1: ("あ", "き"),
    2: ("く", "し"),
    3: ("せ", "の"),
    4: ("は", "—"),
}


@dataclass(frozen=True)
class KanjiEntry:
    kanji: str
    slug: str
    strokes: int
    heisig_number: int
    joyo_index: int
    gojuon: str


def _joyo_index(row: dict) -> int:
    v = row.get("joyo_index") or "0"
    return int(v) if str(v).isdigit() else 99999


def gojuon_key(row: dict) -> str:
    for src in (row.get("on_reading") or "", row.get("kun_readings") or ""):
        if not src:
            continue
        c = src.strip()[0]
        if c in KATAKANA:
            return HIRAGANA[KATAKANA.index(c)]
        if c in HIRAGANA:
            return c
    return "—"


def load_grade_4_sections() -> list[tuple[str, list[KanjiEntry]]]:
    """All grade-4 joyo kanji grouped by gojūon section, ordered."""
    groups: dict[str, list[KanjiEntry]] = defaultdict(list)
    with MASTER_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("category") != "joyo" or row.get("grade") != "4":
                continue
            key = gojuon_key(row)
            groups[key].append(
                KanjiEntry(
                    kanji=row["kanji"],
                    slug=row["slug"].strip(),
                    strokes=int(row["strokes"]),
                    heisig_number=int(row["heisig_number"]),
                    joyo_index=_joyo_index(row),
                    gojuon=key,
                )
            )
    for key in groups:
        groups[key].sort(key=lambda e: e.joyo_index)

    order = [k for k in HIRAGANA if k in groups]
    if "—" in groups:
        order.append("—")
    return [(k, groups[k]) for k in order]


def _section_index(sections: list[tuple[str, list]], kana: str) -> int:
    for i, (k, _) in enumerate(sections):
        if k == kana:
            return i
    raise KeyError(kana)


def sections_for_part(part: int) -> list[tuple[str, list[KanjiEntry]]]:
    all_sections = load_grade_4_sections()
    start, end = PART_SECTION_RANGES[part]
    i0 = _section_index(all_sections, start)
    i1 = _section_index(all_sections, end)
    return all_sections[i0 : i1 + 1]


def pigment_for_section(kana: str) -> str:
    return PIGMENT_HEX.get(kana, PIGMENT_HEX["—"])


def grid_index_for_kana(kana: str) -> int:
    if kana in HIRAGANA:
        return HIRAGANA.index(kana)
    return 49


def all_board_kana() -> list[str]:
    """50-cell board labels (46 gojūon + padding)."""
    cells = list(HIRAGANA)
    while len(cells) < 50:
        cells.append("")
    return cells[:50]
