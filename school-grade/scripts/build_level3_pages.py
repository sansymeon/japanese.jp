#!/usr/bin/env python3
"""Write the fourteen 漢検3級 lesson pages and their compiled vocabulary pages.

Uses the 漢検3級 card layout. Output lives at kanken/level-3/.
The level entrance is written by kml/scripts/build_kanken_level_pages.py --level3.
The 284 characters are the 常用漢字表 grade-S rows whose 漢検 level is 3,
in 掲載順. There is no separate school-film cut for this level. The
post-elementary films are one collection shared by 漢検4級 through 漢検2級.
Lessons are ten groups of 20 and four groups of 21, in that order.

English starts from the first KANJIDIC2 gloss. MEANING_CHOICES may name a
clearer gloss from that same entry, or a marked paraphrase. Heisig stays on
its own line only when that keyword is not already the displayed wording.
Radicals stay on the KANJIDIC2 classical radical. 着 is not in this level.

Bare readings are filled from KML compounds filed under any character when
the reading match is the same mechanical test used on 8級, limited to a
short headword or a verb. One-mora on readings are not filled that way.
VERIFIED_EXAMPLES then adds a dictionary form only when a KML sentence
segment, or ruby in a KML verse, locks that exact 常用漢字表 reading.
A reading with no suitable verified word stays bare and is listed in the review.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GRADE = REPO / "kanken/level-3"
DISCLAIMER = REPO / "school-grade/partials/disclaimer.html"
REVIEW = GRADE / "VOCABULARY_REVIEW.md"
ORDER = GRADE / "order.json"
HEROES = GRADE / "heroes.json"
STUDIES = REPO / "kml/assets/studies"
INDEX = REPO / "kml/data/kanji/kanken_index.json"
JOYO = REPO / "kml/analytics/reference/joyo_kanji.csv"

spec = importlib.util.spec_from_file_location(
    "build_grade2_pages", Path(__file__).with_name("build_grade2_pages.py")
)
grade2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grade2)

spec8 = importlib.util.spec_from_file_location(
    "build_level8_pages", Path(__file__).with_name("build_level8_pages.py")
)
level8 = importlib.util.module_from_spec(spec8)
spec8.loader.exec_module(level8)

RADICALS = {
    **level8.RADICALS,
    20: ("勹", "つつみがまえ", ""),
    26: ("卩", "ふしづくり", ""),
    34: ("夂", "ふゆがしら", ""),
    54: ("廴", "えんにょう", "いんにょうとも呼ばれます。"),
    62: ("戈", "かのほこ", ""),
    68: ("斗", "とます", ""),
    83: ("氏", "うじ", ""),
    122: ("罒", "よんかしら", "古典部首は网（あみがしら）です。署にある形は罒です。"),
    131: ("臣", "しん", ""),
    138: ("艮", "ねづくり", "こんとも呼ばれます。"),
    160: ("辛", "からい", ""),
    183: ("飛", "とぶ", ""),
    186: ("香", "かおり", ""),
    198: ("鹿", "しか", ""),
    55: ("廾", "にじゅうあし", ""),
    65: ("支", "しんよう", "じゅうまたとも呼ばれます。"),
    79: ("殳", "ほこつくり", "るまたとも呼ばれます。"),
    81: ("比", "くらべる", ""),
    91: ("片", "かた", ""),
    95: ("玄", "げん", ""),
    127: ("耒", "らいすき", ""),
    134: ("臼", "うす", ""),
    152: ("豕", "いのこ", ""),
    175: ("非", "あらず", ""),
    16: ("几", "つくえ", ""),
    43: ("尢", "だいのまげあし", "もっともとも呼ばれます。"),
    49: ("己", "おのれ", ""),
    52: ("幺", "いとがしら", "ようへんとも呼ばれます。"),
    103: ("疋", "ひき", ""),
    133: ("至", "いたる", ""),
    135: ("舌", "した", ""),
    177: ("革", "かわ", "かくのかわとも呼ばれます。"),
    188: ("骨", "ほね", ""),
    25: ("卜", "ぼくのと", ""),
    99: ("甘", "あまい", "KANJIDIC2 に rad_name はありません。カードは甘の読みです。"),
    110: ("矛", "ほこ", "KANJIDIC2 に rad_name はありません。カードは矛の読みです。"),
    126: ("而", "しこうして", "KANJIDIC2 に rad_name はありません。カードは而の常用の読みです。"),
    136: ("舛", "まいあし", ""),
    165: ("釆", "のごめ", ""),
    171: ("隶", "れいづくり", ""),
    190: ("髟", "かみがしら", "かみかんむりとも呼ばれます。"),
    194: ("鬼", "おに", "KANJIDIC2 に rad_name はありません。カードは鬼の読みです。"),
    207: ("鼓", "つづみ", "KANJIDIC2 に rad_name はありません。カードは鼓の読みです。"),
    211: ("齒", "は", "KANJIDIC2 に rad_name はありません。カードは齒の読みです。"),
    22: ("匚", "はこがまえ", ""),
    71: ("无", "むにょう", "むとも、なしとも呼ばれます。"),
    141: ("虍", "とらかんむり", "とらがしらとも呼ばれます。"),
}

# One existing 16:9 study image from a character in that lesson.
# The overview hero, 鯨, is in lesson 4 and is not that lesson’s cover.
HERO_CHOICES = {
    1: ("inflammation", "炎"),
    2: ("mountain_peak", "岳"),
    3: ("chess_piece", "棋"),
    4: ("chicken", "鶏"),
    5: ("outskirts", "郊"),
    6: ("waiter", "侍"),
    7: ("bell", "鐘"),
    8: ("rapids", "瀬"),
    9: ("burial", "葬"),
    10: ("carve", "彫"),
    11: ("pork", "豚"),
    12: ("seal", "封"),
    13: ("black_ink", "墨"),
    14: ("gulf", "湾"),
}
OVERVIEW_HERO = ("whale", "鯨")

# Each part is an exact KANJIDIC2 gloss, a Heisig keyword, or a marked paraphrase.
# show_heisig is false when that keyword is already the displayed wording,
# or when it is not a gloss.
MEANING_CHOICES = {
    "架": {
        "parts": (("frame", "kanjidic"), ("shelf", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “erect” is a verb sense. Heisig “rack” is not a gloss.",
    },
    "岳": {
        "parts": (("peak", "kanjidic"), ("mountain", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “point” hides the mountain. Heisig “mountain peak” restates these glosses and is not shown.",
    },
    "恨": {
        "parts": (("regret", "kanjidic"), ("resentment", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “resentment” is the second gloss on the card.",
    },
    "施": {
        "parts": (("give", "kanjidic"), ("alms", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “alms” is the second gloss on the card.",
    },
    "穂": {
        "parts": (("ear (grain)", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “ear (grain)”. The first gloss “ear” is ambiguous in English. Heisig “ear of plant” restates this gloss and is not shown.",
    },
    "葬": {
        "parts": (("bury", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “bury”. The first gloss “interment” is the same sense in rarer wording. Heisig “burial” restates “bury” and is not a gloss.",
    },
    "奉": {
        "parts": (("offer", "kanjidic"), ("dedicate", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “observance” is a narrower sense. Heisig “dedicate” is the second gloss on the card.",
    },
    "乏": {
        "parts": (("scarce", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “scarce”. The first gloss “destitution” is the noun sense. Heisig “scarce” is this gloss.",
    },
    "揚": {
        "parts": (("raise", "kanjidic"), ("hoist", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “hoist” is the second gloss on the card.",
    },
    "了": {
        "parts": (("complete", "kanjidic"), ("finish", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “finish” is the second gloss on the card.",
    },
    "乙": {
        "parts": (("the latter", "kanjidic"), ("strange", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses, and the sense depends on context. 甲乙 is “the latter”. 乙な is “strange”, or the gloss “witty”. “duplicate” and “fishhook radical (no. 5)” are other glosses and are not on the card. Heisig “hook” names the shape and is not a gloss.",
    },
    "駐": {
        "parts": (("reside in", "kanjidic"), ("resident", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “stop-over” is the same stop sense in less familiar wording. Heisig “parking” is the 駐車 context and is not a gloss, so it is not on the card. The sense depends on the word.",
    },
    "陪": {
        "parts": (("accompany", "kanjidic"), ("attend on", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “obeisance” is archaic. “follow” is also a gloss and overlaps “accompany”. Heisig “jury” is the 陪審 context only and is not a gloss.",
    },
    "幽": {
        "parts": (("secluded", "kanjidic"), ("faint", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “seclude” is the verb. “confine to a room”, “deep”, and “profound” are other glosses and are not on the card. Heisig “dim” is not a gloss. The sense depends on the word: 幽閉 is confinement, 幽玄 is profound, and 幽霊 is a ghost.",
    },
    "厘": {
        "parts": (("rin", "kanjidic"), ("thousandth", "heisig")),
        "show_heisig": False,
        "note": "“rin” is the KANJIDIC gloss, the name of the unit. “thousandth” is the Heisig keyword and the 常用漢字表 English column. KANJIDIC also glosses “1/10 sen” and “1/10 bu”. Those are other traditional units, so the size of a rin depends on context.",
    },
}

# First gloss kept. Heisig is the same sense and is not an exact gloss, so it is not shown.
MEANING_REVIEW = {
    "遇": "KANJIDIC gloss “meet”. Heisig “interview” is a later gloss and is not shown.",
    "掲": "KANJIDIC gloss “put up (a notice)”. Heisig “put up notice” is the shorter form of this gloss and is not shown.",
    "紺": "KANJIDIC gloss “dark blue”. Heisig “navy blue” is the longer form of the gloss “navy” and is not shown.",
    "墾": "KANJIDIC gloss “ground-breaking”. Heisig “groundbreaking” is the same word without the hyphen.",
    "昇": "KANJIDIC gloss “rise up”. Heisig “rise” is the shorter form of this gloss and is not shown.",
    "掌": "KANJIDIC gloss “palm of hand”. Heisig “manipulate” is not a gloss and is not shown.",
    "随": "KANJIDIC gloss “follow”. Heisig “accompany” is not a gloss and is not shown.",
    "胆": "KANJIDIC gloss “gall bladder”. Heisig “gallbladder” is the same word without the space.",
    "陳": "KANJIDIC gloss “exhibit”. Heisig “set forth” is not a gloss and is not shown.",
}

RADICAL_CARD = {}

# Real classification differences. The card stays on the KANJIDIC2 classical radical.
CHARACTER_RADICAL_NOTES = {
    "寿": "KANJIDIC2の古典部首は寸です。joyo_kanji.csv は士で、壽の部首です。カードは寸のままです。",
    "双": "KANJIDIC2の古典部首は又です。joyo_kanji.csv は隹で、雙の部首です。カードは又のままです。",
    "翻": "KANJIDIC2の古典部首は羽です。joyo_kanji.csv は飛で、飜の部首です。カードは羽のままです。",
}
SKIP_EXAMPLES = set()
# Dictionary form shown to the learner. The snippet is an existing KML sentence or verse.
# stem mode: the segment is the character alone, read as `stem`, and the next
# segment starts with `follows`, which has to be an inflection of this reading only.
# ruby mode: the HTML contains ruby for this character and this full reading.
# ruby-stem mode: the ruby is the stem only, and the kana immediately after it
# is an inflection of this reading and of no other reading with that stem.
VERIFIED_EXAMPLES = (
    {
        "kanji": "掛",
        "raw": "か-かる",
        "surface": "掛かる",
        "reading": "かかる",
        "snippet": "壁に祖母の絵が掛かっています。",
        "source": "kml/data/compounds/lesson_73.json",
        "mode": "stem",
        "stem": "か",
        "follows": "かっています。",
        "form": "掛かっています is か-かる. か-ける would be 掛けています",
    },
    {
        "kanji": "崩",
        "raw": "くず-れる",
        "surface": "崩れる",
        "reading": "くずれる",
        "snippet": "天候が崩れそうなので、出発を早めます。",
        "source": "kml/data/compounds/lesson_89.json",
        "mode": "stem",
        "stem": "くず",
        "follows": "れ",
        "form": "崩れそう is くず-れる. くず-す would be 崩しそう",
    },
    {
        "kanji": "擦",
        "raw": "す-る",
        "surface": "擦る",
        "reading": "する",
        "snippet": "転んで脛を擦りむいた。",
        "source": "kml/data/compounds/lesson_150.json",
        "mode": "stem",
        "stem": "す",
        "follows": "り",
        "form": "擦りむいた is す-る. す-れる would be 擦れて",
    },
    {
        "kanji": "炎",
        "raw": "ほのお",
        "surface": "炎",
        "reading": "ほのお",
        "snippet": "Within the quiet time around fire,",
        "source": "kml/contents/books/book_01/lessons/lesson_16.html",
        "mode": "ruby",
        "form": "The verse reads 炎 as ほのお, and its English is “Within the quiet time around fire”",
    },
    {
        "kanji": "華",
        "raw": "はな",
        "surface": "華",
        "reading": "はな",
        "snippet": "Wildflowers bloom beautifully,",
        "source": "kml/contents/books/book_01/lessons/lesson_86.html",
        "mode": "ruby",
        "form": "The verse reads 華 as はな in the line whose English is “Wildflowers bloom beautifully”",
    },
    {
        "kanji": "岳",
        "raw": "たけ",
        "surface": "岳",
        "reading": "たけ",
        "snippet": "The lofty peak",
        "source": "kml/contents/books/book_01/lessons/lesson_72.html",
        "mode": "ruby",
        "form": "The verse reads 岳 as たけ, and its English is “The lofty peak”",
    },
    {
        "kanji": "肝",
        "raw": "きも",
        "surface": "肝",
        "reading": "きも",
        "snippet": "Walk with steady courage,",
        "source": "kml/contents/books/book_01/lessons/lesson_89.html",
        "mode": "ruby",
        "form": "The verse reads 肝 as きも, and its English is “Walk with steady courage”",
    },
    {
        "kanji": "冠",
        "raw": "かんむり",
        "surface": "冠",
        "reading": "かんむり",
        "snippet": "Even beneath the lofty crown",
        "source": "kml/contents/books/book_01/lessons/lesson_17.html",
        "mode": "ruby",
        "form": "The verse reads 冠 as かんむり, and its English is “Even beneath the lofty crown”",
    },
    {
        "kanji": "殊",
        "raw": "こと",
        "surface": "殊",
        "reading": "こと",
        "snippet": "Because each person is unique,",
        "source": "kml/contents/books/book_01/lessons/lesson_44.html",
        "mode": "ruby",
        "form": "The verse reads 殊 as こと, and its English is “Because each person is unique”",
    },
    {
        "kanji": "寿",
        "raw": "ことぶき",
        "surface": "寿",
        "reading": "ことぶき",
        "snippet": "A celebration of long life",
        "source": "kml/contents/books/book_01/lessons/lesson_85.html",
        "mode": "ruby",
        "form": "The verse reads 寿 as ことぶき, and its English is “A celebration of long life”",
    },
    {
        "kanji": "房",
        "raw": "ふさ",
        "surface": "房",
        "reading": "ふさ",
        "snippet": "The sunlit cluster of grapes",
        "source": "kml/contents/books/book_01/lessons/lesson_17.html",
        "mode": "ruby",
        "form": "The verse reads 房 as ふさ, and its English is “The sunlit cluster of grapes”",
    },
    {
        "kanji": "陵",
        "raw": "みささぎ",
        "surface": "陵",
        "reading": "みささぎ",
        "snippet": "Standing before an ancient tomb,",
        "source": "kml/contents/books/book_01/lessons/lesson_82.html",
        "mode": "ruby",
        "form": "The verse reads 陵 as みささぎ, and its English is “Standing before an ancient tomb”",
    },
    {
        "kanji": "糧",
        "raw": "かて",
        "surface": "糧",
        "reading": "かて",
        "snippet": "Today's experiences",
        "source": "kml/contents/books/book_01/lessons/lesson_50.html",
        "mode": "ruby",
        "form": "The verse reads 糧 as かて, and its English is “Today's experiences become tomorrow's nourishment”",
    },
    {
        "kanji": "施",
        "raw": "セ",
        "surface": "施錠",
        "reading": "せじょう",
        "snippet": "夜は必ず施錠してください。",
        "source": "kml/data/compounds/lesson_21.json",
        "mode": "word",
        "form": "施錠 is セ. シ would be しじょう",
    },
    {
        "kanji": "架",
        "raw": "か-かる",
        "surface": "架かる",
        "reading": "かかる",
        "snippet": "a quiet rainbow stretches across the sky.",
        "source": "kml/contents/books/book_01/lessons/lesson_97.html",
        "mode": "ruby-stem",
        "stem": "か",
        "follows": "かった。",
        "form": "架かった is か-かる. か-ける would be 架けた. The verse’s English is “a quiet rainbow stretches across the sky”",
    },
    {
        "kanji": "搾",
        "raw": "しぼ-る",
        "surface": "搾る",
        "reading": "しぼる",
        "snippet": "Press the ripe fruit,",
        "source": "kml/contents/books/book_01/lessons/lesson_72.html",
        "mode": "ruby-stem",
        "stem": "しぼ",
        "follows": "れ",
        "form": "搾れば is しぼ-る. The verse’s English is “Press the ripe fruit”",
    },
    {
        "kanji": "潤",
        "raw": "うるお-す",
        "surface": "潤す",
        "reading": "うるおす",
        "snippet": "gently refreshes a thirsty throat.",
        "source": "kml/contents/books/book_01/lessons/lesson_89.html",
        "mode": "ruby-stem",
        "stem": "うるお",
        "follows": "す。",
        "form": "潤す is うるお-す. うるお-う would be 潤う. The verse’s English is “gently refreshes a thirsty throat”",
    },
    {
        "kanji": "請",
        "raw": "こ-う",
        "surface": "請う",
        "reading": "こう",
        "snippet": "When you quietly ask for help,",
        "source": "kml/contents/books/book_01/lessons/lesson_83.html",
        "mode": "ruby-stem",
        "stem": "こ",
        "follows": "えば、",
        "form": "請えば is こ-う. う-ける would be 請ければ. The verse’s English is “When you quietly ask for help”",
    },
    {
        "kanji": "伸",
        "raw": "の-べる",
        "surface": "伸べる",
        "reading": "のべる",
        "snippet": "offers its hand without expecting reward.",
        "source": "kml/contents/books/book_01/lessons/lesson_54.html",
        "mode": "ruby-stem",
        "stem": "の",
        "follows": "べる。",
        "form": "伸べる is の-べる. の-びる would be 伸びる. The verse’s English is “offers its hand without expecting reward”",
    },
    {
        "kanji": "凍",
        "raw": "こご-える",
        "surface": "凍える",
        "reading": "こごえる",
        "snippet": "and holds their frozen hands toward the fire.",
        "source": "kml/contents/books/book_01/lessons/lesson_105.html",
        "mode": "ruby-stem",
        "stem": "こご",
        "follows": "えた",
        "form": "凍えた is こご-える. The verse’s English is “holds their frozen hands toward the fire”",
    },
    {
        "kanji": "揚",
        "raw": "あ-がる",
        "surface": "揚がる",
        "reading": "あがる",
        "snippet": "a great tuna is brought ashore.",
        "source": "kml/contents/books/book_01/lessons/lesson_142.html",
        "mode": "ruby-stem",
        "stem": "あ",
        "follows": "がる。",
        "form": "揚がる is あ-がる, here “brought ashore”. あ-げる would be 揚げる. The verse’s English is “a great tuna is brought ashore”",
    },
    {
        "kanji": "揺",
        "raw": "ゆ-る",
        "surface": "揺る",
        "reading": "ゆる",
        "snippet": "does not yield to strong winds.",
        "source": "kml/contents/books/book_01/lessons/lesson_79.html",
        "mode": "ruby-stem",
        "stem": "ゆ",
        "follows": "るがない。",
        "form": "揺るがない is ゆ-る. ゆ-らぐ would be 揺らがない. The verse’s English is “does not yield to strong winds”",
    },
)
HELD_BACK = (
    "湿（しめす） is the reading behind the reported “示す”. 示 is 常用漢字表 grade 5 and is not in 漢検3級. No KML sentence locks 湿す, so しめす stays bare.",
    "請（うける） is the reading behind the reported “受ける”. 受 is grade 3 and is not in 漢検3級. 茶請け（ちゃうけ） does not lock う-ける. That reading stays bare. こう is a separate reading and has its own example.",
    "換（かわる）, 緩（ゆるめる）, 憎（にくい）, 滞（とどこおる）, 崩（くずす）, 膨（ふくれる）, 謀（はかる）, and 超（こす） have no sentence that locks the character and that reading.",
    "揺（ゆさぶる） locks in 入札の醜聞が、組合の信用を揺さぶりました, and 揺（ゆする） locks in 嵐は乾坤を揺する勢いで、船を押し流しました. Both are uncommon wording, so they stay bare.",
    "悔（くいる） locks in 若気の放蕩を今は悔いている. The wording is old-fashioned, so it stays bare.",
    "緩（ゆるやか） is read ゆる in 曼たる動きは、時まで緩やかにする. The line is figurative, so it stays bare.",
)

LEVEL_PAGE = "./"
NEXT_LEVEL = "../level-jun2/"
LESSON_COUNT = 14
LESSON_SIZES = [20] * 10 + [21] * 4
SAFE_HOW = {"okurigana", "whole word", "start", "end"}


def load_level() -> tuple[list[dict], dict, list[int]]:
    import csv

    joyo = {}
    with JOYO.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            joyo[row["kanji"]] = row
    records = [
        record
        for record in json.loads(INDEX.read_text(encoding="utf-8"))["characters"]
        if record["introducedAt"] == "3"
    ]
    if len(records) != 284 or len({record["kanji"] for record in records}) != 284:
        raise SystemExit(f"漢検3級 has {len(records)} characters")
    records.sort(key=lambda record: int(joyo[record["kanji"]]["joyo_index"]))
    if {joyo[record["kanji"]]["grade"] for record in records} != {"S"}:
        raise SystemExit("漢検3級 is not entirely 常用漢字表 grade S")
    if sum(LESSON_SIZES) != 284 or LESSON_SIZES != [20] * 10 + [21] * 4:
        raise SystemExit("3級 lessons are not ten of 20 and four of 21")
    lessons = []
    for number, size in enumerate(LESSON_SIZES, start=1):
        lessons.extend([number] * size)
    return records, joyo, lessons


def lesson_nav(number: int) -> str:
    left = (
        f'<a href="{LEVEL_PAGE}">← 漢検3級</a>'
        if number == 1
        else f'<a href="lesson-{number - 1:02d}.html">← 第{number - 1}課</a>'
    )
    right = (
        f'<a href="{NEXT_LEVEL}">漢検準2級 →</a>'
        if number == LESSON_COUNT
        else f'<a href="lesson-{number + 1:02d}.html">第{number + 1}課 →</a>'
    )
    return f"""<div class="navbar">
  {left}
  <a href="{LEVEL_PAGE}">漢検3級</a>
  {right}
