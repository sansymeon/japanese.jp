# KML Curriculum Analytics

A completely separate, read-only analytics system for the KML Vocabulary
curriculum. It analyzes the published vocabulary lessons and generates
educational statistics that can be regenerated at any time as new lessons
are added.

**This project never modifies the master vocabulary database.**
`kml/data/vocabulary/kml_master_vocabulary.v1.json` is opened read-only,
used only as an enrichment lookup (POS / themes / JLPT where available),
and its SHA-256 is recorded in every output file for provenance.

## Layout

```
kml/analytics/
├── README.md                 this file
├── analytics_config.json     all paths, frequency bands, output names
├── scripts/
│   ├── analyze_curriculum.py         the analytics engine (rerun any time)
│   └── build_frequency_reference.py  one-time builder for the frequency list
├── reference/                vendored reference datasets (read-only inputs)
│   ├── jlpt_n5.csv … jlpt_n1.csv     JLPT word lists (elzup/jlpt-word-list)
│   ├── ja_opensubtitles_full.txt     raw OpenSubtitles 2018 ja word counts
│   ├── ja_spoken_frequency_lemmas.tsv  lemmatized spoken-frequency ranks
│   └── joyo_kanji.csv                joyo kanji table (2,136 characters)
└── output/                   GENERATED FILES — never edit, never canonical
    ├── kml_curriculum_analysis.json
    ├── kml_jlpt_statistics.json
    ├── kml_frequency_statistics.json
    ├── kml_channel_statistics.json
    └── CURRICULUM_REPORT.md
```

## Running

```bash
cd /home/sjnelson/japanese.jp
.venv/bin/python kml/analytics/scripts/analyze_curriculum.py
.venv/bin/python kml/analytics/scripts/analyze_channel_learning.py
```

### Pre-deploy flow

```
create lesson (or any non-output change)
    ↓
git push to main
    ↓
GitHub Action pre-deploy-analytics.yml runs analyze_channel_learning.py
    ↓
new JSON under kml/analytics/output/ (committed back to main when changed)
    ↓
Netlify deploy (homepage + dashboard serve the fresh JSON)
```

Locally (same script the Action runs):

```bash
./scripts/pre-deploy.sh
```

There is **no daily cron**, Netlify scheduled function, or build-time stats step.
Stats refresh only when `analyze_channel_learning.py` runs (via
`./scripts/pre-deploy.sh` or the GitHub Action) and the resulting JSON is on
`main`.

On **every push to `main`** that is not limited to `kml/analytics/output/**`,
GitHub Actions runs `.github/workflows/pre-deploy-analytics.yml`, regenerates
outputs, and commits them when they change. `paths-ignore` on `output/**`
avoids an Action loop; the bot commit is intentionally *not* marked
`[skip ci]` so Netlify still deploys the fresh JSON. Manual runs: Actions →
“Pre-deploy analytics” → Run workflow.

The homepage and dashboard both load
`kml/analytics/output/kml_channel_learning.json` (not the local `dashboard/data`
symlink, which deploy hosts often do not expose).

Escape hatch: `SKIP_ANALYTICS=1 ./scripts/pre-deploy.sh`

`analyze_curriculum.py` covers the Japanese Vocabulary series only.
Lessons are discovered with the glob
`kml/tools/ambient/collections/vocabulary/vocabulary_*.json`, so **adding
Lesson 13 (or 130) requires no code changes** — publish the lesson JSON and
rerun the script. Everything in `output/` is rebuilt from scratch on every
run.

`analyze_channel_learning.py` treats **every playlist as an independent
learning path** and builds one **global channel path** (educational order).
After every video it computes cumulative unique vocabulary/kanji, JLPT word
and kanji coverage, Joyo coverage, spoken-frequency band coverage, **exposure
depth** (how many distinct videos each item appears in), **learning value per
video** (new vs reinforced + JLPT/spoken gains + educational role), and review
opportunities — then reports the exact lesson where each of
10% / 25% / 50% / 75% / 90% / 95% / 100% is crossed.

Exposure bands (per distinct video):

