# 漢検3級 vocabulary review

Learner pages do not explain these choices. The covers are approved, including lettering.
Nothing here has been deployed.

KANJIDIC2 2026-074, 2026-03-15.
English on a card is the first KANJIDIC2 gloss, unless MEANING_CHOICES names a clearer gloss from that same list, a Heisig keyword, or a marked paraphrase.
A displayed meaning tagged kanjidic is that exact gloss. A paraphrase is editorial. A meaning tagged heisig is that keyword used as the card wording.
Heisig stays on its own line only when the keyword is not already the displayed wording.
Readings are the 常用漢字表 音訓. Parentheses are the table’s indented readings.
Example words come from `kml/data/compounds/`. A word filed under another character is used only when
the same matcher used on 8級 locks it to that reading, and the word is a verb or a headword of at most three kanji.
One-mora on readings are not filled that way. A dictionary form is added only when a sentence segment
locks that exact reading. A reading with no suitable word stays bare.
Bare readings remaining: 61.

Order is the 常用漢字表 掲載順 of the 284 grade-S characters at 漢検3級.
There is no 3級 school-film cut. Lessons are ten of 20 and four of 21.
The music link is the existing post-elementary collection, shared by 漢検4級 through 漢検2級.

The overview hero is 鯨 `kml/assets/studies/whale.jpg`. It is in 第4課 and is not that lesson’s cover.
Lesson covers are existing study images, one character from each lesson:

- 第1課 炎 `kml/assets/studies/inflammation.jpg` — native 16:9 at 1535×863
- 第2課 岳 `kml/assets/studies/mountain_peak.jpg` — 山頂 is lettered on the post
- 第3課 棋 `kml/assets/studies/chess_piece.jpg`
- 第4課 鶏 `kml/assets/studies/chicken.jpg`
- 第5課 郊 `kml/assets/studies/outskirts.jpg` — 郊 is lettered on the sign
- 第6課 侍 `kml/assets/studies/waiter.jpg` — 心 is lettered on the scroll
- 第7課 鐘 `kml/assets/studies/bell.jpg` — vertical text is lettered on the pillar
- 第8課 瀬 `kml/assets/studies/rapids.jpg` — 瀬 is lettered on the rock
- 第9課 葬 `kml/assets/studies/burial.jpg` — 南無阿弥陀仏 is lettered on the stone
- 第10課 彫 `kml/assets/studies/carve.jpg` — 彫 is lettered on the sign
- 第11課 豚 `kml/assets/studies/pork.jpg`
- 第12課 封 `kml/assets/studies/seal.jpg`
- 第13課 墨 `kml/assets/studies/black_ink.jpg` — 墨 is lettered on the paper
- 第14課 湾 `kml/assets/studies/gulf.jpg`

Not used: 穫 `harvest.jpg` carries a long vertical text.

## Cross-file examples

Each attached word contains its target character once, and the matcher locks that character’s reading.
A dictionary form is added when a sentence segment or a verse ruby locks that exact reading.
A reading without that lock stays bare.

## Kept

- Clearer exact KANJIDIC glosses, with the Heisig line omitted when it restates the card: 架 frame; shelf, 岳 peak; mountain, 恨 regret; resentment, 施 give; alms, 穂 ear (grain), 葬 bury, 奉 offer; dedicate, 乏 scarce, 揚 raise; hoist, 了 complete; finish, 乙 the latter; strange, 駐 reside in; resident, 陪 accompany; attend on, 幽 secluded; faint.
- 厘 is “rin; thousandth”. “rin” is the KANJIDIC gloss. “thousandth” is the Heisig keyword. No separate Heisig line.
- Context still changes the sense: 乙（甲乙 / 乙な / the fishhook shape）, 駐（駐在 / 駐車）, 陪（attend / 陪審）, 幽（幽閉 / 幽玄 / 幽霊）, 厘（a thousandth / 1/10 sen / 1/10 bu）.
- First gloss kept, Heisig not shown: 遇 meet, 掲 put up (a notice), 紺 dark blue, 墾 ground-breaking, 昇 rise up, 掌 palm of hand, 随 follow, 胆 gall bladder, 陳 exhibit.

## Held back

- 湿（しめす） is the reading behind the reported “示す”. 示 is 常用漢字表 grade 5 and is not in 漢検3級. No KML sentence locks 湿す, so しめす stays bare.
- 請（うける） is the reading behind the reported “受ける”. 受 is grade 3 and is not in 漢検3級. 茶請け（ちゃうけ） does not lock う-ける. That reading stays bare. こう is a separate reading and has its own example.
- 換（かわる）, 緩（ゆるめる）, 憎（にくい）, 滞（とどこおる）, 崩（くずす）, 膨（ふくれる）, 謀（はかる）, and 超（こす） have no sentence that locks the character and that reading.
- 揺（ゆさぶる） locks in 入札の醜聞が、組合の信用を揺さぶりました, and 揺（ゆする） locks in 嵐は乾坤を揺する勢いで、船を押し流しました. Both are uncommon wording, so they stay bare.
- 悔（くいる） locks in 若気の放蕩を今は悔いている. The wording is old-fashioned, so it stays bare.
- 緩（ゆるやか） is read ゆる in 曼たる動きは、時まで緩やかにする. The line is figurative, so it stays bare.

