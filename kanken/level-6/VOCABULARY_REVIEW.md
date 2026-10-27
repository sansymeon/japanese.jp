# 漢検6級 vocabulary review

Learner pages do not explain these choices. The lesson covers are approved, including 第4課 採.
Meanings and examples below record the review. Nothing here has been deployed.

KANJIDIC2 2026-074, 2026-03-15.
English on a card is the first KANJIDIC2 gloss, unless MEANING_CHOICES names a clearer gloss from that same list or a marked paraphrase.
A displayed meaning tagged kanjidic is that exact gloss. A paraphrase is editorial. A meaning tagged heisig is that keyword used as the card wording.
Heisig stays on its own line only when the keyword is not already the displayed wording.
Readings are the 常用漢字表 音訓. Parentheses are the table’s indented readings.
Example words come from `kml/data/compounds/`. A word filed under another character is used only when
the same matcher used on 8級 locks it to that reading, and the word is a verb or a headword of at most three kanji.
One-mora on readings are not filled that way. A dictionary form is added only when a sentence segment
locks that exact reading. A reading with no suitable word stays bare.
Bare readings remaining: 61.

The overview hero is 桜 `kml/assets/studies/cherry_blossom.jpg`.
Lesson covers are existing study images, one character from each lesson:

- 第1課 演 `kml/assets/studies/performance.jpg`
- 第2課 幹 `kml/assets/studies/tree_trunk.jpg`
- 第3課 耕 `kml/assets/studies/till.jpg`
- 第4課 採 `kml/assets/studies/pick.jpg`
- 第5課 枝 `kml/assets/studies/bough.jpg`
- 第6課 織 `kml/assets/studies/weave.jpg`
- 第7課 築 `kml/assets/studies/fabricate.jpg`
- 第8課 堂 `kml/assets/studies/public_hall.jpg`
- 第9課 布 `kml/assets/studies/linen.jpg`
- 第10課 綿 `kml/assets/studies/cotton.jpg`

河 `large_river.jpg` is a night sky over fields, so it is not the overview. 粉 `flour.jpg` is a snowy street, so it is not a cover.
第4課 uses 採 `pick.jpg`. The crystal close-up `mineral.jpg` is not the cover.

## Cross-file examples

Each attached word contains its target character once, and the matcher locks that character’s reading.
雑 ゾウ uses 雑巾（ぞうきん） from lesson_22.json, 床を雑巾で拭きました. The word contains 雑. It is not an example for 造. 造 uses 建造, 改造, 製造, and 造る.
性 ショウ uses 相性（あいしょう） from lesson_12.json, この二人は相性がいいです. しょう is 性.
率 ソツ uses 軽率（けいそつ） from lesson_39.json, 彼女の態度は軽率です. そつ is 率.

## For judgment

- 桜 shows “cherry blossom”, Heisig’s keyword. KANJIDIC2’s only gloss is “cherry”. The separate Heisig line is omitted.
- 経 shows “sutra; pass through”. “pass through” spells out the gloss “pass thru”.
- 性 shows “sex; gender; nature”. All three are KANJIDIC glosses, so “gender” is not left on a Heisig-only line.
- 製 shows “manufacture”. The first gloss “made in...” is not shown.
- 破 shows “tear; break”. The first gloss “rend” is not shown.
- 堂 shows “hall”, the KANJIDIC gloss. “public chamber” is the same sense. Heisig “public hall” is not shown.
- 統 shows “unite; govern”. “unite” is Heisig’s keyword. “govern” is the editorial verb for “governing”.
- 断 shows “cut off; decide; refuse”. “decide” is the editorial verb form of the gloss “decision”.
- 設 shows “establish”, Heisig’s keyword. The KANJIDIC gloss is the noun “establishment”.
- 旧 shows “old times; former”. Both are KANJIDIC glosses.
- 営 shows “conduct (business); camp”. Both are KANJIDIC glosses, with 営業 first.
- 可 shows “possible”, Heisig’s keyword on the KML lesson. It is not a KANJIDIC gloss. The glosses are “can”, “passable”, and “approval”.
- 非 still shows “un-; negative”. “un-” is the KANJIDIC prefix gloss.
- 因 still shows “cause”. Heisig “reason” is not a gloss.
- 河 still shows “river”. Heisig “large river” is not a gloss.
- 制 still shows “system”. Heisig “control” is not a gloss. Later glosses are “law” and “rule”.
- 応 still shows “apply; answer”. Heisig “respond” is not a gloss.
- 示 prints 示（しめす）. The shared radical table’s 礻 is the form in 社, and it is the same classical radical.

## Held back

