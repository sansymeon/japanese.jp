# Lesson Art Gallery — prototypes

Short-form lesson galleries (≈2.5–3 min chamber music), separate from long Ambient Exhibitions.

## Current prototype settings (v2)

- Dissolves: **3.75s** (artwork gently fades into the next)
- Ordinary scenes: **still** (no Ken Burns)
- Panorama: GPU **translate3d** walk, soft ease-in/out, ~42s allocation
- Capture: **3840×2160 → Lanczos 1080p** for smoother motion
- Crest: understated gold, within musical ending
- No text / keyword / kanji / verse overlays

## Preview

- Review sheet: [`tools/tmp/lesson_art_gallery_prototypes/index.html`](../../tmp/lesson_art_gallery_prototypes/index.html)
- Player (with ambient server): `exhibition.html?collection=proto_lesson_art_gallery_34` (also `_32`, `_31_panorama`)

## Build / record

```bash
cd kml/tools/ambient
python3 scripts/build_lesson_art_gallery_prototypes.py
.venv/bin/python scripts/record_lesson_art_gallery_prototypes.py
# or one: ... --only proto_lesson_art_gallery_34
```

MP4s land in `collections/prototypes/proto_lesson_art_gallery_*.mp4`.

Do not propagate to other lessons until these prototypes are approved.