## Needs review

### 哀（第1課）

- 例のない読み: あわれむ
- アイの例は3語までです。残り1語は出していません。

### 慰（第1課）

- 例のない読み: なぐさむ

### 詠（第1課）

- エイの例は3語までです。残り1語は出していません。

### 悦（第1課）

- 例にしていない語: 悦に入る（えつにいる）
- 悦服（えっぷく）をエツに付けました（sokuon）。
- 悦声（えっせい）をエツに付けました（sokuon）。
- エツの例は3語までです。残り1語は出していません。

### 炎（第1課）

- 例にしていない語: 怒りの炎（いかりのほのお）
- Added 炎（ほのお） for ほのお from kml/contents/books/book_01/lessons/lesson_16.html (The verse reads 炎 as ほのお, and its English is “Within the quiet time around fire”). Snippet: Within the quiet time around fire,。
- エンの例は3語までです。残り1語は出していません。

### 宴（第1課）

- 例にしていない語: 大宴会（だいえんかい）
- エンの例は3語までです。残り1語は出していません。

### 殴（第1課）

- るまたとも呼ばれます。

### 乙（第1課）

- Both are KANJIDIC glosses, and the sense depends on context. 甲乙 is “the latter”. 乙な is “strange”, or the gloss “witty”. “duplicate” and “fishhook radical (no. 5)” are other glosses and are not on the card. Heisig “hook” names the shape and is not a gloss.
- 例にしていない語: 乙女（おとめ）
- オツの例は3語までです。残り1語は出していません。

### 卸（第1課）

- 卸値（おろしね）をおろしに付けました（compound）。
- 卸売（おろしうり）をおろしに付けました（compound）。

### 架（第1課）

- Both are KANJIDIC glosses. The first gloss “erect” is a verb sense. Heisig “rack” is not a gloss.
- Added 架かる（かかる） for かかる from kml/contents/books/book_01/lessons/lesson_97.html (架かった is か-かる. か-ける would be 架けた. The verse’s English is “a quiet rainbow stretches across the sky”). Snippet: a quiet rainbow stretches across the sky。

### 華（第1課）

- joyo_kanji.csv の部首欄は艸、カードは 艹（くさかんむり）、出典 kanjidic
- 例にしていない語: 華やか（はなやか）、華奢（きゃしゃ）、華々しい（はなばなしい）
- Added 華（はな） for はな from kml/contents/books/book_01/lessons/lesson_86.html (The verse reads 華 as はな in the line whose English is “Wildflowers bloom beautifully”). Snippet: Wildflowers bloom beautifully,。

### 嫁（第1課）

- 例のない読み: カ
- 例にしていない語: 嫁入り（よめいり）、良い嫁（よいよめ）
- 花嫁（はなよめ）をよめに付けました（compound）。

### 怪（第1課）

- 例のない読み: あやしむ
- 例にしていない語: 怪我（けが）

### 悔（第1課）

- 例のない読み: くいる
- 例にしていない語: 懺悔（ざんげ）

### 塊（第1課）

- 例のない読み: カイ
- 一塊（ひとかたまり）をかたまりに付けました（compound）。

### 概（第2課）

- ガイの例は3語までです。残り2語は出していません。

### 郭（第2課）

- 古典部首は邑です。都・部にある形は阝です。
- joyo_kanji.csv の部首欄は邑、カードは 阝（おおざと）、出典 kanjidic

### 隔（第2課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic

### 穫（第2課）

- 例にしていない語: 収穫量（しゅうかくりょう）

### 岳（第2課）

- Both are KANJIDIC glosses. The first gloss “point” hides the mountain. Heisig “mountain peak” restates these glosses and is not shown.
- Added 岳（たけ） for たけ from kml/contents/books/book_01/lessons/lesson_72.html (The verse reads 岳 as たけ, and its English is “The lofty peak”). Snippet: The lofty peak。

### 掛（第2課）

- 例のない読み: かかり
- 例にしていない語: 腰掛け（こしかけ）、掛け時計（かけどけい）、仕掛け（しかけ）
- Added 掛かる（かかる） for かかる from kml/data/compounds/lesson_73.json (掛かっています is か-かる. か-ける would be 掛けています). Snippet: 壁に祖母の絵が掛かっています。