- 混 まじる: 茉莉の匂いが、南からの船荷に混じっていました. The jasmine wording is not a learner example.
- 移 うつす: 冗員を別の仕事へ移しました and 牝の馬を別の厩に移した. Neither is a learner sentence.
- 導 みちびく: 御者は鞭を上げず声で導いた. Not a learner sentence.
- 示 シ: sentences that read 示 as しめ were not used. しめ begins with し, so it is not an example of シ.
- 眼 まなこ: lesson_79.html reads 澄んだ眼 as まなこ. That word is literary, so the reading stays bare.

## Needs review

### 圧（第1課）

- 圧倒（あっとう）をアツに付けました（sokuon）。
- 圧縮（あっしゅく）をアツに付けました（sokuon）。
- アツの例は3語までです。残り2語は出していません。

### 囲（第1課）

- 例のない読み: かこう
- 例にしていない語: 雰囲気（ふんいき）

### 移（第1課）

- 例のない読み: うつす
- イの例は3語までです。残り1語は出していません。

### 因（第1課）

- Meaning “cause”, Heisig “reason” (uncertain: keyword does not match a KANJIDIC2 gloss closely enough to decide)
- 例のない読み: よる
- インの例は3語までです。残り2語は出していません。

### 永（第1課）

- 例のない読み: ながい
- エイの例は3語までです。残り2語は出していません。

### 営（第1課）

- Both are KANJIDIC glosses. “conduct (business)” is placed first for 営業. “camp” remains for 陣営. Heisig “occupation” is not a gloss and is not shown.
- KANJIDIC2の古典部首は口です。joyo_kanji.csv は火で、營の部首です。カードは口のままです。
- joyo_kanji.csv の部首欄は火、カードは 口（くち）、出典 kanjidic
- エイの例は3語までです。残り1語は出していません。

### 衛（第1課）

- エイの例は3語までです。残り2語は出していません。

### 益（第1課）

- 例にしていない語: 益々（ますます）

### 液（第1課）

- エキの例は3語までです。残り2語は出していません。

### 演（第1課）

- 例にしていない語: 演じる（えんじる）

### 応（第1課）

- Both are KANJIDIC glosses. Heisig “respond” is not a gloss and is not shown.
- 例のない読み: こたえる
- 例にしていない語: 反応（はんのう）
- オウの例は3語までです。残り1語は出していません。

### 桜（第1課）

- The card wording is Heisig’s keyword “cherry blossom”. KANJIDIC2’s only gloss is “cherry”, which can be read as the fruit. The separate Heisig line is omitted because it would repeat the card.
- 例のない読み: オウ
- 桜前線（さくらぜんせん）をさくらに付けました（compound）。

### 可（第1課）

- The card wording is Heisig’s keyword “possible”, printed on the KML lesson. It is not a KANJIDIC2 gloss. Those glosses are “can”, “passable”, and “approval”. The separate Heisig line is omitted.
- カの例は3語までです。残り1語は出していません。

### 仮（第1課）

- KANJIDIC gloss “temporary”. The first gloss “sham” is a different sense. Heisig “temporary” is this gloss.
- 例にしていない語: 平仮名（ひらがな）、片仮名（かたかな）
- Added 仮（かり） for かり from kml/contents/books/book_01/lessons/lesson_52.html (The verse reads 仮 as かり in 仮の橋を渡り, and its English is “a temporary bridge”). Snippet: Crossing a temporary bridge。

### 価（第1課）

- Both are KANJIDIC glosses. Heisig “cost” is not a gloss and is not shown.
- Added 価（あたい） for あたい from kml/contents/books/book_01/lessons/lesson_87.html (The verse reads 価 as あたい in 本当の価は, and its English is “True worth”). Snippet: True worth。
- カの例は3語までです。残り2語は出していません。

### 河（第1課）

- Meaning “river”, Heisig “large river” (uncertain: the first gloss is a shorter form of the keyword)
- 例にしていない語: 銀河（ぎんが）、運河（うんが）、大河（たいが）
- Added 河（かわ） for かわ from kml/contents/books/book_01/lessons/lesson_08.html (The verse reads 河 as かわ in 広い河は, and its English is “A broad river”. 銀河 in the same lesson is が, not かわ). Snippet: A broad river。

### 過（第1課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic
- 例のない読み: あやまつ、あやまち

### 快（第1課）

- カイの例は3語までです。残り1語は出していません。

### 解（第2課）

- Both are KANJIDIC glosses. Heisig “solution” is not a gloss and is not shown.
- 例のない読み: ゲ、とかす
- Added 解ける（とける） for とける from kml/data/compounds/lesson_91.json (解けます is と-ける. と-く would be 解きます). Snippet: この種の問題は、話し合いで解けます。
- Added 解く（とく） for とく from kml/data/compounds/lesson_19.json (解きます is と-く. と-ける would be 解けます). Snippet: 祖父は夜、詰将棋を解きます。
- カイの例は3語までです。残り2語は出していません。

