#!/usr/bin/env python3
"""
PASS 4B — Layout prediction assist (non-authoritative prefill).
Predicts layout_type where blank; adds pass4b_suggest notes as scratch hints.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
V4 = BASE / "data/kanji/kanji_master_with_components.v4.csv"
V4B = BASE / "data/kanji/kanji_master_with_components.v4b.csv"
REPORT = BASE / "data/kanji/layout_prediction_report.txt"

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

VALID_LAYOUTS = frozenset({"a", "h", "v", "2l", "2r", "2t", "2b", "e", "ei"})

# Outer shell glyphs often used in enclosure layouts (conservative ei bias)
ENCLOSURE_SHELLS = frozenset(
    "口囗冂門门厂广疒辶辵凵几氵扌忄衤礻宀冖罒囗"
)

MANUAL_MARKERS = ("render_override=manual", "handcrafted_only", "manual_override")


def split_parts(raw: str) -> list[str]:
    if not raw:
        return []
    return [p.strip() for p in raw.split("|") if p.strip()]


def append_note(existing: str, addition: str) -> str:
    existing = (existing or "").strip()
    if not existing:
        return addition
    if addition in existing:
        return existing
    return f"{existing}; {addition}"


def has_manual_notes(notes: str) -> bool:
    n = (notes or "").lower()
    return any(m in n for m in MANUAL_MARKERS)


def has_pass4_harvest(notes: str) -> bool:
    return "pass4: harvested" in (notes or "")


def learn_pipe_layouts(rows: list[dict]) -> dict[str, str]:
    """Most common layout_type per exact kml_primitives pipe string (L1-22 harvest)."""
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        pp = (row.get("kml_primitives") or "").strip()
        lt = (row.get("layout_type") or "").strip()
        if not pp or not lt or lt not in VALID_LAYOUTS:
            continue
        try:
            ln = int(row.get("lesson_number") or 0)
        except ValueError:
            ln = 0
        weight = 3 if ln <= 22 else 1
        counts[pp][lt] += weight
    return {pp: c.most_common(1)[0][0] for pp, c in counts.items()}


def predict_from_parts(
    parts: list[str],
    kanji: str,
    pipe_layouts: dict[str, str],
    primitives_pipe: str,
) -> tuple[str, str]:
    """Return (layout_code, reason). Conservative bias."""
    if primitives_pipe in pipe_layouts:
        return pipe_layouts[primitives_pipe], "exact_pipe_match_L1-22"

    n = len(parts)
    if n == 0:
        return "a", "no_primitives_anchor_default"

    if n == 1:
        p = parts[0]
        if p == kanji:
            return "a", "single_stable_kanji_anchor"
        if p in ENCLOSURE_SHELLS:
            return "e", "single_shell_enclosure"
        return "a", "single_part_anchor"

    if n == 2:
        if parts[0] in ENCLOSURE_SHELLS:
            return "ei", "shell_plus_inner_two_part"
        return "h", "two_part_horizontal_family"

    if n == 3:
        if parts[0] in ENCLOSURE_SHELLS:
            return "ei", "shell_plus_inner_three_part"
        # 朋/明 style horizontal triple vs 晶 vertical stack — bias 2t (conservative chunk)
        if parts[0] == parts[1] or parts[1] == parts[2]:
            return "h", "repeated_glyph_horizontal"
        return "2t", "three_part_top_group"

    if n == 4:
        if parts[0] in ENCLOSURE_SHELLS:
            return "ei", "shell_plus_multi_inner"
        return "2r", "four_part_right_stack_bias"

    if n >= 5:
        return "2r", "multi_part_composite_bias"

    return "a", "fallback_anchor"


def main() -> None:
    with open(V4, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    pipe_layouts = learn_pipe_layouts(rows)

    stats = {
        "filled_blank": 0,
        "scratch_suggest": 0,
        "unchanged": 0,
        "skipped_manual": 0,
        "intentionally_blank": 0,
    }
    filled_log: list[str] = []
    suggest_log: list[str] = []
    ambiguous: list[str] = []
    left_blank: list[str] = []

    for row in rows:
        kanji = (row.get("kanji") or "").strip()
        notes = (row.get("notes") or "").strip()
        old_lt = (row.get("layout_type") or "").strip()
        prim_raw = (row.get("kml_primitives") or "").strip()
        parts = split_parts(prim_raw)

        if has_manual_notes(notes):
            stats["skipped_manual"] += 1
            continue

        pred, reason = predict_from_parts(parts, kanji, pipe_layouts, prim_raw)

        if not pred or pred not in VALID_LAYOUTS:
            stats["intentionally_blank"] += 1
            left_blank.append(f"{kanji}\tno_valid_prediction\t{reason}")
            continue

        # Low confidence flag for heuristic (not exact pipe match)
        conf = "high" if reason.startswith("exact_pipe") else "low"
        tag = f"pass4b_predict:{pred} ({reason}, conf={conf})"

        if not old_lt:
            row["layout_type"] = pred
            row["notes"] = append_note(notes, tag)
            stats["filled_blank"] += 1
            filled_log.append(f"  {kanji}\t-> {pred}\t{reason}\tprim={prim_raw or '—'}")
            continue

        # Scratch suggestion when layout exists but not from HTML harvest (L>22 editing aid)
        try:
            ln = int(row.get("lesson_number") or 0)
        except ValueError:
            ln = 0

        if has_pass4_harvest(notes):
            stats["unchanged"] += 1
            continue

        if old_lt == pred:
            stats["unchanged"] += 1
            continue

        # Suggest only — do not overwrite authoritative/pass2a values
        suggest = f"pass4b_suggest:{pred} (was {old_lt}; {reason})"
        row["notes"] = append_note(notes, suggest)
        stats["scratch_suggest"] += 1
        suggest_log.append(f"  {kanji}\tL{ln}\t{old_lt} -> suggest {pred}\t{reason}")

        if reason in (
            "four_part_right_stack_bias",
            "three_part_top_group",
            "multi_part_composite_bias",
        ):
            ambiguous.append(
                f"  {kanji}\t{old_lt} vs suggest {pred}\t{prim_raw or '—'}\t({reason})"
            )

    with open(V4B, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

    lines = [
        "PASS 4B — LAYOUT PREDICTION ASSIST REPORT",
        "=" * 60,
        "",
        "Non-authoritative prefill. Human editor may erase or override.",
        f"Source: {V4.name}",
        f"Output: {V4B.name}",
        "",
        "Philosophy: conservative bias (anchors, simple layouts); false positives OK.",
        "",
        "## SUMMARY",
        "",
        f"  layout_type filled (was blank):     {stats['filled_blank']}",
        f"  pass4b_suggest notes (scratch):     {stats['scratch_suggest']}",
        f"  unchanged:                          {stats['unchanged']}",
        f"  skipped (manual override):          {stats['skipped_manual']}",
        f"  intentionally left blank:           {stats['intentionally_blank']}",
        "",
        f"  learned pipe patterns (L1-22):      {len(pipe_layouts)}",
        "",
        "## ROWS UPDATED (blank -> predicted)",
        "",
    ]
    lines.extend(filled_log[:120])
    if len(filled_log) > 120:
        lines.append(f"  ... +{len(filled_log) - 120} more")

    lines += ["", "## SCRATCH SUGGESTIONS (layout kept; note only)", ""]
    lines.extend(suggest_log[:80])
    if len(suggest_log) > 80:
        lines.append(f"  ... +{len(suggest_log) - 80} more")

    lines += ["", "## AMBIGUOUS / REVIEW", ""]
    if ambiguous:
        lines.extend(ambiguous[:40])
    else:
        lines.append("  (none flagged)")

    lines += ["", "## INTENTIONALLY LEFT BLANK", ""]
    if left_blank:
        lines.extend(left_blank)
    else:
        lines.append("  (none)")

    lines += [
        "",
        "## EXAMPLES (editor reference)",
        "",
        "  市 → suggest a (stable anchor; was v in source)",
        "  柿 → h (unchanged if already h)",
        "  姉 → h (unchanged if already h)",
        "",
        "## HEURISTIC DEFAULTS",
        "",
        "  no primitives     -> a",
        "  1 part            -> a",
        "  2 parts           -> h (or ei if shell+inner)",
        "  3 parts           -> 2t (or h if repeated glyphs)",
        "  4+ parts          -> 2r",
        "",
    ]

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("PASS 4B complete.")
    print(f"  filled blank: {stats['filled_blank']}")
    print(f"  scratch suggest: {stats['scratch_suggest']}")
    print(f"  {V4B}")
    print(f"  {REPORT}")


if __name__ == "__main__":
    main()
