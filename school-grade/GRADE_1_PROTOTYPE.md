# Grade 1 school-grade prototype

Local preview: `school-grade/grade-1/index.html`

The Heisig lessons, the live 漢検 pages, and the YouTube collections were not modified.

## Ordering reference

The sequence is the grade 1 list of the 学年別漢字配当表 (elementary school kanji allocation, 五十音順), as stored in `kml/data/kanji/kanji_master.csv`.

Characters with `category=joyo` and `grade=1` were taken in `joyo_index` order. That column is the character’s place in the 常用漢字表, which is itself in 五十音順. They were not sorted again by reading, stroke count, or Heisig number.

The resulting 80 characters match the conventional grade 1 sequence, including the opening 一 → 右 → 雨 → 円 → 王 → 音 → 下 → 火 → 花 → 貝. The same four groups are already used by the Grade 1 熟語 films.

- Lesson 1: 一 → 見 (20 characters)
- Lesson 2: 五 → 森 (20 characters)
- Lesson 3: 人 → 虫 (20 characters)
- Lesson 4: 町 → 六 (20 characters)

All 80 characters appear once.

Recorded in `school-grade/grade-1/order.json` so later grades can follow the same rule: filter the master table to the grade, keep `joyo_index` order, and do not re-sort.

## English meanings

Source: KANJIDIC2 `kml/kanjidic2.xml`, database 2026-074, created 2026-03-15.

The standard meaning is the first English `<meaning>` (no `m_lang`) in document order. The Heisig keyword is the text already shown in the lesson HTML. The Heisig pages were not edited.

Comparison, in order:

1. Same wording after case, punctuation, underscores, articles, and a simple plural fold. Show only the KANJIDIC2 wording.
2. Otherwise, if the pair is a near-synonym or one phrase is only a shorter form of the other, show both and flag it here. Those were not treated as a match or as a split.
3. Otherwise, if the keyword matches a later KANJIDIC2 gloss exactly, show the first gloss and then `(Heisig: …)`.
4. Otherwise show both and flag the comparison. The keyword was not forced into either decision.

### Same meaning (67)

Only the standard meaning is shown.

