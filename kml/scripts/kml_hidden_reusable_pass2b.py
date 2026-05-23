#!/usr/bin/env python3
"""PASS 2B — Insert hidden reusable kanji placeholders into v3 -> v3b."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
V3 = BASE / "data/kanji/kanji_master_with_components.v3.csv"
V3B = BASE / "data/kanji/kanji_master_with_components.v3b.csv"
REPORT = BASE / "data/kanji/hidden_reusable_insert_report.txt"

FIELDNAMES = [
    "kanji",
    "keyword",
    "lesson_number",
    "kml_primitives",
    "cluster_components",
    "collapse_to",
    "layout_type",
    "first_use",
    "notes",
]

INSERTIONS = [
    {
        "kanji": "戈",
        "keyword": "halberd",
        "lesson_number": "19",
        "kml_primitives": "戈",
        "cluster_components": "",
        "collapse_to": "",
        "layout_type": "a",
        "first_use": "式",
        "notes": (
            "status=hidden_reusable; pass2b placeholder; "
            "weapon-family anchor; readings/verses TBD"
        ),
    },
    {
        "kanji": "俞",
        "keyword": "yu",
        "lesson_number": "16",
        "kml_primitives": "俞",
        "cluster_components": "",
        "collapse_to": "",
        "layout_type": "a",
        "first_use": "輸",
        "notes": (
            "status=hidden_reusable; pass2b placeholder; "
            "meeting-family anchor; readings/verses TBD"
        ),
    },
    {
        "kanji": "袁",
        "keyword": "robe_family",
        "lesson_number": "22",
        "kml_primitives": "袁",
        "cluster_components": "",
        "collapse_to": "",
        "layout_type": "a",
        "first_use": "遠",
        "notes": (
            "status=hidden_reusable; pass2b placeholder; "
            "robe-family anchor; readings/verses TBD"
        ),
    },
]


def main() -> None:
    with open(V3, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    existing_kanji = [r.get("kanji", "").strip() for r in rows]
    counts = Counter(existing_kanji)

    report: list[str] = [
        "PASS 2B — HIDDEN REUSABLE KANJI INSERT REPORT",
        "=" * 60,
        "",
        f"Source: {V3.name}",
        f"Output: {V3B.name}",
        f"Rows before insert: {len(rows)}",
        "",
        "## DUPLICATE CHECK (before insert)",
        "",
    ]

    duplicates_before = [k for k, c in counts.items() if c > 1 and k]
    if duplicates_before:
        report.append(f"  WARNING: {len(duplicates_before)} duplicate kanji in v3:")
        for k in duplicates_before[:20]:
            report.append(f"    {k!r} x{counts[k]}")
    else:
        report.append("  No duplicate kanji rows in v3.")

    report += ["", "## INSERTIONS", ""]
    inserted = []
    skipped = []

    for entry in INSERTIONS:
        k = entry["kanji"]
        if k in counts:
            skipped.append((k, f"already present x{counts[k]}"))
            report.append(f"  SKIP {k}: already in file")
            continue
        rows.append(entry)
        counts[k] = 1
        inserted.append(k)
        report.append(f"  ADD {k}")
        report.append(f"    keyword: {entry['keyword']}")
        report.append(f"    lesson_number: {entry['lesson_number']}")
        report.append(f"    layout_type: {entry['layout_type']}")
        report.append(f"    first_use: {entry['first_use']}")
        report.append(f"    kml_primitives: {entry['kml_primitives']}")
        report.append(f"    notes: {entry['notes']}")
        report.append("")

    with open(V3B, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

    final_counts = Counter(r.get("kanji", "").strip() for r in rows)
    duplicates_after = [k for k, c in final_counts.items() if c > 1 and k]

    new_dupes = [k for k in duplicates_after if k not in duplicates_before]

    report += [
        "## DUPLICATE CHECK (after insert)",
        "",
    ]
    if new_dupes:
        report.append(f"  FAIL: new duplicates from pass2b: {new_dupes}")
    else:
        report.append("  OK: 戈, 俞, 袁 — no duplicate rows for inserted kanji.")

    if duplicates_after:
        report.append(
            f"  Pre-existing duplicates in v3 (unchanged by pass2b): "
            f"{len(duplicates_after)} kanji"
        )
        for k in duplicates_after:
            report.append(f"    {k!r} x{final_counts[k]}")
    elif not duplicates_after:
        report.append("  OK: no duplicate kanji rows in file.")

    report += [
        "",
        f"Rows after insert: {len(rows)}",
        f"Inserted: {len(inserted)} ({', '.join(inserted) if inserted else 'none'})",
        f"Skipped: {len(skipped)}",
        "",
        "## LESSONS NOT REGENERATED",
        "",
        "  HTML lesson files unchanged (pass2b).",
    ]

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"v3b written: {V3B} ({len(rows)} rows)")
    print(f"inserted: {inserted}")
    print(f"duplicates after: {duplicates_after or 'none'}")


if __name__ == "__main__":
    main()
