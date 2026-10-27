# 漢検5級 vocabulary review

Learner pages do not explain these choices. The lesson covers are approved, including the lettering on 蒸 and 俵.
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
Bare readings remaining: 71.

Order is the 常用漢字表 掲載順. Lessons use the grade 6 熟語 film sizes: nine of 20 and one of 11.
Lessons 1–8 match those films. 補 stays before 暮, in 第9課. The films place 補 after 論, at the end of film 10.

The overview hero is 窓 `kml/assets/studies/window.jpg`.
Lesson covers are existing study images, one character from each lesson:

- 第1課 宇 `kml/assets/studies/eaves.jpg`
- 第2課 絹 `kml/assets/studies/silk.jpg`
- 第3課 紅 `kml/assets/studies/crimson.jpg`
- 第4課 若 `kml/assets/studies/young.jpg`
- 第5課 蒸 `kml/assets/studies/steam.jpg` — 蒸 is lettered on the banner
- 第6課 染 `kml/assets/studies/dye.jpg`
- 第7課 暖 `kml/assets/studies/warmth.jpg`
- 第8課 俵 `kml/assets/studies/bag.jpg` — 俵 is lettered on the wooden post
- 第9課 幕 `kml/assets/studies/curtain.jpg`
- 第10課 幼 `kml/assets/studies/infancy.jpg`

乳 `milk.jpg` is a spring labeled 乳白の泉, so it is not a cover. 泉 `spring.jpg` is a fountain. 卵 `egg.jpg` letters 卵; 第10課 uses 幼.
砂 `sand.jpg` is an hourglass in a lettered study, so it is not a cover.

## Cross-file examples

Each attached word contains its target character once, and the matcher locks that character’s reading.

## Kept

- 翌 stays “the following”. Heisig “following day” is the same sense in a fuller phrase.
- 署 stays “signature; government office”. “government office” spells out the gloss “govt office”.
- 枚 is “counter for flat objects”. That is an editorial paraphrase of the KANJIDIC gloss “counter for flat thin objects or sheets”, dropping “thin” and “or sheets”. Heisig “sheet of” is not shown.

## Held back

- 異 こと: 二つの地図は、境界が異なります. The segment reads 異 as こと, and なります is not okurigana of that bare reading, so it does not lock.
- 我 わ: lesson_112.html reads 我 in これ我が道. That is a classical inscription, so わ stays bare.
- 優 すぐれる: 藩校には、詩文に優れた才媛がいました. 藩校 and 才媛 are not learner wording.
- 討 うつ: 将軍は逆賊を討ちました and 海難の仇を討つ話. Both are historical tales, so うつ stays bare.
- 乱 みだれる: 詩人は世の乱れを歎いた. The sentence is literary, and the word is the noun 乱れ.
- 乳 ちち: lesson_40.html reads 乳のような泉 as ちち. That verse is poetic, so ちち stays bare.
- 否 いな: a nearby verse reads 否む, which is いなむ, not いな.
- 延 のべる: 延べ百人が展覧会に来ました. The segment is 延べ（のべ）, and the lock requires the full okurigana べる.
- 射 いる: 的を射ていました. 射て does not lock い-る.
- 危 あやぶむ: 出漁が危ぶまれます. 危ぶまれます does not lock あや-ぶむ, and the sentence uses 出漁.

## Needs review

### 胃（第1課）

- イの例は3語までです。残り3語は出していません。

### 異（第1課）

- 例のない読み: こと
- 例にしていない語: 異なる（ことなる）
- イの例は3語までです。残り1語は出していません。

### 遺（第1課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic

### 域（第1課）

- イキの例は3語までです。残り2語は出していません。

### 延（第1課）

- いんにょうとも呼ばれます。
- 例のない読み: のべる
- 例にしていない語: 延べ（のべ）
- Added 延びる（のびる） for のびる from kml/data/compounds/lesson_103.json (延びました is の-びる. の-べる would be 延べました. の-ばす would be 延ばしました). Snippet: 予算の審議は、夜まで延びました。
- Added 延ばす（のばす） for のばす from kml/data/compounds/lesson_104.json (延ばしました is の-ばす. The sentence uses 出漁. の-びる would be 延びました). Snippet: 荒天を避ける作戦で、出漁を一日延ばしました。
- エンの例は3語までです。残り1語は出していません。

