#!/usr/bin/env python3
"""
PASS 3 — Render engine proof-of-concept.
Generates test comparison page + render_engine_report.txt.
Does NOT regenerate lesson files.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from lib.kml_render_engine import (  # noqa: E402
    ComponentRenderEngine,
    RenderEngineConfig,
    compare_boxes,
    extract_handcrafted_box,
    normalize_component_box,
)

import os

V3B = Path(
    os.environ.get(
        "KML_MASTER_CSV",
        BASE / "data/kanji/kanji_master_with_components.v3b.csv",
    )
)
LESSONS_DIR = BASE / "contents/books/book_01/lessons"
OUT_HTML = BASE / "tools/render_proof/index.html"
REPORT = BASE / "data/kanji/render_engine_report.txt"

# Representative kanji: layouts + family cognition + hidden reusables
PROOF_KANJI = [
    "一",
    "二",
    "四",
    "古",
    "朋",
    "明",
    "唱",
    "晶",
    "品",
    "旭",
    "負",
    "別",
    "森",
    "暦",
    "婿",
    "裁",
    "壊",
    "遠",
    "布",
    "幌",
    "錦",
    "戈",
    "俞",
    "袁",
]


def load_rows() -> dict[str, dict]:
    with open(V3B, encoding="utf-8") as f:
        return {(r.get("kanji") or "").strip(): r for r in csv.DictReader(f) if r.get("kanji")}


def lesson_section(lesson_num: int, kanji: str) -> str:
    path = LESSONS_DIR / f"lesson_{lesson_num:02d}.html"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    for block in re.split(r'<section\s+class="kanji-entry"', text)[1:]:
        if f'data-kanji="{kanji}"' in block[:200]:
            return block
    return ""


def build_proof_html(cards: list[dict]) -> str:
    rows_html = []
    for c in cards:
        status_cls = c["status"]
        rows_html.append(
            f"""
<section class="proof-card" data-kanji="{c['kanji']}" data-status="{status_cls}">
  <h2>{c['kanji']} <span class="kw">({c['keyword']})</span>
    <span class="badge layout">{c['layout']}</span>
    <span class="badge {status_cls}">{c['status']}</span>
  </h2>
  <p class="meta">L{c['lesson']} · parts CSV: {c['csv_parts'] or '—'} · {c['message']}</p>
  <div class="compare">
    <div class="col">
      <h3>Generated (CSV → engine)</h3>
      <div class="render-panel">{c['generated'] or '<em>no output</em>'}</div>
    </div>
    <div class="col">
      <h3>Handcrafted (lesson HTML)</h3>
      <div class="render-panel">{c['handcrafted'] or '<em>no component-box</em>'}</div>
    </div>
  </div>
