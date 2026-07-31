# Lesson 002 proof — Phase A

**Date:** 2026-07-29  
**Result:** Pass — model is not a Lesson 001 special case.

## What was done

Authored `data/lessons/lesson_002/` using the **unchanged** Lesson 001 pack schema.
No architecture modifications.

| Pack file | Lesson 001 | Lesson 002 |
|---|---|---|
| kanji | 20 (一→明, H1–20) | 20 (唱→千, H21–40) |
| vocabulary (atoms) | 143 | 152 |
| phrases | 156 | 170 |
| compounds | 89 | 87 |
| gallery collections | 6 | 6 |
| youtube | unpublished | unpublished |

Validation:

```bash
python3 kml_v2/scripts/validate_metadata.py
# lesson_001 + lesson_002 → All checks passed.
```

## Experience

Authoring felt **natural**: same sources (CSV stories, production kanji rows, ambient vocab/compounds/gallery), same eight files, same field shapes. No schema gap forced a redesign.

## Genuine flaws?

None discovered that meet the high-change threshold. Optional tooling improvements (extractor script, authoring CLI) belong to **Phase B**, not schema change.

## Gate status

- Phase A (prove model): **complete**
- Bulk migration: still wait for Phase B tooling (recommended) then Phase C generation, then Phase D batches
- Metadata model: **ready for scale** once authoring tools exist