### 沿（第1課）

- 例にしていない語: 川沿い（かわぞい）

### 恩（第1課）

- 例にしていない語: 恩返し（おんがえし）
- オンの例は3語までです。残り1語は出していません。

### 我（第1課）

- Both are KANJIDIC glosses. “I” alone hides 自我. Heisig “ego” is the second gloss.
- 例のない読み: わ
- 例にしていない語: 我が家（わがや）
- 我々（われわれ）をわれに付けました（compound）。

### 灰（第1課）

- 例にしていない語: 灰になる（はいになる）
- 灰皿（はいざら）をはいに付けました（compound）。
- 灰色（はいいろ）をはいに付けました（compound）。
- 火山灰（かざんばい）をはいに付けました（rendaku）。

### 拡（第1課）

- カクの例は3語までです。残り2語は出していません。

### 革（第1課）

- かくのかわとも呼ばれます。
- Added 革（かわ） for かわ from kml/contents/books/book_01/lessons/lesson_140.html (The verse reads 革 as かわ in 古い革の鞄, and its English is “the old leather bag”). Snippet: shine on the old leather bag。
- カクの例は3語までです。残り1語は出していません。

### 割（第1課）

- 例のない読み: カツ、さく
- 割合（わりあい）をわりに付けました（compound）。
- 割算（わりざん）をわりに付けました（compound）。
- 役割（やくわり）をわりに付けました（compound）。

### 株（第1課）

- 例にしていない語: 切り株（きりかぶ）
- 株式（かぶしき）をかぶに付けました（compound）。
- 株価（かぶか）をかぶに付けました（compound）。
- 株主（かぶぬし）をかぶに付けました（compound）。
- かぶの例は3語までです。残り1語は出していません。

### 干（第1課）

- 例のない読み: ひる
- 例にしていない語: 干物（ひもの）

### 巻（第1課）

- KANJIDIC2の古典部首は己です。joyo_kanji.csv は卩で、卷の部首です。カードは己のままです。
- joyo_kanji.csv の部首欄は卩、カードは 己（おのれ）、出典 kanjidic
- Added 巻末（かんまつ） for カン from kml/data/compounds/lesson_97.json (巻末 is カン. ま-く would be 巻く. まき would be 巻). Snippet: 作家の年譜を、巻末で確認しました。
- 巻物（まきもの）をまきに付けました（compound）。
- 寝巻（ねまき）をまきに付けました（compound）。
- 巻貝（まきがい）をまきに付けました（compound）。

### 看（第1課）

- 例にしていない語: 看取る（みとる）
- カンの例は3語までです。残り1語は出していません。

### 簡（第1課）

- カンの例は3語までです。残り1語は出していません。

### 危（第2課）

- 例のない読み: あやぶむ

### 机（第2課）

- 学習机（がくしゅうづくえ）をつくえに付けました（rendaku）。
- 文机（ふづくえ）をつくえに付けました（rendaku）。

### 揮（第2課）

- 例にしていない語: 指揮者（しきしゃ）、采配を揮う（さいはいをふるう）

### 貴（第2課）

- 例のない読み: たっとい、たっとぶ、とうとぶ

### 疑（第2課）

- ギの例は3語までです。残り1語は出していません。

### 吸（第2課）

- キュウの例は3語までです。残り1語は出していません。

### 供（第2課）

- Both are KANJIDIC glosses. The first gloss “submit” hides 提供. Heisig “offer” is the second gloss.
- 例にしていない語: お供（おとも）
- Added 供える（そなえる） for そなえる from kml/data/compounds/lesson_32.json (供えます is そな-える. とも is a different reading). Snippet: 朝、仏壇に水を供えます。
- 子供（こども）をともに付けました（rendaku）。

### 郷（第2課）

- KANJIDIC gloss “home town”. Heisig “hometown” is the same wording.
- 古典部首は邑です。都・部にある形は阝です。
- joyo_kanji.csv の部首欄は邑、カードは 阝（おおざと）、出典 kanjidic
- 例のない読み: ゴウ
- 例にしていない語: 故郷（ふるさと）
- キョウの例は3語までです。残り1語は出していません。

### 勤（第2課）

- 例のない読み: つとまる
- 例にしていない語: 勤め（つとめ）

### 筋（第2課）

