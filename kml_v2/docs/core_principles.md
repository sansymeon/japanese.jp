# KML V2 — Core Development Principles

These principles take precedence over implementation details.
When a coding choice conflicts with a principle, follow the principle.

---

## 1. Metadata First

Do not begin by recreating HTML pages.

Author the curriculum into structured metadata first.
HTML is generated from templates using that metadata.

Lesson pages are the **presentation layer** — not the source of truth.

---

## 2. Lesson 1 Defines the Pattern

Do not migrate all lessons immediately.

Build Lesson 1 on the new metadata architecture.
Once approved, treat it as the reference implementation for every future lesson.
Only then migrate additional lessons.

---

## 3. Content Before Presentation

The important asset is the curriculum.

Separate curriculum data from presentation. Examples that belong in structured data:

- lesson information
- book relationships
- vocabulary
- YouTube IDs
- gallery links
- ambient collections
- tags
- publication status

Not in hard-coded HTML.

---

## 4. HTML Is Disposable

HTML pages should become generated output.

If templates improve later, pages must be regeneratable from metadata
without re-entering information.

---

## 5. Keep Media Outside Git

Do not commit:

- MP3 / MP4
- OBS recordings
- original artwork
- high-resolution images
- render files

Store only metadata that **references** those assets.
Keep media path conventions stable so storage location can change later.

---

## 6. Stable Paths

Design media references so future storage changes need minimal updates.

Avoid embedding storage assumptions throughout the codebase.
Use consistent path conventions for images, thumbnails, audio, and video.

Canonical form (logical path, not a vendor URL):

```text
media/lessons/lesson_001/hero.jpg
media/lessons/lesson_001/thumb.jpg
media/lessons/lesson_001/study.png
media/lessons/lesson_001/audio.mp3
media/lessons/lesson_001/video.mp4
```

Physical storage (disk, object store, CDN) may resolve these paths later.

---

## 7. Validate Metadata

JSON schemas (or equivalent) define contracts under `data/schema/`.

As the project matures, run automated validation in CI so malformed
metadata fails before pages are generated or deployed.

---

## 8. Grow Metadata Incrementally

Keep index files lightweight.

`data/lessons/index.json` — summary fields only.

Rich detail lives in each lesson **pack**:

```text
data/lessons/lesson_001/
  lesson.json
  vocabulary.json
  gallery.json
  youtube.json
  assets.json
```

Indexes stay fast; packs grow richer over time.

---

## 9. Migrate Knowledge, Not HTML

Do not copy old HTML structure.

Instead extract:

- curriculum facts
- relationships
- metadata

Then rebuild presentation with V2 templates and components.
Preserve knowledge; replace implementation.

---

## 10. One Source of Truth

Every fact exists in one place.

A lesson title must not be maintained separately on the homepage,
bookshelf, lesson page, YouTube helper, sitemap, and search index.

It lives once in metadata; every consumer derives it from there.

Locked file authorities are listed in
[architecture_decisions.md](architecture_decisions.md).

---

## Final objective

KML V2 is a **publishing platform**, not a traditional website.

Website, YouTube tooling, automation, search, indexes, playlists,
and future tools all consume the same structured metadata.

**Success = how little duplicated information exists across the project.**

**Reference model:** Lesson 001 pack — future changes should be evolutionary.
