# KML Component Consistency Audit

Generated after the Book 1 first-pass (Lessons 1–153).  
Policy: consistency only — no structural redesign of approved HTML.

Related: `KML_COMPONENT_LATER_REVIEW.md`, `KML_COMPONENT_SOURCE_POLICY.md`.

## Scope checked

1. Catalog: one canonical label per glyph; introductions vs labels
2. Reuse: same glyph → same catalog entry across the curriculum
3. Near-duplicate / shared-label definitions
4. Markup that blocks HTML → database parse
5. Derived rebuild from finalized HTML

## Markup (fixed or deferred)

| Item | Status |
|------|--------|
| L42 **唆** / **峠** — unclosed `component-box` (missing final `</div>`) | **Fixed** — boxes now parse; structures unchanged |
| L149 **轁** (U+8F61) curriculum glyph check | Deferred — see later-review note |
| Lessons 1–24 residual legacy layout classes (`anchor-box`, `kanji-left`/`kanji-right`, `kanji-composite`) | **76 entries, all ≤ L24** — Phase-1 early-lesson cleanup backlog; none in L41–153 |

## Catalog health

- **Introductions:** no duplicate intro glyphs; intro labels match `componentLabels`
- **Normalize map:** aliases (`´`→`丶`, `⻌`→`辶`, etc.) are one-way; source glyphs need not carry their own labels
- **Intentional shared names** (radical / variant pairs — OK for now):  
  `人`/`亻`, `亠`/`⼇`, `勹`/`⼓`, `𠂊`/`⺈`, `戉`/`戊`, `彳`/`亍`, `阜`/`阝`, `乂`/`㐅`, `廿`/`卄`, and simp/trad pairs (`寿`/`壽`, `龍`/`龙`, `鬱`/`欝`, …)

## Label collisions needing editorial decision

Same English label on **distinct** glyphs (not intentional radical pairs).  
Structures stay as-is; rename the secondary label when approved.

| Shared label | Glyphs | Notes |
|--------------|--------|-------|
| companion | 尞, 朋 | 朋 is the kanji “companion”; 尞 is the L93 phonetic (often “pup tent”) |
| cover | 冖, 冡 | 冖 is intro’d; 冡 only in 蒙 |
| dancing legs | 舛, 亦 | 亦 is intro’d L95; 舛 used earlier (瞬, 傑, …) |
| furthermore | 尤, 尚 | 尚 is a lesson kanji keyword |
| hill | 丘, 岡 | both lesson keywords / families |
| home | 乇, 宅 | 宅 is lesson kanji; 乇 is the phonetic in 宅/託 |
| meeting | 𠆢, 会 | 会 is lesson kanji; 𠆢 in 命/令 |
| porter | 壬, 襄 | 壬 is intro’d; 襄 is the L83 family phonetic |
| stamp | 卩, 印 | 印 is lesson kanji |
| swift | 卂, 疌 | 卂 intro’d (迅); 疌 in 捷 |
| warrior | 戎, 武 | 戎 unused in current `partsFlat`; 武 is lesson-related |
| wheat | 禾, 麦 | 禾 is intro’d; 麦 is lesson kanji |
| wind | 几, 風, 风 | 几 is intro’d; 風 is lesson kanji; 风 unused |

**Action:** assign a unique label to each secondary glyph (keep intro / primary names stable). Do not change HTML until labels are approved.

## Duplicate lesson kanji (informational)

L153 re-teaches units already present earlier (`子`, `午`, `未`, `申`, `酉`, `亥`, `此`, …).  
Database flags `duplicate_kanji_entry` — expected for the zodiac / review lesson; not a structure bug.

## Rebuild

After this audit snapshot:

1. `python3 scripts/build_kml_component_database.py`
2. Rebuild ambient `lesson_XX_components.json` (+ prototypes) for all lessons from HTML

Target: `partSourcesUsed: ['html']`, `v4cFallback: 0`, `absent` only if truly missing boxes.