### 格（第2課）

- 格好（かっこう）をカクに付けました（sokuon）。
- カクの例は3語までです。残り2語は出していません。

### 確（第2課）

- Added 確かめる（たしかめる） for たしかめる from kml/data/compounds/lesson_30.json (確かめました is たし-かめる). Snippet: 地図で朝鮮半島の位置を確かめました。
- カクの例は3語までです。残り1語は出していません。

### 額（第2課）

- Both are KANJIDIC glosses. “forehead” alone hides 金額. Heisig “amount” is the second gloss.
- 例のない読み: ひたい
- ガクの例は3語までです。残り2語は出していません。

### 刊（第2課）

- カンの例は3語までです。残り2語は出していません。

### 幹（第2課）

- 例にしていない語: 新幹線（しんかんせん）

### 慣（第2課）

- 例のない読み: ならす
- 例にしていない語: 不慣れ（ふなれ）

### 眼（第2課）

- 例のない読み: まなこ
- 例にしていない語: 眼鏡（めがね）、双眼鏡（そうがんきょう）

### 基（第2課）

- KANJIDIC gloss “foundation”. The first gloss “fundamentals” is another sense in the same entry. Heisig “foundation” is this gloss.
- 例のない読み: もとい
- 例にしていない語: 基づく（もとづく）

### 規（第2課）

- 例にしていない語: 定規（じょうぎ）
- キの例は3語までです。残り1語は出していません。

### 喜（第2課）

- 例にしていない語: 喜び（よろこび）

### 技（第2課）

- ギの例は3語までです。残り1語は出していません。

### 義（第2課）

- ギの例は3語までです。残り2語は出していません。

### 逆（第2課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic
- Added 逆（さか） for さか from kml/contents/books/book_01/lessons/lesson_106.html (The verse reads 逆 as さか in 流れに逆らい. The English is “Resisting the strong river current”). Snippet: Resisting the strong river current。

### 久（第2課）

- 例にしていない語: 久しぶり（ひさしぶり）

### 旧（第2課）

- Both are KANJIDIC glosses. “old times” alone hides 旧姓 and 旧制. Heisig “olden times” restates the first gloss and is not shown.
- KANJIDIC2の古典部首は日です。joyo_kanji.csv は臼で、舊の部首です。カードは日のままです。
- joyo_kanji.csv の部首欄は臼、カードは 日（ひ）、出典 kanjidic
- キュウの例は3語までです。残り3語は出していません。

### 救（第2課）

- 古典部首は攴です。教・数にある形は攵です。
- joyo_kanji.csv の部首欄は攴、カードは 攵（のぶん）、出典 kanjidic
- 例にしていない語: 救い（すくい）

### 居（第2課）

- 例にしていない語: 居間（いま）、芝居（しばい）、居眠り（いねむり）

### 許（第3課）

- キョの例は3語までです。残り1語は出していません。

### 境（第3課）

- 例にしていない語: 境内（けいだい）
- Added 境（さかい） for さかい from kml/contents/books/book_01/lessons/lesson_09.html (The verse reads 境 as さかい in 空と海との境が消える). Snippet: sea and sky become one。
- キョウの例は3語までです。残り1語は出していません。

### 均（第3課）

- キンの例は3語までです。残り2語は出していません。

### 禁（第3課）

- 古典部首は示です。社にある形は礻です。
- joyo_kanji.csv の部首欄は示、カードは 礻（しめすへん）、出典 kanjidic
- 例にしていない語: 禁じる（きんじる）
- キンの例は3語までです。残り1語は出していません。

### 句（第3課）

- クの例は3語までです。残り3語は出していません。

### 型（第3課）

- 大型（おおがた）をかたに付けました（rendaku）。
- 血液型（けつえきがた）をかたに付けました（rendaku）。
- 新型（しんがた）をかたに付けました（rendaku）。
- かたの例は3語までです。残り1語は出していません。

### 経（第3課）

- “sutra” is a KANJIDIC gloss. “pass through” is the editorial spelling of the KANJIDIC gloss “pass thru”. Heisig “manage” is not a gloss and is not shown.
- 例のない読み: へる
- Added 経（きょう） for キョウ from kml/data/compounds/lesson_02.json (経（きょう） is キョウ, the sutra reading. ケイ would be けい. へ-る would be 経る). Snippet: 寺で人がお経を唱えます。
- ケイの例は3語までです。残り2語は出していません。

### 潔（第3課）

- 例のない読み: いさぎよい

### 件（第3課）

- ケンの例は3語までです。残り2語は出していません。