### 滑（第2課）

- 滑稽（こっけい）をコツに付けました（sokuon）。

### 肝（第2課）

- 例にしていない語: 肝胆相照らす（かんたんあいてらす）
- Added 肝（きも） for きも from kml/contents/books/book_01/lessons/lesson_89.html (The verse reads 肝 as きも, and its English is “Walk with steady courage”). Snippet: Walk with steady courage,。
- カンの例は3語までです。残り1語は出していません。

### 冠（第2課）

- Added 冠（かんむり） for かんむり from kml/contents/books/book_01/lessons/lesson_17.html (The verse reads 冠 as かんむり, and its English is “Even beneath the lofty crown”). Snippet: Even beneath the lofty crown。
- カンの例は3語までです。残り2語は出していません。

### 勘（第2課）

- 例にしていない語: 勘違い（かんちがい）

### 換（第2課）

- 例のない読み: かわる
- 例にしていない語: 乗換（のりかえ）

### 敢（第2課）

- 古典部首は攴です。教・数にある形は攵です。
- joyo_kanji.csv の部首欄は攴、カードは 攵（のぶん）、出典 kanjidic
- 例にしていない語: 敢えて（あえて）

### 緩（第2課）

- 例のない読み: ゆるやか、ゆるめる

### 企（第2課）

- キの例は3語までです。残り1語は出していません。

### 忌（第2課）

- 例のない読み: いむ
- キの例は3語までです。残り1語は出していません。

### 軌（第2課）

- キの例は3語までです。残り2語は出していません。

### 既（第3課）

- むとも、なしとも呼ばれます。
- 例にしていない語: 皆既月食（かいきげっしょく）

### 棋（第3課）

- 例にしていない語: 将棋（しょうぎ）、詰将棋（つめしょうぎ）

### 犠（第3課）

- 例にしていない語: 自己犠牲（じこぎせい）
- ギの例は3語までです。残り1語は出していません。

### 菊（第3課）

- joyo_kanji.csv の部首欄は艸、カードは 艹（くさかんむり）、出典 kanjidic
- 例にしていない語: 白菊（しらぎく）
- 菊花（きっか）をキクに付けました（sokuon）。

### 吉（第3課）

- 吉報（きっぽう）をキチに付けました（sokuon）。
- 吉兆（きっちょう）をキチに付けました（sokuon）。
- キチの例は3語までです。残り1語は出していません。

### 喫（第3課）

- 喫茶店（きっさてん）をキツに付けました（sokuon）。

### 虐（第3課）

- とらがしらとも呼ばれます。
- 例のない読み: しいたげる

### 虚（第3課）

- とらがしらとも呼ばれます。

### 斤（第3課）

- 例にしていない語: 斤売り（きんうり）

### 偶（第3課）

- 例にしていない語: 配偶者（はいぐうしゃ）

### 遇（第3課）

- KANJIDIC gloss “meet”. Heisig “interview” is a later gloss and is not shown.
- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic

### 刑（第3課）

- ケイの例は3語までです。残り2語は出していません。

### 契（第4課）

- 例のない読み: ちぎる

### 掲（第4課）

- KANJIDIC gloss “put up (a notice)”. Heisig “put up notice” is the shorter form of this gloss and is not shown.
- ケイの例は3語までです。残り1語は出していません。

### 鶏（第4課）

- 例にしていない語: 鶏肉（とりにく）

### 鯨（第4課）

- ゲイの例は3語までです。残り1語は出していません。

### 幻（第4課）

- ようへんとも呼ばれます。

### 悟（第4課）

- ゴの例は3語までです。残り1語は出していません。

### 孔（第4課）

- コウの例は3語までです。残り1語は出していません。

### 甲（第4課）

- 例にしていない語: 亀の甲（かめのこう）、生き甲斐（いきがい）

### 坑（第4課）

- コウの例は3語までです。残り2語は出していません。

### 拘（第5課）

- 例にしていない語: 無拘束（むこうそく）
- コウの例は3語までです。残り1語は出していません。

### 郊（第5課）

- 古典部首は邑です。都・部にある形は阝です。
- joyo_kanji.csv の部首欄は邑、カードは 阝（おおざと）、出典 kanjidic

### 控（第5課）

- 例にしていない語: 控室（ひかえしつ）

### 慌（第5課）

- 例にしていない語: 狼狽慌乱（ろうばいこうらん）、大慌て（おおあわて）

### 硬（第5課）

- コウの例は3語までです。残り1語は出していません。

### 絞（第5課）

- 例のない読み: コウ、しめる、しまる
- 例にしていない語: 絞り込み（しぼりこみ）

### 克（第5課）

- 例にしていない語: 難関克服（なんかんこくふく）
- 克己心（こっきしん）をコクに付けました（sokuon）。

