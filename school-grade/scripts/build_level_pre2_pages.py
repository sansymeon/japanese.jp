#!/usr/bin/env python3
"""Write the sixteen 漢検準2級 lesson pages and their compiled vocabulary pages.

Uses the 漢検準2級 card layout. Output lives at kanken/level-jun2/.
The level entrance is written by kml/scripts/build_kanken_level_pages.py --levelpre2.
The 328 characters are the 常用漢字表 grade-S rows whose 漢検 level is pre2,
in 掲載順. There is no separate school-film cut for this level. The
post-elementary films are one collection shared by 漢検4級 through 漢検2級.
Lessons are eight groups of 20 and eight groups of 21, in that order.

English starts from the first KANJIDIC2 gloss. MEANING_CHOICES may name a
clearer gloss from that same entry, or a marked paraphrase. Heisig stays on
its own line only when that keyword is not already the displayed wording.
Radicals stay on the KANJIDIC2 classical radical. 着 is not in this level.

Bare readings are filled from KML compounds filed under any character when
the reading match is the same mechanical test used on 8級, limited to a
short headword or a verb. One-mora on readings are not filled that way.
VERIFIED_EXAMPLES then adds a dictionary form only when a KML sentence
segment, or ruby in a KML verse, locks that exact 常用漢字表 reading.
A ruby may end after the joyo hyphen. It still locks when the ruby and the
kana written after it spell that whole reading and no other reading.
A reading with no suitable verified word stays bare and is listed in the review.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GRADE = REPO / "kanken/level-jun2"
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
    45: ("屮", "ふるくさ", ""),
    87: ("爪", "つめ", "KANJIDIC2 に rad_name はありません。カードは爪の読みです。爫の呼び名はつめかんむりです。"),
    98: ("瓦", "かわら", "KANJIDIC2 に rad_name はありません。カードは瓦の読みです。"),
    121: ("缶", "ほとぎ", ""),
    129: ("聿", "ふでづくり", ""),
    200: ("麻", "あさ", "KANJIDIC2 に rad_name はありません。カードは麻の読みです。"),
}

# One existing 16:9 study image from a character in that lesson.
# The overview hero, 竜, is in lesson 16 and is not that lesson’s cover.
HERO_CHOICES = {
    1: ("monkey", "猿"),
    2: ("horizon", "涯"),
    3: ("sunrise", "暁"),
    4: ("mountain_stream", "渓"),
    5: ("flood", "洪"),
    6: ("umbrella", "傘"),
    7: ("early_evening", "宵"),
    8: ("reef", "礁"),
    9: ("sugi", "杉"),
    10: ("frost", "霜"),
    11: ("angling", "釣"),
    12: ("den", "洞"),
    13: ("cat", "猫"),
    14: ("flower_pot", "瓶"),
    15: ("headland", "岬"),
    16: ("willow", "柳"),
}
OVERVIEW_HERO = ("dragon", "竜")

# Each part is an exact KANJIDIC2 gloss, a Heisig keyword, or a marked paraphrase.
# show_heisig is false when that keyword is already the displayed wording,
# or when it is not a gloss.
MEANING_CHOICES = {
    "逸": {
        "parts": (("deviate", "kanjidic"), ("elude", "kanjidic")),
        "show_heisig": False,
        "note": "The card stays “deviate; elude”. “deviate” is the first KANJIDIC gloss, and “elude” is the sixth. 逸脱 is “deviate”, and 逃逸 is “elude”. The 常用漢字表 English column is “deviate”. The lesson-page Heisig keyword “elude” is that sixth gloss. “idleness” and “leisure” are also glosses, for 安逸, and stay off the card.",
    },
    "虞": {
        "parts": (("fear", "kanjidic"), ("uneasiness", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “uneasiness” is the second gloss on the card.",
    },
    "懐": {
        "parts": (("feelings", "kanjidic"), ("yearn", "kanjidic"), ("pocket", "kanjidic")),
        "show_heisig": False,
        "note": "KANJIDIC glosses “feelings”, “yearn”, and “pocket” (the first, third, and eighth). “heart” is the second gloss and restates “feelings”. “yearn” is the なつかしい reading. “pocket” is also the 常用漢字表 English column and the lesson-page Heisig keyword, so that keyword is not given its own line.",
    },
    "享": {
        "parts": (("enjoy", "kanjidic"), ("receive", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “receive” is the second gloss on the card.",
    },
    "薫": {
        "parts": (("fragrant", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “fragrant”. The first gloss “send forth fragrance” is the verb form of the same sense. Heisig “fragrant” is this gloss.",
    },
    "洪": {
        "parts": (("flood", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “flood”. The first gloss “deluge” is the same sense in rarer wording. Heisig “flood” is this gloss.",
    },
    "宵": {
        "parts": (("evening", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “evening”. The first gloss “wee hours” is later at night than 宵. Heisig “early evening” restates “evening” and is not a gloss.",
    },
    "懸": {
        "parts": (("hang", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “hang”. The first gloss “state of suspension” is the noun form of the same sense. Heisig “suspend” is not a gloss.",
    },
    "酌": {
        "parts": (("serving sake", "kanjidic"), ("ladle", "kanjidic")),
        "show_heisig": False,
        "note": "KANJIDIC glosses “serving sake” and “ladle” (the second and fifth). “serving sake” is 晩酌. “ladle” is the くむ reading. The first gloss “bar-tending” is the same hosting sense. The 常用漢字表 English column and the lesson-page Heisig keyword are “bartending”, which restates that sense and is not a separate line.",
    },
    "挟": {
        "parts": (("pinch", "kanjidic"), ("between", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “sandwiched” is not a gloss.",
    },
    "披": {
        "parts": (("expose", "kanjidic"), ("open", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “reveal” is not a gloss.",
    },
    "塀": {
        "parts": (("fence", "kanjidic"), ("wall", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “brick wall” is not a gloss.",
    },
    "僕": {
        "parts": (("me", "kanjidic"), ("servant", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “I (male)” is also a gloss. Heisig “me male” names that male sense and is not an exact gloss.",
    },
    "奔": {
        "parts": (("run", "kanjidic"), ("bustle", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “bustle” is the second gloss on the card.",
    },
    "猶": {
        "parts": (("furthermore", "kanjidic"), ("still", "kanjidic")),
        "show_heisig": False,
        "note": "The card stays “furthermore; still”. “furthermore” is the first KANJIDIC gloss, and “still” is the second. “yet” is the third and restates “still”. The 常用漢字表 English column is “furthermore”. The lesson-page Heisig keyword “still” is the second gloss. heisig_list.csv says “waver”, which is not the page keyword and is not a gloss.",
    },
    "履": {
        "parts": (("perform", "kanjidic"), ("put on (the feet)", "kanjidic")),
        "show_heisig": False,
        "note": "KANJIDIC glosses “perform” and “put on (the feet)” (the first and sixth). “perform” is 履行. “put on (the feet)” is the はく reading. “footgear” is the third gloss, the 常用漢字表 English column, and the lesson-page Heisig keyword. “shoes” and “boots” are that same noun sense. The keyword restates it, so it is not given its own line.",
    },
    "騰": {
        "parts": (("rising", "kanjidic"),),
        "show_heisig": False,
        "note": "The card stays “rising”, the third KANJIDIC gloss. “leaping up” and “jumping up” are the first two glosses and name the same motion more physically. The 常用漢字表 English column and the lesson-page Heisig keyword are “inflation”, which is the 騰貴 use of “rising” and is not a KANJIDIC gloss.",
    },
    "戻": {
        "parts": (("return", "kanjidic"), ("revert", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “re-” is a prefix, not a meaning by itself. Heisig “revert” is the second gloss on the card.",
    },
}

# First gloss kept. Heisig is the same sense and is not an exact gloss, so it is not shown.
MEANING_REVIEW = {
    "翁": "KANJIDIC gloss “venerable old man”. Heisig “elderly man” is the same sense and is not an exact gloss.",
    "暁": "KANJIDIC gloss “daybreak”. Heisig “sunrise” is the same time of day and is not a gloss.",
    "碁": "KANJIDIC gloss “Go”. Heisig “go game” is the longer form of this gloss.",
    "璽": "KANJIDIC gloss “emperor's seal”. Heisig “imperial seal” is the same object and is not an exact gloss.",
    "杉": "KANJIDIC gloss “cedar”. Heisig “sugi” is the Japanese name of this tree. “cryptomeria” is the other gloss.",
    "坪": "KANJIDIC gloss “two-mat area”. Heisig “two mats” is the shorter form of this gloss.",
    "忍": "KANJIDIC gloss “endure”. Heisig “endure silently” is the longer form of this gloss.",
    "酪": "KANJIDIC gloss “dairy products”. Heisig “dairy” is the shorter form of this gloss.",
    "硫": "KANJIDIC gloss “sulphur”. Heisig “sulfur” is the same word in American spelling.",
    "賓": "KANJIDIC gloss “V.I.P.”. Heisig “VIP” is the same abbreviation. “guest” is another gloss.",
    "瓶": "KANJIDIC gloss “bottle”. Heisig “flower pot” is not a gloss.",
    "扶": "KANJIDIC gloss “aid”. Heisig “support” is not a gloss.",
    "轄": "KANJIDIC gloss “control”. Heisig “jurisdiction” is not a gloss. “wedge” is another gloss.",
    "嚇": "KANJIDIC gloss “menacing”. Heisig “upbraid” is not a gloss.",
    "訟": "KANJIDIC gloss “sue”. Heisig “litigation” is not a gloss.",
    "曹": "KANJIDIC gloss “office”. Heisig “cadet” is not a gloss.",
    "貞": "KANJIDIC gloss “upright”. Heisig “virtue” is not a gloss.",
    "頒": "KANJIDIC gloss “distribute”. Heisig “partition” is a later gloss and is not shown.",
    "累": "KANJIDIC gloss “accumulate”. Heisig “pile up” is not a gloss.",
}

VERIFIED_EXAMPLES = (
    {
        "kanji": "釣",
        "raw": "つ-る",
        "surface": "釣る",
        "reading": "つる",
        "snippet": "時々、父と川へ釣りに行きます。",
        "source": "kml/data/compounds/lesson_09.json",
        "mode": "stem",
        "stem": "つ",
        "follows": "り",
        "form": "釣りに is つ-る",
    },
    {
        "kanji": "履",
        "raw": "は-く",
        "surface": "履く",
        "reading": "はく",
        "snippet": "茶色の靴を履いて出かけました。",
        "source": "kml/data/compounds/lesson_14.json",
        "mode": "stem",
        "stem": "は",
        "follows": "い",
        "form": "履いて is は-く",
    },
    {
        "kanji": "渇",
        "raw": "かわ-く",
        "surface": "渇く",
        "reading": "かわく",
        "snippet": "埃で喉が渇きました。",
        "source": "kml/data/compounds/lesson_89.json",
        "mode": "stem",
        "stem": "かわ",
        "follows": "き",
        "form": "渇きました is かわ-く",
    },
    {
        "kanji": "充",
        "raw": "あ-てる",
        "surface": "充てる",
        "reading": "あてる",
        "snippet": "夜は小説の創作に充てています。",
        "source": "kml/data/compounds/lesson_88.json",
        "mode": "stem",
        "stem": "あ",
        "follows": "て",
        "form": "充てています is あ-てる",
    },
    {
        "kanji": "薦",
        "raw": "すす-める",
        "surface": "薦める",
        "reading": "すすめる",
        "snippet": "an old man recommends a single book.",
        "source": "kml/contents/books/book_01/lessons/lesson_108.html",
        "mode": "ruby-stem",
        "stem": "すす",
        "follows": "める。",
        "form": "薦める is すす-める. The verse’s English is “an old man recommends a single book”",
    },
    {
        "kanji": "懸",
        "raw": "か-ける",
        "surface": "懸ける",
        "reading": "かける",
        "snippet": "When you devote yourself to a dream,",
        "source": "kml/contents/books/book_01/lessons/lesson_75.html",
        "mode": "ruby-stem",
        "stem": "か",
        "follows": "けて",
        "form": "懸けて is か-ける. か-かる would be 懸かって. The verse’s English is “When you devote yourself to a dream”",
    },
    {
        "kanji": "弦",
        "raw": "つる",
        "surface": "弦",
        "reading": "つる",
        "snippet": "Pluck a single string,",
        "source": "kml/contents/books/book_01/lessons/lesson_75.html",
        "mode": "ruby-stem",
        "stem": "つる",
        "follows": "を",
        "form": "弦を is つる. The verse’s English is “Pluck a single string”",
    },
    {
        "kanji": "柳",
        "raw": "やなぎ",
        "surface": "柳",
        "reading": "やなぎ",
        "snippet": "The willow by the river",
        "source": "kml/contents/books/book_01/lessons/lesson_77.html",
        "mode": "ruby-stem",
        "stem": "やなぎ",
        "follows": "は、",
        "form": "柳は is やなぎ. The verse’s English is “The willow by the river”",
    },
    {
        "kanji": "漆",
        "raw": "うるし",
        "surface": "漆",
        "reading": "うるし",
        "snippet": "The lacquered bowl",
        "source": "kml/contents/books/book_01/lessons/lesson_51.html",
        "mode": "ruby-stem",
        "stem": "うるし",
        "follows": "の",
        "form": "漆の is うるし. The verse’s English is “The lacquered bowl”",
    },
    {
        "kanji": "藻",
        "raw": "も",
        "surface": "藻",
        "reading": "も",
        "snippet": "Waterweed sways at the bottom of the clear pond,",
        "source": "kml/contents/books/book_01/lessons/lesson_110.html",
        "mode": "ruby-stem",
        "stem": "も",
        "follows": "が",
        "form": "藻が is も. The verse’s English is “Waterweed sways at the bottom of the clear pond”",
    },
    {
        "kanji": "癒",
        "raw": "い-やす",
        "surface": "癒す",
        "reading": "いやす",
        "snippet": "Small tools mend wounds.",
        "source": "kml/contents/books/book_01/lessons/lesson_15.html",
        "mode": "ruby-split",
        "ruby": "いや",
        "written": "す",
        "form": "癒す is いやす. The ruby is いや and す is written after it, so the ruby ends one kana later than the 常用漢字表 hyphen in い-やす. い-える would be いえる. The verse’s English is “Small tools mend wounds”",
    },
    {
        "kanji": "償",
        "raw": "つぐな-う",
        "surface": "償う",
        "reading": "つぐなう",
        "snippet": "When a mistake is made right,",
        "source": "kml/contents/books/book_01/lessons/lesson_54.html",
        "mode": "ruby-stem",
        "stem": "つぐな",
        "follows": "え",
        "form": "償えば is つぐな-う. The verse’s English is “When a mistake is made right”",
    },
)
HELD_BACK = (
    "拒（こばむ） locks in 一度は拒んだが、説得されて翻意しました and in 傷が残っても、容貌で職を拒む理由にはなりません. 翻意 and 容貌 make the wording uncommon, so it stays bare.",
    "弔（とむらう） locks in 沈んだ船の魂を、浜で弔います. The wording is literary, so it stays bare.",
    "併（あわせる） locks in 恵みを併せ持つ. The line is figurative, so it stays bare.",
    "矯（ためる）, 窮（きわまる）, 愁（うれい）, 疎（うとい）, 懇（ねんごろ）, and 憤（いきどおる） lock only in verse. Those lines stay bare.",
    "癒（いやして） and 癒（いやし） cross the same hyphen, but して and し do not spell いやす. Those lines are not examples of that reading.",
)

RADICAL_CARD = {}

# Real classification differences. The card stays on the KANJIDIC2 classical radical.
CHARACTER_RADICAL_NOTES = {
    "斎": "KANJIDIC2の古典部首は文です。joyo_kanji.csv は齊で、齋の部首です。カードは文のままです。",
    "斉": "KANJIDIC2の古典部首は文です。joyo_kanji.csv は齊で、齊の部首です。カードは文のままです。",
    "叙": "KANJIDIC2の古典部首は又です。joyo_kanji.csv は攴で、敍の部首です。カードは又のままです。",
    "覇": "KANJIDIC2の古典部首は襾です。joyo_kanji.csv は雨で、霸の部首です。カードは襾のままです。",
    "竜": "KANJIDIC2の古典部首は立です。joyo_kanji.csv は龍で、龍の部首です。カードは立のままです。",
}

LEVEL_PAGE = "./"
NEXT_LEVEL = "../level-2/"
LESSON_COUNT = 16
LESSON_SIZES = [20] * 8 + [21] * 8
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
        if record["introducedAt"] == "pre2"
    ]
    if len(records) != 328 or len({record["kanji"] for record in records}) != 328:
        raise SystemExit(f"漢検準2級 has {len(records)} characters")
    records.sort(key=lambda record: int(joyo[record["kanji"]]["joyo_index"]))
    if {joyo[record["kanji"]]["grade"] for record in records} != {"S"}:
        raise SystemExit("漢検準2級 is not entirely 常用漢字表 grade S")
    if sum(LESSON_SIZES) != 328 or LESSON_SIZES != [20] * 8 + [21] * 8:
        raise SystemExit("準2級 lessons are not eight of 20 and eight of 21")
    lessons = []
    for number, size in enumerate(LESSON_SIZES, start=1):
        lessons.extend([number] * size)
    return records, joyo, lessons


def lesson_nav(number: int) -> str:
    left = (
        f'<a href="{LEVEL_PAGE}">← 漢検準2級</a>'
        if number == 1
        else f'<a href="lesson-{number - 1:02d}.html">← 第{number - 1}課</a>'
    )
    right = (
        f'<a href="{NEXT_LEVEL}">漢検2級 →</a>'
        if number == LESSON_COUNT
        else f'<a href="lesson-{number + 1:02d}.html">第{number + 1}課 →</a>'
    )
    return f"""<div class="navbar">
  {left}
  <a href="{LEVEL_PAGE}">漢検準2級</a>
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
<p class="school-kicker" lang="ja">漢検準2級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">常用漢字表の中学校以降の漢字のうち328字</p>
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
    text = grade2.page_head(title, f"漢検準2級レベルの漢字。常用漢字表の中学校以降の漢字のうち328字のうち、第{number}課。")
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
  <a href="{LEVEL_PAGE}">漢検準2級</a>