### 険（第3課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic

### 検（第3課）

- ケンの例は3語までです。残り2語は出していません。

### 限（第3課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic
- 例にしていない語: 限り（かぎり）

### 現（第3課）

- 例のない読み: あらわす
- Added 現れる（あらわれる） for あらわれる from kml/data/compounds/lesson_101.json (現れました is あらわ-れる. あらわ-す would be 現しました). Snippet: 朝の船は、霧の中から現れました。
- ゲンの例は3語までです。残り2語は出していません。

### 減（第3課）

- 例にしていない語: 値下げ減税（げんぜい）
- Added 減る（へる） for へる from kml/data/compounds/lesson_23.json (減ります is へ-る. へ-らす would be 減らします). Snippet: 冬季のバスは本数が減ります。
- Added 減らす（へらす） for へらす from kml/data/compounds/lesson_94.json (減らした is へ-らす. へ-る would be 減った). Snippet: 農薬を減らした野菜が、店に並んでいます。
- ゲンの例は3語までです。残り1語は出していません。

### 故（第3課）

- 古典部首は攴です。教・数にある形は攵です。
- joyo_kanji.csv の部首欄は攴、カードは 攵（のぶん）、出典 kanjidic
- 例のない読み: ゆえ
- 例にしていない語: 何故（なぜ）
- コの例は3語までです。残り1語は出していません。

### 個（第3課）

- コの例は3語までです。残り2語は出していません。

### 護（第3課）

- ゴの例は3語までです。残り2語は出していません。

### 効（第3課）

- Both are KANJIDIC glosses. Heisig “effect” is not a gloss and is not shown.
- コウの例は3語までです。残り1語は出していません。

### 厚（第3課）

- 例にしていない語: 厚紙（あつがみ）

### 航（第4課）

- コウの例は3語までです。残り1語は出していません。

### 鉱（第4課）

- 例にしていない語: 鉄鉱石（てっこうせき）
- コウの例は3語までです。残り1語は出していません。

### 構（第4課）

- Both are KANJIDIC glosses. Heisig “construct” is not a gloss and is not shown.
- 例のない読み: かまえる、かまう
- 例にしていない語: 構いません（かまいません）
- コウの例は3語までです。残り1語は出していません。

### 興（第4課）

- 例のない読み: おこる、おこす
- コウの例は3語までです。残り1語は出していません。

### 講（第4課）

- コウの例は3語までです。残り2語は出していません。

### 告（第4課）

- 例のない読み: つげる
- コクの例は3語までです。残り2語は出していません。

### 混（第4課）

- 例のない読み: まじる
- Added 混む（こむ） for こむ from kml/data/compounds/lesson_12.json (混みます is こ-む). Snippet: 年末は店が大変混みます。
- Added 混ぜる（まぜる） for まぜる from kml/data/compounds/lesson_75.json (混ぜて is ま-ぜる. ま-じる would be 混じって). Snippet: 最近は玄米を混ぜて炊きます。
- コンの例は3語までです。残り1語は出していません。

### 査（第4課）

- サの例は3語までです。残り2語は出していません。

### 再（第4課）

- 例にしていない語: 再来月（さらいげつ）、再来週（さらいしゅう）

### 災（第4課）

- 例のない読み: わざわい
- サイの例は3語までです。残り2語は出していません。

### 採（第4課）

- Added 採る（とる） for とる from kml/data/compounds/lesson_30.json (朝採り is と-る). Snippet: 朝採りの野菜は新鮮で甘いです。
- サイの例は3語までです。残り2語は出していません。

### 際（第4課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic
- 手際（てぎわ）をきわに付けました（rendaku）。
- サイの例は3語までです。残り1語は出していません。

### 在（第4課）

- 例のない読み: ある
- ザイの例は3語までです。残り2語は出していません。

### 財（第4課）

- 例にしていない語: 財布（さいふ）
- ザイの例は3語までです。残り1語は出していません。

### 罪（第4課）

- 古典部首は网（あみがしら）です。罪にある形は罒です。
- joyo_kanji.csv の部首欄は网、カードは 罒（よんかしら）、出典 kanjidic

### 殺（第4課）

- るまたとも呼ばれます。
- 例にしていない語: 必殺技（ひっさつわざ）

### 雑（第4課）

- Added 雑巾（ぞうきん） for ゾウ from a KML compound filed under another character (start).
- 雑誌（ざっし）をザツに付けました（sokuon）。
- 雑貨（ざっか）をザツに付けました（sokuon）。
- ザツの例は3語までです。残り2語は出していません。

### 酸（第4課）

- 例のない読み: すい
- サンの例は3語までです。残り2語は出していません。

### 士（第5課）