### 獄（第5課）

- ゴクの例は3語までです。残り2語は出していません。

### 恨（第5課）

- Both are KANJIDIC glosses. Heisig “resentment” is the second gloss on the card.
- 例のない読み: うらめしい
- 例にしていない語: 恨み（うらみ）

### 紺（第5課）

- KANJIDIC gloss “dark blue”. Heisig “navy blue” is the longer form of the gloss “navy” and is not shown.

### 魂（第5課）

- KANJIDIC2 に rad_name はありません。カードは鬼の読みです。

### 墾（第5課）

- KANJIDIC gloss “ground-breaking”. Heisig “groundbreaking” is the same word without the hyphen.

### 催（第5課）

- 例にしていない語: 催し（もよおし）

### 搾（第5課）

- Added 搾る（しぼる） for しぼる from kml/contents/books/book_01/lessons/lesson_72.html (搾れば is しぼ-る. The verse’s English is “Press the ripe fruit”). Snippet: Press the ripe fruit,。

### 錯（第5課）

- 錯覚（さっかく）をサクに付けました（sokuon）。

### 擦（第6課）

- 例にしていない語: 擦り傷（すりきず）、擦る（こ）、擦る（か）
- Added 擦る（する） for する from kml/data/compounds/lesson_150.json (擦りむいた is す-る. す-れる would be 擦れて). Snippet: 転んで脛を擦りむいた。

### 祉（第6課）

- 古典部首は示です。社にある形は礻です。
- joyo_kanji.csv の部首欄は示、カードは 礻（しめすへん）、出典 kanjidic

### 施（第6課）

- Both are KANJIDIC glosses. Heisig “alms” is the second gloss on the card.
- Added 施錠（せじょう） for セ from kml/data/compounds/lesson_21.json (施錠 is セ. シ would be しじょう). Snippet: 夜は必ず施錠してください。
- シの例は3語までです。残り1語は出していません。

### 諮（第6課）

- シの例は3語までです。残り1語は出していません。

### 慈（第6課）

- 例のない読み: いつくしむ

### 疾（第6課）

- 例にしていない語: 慢性疾患（まんせいしっかん）
- 疾患（しっかん）をシツに付けました（sokuon）。
- 疾走（しっそう）をシツに付けました（sokuon）。

### 湿（第6課）

- 例のない読み: しめす
- 例にしていない語: 湿気る（しける）
- 湿気（しっけ）をシツに付けました（sokuon）。
- 湿気（しっき）をシツに付けました（sokuon）。

### 邪（第6課）

- 古典部首は邑です。都・部にある形は阝です。
- joyo_kanji.csv の部首欄は邑、カードは 阝（おおざと）、出典 kanjidic
- 例にしていない語: 風邪（かぜ）

### 殊（第6課）

- かばねとも呼ばれます。
- 例にしていない語: 殊に（ことに）
- Added 殊（こと） for こと from kml/contents/books/book_01/lessons/lesson_44.html (The verse reads 殊 as こと, and its English is “Because each person is unique”). Snippet: Because each person is unique,。

### 寿（第6課）

- KANJIDIC2の古典部首は寸です。joyo_kanji.csv は士で、壽の部首です。カードは寸のままです。
- joyo_kanji.csv の部首欄は士、カードは 寸（すん）、出典 kanjidic
- 例にしていない語: 寿司（すし）
- Added 寿（ことぶき） for ことぶき from kml/contents/books/book_01/lessons/lesson_85.html (The verse reads 寿 as ことぶき, and its English is “A celebration of long life”). Snippet: A celebration of long life。

### 潤（第6課）

- 例のない読み: うるむ
- Added 潤す（うるおす） for うるおす from kml/contents/books/book_01/lessons/lesson_89.html (潤す is うるお-す. うるお-う would be 潤う. The verse’s English is “gently refreshes a thirsty throat”). Snippet: gently refreshes a thirsty throat。

### 遵（第6課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic

### 如（第6課）

- 例にしていない語: 少女の如く（しょうじょのごとく）
- Added 晏如（あんじょ） for ジョ from a KML compound filed under another character (end).
- Added 欠如（けつじょ） for ジョ from a KML compound filed under another character (end).

### 徐（第6課）

- 例にしていない語: 徐々に（じょじょに）

### 昇（第6課）

- KANJIDIC gloss “rise up”. Heisig “rise” is the shorter form of this gloss and is not shown.
- ショウの例は3語までです。残り2語は出していません。

### 掌（第7課）

- KANJIDIC gloss “palm of hand”. Heisig “manipulate” is not a gloss and is not shown.
- 例にしていない語: 掌（てのひら）
- ショウの例は3語までです。残り1語は出していません。

### 晶（第7課）