- 一筋（ひとすじ）をすじに付けました（compound）。
- 大筋（おおすじ）をすじに付けました（compound）。
- 粗筋（あらすじ）をすじに付けました（compound）。
- すじの例は3語までです。残り1語は出していません。

### 敬（第2課）

- KANJIDIC gloss “respect”. The first gloss “awe” is the same sense. Heisig “awe” is that gloss and is not shown.
- 古典部首は攴です。教・数にある形は攵です。
- joyo_kanji.csv の部首欄は攴、カードは 攵（のぶん）、出典 kanjidic
- 例のない読み: うやまう
- ケイの例は3語までです。残り2語は出していません。

### 警（第2課）

- ケイの例は3語までです。残り2語は出していません。

### 激（第2課）

- ゲキの例は3語までです。残り1語は出していません。

### 穴（第2課）

- 例にしていない語: 落とし穴（おとしあな）
- Added 虎穴（こけつ） for ケツ from a KML compound filed under another character (end).
- 洞穴（ほらあな）をあなに付けました（compound）。
- 鍵穴（かぎあな）をあなに付けました（compound）。

### 券（第2課）

- ケンの例は3語までです。残り2語は出していません。

### 絹（第2課）

- 例のない読み: ケン
- 絹糸（きぬいと）をきぬに付けました（compound）。

### 権（第2課）

- Both are KANJIDIC glosses. “authority” alone hides 権利. Heisig “rights” is the second gloss.
- ケンの例は3語までです。残り2語は出していません。

### 源（第3課）

- Added 源（みなもと） for みなもと from kml/contents/books/book_01/lessons/lesson_98.html (The verse reads 源 as みなもと in 清らかな源は, and its English is “A pure source”). Snippet: A pure source never runs dry。
- ゲンの例は3語までです。残り2語は出していません。

### 厳（第3課）

- KANJIDIC2の古典部首は厂です。joyo_kanji.csv は口で、嚴の部首です。カードは厂のままです。
- joyo_kanji.csv の部首欄は口、カードは 厂（がんだれ）、出典 kanjidic
- 例のない読み: おごそか

### 己（第3課）

- 例にしていない語: 利己的（りこてき）

### 呼（第3課）

- 例にしていない語: 呼び出す（よびだす）、呼び掛ける（よびかける）、呼び止める（よびとめる）

### 后（第3課）

- 例にしていない語: 皇后（こうごう）

### 孝（第3課）

- 例にしていない語: 親孝行（おやこうこう）

### 皇（第3課）

- 例のない読み: オウ
- 例にしていない語: 天皇（てんのう）
- コウの例は3語までです。残り1語は出していません。

### 紅（第3課）

- 例にしていない語: 紅葉（もみじ）、紅葉狩り（もみじがり）
- Added 紅（くれない） for くれない from kml/contents/books/book_01/lessons/lesson_32.html (The verse reads 紅 as くれない in 紅の葉, and its English is “a crimson leaf”. べに is a different reading). Snippet: floated a crimson leaf。
- 口紅（くちべに）をべにに付けました（compound）。

### 降（第3課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic

### 刻（第3課）

- コクの例は3語までです。残り1語は出していません。

### 骨（第3課）

- KANJIDIC gloss “bone”. The first gloss “skeleton” is a narrower sense. Heisig “bone” is this gloss.
- 骨折（こっせつ）をコツに付けました（sokuon）。
- 骨董品（こっとうひん）をコツに付けました（sokuon）。
- コツの例は3語までです。残り1語は出していません。

### 困（第3課）

- コンの例は3語までです。残り1語は出していません。

### 砂（第3課）

- 例のない読み: シャ
- 例にしていない語: 砂利（じゃり）

### 座（第3課）

- Both are KANJIDIC glosses. The first gloss “squat” is not the learner sense of 座る. Heisig “sit” is the gloss “sit”.
- ザの例は3語までです。残り1語は出していません。

### 済（第3課）

- 例にしていない語: 経済（けいざい）、済ませる（すませる）
- Added 済ます（すます） for すます from kml/data/compounds/lesson_64.json (済ませて is す-ます. す-む would be 済んで). Snippet: 駅の前で用事を済ませてから帰りました。

### 裁（第3課）