</div>"""


def review_block() -> str:
    return """
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLI-ULFjSKz58" target="_blank" rel="noopener noreferrer">小学校以降の常用漢字<br><span style="font-size:0.82rem;font-weight:400">漢検4級–2級 · one collection</span></a>
  </div>
</section>
"""


def card_html(entry: dict) -> str:
    esc = grade2.esc
    slug = entry["slug"]
    number = f"{entry['lesson']:02d}"
    heisig = ""
    if entry["show_heisig"]:
        heisig = f'\n  <p class="sg-heisig">(Heisig: {esc(entry["keyword"])})</p>'
    panels = ['<div class="sg-panels' + ("" if entry["panel_kun"] and entry["panel_on"] else " sg-panels-single") + '">']
    if entry["panel_on"]:
        panels.append(
            f"""    <a class="sg-panel" href="lesson-{number}-readings.html#kanji-{esc(slug)}-on">
      <span class="sg-panel-label" lang="ja">音読み</span>
      <span class="sg-panel-yomi" lang="ja">{esc(entry["panel_on"])}</span>
    </a>"""
        )
    if entry["panel_kun"]:
        panels.append(
            f"""    <a class="sg-panel" href="lesson-{number}-readings.html#kanji-{esc(slug)}-kun">
      <span class="sg-panel-label" lang="ja">訓読み</span>
      <span class="sg-panel-yomi" lang="ja">{esc(entry["panel_kun"])}</span>
    </a>"""
        )
    panels.append("  </div>")
    return f"""<article class="sg-card" id="kanji-{esc(slug)}" data-kanji="{esc(entry["kanji"])}">
  <a class="sg-kanji-link" href="../../{esc(entry["stroke_path"])}">
    <span class="sg-kanji" lang="ja">{esc(entry["kanji"])}</span>
  </a>
  <p class="sg-meaning" lang="en" data-meaning-source="{esc(entry["meaning_sources"])}">{esc(entry["meaning"])}</p>{heisig}
  {chr(10).join(panels)}
  <p class="sg-facts">
    <span lang="ja">部首 <b>{esc(entry["radical"])}</b>（{esc(entry["radical_name"])}）</span>
    <span lang="ja">画数 <b>{entry["strokes"]}</b></span>
  </p>
  <a class="sg-kml-link" href="../../{esc(entry["lesson_path"])}">KMLで詳しく見る</a>