- 例にしていない語: 晶（あきら）、晶子（あきこ）

### 焦（第7課）

- 例のない読み: こがす、こがれる
- 例にしていない語: 黒焦げ（くろこげ）

### 鐘（第7課）

- 例にしていない語: 除夜の鐘（じょやのかね）
- 釣鐘（つりがね）をかねに付けました（rendaku）。

### 冗（第7課）

- ジョウの例は3語までです。残り2語は出していません。

### 嬢（第7課）

- 例にしていない語: お嬢さん（おじょうさん）

### 錠（第7課）

- ジョウの例は3語までです。残り2語は出していません。

### 伸（第7課）

- Added 伸べる（のべる） for のべる from kml/contents/books/book_01/lessons/lesson_54.html (伸べる is の-べる. の-びる would be 伸びる. The verse’s English is “offers its hand without expecting reward”). Snippet: offers its hand without expecting reward。

### 辛（第7課）

- 例にしていない語: 辛い（つらい）、香辛料（こうしんりょう）

### 炊（第7課）

- スイの例は3語までです。残り1語は出していません。

### 酔（第7課）

- 例にしていない語: 酔っ払い（よっぱらい）

### 遂（第7課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic
- 例にしていない語: 遂に（ついに）

### 穂（第7課）

- KANJIDIC gloss “ear (grain)”. The first gloss “ear” is ambiguous in English. Heisig “ear of plant” restates this gloss and is not shown.
- 例のない読み: スイ
- 稲穂（いなほ）をほに付けました（compound）。
- 穂先（ほさき）をほに付けました（compound）。

### 随（第8課）

- KANJIDIC gloss “follow”. Heisig “accompany” is not a gloss and is not shown.
- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic

### 髄（第8課）

- 例にしていない語: 脊髄炎（せきずいえん）

### 瀬（第8課）

- 瀬戸（せと）をせに付けました（compound）。
- 瀬戸際（せとぎわ）をせに付けました（compound）。
- 瀬戸物（せともの）をせに付けました（compound）。
- 浅瀬（あさせ）をせに付けました（compound）。
- せの例は3語までです。残り1語は出していません。

### 牲（第8課）

- 例にしていない語: 犠牲心（ぎせいしん）、犠牲者（ぎせいしゃ）

### 婿（第8課）

- 花婿（はなむこ）をむこに付けました（compound）。
- 婿養子（むこようし）をむこに付けました（compound）。
- 新婿（しんむこ）をむこに付けました（compound）。
- むこの例は3語までです。残り1語は出していません。

### 請（第8課）

- 例のない読み: うける
- Added 請う（こう） for こう from kml/contents/books/book_01/lessons/lesson_83.html (請えば is こ-う. う-ける would be 請ければ. The verse’s English is “When you quietly ask for help”). Snippet: When you quietly ask for help,。

### 斥（第8課）

- 斥候（せっこう）をセキに付けました（sokuon）。

### 摂（第8課）

- 摂取（せっしゅ）をセツに付けました（sokuon）。
- 摂食（せっしょく）をセツに付けました（sokuon）。

### 潜（第8課）

- 例にしていない語: 呂号潜水艦（ろごうせんすいかん）

### 阻（第8課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic

### 粗（第8課）

- 例にしていない語: 粗大ごみ（そだいごみ）、粗（あら）

### 礎（第8課）

- 例にしていない語: 基礎学力（きそがくりょく）、基礎工事（きそこうじ）

### 双（第8課）

- KANJIDIC2の古典部首は又です。joyo_kanji.csv は隹で、雙の部首です。カードは又のままです。
- joyo_kanji.csv の部首欄は隹、カードは 又（また）、出典 kanjidic
- 双子（ふたご）をふたに付けました（compound）。
- 双葉（ふたば）をふたに付けました（compound）。

### 桑（第8課）

- 例のない読み: ソウ
- 例にしていない語: 桑の実（くわのみ）
- 桑畑（くわばたけ）をくわに付けました（compound）。
- 桑名（くわな）をくわに付けました（compound）。

### 葬（第9課）

- KANJIDIC gloss “bury”. The first gloss “interment” is the same sense in rarer wording. Heisig “burial” restates “bury” and is not a gloss.
- joyo_kanji.csv の部首欄は艸、カードは 艹（くさかんむり）、出典 kanjidic
- 例にしていない語: 冠婚葬祭（かんこんそうさい）

### 遭（第9課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic

### 憎（第9課）

- 例のない読み: にくい、にくらしい

### 促（第9課）

- ソクの例は3語までです。残り1語は出していません。

### 賊（第9課）

- ゾクの例は3語までです。残り2語は出していません。

### 怠（第9課）

- 例にしていない語: 職務怠慢（しょくむたいまん）

### 胎（第9課）

