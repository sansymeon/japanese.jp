#!/usr/bin/env python3
"""Write selection JSON from _selection_l123_153.py. Lessons 123–153 only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SELECTION = HERE / "selection"
sys.path.insert(0, str(HERE))
from _selection_l123_153 import LESSONS as ALL_LESSONS


def dump(lessons: dict) -> None:
    data = ALL_LESSONS
    for n, chars in data.items():
        if n not in lessons:
            continue
        out_chars = []
        for kanji, readings, keyword, compounds in chars:
            rec = {
                "kanji": kanji,
                "readings": readings,
                "keyword": keyword,
                "compounds": [],
            }
            for item in compounds:
                surface, reading, meaning, *rest = item
                row = {
                    "surface": surface,
                    "reading": reading,
                    "meaning": meaning,
                    "provenance": list(rest[0]) if rest else ["curated"],
                }
                rec["compounds"].append(row)
            if len(rec["compounds"]) < 5:
                rec["fewerThanFive"] = (
                    "Fewer than five useful ordinary words. Padding would be dictionary excavation."
                )
            out_chars.append(rec)
        payload = {
            "schema": "kml.compounds.selection.v1",
            "lesson": n,
            "status": "vocabulary-selection",
            "note": "Authoritative word list for this lesson. No example sentences.",
            "characters": out_chars,
        }
        (SELECTION / f"lesson_{n:02d}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"selection {n:02d}  kanji {len(out_chars)}  words {sum(len(c['compounds']) for c in out_chars)}")


if __name__ == "__main__":
    dump(set(range(123, 154)))
