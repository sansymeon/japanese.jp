"""Grade 5 gojūon ordering, matured pigments, and part boundaries."""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from grade4_gojuon import PIGMENT_HEX as G4_PIGMENT_HEX, HIRAGANA, KATAKANA, gojuon_key
from grade_palette import mature_grade5

REPO = Path(__file__).resolve().parents[3]
MASTER_CSV = REPO / "data/kanji/kanji_master.csv"

PIGMENT_HEX: dict[str, str] = {k: mature_grade5(v) for k, v in G4_PIGMENT_HEX.items()}

# Inclusive section ranges per part (gojūon order, ~348 s soundtrack for parts 1–3).
PART_SECTION_RANGES: dict[int, tuple[str, str]] = {
    1: ("あ", "く"),
    2: ("け", "し"),
    3: ("す", "は"),
    4: ("ひ", "—"),
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


def load_grade_5_sections() -> list[tuple[str, list[KanjiEntry]]]:
    """All grade-5 joyo kanji grouped by gojūon section, ordered."""
    groups: dict[str, list[KanjiEntry]] = defaultdict(list)
    with MASTER_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("category") != "joyo" or row.get("grade") != "5":
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
    all_sections = load_grade_5_sections()
    start, end = PART_SECTION_RANGES[part]
    i0 = _section_index(all_sections, start)
    i1 = _section_index(all_sections, end)
    return all_sections[i0 : i1 + 1]


def pigment_for_section(kana: str) -> str:
    return PIGMENT_HEX.get(kana, PIGMENT_HEX["—"])
