"""Post-elementary through end of Jōyō kanji (grade S) for soundtrack collections.

Official Jōyō after elementary school (grades 1–6). Does not include post-Jōyō /
high-school-only kanji — that will be a separate series.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MASTER_CSV = REPO / "data/kanji/kanji_master.csv"
STROKE_PAGES = REPO / "tools/strokes/pages"


@dataclass(frozen=True)
class KanjiEntry:
    kanji: str
    slug: str
    strokes: int
    heisig_number: int
    joyo_rank: str


def load_post_elementary_kanji(*, require_stroke_page: bool = True) -> list[KanjiEntry]:
    """Joyo grade-S kanji in Heisig order (post-elementary → end of Jōyō)."""
    rows: list[KanjiEntry] = []
    with MASTER_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("category") != "joyo" or row.get("grade") != "S":
                continue
            slug = row["slug"].strip()
            if require_stroke_page and not (STROKE_PAGES / f"{slug}.html").is_file():
                continue
            rows.append(
                KanjiEntry(
                    kanji=row["kanji"],
                    slug=slug,
                    strokes=int(row["strokes"]),
                    heisig_number=int(row["heisig_number"]),
                    joyo_rank=row.get("joyo_rank") or "",
                )
            )
    rows.sort(key=lambda e: e.heisig_number)
    return rows


def part_slice(
    entries: list[KanjiEntry], part: int, *, size: int
) -> list[KanjiEntry]:
    if part < 1:
        raise ValueError("part must be >= 1")
    start = (part - 1) * size
    end = start + size
    return entries[start:end]


def part_count(entries: list[KanjiEntry], *, size: int) -> int:
    if size < 1:
        raise ValueError("size must be >= 1")
    return max(1, (len(entries) + size - 1) // size)