- 一 — standard “one”; Heisig “one”; other glosses: one; one radical (no.1). same wording as the first KANJIDIC2 gloss.
- 右 — standard “right”; Heisig “right”; other glosses: right. same wording as the first KANJIDIC2 gloss.
- 雨 — standard “rain”; Heisig “rain”; other glosses: rain. same wording as the first KANJIDIC2 gloss.
- 円 — standard “circle”; Heisig “circle”; other glosses: circle; yen; round. same wording as the first KANJIDIC2 gloss.
- 王 — standard “king”; Heisig “king”; other glosses: king; rule; magnate. same wording as the first KANJIDIC2 gloss.
- 音 — standard “sound”; Heisig “sound”; other glosses: sound; noise. same wording as the first KANJIDIC2 gloss.
- 下 — standard “below”; Heisig “below”; other glosses: below; down; descend; give; low; inferior. same wording as the first KANJIDIC2 gloss.
- 火 — standard “fire”; Heisig “fire”; other glosses: fire. same wording as the first KANJIDIC2 gloss.
- 花 — standard “flower”; Heisig “flower”; other glosses: flower. same wording as the first KANJIDIC2 gloss.
- 貝 — standard “shellfish”; Heisig “shellfish”; other glosses: shellfish. same wording as the first KANJIDIC2 gloss.
- 学 — standard “study”; Heisig “study”; other glosses: study; learning; science. same wording as the first KANJIDIC2 gloss.
- 気 — standard “spirit”; Heisig “spirit”; other glosses: spirit; mind; air; atmosphere; mood. same wording as the first KANJIDIC2 gloss.
- 九 — standard “nine”; Heisig “nine”; other glosses: nine. same wording as the first KANJIDIC2 gloss.
- 休 — standard “rest”; Heisig “rest”; other glosses: rest; day off; retire; sleep. same wording as the first KANJIDIC2 gloss.
- 金 — standard “gold”; Heisig “gold”; other glosses: gold. same wording as the first KANJIDIC2 gloss.
- 犬 — standard “dog”; Heisig “dog”; other glosses: dog. same wording as the first KANJIDIC2 gloss.
- 見 — standard “see”; Heisig “see”; other glosses: see; hopes; chances; idea; opinion; look at; visible. same wording as the first KANJIDIC2 gloss.
- 五 — standard “five”; Heisig “five”; other glosses: five. same wording as the first KANJIDIC2 gloss.
- 口 — standard “mouth”; Heisig “mouth”; other glosses: mouth. same wording as the first KANJIDIC2 gloss.
- 校 — standard “exam”; Heisig “exam”; other glosses: exam; school; printing; proof; correction. same wording as the first KANJIDIC2 gloss.
- 左 — standard “left”; Heisig “left”; other glosses: left. same wording as the first KANJIDIC2 gloss.
- 三 — standard “three”; Heisig “three”; other glosses: three. same wording as the first KANJIDIC2 gloss.
- 山 — standard “mountain”; Heisig “mountain”; other glosses: mountain. same wording as the first KANJIDIC2 gloss.
- 子 — standard “child”; Heisig “child”; other glosses: child; sign of the rat; 11PM-1AM; first sign of Chinese zodiac. same wording as the first KANJIDIC2 gloss.
- 四 — standard “four”; Heisig “four”; other glosses: four. same wording as the first KANJIDIC2 gloss.
- 糸 — standard “thread”; Heisig “thread”; other glosses: thread. same wording as the first KANJIDIC2 gloss.
- 耳 — standard “ear”; Heisig “ear”; other glosses: ear. same wording as the first KANJIDIC2 gloss.
- 七 — standard “seven”; Heisig “seven”; other glosses: seven. same wording as the first KANJIDIC2 gloss.
- 車 — standard “car”; Heisig “car”; other glosses: car. same wording as the first KANJIDIC2 gloss.
- 手 — standard “hand”; Heisig “hand”; other glosses: hand. same wording as the first KANJIDIC2 gloss.
- 十 — standard “ten”; Heisig “ten”; other glosses: ten. same wording as the first KANJIDIC2 gloss.
- 出 — standard “exit”; Heisig “exit”; other glosses: exit; leave; go out; come out; put out; protrude. same wording as the first KANJIDIC2 gloss.
- 女 — standard “woman”; Heisig “woman”; other glosses: woman; female. same wording as the first KANJIDIC2 gloss.
- 森 — standard “forest”; Heisig “forest”; other glosses: forest; woods. same wording as the first KANJIDIC2 gloss.
- 人 — standard “person”; Heisig “person”; other glosses: person. same wording as the first KANJIDIC2 gloss.
- 水 — standard “water”; Heisig “water”; other glosses: water. same wording as the first KANJIDIC2 gloss.
- 正 — standard “correct”; Heisig “correct”; other glosses: correct; justice; righteous; 10**40. same wording as the first KANJIDIC2 gloss.
- 生 — standard “life”; Heisig “life”; other glosses: life; genuine; birth. same wording as the first KANJIDIC2 gloss.
- 青 — standard “blue”; Heisig “blue”; other glosses: blue; green. same wording as the first KANJIDIC2 gloss.
- 夕 — standard “evening”; Heisig “evening”; other glosses: evening. same wording as the first KANJIDIC2 gloss.
- 石 — standard “stone”; Heisig “stone”; other glosses: stone. same wording as the first KANJIDIC2 gloss.
- 赤 — standard “red”; Heisig “red”; other glosses: red. same wording as the first KANJIDIC2 gloss.
- 千 — standard “thousand”; Heisig “thousand”; other glosses: thousand. same wording as the first KANJIDIC2 gloss.
- 早 — standard “early”; Heisig “early”; other glosses: early; fast. same wording as the first KANJIDIC2 gloss.
- 草 — standard “grass”; Heisig “grass”; other glosses: grass; weeds; herbs; pasture; write; draft. same wording as the first KANJIDIC2 gloss.
- 足 — standard “leg”; Heisig “leg”; other glosses: leg; foot; be sufficient; counter for pairs of footwear. same wording as the first KANJIDIC2 gloss.
- 村 — standard “village”; Heisig “village”; other glosses: village; town. same wording as the first KANJIDIC2 gloss.
- 大 — standard “large”; Heisig “large”; other glosses: large; big. same wording as the first KANJIDIC2 gloss.
- 竹 — standard “bamboo”; Heisig “bamboo”; other glosses: bamboo. same wording as the first KANJIDIC2 gloss.
- 虫 — standard “insect”; Heisig “insect”; other glosses: insect; bug; temper. same wording as the first KANJIDIC2 gloss.
- 町 — standard “town”; Heisig “town”; other glosses: town; village; block; street. same wording as the first KANJIDIC2 gloss.
- 天 — standard “heavens”; Heisig “heaven”; other glosses: heavens; sky; imperial. same wording as the first KANJIDIC2 gloss.
- 土 — standard “soil”; Heisig “soil”; other glosses: soil; earth; ground; Turkey. same wording as the first KANJIDIC2 gloss.
- 二 — standard “two”; Heisig “two”; other glosses: two; two radical (no. 7). same wording as the first KANJIDIC2 gloss.
- 入 — standard “enter”; Heisig “enter”; other glosses: enter; insert. same wording as the first KANJIDIC2 gloss.
- 年 — standard “year”; Heisig “year”; other glosses: year; counter for years. same wording as the first KANJIDIC2 gloss.
- 白 — standard “white”; Heisig “white”; other glosses: white. same wording as the first KANJIDIC2 gloss.
- 八 — standard “eight”; Heisig “eight”; other glosses: eight; eight radical (no. 12). same wording as the first KANJIDIC2 gloss.
- 百 — standard “hundred”; Heisig “hundred”; other glosses: hundred. same wording as the first KANJIDIC2 gloss.
- 文 — standard “sentence”; Heisig “sentence”; other glosses: sentence; literature; style; art; decoration; figures; plan; literary radical (no. 67). same wording as the first KANJIDIC2 gloss.
- 木 — standard “tree”; Heisig “tree”; other glosses: tree; wood. same wording as the first KANJIDIC2 gloss.
- 本 — standard “book”; Heisig “book”; other glosses: book; present; main; origin; true; real; counter for long cylindrical things. same wording as the first KANJIDIC2 gloss.
- 名 — standard “name”; Heisig “name”; other glosses: name; noted; distinguished; reputation. same wording as the first KANJIDIC2 gloss.
- 目 — standard “eye”; Heisig “eye”; other glosses: eye; class; look; insight; experience; care; favor. same wording as the first KANJIDIC2 gloss.
- 立 — standard “stand up”; Heisig “stand up”; other glosses: stand up; rise; set up; erect. same wording as the first KANJIDIC2 gloss.
- 力 — standard “power”; Heisig “power”; other glosses: power; strength; strong; strain; bear up; exert. same wording as the first KANJIDIC2 gloss.
- 六 — standard “six”; Heisig “six”; other glosses: six. same wording as the first KANJIDIC2 gloss.

