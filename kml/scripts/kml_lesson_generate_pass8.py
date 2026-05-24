#!/usr/bin/env python3
"""
PASS 8 — Generate lesson_23–27_v2.html from v4c + render engine (safe side-by-side).
Does NOT overwrite existing lesson files.
"""

from __future__ import annotations

import csv
import re
import sys
from copy import deepcopy
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from lib.kml_render_engine import ComponentRenderEngine, RenderEngineConfig  # noqa: E402

V4C = BASE / "data/kanji/kanji_master_with_components.v4c.csv"
GLOSSARY = BASE / "data/kanji/glossary_family.csv"
LESSONS_DIR = BASE / "contents/books/book_01/lessons"
REPORT = BASE / "data/kanji/lesson_generation_report_23_27.txt"

LESSON_RANGE = range(23, 28)

# Glossary anchors — do not atomize when the kanji IS the hub.
ANCHOR_COMPRESS = frozenset(
    {"曷", "啇", "商", "袁", "戈", "俞", "夂", "𧘇", "竟", "競", "鏡", "境"}
)

SECTION_RE = re.compile(
    r'<section\s+class="kanji-entry"[^>]*data-kanji="([^"]+)"[^>]*>.*?</section>',
    re.DOTALL,
)
COMPONENT_BOX_RE = re.compile(
    r"\s*<div\s+class=\"component-box\"[^>]*>.*?</motion div>\s*</motion div>\s*",
    re.DOTALL,
)


