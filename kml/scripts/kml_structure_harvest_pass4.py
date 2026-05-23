#!/usr/bin/env python3
"""
PASS 4 — Harvest handcrafted component structures from lessons 1–22 HTML.
Backfill v3b -> v4. Does not regenerate lessons or invent decomposition.
"""

from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LESSONS_DIR = BASE / "contents/books/book_01/lessons"
V3B = BASE / "data/kanji/kanji_master_with_components.v3b.csv"
V4 = BASE / "data/kanji/kanji_master_with_components.v4.csv"
HARVEST_REPORT = BASE / "data/kanji/structural_harvest_report.txt"
INCOMPLETE_OUT = BASE / "data/kanji/remaining_incomplete_structures.txt"

LESSON_RANGE = range(1, 23)

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

MANUAL_MARKERS = (
    "render_override=manual",
    "handcrafted_only",
    "manual_override",
)

# Document-order extraction (single pass, left-to-right)
ORDERED_PART_RE = re.compile(
    r'<span\s+class="kanji-part(?:\s+enclosure-part)?"[^>]*>\s*([^<]+?)\s*</span>|'
    r'<div\s+class="outer-kanji"[^>]*>\s*([^<]+?)\s*</div>|'
    r'<div\s+class="inner-kanji"[^>]*>\s*([^<]+?)\s*</div>|'
    r'<div\s+class="enclosure-inner"[^>]*>\s*'
    r'<span\s+class="kanji-part"[^>]*>\s*([^<]+?)\s*</span>',
    re.DOTALL,
)

KANJI_PART_RE = re.compile(
    r'<span\s+class="kanji-part[^"]*">([^<]+)</span>'
)


def extract_component_box(section: str) -> str:
    m = re.search(
        r'<div\s+class="component-box"[^>]*>(.*)',
        section,
        re.DOTALL,
    )
    if not m:
        return ""
    chunk = m.group(0)
    end = chunk.find("</section>")
    if end != -1:
        chunk = chunk[:end]
    return chunk.strip()


def extract_parts_ordered(box: str) -> list[str]:
    """Authoritative render order from handcrafted HTML."""
    if not box:
        return []
    parts: list[str] = []
    seen_at: set[tuple[int, str]] = set()
    for m in ORDERED_PART_RE.finditer(box):
        sym = next((g.strip() for g in m.groups() if g and g.strip()), "")
        if not sym:
            continue
        key = (m.start(), sym)
        if key in seen_at:
            continue
        seen_at.add(key)
        parts.append(sym)
    return parts


def _side_block(box: str, side: str) -> str:
    pat = (
        rf'<div\s+class="(?:kanji|component)-{side}([^"]*)"[^>]*>(.*?)</div>\s*'
        rf'(?:<div\s+class="(?:kanji|component)-(?:left|right)|</div>)'
    )
    m = re.search(pat, box, re.DOTALL)
    return m.group(2) if m else ""


def infer_composite_layout(box: str) -> str:
    left = _side_block(box, "left")
    right = _side_block(box, "right")
    if not left and not right:
        parts = extract_parts_ordered(box)
        return "h" if len(parts) >= 2 else "a"

    def side_info(block: str) -> tuple[bool, int]:
        if not block:
            return False, 0
        vertical = "stack-vertical" in block
        count = len(KANJI_PART_RE.findall(block))
        return vertical or count > 1, count

    lv, lc = side_info(left)
    rv, rc = side_info(right)
    if not lv and rv:
        return "2r"
    if lv and not rv:
        return "2l"
    if lv and rv:
        return "2l" if lc >= rc else "2r"
    return "h"


def infer_vertical_layout(box: str) -> str:
    if "stack-horizontal" not in box and "component-bottom" not in box:
        return "v"
    if "component-top" in box and (
        "component-bottom" in box or "stack-horizontal" in box
    ):
        return "2t"
    if "component-bottom" in box and "component-top" not in box:
        return "2b"
    h_pos = box.find("stack-horizontal")
    first_part = box.find("kanji-part")
    if h_pos == -1 or first_part == -1:
        return "v"
    return "2b" if first_part < h_pos else "2t"


def infer_layout_from_box(box: str) -> str:
    if not box:
        return ""
    m = re.search(r'class="component-layout\s+([^"]+)"', box)
    if not m:
        return ""
    outer = m.group(1).strip().split()[0]

    if outer == "anchor-box":
        return "a"
    if outer in ("stack-horizontal", "composite-horizontal"):
        return "h"
    if outer == "enclosure-layout":
        if "enclosure-inner" in box or "inner-kanji" in box:
            return "ei"
        return "e"
    if outer in ("kanji-composite", "component-horizontal", "component-composite"):
        return infer_composite_layout(box)
    if outer in ("stack-vertical", "composite-vertical"):
        return infer_vertical_layout(box)
    return ""