</article>
"""


def write_lesson(number: int, entries: list[dict], hero: dict, notice: str) -> None:
    esc = grade2.esc
    first, last = entries[0]["kanji"], entries[-1]["kanji"]
    title = f"第{number}課 — {first} 〜 {last}"
    anchors = "\n".join(
        f'<a href="#kanji-{esc(entry["slug"])}">{esc(entry["kanji"])}</a>' for entry in entries
    )
    cards = "\n".join(card_html(entry) for entry in entries)
    body = f"""<body class="sg-lesson" id="top">
{lesson_nav(number)}
<div class="lesson-art">
  <img src="{esc(hero["src"])}" alt="{esc(hero["alt"])}" width="{hero["width"]}" height="{hero["height"]}">
</div>
<p class="school-kicker" lang="ja">漢検3級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">常用漢字表の中学校以降の漢字のうち284字</p>
<h1 class="school-title">{esc(title)}</h1>
<p class="sg-to-words"><a href="lesson-{number:02d}-readings.html">読み方とことば</a></p>
<nav class="anchor-list">
{anchors}
</nav>
{cards}
{review_block()}
{lesson_nav(number)}
<p class="school-footer-note">英語・画数・部首の基準は KANJIDIC2（EDRDG、2026-074、2026-03-15）です。読み方は常用漢字表の音訓です。</p>
{notice}
</body>
</html>
"""
    text = grade2.page_head(title, f"漢検3級レベルの漢字。常用漢字表の中学校以降の漢字のうち284字のうち、第{number}課。")
    (GRADE / f"lesson-{number:02d}.html").write_text(text + body, encoding="utf-8")


def write_compiled(number: int, entries: list[dict], notice: str) -> None:
    esc = grade2.esc
    articles = []
    for entry in entries:
        slug = entry["slug"]
        on_html = ""
        kun_html = ""
        if entry["on"]:
            groups = [(grade2.display_reading(raw), entry["words"][raw]) for raw in entry["on"]]
            on_html = f"""  <div class="sg-read-block" id="kanji-{esc(slug)}-on">
    <h3 class="sg-side" lang="ja">音読み</h3>
    {grade2.reading_groups(groups)}
  </div>"""
        if entry["kun"]:
            groups = [(grade2.display_reading(raw), entry["words"][raw]) for raw in entry["kun"]]
            kun_html = f"""  <div class="sg-read-block" id="kanji-{esc(slug)}-kun">
    <h3 class="sg-side" lang="ja">訓読み</h3>
    {grade2.reading_groups(groups)}
  </div>"""
        articles.append(
            f"""<article class="sg-entry" id="kanji-{esc(slug)}">
  <h2 class="sg-entry-kanji" lang="ja">{esc(entry["kanji"])}</h2>
  <a class="sg-entry-back" href="lesson-{number:02d}.html#kanji-{esc(slug)}">第{number}課の{esc(entry["kanji"])}</a>
{on_html}
{kun_html}
</article>"""
        )
    anchors = "\n".join(
        f'<a href="#kanji-{esc(entry["slug"])}">{esc(entry["kanji"])}</a>' for entry in entries
    )
    title = f"第{number}課 — 読み方とことば"
    body = f"""<body class="sg-readings sg-compiled" id="top">
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="{LEVEL_PAGE}">漢検3級</a>
</div>
<p class="school-kicker" lang="ja">漢検3級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">常用漢字表の中学校以降の漢字のうち284字</p>
<h1 class="school-title">{esc(title)}</h1>
{grade2.furigana_bar()}
<nav class="anchor-list">
{anchors}
</nav>
{chr(10).join(articles)}
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="{LEVEL_PAGE}">漢検3級</a>
</div>
{notice}
{grade2.furigana_script()}
</body>
</html>
"""
    text = grade2.page_head(title, f"漢検3級 第{number}課の読み方とことば。常用漢字表の中学校以降の漢字のうち284字。")
    (GRADE / f"lesson-{number:02d}-readings.html").write_text(text + body, encoding="utf-8")


def kanji_count(surface: str) -> int:
    return sum(1 for char in surface if not grade2.hiragana(char))


BOUNDARY = "。、！？はがをにのともへでやてと"


def _tail_ok(rest: str, starters: tuple[str, ...]) -> bool:
    if not rest or rest[0] in BOUNDARY or rest.startswith("です"):
        return True
    return rest.startswith(starters)


def follows_reading(raw: str, follows: str) -> bool:
    """True when `follows` is this reading's okurigana or a real inflection of it."""
    special, _stem, okuri = grade2.parse_reading(raw)
    if special or not follows:
        return False
    if not okuri:
        return follows[0] in BOUNDARY
    if follows.startswith(okuri):
        return _tail_ok(follows[len(okuri):], ())
    verb_tail = ("ます", "ました", "ません", "ましょう", "て", "た", "だ", "ない", "ぬ", "ず")
    if okuri.endswith("る") and len(okuri) > 1:
        base = okuri[:-1]
        if follows.startswith(base):
            return _tail_ok(follows[len(base):], ("り", "っ", "れ", "ろ", "よ") + verb_tail)
    if okuri == "る":
        for alt in ("り", "っ", "れ", "ろ"):
            if follows.startswith(alt) and _tail_ok(follows[len(alt):], verb_tail):
                return True
    # masu/te stems, then the conditional column, which only takes ば.
    godan = {
        "う": (("い", "っ"), "え"),
        "く": (("き", "い"), "け"),
        "ぐ": (("ぎ", "い"), "げ"),
        "す": (("し",), "せ"),
        "つ": (("ち", "っ"), "て"),
        "ぬ": (("に",), "ね"),
        "ぶ": (("び", "ん"), "べ"),
        "む": (("み", "ん"), "め"),
    }
    stems, conditional = godan.get(okuri[-1], ((), ""))
    for alt in stems:
        prefix = okuri[:-1] + alt
        if follows.startswith(prefix) and _tail_ok(follows[len(prefix):], verb_tail):
            return True
    if conditional:
        prefix = okuri[:-1] + conditional
        if follows.startswith(prefix) and _tail_ok(follows[len(prefix):], ("ば",)):
            return True
    if okuri.endswith("い"):
        prefix = okuri[:-1] + "く"
        if follows.startswith(prefix):
            return _tail_ok(follows[len(prefix):], ("な", "し") + verb_tail)
    return False


