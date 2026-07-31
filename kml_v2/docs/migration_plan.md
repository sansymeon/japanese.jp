# KML Website V2 — Migration Plan

## Architecture Freeze v1

The platform is **frozen** as Version 1.
See [architecture_freeze_v1.md](architecture_freeze_v1.md).

Prioritize authoring experience, educational content, and tooling.
Architectural changes only when real use shows a hard limitation.

---

## Strategy

| Phase | Goal | Status |
|---|---|---|
| A — Prove model | Lesson 002 on locked schema | **Done** |
| B — Publishing Engine | metadata → Jinja2 → HTML + CLI | **Done (v1)** |
| C — Authoring Workspace / Studio | Local web control center | **Done (v1 web app)** |
| D — Dashboard depth | Activity log, queue polish | Ongoing via Studio |
| E — Batch migration | 1–5, 6–10, 11–20… | After Studio feels routine |

---

## Publishing Engine (B) + Studio (C)

```bash
cd kml_v2
.venv/bin/python -m publish build all
.venv/bin/python -m publish status
.venv/bin/python -m studio          # http://127.0.0.1:8787/
```

See [publishing_engine.md](publishing_engine.md) and [kml_studio.md](kml_studio.md).

---

## Gates

```
001 + 002 packs valid
    → Engine renders both   [done]
    → Authoring workspace / daily CLI comfort (C)
    → Batch migration (E)
```

Do not migrate Lessons 3–50 in one pass. Prefer:

1. Lessons 1–5 → review  
2. Lessons 6–10 → review  
3. Lessons 11–20 → …

---

## Validation

```bash
.venv/bin/python -m publish validate lesson_001
.venv/bin/python -m publish build lesson lesson_001   # fails if invalid
```
