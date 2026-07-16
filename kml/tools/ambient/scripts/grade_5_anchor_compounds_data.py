"""Grade 5 anchor compound seed data — school edition.

Source: collections/grade_5/grade_5_jukugo_list.json (10 parts; 20×9 + 13).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JUKUGO_LIST = ROOT / "collections" / "grade_5" / "grade_5_jukugo_list.json"


def _entry(
    kanji: str,
    anchor: str,
    reading: str,
    *,
    display_order: int,
    part: int,
    exception: bool = False,
    emphasize: str | None = None,
    exception_reason: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "kanji": kanji,
        "anchor": anchor,
        "reading": reading,
        "grade": 4,
        "lesson": None,
        "part": part,
        "displayOrder": display_order,
        "exception": exception,
    }
    if exception:
        target = emphasize or kanji
        item["visualWeightTarget"] = target
        item["emphasize"] = target
        if exception_reason:
            item["exceptionReason"] = exception_reason
    if notes:
        item["notes"] = notes
    return item


def _load_jukugo_doc() -> dict[str, Any]:
    if not JUKUGO_LIST.is_file():
        raise FileNotFoundError(f"Missing Grade 5 jukugo list: {JUKUGO_LIST}")
    return json.loads(JUKUGO_LIST.read_text(encoding="utf-8"))


def _entries_from_jukugo_doc(doc: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen_anchors: dict[str, str] = {}
    order = 0

    # Grade 5 list shape: {"jukugo": {"part1": [[kanji, word, reading], ...], ...}}
    # Also accept Grade 3/4 shape: {"parts": [{"part": n, "entries": [...]}]}
    if doc.get("parts"):
        part_iter = []
        for part in doc["parts"]:
            part_iter.append((int(part.get("part") or 0), part.get("entries") or []))
    else:
        jukugo = doc.get("jukugo") or {}
        part_iter = []
        for key in sorted(jukugo.keys(), key=lambda k: int("".join(ch for ch in k if ch.isdigit()) or 0)):
            part_num = int("".join(ch for ch in key if ch.isdigit()) or 0)
            raw_rows = []
            for row in jukugo[key]:
                if isinstance(row, (list, tuple)):
                    raw_rows.append({"kanji": row[0], "jukugo": row[1], "reading": row[2]})
                else:
                    raw_rows.append(row)
            part_iter.append((part_num, raw_rows))

    for part_num, entries in part_iter:
        for raw in entries:
            order += 1
            kanji = raw["kanji"]
            anchor = raw["jukugo"]
            reading = raw["reading"]
            exception = False
            emphasize: str | None = None
            reason: str | None = None

            if anchor in seen_anchors and seen_anchors[anchor] != kanji:
                exception = True
                emphasize = kanji
                reason = "duplicate anchor word; emphasize target kanji"
            elif kanji not in anchor:
                exception = True
                emphasize = kanji
                reason = "target kanji not present in anchor word"
            elif anchor.index(kanji) > 0:
                exception = True
                emphasize = kanji
                reason = "high-value compound; target kanji not initial"

            seen_anchors.setdefault(anchor, kanji)
            rows.append(
                _entry(
                    kanji,
                    anchor,
                    reading,
                    display_order=order,
                    part=part_num,
                    exception=exception,
                    emphasize=emphasize,
                    exception_reason=reason,
                )
            )

    return rows


GRADE_4_ANCHOR_SEED: list[dict[str, Any]] = _entries_from_jukugo_doc(_load_jukugo_doc())

ANCHOR_BY_KANJI: dict[str, dict] = {
    entry["kanji"]: entry for entry in GRADE_4_ANCHOR_SEED
}


def ordered_anchor_entries() -> list[dict[str, Any]]:
    """Anchors in displayOrder (school jukugo batches)."""
    if not GRADE_4_ANCHOR_SEED:
        raise ValueError("No Grade 5 anchor compound entries seeded.")
    return sorted(GRADE_4_ANCHOR_SEED, key=lambda e: e["displayOrder"])


def part_batches(entries: list[dict[str, Any]] | None = None) -> list[tuple[int, list[dict[str, Any]]]]:
    """Group seeded entries by their source part number."""
    rows = entries if entries is not None else ordered_anchor_entries()
    by_part: dict[int, list[dict[str, Any]]] = {}
    for entry in rows:
        by_part.setdefault(int(entry["part"]), []).append(entry)
    return sorted(by_part.items(), key=lambda item: item[0])