### Meaningfully different (4)

The standard meaning is shown first. The original keyword follows in smaller type.

- 玉 — standard “jewel”; Heisig “ball”; other glosses: jewel; ball. keyword matches a later gloss (ball), not the first.
- 空 — standard “empty”; Heisig “sky”; other glosses: empty; sky; void; vacant; vacuum. keyword matches a later gloss (sky), not the first.
- 月 — standard “month”; Heisig “moon”; other glosses: month; moon. keyword matches a later gloss (moon), not the first.
- 日 — standard “day”; Heisig “sun”; other glosses: day; sun; Japan; counter for days. keyword matches a later gloss (sun), not the first.

### Uncertain — review (9)

Both are shown, in the same way as a difference, so neither source is hidden. These still need a human decision before the Heisig line is removed or kept as a real difference.

- 字 — standard “character”; Heisig “letter”; other glosses: character; letter; word; section of village. different words that may be the same sense.
- 小 — standard “little”; Heisig “small”; other glosses: little; small. different words that may be the same sense.
- 上 — standard “above”; Heisig “up”; other glosses: above; up. different words that may be the same sense.
- 川 — standard “stream”; Heisig “river”; other glosses: stream; river; river or three-stroke river radical (no. 47). different words that may be the same sense.
- 先 — standard “before”; Heisig “previous”; other glosses: before; ahead; previous; future; precedence. different words that may be the same sense.
- 男 — standard “male”; Heisig “man”; other glosses: male. different words that may be the same sense.
- 中 — standard “in”; Heisig “middle”; other glosses: in; inside; middle; mean; center. different words that may be the same sense.
- 田 — standard “rice field”; Heisig “field”; other glosses: rice field; rice paddy. the keyword is a shorter form of the first gloss.
- 林 — standard “grove”; Heisig “woods”; other glosses: grove; forest. different words that may be the same sense.

