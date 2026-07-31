# KML Component Source Policy

## Phase 1 style

Recognition only. Layouts: **Horizontal** and **Vertical** (nestable). No
enclosures. Lessons 1–40 are manually reviewed and define the KML style.

- Decomposition choices: `KML_COMPONENT_PHILOSOPHY.md`
- Layout / review tooling: `KML_COMPONENT_STYLE_PHASE1.md`

Review UI: `tools/component_review/` — rebuild with
`python3 scripts/build_component_review.py`.

## History

The original component dataset (including v4c) was **placeholder content** so every
lesson page could be built. Lesson HTML was then **manually reviewed and edited**
over time.

Therefore:

- Placeholder decompositions are **not** editorial intent.
- Leftover placeholder patterns in HTML (especially a kanji repeating itself as a
  “part”) are **not** approved KML structure — they are unfinished cleanup.
- The **current, reviewed lesson HTML** is the approved source for KML
  decompositions and layouts.

## Canonical source

**Lesson HTML** (`contents/books/book_01/lessons/lesson_XX.html`) — after editorial
review — is the canonical source for decompositions and layout relationships
(`stack-horizontal`, `stack-vertical`, `enclosure-layout`, composites, nested
layouts).

## Legacy reference

**v4c** (`data/kanji/kanji_master_with_components.v4c.csv`) was not maintained
during lesson development. Treat it as a legacy reference only:

- comparison reports
- recovery when a decomposition is completely absent from HTML

If reviewed HTML and v4c disagree, **HTML is correct** unless explicitly reported
otherwise. Do not “fix” HTML to match v4c. Do not treat v4c placeholders as
authority over HTML.

## Placeholder remnants

Patterns that usually mean unfinished placeholder data, **not** approved intent:

- Parent kanji appearing in its own part list (e.g. `海 → 氵|海`, `浦 → 浦|浦`)
- Empty / missing `component-box` where a real decomposition is expected

These are reported for cleanup. Downstream builds should not present self-reference
parts as meaningful components.

## Generated artifacts

| Artifact | Command | Role |
|----------|---------|------|
| `data/kanji/kml_component_database.json` | `python3 scripts/build_kml_component_database.py` | Master DB harvested from HTML |
| `data/kanji/kml_component_database_report.md` | (same) | Inconsistency / placeholder report (no auto-rewrites of HTML) |
| `tools/ambient/exhibition/lesson_N_foundations.json` | `python3 scripts/build_foundations_from_html.py --lessons …` | Order + keywords from HTML |
| Ambient Kanji Components JSON | `python3 tools/ambient/scripts/build_kanji_components.py` | Exhibition builds; parts from HTML DB |

## Ambient catalog

`tools/ambient/data/kanji_components_catalog.json` still owns:

- English labels for non-kanji components
- New Component introduction pacing
- glyphNormalize (variant display forms)

`componentOverrides` are a legacy escape hatch and apply **only** when HTML
has no usable parts for that kanji.
