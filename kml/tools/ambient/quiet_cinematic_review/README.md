# Quiet Cinematic Japan — Lessons 21–30 (Draft Review)

Temporary curation workspace. **Not a finished exhibition.**

Split like earlier blocks (1–5 / 6–10):

| Block | Draft candidates | Target final | Review |
|---|---:|---:|---|
| Lessons 21–25 | 33 | ~30 | [`index.html?block=21-25`](./index.html?block=21-25) |
| Lessons 26–30 | 45 | ~30 | [`index.html?block=26-30`](./index.html?block=26-30) |

## Theme

**Quiet Cinematic Japan** — scenes that feel like moments from a beautifully filmed Japanese story.

Priorities: immediately feels like Japan → panoramic landscape / architecture → quiet atmosphere → linger-worthy frames. People appear only when they serve mood (traveler, temple visitor, figure in mist), never as portraits.

## Layout

- `index.html` — responsive review grid (drag/drop order, remove, lightbox)
- `data/lessons_21_25_draft.json` — candidate pool for 21–25
- `data/lessons_26_30_draft.json` — candidate pool for 26–30
- `css/` · `js/` — review UI

Images resolve from `kml/assets/studies/` via `assetsBase`.

## Built exhibition (21–25)

Collection: `collections/lesson_21/lessons_21_25_quiet_cinematic.json`

```bash
cd kml/tools/ambient
.venv/bin/python scripts/build_lessons_21_25_quiet_cinematic.py
.venv/bin/python scripts/record_lessons_21_25_quiet_cinematic.py   # ~56 min
```

Preview: `exhibition.html?collection=lessons_21_25_quiet_cinematic`  
MP4: `extended_exhibitions/lessons_21_25_quiet_cinematic.mp4`

## How to review

1. Open the review page for a block (serve from `kml/tools/ambient/` or open via local static server).
2. Remove weak or redundant scenes; drag to set exhibition order.
3. **Export order** or **Download JSON** when the shortlist feels close.
4. Later: promote the edited list into a collection JSON for `exhibition.html`.

Edits persist in browser `localStorage` until Reset.

## Notes

- Uneven lesson counts are intentional — strength over equal representation.
- Draft size is ~1.5× the intended finished exhibition so refinement has room.