def same_stem_readings(entry: dict, stem: str) -> list[str]:
    found = []
    for raw in entry["on"] + entry["kun"]:
        special, raw_stem, _okuri = grade2.parse_reading(raw)
        if not special and raw_stem == stem:
            found.append(raw)
    return found


def attest_example(item: dict, entry: dict) -> None:
    source = REPO / item["source"]
    text = source.read_text(encoding="utf-8")
    kanji = item["kanji"]
    if item["mode"] == "ruby":
        ruby = f"<ruby>{kanji}<rt>{item['reading']}</rt></ruby>"
        if ruby not in text or item["snippet"] not in text:
            raise SystemExit(f"Missing ruby example for {kanji} {item['raw']}")
        assigned = grade2.assign_compound(
            kanji, item["surface"], item["reading"], entry["on"], entry["kun"]
        )
        if assigned is None or assigned[1] != item["raw"]:
            raise SystemExit(f"{item['surface']}（{item['reading']}） does not lock {kanji} {item['raw']}")
        return
    if item["mode"] == "ruby-stem":
        ruby = f"<ruby>{kanji}<rt>{item['stem']}</rt></ruby>"
        if item["snippet"] not in text:
            raise SystemExit(f"Missing ruby-stem snippet for {kanji} {item['raw']}")
        start = 0
        while True:
            index = text.find(ruby, start)
            if index < 0:
                break
            after = text[index + len(ruby):]
            if after.startswith(item["follows"]):
                locked = [
                    raw
                    for raw in same_stem_readings(entry, item["stem"])
                    if follows_reading(raw, item["follows"])
                ]
                if locked != [item["raw"]]:
                    raise SystemExit(f"{kanji} {item['follows']} locks {locked}, not {item['raw']}")
                return
            start = index + len(ruby)
        raise SystemExit(f"Missing ruby-stem for {kanji} {item['raw']}: {item['follows']}")
    data = json.loads(text)
    if item["mode"] == "stem":
        for character in data.get("characters") or []:
            for compound in character.get("compounds") or []:
                example = compound.get("example") or {}
                if item["snippet"] not in (example.get("ja") or ""):
                    continue
                segments = example.get("segments") or []
                for index, segment in enumerate(segments):
                    if segment.get("text") != kanji:
                        continue
                    if grade2.kata_to_hira(segment.get("reading") or "") != item["stem"]:
                        continue
                    nxt = segments[index + 1].get("text") if index + 1 < len(segments) else ""
                    if not nxt.startswith(item["follows"]):
                        continue
                    locked = [
                        raw
                        for raw in same_stem_readings(entry, item["stem"])
                        if follows_reading(raw, item["follows"])
                    ]
                    if locked != [item["raw"]]:
                        raise SystemExit(
                            f"{kanji} {item['follows']} locks {locked}, not {item['raw']}"
                        )
                    return
        raise SystemExit(f"Missing segment for {kanji} {item['raw']}: {item['snippet']}")
    if item["mode"] != "word":
        raise SystemExit(f"{kanji} has an unknown example mode")
    for character in data.get("characters") or []:
        for compound in character.get("compounds") or []:
            candidates = []
            if compound.get("surface") and compound.get("reading"):
                candidates.append((compound["surface"], compound["reading"], compound.get("example") or {}))
            example = compound.get("example") or {}
            for segment in example.get("segments") or []:
                if segment.get("text") and segment.get("reading"):
                    candidates.append((segment["text"], segment["reading"], example))
            for surface, reading, example in candidates:
                if surface != item["surface"] or grade2.kata_to_hira(reading) != item["reading"]:
                    continue
                if item["snippet"] not in (example.get("ja") or "") and item["snippet"] not in surface:
                    continue
                assigned = grade2.assign_compound(
                    kanji, surface, grade2.kata_to_hira(reading), entry["on"], entry["kun"]
                )
                if assigned is None or assigned[1] != item["raw"]:
                    raise SystemExit(f"{surface}（{reading}） does not lock {kanji} {item['raw']}")
                return
    raise SystemExit(f"Missing word for {kanji} {item['raw']}: {item['surface']}")


