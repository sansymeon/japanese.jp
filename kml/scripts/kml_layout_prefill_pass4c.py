#!/usr/bin/env python3
"""
PASS 4C — Active layout_type prefill for CSV editing acceleration.
Overwrites layout_type on non-authoritative rows; protects harvested/manual rows.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))

from kml_layout_predict_pass4b import (  # noqa: E402
    FIELDNAMES,
    VALID_LAYOUTS,
    append_note,
    has_manual_notes,
    has_pass4_harvest,
    learn_pipe_layouts,
    predict_from_parts,
    split_parts,
)

V4B = BASE / "data/kanji/kanji_master_with_components.v4b.csv"
V4C = BASE / "data/kanji/kanji_master_with_components.v4c.csv"
REPORT = BASE / "data/kanji/layout_prefill_active_report.txt"

# Heuristic reasons where we simplify to h (conservative) unless exact pipe match
SIMPLIFY_TO_H = frozenset(
    {
        "three_part_top_group",
        "four_part_right_stack_bias",
        "multi_part_composite_bias",
        "shell_plus_inner_three_part",
        "shell_plus_multi_inner",
    }
)


def is_authoritative(notes: str) -> bool:
    return has_pass4_harvest(notes) or has_manual_notes(notes)


def strip_pass4b_notes(notes: str) -> str:
    """Remove pass4b_suggest / pass4b_predict tags superseded by active prefill."""
    if not notes:
        return ""
    parts = [
        p.strip()
        for p in notes.split(";")
        if p.strip()
        and not p.strip().startswith("pass4b_suggest:")
        and not p.strip().startswith("pass4b_predict:")
    ]
    return "; ".join(parts)


def conservative_prediction(
    parts: list[str],
    kanji: str,
    pipe_layouts: dict[str, str],
    primitives_pipe: str,
) -> tuple[str, str]:
    pred, reason = predict_from_parts(parts, kanji, pipe_layouts, primitives_pipe)
    if reason.startswith("exact_pipe_match"):
        return pred, reason
    if pred in SIMPLIFY_TO_H or pred in ("2l", "2r", "2t", "2b"):
        return "h", f"{reason}_pass4c_simplified_h"
    if pred in ("e", "ei") and len(parts) <= 2:
        return "h", f"{reason}_pass4c_simplified_h"
    return pred, reason


def main() -> None:
    with open(V4B, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    pipe_layouts = learn_pipe_layouts(rows)

    stats = {
        "protected": 0,
        "prefilled": 0,
        "unchanged_match": 0,
        "blank_to_prefill": 0,
        "overwrite": 0,
    }
    prefill_log: list[str] = []
    protected_log: list[str] = []
    examples: list[str] = []

    for row in rows:
        kanji = (row.get("kanji") or "").strip()
        notes = (row.get("notes") or "").strip()
        old_lt = (row.get("layout_type") or "").strip()
        prim_raw = (row.get("kml_primitives") or "").strip()
        parts = split_parts(prim_raw)

        if is_authoritative(notes):
            stats["protected"] += 1
            if len(protected_log) < 15:
                protected_log.append(f"  {kanji}\tkept {old_lt}\t{notes[:60]}")
            continue

        pred, reason = conservative_prediction(
            parts, kanji, pipe_layouts, prim_raw
        )

        if pred not in VALID_LAYOUTS:
            continue

        if old_lt == pred:
            stats["unchanged_match"] += 1
            continue

        was_blank = not old_lt
        row["layout_type"] = pred
        notes = strip_pass4b_notes(notes)
        trace = f"pass4c:auto_prefill:{pred}"
        if not was_blank:
            trace += f" (was {old_lt})"
        row["notes"] = append_note(notes, trace)

        stats["prefilled"] += 1
        if was_blank:
            stats["blank_to_prefill"] += 1
        else:
            stats["overwrite"] += 1

        if kanji in ("市", "柿", "姉") or len(prefill_log) < 120:
            prefill_log.append(
                f"  {kanji}\t{old_lt or '—'} -> {pred}\t{reason}\tprim={prim_raw or '—'}"
            )
        if kanji == "市":
            examples.append(f"  市: {old_lt or '—'} -> {pred} (active prefill)")

    with open(V4C, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

    lines = [
        "PASS 4C — ACTIVE LAYOUT PREFILL REPORT",
        "=" * 60,
        "",
        "Active overwrite of layout_type on non-authoritative rows.",
        f"Source: {V4B.name}",
        f"Output: {V4C.name}",
        "",
        "## PROTECTED (not modified)",
        "",
        "  pass4: harvested",
        "  render_override=manual",
        "",
    ]
    lines.extend(protected_log)
    lines.append(f"  ... total protected: {stats['protected']}")

    lines += [
        "",
        "## SUMMARY",
        "",
        f"  layout_type actively prefilled:  {stats['prefilled']}",
        f"    from blank:                    {stats['blank_to_prefill']}",
        f"    overwrote existing:            {stats['overwrite']}",
        f"  already matched prediction:      {stats['unchanged_match']}",
        f"  protected (authoritative):       {stats['protected']}",
        "",
        "## CONFIRMED EXAMPLES",
        "",
    ]
    lines.extend(examples or ["  (see prefill log)"])

    lines += ["", "## PREFILL LOG (sample)", ""]
    lines.extend(prefill_log[:100])
    if len(prefill_log) > 100:
        lines.append(f"  ... +{len(prefill_log) - 100} more in full run")

    lines += [
        "",
        "## CONSERVATIVE SIMPLIFICATION",
        "",
        "  Low-confidence 2l/2r/2t/2b/ei heuristics -> h (unless exact_pipe_match)",
        "  No primitives -> a",
        "",
        "## NOTES TRACE",
        "",
        "  pass4c:auto_prefill:<code>",
        "  pass4c:auto_prefill:<code> (was <old>)",
        "",
    ]

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("PASS 4C complete.")
    print(f"  prefilled: {stats['prefilled']} (overwrite {stats['overwrite']})")
    print(f"  protected: {stats['protected']}")
    print(f"  {V4C}")
    print(f"  {REPORT}")


if __name__ == "__main__":
    main()
