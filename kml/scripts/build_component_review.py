#!/usr/bin/env python3
"""Build Phase-1 component review pages for Lessons 1–40.

Workflow:
  1. Edit lesson_XX.html component-box to nested Horizontal/Vertical only
  2. python3 scripts/build_component_review.py
  3. Open tools/component_review/index.html — verify one lesson in minutes

Displays exactly what lesson HTML contains. Does not invent layouts.
Legacy enclosure / composite structures are flagged for manual conversion.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from lib.html_component_parser import parse_lesson_html  # noqa: E402
from lib.kml_hv_renderer import (  # noqa: E402
    outline,
    render_box,
    tree_from_parser_node,
)

LESSONS_DIR = BASE / "contents" / "books" / "book_01" / "lessons"
OUT_DIR = BASE / "tools" / "component_review"
LABELS_PATH = BASE / "tools" / "ambient" / "data" / "kanji_components_catalog.json"


def load_labels() -> dict[str, str]:
    if not LABELS_PATH.exists():
        return {}
    cat = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    return dict(cat.get("componentLabels") or {})


def build_lesson_page(lesson: int, labels: dict[str, str]) -> dict:
    path = LESSONS_DIR / f"lesson_{lesson:02d}.html"
    decomps = parse_lesson_html(path, lesson)
    rows = []
    ok = 0
    needs = 0
    for d in decomps:
        issues: list[str] = []
        tree = None
        rendered = ""
        text_outline = ""
        status = "ok"

        if not d.has_box:
            status = "needs_edit"
            issues.append("no_component_box")
            needs += 1
        elif d.tree is None:
            status = "needs_edit"
            issues.append("empty_tree")
            needs += 1
        else:
            tree, conv_issues = tree_from_parser_node(d.tree)
            issues.extend(conv_issues)
            if tree is None or conv_issues:
                status = "needs_edit"
                needs += 1
                # Show raw lesson HTML box for editing reference
                rendered = d.raw_box
            else:
                status = "ok"
                ok += 1
                rendered = render_box(tree)
                text_outline = outline(tree)

        # Placeholder self-ref note
        if "placeholder_self_reference" in (d.notes or []):
            issues.append("placeholder_self_reference")
            if status == "ok":
                status = "needs_edit"
                needs += 1
                ok = max(0, ok - 1)

        part_labels = []
        for g in d.parts_flat:
            part_labels.append(
                {"glyph": g, "label": labels.get(g) or g}
            )

        rows.append(
            {
                "kanji": d.kanji,
                "keyword": d.keyword,
                "slug": d.slug,
                "status": status,
                "issues": issues,
                "partsFlat": d.parts_flat,
                "partLabels": part_labels,
                "outline": text_outline,
                "renderedHtml": rendered,
                "layoutType": d.layout_type,
            }
        )

    return {
        "lesson": lesson,
        "ok": ok,
        "needsEdit": needs,
        "total": len(rows),
        "rows": rows,
    }


def page_html(data: dict) -> str:
    lesson = data["lesson"]
    cards = []
    for r in data["rows"]:
        issues = ""
        if r["issues"]:
            issues = (
                '<ul class="issues">'
                + "".join(f"<li>{html_lib.escape(i)}</li>" for i in r["issues"])
                + "</ul>"
            )
        outline_pre = ""
        if r["outline"]:
            outline_pre = (
                f'<pre class="outline">{html_lib.escape(r["outline"])}</pre>'
            )
        parts = " · ".join(
            f'{html_lib.escape(p["glyph"])}'
            + (
                f' <span class="plabel">{html_lib.escape(p["label"])}</span>'
                if p["label"] != p["glyph"]
                else ""
            )
            for p in r["partLabels"]
        )
        cards.append(
            f"""
<article class="card status-{html_lib.escape(r['status'])}" id="{html_lib.escape(r['slug'] or r['kanji'])}">
  <header>
    <span class="hero">{html_lib.escape(r['kanji'])}</span>
    <span class="kw">{html_lib.escape(r['keyword'])}</span>
    <span class="badge">{html_lib.escape(r['status'])}</span>
  </header>
  <div class="body">
    <div class="render">{r['renderedHtml']}</div>
    <div class="meta">
      {outline_pre}
      <p class="parts">{parts}</p>
      {issues}
    </div>
  </div>
</article>
"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lesson {lesson} — Component Review</title>
  <link rel="stylesheet" href="../../assets/site/css/kml_components_hv.css">
  <link rel="stylesheet" href="review.css">
</head>
<body>
  <nav class="top">
    <a href="index.html">All lessons</a>
    <span>Lesson {lesson}</span>
    <span class="summary ok">{data['ok']} ok</span>
    <span class="summary needs">{data['needsEdit']} need edit</span>
  </nav>
  <header class="page-head">
    <h1>Lesson {lesson}</h1>
    <p>Phase 1 — Horizontal / Vertical only. Edit
      <code>contents/books/book_01/lessons/lesson_{lesson:02d}.html</code>,
      then rebuild.</p>
  </header>
  <main class="grid">
    {"".join(cards)}
  </main>