def add_verified_examples(entry: dict) -> None:
    notes = list(entry["example_notes"])
    for item in VERIFIED_EXAMPLES:
        if item["kanji"] != entry["kanji"]:
            continue
        if item["raw"] not in entry["on"] + entry["kun"]:
            raise SystemExit(f"{item['kanji']} example uses {item['raw']}, which is not a 常用漢字表 reading")
        if item["surface"].count(item["kanji"]) != 1:
            raise SystemExit(f"{item['surface']} does not contain {item['kanji']} once")
        attest_example(item, entry)
        label = grade2.display_reading(item["raw"])
        if label not in entry["bare"]:
            raise SystemExit(f"{item['kanji']} {label} already has an example")
        entry["words"][item["raw"]] = [(item["surface"], item["reading"])]
        entry["bare"].remove(label)
        snippet = item["snippet"].rstrip("。.")
        notes.append(
            f"Added {item['surface']}（{item['reading']}） for {label} from {item['source']} ({item['form']}). Snippet: {snippet}。"
        )
    entry["example_notes"] = notes


def fill_from_corpus(entry: dict, pool: list[tuple[str, str]]) -> None:
    """Attach a short KML headword when it is filed under another character."""
    kanji = entry["kanji"]
    notes = list(entry["example_notes"])
    for raw in entry["on"] + entry["kun"]:
        label = grade2.display_reading(raw)
        if label not in entry["bare"]:
            continue
        special, stem, _okuri = grade2.parse_reading(raw)
        if special:
            continue
        added = []
        seen = set()
        for surface, reading in pool:
            if surface.count(kanji) != 1:
                raise SystemExit(f"{surface} was offered for {kanji} but does not contain it once")
            if (surface, reading) in seen:
                continue
            assigned = grade2.assign_compound(kanji, surface, reading, entry["on"], entry["kun"])
            if assigned is None or assigned[1] != raw:
                continue
            kind, _raw, how = assigned
            if how not in SAFE_HOW:
                continue
            if kind == "on" and len(stem) < 2:
                continue
            if how in {"start", "end"} and kanji_count(surface) > 3:
                continue
            if (kanji, surface) in SKIP_EXAMPLES:
                continue
            seen.add((surface, reading))
            added.append((surface, reading, how))
        added.sort(key=lambda item: (kanji_count(item[0]), len(item[0]), item[0]))
        chosen = added[: grade2.MAX_EXAMPLES]
        if not chosen:
            continue
        entry["words"][raw] = [(surface, reading) for surface, reading, _how in chosen]
        entry["bare"].remove(label)
        for surface, reading, how in chosen:
            notes.append(
                f"Added {surface}（{reading}） for {label} from a KML compound filed under another character ({how})."
            )
    entry["example_notes"] = notes


