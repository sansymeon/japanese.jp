#!/usr/bin/env python3
"""Write selection JSON from _selection_l101_122.py. Lessons 101–122 only."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SELECTION = HERE / "selection"


def dump(lessons: dict) -> None:
    ns: dict = {}
    exec((HERE / "_selection_l101_122.py").read_text(encoding="utf-8"), ns)
    data = ns["LESSONS"]
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
            "note": "Authoritative word list for this lesson. No example sentences. The learner page is unchanged.",
            "characters": out_chars,
        }
        path = SELECTION / f"lesson_{n:02d}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", path.name, "kanji", len(out_chars), "words", sum(len(c["compounds"]) for c in out_chars))


if __name__ == "__main__":
    import sys

    ns: dict = {}
    exec((HERE / "_selection_l101_122.py").read_text(encoding="utf-8"), ns)
    wanted = {int(x) for x in sys.argv[1:]} if len(sys.argv) > 1 else set(ns["LESSONS"])
    dump(wanted)
