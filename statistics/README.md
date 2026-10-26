# Statistics

Public statistics for Kanji・Music・Landscape.

The page describes published KML materials across the website and YouTube
collections, with curriculum coverage kept separate from the rest of the
ecosystem.

## Sections

1. **Interesting Statistics** — library scale + published curriculum + YouTube
2. **Permanent Library** — designed KML resources (3,096 one-per-kanji items,
   plus full vocabulary / compound / component totals)
3. **Published Curriculum** — planned lessons whose pages, covers, and study images are present
4. **Curriculum Coverage** — JLPT / grades / Jōyō from the completed planned lessons only
5. **Learning Resources** — lesson-sequence totals, then other site series
6. **Media Library** — exhibitions, ambient collections, audio, YouTube channel

## Refresh counts

```bash
python3 scripts/build_project_stats.py
```

Writes `statistics/data/project_stats.json`.

### Permanent library

- **Kanji / verses / stroke-order pages (3,096)** — one resource per kanji in
  the designed master collection
- **Vocabulary / compounds / components** — counted from production
  collections; not assumed to be 3,094

### Published curriculum

**Lessons Completed** counts planned lessons 1–153 whose production HTML,
JPEG cover, and study images named in that HTML are all present. Lesson 154
is the encore and is not part of that count. The figure is calculated by
`scripts/build_project_stats.py` from the files in the repository.

Gallery videos, stroke-order recordings, and compound videos are not included.
A complete lesson page does not mean those films have been produced.

### YouTube

The public YouTube figure is the live `@ambientkanji` content library
(847 videos, 807 public, 189 playlists, as of 2026-10-07). Local `.mp4`
files and the 222-film learning-path analytics subset are not the channel
library.