- 例にしていない語: 博士（はかせ）
- シの例は3語までです。残り1語は出していません。

### 支（第5課）

- じゅうまたとも呼ばれます。
- Added 支える（ささえる） for ささえる from kml/data/compounds/lesson_93.json (支える is ささ-える). Snippet: 過疎地の医療を、支える人が減っています。
- シの例は3語までです。残り2語は出していません。

### 史（第5課）

- シの例は3語までです。残り2語は出していません。

### 志（第5課）

- Added 志（こころざし） for こころざし from kml/contents/books/book_01/lessons/lesson_21.html (The verse reads 志 as こころざし, and its English is “Resolve”). Snippet: Resolve first appears in the eyes。
- シの例は3語までです。残り1語は出していません。

### 枝（第5課）

- 例にしていない語: 枝分かれ（えだわかれ）
- 小枝（こえだ）をえだに付けました（compound）。
- 枝道（えだみち）をえだに付けました（compound）。

### 師（第5課）

- シの例は3語までです。残り2語は出していません。

### 資（第5課）

- シの例は3語までです。残り2語は出していません。

### 飼（第5課）

- 例にしていない語: 飼い主（かいぬし）

### 示（第5課）

- Both are KANJIDIC glosses. Heisig “indicate” is the second gloss.
- この字そのものが部首です。社などにある形は礻（しめすへん）で、同じ古典部首です。
- 例のない読み: シ
- ジの例は3語までです。残り1語は出していません。

### 似（第5課）

- KANJIDIC gloss “resemble”. The first gloss “becoming” is a different sense. Heisig “resemble” is this gloss.
- 例にしていない語: 似顔絵（にがおえ）、真似（まね）、似合う（にあう）、真似る（まねる）
- Added 擬似（ぎじ） for ジ from kml/data/compounds/lesson_76.json (擬似 ends with ジ). Snippet: 擬似の星空が、天井に映されています。

### 識（第5課）

- シキの例は3語までです。残り2語は出していません。

### 質（第5課）

- Both are KANJIDIC glosses. Heisig “quality” is the second gloss.
- 例のない読み: シチ
- シツの例は3語までです。残り2語は出していません。

### 舎（第5課）

- KANJIDIC2の古典部首は人です。joyo_kanji.csv は舌で、舍の部首です。カードは人のままです。
- joyo_kanji.csv の部首欄は舌、カードは 人（ひと）、出典 kanjidic
- シャの例は3語までです。残り2語は出していません。

### 謝（第5課）

- Both are KANJIDIC glosses. Heisig “thank” is the second gloss.

### 授（第5課）

- Both are KANJIDIC glosses. Heisig “instruct” is the second gloss.
- 例のない読み: さずける
- ジュの例は3語までです。残り1語は出していません。

### 修（第5課）

- 例のない読み: おさめる、おさまる
- シュウの例は3語までです。残り2語は出していません。

### 述（第5課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic

### 術（第5課）

- Both are KANJIDIC glosses. Heisig “technique” is the second gloss.
- 例にしていない語: 美術館（びじゅつかん）
- ジュツの例は3語までです。残り1語は出していません。

### 準（第5課）

- KANJIDIC gloss “conform”. The first gloss “semi-” is the prefix sense. Heisig “conform” is this gloss.
- ジュンの例は3語までです。残り2語は出していません。

### 招（第6課）

- ショウの例は3語までです。残り1語は出していません。

### 証（第6課）

- 例にしていない語: 身分証明書（みぶんしょうめいしょ）
- ショウの例は3語までです。残り1語は出していません。

### 賞（第6課）

- ショウの例は3語までです。残り2語は出していません。

### 条（第6課）

- Both are KANJIDIC glosses. Heisig “clause” is the second gloss.
- 例にしていない語: 箇条書き（かじょうがき）
- ジョウの例は3語までです。残り1語は出していません。

### 状（第6課）

- ジョウの例は3語までです。残り2語は出していません。

### 常（第6課）

- 例のない読み: とこ
- 例にしていない語: 常に（つねに）
- Added 常（つね） for つね from kml/data/compounds/lesson_83.json (常に is つね. とこ is a different reading and does not lock here). Snippet: 厨房は、常に清潔に保ちます。
- ジョウの例は3語までです。残り1語は出していません。

### 情（第6課）

- 例のない読み: なさけ
- ジョウの例は3語までです。残り2語は出していません。

### 織（第6課）

- 例のない読み: ショク
- 例にしていない語: 織物（おりもの）、錦織（にしきおり）

### 職（第6課）

- Both are KANJIDIC glosses. Heisig “employment” is the second gloss.
- ショクの例は3語までです。残り2語は出していません。

### 制（第6課）

