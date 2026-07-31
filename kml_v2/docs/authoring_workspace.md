# Authoring Workspace (design)

**Status:** Active with KML Studio — virtual workspace now; physical co-location later  
**Depends on:** [architecture_decisions.md](architecture_decisions.md), [kml_studio.md](kml_studio.md)

## Purpose

Improve the **author’s** content-creation experience — not the generated website.

Each lesson should become a self-contained workspace where every resource required
to create, review, publish, and maintain that lesson is discoverable in one place.

The publishing pipeline continues to consume **structured metadata only**.
The authoring layer stays independent of presentation and build logic.

---

## Target shape (proposal)

```
lesson_001/
  author/
    notes.md
    prompts.md
    todo.md
    research.md
  data/
    lesson.json
    kanji.json
    compounds.json
    vocabulary.json
    phrases.json
    gallery.json
    youtube.json
    assets.json
  media/
    hero.png
    thumbnails/
    references/
  build/          # generated previews, not source of truth
```

Today’s metadata lives at `kml_v2/data/lessons/lesson_NNN/`. Relocating into
an authoring workspace is an **evolutionary** move once tooling exists —
paths in consumers should resolve through a single root convention.

---

## Rules

1. Authoring files (`author/`, local notes) are for humans; they are not
   duplicated into HTML.
2. `data/` remains the publishable contract (schemas + validation).
3. `media/` stays outside Git (or stays gitignored); metadata stores paths.
4. `build/` is disposable output (previews, generated pages).
5. Do not relocate pack folders until Studio v1 workflows feel routine for
   several lessons. Prefer the virtual workspace in KML Studio first.

---

## Guiding principle

KML V2 is a metadata-driven publishing platform with a lesson-centered
authoring workflow — not merely a website.