- タイの例は3語までです。残り2語は出していません。

### 袋（第9課）

- 例のない読み: タイ
- 例にしていない語: 袋詰め（ふくろづめ）、お袋（おふくろ）、足袋（たび）
- 手袋（てぶくろ）をふくろに付けました（rendaku）。

### 逮（第9課）

- 古典部首は辵です。カードは辶です。
- joyo_kanji.csv の部首欄は辵、カードは 辶（しんにょう）、出典 kanjidic

### 滞（第9課）

- 例のない読み: とどこおる
- タイの例は3語までです。残り2語は出していません。

### 滝（第9課）

- 例にしていない語: 那智の滝（なちのたき）
- 滝壺（たきつぼ）をたきに付けました（compound）。
- 滝川（たきがわ）をたきに付けました（compound）。
- 滝行（たきぎょう）をたきに付けました（compound）。
- たきの例は3語までです。残り1語は出していません。

### 択（第9課）

- 例にしていない語: 二者択一（にしゃたくいつ）

### 卓（第9課）

- 卓球（たっきゅう）をタクに付けました（sokuon）。
- 卓見（たっけん）をタクに付けました（sokuon）。
- タクの例は3語までです。残り2語は出していません。

### 託（第9課）

- 例にしていない語: 託す（たくす）

### 諾（第9課）

- ダクの例は3語までです。残り2語は出していません。

### 奪（第9課）

- 奪取（だっしゅ）をダツに付けました（sokuon）。
- 奪回（だっかい）をダツに付けました（sokuon）。
- ダツの例は3語までです。残り1語は出していません。

### 胆（第9課）

- KANJIDIC gloss “gall bladder”. Heisig “gallbladder” is the same word without the space.
- 例にしていない語: 胆のう（たんのう）、肝胆相照らす（かんたんあいてらす）
- タンの例は3語までです。残り1語は出していません。

### 壇（第9課）

- ダンの例は3語までです。残り2語は出していません。

### 稚（第9課）

- 例にしていない語: 幼稚園（ようちえん）

### 畜（第10課）

- チクの例は3語までです。残り1語は出していません。

### 窒（第10課）

- 窒息（ちっそく）をチツに付けました（sokuon）。
- 窒素（ちっそ）をチツに付けました（sokuon）。

### 鋳（第10課）

- 例のない読み: いる
- 例にしていない語: 鋳物（いもの）

### 駐（第10課）

- Both are KANJIDIC glosses. The first gloss “stop-over” is the same stop sense in less familiar wording. Heisig “parking” is the 駐車 context and is not a gloss, so it is not on the card. The sense depends on the word.

### 超（第10課）

- 例のない読み: こす
- チョウの例は3語までです。残り1語は出していません。

### 陳（第10課）

- KANJIDIC gloss “exhibit”. Heisig “set forth” is not a gloss and is not shown.
- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic

### 鎮（第10課）

- 例のない読み: しずめる、しずまる
- チンの例は3語までです。残り2語は出していません。

### 帝（第10課）

- テイの例は3語までです。残り2語は出していません。

### 訂（第10課）

- テイの例は3語までです。残り2語は出していません。

### 締（第10課）

- 例のない読み: しまる
- 例にしていない語: 締切（しめきり）、戸締り（とじまり）、締め切る（しめきる）

### 凍（第10課）

- 例にしていない語: 冷凍庫（れいとうこ）
- Added 凍える（こごえる） for こごえる from kml/contents/books/book_01/lessons/lesson_105.html (凍えた is こご-える. The verse’s English is “holds their frozen hands toward the fire”). Snippet: and holds their frozen hands toward the fire。

### 陶（第10課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic

### 匿（第11課）

- 例にしていない語: 匿う（かくまう）

### 豚（第11課）

- 豚肉（ぶたにく）をぶたに付けました（compound）。
- 黒豚（くろぶた）をぶたに付けました（compound）。
- 子豚（こぶた）をぶたに付けました（compound）。
- ぶたの例は3語までです。残り1語は出していません。

### 尿（第11課）

- ニョウの例は3語までです。残り1語は出していません。

### 粘（第11課）

- 例にしていない語: 粘り（ねばり）

### 婆（第11課）

- 例にしていない語: お婆さん（おばあさん）

### 陪（第11課）

- Both are KANJIDIC glosses. The first gloss “obeisance” is archaic. “follow” is also a gloss and overlaps “accompany”. Heisig “jury” is the 陪審 context only and is not a gloss.
- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic

### 伐（第11課）

- 伐採（ばっさい）をバツに付けました（sokuon）。

### 帆（第11課）

- 例にしていない語: 一帆風順（いっぱんふうじゅん）
- 帆影（ほえい）をほに付けました（compound）。
- 白帆（しらほ）をほに付けました（compound）。