</body>
</html>
"""


def index_html(summaries: list[dict]) -> str:
    rows = []
    for s in summaries:
        cls = "done" if s["needsEdit"] == 0 else "open"
        rows.append(
            f'<li class="{cls}">'
            f'<a href="lesson_{s["lesson"]:02d}.html">Lesson {s["lesson"]}</a>'
            f' — {s["ok"]}/{s["total"]} ok'
            f'{f", {s['needsEdit']} need edit" if s["needsEdit"] else ""}'
            f"</li>"
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>KML Component Review — Lessons 1–40</title>
  <link rel="stylesheet" href="review.css">
</head>
<body>
  <header class="page-head">
    <h1>KML Component Review</h1>
    <p>Phase 1 editorial standard (Lessons 1–40).</p>
    <p>Only <strong>Horizontal</strong> and <strong>Vertical</strong> groups
       (nestable). No enclosure layouts. Recognition, not linguistic
       decomposition.</p>
    <p>Rebuild after HTML edits:</p>
    <pre>python3 scripts/build_component_review.py</pre>
  </header>
  <ol class="lesson-list">
    {"".join(rows)}
  </ol>
</body>
</html>
"""


REVIEW_CSS = """
:root {
  --bg: #f7f4ef;
  --ink: #1c1917;
  --muted: #78716c;
  --ok: #166534;
  --needs: #9a3412;
  --card: #fffdf9;
  --line: #e7e5e4;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.45;
}
.top {
  position: sticky; top: 0; z-index: 2;
  display: flex; gap: 1rem; align-items: center;
  padding: 0.65rem 1.25rem;
  background: rgba(247,244,239,0.92);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(6px);
}
.top a { color: var(--ink); }
.summary.ok { color: var(--ok); }
.summary.needs { color: var(--needs); }
.page-head { padding: 1.5rem 1.25rem 0.5rem; max-width: 1100px; margin: 0 auto; }
.page-head h1 { margin: 0 0 0.4rem; font-weight: 600; }
.page-head p { color: var(--muted); margin: 0.35rem 0; }
.page-head pre {
  background: #fff; border: 1px solid var(--line); padding: 0.6rem 0.8rem;
  border-radius: 6px; overflow: auto;
}
.lesson-list { max-width: 700px; margin: 1rem auto 3rem; padding: 0 1.25rem; }
.lesson-list li { margin: 0.35rem 0; }
.lesson-list .done a { color: var(--ok); }
.grid {
  max-width: 1100px; margin: 0 auto 3rem; padding: 0.5rem 1rem 2rem;
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.85rem 1rem 1rem;
}
.card.status-needs_edit { border-color: #fdba74; background: #fff7ed; }
.card header { display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.6rem; }
.hero {
  font-family: "Noto Serif JP", "Yuji Syuku", serif;
  font-size: 2.4rem; line-height: 1;
}
.kw { color: var(--muted); font-size: 0.95rem; }
.badge {
  margin-left: auto; font-size: 0.7rem; text-transform: uppercase;
  letter-spacing: 0.04em; padding: 0.15rem 0.45rem; border-radius: 999px;
  background: #dcfce7; color: var(--ok);
}
.status-needs_edit .badge { background: #ffedd5; color: var(--needs); }
.body { display: grid; grid-template-columns: 120px 1fr; gap: 0.75rem; align-items: start; }
.render {
  min-height: 120px; display: flex; align-items: center; justify-content: center;
  background: #fff; border: 1px dashed var(--line); border-radius: 8px;
}
.outline {
  margin: 0 0 0.4rem; font-family: ui-monospace, monospace; font-size: 0.78rem;
  white-space: pre; color: #44403c;
}
.parts { margin: 0; font-size: 0.85rem; color: var(--muted); }
.plabel { color: #a8a29e; font-size: 0.8em; }
.issues { margin: 0.4rem 0 0; padding-left: 1.1rem; color: var(--needs); font-size: 0.8rem; }
@media (max-width: 640px) {
  .body { grid-template-columns: 1fr; }
}
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-lesson", type=int, default=40)
    ap.add_argument("--min-lesson", type=int, default=1)
    args = ap.parse_args()

    labels = load_labels()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "review.css").write_text(REVIEW_CSS, encoding="utf-8")

    summaries = []
    for n in range(args.min_lesson, args.max_lesson + 1):
        path = LESSONS_DIR / f"lesson_{n:02d}.html"
        if not path.exists():
            print(f"skip missing {path.name}")
            continue
        data = build_lesson_page(n, labels)
        summaries.append(
            {
                "lesson": n,
                "ok": data["ok"],
                "needsEdit": data["needsEdit"],
                "total": data["total"],
            }
        )
        out = OUT_DIR / f"lesson_{n:02d}.html"
        out.write_text(page_html(data), encoding="utf-8")
        print(
            f"L{n:02d}: {data['ok']}/{data['total']} ok, "
            f"{data['needsEdit']} need edit → {out.relative_to(BASE)}"
        )

    (OUT_DIR / "index.html").write_text(index_html(summaries), encoding="utf-8")
    print(f"wrote {OUT_DIR.relative_to(BASE)}/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