def detect_manual_override(box: str) -> list[str]:
    reasons: list[str] = []
    if not box:
        return reasons
    layouts = re.findall(r'class="component-layout\s+([^"]+)"', box)
    if len(layouts) > 1:
        reasons.append("nested_component_layout")
    outer = layouts[0].split() if layouts else []
    if "component-composite" in outer:
        reasons.append("legacy_component_composite_outer")
    if layouts and not infer_layout_from_box(box):
        reasons.append("unmapped_layout_template")
    return reasons


def harvest_lesson(path: Path, lesson_num: int) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8")
    out: dict[str, dict] = {}
    for block in re.split(r'<section\s+class="kanji-entry"', text)[1:]:
        km = re.search(r'data-kanji="([^"]*)"', block)
        if not km:
            continue
        kanji = km.group(1).strip()
        box = extract_component_box(block)
        parts = extract_parts_ordered(box)
        outer_m = re.search(r'class="component-layout\s+([^"]+)"', box)
        outer = outer_m.group(1).strip() if outer_m else ""
        layout = infer_layout_from_box(box)
        manual = detect_manual_override(box)
        out[kanji] = {
            "lesson": lesson_num,
            "parts": parts,
            "layout": layout,
            "outer": outer,
            "has_box": bool(box),
            "manual_reasons": manual,
            "primitives_pipe": "|".join(parts),
        }
    return out


def has_manual_notes(notes: str) -> bool:
    n = (notes or "").lower()
    return any(m in n for m in MANUAL_MARKERS)


def append_note(existing: str, addition: str) -> str:
    existing = (existing or "").strip()
    if not existing:
        return addition
    if addition in existing:
        return existing
    return f"{existing}; {addition}"


def harvest_all_lessons() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for n in LESSON_RANGE:
        path = LESSONS_DIR / f"lesson_{n:02d}.html"
        if not path.exists():
            continue
        for kanji, info in harvest_lesson(path, n).items():
            merged[kanji] = info
    return merged