- Both are KANJIDIC glosses. “judge” is placed first for 裁判. “tailor” remains for 裁つ. Heisig “judge” is the gloss “judge”.
- 例のない読み: たつ
- Added 裁く（さばく） for さばく from kml/data/compounds/lesson_42.json (裁き is さば-く. た-つ would be 裁つ). Snippet: 裁きは感情ではなく、公允でなければならないと先輩は言った。
- サイの例は3語までです。残り2語は出していません。

### 策（第4課）

- サクの例は3語までです。残り1語は出していません。

### 冊（第4課）

- KANJIDIC gloss “volume”. The first gloss “tome” is rare in learner English. Heisig “volume” is this gloss.
- 例のない読み: サク

### 蚕（第4課）

- サンの例は3語までです。残り1語は出していません。

### 至（第4課）

- 例にしていない語: 冬至（とうじ）

### 私（第4課）

- Both are KANJIDIC glosses. “private” alone hides the reading of 私 as “I”. Heisig “me” restates “I” and is not shown.

### 姿（第4課）

- 例にしていない語: 後ろ姿（うしろすがた）、立ち姿（たちすがた）

### 視（第4課）

- シの例は3語までです。残り2語は出していません。

### 詞（第4課）

- シの例は3語までです。残り2語は出していません。

### 誌（第4課）

- シの例は3語までです。残り2語は出していません。

### 射（第4課）

- 例のない読み: いる
- 例にしていない語: 射す（さす）、陽射し（ひざし）

### 捨（第4課）

- 例にしていない語: 取捨選択（しゅしゃせんたく）

### 若（第4課）

- joyo_kanji.csv の部首欄は艸、カードは 艹（くさかんむり）、出典 kanjidic
- 例のない読み: もしくは
- 例にしていない語: 若者（わかもの）、若返る（わかがえる）、若葉（わかば）

### 樹（第4課）

- 例にしていない語: 果樹園（かじゅえん）

### 収（第4課）

- KANJIDIC2の古典部首は又です。joyo_kanji.csv は攴で、收の部首です。カードは又のままです。
- joyo_kanji.csv の部首欄は攴、カードは 又（また）、出典 kanjidic
- 例のない読み: おさまる
- シュウの例は3語までです。残り1語は出していません。

### 宗（第4課）

- 例のない読み: ソウ

### 就（第4課）

- もっともとも呼ばれます。
- 例のない読み: つく、つける

### 衆（第4課）

- シュウの例は3語までです。残り1語は出していません。

### 従（第4課）

- Both are KANJIDIC glosses. The first gloss “accompany” is 従える. Heisig “obey” is the gloss “obey”.
- 例のない読み: したがえる
- 例にしていない語: 従兄弟（いとこ）、従姉妹（いとこ）

### 縦（第5課）

- 例にしていない語: 縦書き（たてがき）、恣縦（ししょう）
- Added 縦（たて） for たて from kml/contents/books/book_01/lessons/lesson_72.html (The verse reads 縦 as たて in 高い杉が縦に伸び, and its English is “Tall cedars rise straight upward”). Snippet: Tall cedars rise straight upward,。

### 縮（第5課）

- 例のない読み: ちぢまる、ちぢれる、ちぢらす

### 熟（第5課）

- KANJIDIC gloss “ripen”. The first gloss “mellow” is a narrower sense. Heisig “ripe” is not a gloss and is not shown.
- 例のない読み: うれる
- 熟考（じゅっこう）をジュクに付けました（sokuon）。
- ジュクの例は3語までです。残り2語は出していません。

### 純（第5課）

- ジュンの例は3語までです。残り2語は出していません。

### 処（第5課）

- KANJIDIC2の古典部首は几です。joyo_kanji.csv は虍で、處の部首です。KANJIDICのネルソン部首は夂です。カードは几のままです。
- joyo_kanji.csv の部首欄は虍、カードは 几（つくえ）、出典 kanjidic
- ショの例は3語までです。残り2語は出していません。

### 署（第5課）

- “signature” is a KANJIDIC gloss. “government office” spells out the gloss “govt office”. Heisig “government bureau” is not a gloss and is not shown.
- 古典部首は网（あみがしら）です。署にある形は罒です。
- joyo_kanji.csv の部首欄は网、カードは 罒（よんかしら）、出典 kanjidic

### 除（第5課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic
- 例にしていない語: 掃除（そうじ）