### 伴（第11課）

- Added 伴侶（はんりょ） for ハン from a KML compound filed under another character (start).

### 藩（第11課）

- joyo_kanji.csv の部首欄は艸、カードは 艹（くさかんむり）、出典 kanjidic

### 卑（第11課）

- 例のない読み: いやしむ、いやしめる

### 泌（第11課）

- 例のない読み: ヒツ、ヒ
- 例にしていない語: 分泌（ぶんぴつ）、涙腺分泌（るいせんぶんぴつ）、内分泌（ないぶんぴつ）、外分泌（がいぶんぴつ）、分泌物（ぶんぴつぶつ）

### 姫（第11課）

- 姫様（ひめさま）をひめに付けました（compound）。
- 歌姫（うたひめ）をひめに付けました（compound）。

### 苗（第11課）

- joyo_kanji.csv の部首欄は艸、カードは 艹（くさかんむり）、出典 kanjidic
- 例のない読み: ビョウ
- 例にしていない語: 苗字（みょうじ）
- 苗木（なえぎ）をなえに付けました（compound）。
- 苗床（なえどこ）をなえに付けました（compound）。
- 苗場（なえば）をなえに付けました（compound）。
- なえの例は3語までです。残り1語は出していません。

### 赴（第12課）

- 例にしていない語: 単身赴任（たんしんふにん）、遠赴（えんぷ）

### 符（第12課）

- 例にしていない語: 切符（きっぷ）

### 封（第12課）

- 例にしていない語: 密封（みっぷう）

### 伏（第12課）

- 例のない読み: ふす
- 例にしていない語: 潜伏（せんぷく）

### 覆（第12課）

- 西の古典部首です。
- 例のない読み: くつがえる

### 紛（第12課）

- 例のない読み: まぎらす、まぎらわす

### 癖（第12課）

- 例のない読み: ヘキ
- 例にしていない語: 癖になる（くせになる）
- 口癖（くちぐせ）をくせに付けました（rendaku）。

### 募（第12課）

- ボの例は3語までです。残り1語は出していません。

### 慕（第12課）

- ボの例は3語までです。残り1語は出していません。

### 芳（第12課）

- joyo_kanji.csv の部首欄は艸、カードは 艹（くさかんむり）、出典 kanjidic
- ホウの例は3語までです。残り1語は出していません。

### 邦（第12課）

- 古典部首は邑です。都・部にある形は阝です。
- joyo_kanji.csv の部首欄は邑、カードは 阝（おおざと）、出典 kanjidic
- 例にしていない語: 連邦（れんぽう）

### 奉（第12課）

- Both are KANJIDIC glosses. The first gloss “observance” is a narrower sense. Heisig “dedicate” is the second gloss on the card.

### 胞（第12課）

- 例にしていない語: 細胞（さいぼう）、細胞膜（さいぼうまく）、癌細胞（がんさいぼう）

### 崩（第12課）

- 例のない読み: くずす
- 例にしていない語: 雪崩（なだれ）
- Added 崩れる（くずれる） for くずれる from kml/data/compounds/lesson_89.json (崩れそう is くず-れる. くず-す would be 崩しそう). Snippet: 天候が崩れそうなので、出発を早めます。

### 飽（第12課）

- 例のない読み: あかす
- 例にしていない語: 飽くまで（あくまで）

### 乏（第12課）

- KANJIDIC gloss “scarce”. The first gloss “destitution” is the noun sense. Heisig “scarce” is this gloss.

### 妨（第12課）

- 例にしていない語: 営業妨害（えいぎょうぼうがい）、進路妨害（しんろぼうがい）

### 房（第13課）

- 古典部首は戶です。カードは戸です。
- joyo_kanji.csv の部首欄は戶、カードは 戸（と）、出典 kanjidic
- 例にしていない語: 文房具（ぶんぼうぐ）
- Added 房（ふさ） for ふさ from kml/contents/books/book_01/lessons/lesson_17.html (The verse reads 房 as ふさ, and its English is “The sunlit cluster of grapes”). Snippet: The sunlit cluster of grapes。

### 膨（第13課）

- 例のない読み: ふくれる
- 例にしていない語: 膨らます（ふくらます）

### 謀（第13課）

- 例のない読み: はかる

### 墨（第13課）

- 墨絵（すみえ）をすみに付けました（compound）。
- 墨色（すみいろ）をすみに付けました（compound）。

### 没（第13課）

- 没収（ぼっしゅう）をボツに付けました（sokuon）。
- 没頭（ぼっとう）をボツに付けました（sokuon）。
- ボツの例は3語までです。残り2語は出していません。

### 翻（第13課）

- KANJIDIC2の古典部首は羽です。joyo_kanji.csv は飛で、飜の部首です。カードは羽のままです。
- joyo_kanji.csv の部首欄は飛、カードは 羽（はね）、出典 kanjidic
- 例のない読み: ひるがえす

