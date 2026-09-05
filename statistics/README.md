# Statistics

Public statistics for Kanji・Music・Landscape.

The page describes published KML materials across the website and YouTube
collections, with curriculum coverage kept separate from the rest of the
ecosystem.

## Sections

1. **Interesting Statistics** — library scale + published curriculum + YouTube
2. **Permanent Library** — designed KML resources (3,094 one-per-kanji items,
   plus full vocabulary / compound / component totals)
3. **Published Curriculum** — completed lesson sequence (currently 1–50)
4. **Curriculum Coverage** — JLPT / grades / Jōyō from Lessons 1–50 only
5. **Learning Resources** — lesson-sequence totals, then other site series
6. **Media Library** — exhibitions, ambient collections, audio, YouTube channel

## Refresh counts

```bash
python3 scripts/build_project_stats.py
```

Writes `statistics/data/project_stats.json`.

### Permanent library

- **Kanji / verses / stroke-order pages (3,094)** — one resource per kanji in
  the designed master collection
- **Vocabulary / compounds / components** — counted from production
  collections; not assumed to be 3,094

### Published curriculum

**Lessons Completed** is the published curriculum range (currently lessons
1–50). A lesson is complete when its production HTML exists.

### YouTube

The public YouTube figure is the live `@ambientkanji` channel total
(551 as of 2026-09-05). Local `.mp4` files and the 222-film learning-path
analytics subset are not the channel library.