### 承（第5課）

- 例のない読み: うけたまわる

### 将（第5課）

- ショウの例は3語までです。残り2語は出していません。

### 傷（第5課）

- 例にしていない語: 火傷（やけど）
- Added 傷む（いたむ） for いたむ from kml/data/compounds/lesson_104.json (傷みやすい is いた-む. いた-める would be 傷め). Snippet: 港の住宅は、潮風で傷みやすいです。
- 傷口（きずぐち）をきずに付けました（compound）。

### 障（第5課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic
- ショウの例は3語までです。残り1語は出していません。

### 蒸（第5課）

- joyo_kanji.csv の部首欄は艸、カードは 艹（くさかんむり）、出典 kanjidic
- 例のない読み: むれる、むらす

### 針（第5課）

- 例にしていない語: 時計の針（とけいのはり）
- 針金（はりがね）をはりに付けました（compound）。
- 注射針（ちゅうしゃばり）をはりに付けました（rendaku）。

### 仁（第5課）

- 例のない読み: ジン
- 例にしていない語: 仁王（におう）、杏仁（あんにん）

### 垂（第5課）

- Added 垂らす（たらす） for たらす from kml/data/compounds/lesson_102.json (垂らしています is た-らす. た-れる would be 垂れています). Snippet: 余暇には、川で糸を垂らしています。

### 推（第5課）

- Both are KANJIDIC glosses. The first gloss “conjecture” is the same sense as “infer”. Heisig “infer” is this gloss.
- 例のない読み: おす
- スイの例は3語までです。残り2語は出していません。

### 寸（第5課）

- 例にしていない語: 一寸（ちょっと）
- スンの例は3語までです。残り2語は出していません。

### 盛（第5課）

- 例のない読み: さかる
- 例にしていない語: 盛り（さかり）

### 聖（第5課）

- セイの例は3語までです。残り2語は出していません。

### 誠（第6課）

- 例にしていない語: 真心誠意（まごころせいい）、誠心誠意（せいしんせいい）

### 舌（第6課）

- 例にしていない語: 舌打ち（したうち）
- 二枚舌（にまいじた）をしたに付けました（rendaku）。

### 宣（第6課）

- センの例は3語までです。残り2語は出していません。

### 専（第6課）

- 例のない読み: もっぱら
- センの例は3語までです。残り3語は出していません。

### 泉（第6課）

- Added 泉（いずみ） for いずみ from kml/contents/books/book_01/lessons/lesson_76.html (The verse reads 泉 as いずみ in 山の泉が湧き, and its English is “A mountain spring”). Snippet: A mountain spring wells up,。
- センの例は3語までです。残り2語は出していません。

### 洗（第6課）

- 例にしていない語: 手洗い（てあらい）、丸洗い（まるあらい）
- Added 洗う（あらう） for あらう from kml/data/compounds/lesson_07.json (洗いました is あら-う). Snippet: 夕食の後で食器を洗いました。

### 染（第6課）

- 例のない読み: しみる、しみ
- 例にしていない語: 伝染病（でんせんびょう）
- Added 染まる（そまる） for そまる from kml/data/compounds/lesson_125.json (染まった is そ-まる. そ-める would be 染めた. し-みる would be 染みる). Snippet: 西の空が茜に染まった。

### 銭（第6課）

- 小銭（こぜに）をぜにに付けました（compound）。
- 銭形（ぜにがた）をぜにに付けました（compound）。

### 善（第6課）

- 例のない読み: よい
- ゼンの例は3語までです。残り2語は出していません。

### 奏（第6課）

- 例のない読み: かなでる
- 例にしていない語: 吹奏楽（すいそうがく）

### 窓（第6課）

- 窓口（まどぐち）をまどに付けました（compound）。
- 天窓（てんまど）をまどに付けました（compound）。
- 出窓（でまど）をまどに付けました（compound）。
- まどの例は3語までです。残り1語は出していません。

### 創（第6課）

- 例のない読み: つくる
- ソウの例は3語までです。残り2語は出していません。

### 装（第6課）

- Added 衣装（いしょう） for ショウ from a KML compound filed under another character (end).
- Added 装う（よそおう） for よそおう from kml/data/compounds/lesson_153.json (装い is よそお-う). Snippet: 清楚な装いが式に似合う。
- ソウの例は3語までです。残り2語は出していません。

