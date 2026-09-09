# KML Spoken Japanese — Foundation Vocabulary (F1–F6)

Internal course name: **Foundation Vocabulary**.
Learner-facing entrance: **I need help with vocabulary**.

Six lessons of **25 target items + 1 Beautiful Word**, same exhibition format as
Japanese Vocabulary Lessons 1–22. Collection IDs are `vocabulary_f01` …
`vocabulary_f06` so they never collide with `vocabulary_01`–`vocabulary_22`.

Presentation is **vocabulary in context**: after a target headword, the
exhibition may show a short, familiar phrase. Only `coverage: "target"`
steps count as taught. `coverage: "exposure"` is scaffolding (particles,
supporting words, Start Here lyrics) and does not receive curriculum credit.
A target-linked exposure may omit the lemma entirely when a natural reply
or contrast should not force the word into the Japanese.

Context expansions live in `foundation_context.py`. Locked headwords and
sequence stay in `foundation_module.json`. Each expansion is a valid
stopping point; later lines are invitations. The target stays
typographically prominent (bold) inside context. Learners may turn
readings on for kanji.

The **interactive JSON exhibition is the primary Foundation experience**.
Learner-controlled progression, optional furigana, arbitrary stopping
points, and later Ask ChatGPT Sensei all depend on live JSON rather than
MP4. Recording scripts stay in the repo for possible YouTube Shorts or
promotional excerpts; recording F1–F6 is not the primary delivery plan.

Foundation may **preview** useful Japanese (な-adjectives, 〜そう, 〜たい,
〜ましょう, て-form expressions, あります / います, counters, time,
natural particles, casual and polite conversation). Preview is not taught
merely because it appears. The same forms can return later as explicit
targets. This is intentional recycling, not a requirement to cram grammar
into every item.

Governing principle: **the bold target tells the learner what they are
responsible for. Everything else is an invitation.** Foundation does not
protect beginners from unseen Japanese.

Existing Lessons 1–22 are not renumbered. Pathway:

> I need help with vocabulary → F1–F6 → Vocabulary Lesson 1 onward

Hiragana is **not** a prerequisite. Start Here words appear as reviews;
a few items return later as kanji in Lessons 1–22 (reunions, not replacements).

## The lessons

| Lesson | Collection | Arc | Beautiful Word | Proverb |
|---|---|---|---|---|
| F1 | `vocabulary_f01` | わたしと あなた | 言の葉 | 礼に始まり礼に終わる |
| F2 | `vocabulary_f02` | うちの ひと | 団欒 | 子は宝 |
| F3 | `vocabulary_f03` | へやの なか | 灯火 | 住めば都 |
| F4 | `vocabulary_f04` | まちへ いく | 道草 | 待てば海路の日和あり |
| F5 | `vocabulary_f05` | ごはんを たべる | 湯気 | 腹八分目 |
| F6 | `vocabulary_f06` | そらと かぜ | 空模様 | 明日は明日の風が吹く |

Soundtrack: `kml/tools/ambient/audio/vocabulary_f1_series.mp3` for all of F1–F6.
Do not loop. Fade the bed when the lesson content ends, then 漢 crest.

## Rebuild

```bash
python3 kml/data/vocabulary/modules/foundation/build_foundation_module.py
```

Preview:

```
kml/tools/ambient/exhibition.html?collection=vocabulary_f01
```

Development review (not public). Rebuilds with the Foundation builder:

```
kml/tools/tmp/foundation_f1_f6_review/index.html
```

Public entrance: `/kml/` → Vocabulary → `/kml/vocabulary/`.

## Pause → Ask ChatGPT Sensei

Foundation live exhibitions show a quiet three-slot bar:

* **Readings** on the left (independently toggleable, including while paused)
* **Pause** in the center, which becomes **Resume** while paused
* **Ask ChatGPT Sensei** on the right, revealed only while paused

Pause freezes the current exhibit, Ken Burns motion, and soundtrack.
Opening or closing Ask Chat does not resume; only **Resume** does.

Sensei uses the existing clipboard handoff. The prompt tells it that the
**bold element is the designated target** and that surrounding Japanese is
optional exposure.

Hidden during `recordPipeline=1`.