Later KANJIDIC2 glosses are not added to the page when the keyword already matches the first gloss. For school reading, the ones most worth a second look are 校 (first gloss “exam”, later “school”), 円 (later “yen”), 青 (later “green”), and 足 (later “foot”).

## Source material

Each page reuses the Heisig `<section class="kanji-entry">` for that character: landscape study, verse, readings, printed and written forms, component diagram, and stroke-order link. Compounds and their example sentences come from that character’s lesson file in `kml/data/compounds/`. Asset files are linked, not copied.

The lesson page already spells the keyword differently from `kanji_master.csv`. The comparison uses the lesson page. 立: page “stand up”, table “stand_up”
The same character also has another Heisig entry. The grade list keeps the entry whose lesson matches its Heisig number.
- 子: kept lesson 5 “child”; also lesson 153 “rat zodiac”
Study images already on the Heisig pages that are not 16:9. Left as they are:
- 一 ../../kml/assets/studies/one.jpg 1536×1024
- 右 ../../kml/assets/studies/right.jpg 1535×1024
- 王 ../../kml/assets/studies/king.jpg 1536×1024
- 下 ../../kml/assets/studies/below.jpg 1537×1023
- 貝 ../../kml/assets/studies/shellfish.jpg 1402×1122
- 学 ../../kml/assets/studies/study.jpg 1536×1024
- 九 ../../kml/assets/studies/nine.jpg 1536×1024
- 玉 ../../kml/assets/studies/ball.jpg 1536×1024
- 金 ../../kml/assets/studies/gold.jpg 1536×1024
- 月 ../../kml/assets/studies/moon.jpg 1402×1122
- 犬 ../../kml/assets/studies/dog.jpg 1536×1024
- 見 ../../kml/assets/studies/see.jpg 1537×1023
- 五 ../../kml/assets/studies/five.jpg 1536×1024
- 口 ../../kml/assets/studies/mouth.jpg 1536×1024
- 左 ../../kml/assets/studies/left.jpg 1537×1023
- 三 ../../kml/assets/studies/three.jpg 1536×1024
- 子 ../../kml/assets/studies/child.jpg 1536×1024
- 四 ../../kml/assets/studies/four.jpg 1537×1023
- 字 ../../kml/assets/studies/letter.jpg 1536×1024
- 七 ../../kml/assets/studies/seven.jpg 1536×1024
- 車 ../../kml/assets/studies/car.jpg 1535×1024
- 手 ../../kml/assets/studies/hand.jpg 1535×1024
- 十 ../../kml/assets/studies/ten.jpg 1536×1024
- 女 ../../kml/assets/studies/woman.jpg 1536×1024
- 小 ../../kml/assets/studies/small.jpg 1536×1024
- 上 ../../kml/assets/studies/up.jpg 1536×1024
- 森 ../../kml/assets/studies/forest.jpg 1536×1024
- 水 ../../kml/assets/studies/water.jpg 1535×1024
- 夕 ../../kml/assets/studies/evening.jpg 1536×1024
- 石 ../../kml/assets/studies/stone.jpg 1536×1024
- 千 ../../kml/assets/studies/thousand.jpg 1537×1023
- 川 ../../kml/assets/studies/river.jpg 1535×1024
- 先 ../../kml/assets/studies/previous.jpg 1535×1024
- 早 ../../kml/assets/studies/early.jpg 1537×1023
- 村 ../../kml/assets/studies/village.jpg 1536×1024
- 大 ../../kml/assets/studies/large.jpg 1536×1024
- 中 ../../kml/assets/studies/middle.jpg 1537×1023
- 町 ../../kml/assets/studies/town.jpg 1536×1024
- 田 ../../kml/assets/studies/field.jpg 1536×1024
- 二 ../../kml/assets/studies/two.jpg 1536×1024
- 日 ../../kml/assets/studies/sun.jpg 1536×1024
- 白 ../../kml/assets/studies/white.jpg 1537×1023
- 八 ../../kml/assets/studies/eight.jpg 1536×1024
- 百 ../../kml/assets/studies/hundred.jpg 1537×1023
- 木 ../../kml/assets/studies/tree.jpg 1536×1024
- 本 ../../kml/assets/studies/book.jpg 1535×1024
- 名 ../../kml/assets/studies/name.jpg 1536×1024
- 目 ../../kml/assets/studies/eye.jpg 1536×1024
- 林 ../../kml/assets/studies/woods.jpg 1536×1024
- 六 ../../kml/assets/studies/six.jpg 1537×1023

