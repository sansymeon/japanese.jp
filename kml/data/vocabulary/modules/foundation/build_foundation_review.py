#!/usr/bin/env python3
"""Generate a development-only F1–F6 review page from exhibition JSON.

The page is a viewer, not a curriculum. Vocabulary is copied from
vocabulary_f01.json … vocabulary_f06.json at generate time, and the page
also tries to fetch those files live when served.

Run: python3 kml/data/vocabulary/modules/foundation/build_foundation_review.py
(also invoked by build_foundation_module.py)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
LESSON_DIR = REPO / "kml/tools/ambient/collections/vocabulary"
OUT_DIR = REPO / "kml/tools/tmp/foundation_f1_f6_review"
OUT_HTML = OUT_DIR / "index.html"
COLLECTIONS = [f"vocabulary_f0{n}.json" for n in range(1, 7)]
JSON_REL = "../../ambient/collections/vocabulary"


def project(data: dict, filename: str) -> dict:
    scene = data["scenes"][0]
    opening = (data.get("bookends") or {}).get("opening") or {}
    meta = data.get("meta") or {}
    return {
        "id": data["id"],
        "title": data.get("title", ""),
        "jsonFile": filename,
        "jsonUrl": f"{JSON_REL}/{filename}",
        "exhibitionUrl": f"../../ambient/exhibition.html?collection={data['id']}",
        "soundtrack": (data.get("soundtrack") or {}).get("main", ""),
        "proverb": {"jp": opening.get("jp", ""), "en": opening.get("en", "")},
        "beautifulWord": data.get("beautifulWord") or {},
        "meta": {
            "lesson": meta.get("lesson"),
            "moduleTitle": meta.get("moduleTitle"),
            "theme": (scene.get("meta") or {}).get("theme", ""),
            "targetCount": meta.get("targetCount"),
            "exposureCount": meta.get("exposureCount"),
            "exhibitCount": meta.get("exhibitCount"),
            "compoundCount": meta.get("compoundCount"),
            "coverageRule": meta.get("coverageRule", ""),
            "learnerNote": meta.get("learnerNote", ""),
            "reviewWords": (scene.get("meta") or {}).get("reviewWords") or [],
            "targetWords": meta.get("targetWords") or [],
        },
        "steps": (scene.get("compounds") or {}).get("steps") or [],
    }


def load_lessons() -> list[dict]:
    lessons = []
    for name in COLLECTIONS:
        path = LESSON_DIR / name
        if not path.is_file():
            raise SystemExit(f"Missing {path} — rebuild Foundation first.")
        data = json.loads(path.read_text(encoding="utf-8"))
        lessons.append(project(data, name))
    return lessons


def build_html(lessons: list[dict]) -> str:
    payload = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source": "kml/tools/ambient/collections/vocabulary/vocabulary_f01.json … f06.json",
        "lessons": lessons,
    }
    data_json = json.dumps(payload, ensure_ascii=False)
    return TEMPLATE.replace("/*__DATA__*/", data_json)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Foundation F1–F6 — Vocabulary in Context Review</title>
  <style>
    :root {
      --bg: #141518;
      --fg: #c8c4bc;
      --muted: #7a7670;
      --soft: #9a958c;
      --line: #2a2c32;
      --accent: #b8a078;
      --card: #1b1d22;
      --target: #ece8e0;
      --start: #c4a56a;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--fg);
      font: 13px/1.45 "Segoe UI", system-ui, sans-serif;
      padding: 20px 18px 72px;
    }
    .wrap { max-width: 920px; margin: 0 auto; }
    header {
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--line);
    }
    .eyebrow {
      color: var(--accent);
      font-size: 11px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      margin-bottom: 6px;
    }
    h1 {
      font-size: 22px;
      font-weight: 560;
      color: #e6e2da;
      margin-bottom: 6px;
    }
    .sub { color: var(--soft); max-width: 46rem; margin-bottom: 12px; }
    .stats { display: flex; flex-wrap: wrap; gap: 10px 18px; margin-bottom: 10px; }
    .stat span { color: var(--muted); margin-right: 4px; }
    .stat strong { color: #eeeae2; font-weight: 600; }
    .toc, .filters {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }
    .toc a, .filters button, .lesson-head a {
      color: var(--accent);
      text-decoration: none;
      font-size: 12px;
      padding: 3px 8px;
      border: 1px solid var(--line);
      background: #1c1e24;
      border-radius: 3px;
      cursor: pointer;
      font: inherit;
    }
    .toc a:hover, .filters button:hover, .lesson-head a:hover {
      background: #252830;
    }
    .filters button.is-on {
      border-color: #4a4030;
      color: #e6d7b8;
      background: #2a261e;
    }
    .hint, .source {
      margin-top: 10px;
      color: var(--muted);
      font-size: 12px;
    }
    .source code { color: var(--soft); }
    section.lesson {
      margin-top: 32px;
      scroll-margin-top: 8px;
    }
    .lesson-head {
      position: sticky;
      top: 0;
      z-index: 2;
      background: rgba(20, 21, 24, 0.94);
      backdrop-filter: blur(6px);
      padding: 8px 0 8px;
      margin-bottom: 8px;
      border-bottom: 1px solid var(--line);
    }
    .lesson-head h2 {
      font-size: 16px;
      font-weight: 600;
      color: #ddd9d1;
    }
    .lesson-meta {
      color: var(--muted);
      font-size: 12px;
      margin-top: 4px;
    }
    .proverb {
      margin: 10px 0 14px;
      padding: 10px 12px;
      background: var(--card);
      border: 1px solid var(--line);
      color: var(--soft);
    }
    .proverb .jp {
      color: var(--target);
      font-size: 16px;
      font-family: "Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", serif;
      margin-bottom: 2px;
    }
    .group {
      display: grid;
      grid-template-columns: 2.2rem 1fr;
      gap: 0 10px;
      padding: 8px 0;
      border-bottom: 1px solid #22242a;
    }
    .group.is-isolated { opacity: 0.92; }
    .group.is-start .n { color: var(--start); }
    .n {
      color: var(--muted);
      font-variant-numeric: tabular-nums;
      padding-top: 3px;
    }
    .row {
      display: grid;
      grid-template-columns: minmax(12rem, 1.2fr) minmax(10rem, 1fr) auto;
      gap: 8px 14px;
      align-items: baseline;
      padding: 2px 0;
    }
    .row.exposure {
      padding-left: 1.1rem;
    }
    .row.target .jp {
      font-weight: 700;
      color: var(--target);
    }
    .row.exposure .jp {
      font-size: 16px;
      color: #d9d4cb;
      font-weight: 400;
    }
    .row.exposure .jp .kml-target-word {
      font-weight: 700;
      color: var(--target);
    }
    .jp ruby { ruby-position: over; }
    .jp rt {
      font-size: 0.45em;
      font-weight: 400;
      color: var(--soft);
    }
    body:not(.show-readings) .jp rt { display: none; }
    .jp {
      font-family: "Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", "Hiragino Sans", sans-serif;
      font-size: 20px;
      line-height: 1.45;
      color: var(--target);
    }
    .en { color: var(--fg); white-space: pre-line; }
    .row.exposure .en { color: var(--soft); }
    .badges { display: flex; flex-wrap: wrap; gap: 4px; justify-content: flex-end; }
    .pill {
      font-size: 10px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
      border: 1px solid var(--line);
      padding: 1px 6px;
      border-radius: 3px;
      white-space: nowrap;
    }
    .pill.target { color: #ddd8ce; border-color: #3a3c44; }
    .pill.exposure { color: #8a8680; }
    .pill.start-here {
      color: var(--start);
      border-color: #5a4830;
    }
    .pill.review { color: #9aaa8a; }
    .pill.heard, .pill.preview { color: #8a9aaa; }
    .start-note {
      grid-column: 1 / -1;
      color: var(--muted);
      font-size: 11px;
      padding-left: 1.1rem;
    }
    .bw {
      margin-top: 16px;
      padding: 12px;
      border: 1px solid #3a3228;
      background: #1c1a16;
    }
    .bw .label {
      font-size: 10px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 4px;
    }
    .bw .jp { font-size: 22px; }
    .bw ruby { ruby-position: over; }
    footer {
      margin-top: 36px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 12px;
    }
    .empty {
      padding: 24px;
      color: var(--soft);
      border: 1px dashed var(--line);
    }
    @media (max-width: 720px) {
      .row { grid-template-columns: 1fr; }
      .badges { justify-content: flex-start; }
      .row.exposure { padding-left: 0.6rem; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <p class="eyebrow">Temporary review · not public · do not publish</p>
      <h1>Foundation F1–F6 — Vocabulary in Context</h1>
      <p class="sub">Each step is optional. Follow the Japanese as far as you like. Bold is the target; normal weight is Japanese you are invited to explore. Gold marks Start Here wording. Exposure never counts as taught.</p>
      <div class="stats" id="stats"></div>
      <nav class="toc" id="toc" aria-label="Jump to lesson"></nav>
      <div class="filters" id="filters" role="toolbar" aria-label="Filter"></div>
      <p class="source" id="source"></p>
      <p class="hint">Generated from exhibition JSON. Edit vocabulary_f01–f06 (via the Foundation builder), then rebuild this page. Not a second curriculum.</p>
    </header>
    <main id="main"></main>
    <footer>
      <p>Development only · Lessons 1–22 untouched · No MP4s</p>
      <p id="footer-meta"></p>
    </footer>
  </div>
  <script>
    const SNAPSHOT = /*__DATA__*/;

    const FILTERS = [
      ["all", "All"],
      ["context", "Has context"],
      ["isolated", "Isolated"],
      ["start-here", "Start Here"],
    ];

    let filter = "all";
    let showReadings = false;
    let payload = SNAPSHOT;
    let sourceLabel = "generated snapshot";

    async function boot() {
      try {
        const live = await Promise.all(
          SNAPSHOT.lessons.map((lesson) =>
            fetch(lesson.jsonUrl, { cache: "no-store" }).then((r) => {
              if (!r.ok) throw new Error(String(r.status));
              return r.json();
            })
          )
        );
        payload = {
          generatedAt: SNAPSHOT.generatedAt,
          lessons: live.map((data, i) => projectLive(data, SNAPSHOT.lessons[i])),
        };
        sourceLabel = "live JSON";
      } catch {
        payload = SNAPSHOT;
        sourceLabel = "generated snapshot (serve the folder to load live JSON)";
      }
      render();
    }

    function projectLive(data, fallback) {
      const scene = (data.scenes && data.scenes[0]) || {};
      const opening = (data.bookends && data.bookends.opening) || {};
      const meta = data.meta || {};
      return {
        id: data.id || fallback.id,
        title: data.title || fallback.title,
        jsonFile: fallback.jsonFile,
        jsonUrl: fallback.jsonUrl,
        exhibitionUrl: fallback.exhibitionUrl,
        soundtrack: (data.soundtrack && data.soundtrack.main) || "",
        proverb: { jp: opening.jp || "", en: opening.en || "" },
        beautifulWord: data.beautifulWord || {},
        meta: {
          lesson: meta.lesson,
          moduleTitle: meta.moduleTitle,
          theme: (scene.meta && scene.meta.theme) || "",
          targetCount: meta.targetCount,
          exposureCount: meta.exposureCount,
          exhibitCount: meta.exhibitCount,
          compoundCount: meta.compoundCount,
          coverageRule: meta.coverageRule || "",
          learnerNote: meta.learnerNote || "",
          reviewWords: (scene.meta && scene.meta.reviewWords) || [],
          targetWords: meta.targetWords || [],
        },
        steps: (scene.compounds && scene.compounds.steps) || [],
      };
    }

    function groupsOf(steps) {
      const groups = [];
      for (const step of steps) {
        if (step.coverage === "exposure") {
          if (!groups.length) {
            groups.push({ target: null, exposures: [step] });
          } else {
            groups[groups.length - 1].exposures.push(step);
          }
        } else {
          groups.push({ target: step, exposures: [] });
        }
      }
      return groups;
    }

    function render() {
      const lessons = payload.lessons || [];
      let targets = 0;
      let exposures = 0;
      let startHere = 0;
      let isolated = 0;
      for (const lesson of lessons) {
        const groups = groupsOf(lesson.steps);
        targets += groups.filter((g) => g.target).length;
        for (const g of groups) {
          exposures += g.exposures.length;
          if (g.target && !g.exposures.length) isolated += 1;
          startHere += g.exposures.filter((s) => s.source === "start-here").length;
        }
      }

      document.getElementById("stats").innerHTML = [
        stat("Lessons", lessons.length),
        stat("Targets", targets),
        stat("Exposure", exposures),
        stat("Start Here", startHere),
        stat("Isolated", isolated),
      ].join("");

      document.getElementById("source").innerHTML =
        `Source: <code>${escapeHtml(SNAPSHOT.source)}</code> · showing <strong>${sourceLabel}</strong>` +
        (SNAPSHOT.generatedAt ? ` · snapshot ${escapeHtml(SNAPSHOT.generatedAt)}` : "");

      const toc = document.getElementById("toc");
      toc.innerHTML = "";
      const filters = document.getElementById("filters");
      filters.innerHTML = "";
      for (const [id, label] of FILTERS) {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = label;
        b.className = id === filter ? "is-on" : "";
        b.addEventListener("click", () => {
          filter = id;
          render();
        });
        filters.appendChild(b);
      }
      const readingsBtn = document.createElement("button");
      readingsBtn.type = "button";
      readingsBtn.textContent = "Readings";
      readingsBtn.className = showReadings ? "is-on" : "";
      readingsBtn.addEventListener("click", () => {
        showReadings = !showReadings;
        document.body.classList.toggle("show-readings", showReadings);
        readingsBtn.classList.toggle("is-on", showReadings);
      });
      filters.appendChild(readingsBtn);
      document.body.classList.toggle("show-readings", showReadings);

      const main = document.getElementById("main");
      main.innerHTML = "";
      for (const lesson of lessons) {
        const a = document.createElement("a");
        a.href = `#${lesson.id}`;
        a.textContent = lesson.meta.lesson || lesson.id;
        toc.appendChild(a);
        main.appendChild(lessonSection(lesson));
      }

      document.getElementById("footer-meta").textContent =
        `${targets} targets credited · ${exposures} exposure lines not credited`;
    }

    function lessonSection(lesson) {
      const groups = groupsOf(lesson.steps);
      const shown = groups.filter(matchesFilter);
      const section = document.createElement("section");
      section.className = "lesson";
      section.id = lesson.id;
      const m = lesson.meta || {};
      const bw = lesson.beautifulWord || {};
      const startN = groups.reduce(
        (n, g) => n + g.exposures.filter((s) => s.source === "start-here").length,
        0
      );
      section.innerHTML = `
        <div class="lesson-head">
          <h2>${escapeHtml(m.lesson)} — ${escapeHtml(m.moduleTitle || lesson.title)}</h2>
          <p class="lesson-meta">
            ${m.targetCount ?? groups.filter((g) => g.target).length} targets
            · ${m.exposureCount ?? ""} exposure
            · ${startN} Start Here
            · ${escapeHtml(lesson.soundtrack || "")}
            · <a href="${escapeHtml(lesson.exhibitionUrl)}">open exhibition</a>
          </p>
        </div>
        <div class="proverb">
          <div class="jp">${escapeHtml(lesson.proverb && lesson.proverb.jp)}</div>
          <div>${escapeHtml(lesson.proverb && lesson.proverb.en)}</div>
          <div style="margin-top:6px;color:#7a7670">${escapeHtml(m.theme)}</div>
        </div>
        <div class="groups"></div>
        <div class="bw">
          <div class="label">Beautiful Word · not a vocabulary target</div>
          <div class="jp">${bw.jpHtml || escapeHtml(bw.jp || "")}</div>
          <div class="en">${escapeHtml(bw.reading || "")} — ${escapeHtml(bw.en || "")}</div>
        </div>
      `;
      const box = section.querySelector(".groups");
      if (!shown.length) {
        box.innerHTML = `<p class="empty">Nothing in this filter.</p>`;
        return section;
      }
      shown.forEach((group, i) => {
        const n = groups.indexOf(group) + 1;
        box.appendChild(groupEl(group, n));
      });
      return section;
    }

    function matchesFilter(group) {
      const hasStart = group.exposures.some((s) => s.source === "start-here");
      if (filter === "all") return true;
      if (filter === "context") return group.exposures.length > 0;
      if (filter === "isolated") return group.exposures.length === 0;
      if (filter === "start-here") return hasStart;
      return true;
    }

    function groupEl(group, n) {
      const el = document.createElement("div");
      const hasStart = group.exposures.some((s) => s.source === "start-here");
      el.className = "group"
        + (group.exposures.length ? "" : " is-isolated")
        + (hasStart ? " is-start" : "");
      const target = group.target;
      let html = `<div class="n">${String(n).padStart(2, "0")}</div><div>`;
      if (target) {
        html += rowHtml(target, "target");
      }
      for (const step of group.exposures) {
        html += rowHtml(step, "exposure");
        if (step.startHere) {
          html += `<div class="start-note">${escapeHtml(step.startHere)}</div>`;
        }
      }
      html += "</div>";
      el.innerHTML = html;
      return el;
    }

    function rowHtml(step, kind) {
      const pills = [];
      pills.push(`<span class="pill ${kind}">${kind}</span>`);
      if (kind === "target" && step.curriculumRole) {
        pills.push(`<span class="pill ${escapeHtml(step.curriculumRole)}">${escapeHtml(step.curriculumRole)}</span>`);
      }
      if (step.source === "start-here") {
        pills.push(`<span class="pill start-here">Start Here</span>`);
      } else if (kind === "exposure" && step.source) {
        pills.push(`<span class="pill">${escapeHtml(step.source)}</span>`);
      }
      if (kind === "exposure" && step.containsTarget === false) {
        pills.push(`<span class="pill">no lemma</span>`);
      }
      return `
        <div class="row ${kind}">
          <div class="jp" lang="ja">${step.jpHtml || escapeHtml(step.jp)}</div>
          <div class="en">${escapeHtml(step.en)}</div>
          <div class="badges">${pills.join("")}</div>
        </div>`;
    }

    function stat(label, value) {
      return `<div class="stat"><span>${label}</span><strong>${value}</strong></div>`;
    }

    function escapeHtml(s) {
      return String(s ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    boot();
  </script>
</body>
</html>
"""


def main() -> int:
    lessons = load_lessons()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(build_html(lessons), encoding="utf-8")
    print(f"wrote {OUT_HTML.relative_to(REPO)}")
    print("open:  xdg-open kml/tools/tmp/foundation_f1_f6_review/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