def apply_meaning(entry: dict, glosses: list[str]) -> None:
    choice = MEANING_CHOICES.get(entry["kanji"])
    if not choice:
        return
    known = {gloss.lower() for gloss in glosses}
    for text, source in choice["parts"]:
        if source == "kanjidic" and text.lower() not in known:
            raise SystemExit(f"{entry['kanji']} meaning “{text}” is not a KANJIDIC2 gloss")
        if source == "heisig" and text != entry["keyword"]:
            raise SystemExit(f"{entry['kanji']} heisig wording “{text}” is not the keyword “{entry['keyword']}”")
        if source not in {"kanjidic", "heisig", "paraphrase"}:
            raise SystemExit(f"{entry['kanji']} has an unknown meaning source")
    entry["meaning"] = "; ".join(text for text, _source in choice["parts"])
    entry["meaning_sources"] = "+".join(dict.fromkeys(source for _text, source in choice["parts"]))
    entry["meaning_note"] = choice["note"]
    entry["show_heisig"] = choice["show_heisig"]


def prepare(records: list[dict], joyo: dict, lessons: list[int], kanjidic: dict, compounds: dict) -> list[dict]:
    wider = level8.compounds_by_kanji({record["kanji"] for record in records})
    entries = []
    for index, record in enumerate(records):
        kanji = record["kanji"]
        info = kanjidic[kanji]
        if info["classical"] not in RADICALS:
            raise SystemExit(f"No radical name for {kanji} classical {info['classical']}")
        glyph, name, note = RADICALS[info["classical"]]
        if info["classical"] == 47 and not note:
            note = "康熙字典の47は川です。巛は同じ部の別の字形です。"
        if kanji in CHARACTER_RADICAL_NOTES:
            note = CHARACTER_RADICAL_NOTES[kanji]
        if kanji in RADICAL_CARD:
            glyph, name, note = RADICAL_CARD[kanji]
        lesson_no, anchor, keyword = grade2.keyword_from_page(record)
        compared = grade2.grade1.compare_meanings(keyword, info["glosses"])
        row = joyo[kanji]
        ons = grade2.split_joyo(re.sub(r"\[\d+\]", "", row["on_kana"]))
        kuns = grade2.split_joyo(re.sub(r"\[\d+\]", "", row["kun_kana"]))
        words, bare, unmatched, match_notes = grade2.attach_words(
            kanji, ons, kuns, compounds.get(kanji, [])
        )
        stroke_path = record["strokePage"].lstrip("/")
        lesson_path = record["lessonPage"].lstrip("/")
        if not (REPO / stroke_path).is_file():
            raise SystemExit(f"Missing stroke page for {kanji}")
        if not (REPO / lesson_path.split("#", 1)[0]).is_file():
            raise SystemExit(f"Missing KML lesson for {kanji}")
        lesson = lessons[index]
        hero_slug, hero_kanji = HERO_CHOICES[lesson]
        if index == sum(lessons.count(n) for n in range(1, lesson)) and kanji != records[index]["kanji"]:
            raise SystemExit("lesson index drifted")
        if hero_kanji not in [item["kanji"] for item in records if lessons[records.index(item)] == lesson]:
            raise SystemExit(f"Cover {hero_kanji} is not in lesson {lesson}")
        entries.append(
            {
                "kanji": kanji,
                "slug": record["slug"],
                "lesson": lesson,
                "meaning": compared["standard"],
                "keyword": keyword,
                "meaning_kind": compared["kind"],
                "meaning_reason": compared["reason"],
                "meaning_sources": "kanjidic",
                "meaning_note": "",
                "show_heisig": compared["kind"] == "differs",
                "strokes": info["strokes"],
                "joyo_strokes": int(row["strokes"]),
                "radical": glyph,
                "radical_name": name,
                "radical_note": note,
                "radical_number": info["classical"],
                "radical_source": "kanjidic",
                "joyo_radical": row["radical"],
                "joyo_index": int(row["joyo_index"]),
                "heisig_number": record["heisigNumber"],
                "source_lesson": lesson_no,
                "anchor": anchor,
                "on": ons,
                "kun": kuns,
                "panel_on": "・".join(grade2.display_reading(item) for item in ons),
                "panel_kun": "・".join(grade2.display_reading(item) for item in kuns),
                "words": words,
                "bare": bare,
                "unmatched": unmatched,
                "match_notes": match_notes,
                "example_notes": [],
                "stroke_path": stroke_path,
                "lesson_path": lesson_path,
                "cover_slug": hero_slug,
            }
        )
        apply_meaning(entries[-1], info["glosses"])
        entries[-1]["meaning_review"] = MEANING_REVIEW.get(kanji, "")
        fill_from_corpus(entries[-1], wider[kanji])
        add_verified_examples(entries[-1])
    return entries


