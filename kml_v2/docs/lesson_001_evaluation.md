# Phase 3 — Lesson 1 metadata evaluation

**Status: Approved as reference model** (2026-07-29).  
See [architecture_decisions.md](architecture_decisions.md).

## Pack contents

```
data/lessons/lesson_001/
  lesson.json       core identity, book, status, relationships, nav
  kanji.json        20 characters (Heisig 1–20) + verses + readings
  vocabulary.json   299 items (143 atoms / 156 phrases) — prototype
  compounds.json    89 compounds
  gallery.json      ambient/gallery collection links
  youtube.json      unpublished (no production YouTube ID)
  assets.json       logical media paths + old-tree source_refs
```

## Schema improvements made

| Change | Why |
|---|---|
| Added **`kanji.json`** | Lesson is centered on characters; packing them into vocabulary was wrong |
| Added **`compounds.json`** | Distinct entity layer (not ambient-only trivia) |
| Expanded `lesson.json` `pack` + `focus` | Explicit file map; Heisig range / open–close characters |
| `gallery.json` → `collections[]` | Named ambient surfaces with roles, not a flat id list alone |
| `assets.json` `logical_layout` + `source_refs` | Stable V2 paths vs temporary pointers into old `kml/` tree |
| Index fields `opening_character`, `kanji_count` | Thin listing without loading full packs |

## Redundancy to avoid

| Avoid | Prefer |
|---|---|
| Re-storing each kanji’s `study_image` only in `assets.json` | Keep per-kanji paths on `kanji.json` items; lesson-level cover in `assets.json` |
| Duplicating verse text into `vocabulary.json` | Verses live on `kanji.json`; vocab derives atoms/phrases |
| Copying YouTube titles by hand into homepage/sitemap | Derive from `lesson.json` / generate description from pack |
| Embedding exhibition timing/cameras in the lesson pack | Keep in ambient source files until an ambient schema exists |
| Dual philosophy-verse sources (`kanji_production` vs stories CSV) | **Canonical verses = `lesson_01_stories.csv` / production verse text** (already used in `kanji.json`) |

## Gaps / missing before Lesson 2

1. **Beyond Jōyō** — add optional `beyond_joyo.json` or items with `category: "beyond_joyo"` / link ids (lesson 001 has empty `beyond_joyo_ids`).
2. **Site-wide Vocabulary section** — lesson `vocabulary.json` ≠ top-level `vocabulary/` product; need a clear ID scheme when that section ships.
3. **Shared kanji registry** — long-term, characters may deserve `data/kanji/k_one.json` referenced by many lessons; today’s pack embeds them (correct for Lesson 1 autonomy).
4. **Stroke SVG references** — stroke HTML paths noted; SVG asset ids not yet first-class.
5. **JLPT / frequency** — omitted from pack (available in master CSV); add only if product needs them as curriculum facts.
6. **CI validation** — schemas exist; wire `check-jsonschema` (or similar) before bulk authoring.

## Can this support…?

| Surface | Verdict |
|---|---|
| Fifty lessons | Yes — one pack folder each; thin index |
| Beyond Jōyō | Yes with `category` / relationship ids (gap #1) |
| Vocabulary product | Partially — lesson vocab yes; site section needs its own index |
| Ambient collections | Yes via `gallery.json` collections + `relationships.ambient_ids` |
| Future books | Yes — `book_id` / `book_number` + book records |
| YouTube tooling | Yes once `youtube.id` is set; generate body from pack |

## Recommendations before Lesson 2

1. **Approve** `kanji.json` + `compounds.json` as required pack files for curriculum lessons.
2. Decide whether vocabulary **phrases** stay in `vocabulary.json` or move to `phrases.json`.
3. Do **not** mass-import ambient timing JSON into packs.
4. Sync binaries into `media/lessons/lesson_001/` when presentation work starts (still outside Git).
5. Only after approval: author `lesson_002/` pack the same way — still no bulk HTML migration.

## Demo

Serve `kml_v2` over HTTP and open  
`/books/book_01/lessons/lesson_01.html`  
— roster and summary hydrate from the pack.
