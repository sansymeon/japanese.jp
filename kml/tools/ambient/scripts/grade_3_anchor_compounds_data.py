"""Grade 3 anchor compound seed data — school edition.

Source: collections/grade_3/grade_3_jukugo_list.json (10 parts × 20 kanji).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JUKUGO_LIST = ROOT / "collections" / "grade_3" / "grade_3_jukugo_list.json"


def _entry(
    kanji: str,
    anchor: str,
    reading: str,
    *,
    display_order: int,
    exception: bool = False,
    emphasize: str | None = None,
    exception_reason: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "kanji": kanji,
        "anchor": anchor,
        "reading": reading,
        "grade": 3,
        "lesson": None,
        "part": None,
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
        raise FileNotFoundError(f"Missing Grade 3 jukugo list: {JUKUGO_LIST}")
    return json.loads(JUKUGO_LIST.read_text(encoding="utf-8"))


def _entries_from_jukugo_doc(doc: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen_anchors: dict[str, str] = {}
    order = 0

    for part in doc.get("parts") or []:
        for raw in part.get("entries") or []:
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
                    exception=exception,
                    emphasize=emphasize,
                    exception_reason=reason,
                )
            )

    return rows


GRADE_3_ANCHOR_SEED: list[dict[str, Any]] = _entries_from_jukugo_doc(_load_jukugo_doc())

ANCHOR_BY_KANJI: dict[str, dict] = {
    entry["kanji"]: entry for entry in GRADE_3_ANCHOR_SEED
}


def ordered_anchor_entries() -> list[dict[str, Any]]:
    """Anchors in displayOrder (school jukugo batches)."""
    if not GRADE_3_ANCHOR_SEED:
        raise ValueError("No Grade 3 anchor compound entries seeded.")
    return sorted(GRADE_3_ANCHOR_SEED, key=lambda e: e["displayOrder"])