</div>
<p class="school-kicker" lang="ja">漢検準2級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">常用漢字表の中学校以降の漢字のうち328字</p>
<h1 class="school-title">{esc(title)}</h1>
{grade2.furigana_bar()}
<nav class="anchor-list">
{anchors}
</nav>
{chr(10).join(articles)}
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="{LEVEL_PAGE}">漢検準2級</a>
</div>
{notice}
{grade2.furigana_script()}
</body>
</html>
"""
    text = grade2.page_head(title, f"漢検準2級 第{number}課の読み方とことば。常用漢字表の中学校以降の漢字のうち328字。")
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
    if item["mode"] == "ruby-split":
        ruby = f"<ruby>{kanji}<rt>{item['ruby']}</rt></ruby>{item['written']}"
        if ruby not in text or item["snippet"] not in text:
            raise SystemExit(f"Missing ruby-split example for {kanji} {item['raw']}")
        rt = grade2.kata_to_hira(item["ruby"])
        written = grade2.kata_to_hira(item["written"])
        if rt + written != item["reading"]:
            raise SystemExit(f"{kanji} ruby {rt} plus {written} is not {item['reading']}")
        if item["surface"] != kanji + item["written"]:
            raise SystemExit(f"{item['surface']} is not {kanji} plus the written kana {item['written']}")
        special, stem, okuri = grade2.parse_reading(item["raw"])
        whole = "" if special else stem + okuri
        if whole != item["reading"] or not (rt.startswith(stem) and len(stem) < len(rt) < len(whole)):
            raise SystemExit(f"{kanji} ruby {rt} does not cross the hyphen in {item['raw']}")
        if whole[len(rt):] != written:
            raise SystemExit(f"{kanji} written {written} does not finish {item['raw']}")
        locked = []
        for raw in entry["on"] + entry["kun"]:
            other_special, other_stem, other_okuri = grade2.parse_reading(raw)
            if other_special or not other_okuri:
                continue
            other = other_stem + other_okuri
            if (
                rt.startswith(other_stem)
                and len(other_stem) < len(rt) < len(other)
                and other.startswith(rt)
                and other[len(rt):] == written
            ):
                locked.append(raw)
        if locked != [item["raw"]]:
            raise SystemExit(f"{kanji} {rt}+{written} locks {locked}, not {item['raw']}")
        return
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
        "# 漢検準2級 vocabulary review",
        "",
        "Learner pages do not explain these choices. The covers below are approved and are kept.",
        "Some show the lesson character, or other lettering. Nothing here has been deployed.",
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
        "Order is the 常用漢字表 掲載順 of the 328 grade-S characters at 漢検準2級.",
        "There is no 準2級 school-film cut. Lessons are eight of 20 and eight of 21.",
        "The music link is the existing post-elementary collection, shared by 漢検4級 through 漢検2級.",
        "",
        "The overview hero is 竜 `kml/assets/studies/dragon.jpg`. It is in 第16課 and is not that lesson’s cover.",
        "Lesson covers are existing study images, one character from each lesson:",
        "",
    ]
    for number, (slug, kanji) in HERO_CHOICES.items():
        hero = heroes[number]
        note = ""
        lettering = {
            "sunrise": " — 暁 is lettered on the pillar",
            "flood": " — 洪 is lettered on the sign",
            "sugi": " — 杉 is lettered on the sign",
            "headland": " — 海は果てしない物語 is lettered on the post",
            "willow": " — 柳 is lettered on the sign",
            "flower_pot": " — the scene is a flower vase",
        }
        if slug in lettering:
            note = lettering[slug]
        elif hero["width"] != 1672 or hero["height"] != 941:
            note = f" — native 16:9 at {hero['width']}×{hero['height']}"
        lines.append(f"- 第{number}課 {kanji} `kml/assets/studies/{slug}.jpg`{note}")
    lines.extend(
        [
            "",
            "Not used for a cover: 酢 `vinegar.jpg` carries several labels, and 蛇 `snake.jpg` has a long inscription on the stone.",
            "",
            "## Cross-file examples",
            "",
            "Each attached word contains its target character once, and the matcher locks that character’s reading.",
            "A dictionary form is added when a sentence segment or a verse ruby locks that exact reading.",
            "The ruby may end after the 常用漢字表 hyphen. It locks when the ruby plus the kana written after it spell that whole reading and no other reading.",
            "A reading with no suitable lock stays bare.",
            "",
            "## Kept",
            "",
            "- Clearer exact KANJIDIC glosses, with the Heisig line omitted when it restates the card: 逸 deviate; elude, 虞 fear; uneasiness, 懐 feelings; yearn; pocket, 享 enjoy; receive, 薫 fragrant, 洪 flood, 宵 evening, 懸 hang, 酌 serving sake; ladle, 挟 pinch; between, 披 expose; open, 塀 fence; wall, 僕 me; servant, 奔 run; bustle, 猶 furthermore; still, 履 perform; put on (the feet), 騰 rising, 戻 return; revert.",
            "- Reviewed and kept: 逸 “deviate; elude”, 猶 “furthermore; still”, 騰 “rising”.",
            "- Applied: 懐 “feelings; yearn; pocket”, 酌 “serving sake; ladle”, 履 “perform; put on (the feet)”. Heisig stays off the card: “pocket” is already displayed, “bartending” restates the serving sense, and “footgear” restates the footwear sense.",
            "- First gloss kept, Heisig not shown: 翁 venerable old man, 暁 daybreak, 碁 Go, 璽 emperor's seal, 杉 cedar, 坪 two-mat area, 忍 endure, 酪 dairy products, 硫 sulphur, 賓 V.I.P., 瓶 bottle, 扶 aid, 轄 control, 嚇 menacing, 訟 sue, 曹 office, 貞 upright, 頒 distribute, 累 accumulate.",
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
            "The card uses the KANJIDIC2 classical radical, the same default as 10級 through 3級.",
            "Names new at this level: 屮 ふるくさ, 缶 ほとぎ, 聿 ふでづくり. 爪 つめ, 瓦 かわら, and 麻 あさ have no KANJIDIC2 rad_name, so the card uses that character’s reading. 爫 is つめかんむり and is not the card for 爵.",
            "These cards stay on the KANJIDIC2 radical where the joyo column names the radical of the traditional character: 斎 文（齊, from 齋）, 斉 文（齊）, 叙 又（攴, from 敍）, 覇 襾（雨, from 霸）, 竜 立（龍）.",
            "辶, 阝, 攵, 艹, 礻, and 戸 on these cards are the printed forms of 辵, 阜 or 邑, 攴, 艸, 示, and 戶.",
            "着 is not in 準2級. Its 8級 exception, 羊 rather than 目, is not copied onto other characters.",
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
        "level": "pre2",
        "count": 328,
        "order": "五十音順",
        "reference": "常用漢字表 grade S via joyo_kanji.csv, the 328 characters introduced at 漢検準2級",
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