YouTube links are the three Grade 1 playlists already published on `elementary/grade-1/index.html`:

- 1学年で学ぶ漢字 — https://www.youtube.com/playlist?list=PLDqZ_saSB25k
- 熟語 — https://www.youtube.com/playlist?list=PLUK4NyqFdNMw
- 書き順 — https://www.youtube.com/playlist?list=PLYpgcBuk0PGg

Individual film URLs are not stored in the repository, so the prototype uses those playlists. The musical kanji set is two films of 40 characters; 熟語 and 書き順 are four films of 20, matching these lessons. The playlist ids are the ones already on the 漢検 grade page. They are shorter than a typical current YouTube playlist id, and that page was not changed.

## Component explanations

The diagrams are kept. The school-grade pages add the heading 漢字のしくみ — How This Kanji Is Built, so the diagram is a construction note rather than a step in the Heisig sequence.

Prose that assumes a component was already studied in Heisig order:

None found in the reused entry text.

Diagrams that include a glyph outside this grade (or a non-character part). No new explanation was written for these. They are the items most likely to need a plain label if the pathway is taught without Heisig:

- 右 (Heisig lesson 5): 𠂇
- 下 (Heisig lesson 3): 卜
- 花 (Heisig lesson 55): 艹 化
- 貝 (Heisig lesson 3): ㇵ
- 学 (Heisig lesson 18): ⺍ 冖
- 気 (Heisig lesson 102): 气 㐅
- 休 (Heisig lesson 52): 亻
- 玉 (Heisig lesson 14): 丶
- 空 (Heisig lesson 71): 穴 工
- 犬 (Heisig lesson 13): 丶
- 見 (Heisig lesson 4): 儿
- 校 (Heisig lesson 69): 交
- 左 (Heisig lesson 5): 𠂇 工
- 四 (Heisig lesson 1): 儿
- 字 (Heisig lesson 10): 宀
- 上 (Heisig lesson 3): 卜
- 青 (Heisig lesson 83): 龶
- 石 (Heisig lesson 6): 厂
- 千 (Heisig lesson 2): 丿
- 先 (Heisig lesson 14): 牛 儿
- 草 (Heisig lesson 12): 艹
- 村 (Heisig lesson 12): 寸
- 町 (Heisig lesson 5): 丁
- 白 (Heisig lesson 2): 丿
- 六 (Heisig lesson 1): ⼇ ㇵ

## What can be automated for Grades 2–6

The generator can be reused as it stands for the extraction, meaning comparison, compound attachment, component heading, and lesson navigation.

What is already general:

- Lesson HTML is the entry source. One character is lifted from whichever Heisig lesson contains it.
- Compounds are taken from the matching `kml/data/compounds/lesson_NN.json` character.
- KANJIDIC2 supplies the standard English meaning with the same comparison rules.
- `joyo_index` within a grade reproduces 五十音順 without a hand-built sort.

What Grade 1 does not settle:

- Grades 2–6 are 160, 200, 202, 193, and 191 characters. Equal lessons of 20 do not come out even. The existing films already split those grades on their own boundaries, including gojūon sections in the later grades. Those boundaries should be recorded the way Grade 1’s four groups of 20 are recorded here.
- The near-synonym list in the meaning comparison is a review aid for uncertain pairs, not a complete dictionary. Later grades will add pairs this list does not know. Those should stay in the uncertain report.
- Component diagrams that point outside the current grade will be more common from Grade 2 on. The heading is in place; plain-language labels for those parts are still an editorial pass, not something the generator should invent.