def main() -> None:
    html = harvest_all_lessons()

    with open(V3B, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    stats = {
        "harvested_primitives": 0,
        "primitives_unchanged": 0,
        "primitives_conflict_kept": 0,
        "layout_updated": 0,
        "manual_flagged": 0,
        "skipped_manual": 0,
        "no_box": 0,
    }
    harvest_log: list[str] = []
    layout_conflicts: list[str] = []

    for row in rows:
        kanji = (row.get("kanji") or "").strip()
        if not kanji:
            continue

        try:
            ln = int(row.get("lesson_number") or 0)
        except ValueError:
            ln = 0

        if ln > 22 and kanji not in html:
            continue

        h = html.get(kanji)
        if not h:
            continue

        notes = (row.get("notes") or "").strip()

        if h["manual_reasons"] and not has_manual_notes(notes):
            notes = append_note(notes, "render_override=manual")
            notes = append_note(
                notes, f"pass4: non-template ({','.join(h['manual_reasons'])})"
            )
            row["notes"] = notes
            stats["manual_flagged"] += 1

        if has_manual_notes(notes):
            stats["skipped_manual"] += 1
            continue

        if not h["has_box"]:
            stats["no_box"] += 1
            continue

        if not h["parts"]:
            stats["no_box"] += 1
            continue

        old_prim = (row.get("kml_primitives") or "").strip()
        new_prim = h["primitives_pipe"]
        old_layout = (row.get("layout_type") or "").strip()
        html_layout = h["layout"]

        if old_prim and old_prim != new_prim:
            # HTML wins for L1-22; log conflict
            harvest_log.append(
                f"  {kanji}: primitives {old_prim!r} -> {new_prim!r} (HTML order)"
            )
        elif not old_prim:
            harvest_log.append(f"  {kanji}: filled {new_prim!r}")

        if new_prim:
            row["kml_primitives"] = new_prim
            row["cluster_components"] = new_prim
            if old_prim == new_prim:
                stats["primitives_unchanged"] += 1
            else:
                stats["harvested_primitives"] += 1
            row["notes"] = append_note(
                row.get("notes", ""),
                f"pass4: harvested L{h['lesson']:02d} HTML ({new_prim})",
            )

        if html_layout and html_layout != old_layout:
            layout_conflicts.append(
                f"  {kanji}: layout {old_layout or '—'} -> {html_layout} "
                f"(outer={h['outer']})"
            )
            row["layout_type"] = html_layout
            row["notes"] = append_note(
                row.get("notes", ""),
                f"pass4: layout {old_layout or '—'} -> {html_layout}",
            )
            stats["layout_updated"] += 1

    with open(V4, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

    # Remaining incomplete (L1-22 focus)
    incomplete: list[str] = []
    for row in rows:
        try:
            ln = int(row.get("lesson_number") or 0)
        except ValueError:
            ln = 0
        if ln > 22:
            continue
        lt = (row.get("layout_type") or "").strip()
        prim = (row.get("kml_primitives") or "").strip()
        if lt and not prim and not has_manual_notes(row.get("notes") or ""):
            incomplete.append(
                f"{row.get('kanji')}\tL{ln}\tlayout={lt}\tkeyword={row.get('keyword','')}"
            )

    incomplete_lines = [
        "REMAINING INCOMPLETE STRUCTURES (lessons 1–22)",
        "=" * 60,
        "layout_type set but kml_primitives blank after PASS 4 harvest.",
        "May need manual authoring, hidden anchor only, or intentional omission.",
        "",
    ]
    if incomplete:
        incomplete_lines.extend(incomplete)
    else:
        incomplete_lines.append("(none)")
    incomplete_lines.append("")
    incomplete_lines.append(f"Total: {len(incomplete)}")
    INCOMPLETE_OUT.write_text("\n".join(incomplete_lines) + "\n", encoding="utf-8")

    report = [
        "PASS 4 — STRUCTURAL HARVEST REPORT",
        "=" * 60,
        "",
        "Philosophy: handcrafted HTML is authoritative; no IDS/radical inference.",
        f"Source: {V3B.name}",
        f"Output: {V4.name}",
        "",
        f"HTML entries harvested (lessons 1–22): {len(html)}",
        f"  with component-box + parts: {sum(1 for x in html.values() if x['parts'])}",
        "",
        "## BACKFILL STATS",
        "",
        f"  primitives newly filled/updated: {stats['harvested_primitives']}",
        f"  primitives unchanged (matched):  {stats['primitives_unchanged']}",
        f"  layout_type updated (HTML≠CSV):  {stats['layout_updated']}",
        f"  render_override=manual flagged:  {stats['manual_flagged']}",
        f"  skipped (already manual):        {stats['skipped_manual']}",
        f"  no box / no parts in HTML:       {stats['no_box']}",
        "",
        "## CONFIRMED FAMILY EXAMPLES",
        "",
    ]
    for k in ("裁", "壊", "遠", "錦", "布", "幌", "婿"):
        info = html.get(k, {})
        row = next((r for r in rows if (r.get("kanji") or "").strip() == k), None)
        prim = (row or {}).get("kml_primitives", "") if row else ""
        report.append(
            f"  {k}: HTML={'|'.join(info.get('parts', []))} "
            f"CSV={prim} layout={(row or {}).get('layout_type','')}"
        )

    report += ["", "## PRIMITIVE UPDATES (sample)", ""]
    report += harvest_log[:80]
    if len(harvest_log) > 80:
        report.append(f"  ... +{len(harvest_log) - 80} more")

    if layout_conflicts:
        report += ["", "## LAYOUT CHANGES (HTML differed from PASS 2A)", ""]
        report.extend(layout_conflicts[:40])

    report += [
        "",
        f"Remaining incomplete (L1-22): {len(incomplete)}",
        f"See: {INCOMPLETE_OUT.name}",
        "",
    ]

    HARVEST_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    # Re-run render proof against v4
    proof_script = BASE / "scripts" / "kml_render_proof.py"
    proof_result = ""
    if proof_script.exists():
        env = {**__import__("os").environ, "KML_MASTER_CSV": str(V4)}
        r = subprocess.run(
            [sys.executable, str(proof_script)],
            cwd=str(BASE),
            env=env,
            capture_output=True,
            text=True,
        )
        proof_result = r.stdout + r.stderr
        report += ["", "## POST-HARVEST RENDER PROOF", "", proof_result.strip() or "(no output)"]

    HARVEST_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("PASS 4 harvest complete.")
    print(f"  primitives updated: {stats['harvested_primitives']}")
    print(f"  remaining incomplete L1-22: {len(incomplete)}")
    print(f"  {V4}")
    print(f"  {HARVEST_REPORT}")


if __name__ == "__main__":
    main()