def write_review(entries: list[dict], meta: dict, heroes: dict[int, dict]) -> None:
    bare = sum(len(entry["bare"]) for entry in entries)
    lines = [
        "# 漢検3級 vocabulary review",
        "",
        "Learner pages do not explain these choices. The covers are approved, including lettering.",
        "Nothing here has been deployed.",
        "",
        f"KANJIDIC2 {meta['database']}, {meta['date']}.",
        "English on a card is the first KANJIDIC2 gloss, unless MEANING_CHOICES names a clearer gloss from that same list, a Heisig keyword, or a marked paraphrase.",
        "A displayed meaning tagged kanjidic is that exact gloss. A paraphrase is editorial. A meaning tagged heisig is that keyword used as the card wording.",
        "Heisig stays on its own line only when the keyword is not already the displayed wording.",
        "Readings are the 常用漢字表 音訓. Parentheses are the table’s indented readings.",
        "Example words come from `kml/data/compounds/`. A word filed under another character is used only when",
        "the same matcher used on 8級 locks it to that reading, and the word is a verb or a headword of at most three kanji.",
        "One-mora on readings are not filled that way. A dictionary form is added only when a sentence segment",
        "locks that exact reading. A reading with no suitable word stays bare.",
        f"Bare readings remaining: {bare}.",
        "",
        "Order is the 常用漢字表 掲載順 of the 284 grade-S characters at 漢検3級.",
        "There is no 3級 school-film cut. Lessons are ten of 20 and four of 21.",
        "The music link is the existing post-elementary collection, shared by 漢検4級 through 漢検2級.",
        "",
        "The overview hero is 鯨 `kml/assets/studies/whale.jpg`. It is in 第4課 and is not that lesson’s cover.",
        "Lesson covers are existing study images, one character from each lesson:",
        "",
    ]
    for number, (slug, kanji) in HERO_CHOICES.items():
        hero = heroes[number]
        note = ""
        lettering = {
            "mountain_peak": " — 山頂 is lettered on the post",
            "outskirts": " — 郊 is lettered on the sign",
            "waiter": " — 心 is lettered on the scroll",
            "bell": " — vertical text is lettered on the pillar",
            "rapids": " — 瀬 is lettered on the rock",
            "burial": " — 南無阿弥陀仏 is lettered on the stone",
            "carve": " — 彫 is lettered on the sign",
            "black_ink": " — 墨 is lettered on the paper",
        }
        if slug in lettering:
            note = lettering[slug]
        elif hero["width"] != 1672 or hero["height"] != 941:
            note = f" — native 16:9 at {hero['width']}×{hero['height']}"
        lines.append(f"- 第{number}課 {kanji} `kml/assets/studies/{slug}.jpg`{note}")
    lines.extend(
        [
            "",
            "Not used: 穫 `harvest.jpg` carries a long vertical text.",
            "",
            "## Cross-file examples",
            "",
            "Each attached word contains its target character once, and the matcher locks that character’s reading.",
            "A dictionary form is added when a sentence segment or a verse ruby locks that exact reading.",
            "A reading without that lock stays bare.",
            "",
            "## Kept",
            "",
            "- Clearer exact KANJIDIC glosses, with the Heisig line omitted when it restates the card: 架 frame; shelf, 岳 peak; mountain, 恨 regret; resentment, 施 give; alms, 穂 ear (grain), 葬 bury, 奉 offer; dedicate, 乏 scarce, 揚 raise; hoist, 了 complete; finish, 乙 the latter; strange, 駐 reside in; resident, 陪 accompany; attend on, 幽 secluded; faint.",
            "- 厘 is “rin; thousandth”. “rin” is the KANJIDIC gloss. “thousandth” is the Heisig keyword. No separate Heisig line.",
            "- Context still changes the sense: 乙（甲乙 / 乙な / the fishhook shape）, 駐（駐在 / 駐車）, 陪（attend / 陪審）, 幽（幽閉 / 幽玄 / 幽霊）, 厘（a thousandth / 1/10 sen / 1/10 bu）.",
            "- First gloss kept, Heisig not shown: 遇 meet, 掲 put up (a notice), 紺 dark blue, 墾 ground-breaking, 昇 rise up, 掌 palm of hand, 随 follow, 胆 gall bladder, 陳 exhibit.",
            "",
            "## Held back",
            "",
        ]
    )
    for item in HELD_BACK:
        lines.append(f"- {item}")
    lines.extend(["", "## Needs review", ""])
    for entry in entries:
        flags = []
        if entry["meaning_note"]:
            flags.append(entry["meaning_note"])
        elif entry.get("meaning_review"):
            flags.append(entry["meaning_review"])
        elif entry["meaning_kind"] != "equivalent":
            flags.append(
                f"Meaning “{entry['meaning']}”, Heisig “{entry['keyword']}” ({entry['meaning_kind']}: {entry['meaning_reason']})"
            )
        if entry["joyo_strokes"] != entry["strokes"]:
            flags.append(f"画数: KANJIDIC {entry['strokes']}, 常用漢字表 {entry['joyo_strokes']}")
        if entry["radical_note"]:
            flags.append(entry["radical_note"])
        if entry["joyo_radical"] != entry["radical"]:
            flags.append(
                f"joyo_kanji.csv の部首欄は{entry['joyo_radical']}、カードは {entry['radical']}（{entry['radical_name']}）、出典 {entry['radical_source']}"
            )
        if entry["bare"]:
            flags.append("例のない読み: " + "、".join(entry["bare"]))
        if entry["unmatched"]:
            flags.append("例にしていない語: " + "、".join(entry["unmatched"][:8]))
            if len(entry["unmatched"]) > 8:
                flags.append(f"ほか{len(entry['unmatched']) - 8}語")
        flags.extend(entry["example_notes"])
        flags.extend(entry["match_notes"])
        if not flags:
            continue
        lines.append(f"### {entry['kanji']}（第{entry['lesson']}課）")
        lines.append("")
        for flag in flags:
            lines.append(f"- {flag}")
        lines.append("")
    lines.extend(
        [
            "## 部首",
            "",
            "The card uses the KANJIDIC2 classical radical, the same default as 10級 through 4級.",
            "Names new at this level with a KANJIDIC2 `rad_name`: 匚 はこがまえ, 无 むにょう（むとも、なしとも）, 虍 とらかんむり（とらがしらとも）.",
            "These cards stay on the KANJIDIC2 radical where the joyo column names the radical of the traditional character: 寿 寸（士, from 壽）, 双 又（隹, from 雙）, 翻 羽（飛, from 飜）.",
            "辶, 阝, 攵, 艹, 礻, and 戸 on these cards are the printed forms of 辵, 阜 or 邑, 攴, 艸, 示, and 戶.",
            "着 is not in 3級. Its 8級 exception, 羊 rather than 目, is not copied onto other characters.",
            "",
        ]
    )
    REVIEW.write_text("\n".join(lines), encoding="utf-8")


