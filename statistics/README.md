# Statistics

Public statistics for Kanji・Music・Landscape.

The page describes the **published** KML collection — not the private
development repository. Visitors see the project grow as lessons are completed.

## Sections

1. **Interesting Statistics** — library scope + key published progress
2. **Permanent Library** — full collection size (Kanji Collection, Planned Lessons)
3. **Published Progress** — derived from completed lessons
4. **Curriculum Coverage** — JLPT / grades / Jōyō from published kanji only
5. **Learning Resources** — vocabulary, compounds, readings, components, strokes
6. **Media Library** — published exhibitions, ambient films, videos, audio

## Refresh counts

```bash
python3 scripts/build_project_stats.py
```

Writes `statistics/data/project_stats.json`.

### Permanent (occasional updates)

- **Kanji Collection (3,094)** — complete KML library scope
- **Planned Lessons (153)** — full lesson curriculum

### Published progress (automatic)

**Lessons Completed** counts fully illustrated lessons. From that set the
builder derives kanji, verses, illustrations, components, vocabulary,
compounds, readings, and educational coverage. Future-lesson material is
excluded until those lessons are completed.