</section>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>KML Render Engine — Proof</title>
  <link rel="stylesheet" href="../../assets/site/css/kml_style.css">
  <style>
    body {{ max-width: 1100px; margin: 0 auto; padding: 1.5rem; font-family: system-ui, sans-serif; }}
    h1 {{ font-size: 1.4rem; }}
    .proof-card {{ border: 1px solid #ccc; margin: 1.5rem 0; padding: 1rem; border-radius: 8px; }}
    .compare {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
    .render-panel {{ min-height: 80px; padding: 0.5rem; background: #fafafa; border: 1px dashed #ddd; }}
    .badge {{ font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 4px; background: #eee; }}
    .badge.ok {{ background: #d4edda; }}
    .badge.partial {{ background: #fff3cd; }}
    .badge.incomplete {{ background: #f8d7da; }}
    .badge.skipped_override {{ background: #e2e3e5; }}
    .kw {{ font-weight: normal; color: #555; }}
    .meta {{ font-size: 0.85rem; color: #666; }}
  </style>
</head>
<body>
  <h1>KML Component Render Engine — Proof (PASS 3)</h1>
  <p>Compare CSV-driven <code>component-box</code> output vs handcrafted lessons 1–22.
     No lessons were regenerated.</p>
  <p><strong>Override policy:</strong> rows with <code>render_override=manual</code> in notes
     skip auto-render (handcrafted preserved).</p>
  {"".join(rows_html)}
</body>
</html>
"""


def main() -> None:
    rows = load_rows()
    engine = ComponentRenderEngine.from_csv(V3B)

    cards: list[dict] = []
    report_lines = [
        "KML COMPONENT RENDER ENGINE — PASS 3 REPORT",
        "=" * 60,
        "",
        "Mode: proof-of-concept only; lessons NOT regenerated.",
        f"Templates: {BASE / 'templates/layouts'}",
        f"Data: {V3B}",
        f"Proof kanji sample: {len(PROOF_KANJI)}",
        "",
    ]

    ok_list: list[str] = []
    partial_list: list[str] = []
    incomplete_list: list[str] = []
    mismatch_list: list[str] = []
    ambiguous_list: list[str] = []
    override_list: list[str] = []
    unsupported_list: list[str] = []

    for kanji in PROOF_KANJI:
        row = rows.get(kanji)
        if not row:
            report_lines.append(f"  MISSING ROW: {kanji}")
            continue

        ln = int(row.get("lesson_number") or 0)
        section = lesson_section(ln, kanji) if ln else ""
        hand_box = extract_handcrafted_box(section) if section else ""

        result = engine.render(row)
        gen_box = result.html.strip()

        cmp: dict = {}
        if result.status == "ok" and hand_box:
            cmp = compare_boxes(gen_box, hand_box, result.layout_type)

        # Classify card status for UI
        if result.status == "skipped_override":
            card_status = "skipped_override"
            override_list.append(kanji)
        elif result.status in ("unsupported", "error"):
            card_status = result.status
            unsupported_list.append(f"{kanji}: {result.message}")
        elif result.status == "incomplete":
            card_status = "incomplete"
            incomplete_list.append(f"{kanji}: {result.message} (layout={result.layout_type})")
        elif result.status == "ok" and not hand_box:
            card_status = "partial"
            partial_list.append(f"{kanji}: generated only (no handcrafted box in lesson)")
        elif cmp.get("match"):
            card_status = "ok"
            ok_list.append(kanji)
        elif cmp.get("layout_match") and not cmp.get("parts_match"):
            card_status = "partial"
            partial_list.append(
                f"{kanji}: layout OK; gen={cmp.get('gen_parts')} hand={cmp.get('hand_parts')}"
            )
        elif result.status == "ok" and not cmp:
            card_status = "partial"
            partial_list.append(f"{kanji}: no handcrafted comparison")
        else:
            card_status = "mismatch"
            mismatch_list.append(
                f"{kanji}: csv={cmp.get('csv_layout')} gen={cmp.get('gen_layout')} "
                f"hand={cmp.get('hand_layout')} gen_parts={cmp.get('gen_parts')} "
                f"hand_parts={cmp.get('hand_parts')}"
            )
            if (
                result.layout_type
                and cmp.get("hand_layout")
                and cmp.get("hand_layout") != result.layout_type
            ):
                ambiguous_list.append(f"{kanji}: CSV layout vs hand fingerprint")

        cards.append(
            {
                "kanji": kanji,
                "keyword": row.get("keyword", ""),
                "lesson": ln,
                "layout": result.layout_type,
                "csv_parts": "|".join(result.parts),
                "status": card_status,
                "message": result.message or card_status,
                "generated": gen_box,
                "handcrafted": hand_box,
            }
        )

    report_lines += [
        "## SUCCESSFUL RENDERS (layout + parts match handcrafted)",
        "",
    ]
    report_lines += [f"  {k}" for k in ok_list] or ["  (none)"]
    report_lines += ["", "## PARTIAL (layout match, parts differ)", ""]
    report_lines += [f"  {x}" for x in partial_list] or ["  (none)"]
    report_lines += ["", "## MISMATCHES", ""]
    report_lines += [f"  {x}" for x in mismatch_list] or ["  (none)"]
    report_lines += ["", "## INCOMPLETE DATA (needs CSV primitives or override)", ""]
    report_lines += [f"  {x}" for x in incomplete_list] or ["  (none)"]
    report_lines += ["", "## AMBIGUOUS LAYOUT", ""]
    report_lines += [f"  {x}" for x in ambiguous_list] or ["  (none)"]
    report_lines += ["", "## MANUAL OVERRIDE SKIPS", ""]
    report_lines += [f"  {x}" for x in override_list] or ["  (none)"]
    report_lines += ["", "## UNSUPPORTED / ERROR", ""]
    report_lines += [f"  {x}" for x in unsupported_list] or ["  (none)"]
    report_lines += [
        "",
        "## OVERRIDE SYSTEM",
        "",
        "  Mark rows with notes containing: render_override=manual",
        "  Engine returns status=skipped_override and empty HTML.",
        "  Handcrafted lesson HTML remains authoritative.",
        "",
        "## VISIBILITY HOOKS",
        "",
        "  All generated kanji-part spans include data-visibility=\"visible\".",
        "  Future: hidden | study | quiz (logic not implemented).",
        "",
        "## LAYOUT TEMPLATES",
        "",
    ]
    for code, fname in sorted(
        {
            "a": "anchor.html",
            "h": "horizontal.html",
            "v": "vertical.html",
            "2l": "2l.html",
            "2r": "2r.html",
            "2t": "2t.html",
            "2b": "2b.html",
            "e": "enclosure.html",
            "ei": "enclosure_inner.html",
        }.items()
    ):
        report_lines.append(f"  {code:3s} -> templates/layouts/{fname}")

    report_lines += [
        "",
        "## SUMMARY",
        "",
        f"  ok:         {len(ok_list)}",
        f"  partial:    {len(partial_list)}",
        f"  mismatch:   {len(mismatch_list)}",
        f"  incomplete: {len(incomplete_list)}",
        f"  ambiguous:  {len(ambiguous_list)}",
        "",
        "## NEXT STEPS (not in PASS 3)",
        "",
        "  1. Backfill kml_primitives for rows with layout but empty components.",
        "  2. Mark handcrafted exceptions: render_override=manual in notes.",
        "  3. Enable allow_hidden_links for future-kanji-link parity when ready.",
        "  4. Do not mass-regenerate lessons until CSV + overrides are stable.",
        "",
        "## ENGINE USAGE",
        "",
        "  from lib.kml_render_engine import ComponentRenderEngine",
        "  engine = ComponentRenderEngine.from_csv('...v3b.csv')",
        "  result = engine.render(row)",
        "",
        f"Proof page: {OUT_HTML}",
    ]

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(build_proof_html(cards), encoding="utf-8")
    REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("PASS 3 proof complete.")
    print(f"  ok={len(ok_list)} partial={len(partial_list)} mismatch={len(mismatch_list)}")
    print(f"  incomplete={len(incomplete_list)}")
    print(f"  {OUT_HTML}")
    print(f"  {REPORT}")


if __name__ == "__main__":
    main()