### 層（第6課）

- ソウの例は3語までです。残り2語は出していません。

### 操（第6課）

- 例のない読み: みさお
- ソウの例は3語までです。残り1語は出していません。

### 蔵（第6課）

- joyo_kanji.csv の部首欄は艸、カードは 艹（くさかんむり）、出典 kanjidic
- 例にしていない語: 冷蔵庫（れいぞうこ）

### 臓（第6課）

- ゾウの例は3語までです。残り1語は出していません。

### 存（第6課）

- KANJIDIC gloss “exist”. Heisig “remain” is not a gloss and is not shown.
- 例にしていない語: ご存じ（ごぞんじ）

### 尊（第6課）

- 例のない読み: たっとい、たっとぶ
- 例にしていない語: 自尊心（じそんしん）

### 退（第6課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic
- 例のない読み: しりぞける
- 例にしていない語: 退く（どく）
- Added 退く（しりぞく） for しりぞく from kml/data/compounds/lesson_79.json (退いて is しりぞ-く. しりぞ-ける would be 退けて). Snippet: 車が来るので、道から退いてください。
- タイの例は3語までです。残り1語は出していません。

### 担（第7課）

- Added 担ぐ（かつぐ） for かつぐ from kml/data/compounds/lesson_149.json (担いだ is かつ-ぐ. にな-う would be 担う). Snippet: 逞しい腕で荷物を担いだ。
- タンの例は3語までです。残り1語は出していません。

### 誕（第7課）

- 例にしていない語: 聖誕祭（せいたんさい）
- タンの例は3語までです。残り1語は出していません。

### 段（第7課）

- るまたとも呼ばれます。
- ダンの例は3語までです。残り2語は出していません。

### 暖（第7課）

- 例のない読み: あたたまる、あたためる
- Added 暖かい（あたたかい） for あたたか from kml/data/compounds/lesson_78.json (暖かい is あたた-か. あたた-まる would be 暖まる. あたた-める would be 暖める). Snippet: 猫は暖かい場所を喜びます。

### 値（第7課）

- Both are KANJIDIC glosses. Heisig “value” is the second gloss.
- 例にしていない語: 値打ち（ねうち）
- 値段（ねだん）をねに付けました（compound）。

### 宙（第7課）

- Both are KANJIDIC glosses. “mid-air” alone hides 宇宙. Heisig “midair” restates the first gloss and is not shown.
- 例にしていない語: 宙返り（ちゅうがえり）

### 忠（第7課）

- チュウの例は3語までです。残り2語は出していません。

### 著（第7課）

- joyo_kanji.csv の部首欄は艸、カードは 艹（くさかんむり）、出典 kanjidic
- 例のない読み: いちじるしい
- チョの例は3語までです。残り1語は出していません。

### 庁（第7課）

- チョウの例は3語までです。残り2語は出していません。

### 頂（第7課）

- Both are KANJIDIC glosses. The first gloss “place on the head” is the same sense as “top” in longer wording. Heisig “top” is the gloss “top”.
- Added 頂（いただき） for いただき from kml/contents/books/book_01/lessons/lesson_86.html (The verse reads 頂 as いただき, and its English is “the summit”. いただ-く would be 頂く). Snippet: the summit draws near。

### 腸（第7課）

- チョウの例は3語までです。残り2語は出していません。

### 潮（第7課）

- 潮風（しおかぜ）をしおに付けました（compound）。
- 高潮（たかしお）をしおに付けました（compound）。

### 痛（第7課）

- 例にしていない語: 痛み（いたみ）
- Added 痛む（いたむ） for いたむ from kml/data/compounds/lesson_13.json (痛みました is いた-む. いた-める would be 痛めました. いた-い would be 痛かった). Snippet: 大きな音で鼓膜が痛みました。
- Added 痛める（いためる） for いためる from kml/data/compounds/lesson_14.json (痛めました is いた-める. いた-む would be 痛みました). Snippet: 転んで脊椎を痛めました。

### 敵（第7課）

- 古典部首は攴です。教・数にある形は攵です。
- joyo_kanji.csv の部首欄は攴、カードは 攵（のぶん）、出典 kanjidic
- 例のない読み: かたき
- テキの例は3語までです。残り2語は出していません。

### 討（第7課）