- Meaning “system”, Heisig “control” (uncertain: keyword does not match a KANJIDIC2 gloss closely enough to decide)
- セイの例は3語までです。残り2語は出していません。

### 性（第6課）

- All three are KANJIDIC glosses. “sex” alone hides 性別 and 性質. Heisig “gender” is the second gloss, so the separate line is omitted.
- Added 相性（あいしょう） for ショウ from a KML compound filed under another character (end).
- セイの例は3語までです。残り2語は出していません。

### 政（第6課）

- 古典部首は攴です。教・数にある形は攵です。
- joyo_kanji.csv の部首欄は攴、カードは 攵（のぶん）、出典 kanjidic
- 例のない読み: まつりごと
- セイの例は3語までです。残り2語は出していません。

### 勢（第6課）

- 例にしていない語: 大勢（おおぜい）

### 精（第6課）

- セイの例は3語までです。残り2語は出していません。

### 製（第6課）

- KANJIDIC gloss “manufacture”. The first gloss “made in...” leaves the phrase unfinished. Heisig “made in” restates that gloss and is not shown.
- セイの例は3語までです。残り2語は出していません。

### 税（第6課）

- ゼイの例は3語までです。残り2語は出していません。

### 責（第6課）

- セキの例は3語までです。残り1語は出していません。

### 績（第6課）

- セキの例は3語までです。残り2語は出していません。

### 接（第6課）

- 例のない読み: つぐ
- 例にしていない語: 応接室（おうせつしつ）
- 接触（せっしょく）をセツに付けました（sokuon）。
- セツの例は3語までです。残り1語は出していません。

### 設（第7課）

- The card wording is Heisig’s keyword “establish”. KANJIDIC2’s gloss is the noun “establishment”. The separate Heisig line is omitted.
- 設定（せってい）をセツに付けました（sokuon）。
- セツの例は3語までです。残り1語は出していません。

### 絶（第7課）

- 例のない読み: たやす、たつ
- 例にしていない語: 絶えず（たえず）
- Added 絶える（たえる） for たえる from kml/data/compounds/lesson_82.json (絶えません is た-える. た-やす would be 絶やしません. た-つ would be 絶ちません). Snippet: 熱帯の夜は、虫の声が絶えません。
- 絶対（ぜったい）をゼツに付けました（sokuon）。
- 絶版（ぜっぱん）をゼツに付けました（sokuon）。
- ゼツの例は3語までです。残り1語は出していません。

### 祖（第7課）

- 古典部首は示です。社にある形は礻です。
- joyo_kanji.csv の部首欄は示、カードは 礻（しめすへん）、出典 kanjidic
- 例にしていない語: 先祖（せんぞ）
- ソの例は3語までです。残り1語は出していません。

### 素（第7課）

- 例にしていない語: 素（もと）、素晴らしい（すばらしい）
- Added 素肌（すはだ） for ス from kml/data/compounds/lesson_04.json (素肌 begins with ス. The sentence is a cold wind on bare skin). Snippet: 冷たい風が素肌に当たりました。

### 総（第7課）

- Both are KANJIDIC glosses. Heisig “total” is the second gloss.
- ソウの例は3語までです。残り1語は出していません。

### 造（第7課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic
- Added 造る（つくる） for つくる from kml/data/compounds/lesson_67.json (造ります is つく-る). Snippet: 老朽した橋は、来年造ります。
- ゾウの例は3語までです。残り2語は出していません。

### 増（第7課）

- 例のない読み: ます
- Added 増やす（ふやす） for ふやす from kml/data/compounds/lesson_88.json (増やしては is ふ-やす. ます would be 増します). Snippet: 無闇に薬を増やしてはいけません。
- ゾウの例は3語までです。残り1語は出していません。

### 則（第7課）

- ソクの例は3語までです。残り1語は出していません。

### 測（第7課）

- ソクの例は3語までです。残り1語は出していません。

### 属（第7課）

- 例にしていない語: 属する（ぞくする）

### 率（第7課）

- Both are KANJIDIC glosses. Heisig “rate” is the second gloss.
- 例のない読み: ひきいる
- Added 軽率（けいそつ） for ソツ from a KML compound filed under another character (end).
- リツの例は3語までです。残り2語は出していません。

### 損（第7課）

- 例のない読み: そこねる
- ソンの例は3語までです。残り1語は出していません。

### 貸（第7課）

- 例のない読み: タイ
- 例にしていない語: 貸出（かしだし）、貸し（かし）、貸家（かしや）、貸間（かしま）

### 態（第7課）

- 例にしていない語: 態と（わざと）

### 団（第7課）

- ダンの例は3語までです。残り2語は出していません。

### 断（第7課）

