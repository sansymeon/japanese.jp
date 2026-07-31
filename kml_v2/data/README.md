# KML V2 metadata

> Governing rules: [Core Development Principles](../docs/core_principles.md)  
> Locked decisions: [Architecture Decisions](../docs/architecture_decisions.md)

## Approved lesson pack (reference: `lesson_001`)

```
data/lessons/lesson_NNN/
  lesson.json
  kanji.json          # required — characters are first-class
  vocabulary.json     # atoms
  phrases.json        # permanent
  compounds.json      # permanent
  gallery.json
  youtube.json
  assets.json
```

One fact → one file. Consumers reference; they do not duplicate.

## Validate before authoring more lessons

```bash
cd kml_v2
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements-validate.txt
.venv/bin/python scripts/validate_metadata.py
```