| Encounters | Stage |
|---|---|
| 1 | Introduced |
| 2 | Reinforced |
| 3–5 | Becoming familiar |
| 6–9 | Strong recognition |
| 10+ | Core knowledge |

Outputs:

- `output/kml_channel_learning.json`
- `output/CHANNEL_LEARNING_REPORT.md`

### Curriculum Dashboard (v1.0)

Interactive mission control UI (read-only; fetches analytics JSON only):

```bash
cd kml/analytics/dashboard && ./serve.sh
# → http://localhost:8787/dashboard/
```

See `kml/analytics/dashboard/README.md`.

Requires the repo venv (`.venv`), which provides `fugashi` + UniDic for
morphological analysis. Everything else is the standard library.

## Data sources

| Input | Role | Access |
|---|---|---|
| `vocabulary_*.json` lesson files | primary corpus (compound steps + Beautiful Words) | read-only |
| `kml_master_vocabulary.v1.json` | enrichment lookup (POS, themes, JLPT) when a word exists there | read-only |
| `reference/jlpt_n*.csv` | JLPT N5–N1 classification | read-only |
| `reference/ja_spoken_frequency_lemmas.tsv` | modern spoken Japanese frequency ranks | read-only |
| `reference/joyo_kanji.csv` | joyo vs non-joyo classification | read-only |

### Notes on methodology

- **JLPT levels**: a word is assigned the easiest level that lists it
  (checked N5 → N1). Surface-form match first; kana-only words also match
  by reading. Words in no list are `outside_jlpt`. The master database's
  own `jlpt` field, when present, takes precedence.
- **Spoken frequency**: the reference list is the OpenSubtitles 2018
  Japanese corpus (film/TV dialogue — the best freely available proxy for
  modern spoken Japanese), lemmatized to dictionary forms with UniDic and
  re-ranked. Band coverage is reported two ways: what share of the
  curriculum falls inside the band, and what share of the band the
  curriculum covers. To rebuild this list from the raw counts, run
  `build_frequency_reference.py`.
- **Parts of speech**: master-database POS wins when available; otherwise
  UniDic tokenization with heuristics for multi-token compounds.
- **Themes**: master-database themes win when available; otherwise a word
  is classified by keyword-matching its English gloss against the theme
  keyword table in `analyze_curriculum.py` (shopping, food, travel,
  transportation, school, family, home, work, nature, daily life,
  greetings). Unmatched words are `general`. A word may hold several themes.
- **Loanwords**: identified via UniDic word-origin (*goshu*) class `外`
  plus a katakana-surface check. Per-word source languages are not present
  in the current data, so the wago / kango / gairaigo breakdown is reported
  instead.
- **Spaced-repetition opportunities**: words introduced at least
  `review_gap_lessons` (default 3, see config) lessons ago that have never
  reappeared.

## Design guarantees

- **Read-only** — the script refuses to write anywhere except
  `kml/analytics/output/` (guarded in code) and opens all inputs read-only.
- **Regeneratable** — outputs carry no state; delete `output/` and rerun.
- **Independent of production** — nothing in the site, lesson pipeline, or
  master database references these files; they must never become the
  canonical vocabulary source.
- **Future-proof** — lesson discovery is glob-based; frequency bands,
  paths, and the review gap live in `analytics_config.json`.
- **Traceable** — every output embeds a timestamp and the SHA-256 (first 12
  hex chars) of every input file it was generated from.

## Output files

- `kml_curriculum_analysis.json` — the superset: overall stats, growth,
  JLPT, frequency, POS, themes, kanji, loanwords, reading difficulty,
  reinforcement, cumulative progress after every lesson, plus a full
  per-word index with all derived attributes.
- `kml_jlpt_statistics.json` — JLPT distribution, cumulative coverage by
  lesson, and word lists per level.
- `kml_frequency_statistics.json` — coverage of the top 500 / 1,000 /
  2,000 / 5,000 spoken words, cumulative by lesson, plus per-word ranks.
- `kml_channel_statistics.json` — publication-level summary: lessons
  published, runtimes, words per lesson, and the Beautiful Words list.
- `CURRICULUM_REPORT.md` — the human-readable report with tables and
  charts.
