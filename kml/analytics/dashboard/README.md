# KML Curriculum Dashboard v1.0

Self-contained, read-only visualization of KML curriculum analytics.

**Mission control** for curriculum design, QA, and progress tracking.

## Rules

- Reads **only** generated analytics JSON (`../output/*.json`)
- Never reads production lesson files
- Never modifies analytics or production data
- Updates automatically when analytics are regenerated (live fetch + 30s poll)

## Run

```bash
cd kml/analytics/dashboard
./serve.sh          # http://localhost:8787/dashboard/
# or: ./serve.sh 9000
```

Open [http://localhost:8787/dashboard/](http://localhost:8787/dashboard/).

The UI fetches `../output/kml_channel_learning.json` (same path as production).
`serve.sh` serves from `kml/analytics/` so that relative URL resolves locally.
`./data` remains a symlink to `../output` for convenience only — deploy hosts
often do not expose that symlink. Production also has a Netlify rewrite in
`/_redirects` so `/kml/analytics/dashboard/data/*` maps to `/output/*`.

Regenerate data anytime:

```bash
./scripts/pre-deploy.sh
# or: .venv/bin/python kml/analytics/scripts/analyze_channel_learning.py
```

Preferred release flow: create lesson → push to `main` → GitHub Action
`.github/workflows/pre-deploy-analytics.yml` regenerates JSON and commits it →
Netlify deploy. There is no daily cron; stats update on each qualifying `main`
push (or a manual workflow run). See `kml/analytics/README.md`.

The dashboard reloads the new `generated_at` timestamp without a rebuild.

## Data source

Primary: `kml/analytics/output/kml_channel_learning.json` (schema v4+)

The UI tolerates future fields; missing optional sections degrade gracefully.

## Features

- Summary cards
- Curriculum growth charts (hover = lesson / playlist / new / reinforced)
- Learning-value timeline (coloured by educational role)
- Playlist overview cards
- Exposure-depth stacks + donuts
- JLPT coverage + average encounters
- Spoken-frequency growth
- Heat maps (playlist × JLPT / frequency / value / roles)
- Milestones
- Search (kanji / vocabulary / lesson / playlist)
- Filters (playlist, JLPT, type, role, lesson)
- Export: JSON, CSV, Markdown, PNG (chart), PDF (print)
- Light / dark mode

## Roadmap

| Version | Focus |
|---|---|
| **1.0** | At-a-glance curriculum mission control (this) |
| **2.0** | Historical snapshots · growth between releases |
| **3.0** | Public demonstration dashboard |
| **4.0** | Student personal learning tracker |

## Architecture

```
kml/analytics/dashboard/
  index.html
  css/dashboard.css
  js/dashboard.js
  serve.sh
  README.md
```

Pure static files. Chart.js is loaded from a CDN for charts only.