- “cut off” is Heisig’s keyword, the same sense as the glosses “severance” and “cutting”. “decide” is the editorial verb form of the KANJIDIC gloss “decision”. “refuse” is a KANJIDIC gloss.

### 貯（第7課）

- チョの例は3語までです。残り2語は出していません。

### 張（第7課）

- KANJIDIC gloss “stretch”. The first gloss is the counter for bows and stringed instruments. Heisig “lengthen” restates this gloss and is not shown.

### 停（第8課）

- テイの例は3語までです。残り2語は出していません。

### 提（第8課）

- 例のない読み: さげる
- テイの例は3語までです。残り2語は出していません。

### 程（第8課）

- テイの例は3語までです。残り1語は出していません。

### 適（第8課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic
- テキの例は3語までです。残り2語は出していません。

### 統（第8課）

- “unite” is Heisig’s keyword. “govern” is the editorial verb for the KANJIDIC gloss “governing”. The first gloss “overall” is not shown. デジタル大辞泉 gives 統一 as 「一つにまとめること」 and 統べる as 「全体をまとめて支配する」.
- 例のない読み: すべる
- 例にしていない語: 大統領（だいとうりょう）
- トウの例は3語までです。残り1語は出していません。

### 堂（第8課）

- KANJIDIC gloss “hall”. The first gloss “public chamber” is the same sense. Heisig “public hall” restates it and is not shown.
- ドウの例は3語までです。残り2語は出していません。

### 銅（第8課）

- ドウの例は3語までです。残り2語は出していません。

### 導（第8課）

- 例のない読み: みちびく
- ドウの例は3語までです。残り2語は出していません。

### 得（第8課）

- Both are KANJIDIC glosses. Heisig “acquire” is the second gloss.

### 毒（第8課）

- 母・毎は、学校で母部と呼ばれることがあります。
- 例にしていない語: 気の毒（きのどく）、お気の毒に（おきのどくに）

### 独（第8課）

- Both are KANJIDIC glosses. Heisig “alone” is the second gloss.
- 例のない読み: ひとり
- ドクの例は3語までです。残り2語は出していません。

### 任（第8課）

- 例のない読み: まかす
- ニンの例は3語までです。残り1語は出していません。

### 燃（第8課）

- 例のない読み: もす
- 例にしていない語: 天然ガス燃料（てんねんがすねんりょう）
- Added 燃やす（もやす） for もやす from kml/data/compounds/lesson_42.json (燃やして is も-やす. も-す would be 燃して). Snippet: 昔はこの町でも石炭を燃やして暖を取っていたと聞いた。

### 破（第8課）

- Both are KANJIDIC glosses. The first gloss “rend” is rare in learner English. Heisig “rend” repeats it and is not shown.
- 例のない読み: やぶれる
- 例にしていない語: 突破（とっぱ）

### 犯（第8課）

- ハンの例は3語までです。残り1語は出していません。

### 判（第8課）

- KANJIDIC gloss “judgement”. “judgment” is the same gloss in the other spelling. Heisig “judgment” repeats it and is not shown.
- 例にしていない語: 審判（しんぱん）

### 版（第8課）

- 例にしていない語: 出版（しゅっぱん）、絶版（ぜっぱん）

### 比（第8課）

- ヒの例は3語までです。残り1語は出していません。

### 肥（第8課）

- 例のない読み: こえ、こやす、こやし
- Added 肥える（こえる） for こえる from kml/data/compounds/lesson_98.json (肥えています is こ-える. こ-やす would be 肥やしています). Snippet: 谷の耕地は、狭いですが肥えています。

### 非（第9課）

- Both are KANJIDIC glosses. Heisig “non” matches the gloss “non-” and is not shown.
- 例にしていない語: 非常に（ひじょうに）
- ヒの例は3語までです。残り1語は出していません。

### 費（第9課）

- 例のない読み: ついやす、ついえる
- 例にしていない語: 出費（しゅっぴ）
- ヒの例は3語までです。残り1語は出していません。

### 備（第9課）

- 例のない読み: そなわる
- ビの例は3語までです。残り1語は出していません。

### 評（第9課）

- ヒョウの例は3語までです。残り2語は出していません。

### 布（第9課）

- 例にしていない語: 分布（ぶんぷ）
- 布地（ぬのじ）をぬのに付けました（compound）。

### 婦（第9課）

- フの例は3語までです。残り2語は出していません。

### 武（第9課）

- 例にしていない語: 文武両道（ぶんぶりょうどう）
- Added 武者（むしゃ） for ム from kml/data/compounds/lesson_100.json (武者 begins with ム. ブ would be ぶ). Snippet: 祭りの武者は、木の盾を持っています。
- ブの例は3語までです。残り1語は出していません。