### 魔（第13課）

- KANJIDIC2 に rad_name はありません。カードは鬼の読みです。

### 埋（第13課）

- 例のない読み: うもれる
- 例にしていない語: 埋立地（うめたてち）

### 膜（第13課）

- マクの例は3語までです。残り2語は出していません。

### 又（第13課）

- 例にしていない語: 又は（または）、又聞き（またぎき）、又しても（またしても）
- 又従兄弟（またいとこ）をまたに付けました（compound）。

### 魅（第13課）

- KANJIDIC2 に rad_name はありません。カードは鬼の読みです。

### 滅（第13課）

- 例のない読み: ほろびる、ほろぼす
- 例にしていない語: 滅多に（めったに）
- メツの例は3語までです。残り1語は出していません。

### 幽（第13課）

- Both are KANJIDIC glosses. The first gloss “seclude” is the verb. “confine to a room”, “deep”, and “profound” are other glosses and are not on the card. Heisig “dim” is not a gloss. The sense depends on the word: 幽閉 is confinement, 幽玄 is profound, and 幽霊 is a ghost.
- ようへんとも呼ばれます。

### 誘（第13課）

- ユウの例は3語までです。残り1語は出していません。

### 憂（第13課）

- 例のない読み: うれい、うい
- 例にしていない語: 内憂外患（ないゆうがいかん）

### 揚（第13課）

- Both are KANJIDIC glosses. Heisig “hoist” is the second gloss on the card.
- Added 揚がる（あがる） for あがる from kml/contents/books/book_01/lessons/lesson_142.html (揚がる is あ-がる, here “brought ashore”. あ-げる would be 揚げる. The verse’s English is “a great tuna is brought ashore”). Snippet: a great tuna is brought ashore。
- ヨウの例は3語までです。残り1語は出していません。

### 揺（第13課）

- 例のない読み: ゆらぐ、ゆるぐ、ゆする、ゆさぶる、ゆすぶる
- Added 揺る（ゆる） for ゆる from kml/contents/books/book_01/lessons/lesson_79.html (揺るがない is ゆ-る. ゆ-らぐ would be 揺らがない. The verse’s English is “does not yield to strong winds”). Snippet: does not yield to strong winds。

### 裸（第14課）

- 例にしていない語: 裸足（はだし）

### 濫（第14課）

- 例にしていない語: 粗製濫造（そせいらんぞう）

### 吏（第14課）

- リの例は3語までです。残り2語は出していません。

### 隆（第14課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic

### 了（第14課）

- Both are KANJIDIC glosses. Heisig “finish” is the second gloss on the card.
- リョウの例は3語までです。残り1語は出していません。

### 陵（第14課）

- 古典部首は阜です。院・階・陽にある形は阝です。
- joyo_kanji.csv の部首欄は阜、カードは 阝（こざとへん）、出典 kanjidic
- Added 陵（みささぎ） for みささぎ from kml/contents/books/book_01/lessons/lesson_82.html (The verse reads 陵 as みささぎ, and its English is “Standing before an ancient tomb”). Snippet: Standing before an ancient tomb,。

### 糧（第14課）

- Added 糧（かて） for かて from kml/contents/books/book_01/lessons/lesson_50.html (The verse reads 糧 as かて, and its English is “Today's experiences become tomorrow's nourishment”). Snippet: Today's experiences。

### 厘（第14課）

- “rin” is the KANJIDIC gloss, the name of the unit. “thousandth” is the Heisig keyword and the 常用漢字表 English column. KANJIDIC also glosses “1/10 sen” and “1/10 bu”. Those are other traditional units, so the size of a rin depends on context.
- リンの例は3語までです。残り2語は出していません。

### 零（第14課）

- レイの例は3語までです。残り1語は出していません。

### 霊（第14課）

- 例のない読み: リョウ、たま

### 炉（第14課）

- 例にしていない語: 囲炉裏（いろり）

## 部首

The card uses the KANJIDIC2 classical radical, the same default as 10級 through 4級.
Names new at this level with a KANJIDIC2 `rad_name`: 匚 はこがまえ, 无 むにょう（むとも、なしとも）, 虍 とらかんむり（とらがしらとも）.
These cards stay on the KANJIDIC2 radical where the joyo column names the radical of the traditional character: 寿 寸（士, from 壽）, 双 又（隹, from 雙）, 翻 羽（飛, from 飜）.
辶, 阝, 攵, 艹, 礻, and 戸 on these cards are the printed forms of 辵, 阜 or 邑, 攴, 艸, 示, and 戶.
着 is not in 3級. Its 8級 exception, 羊 rather than 目, is not copied onto other characters.