def load_glossary() -> tuple[dict[str, str], set[str]]:
    """symbol -> family_id; hub symbols for CSS class."""
    by_sym: dict[str, str] = {}
    hubs: set[str] = set()
    with open(GLOSSARY, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fid = (row.get("family_id") or "").strip()
            anchor = (row.get("anchor_symbol") or "").strip()
            priority = (row.get("glossary_priority") or "").strip()
            if not fid or not anchor:
                continue
            if priority in ("high", "medium"):
                hubs.add(anchor)
            by_sym[anchor] = fid
            for k in (row.get("example_kanji") or "").split("|"):
                k = k.strip()
                if k and k not in by_sym:
                    by_sym[k] = fid
    # Explicit lesson cognition overrides
    by_sym["商"] = "deal_family"
    by_sym["啇"] = "merchant_family"
    by_sym["曷"] = "siesta_family"
    by_sym["袁"] = "robe_family"
    by_sym["竟"] = "competition_family"
    hubs.update(ANCHOR_COMPRESS)
    return by_sym, hubs


def load_master() -> tuple[dict[str, dict], set[str]]:
    rows: dict[str, dict] = {}
    hidden: set[str] = set()
    with open(V4C, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            k = (row.get("kanji") or "").strip()
            if k:
                rows[k] = row
                if "hidden_reusable" in (row.get("notes") or "").lower():
                    hidden.add(k)
    hidden.update({"戈", "俞", "袁", "夂"})
    return rows, hidden


def lesson_rows(master: dict[str, dict], n: int) -> list[dict]:
    return [
        master[k]
        for k in sorted(
            (k for k, r in master.items() if str(r.get("lesson_number", "")).strip() == str(n)),
            key=lambda k: master[k].get("keyword", k),
        )
    ]


def infer_layout(parts: list[str], layout: str) -> str:
    if layout:
        return layout
    n = len(parts)
    if n <= 1:
        return "a"
    if n == 2:
        return "h"
    if n == 3:
        return "2r"
    if n >= 4:
        return "2r"
    return "h"


def preprocess_row(
    row: dict,
    log: list[str],
) -> dict:
    row = deepcopy(row)
    kanji = (row.get("kanji") or "").strip()
    layout = (row.get("layout_type") or "").strip()
    raw = (row.get("kml_primitives") or "").strip()
    if raw in ("", "|||"):
        log.append(f"  SKIP incomplete: {kanji} (no kml_primitives)")
        return row

    parts = [p.strip() for p in raw.split("|") if p.strip()]

    if kanji in ANCHOR_COMPRESS and len(parts) > 1:
        log.append(f"  ANCHOR COMPRESS: {kanji} {raw} -> anchor layout a")
        row["kml_primitives"] = kanji
        row["layout_type"] = "a"
        return row

    if not layout:
        inferred = infer_layout(parts, layout)
        log.append(f"  LAYOUT INFER: {kanji} -> {inferred} (was blank, parts={len(parts)})")
        row["layout_type"] = inferred
    elif layout == "3r" and len(parts) < 4:
        row["layout_type"] = "2r"
        log.append(f"  3r FALLBACK: {kanji} parts={len(parts)} -> 2r")

    # Glossary substitution hints (report only; parts unchanged for review)
    for p in parts:
        if p in ANCHOR_COMPRESS and p != kanji:
            log.append(f"  GLOSSARY PART: {kanji} uses hub {p}")

    return row


def section_prefix(section_html: str) -> str:
    m = re.search(r"<div\s+class=\"component-box\"", section_html)
    if m:
        return section_html[: m.start()]
    m = re.search(r"</section>\s*$", section_html, re.DOTALL)
    if m:
        return section_html[: m.start()]
    return section_html


def parse_sections(html: str) -> dict[str, str]:
    return {m.group(1): m.group(0) for m in SECTION_RE.finditer(html)}


def split_lesson_shell(html: str) -> tuple[str, str]:
    first = html.find('<section class="kanji-entry"')
    cta = html.find("<!-- CTA -->")
    if first == -1:
        return html, ""
    head = html[:first]
    foot = html[cta:] if cta != -1 else "</body></html>"
    return head, foot


def patch_head(head: str, lesson_num: int) -> str:
    head = re.sub(
        rf"<title>KML - Lesson {lesson_num}</title>",
        f"<title>KML - Lesson {lesson_num} (v2 preview)</title>",
        head,
    )
    banner = (
        '<p class="pass8-banner" style="background:#fff3cd;padding:0.5rem 1rem;'
        'border-radius:6px;font-size:0.9rem;">'
        "PASS 8 preview — generated component structures for side-by-side review. "
        f'<a href="lesson_{lesson_num:02d}.html">View original lesson {lesson_num}</a>'
        "</p>\n"
    )
    head = head.replace(f"<h1>KML - Lesson {lesson_num}</h1>", f"<h1>KML - Lesson {lesson_num}</h1>\n{banner}")
    head = head.replace(
        f'href="lesson_{lesson_num:02d}.html"',
        f'href="lesson_{lesson_num:02d}_v2.html"',
    )
    return head


def build_section(
    kanji: str,
    sections: dict[str, str],
    box_html: str,
    keyword: str,
) -> str:
    base = sections.get(kanji, "")
    if base:
        prefix = section_prefix(base)
    else:
        slug = keyword.replace(" ", "_")
        prefix = f"""<section class="kanji-entry"
         id="kanji-{slug}"
         data-kanji="{kanji}"
         data-slug="{slug}">

  <h2 class="kanji-header">
    <span class="kanji-main-font">{kanji}</span>
    <span class="kanji-keyword">{keyword}</span>
  </h2>

"""
    if box_html:
        box_html = "\n" + box_html + "\n"
    else:
        box_html = (
            f'\n<div class="component-box" data-render-status="incomplete">\n'
            f'  <!-- pass8: no render for {kanji} -->\n</div>\n'
        )
    return prefix + box_html + "\n</section>\n\n"


def generate_lesson(
    lesson_num: int,
    engine: ComponentRenderEngine,
    master: dict[str, dict],
    log: list[str],
) -> str:
    src_path = LESSONS_DIR / f"lesson_{lesson_num:02d}.html"
    src = src_path.read_text(encoding="utf-8")
    head, foot = split_lesson_shell(src)
    head = patch_head(head, lesson_num)

    sections = parse_sections(src)
    rows = [
        r
        for r in master.values()
        if str(r.get("lesson_number", "")).strip() == str(lesson_num)
    ]
    # Preserve lesson order from original anchor nav / section order
    order = [m.group(1) for m in SECTION_RE.finditer(src)]
    row_by_k = {r["kanji"]: r for r in rows}
    ordered = [row_by_k[k] for k in order if k in row_by_k]
    for r in rows:
        if r["kanji"] not in order:
            ordered.append(r)

    blocks: list[str] = []
    stats = {"ok": 0, "incomplete": 0, "error": 0, "3r": 0}

    for row in ordered:
        kanji = row["kanji"]
        proc = preprocess_row(row, log)
        result = engine.render(proc)
        layout = (proc.get("layout_type") or "").strip()
        if layout == "3r":
            stats["3r"] += 1
            log.append(f"  3r USED: {kanji} parts={'|'.join(result.parts)}")
        if result.status == "ok":
            stats["ok"] += 1
            box = result.html
            if any(p in ANCHOR_COMPRESS for p in result.parts if p != kanji):
                fams = sorted(
                    {engine.config.family_by_symbol.get(p, "") for p in result.parts} - {""}
                )
                if fams:
                    log.append(f"  FAMILY TAGS: {kanji} -> {','.join(fams)}")
        elif result.status == "incomplete":
            stats["incomplete"] += 1
            log.append(f"  UNCERTAIN: {kanji} — {result.message}")
            box = result.html
        else:
            stats["error"] += 1
            log.append(f"  ERROR: {kanji} — {result.message}")
            box = f'<!-- pass8 error: {result.message} -->'

        blocks.append(
            build_section(kanji, sections, box, (row.get("keyword") or kanji).replace("_", " "))
        )

    log.append(f"  Lesson {lesson_num} stats: {stats}")
    return head + "".join(blocks) + foot


def main() -> None:
    family_by_sym, hub_syms = load_glossary()
    master, hidden = load_master()

    cfg = RenderEngineConfig(
        allow_hidden_links=True,
        hidden_kanji=hidden,
        family_by_symbol=family_by_sym,
        glossary_hub_symbols=hub_syms,
    )
    engine = ComponentRenderEngine.from_csv(V4C, config=cfg)

    report: list[str] = [
        "PASS 8 — LESSON GENERATION REPORT (Lessons 23–27 v2)",
        "=" * 70,
        "",
        f"Source CSV: {V4C.name}",
        f"Glossary:   {GLOSSARY.name}",
        "Output:     lesson_XX_v2.html (does NOT overwrite originals)",
        "",
    ]

    for n in LESSON_RANGE:
        report.append(f"## LESSON {n}")
        report.append("")
        lesson_log: list[str] = []
        html = generate_lesson(n, engine, master, lesson_log)
        out = LESSONS_DIR / f"lesson_{n:02d}_v2.html"
        out.write_text(html, encoding="utf-8")
        report.extend(lesson_log)
        report.append(f"  Written: {out.name}")
        report.append("")

    report += [
        "## ARCHITECTURE NOTES",
        "",
        "  - Glossary hubs tagged with data-family + glossary-hub class",
        "  - Anchor compression: hub kanji rendered as layout a (no atomization)",
        "  - Hidden reusables (戈/俞/袁/夂) use future-kanji-link when configured",
        "  - 3r: left anchor + right vertical stack of three (experimental)",
        "",
        "## KEY PRINCIPLE",
        "",
        "  Human-guided assisted cognition rendering — not authoritative decomposition.",
        "",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Wrote lessons 23–27 v2 to {LESSONS_DIR}")
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