### 復（第9課）

- 復旧（ふっきゅう）をフクに付けました（sokuon）。
- 復活（ふっかつ）をフクに付けました（sokuon）。
- フクの例は3語までです。残り2語は出していません。

### 複（第9課）

- フクの例は3語までです。残り2語は出していません。

### 粉（第9課）

- Added 葛粉（くずこ） for こ from kml/data/compounds/lesson_25.json (葛粉 ends with こ. こな is a different reading). Snippet: 母は和菓子に葛粉を使いました。
- 粉々（こなごな）をこなに付けました（compound）。

### 編（第9課）

- 例にしていない語: 短編（たんぺん）、編み物（あみもの）

### 弁（第9課）

- KANJIDIC2の古典部首は廾です。joyo_kanji.csv は辛で、辨・辯・瓣の部首です。カードは廾のままです。
- joyo_kanji.csv の部首欄は辛、カードは 廾（にじゅうあし）、出典 kanjidic
- ベンの例は3語までです。残り2語は出していません。

### 保（第9課）

- Added 保つ（たもつ） for たもつ from kml/data/compounds/lesson_83.json (保ちます is たも-つ). Snippet: 厨房は、常に清潔に保ちます。
- ホの例は3語までです。残り2語は出していません。

### 墓（第9課）

- 例にしていない語: 墓参り（はかまいり）、先祖の墓（せんぞのはか）
- 墓石（はかいし）をはかに付けました（compound）。

### 報（第9課）

- 例のない読み: むくいる
- 例にしていない語: 電報（でんぽう）
- ホウの例は3語までです。残り1語は出していません。

### 防（第9課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic

### 暴（第10課）

- 例のない読み: あばく
- 例にしていない語: 暴露（ばくろ）

### 脈（第10課）

- ミャクの例は3語までです。残り2語は出していません。

### 務（第10課）

- Both are KANJIDIC glosses. Heisig “duty” matches “duties” and is not shown.
- 例のない読み: つとまる
- 例にしていない語: 務め（つとめ）、事務所（じむしょ）、公務員（こうむいん）
- Added 務める（つとめる） for つとめる from kml/data/compounds/lesson_101.json (務めます is つと-める. つと-まる would be 務まります). Snippet: 式の司会は、校長が務めます。

### 夢（第10課）

- 初夢（はつゆめ）をゆめに付けました（compound）。

### 迷（第10課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic
- 例にしていない語: 迷子（まいご）

### 綿（第10課）

- 綿菓子（わたがし）をわたに付けました（compound）。

### 輸（第10課）

- ユの例は3語までです。残り2語は出していません。

### 余（第10課）

- KANJIDIC2の古典部首は人です。joyo_kanji.csv は食で、餘の部首です。カードは人のままです。
- joyo_kanji.csv の部首欄は食、カードは 人（ひと）、出典 kanjidic
- 例のない読み: あます
- 例にしていない語: 余り（あまり）

### 容（第10課）

- ヨウの例は3語までです。残り2語は出していません。

### 略（第10課）

- リャクの例は3語までです。残り2語は出していません。

### 留（第10課）

- 例のない読み: とまる
- 例にしていない語: 留守（るす）、停留所（ていりゅうじょ）

### 領（第10課）

- Both are KANJIDIC glosses. Heisig “territory” is the second gloss.
- リョウの例は3語までです。残り2語は出していません。

### 歴（第10課）

- 例にしていない語: 履歴書（りれきしょ）
- レキの例は3語までです。残り1語は出していません。

## 部首

The card uses the KANJIDIC2 classical radical, the same default as 10級 through 7級.
Japanese names for radicals new at this level come from KANJIDIC2 `rad_name` where that element exists: 廾 にじゅうあし, 支 しんよう（じゅうまたとも）, 殳 ほこつくり（るまたとも）, 耒 らいすき, 豕 いのこ.
比 くらべる, 片 かた, 玄 げん, and 臼 うす have no `rad_name`. The card uses the character’s ordinary reading.
非 あらず has no `rad_name`. あらず is the school name of radical 175.
罪 shows 罒（よんかしら）, the form inside the character. The classical head is 网.
示 prints 示（しめす） because the character is the radical. 社 uses 礻, the same classical radical.
These cards stay on the KANJIDIC2 radical where the joyo column names the radical of the traditional character: 弁 廾（辛, from 辨・辯・瓣）, 旧 日（臼, from 舊）, 舎 人（舌, from 舍）, 余 人（食, from 餘）, 営 口（火, from 營）.
象 stays 豕（いのこ）. That is the KANJIDIC2 classification, and the joyo column agrees.
着 is not in 6級. Its 8級 exception, 羊 rather than 目, is not copied onto other characters.
