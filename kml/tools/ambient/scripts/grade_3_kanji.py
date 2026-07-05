"""Grade 3 (elementary) Jōyō kanji for the cheerful soundtrack series."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MASTER_CSV = REPO / "data/kanji/kanji_master.csv"


@dataclass(frozen=True)
class KanjiEntry:
    kanji: str
    slug: str
    strokes: int
    heisig_number: int
    joyo_index: int


def _joyo_index(row: dict) -> int:
    v = row.get("joyo_index") or "0"
    return int(v) if str(v).isdigit() else 99999


def load_grade_3_kanji() -> list[KanjiEntry]:
    """Grade-3 Jōyō kanji in school joyo_index order."""
    rows: list[KanjiEntry] = []
    with MASTER_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("category") != "joyo" or row.get("grade") != "3":
                continue
            rows.append(
                KanjiEntry(
                    kanji=row["kanji"],
                    slug=row["slug"].strip(),
                    strokes=int(row["strokes"]),
                    heisig_number=int(row["heisig_number"]),
                    joyo_index=_joyo_index(row),
                )
            )
    rows.sort(key=lambda e: e.joyo_index)
    return rows
