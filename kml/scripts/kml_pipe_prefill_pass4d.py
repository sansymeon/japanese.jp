#!/usr/bin/env python3
"""
PASS 4D — Pipe placeholder prefill (|||) for faster manual CSV editing.
No layout prediction, no decomposition, no notes changes.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
V4B = BASE / "data/kanji/kanji_master_with_components.v4b.csv"
V4C = BASE / "data/kanji/kanji_master_with_components.v4c.csv"
REPORT = BASE / "data/kanji/pipe_prefill_report.txt"

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

PIPE_PLACEHOLDER = "|||"

MANUAL_MARKERS = ("render_override=manual", "handcrafted_only", "manual_override")


def is_authoritative(notes: str) -> bool:
    n = (notes or "").lower()
    if "pass4: harvested" in n:
        return True
    return any(m in n for m in MANUAL_MARKERS)


def needs_pipe_placeholder(raw: str) -> bool:
    """Blank or pipe-only placeholder (no meaningful component glyphs)."""
    s = (raw or "").strip()
    if not s:
        return True
    # Only pipes / whitespace — incomplete placeholder
    if re.fullmatch(r"\|+", s):
        return True
    return False


def has_meaningful_primitives(raw: str) -> bool:
    return not needs_pipe_placeholder(raw)


def main() -> None:
    with open(V4B, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    stats = {
        "prefilled": 0,
        "protected": 0,
        "already_meaningful": 0,
        "already_placeholder": 0,
    }
    log: list[str] = []
    protected_samples: list[str] = []

    for row in rows:
        kanji = (row.get("kanji") or "").strip()
        notes = (row.get("notes") or "").strip()
        prim = (row.get("kml_primitives") or "").strip()

        if is_authoritative(notes):
            stats["protected"] += 1
            if len(protected_samples) < 10:
                protected_samples.append(f"  {kanji}\tprimitives={prim or '(blank)'}")
            continue

        if has_meaningful_primitives(prim):
            stats["already_meaningful"] += 1
            continue

        if prim == PIPE_PLACEHOLDER:
            stats["already_placeholder"] += 1
            continue

        row["kml_primitives"] = PIPE_PLACEHOLDER
        stats["prefilled"] += 1
        if len(log) < 80 or kanji in ("肺", "帯", "市"):
            log.append(
                f"  {kanji}\tL{row.get('lesson_number', '')}\t"
                f"{prim or '(blank)'} -> {PIPE_PLACEHOLDER}"
            )

    with open(V4C, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

    lines = [
        "PASS 4D — PIPE PREFILL ASSIST REPORT",
        "=" * 60,
        "",
        "Keyboard assist only: kml_primitives <- ||| for empty/placeholder cells.",
        f"Source: {V4B.name}",
        f"Output: {V4C.name}",
        "",
        "NOT modified: layout_type, notes, cluster_components, harvested structures.",
        "",
        "## SUMMARY",
        "",
        f"  prefilled with |||:           {stats['prefilled']}",
        f"  protected (skipped):         {stats['protected']}",
        f"  already meaningful:          {stats['already_meaningful']}",
        f"  already |||:                  {stats['already_placeholder']}",
        "",
        "## PROTECTED ROWS (sample)",
        "",
        "  pass4: harvested",
        "  render_override=manual",
        "",
    ]
    lines.extend(protected_samples)
    lines.append(f"  ... total protected: {stats['protected']}")

    lines += ["", "## PREFILL LOG (sample)", ""]
    lines.extend(log)
    if stats["prefilled"] > len(log):
        lines.append(f"  ... +{stats['prefilled'] - len(log)} more")

    lines += [
        "",
        "## EXAMPLES",
        "",
        "  肺,lungs,23,|||,,,,,",
        "  帯,sash,23,|||,,,,,",
        "",
        "## NOTE ON v4c",
        "",
        "  This file is rebuilt from v4b with pipe prefill only.",
        "  If you previously ran PASS 4C (layout prefill), re-run 4C after 4D",
        "  or merge layout_type/notes from the earlier v4c backup.",
        "",
    ]

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("PASS 4D complete.")
    print(f"  prefilled: {stats['prefilled']}")
    print(f"  protected: {stats['protected']}")
    print(f"  {V4C}")
    print(f"  {REPORT}")


if __name__ == "__main__":
    main()
