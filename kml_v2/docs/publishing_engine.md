# KML Publishing Engine v1

**Status:** Active  
**Stack:** Python + Jinja2  
**API:** `load_lesson` / `build_lesson` / `build_book` / `build_site` / `build_all`

Metadata is the source of truth. Generated HTML is an output artifact.

```
Lesson Pack → Python objects → Jinja2 templates → HTML
```

Templates never read JSON. Business logic stays in Python.

---

## Setup

```bash
cd kml_v2
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

---

## Commands

```bash
# Validate
.venv/bin/python -m publish validate lesson_001

# Build one lesson
.venv/bin/python -m publish build lesson lesson_001
.venv/bin/python -m publish build lesson lesson_002

# Build a book landing page
.venv/bin/python -m publish build book book_01

# Homepage
.venv/bin/python -m publish build site

# Everything (validates packs; fails closed on errors)
.venv/bin/python -m publish build all

# Authoring helpers
.venv/bin/python -m publish status
.venv/bin/python -m publish report missing
.venv/bin/python -m publish report youtube
.venv/bin/python -m publish report heroes
.venv/bin/python -m publish report drafts
.venv/bin/python -m publish create lesson_003
```

Rendering **stops** if validation fails (missing pack files, empty kanji roster, duplicates, etc.).

---

## Package layout

```
publish/
  models.py      # Lesson, Kanji, Book, …
  loaders.py     # load_lesson / load_book
  validate.py    # pack + object checks
  render.py      # Jinja2 only
  engine.py      # orchestration
  cli.py         # CLI
templates/
  base.html
  lesson.html
  book.html
  home.html
  gallery.html
  search.html
  includes/      # header, footer, nav, hero, sections, kanji_card, …
```

---

## Workflow

```
Create Lesson → Edit metadata → Validate → Build → Preview → Publish
```

1. `python -m publish create lesson_NNN`
2. Author pack under `data/lessons/lesson_NNN/`
3. `python -m publish validate lesson_NNN`
4. `python -m publish build lesson lesson_NNN`
5. Serve `kml_v2/` over HTTP and open the generated path

Do not hand-edit generated HTML (files are marked GENERATED).

---

## Future outputs (same metadata)

HTML pages, book pages, gallery, search index, sitemap, RSS, JSON feeds,
OpenGraph, YouTube descriptions, APIs — without changing lesson packs.

Next phases: Authoring Workspace UX, richer Dashboard (“KML Studio”), batch migration.