- 例のない読み: うつ
- トウの例は3語までです。残り2語は出していません。

### 党（第7課）

- KANJIDIC gloss “party”. Heisig “political party” is the longer form of this gloss and is not shown.
- KANJIDIC2の古典部首は儿です。joyo_kanji.csv は黑で、黨の部首です。カードは儿のままです。
- joyo_kanji.csv の部首欄は黑、カードは 儿（ひとあし）、出典 kanjidic
- トウの例は3語までです。残り2語は出していません。

### 届（第8課）

- 例にしていない語: 欠席届（けっせきとどけ）、届（とどけ）、婚姻届（こんいんとどけ）

### 難（第8課）

- 例のない読み: かたい
- ナンの例は3語までです。残り1語は出していません。

### 乳（第8課）

- 例のない読み: ちち、ち
- ニュウの例は3語までです。残り2語は出していません。

### 認（第8課）

- ニンの例は3語までです。残り1語は出していません。

### 納（第8課）

- 例のない読み: おさまる
- 例にしていない語: 納豆（なっとう）、納得（なっとく）

### 拝（第8課）

- 例にしていない語: 参拝（さんぱい）

### 背（第8課）

- Both are KANJIDIC glosses. The first gloss “stature” hides 背中. Heisig “back” is the gloss “back”.
- 例のない読み: せい、そむく、そむける
- 例にしていない語: 背負う（せおう）
- 背中（せなか）をせに付けました（compound）。
- 背丈（せたけ）をせに付けました（compound）。
- 背広（せびろ）をせに付けました（compound）。

### 肺（第8課）

- 例にしていない語: 肺がん（はいがん）、心肺（しんぱい）

### 否（第8課）

- 例のない読み: いな
- 例にしていない語: 否（いや）
- ヒの例は3語までです。残り1語は出していません。

### 批（第8課）

- ヒの例は3語までです。残り1語は出していません。

### 秘（第8課）

- KANJIDIC2の古典部首は禾です。joyo_kanji.csv は示で、祕の部首です。カードは禾のままです。
- joyo_kanji.csv の部首欄は示、カードは 禾（のぎ）、出典 kanjidic
- 例のない読み: ひめる
- 例にしていない語: 神秘（しんぴ）

### 俵（第8課）

- Added 俵（たわら） for たわら from kml/data/compounds/lesson_124.json (俵を is たわら). Snippet: 俵を藁で編んだ。

### 腹（第8課）

- 例にしていない語: 満腹（まんぷく）

### 奮（第8課）

- 例のない読み: ふるう
- フンの例は3語までです。残り2語は出していません。

### 並（第9課）

- KANJIDIC2の古典部首は一です。joyo_kanji.csv は立です。カードは一のままです。
- joyo_kanji.csv の部首欄は立、カードは 一（いち）、出典 kanjidic
- 例のない読み: ならびに
- 並木（なみき）をなみに付けました（compound）。

### 陛（第9課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic

### 閉（第9課）

- 例のない読み: とざす

### 片（第9課）

- 例のない読み: ヘン
- 例にしていない語: 片付く（かたづく）、片付け（かたづけ）、片付ける（かたづける）
- 片道（かたみち）をかたに付けました（compound）。
- 片仮名（かたかな）をかたに付けました（compound）。

### 補（第9課）

- ホの例は3語までです。残り1語は出していません。

### 暮（第9課）

- Both are KANJIDIC glosses. “evening” alone hides 暮らす. Heisig “livelihood” is the second gloss.
- 例のない読み: ボ
- 例にしていない語: 暮らし（くらし）、夕暮れ（ゆうぐれ）、年暮れ（としくれ）

### 宝（第9課）

- 宝物（たからもの）をたからに付けました（compound）。
- ホウの例は3語までです。残り1語は出していません。

### 訪（第9課）

- 例にしていない語: 探訪（たんぼう）
- Added 訪ねる（たずねる） for たずねる from kml/data/compounds/lesson_09.json (訪ねました is たず-ねる. おとず-れる would be 訪れました). Snippet: 旅の途中で静かな古寺を訪ねました。

### 亡（第9課）

- 例のない読み: ない
- 例にしていない語: 未亡人（みぼうじん）
- ボウの例は3語までです。残り1語は出していません。

### 忘（第9課）

