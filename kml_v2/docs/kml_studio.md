# KML Studio — Authoring Control Center

**Status:** Phase 6 — local web app v1 (Option A) · **Architecture Freeze v1**  
**Audience:** the author  
**Constraint:** [architecture freeze](architecture_freeze_v1.md) — evolve UX/tooling, not the core stack  
**Interface:** local web app — stdlib `http.server` + Jinja2 (no Flask/Django)

Philosophy: [philosophy.md](philosophy.md)

KML Studio is the command center for creating, validating, generating, and
publishing curriculum. The public site still consumes structured metadata only.

```
Author  →  KML Studio (local web)  →  Publishing Engine API  →  generated HTML
                              ↘  repository / data packs (storage)
```

Start:

```bash
cd kml_v2
.venv/bin/python -m studio
# → http://127.0.0.1:8787/
```

---

## Option A stack (locked)

| Piece | Choice |
|---|---|
| HTTP | Python stdlib `ThreadingHTTPServer` |
| Templates | Jinja2 (already used by Publishing Engine) |
| Web framework | **None** — keep local-first and portable |
| Business logic | `studio/services.py` → `publish.*` |
| Site generation | Independent `publish` package (CLI + Studio share it) |

### Package layout

```
studio/
  app.py           # server bootstrap only
  handlers.py      # GET/POST routes (thin)
  httputil.py      # send / redirect / form parse
  views.py         # Jinja2 render for Studio UI
  services.py      # authoring actions → publish engine
  templates/       # Studio UI (not public site templates)
  static/          # Studio CSS/assets
```

Public site templates remain in `kml_v2/templates/` for the Publishing Engine.
Studio UI stays separate so author chrome never mixes with presentation chrome.

---

## Design principles

Studio should answer, at a glance:

| Question | Where |
|---|---|
| What should I work on next? | Attention queue / Next actions |
| Which lessons are incomplete? | Lessons table + warnings |
| What is ready to publish? | Status = `ready` / `published` |
| What assets are missing? | Missing heroes / YouTube / gallery |
| Is everything valid? | Validation panel |
| Can I build with confidence? | Build all + error list |

Minimize searching the repo. Prefer one workspace mental model per lesson.

---

## Lesson lifecycle (uses existing `status`)

No schema redesign. Map the approved enum to the author workflow:

| Author step | `lesson.status` | Meaning |
|---|---|---|
| Create Lesson | `planned` | Pack scaffolded; sparse content |
| Author Metadata | `draft` | Actively filling pack files |
| Add Images / Assets | `draft` | Paths in `assets.json` / media drop |
| Validate | still `draft` until clean | `python -m publish validate` / Studio action |
| Preview | `draft` | Open generated or draft HTML locally |
| Generate | `draft` → consider `ready` | `build lesson` succeeds |
| Publish | `published` | Public site / YouTube go-live |

`publication.*` flags stay as fine-grained facts (website, youtube, recorded, edited).
Studio derives a **workflow stage** for display from status + warnings + build presence.

```
Create → Author → Assets → Validate → Preview → Generate → Publish
```

---

## Publishing workflow

```
Validate pack
    ↓ (must pass)
Build lesson HTML
    ↓
Build book (if book complete enough)
    ↓
Build site (home + bookshelf)
    ↓
Review locally
    ↓
Mark published / ship
```

Engine already fail-closes on invalid packs ([publishing_engine.md](publishing_engine.md)).

---

## Dashboard information model

### Project summary
- Pack count, by status (`planned` / `draft` / `ready` / `published`)
- Validation failure count
- Warning counts (hero, YouTube, compounds, gallery)
- Last build time (when recorded)

### Books
- List from `data/books/`
- Lessons present vs listed in `lesson_ids`
- Link to book page + build book action

### Lessons
- Rows: id, title, status, workflow stage, warnings, quick actions

### Validation
- Per-lesson pass/fail with messages

### Publishing
- Built output paths that exist on disk
- Unpublished but generated
- Missing YouTube IDs

### Recent activity
- In-memory / local log of Studio actions this session (v1)
- Later: append-only `.studio/activity.jsonl` (local, gitignored)

### Quick actions
- New Lesson · Validate · Preview · Build Lesson · Build Book · Build Site · Build All

---

## Command structure

### Web (primary)
Studio UI buttons POST to `/api/...` and run the same Python APIs as the CLI.

### CLI (scriptable twin)

```bash
.venv/bin/python -m publish create lesson_003
.venv/bin/python -m publish validate lesson_003
.venv/bin/python -m publish build lesson lesson_003
.venv/bin/python -m publish build book book_01
.venv/bin/python -m publish build site
.venv/bin/python -m publish build all
.venv/bin/python -m publish status
.venv/bin/python -m studio          # open dashboard
```

Web and CLI share `publish.*` — no duplicated business logic.

---

## Authoring Workspace (evolves with Studio)

Keep packs under `data/lessons/lesson_NNN/` for now (stable).  
Studio lesson detail page is the **virtual workspace** that surfaces:

- Pack files and counts
- Asset paths + missing media
- Validation
- Preview / build links
- Notes link (optional `author/notes.md` later)

Physical co-location (`author/`, `media/` beside `data/`) remains a later evolutionary move documented in [authoring_workspace.md](authoring_workspace.md) — not required to use Studio v1.

---

## Architecture (v1 — Option A)

```
studio/
  app.py           # stdlib HTTP server bootstrap
  handlers.py      # routes (framework-agnostic)
  httputil.py
  views.py         # Studio Jinja2 UI
  services.py      # → publish engine API
  templates/
  static/
publish/           # independent transformation layer (CLI + Studio)
```

See also [philosophy.md](philosophy.md).

---

## Recommendations for daily authoring

1. Start the day in **Studio dashboard**, not a file tree.
2. Work the **attention queue** (invalid → missing assets → drafts).
3. Never hand-edit `GENERATED` HTML; rebuild after metadata edits.
4. Keep YouTube IDs and heroes as Studio “publication readiness” signals.
5. Batch-migrate only after Studio makes Create→Validate→Build feel routine.
6. Add Studio activity log + media file existence checks before scaling to 50 lessons.

---

## Success criteria

The project feels like an integrated publishing system:

**Create or open → complete → validate → preview → build → publish**

guided by the dashboard, with CLI available for automation.
