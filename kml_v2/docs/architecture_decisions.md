# Architecture Decision Record — Lesson Pack Reference Model

**Status:** STABLE BASELINE · **Architecture Freeze v1** ([architecture_freeze_v1.md](architecture_freeze_v1.md))  
**Approved:** 2026-07-29 · **Frozen:** 2026-07-30  
**Reference pack:** `data/lessons/lesson_001/` (canonical)  
**Supersedes:** provisional Phase 2/3 pack experiments where they conflict

The Lesson 001 reference model is approved and the wider V1 platform
(metadata, Publishing Engine, Studio, generated site pipeline) is **frozen**.
Future work prioritizes authoring experience, educational content, and tooling.
Architectural changes require demonstrated limitations in real use.

---

## Stable decisions

1. **Lesson packs** remain the fundamental authoring unit.
2. **`kanji.json` is required** and represents the primary educational entity.
3. **`compounds.json`** is a permanent pack file.
4. **`phrases.json`** is a permanent pack file.
5. **`vocabulary.json`** contains vocabulary **atoms only**.
6. Each fact exists in **one authoritative location**.
7. Consumers **reference** metadata rather than duplicate it.
8. Lessons **reference** entities; entities **own** educational data.
9. Shared entity libraries (e.g. `data/kanji/`) are a **future evolutionary step**,
   not a current requirement.

These principles guide all future development.

---

## Pack shape

Self-contained under `data/lessons/lesson_NNN/`:

```
lesson.json
kanji.json          # required — primary educational entity
vocabulary.json     # atoms only
phrases.json        # permanent
compounds.json      # permanent
gallery.json
youtube.json
assets.json
```

A pack must be understandable without hunting across the repository.

### Kanji

The **character** is the fundamental educational entity. Where appropriate it owns
keyword, verse, components/primitives, readings, study/hero paths, and related
metadata. Packs remain the authoring surface today; a shared registry may come later
so Beyond Jōyō / review / search can reference the same characters without copying.

### One fact → one location

| Fact | Authority |
|---|---|
| Lesson title / status / book | `lesson.json` |
| Kanji verses / keyword / readings | `kanji.json` |
| Study images (per character) | `kanji.json` item assets |
| Lesson cover / layout roots | `assets.json` |
| YouTube id / chapters | `youtube.json` |
| Compounds | `compounds.json` |
| Vocab atoms | `vocabulary.json` |
| Phrases | `phrases.json` |

---

## Validation discipline

Lesson 001’s successful validation confirmed the architecture can hold real curriculum.

Schema/structural validation is part of the development workflow and **must run
before approving any new lesson pack**.

```bash
python3 kml_v2/scripts/validate_metadata.py
python3 kml_v2/scripts/validate_metadata.py --lesson lesson_001
# optional Draft 2020-12:
#   pip install -r kml_v2/scripts/requirements-validate.txt
```

Maintain this discipline throughout migration.

---

## Lesson 002 gate — **passed**

Lesson 002 proved Lesson 001 was not a special case ([lesson_002_proof.md](lesson_002_proof.md)).
Authored on the **unchanged** architecture; validation clean.

Further lessons should use this pack shape. Structural change still needs a high threshold.

## Bulk migration gate

Bulk migration remains **intentionally sequenced**: Phase B tooling → Phase C generation → Phase D batches.
Do not migrate Lessons 3–50 in one pass.

---

## Authoring Workspace (next architectural phase)

See [authoring_workspace.md](authoring_workspace.md).

Purpose: improve **content creation**, not the generated website.
The publishing pipeline continues to consume **structured metadata only**.
The authoring layer organizes lesson resources in one discoverable place,
independent of presentation and build logic.

---

## Long-term vision

KML V2 is a metadata-driven educational publishing platform centered on reusable
educational entities and lesson-centered authoring — not a collection of HTML pages.

Lesson 001 is the **canonical reference implementation**. Future work focuses on
consistency, tooling, and efficient authoring rather than structural redesign.
