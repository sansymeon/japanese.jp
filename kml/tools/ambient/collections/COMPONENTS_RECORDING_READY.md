# Kanji Components — recording ready (L1–30)

JSON built from **lesson HTML** (canonical) + `data/kanji_components_catalog.json` (labels/intros).
Source policy: `kml/data/kanji/KML_COMPONENT_SOURCE_POLICY.md`.
Recorder: `scripts/record_lesson_components.py --lesson N` (N = 1–30).
Output: `collections/lesson_NN/components_lesson_NN.mp4`

Rebuild HTML DB then components:

```bash
cd kml && python3 scripts/build_kml_component_database.py
cd tools/ambient && python3 scripts/build_kanji_components.py
```

## Queue chain

1. `run_kanji_components_l01_05_tonight` — L1–5 DONE
2. `run_kanji_components_l06_08_after_l01_05.sh` — L6–8 recording (on L8)
3. `run_kanji_components_l09_10_after_l06_08.sh` — **queued**: Phase 1 reviewed L9–10 (after L6–8 DONE)
4. `run_kanji_components_l06_10_after_l01_05.sh` — older L6–10 batch (superseded)
5. `run_kanji_components_l11_15_after_l06_10.sh` — after L6–10 (**prepared; start when ready**)
6. `run_kanji_components_l16_20_after_l11_15.sh` — after L11–15 (**prepared; start when ready**)
7. `run_kanji_components_l21_25_after_l16_20.sh` — after L16–20 (**prepared; start when ready**)
8. `run_kanji_components_l26_30_after_l21_25.sh` — after L21–25 (**prepared; start when ready**)

## L6–8 verified (Phase 1)

- Review: 20/20 ok each (H/V only). Spot checks: 石 = 厂|口, 原 = 厂|泉.
- Ambient JSON rebuilt from lesson HTML (`source=lesson_html`).
- Log: `record_kanji_components_l06_08_after_l01_05.log`.

## L9–10 verified (Phase 1)

- Review: 20/20 ok each (H/V only). 涯/均 nested H/V; 尚 = anchor.
- Recording waits on L6–8; log: `record_kanji_components_l09_10_after_l06_08.log`.

## L11–15 verified (Phase 1)

- Review: 20/20 ok each (H/V only). 黙/然 tops wrapped `stack-horizontal`; 膜/漠 link to 莫 (L113).
- Ambient JSON rebuilt from lesson HTML (`source=lesson_html`).
- Recording DONE 2026-07-31T08:09:14+09:00 — log: `record_kanji_components_l11_15_after_l06_10.log`.

| Lesson | Scenes | New Component intros |
|--------|--------|----------------------|
| 11 | 20 | — |
| 12 | 21 | 1 |
| 13 | 22 | 2 |
| 14 | 20 | — |
| 15 | 22 | 2 |

## L16–20 verified (Phase 1)

- Review: 20/20 ok each (H/V only). Fixed 落/冠 closings; 塾/熟/警 tops; 栽/載 → nested H/V; 茂 → 戊.
- Ambient JSON rebuilt from lesson HTML.
- Recording started 2026-07-31 — log: `record_kanji_components_l16_20_after_l11_15.log`.

| Lesson | Scenes | New Component intros |
|--------|--------|----------------------|
| 16 | 22 | 2 |
| 17 | 22 | 2 |
| 18 | 22 | 2 |
| 19 | 21 | 1 |
| 20 | 21 | 1 |

## L26–30 JSON (recording later)

| Lesson | Scenes | New Component intros |
|--------|--------|----------------------|
| 26 | 24 | mist, double back, ice, muzzle |
| 27 | 21 | devil |
| 28 | 22 | porter, scorpion |
| 29 | 22 | eel, pig |
| 30 | 22 | lucky pig, turkey |

Removed intros (expanded instead): turbulence (荒), fin (鏡/境).

## Start later batches

```bash
cd kml/tools/ambient
nohup bash scripts/run_kanji_components_l11_15_after_l06_10.sh \
  > /tmp/kanji_components_l11_15.nohup.out 2>&1 &
nohup bash scripts/run_kanji_components_l16_20_after_l11_15.sh \
  > /tmp/kanji_components_l16_20.nohup.out 2>&1 &
nohup bash scripts/run_kanji_components_l21_25_after_l16_20.sh \
  > /tmp/kanji_components_l21_25.nohup.out 2>&1 &
nohup bash scripts/run_kanji_components_l26_30_after_l21_25.sh \
  > /tmp/kanji_components_l26_30.nohup.out 2>&1 &
```

Or record a single lesson:

```bash
python3 scripts/record_lesson_components.py --lesson 26 --port 9826
```
