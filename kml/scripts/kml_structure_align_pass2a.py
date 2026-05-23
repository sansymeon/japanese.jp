#!/usr/bin/env python3
"""
PASS 2A — Align structural CSV to rendered HTML (lessons 1–22).
HTML wins for layout_type. Safe legacy class renames in lesson HTML only.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LESSONS_DIR = BASE / "contents/books/book_01/lessons"
V2_PATH = BASE / "data/kanji/kanji_master_with_components.v2.csv"
MASTER_PATH = BASE / "data/kanji/kanji_master_with_components.csv"
OUT_DIR = BASE / "data/kanji"

LESSON_RANGE = range(1, 23)
HIDDEN_CANDIDATES = ("戈", "俞", "袁")

HTML_RENAMES = (
    ("component-left", "kanji-left"),
    ("component-right", "kanji-right"),
    ("component-composite", "kanji-composite"),
)

KANJI_PART_RE = re.compile(
    r"<span\s+class=\"kanji-part[^\"]*\">([^<]+)</span>"
)


def extract_component_box(section: str) -> str:
    m = re.search(
        r'<div\s+class="component-box">(.*?)</div>\s*(?:</div>\s*)?(?:</section>|$)',
        section,
        re.DOTALL,
    )
    return m.group(0) if m else ""


def extract_parts_ordered(box: str) -> list[str]:
    parts = []
    for m in KANJI_PART_RE.finditer(box):
        sym = m.group(1).strip()
        if sym:
            parts.append(sym)
    for m in re.finditer(r'class="(?:outer-kanji|enclosure-part)">\s*([^<]+)', box):
        sym = m.group(1).strip()
        if sym:
            parts.append(sym)
    for m in re.finditer(r'class="inner-kanji">\s*([^<]+)', box):
        sym = m.group(1).strip()
        if sym:
            parts.append(sym)
    for m in re.finditer(
        r'<div\s+class="enclosure-inner"[^>]*>\s*<span[^>]*>([^<]+)</span>',
        box,
    ):
        sym = m.group(1).strip()
        if sym:
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
    # component-top / component-bottom (legacy)
    if "component-top" in box and (
        "component-bottom" in box or "stack-horizontal" in box
    ):
        return "2t"
    if "component-bottom" in box and "component-top" not in box:
        return "2b"
    h_pos = box.find("stack-horizontal")
    first_part = box.find("kanji-part")
    if h_pos == -1:
        return "v"
    if first_part == -1:
        return "v"
    if first_part < h_pos:
        return "2b"
    return "2t"


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


def harvest_lesson(path: Path, lesson_num: int) -> dict[str, dict]:
    """kanji -> {layout, parts, outer, box_snippet}"""
    text = path.read_text(encoding="utf-8")
    out: dict[str, dict] = {}
    for block in re.split(r'<section\s+class="kanji-entry"', text)[1:]:
        km = re.search(r'data-kanji="([^"]*)"', block)
        if not km:
            continue
        kanji = km.group(1).strip()
        box = extract_component_box(block)
        outer = ""
        om = re.search(r'class="component-layout\s+([^"]+)"', box)
        if om:
            outer = om.group(1).strip()
        layout = infer_layout_from_box(box)
        parts = extract_parts_ordered(box)
        out[kanji] = {
            "lesson": lesson_num,
            "layout": layout,
            "parts": parts,
            "outer": outer,
            "has_box": bool(box),
        }
    return out


def normalize_lesson_html(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = defaultdict(int)
    for old, new in HTML_RENAMES:
        n = text.count(old)
        if n:
            counts[f"{old} → {new}"] = n
            text = text.replace(old, new)
    return text, dict(counts)


def clean_field(value: str | None) -> str:
    if value is None:
        return ""
    v = value.strip()
    if "|" in v or ";" in v:
        sep = "|" if "|" in v else ";"
        return sep.join(p.strip() for p in v.split(sep) if p.strip())
    return v


def suggest_grouping(parts: list[str], layout: str) -> str:
    if not parts:
        return ""
    if layout in ("2l", "2r", "2t", "2b") and len(parts) >= 2:
        return "|".join(parts)
    return "|".join(parts)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Normalize lesson HTML ---
    html_norm_report: list[str] = []
    total_renames = defaultdict(int)
    for n in LESSON_RANGE:
        path = LESSONS_DIR / f"lesson_{n:02d}.html"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        new_text, counts = normalize_lesson_html(text)
        if counts:
            path.write_text(new_text, encoding="utf-8")
            html_norm_report.append(f"lesson_{n:02d}.html: {counts}")
            for k, v in counts.items():
                total_renames[k] += v

    # Re-harvest after normalization (layout unchanged; naming only)
    html_by_kanji = {}
    for n in LESSON_RANGE:
        path = LESSONS_DIR / f"lesson_{n:02d}.html"
        if path.exists():
            html_by_kanji.update(harvest_lesson(path, n))

    # --- Load v2 ---
    with open(V2_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys()) if rows else []

    alignments: list[dict] = []
    cleanup_items: list[str] = []
    updated_l1_22 = 0

    for row in rows:
        raw_kanji = row.get("kanji") or ""
        kanji = raw_kanji.strip()
        if raw_kanji != kanji:
            cleanup_items.append(f"kanji: {raw_kanji!r} -> {kanji!r}")

        for fld in ("keyword", "kml_primitives", "cluster_components", "collapse_to", "notes"):
            raw = row.get(fld) or ""
            cleaned = clean_field(raw)
            if raw != cleaned and fld != "notes":
                cleanup_items.append(f"{kanji or raw_kanji}.{fld}: trimmed")
            row[fld] = cleaned

        row["kanji"] = kanji

        try:
            ln = int(row.get("lesson_number") or 0)
        except ValueError:
            ln = 0

        old_lt = (row.get("layout_type") or "").strip()
        old_notes = (row.get("notes") or "").strip()
        if "html suggests" in old_notes:
            old_notes = re.sub(r";?\s*html suggests[^;]*", "", old_notes).strip()
        if old_notes.startswith("layout_type unknown"):
            old_notes = ""

        if ln <= 22 and kanji in html_by_kanji:
            h = html_by_kanji[kanji]
            new_lt = h["layout"]
            if new_lt:
                if old_lt != new_lt:
                    alignments.append(
                        {
                            "kanji": kanji,
                            "lesson": ln,
                            "old": old_lt,
                            "new": new_lt,
                            "outer": h["outer"],
                            "parts": "|".join(h["parts"]),
                        }
                    )
                row["layout_type"] = new_lt
                updated_l1_22 += 1
                if old_lt != new_lt:
                    row["notes"] = (
                        f"pass2a: {old_lt or '—'} -> {new_lt}"
                        if not old_notes
                        else f"pass2a: {old_lt or '—'} -> {new_lt}; {old_notes}"
                    )
            elif not h["has_box"] and old_lt in ("", "a"):
                pass
            elif not h["has_box"]:
                alignments.append(
                    {
                        "kanji": kanji,
                        "lesson": ln,
                        "old": old_lt,
                        "new": "(no component-box)",
                        "outer": "",
                        "parts": "",
                    }
                )

    # --- Write v3 ---
    v3_path = OUT_DIR / "kanji_master_with_components.v3.csv"
    with open(v3_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # --- layout_alignment_report.txt ---
    confirmed = [
        ("婿", "2r"),
        ("裁", "2l"),
        ("壊", "2r"),
        ("遠", "h"),
        ("布", "h"),
        ("幌", "2r"),
        ("錦", "2r"),
    ]
    lines = [
        "PASS 2A — LAYOUT ALIGNMENT REPORT",
        "=" * 60,
        "Rule: Lessons 1–22 HTML structure wins over CSV.",
        "",
        f"Kanji in lessons 1–22 with HTML harvest: {sum(1 for r in rows if int(r.get('lesson_number') or 99) <= 22)}",
        f"layout_type updated from HTML: {updated_l1_22}",
        f"layout_type changes (old != new): {len(alignments)}",
        "",
        "## CONFIRMED EXAMPLES (user + verified in HTML)",
        "",
    ]
    for k, expected in confirmed:
        got = html_by_kanji.get(k, {}).get("layout", "?")
        ok = "OK" if got == expected else f"MISMATCH (got {got})"
        lines.append(f"  {k}  expected={expected}  html={got}  {ok}")

    lines += ["", "## ALL LAYOUT CHANGES (lessons 1–22)", ""]
    for a in sorted(alignments, key=lambda x: (x["lesson"], x["kanji"])):
        lines.append(
            f"  L{a['lesson']:2d}  {a['kanji']}\t{a['old'] or '—':4s} -> {a['new']:4s}\t"
            f"outer={a['outer']}\tparts={a['parts']}"
        )

    lines += [
        "",
        "## HTML CLASS RENAMES (lessons 1–22)",
        "",
    ]
    if total_renames:
        for k, v in sorted(total_renames.items()):
            lines.append(f"  {k}: {v}")
    else:
        lines.append("  (none applied)")
    for entry in html_norm_report:
        lines.append(f"  {entry}")

    (OUT_DIR / "layout_alignment_report.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    # --- hidden_reusable_candidates.txt ---
    cand_lines = [
        "HIDDEN REUSABLE KANJI — INSERTION CANDIDATES (PASS 2A)",
        "=" * 60,
        "Recommendations only. NOT inserted into master.",
        "",
    ]
    for sym in HIDDEN_CANDIDATES:
        uses: list[dict] = []
        for n in LESSON_RANGE:
            path = LESSONS_DIR / f"lesson_{n:02d}.html"
            if not path.exists():
                continue
            for parent, info in harvest_lesson(path, n).items():
                if sym in info["parts"]:
                    uses.append(
                        {
                            "lesson": n,
                            "parent": parent,
                            "layout": info["layout"],
                            "parts": info["parts"],
                        }
                    )
        uses.sort(key=lambda u: u["lesson"])
        first = uses[0] if uses else None
        cand_lines.append(f"## {sym}")
        if first:
            cand_lines.append(f"  first_lesson: {first['lesson']}")
            cand_lines.append(f"  first_parent: {first['parent']}")
            cand_lines.append(f"  suggested_layout_type: {first['layout']}")
            idx = first["parts"].index(sym) if sym in first["parts"] else -1
            grouping = "|".join(first["parts"])
            cand_lines.append(f"  suggested_primitive_grouping: {grouping}")
            cand_lines.append(f"  cognitive_note: preserve family grouping as in HTML")
        cand_lines.append(f"  total_parent_uses_in_L1-22: {len(uses)}")
        for u in uses[:6]:
            cand_lines.append(
                f"    L{u['lesson']:2d} parent={u['parent']} layout={u['layout']} parts={'|'.join(u['parts'])}"
            )
        if len(uses) > 6:
            cand_lines.append(f"    ... +{len(uses) - 6} more")
        cand_lines.append("")

    (OUT_DIR / "hidden_reusable_candidates.txt").write_text(
        "\n".join(cand_lines) + "\n", encoding="utf-8"
    )

    # --- cleanup_report.txt ---
    # Also scan full master for whitespace
    master_cleanup: list[str] = []
    if MASTER_PATH.exists():
        with open(MASTER_PATH, encoding="utf-8") as f:
            for i, row in enumerate(csv.DictReader(f), start=2):
                rk = row.get("kanji") or ""
                if rk != rk.strip():
                    master_cleanup.append(f"kanji_master line {i}: {rk!r}")

    # Trim whitespace in source kanji_master_with_components.csv
    if MASTER_PATH.exists():
        with open(MASTER_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            mfields = reader.fieldnames or []
            master_rows = list(reader)
        changed = False
        for row in master_rows:
            for key in list(row.keys()):
                val = row.get(key)
                if not val or not isinstance(val, str):
                    continue
                nv = val.strip()
                if key in ("kml_primitives", "cluster_components") and (
                    "|" in nv or ";" in nv
                ):
                    sep = "|" if "|" in nv else ";"
                    nv = sep.join(p.strip() for p in nv.split(sep) if p.strip())
                if val != nv:
                    changed = True
                row[key] = nv
        if changed:
            with open(MASTER_PATH, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=mfields)
                w.writeheader()
                w.writerows(master_rows)
            cleanup_items.append("kanji_master_with_components.csv: trimmed fields written")

    clean_lines = [
        "PASS 2A — DATA CLEANUP REPORT",
        "=" * 60,
        "",
        "## v3.csv field cleanup",
        "",
    ]
    if cleanup_items:
        for item in cleanup_items[:200]:
            clean_lines.append(f"  {item}")
        if len(cleanup_items) > 200:
            clean_lines.append(f"  ... +{len(cleanup_items) - 200} more")
    else:
        clean_lines.append("  No whitespace fixes needed in v3 fields.")
    clean_lines += ["", f"Total cleanup actions: {len(cleanup_items)}", ""]
    clean_lines += ["## kanji_master_with_components.csv (source file scan)", ""]
    if master_cleanup:
        for item in master_cleanup:
            clean_lines.append(f"  {item}")
    else:
        clean_lines.append("  No remaining kanji whitespace anomalies.")
    (OUT_DIR / "cleanup_report.txt").write_text(
        "\n".join(clean_lines) + "\n", encoding="utf-8"
    )

    print("PASS 2A complete.")
    print(f"  layout changes: {len(alignments)}")
    print(f"  HTML renames: {dict(total_renames)}")
    print(f"  v3: {v3_path}")


if __name__ == "__main__":
    main()
