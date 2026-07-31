# Architecture Freeze — Version 1

**Status:** FROZEN  
**Effective:** 2026-07-30  
**Scope:** KML V2 core platform under `kml_v2/`

## Statement

The core architecture is considered **stable**:

- Metadata model (lesson packs; Lesson 001 reference)
- Publishing Engine (Python + Jinja2; packs → HTML)
- Studio interfaces (stdlib HTTP + Jinja2 local web app; CLI twin)
- Generated site pipeline (lessons, books, bookshelf, homepage)

Future work should prioritize:

1. **Authoring experience** (Studio UX, workflows, feedback)
2. **Educational content** (curriculum packs, media references)
3. **Tooling** (reports, batch helpers, previews)

Architectural changes should be **exceptional** and justified by **demonstrated limitations during real use** — not by speculative redesign.

## What is frozen

| Area | Canonical docs / code |
|---|---|
| Philosophy / layers | [philosophy.md](philosophy.md) |
| Pack schema & principles | [architecture_decisions.md](architecture_decisions.md) |
| Publishing Engine | [publishing_engine.md](publishing_engine.md), `publish/` |
| KML Studio | [kml_studio.md](kml_studio.md), `studio/` |
| Site templates (engine) | `templates/` |
| Studio UI | `studio/templates/`, `studio/static/` |

## Change bar (after freeze)

A structural change may proceed only if all of the following hold:

1. It solves a problem observed while authoring or publishing real lessons.
2. It benefits the curriculum broadly (not a one-off convenience).
3. It cannot reasonably be solved inside Studio UX, tooling, or templates.
4. It preserves Lesson 001 pack compatibility or includes a clear migration path.

Otherwise: keep the V1 shape; improve the author path.

## Allowed without “architecture change”

- New Studio screens, clearer queues, activity logs
- Richer generated page presentation (same data objects)
- Additional CLI/Studio reports and batch helpers
- Authoring more lesson packs and media path references
- Docs and workflow polish

## Not the default path

- New web frameworks for Studio
- Pack schema rewrites
- Shared kanji registry extraction (still evolutionary, only when pain is real)
- Hand-authored HTML as source of truth

## Related

- [architecture_decisions.md](architecture_decisions.md) — STABLE BASELINE  
- [migration_plan.md](migration_plan.md) — batch content after tooling feels routine  
- [core_principles.md](core_principles.md) — metadata-first principles  