- 例にしていない語: 物忘れ（ものわすれ）、健忘症（けんぼうしょう）、備忘録（びぼうろく）

### 枚（第9課）

- “counter for flat objects” is an editorial paraphrase of the KANJIDIC gloss “counter for flat thin objects or sheets”, dropping “thin” and “or sheets”. 大辞泉 describes 枚 as the counter for thin flat things such as paper, boards, and plates. Heisig “sheet of” restates the unfinished gloss “sheet of...” and is not shown.
- マイの例は3語までです。残り2語は出していません。

### 幕（第9課）

- マクの例は3語までです。残り1語は出していません。

### 密（第9課）

- 密集（みっしゅう）をミツに付けました（sokuon）。
- 密室（みっしつ）をミツに付けました（sokuon）。

### 模（第9課）

- 例のない読み: ボ
- モの例は3語までです。残り2語は出していません。

### 訳（第9課）

- 例にしていない語: 訳す（やくす）

### 郵（第9課）

- 古典部首は邑です。都・部にある形は阝です。
- joyo_kanji.csv の部首欄は邑、カードは 阝（おおざと）、出典 kanjidic

### 優（第9課）

- 例のない読み: すぐれる
- ユウの例は3語までです。残り1語は出していません。

### 幼（第10課）

- ようへんとも呼ばれます。
- ヨウの例は3語までです。残り1語は出していません。

### 欲（第10課）

- 例のない読み: ほっする
- 例にしていない語: 欲張り（よくばり）

### 翌（第10課）

- KANJIDIC gloss “the following”. Heisig “following day” is the same sense in a fuller phrase. The shorter gloss stays.
- ヨクの例は3語までです。残り2語は出していません。

### 乱（第10課）

- 例のない読み: みだれる、みだす
- 例にしていない語: 乱（みだれ）
- ランの例は3語までです。残り1語は出していません。

### 卵（第10課）

- 例にしていない語: 卵焼き（たまごやき）

### 覧（第10課）

- 例にしていない語: 展覧会（てんらんかい）
- ランの例は3語までです。残り1語は出していません。

### 裏（第10課）

- Both are KANJIDIC glosses. “reverse” is placed first so the card is not only “back”, which is also 背. Heisig “reverse side” restates “reverse” and is not shown.
- 裏側（うらがわ）をうらに付けました（compound）。
- 裏口（うらぐち）をうらに付けました（compound）。
- 裏表（うらおもて）をうらに付けました（compound）。
- 裏庭（うらにわ）をうらに付けました（compound）。
- うらの例は3語までです。残り1語は出していません。

### 律（第10課）

- Both are KANJIDIC glosses. The first gloss “rhythm” hides 法律. Heisig “law” is the gloss “law”.
- 例にしていない語: 呂律（ろれつ）
- リツの例は3語までです。残り1語は出していません。

### 論（第10課）

- 例にしていない語: 論じる（ろんじる）
- ロンの例は3語までです。残り1語は出していません。

## 部首

The card uses the KANJIDIC2 classical radical, the same default as 10級 through 6級.
Japanese names for radicals new at this level come from KANJIDIC2 `rad_name` where that element exists: 几 つくえ, 尢 だいのまげあし（もっともとも）, 幺 いとがしら（ようへんとも）.
己 おのれ, 至 いたる, 舌 した, and 骨 ほね have no `rad_name`. The card uses the character’s ordinary reading.
疋 ひき has no `rad_name`. ひき is the school name of radical 103.
革 かわ has no `rad_name`. かわ is the reading of the radical character. かくのかわ is the other name.
署 shows 罒（よんかしら）, the form inside the character. The classical head is 网.
These cards stay on the KANJIDIC2 radical where the joyo column names the radical of the traditional character: 厳 厂（口, from 嚴）, 収 又（攴, from 收）, 党 儿（黑, from 黨）, 秘 禾（示, from 祕）, 巻 己（卩, from 卷）, 処 几（虍, from 處）.
処 also has Nelson radical 夂 in KANJIDIC2. The card stays 几.
並 stays 一（いち）. The joyo column says 立. The card stays on the KANJIDIC2 radical.
辶, 阝, 攵, and 艹 on these cards are the printed forms of 辵, 阜 or 邑, 攴, and 艸.
着 is not in 5級. Its 8級 exception, 羊 rather than 目, is not copied onto other characters.