def write_order(entries: list[dict], meta: dict) -> None:
    lessons = []
    for number in range(1, LESSON_COUNT + 1):
        group = [entry for entry in entries if entry["lesson"] == number]
        lessons.append({"lesson": number, "characters": [entry["kanji"] for entry in group]})
    payload = {
        "school": "S",
        "level": "3",
        "count": 284,
        "order": "五十音順",
        "reference": "常用漢字表 grade S via joyo_kanji.csv, the 284 characters introduced at 漢検3級",
        "kanjidic2": {
            "file": "kml/kanjidic2.xml",
            "databaseVersion": meta["database"],
            "dateOfCreation": meta["date"],
        },
        "lessons": lessons,
        "characters": [
            {
                "kanji": entry["kanji"],
                "slug": entry["slug"],
                "joyoIndex": entry["joyo_index"],
                "heisigNumber": entry["heisig_number"],
                "sourceLesson": entry["source_lesson"],
                "standardMeaning": entry["meaning"],
                "heisigKeyword": entry["keyword"],
                "meaningKind": entry["meaning_kind"],
                "meaningReason": entry["meaning_reason"],
            }
            for entry in entries
        ],
    }
    ORDER.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_heroes(heroes: dict[int, dict], overview: dict) -> None:
    payload = {
        "overview": {"src": overview["src"], "alt": overview["alt"]},
        "lessons": {
            str(number): {"src": hero["src"], "alt": hero["alt"]}
            for number, hero in heroes.items()
        },
    }
    HEROES.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checked_hero(slug: str, kanji: str, entries: list[dict], lesson: int | None) -> dict:
    path = STUDIES / f"{slug}.jpg"
    if not path.is_file():
        raise SystemExit(f"Missing cover {path}")
    width, height = grade2.jpeg_size(path)
    if abs(width / height - 16 / 9) > 0.015:
        raise SystemExit(f"Cover {slug}.jpg is {width}×{height}, not 16:9")
    owner = next(entry for entry in entries if entry["slug"] == slug)
    if owner["kanji"] != kanji or (lesson is not None and owner["lesson"] != lesson):
        raise SystemExit(f"Cover {kanji}/{slug} is not lesson {lesson}")
    return {
        "src": f"../../kml/assets/studies/{slug}.jpg",
        "alt": kanji,
        "width": width,
        "height": height,
    }


def main() -> None:
    notice = DISCLAIMER.read_text(encoding="utf-8").strip()
    if "日本漢字能力検定協会" not in notice:
        raise SystemExit("Disclaimer partial is incomplete")
    records, joyo, lessons = load_level()
    kanjidic, meta = grade2.load_kanjidic({record["kanji"] for record in records})
    compounds = grade2.load_compounds()
    entries = prepare(records, joyo, lessons, kanjidic, compounds)
    heroes = {
        number: checked_hero(slug, kanji, entries, number)
        for number, (slug, kanji) in HERO_CHOICES.items()
    }
    overview = checked_hero(*OVERVIEW_HERO, entries, None)
    GRADE.mkdir(parents=True, exist_ok=True)
    for number in range(1, LESSON_COUNT + 1):
        group = [entry for entry in entries if entry["lesson"] == number]
        if not group:
            raise SystemExit(f"Lesson {number} is empty")
        write_lesson(number, group, heroes[number], notice)
        write_compiled(number, group, notice)
        print(f"Wrote lesson {number} ({len(group)})")
    write_order(entries, meta)
    write_heroes(heroes, overview)
    write_review(entries, meta, heroes)
    bare = sum(len(entry["bare"]) for entry in entries)
    print(f"bare readings {bare}")
    print("validation passed")


if __name__ == "__main__":
    main()
