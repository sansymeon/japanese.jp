#!/usr/bin/env python3
"""Write the ten 漢検6級 lesson pages and their compiled vocabulary pages.

Uses the 漢検6級 card layout. Output lives at kanken/level-6/.
The level entrance is written by kml/scripts/build_kanken_level_pages.py --level6.
Groups are the grade 5 熟語 film cuts, which match 常用漢字表 order:
nine lessons of 20 and one of 13.

English starts from the first KANJIDIC2 gloss. MEANING_CHOICES may name a
clearer gloss from that same entry, or a marked paraphrase. Heisig stays on
its own line only when that keyword is not already the displayed wording.
Radicals stay on the KANJIDIC2 classical radical. 示 prints 示, because that character is the radical. 着 is not in this level.

Bare readings are filled from KML compounds filed under any character when
the reading match is the same mechanical test used on 8級, limited to a
short headword or a verb. One-mora on readings are not filled that way.
VERIFIED_EXAMPLES then adds a dictionary form only when a KML sentence
segment locks that exact 常用漢字表 reading. A reading with no suitable
verified word stays bare and is listed in the review.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GRADE = REPO / "kanken/level-6"
FILM_DIR = REPO / "kml/tools/ambient/collections/grade_5"
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
    122: ("罒", "よんかしら", "古典部首は网（あみがしら）です。罪にある形は罒です。"),
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
}

# One existing 16:9 study image from a character in that lesson.
# The overview hero, 桜, is in lesson 1 and is not also that lesson's cover.
HERO_CHOICES = {
    1: ("performance", "演"),
    2: ("tree_trunk", "幹"),
    3: ("till", "耕"),
    4: ("pick", "採"),
    5: ("bough", "枝"),
    6: ("weave", "織"),
    7: ("fabricate", "築"),
    8: ("public_hall", "堂"),
    9: ("linen", "布"),
    10: ("cotton", "綿"),
}
OVERVIEW_HERO = ("cherry_blossom", "桜")

# Each part is an exact KANJIDIC2 gloss, unless source is paraphrase.
# show_heisig is false when that keyword is already the displayed wording,
# or when it is not a gloss.
MEANING_CHOICES = {
    "仮": {
        "parts": (("temporary", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “temporary”. The first gloss “sham” is a different sense. Heisig “temporary” is this gloss.",
    },
    "額": {
        "parts": (("forehead", "kanjidic"), ("amount", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “forehead” alone hides 金額. Heisig “amount” is the second gloss.",
    },
    "基": {
        "parts": (("foundation", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “foundation”. The first gloss “fundamentals” is another sense in the same entry. Heisig “foundation” is this gloss.",
    },
    "張": {
        "parts": (("stretch", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “stretch”. The first gloss is the counter for bows and stringed instruments. Heisig “lengthen” restates this gloss and is not shown.",
    },
    "似": {
        "parts": (("resemble", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “resemble”. The first gloss “becoming” is a different sense. Heisig “resemble” is this gloss.",
    },
    "準": {
        "parts": (("conform", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “conform”. The first gloss “semi-” is the prefix sense. Heisig “conform” is this gloss.",
    },
    "性": {
        "parts": (("sex", "kanjidic"), ("gender", "kanjidic"), ("nature", "kanjidic")),
        "show_heisig": False,
        "note": "All three are KANJIDIC glosses. “sex” alone hides 性別 and 性質. Heisig “gender” is the second gloss, so the separate line is omitted.",
    },
    "示": {
        "parts": (("show", "kanjidic"), ("indicate", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “indicate” is the second gloss.",
    },
    "質": {
        "parts": (("substance", "kanjidic"), ("quality", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “quality” is the second gloss.",
    },
    "謝": {
        "parts": (("apologize", "kanjidic"), ("thank", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “thank” is the second gloss.",
    },
    "術": {
        "parts": (("art", "kanjidic"), ("technique", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “technique” is the second gloss.",
    },
    "職": {
        "parts": (("post", "kanjidic"), ("employment", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “employment” is the second gloss.",
    },
    "総": {
        "parts": (("general", "kanjidic"), ("total", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “total” is the second gloss.",
    },
    "率": {
        "parts": (("ratio", "kanjidic"), ("rate", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “rate” is the second gloss.",
    },
    "得": {
        "parts": (("gain", "kanjidic"), ("acquire", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “acquire” is the second gloss.",
    },
    "独": {
        "parts": (("single", "kanjidic"), ("alone", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “alone” is the second gloss.",
    },
    "領": {
        "parts": (("jurisdiction", "kanjidic"), ("territory", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “territory” is the second gloss.",
    },
    "務": {
        "parts": (("task", "kanjidic"), ("duties", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “duty” matches “duties” and is not shown.",
    },
    "授": {
        "parts": (("impart", "kanjidic"), ("instruct", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “instruct” is the second gloss.",
    },
    "条": {
        "parts": (("article", "kanjidic"), ("clause", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “clause” is the second gloss.",
    },
    "価": {
        "parts": (("value", "kanjidic"), ("price", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “cost” is not a gloss and is not shown.",
    },
    "構": {
        "parts": (("posture", "kanjidic"), ("build", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “construct” is not a gloss and is not shown.",
    },
    "応": {
        "parts": (("apply", "kanjidic"), ("answer", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “respond” is not a gloss and is not shown.",
    },
    "効": {
        "parts": (("merit", "kanjidic"), ("benefit", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “effect” is not a gloss and is not shown.",
    },
    "経": {
        "parts": (("sutra", "kanjidic"), ("pass through", "paraphrase")),
        "show_heisig": False,
        "note": "“sutra” is a KANJIDIC gloss. “pass through” is the editorial spelling of the KANJIDIC gloss “pass thru”. Heisig “manage” is not a gloss and is not shown.",
    },
    "解": {
        "parts": (("unravel", "kanjidic"), ("explanation", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “solution” is not a gloss and is not shown.",
    },
    "営": {
        "parts": (("conduct (business)", "kanjidic"), ("camp", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “conduct (business)” is placed first for 営業. “camp” remains for 陣営. Heisig “occupation” is not a gloss and is not shown.",
    },
    "桜": {
        "parts": (("cherry blossom", "heisig"),),
        "show_heisig": False,
        "note": "The card wording is Heisig’s keyword “cherry blossom”. KANJIDIC2’s only gloss is “cherry”, which can be read as the fruit. The separate Heisig line is omitted because it would repeat the card.",
    },
    "製": {
        "parts": (("manufacture", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “manufacture”. The first gloss “made in...” leaves the phrase unfinished. Heisig “made in” restates that gloss and is not shown.",
    },
    "破": {
        "parts": (("tear", "kanjidic"), ("break", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “rend” is rare in learner English. Heisig “rend” repeats it and is not shown.",
    },
    "判": {
        "parts": (("judgement", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “judgement”. “judgment” is the same gloss in the other spelling. Heisig “judgment” repeats it and is not shown.",
    },
    "非": {
        "parts": (("un-", "kanjidic"), ("negative", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “non” matches the gloss “non-” and is not shown.",
    },
    "堂": {
        "parts": (("hall", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “hall”. The first gloss “public chamber” is the same sense. Heisig “public hall” restates it and is not shown.",
    },
    "統": {
        "parts": (("unite", "heisig"), ("govern", "paraphrase")),
        "show_heisig": False,
        "note": "“unite” is Heisig’s keyword. “govern” is the editorial verb for the KANJIDIC gloss “governing”. The first gloss “overall” is not shown. デジタル大辞泉 gives 統一 as 「一つにまとめること」 and 統べる as 「全体をまとめて支配する」.",
    },
    "断": {
        "parts": (("cut off", "heisig"), ("decide", "paraphrase"), ("refuse", "kanjidic")),
        "show_heisig": False,
        "note": "“cut off” is Heisig’s keyword, the same sense as the glosses “severance” and “cutting”. “decide” is the editorial verb form of the KANJIDIC gloss “decision”. “refuse” is a KANJIDIC gloss.",
    },
    "設": {
        "parts": (("establish", "heisig"),),
        "show_heisig": False,
        "note": "The card wording is Heisig’s keyword “establish”. KANJIDIC2’s gloss is the noun “establishment”. The separate Heisig line is omitted.",
    },
    "旧": {
        "parts": (("old times", "kanjidic"), ("former", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “old times” alone hides 旧姓 and 旧制. Heisig “olden times” restates the first gloss and is not shown.",
    },
    "可": {
        "parts": (("possible", "heisig"),),
        "show_heisig": False,
        "note": "The card wording is Heisig’s keyword “possible”, printed on the KML lesson. It is not a KANJIDIC2 gloss. Those glosses are “can”, “passable”, and “approval”. The separate Heisig line is omitted.",
    },
}

# The shared radical table prints 礻 for classical 113, the form in 社.
# 示 is that radical itself, so the card prints 示.
RADICAL_CARD = {
    "示": (
        "示",
        "しめす",
        "この字そのものが部首です。社などにある形は礻（しめすへん）で、同じ古典部首です。",
    ),
}

# Real classification differences. The card stays on the KANJIDIC2 classical radical.
CHARACTER_RADICAL_NOTES = {
    "弁": "KANJIDIC2の古典部首は廾です。joyo_kanji.csv は辛で、辨・辯・瓣の部首です。カードは廾のままです。",
    "旧": "KANJIDIC2の古典部首は日です。joyo_kanji.csv は臼で、舊の部首です。カードは日のままです。",
    "舎": "KANJIDIC2の古典部首は人です。joyo_kanji.csv は舌で、舍の部首です。カードは人のままです。",
    "余": "KANJIDIC2の古典部首は人です。joyo_kanji.csv は食で、餘の部首です。カードは人のままです。",
    "営": "KANJIDIC2の古典部首は口です。joyo_kanji.csv は火で、營の部首です。カードは口のままです。",
}
SKIP_EXAMPLES = set()

# Reviewed, and the card wording was left as the dictionary gloss.
MEANING_REVIEW = {}

# Dictionary form shown to the learner. The snippet is an existing KML sentence.
# stem mode: the segment is the character alone, read as `stem`, and the next
# segment starts with `follows`, which has to be an inflection of this reading only.
# word mode: a segment's surface and reading assign to this 常用漢字表 reading.
# ruby mode: the HTML contains ruby for this character and reading.
VERIFIED_EXAMPLES = (
    {
        "kanji": "混",
        "raw": "こ-む",
        "surface": "混む",
        "reading": "こむ",
        "snippet": "年末は店が大変混みます",
        "source": "kml/data/compounds/lesson_12.json",
        "mode": "stem",
        "stem": "こ",
        "follows": "みます",
        "form": "混みます is こ-む",
    },
    {
        "kanji": "混",
        "raw": "ま-ぜる",
        "surface": "混ぜる",
        "reading": "まぜる",
        "snippet": "最近は玄米を混ぜて炊きます",
        "source": "kml/data/compounds/lesson_75.json",
        "mode": "stem",
        "stem": "ま",
        "follows": "ぜて",
        "form": "混ぜて is ま-ぜる. ま-じる would be 混じって",
    },
    {
        "kanji": "務",
        "raw": "つと-める",
        "surface": "務める",
        "reading": "つとめる",
        "snippet": "式の司会は、校長が務めます",
        "source": "kml/data/compounds/lesson_101.json",
        "mode": "stem",
        "stem": "つと",
        "follows": "めます",
        "form": "務めます is つと-める. つと-まる would be 務まります",
    },
    {
        "kanji": "現",
        "raw": "あらわ-れる",
        "surface": "現れる",
        "reading": "あらわれる",
        "snippet": "朝の船は、霧の中から現れました",
        "source": "kml/data/compounds/lesson_101.json",
        "mode": "stem",
        "stem": "あらわ",
        "follows": "れました",
        "form": "現れました is あらわ-れる. あらわ-す would be 現しました",
    },
    {
        "kanji": "減",
        "raw": "へ-る",
        "surface": "減る",
        "reading": "へる",
        "snippet": "冬季のバスは本数が減ります",
        "source": "kml/data/compounds/lesson_23.json",
        "mode": "stem",
        "stem": "へ",
        "follows": "ります",
        "form": "減ります is へ-る. へ-らす would be 減らします",
    },
    {
        "kanji": "減",
        "raw": "へ-らす",
        "surface": "減らす",
        "reading": "へらす",
        "snippet": "農薬を減らした野菜が、店に並んでいます",
        "source": "kml/data/compounds/lesson_94.json",
        "mode": "stem",
        "stem": "へ",
        "follows": "らした",
        "form": "減らした is へ-らす. へ-る would be 減った",
    },
    {
        "kanji": "増",
        "raw": "ふ-やす",
        "surface": "増やす",
        "reading": "ふやす",
        "snippet": "無闇に薬を増やしてはいけません",
        "source": "kml/data/compounds/lesson_88.json",
        "mode": "stem",
        "stem": "ふ",
        "follows": "やしてはいけません",
        "form": "増やしては is ふ-やす. ます would be 増します",
    },
    {
        "kanji": "支",
        "raw": "ささ-える",
        "surface": "支える",
        "reading": "ささえる",
        "snippet": "過疎地の医療を、支える人が減っています",
        "source": "kml/data/compounds/lesson_93.json",
        "mode": "stem",
        "stem": "ささ",
        "follows": "える",
        "form": "支える is ささ-える",
    },
    {
        "kanji": "解",
        "raw": "と-ける",
        "surface": "解ける",
        "reading": "とける",
        "snippet": "この種の問題は、話し合いで解けます",
        "source": "kml/data/compounds/lesson_91.json",
        "mode": "stem",
        "stem": "と",
        "follows": "けます",
        "form": "解けます is と-ける. と-く would be 解きます",
    },
    {
        "kanji": "解",
        "raw": "と-く",
        "surface": "解く",
        "reading": "とく",
        "snippet": "祖父は夜、詰将棋を解きます",
        "source": "kml/data/compounds/lesson_19.json",
        "mode": "stem",
        "stem": "と",
        "follows": "きます",
        "form": "解きます is と-く. と-ける would be 解けます",
    },
    {
        "kanji": "確",
        "raw": "たし-かめる",
        "surface": "確かめる",
        "reading": "たしかめる",
        "snippet": "地図で朝鮮半島の位置を確かめました",
        "source": "kml/data/compounds/lesson_30.json",
        "mode": "stem",
        "stem": "たし",
        "follows": "かめました",
        "form": "確かめました is たし-かめる",
    },
    {
        "kanji": "保",
        "raw": "たも-つ",
        "surface": "保つ",
        "reading": "たもつ",
        "snippet": "厨房は、常に清潔に保ちます",
        "source": "kml/data/compounds/lesson_83.json",
        "mode": "stem",
        "stem": "たも",
        "follows": "ちます",
        "form": "保ちます is たも-つ",
    },
    {
        "kanji": "採",
        "raw": "と-る",
        "surface": "採る",
        "reading": "とる",
        "snippet": "朝採りの野菜は新鮮で甘いです",
        "source": "kml/data/compounds/lesson_30.json",
        "mode": "stem",
        "stem": "と",
        "follows": "りの",
        "form": "朝採り is と-る",
    },
    {
        "kanji": "燃",
        "raw": "も-やす",
        "surface": "燃やす",
        "reading": "もやす",
        "snippet": "昔はこの町でも石炭を燃やして暖を取っていたと聞いた",
        "source": "kml/data/compounds/lesson_42.json",
        "mode": "stem",
        "stem": "も",
        "follows": "やして",
        "form": "燃やして is も-やす. も-す would be 燃して",
    },
    {
        "kanji": "造",
        "raw": "つく-る",
        "surface": "造る",
        "reading": "つくる",
        "snippet": "老朽した橋は、来年造ります",
        "source": "kml/data/compounds/lesson_67.json",
        "mode": "stem",
        "stem": "つく",
        "follows": "ります",
        "form": "造ります is つく-る",
    },
    {
        "kanji": "絶",
        "raw": "た-える",
        "surface": "絶える",
        "reading": "たえる",
        "snippet": "熱帯の夜は、虫の声が絶えません",
        "source": "kml/data/compounds/lesson_82.json",
        "mode": "stem",
        "stem": "た",
        "follows": "えません",
        "form": "絶えません is た-える. た-やす would be 絶やしません. た-つ would be 絶ちません",
    },
    {
        "kanji": "肥",
        "raw": "こ-える",
        "surface": "肥える",
        "reading": "こえる",
        "snippet": "谷の耕地は、狭いですが肥えています",
        "source": "kml/data/compounds/lesson_98.json",
        "mode": "stem",
        "stem": "こ",
        "follows": "えています",
        "form": "肥えています is こ-える. こ-やす would be 肥やしています",
    },
    {
        "kanji": "常",
        "raw": "つね",
        "surface": "常",
        "reading": "つね",
        "snippet": "厨房は、常に清潔に保ちます",
        "source": "kml/data/compounds/lesson_83.json",
        "mode": "stem",
        "stem": "つね",
        "follows": "に",
        "form": "常に is つね. とこ is a different reading and does not lock here",
    },
    {
        "kanji": "河",
        "raw": "かわ",
        "surface": "河",
        "reading": "かわ",
        "snippet": "A broad river",
        "source": "kml/contents/books/book_01/lessons/lesson_08.html",
        "mode": "ruby",
        "form": "The verse reads 河 as かわ in 広い河は, and its English is “A broad river”. 銀河 in the same lesson is が, not かわ",
    },
    {
        "kanji": "経",
        "raw": "キョウ",
        "surface": "経",
        "reading": "きょう",
        "snippet": "寺で人がお経を唱えます",
        "source": "kml/data/compounds/lesson_02.json",
        "mode": "word",
        "form": "経（きょう） is キョウ, the sutra reading. ケイ would be けい. へ-る would be 経る",
    },
    {
        "kanji": "素",
        "raw": "ス",
        "surface": "素肌",
        "reading": "すはだ",
        "snippet": "冷たい風が素肌に当たりました",
        "source": "kml/data/compounds/lesson_04.json",
        "mode": "word",
        "form": "素肌 begins with ス. The sentence is a cold wind on bare skin",
    },
    {
        "kanji": "粉",
        "raw": "こ",
        "surface": "葛粉",
        "reading": "くずこ",
        "snippet": "母は和菓子に葛粉を使いました",
        "source": "kml/data/compounds/lesson_25.json",
        "mode": "word",
        "form": "葛粉 ends with こ. こな is a different reading",
    },
    {
        "kanji": "似",
        "raw": "ジ",
        "surface": "擬似",
        "reading": "ぎじ",
        "snippet": "擬似の星空が、天井に映されています",
        "source": "kml/data/compounds/lesson_76.json",
        "mode": "word",
        "form": "擬似 ends with ジ",
    },
    {
        "kanji": "武",
        "raw": "ム",
        "surface": "武者",
        "reading": "むしゃ",
        "snippet": "祭りの武者は、木の盾を持っています",
        "source": "kml/data/compounds/lesson_100.json",
        "mode": "word",
        "form": "武者 begins with ム. ブ would be ぶ",
    },
    {
        "kanji": "境",
        "raw": "さかい",
        "surface": "境",
        "reading": "さかい",
        "snippet": "sea and sky become one",
        "source": "kml/contents/books/book_01/lessons/lesson_09.html",
        "mode": "ruby",
        "form": "The verse reads 境 as さかい in 空と海との境が消える",
    },
    {
        "kanji": "価",
        "raw": "あたい",
        "surface": "価",
        "reading": "あたい",
        "snippet": "True worth",
        "source": "kml/contents/books/book_01/lessons/lesson_87.html",
        "mode": "ruby",
        "form": "The verse reads 価 as あたい in 本当の価は, and its English is “True worth”",
    },
    {
        "kanji": "志",
        "raw": "こころざし",
        "surface": "志",
        "reading": "こころざし",
        "snippet": "Resolve first appears in the eyes",
        "source": "kml/contents/books/book_01/lessons/lesson_21.html",
        "mode": "ruby",
        "form": "The verse reads 志 as こころざし, and its English is “Resolve”",
    },
    {
        "kanji": "仮",
        "raw": "かり",
        "surface": "仮",
        "reading": "かり",
        "snippet": "Crossing a temporary bridge",
        "source": "kml/contents/books/book_01/lessons/lesson_52.html",
        "mode": "ruby",
        "form": "The verse reads 仮 as かり in 仮の橋を渡り, and its English is “a temporary bridge”",
    },
    {
        "kanji": "逆",
        "raw": "さか",
        "surface": "逆",
        "reading": "さか",
        "snippet": "Resisting the strong river current",
        "source": "kml/contents/books/book_01/lessons/lesson_106.html",
        "mode": "ruby",
        "form": "The verse reads 逆 as さか in 流れに逆らい. The English is “Resisting the strong river current”",
    },
)

HELD_BACK = (
    "混 まじる: 茉莉の匂いが、南からの船荷に混じっていました. The jasmine wording is not a learner example.",
    "移 うつす: 冗員を別の仕事へ移しました and 牝の馬を別の厩に移した. Neither is a learner sentence.",
    "導 みちびく: 御者は鞭を上げず声で導いた. Not a learner sentence.",
    "示 シ: sentences that read 示 as しめ were not used. しめ begins with し, so it is not an example of シ.",
    "眼 まなこ: lesson_79.html reads 澄んだ眼 as まなこ. That word is literary, so the reading stays bare.",
)

LEVEL_PAGE = "./"
NEXT_LEVEL = "../level-5/"
LESSON_COUNT = 10
SAFE_HOW = {"okurigana", "whole word", "start", "end"}


def film_cuts() -> list[list[str]]:
    cuts = []
    for number in range(1, LESSON_COUNT + 1):
        path = FILM_DIR / f"grade_5_compounds_school_{number:02d}.json"
        seen: list[str] = []
        for scene in json.loads(path.read_text(encoding="utf-8"))["scenes"]:
            kanji = scene.get("kanji")
            if kanji and len(kanji) == 1 and kanji not in seen:
                seen.append(kanji)
        cuts.append(seen)
    if len(cuts) != LESSON_COUNT or sum(len(cut) for cut in cuts) != 193:
        raise SystemExit("Grade 5 film cuts are not 193 characters in ten lessons")
    return cuts


def load_level() -> tuple[list[dict], dict, list[int]]:
    import csv

    joyo = {}
    with JOYO.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            joyo[row["kanji"]] = row
    records = [
        record
        for record in json.loads(INDEX.read_text(encoding="utf-8"))["characters"]
        if record["introducedAt"] == "6"
    ]
    if len(records) != 193:
        raise SystemExit(f"漢検6級 has {len(records)} characters")
    records.sort(key=lambda record: int(joyo[record["kanji"]]["joyo_index"]))
    cuts = film_cuts()
    if [record["kanji"] for record in records] != [kanji for cut in cuts for kanji in cut]:
        raise SystemExit("6級 order differs from the grade 5 熟語 film cuts")
    lessons = []
    for number, cut in enumerate(cuts, start=1):
        lessons.extend([number] * len(cut))
    return records, joyo, lessons


def lesson_nav(number: int) -> str:
    left = (
        f'<a href="{LEVEL_PAGE}">← 漢検6級</a>'
        if number == 1
        else f'<a href="lesson-{number - 1:02d}.html">← 第{number - 1}課</a>'
    )
    right = (
        f'<a href="{NEXT_LEVEL}">漢検5級 →</a>'
        if number == LESSON_COUNT
        else f'<a href="lesson-{number + 1:02d}.html">第{number + 1}課 →</a>'
    )
    return f"""<div class="navbar">
  {left}
  <a href="{LEVEL_PAGE}">漢検6級</a>
  {right}
</div>"""


def review_block() -> str:
    return """
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLKeIGzGuv0ZU" target="_blank" rel="noopener noreferrer">漢検6級の漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLBy3SmUyWUa0" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 10 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLLPec_9jQnEc" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 8 films</span></a>
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
<p class="school-kicker" lang="ja">漢検6級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学5年生で習う193字</p>
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
    text = grade2.page_head(title, f"漢検6級レベルの漢字。小学5年生で習う193字のうち、第{number}課。")
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
  <a href="{LEVEL_PAGE}">漢検6級</a>
</div>
<p class="school-kicker" lang="ja">漢検6級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学5年生で習う193字</p>
<h1 class="school-title">{esc(title)}</h1>
{grade2.furigana_bar()}
<nav class="anchor-list">
{anchors}
</nav>
{chr(10).join(articles)}
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="{LEVEL_PAGE}">漢検6級</a>
</div>
{notice}
{grade2.furigana_script()}
</body>
</html>
"""
    text = grade2.page_head(title, f"漢検6級 第{number}課の読み方とことば。小学5年生で習う193字。")
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
        notes.append(
            f"Added {item['surface']}（{item['reading']}） for {label} from {item['source']} ({item['form']}). Snippet: {item['snippet']}。"
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
        "# 漢検6級 vocabulary review",
        "",
        "Learner pages do not explain these choices. The lesson covers are approved, including 第4課 採.",
        "Meanings and examples below record the review. Nothing here has been deployed.",
        "",
        f"KANJIDIC2 {meta['database']}, {meta['date']}.",
        "English on a card is the first KANJIDIC2 gloss, unless MEANING_CHOICES names a clearer gloss from that same list or a marked paraphrase.",
        "A displayed meaning tagged kanjidic is that exact gloss. A paraphrase is editorial. A meaning tagged heisig is that keyword used as the card wording.",
        "Heisig stays on its own line only when the keyword is not already the displayed wording.",
        "Readings are the 常用漢字表 音訓. Parentheses are the table’s indented readings.",
        "Example words come from `kml/data/compounds/`. A word filed under another character is used only when",
        "the same matcher used on 8級 locks it to that reading, and the word is a verb or a headword of at most three kanji.",
        "One-mora on readings are not filled that way. A dictionary form is added only when a sentence segment",
        "locks that exact reading. A reading with no suitable word stays bare.",
        f"Bare readings remaining: {bare}.",
        "",
        "The overview hero is 桜 `kml/assets/studies/cherry_blossom.jpg`.",
        "Lesson covers are existing study images, one character from each lesson:",
        "",
    ]
    for number, (slug, kanji) in HERO_CHOICES.items():
        hero = heroes[number]
        note = ""
        if slug == "deer":
            note = " — 鹿 is lettered on the wooden sign"
        elif hero["width"] != 1672 or hero["height"] != 941:
            note = f" — native 16:9 at {hero['width']}×{hero['height']}"
        lines.append(f"- 第{number}課 {kanji} `kml/assets/studies/{slug}.jpg`{note}")
    lines.extend(
        [
            "",
            "河 `large_river.jpg` is a night sky over fields, so it is not the overview. 粉 `flour.jpg` is a snowy street, so it is not a cover.",
            "第4課 uses 採 `pick.jpg`. The crystal close-up `mineral.jpg` is not the cover.",
            "",
            "## Cross-file examples",
            "",
            "Each attached word contains its target character once, and the matcher locks that character’s reading.",
            "雑 ゾウ uses 雑巾（ぞうきん） from lesson_22.json, 床を雑巾で拭きました. The word contains 雑. It is not an example for 造. 造 uses 建造, 改造, 製造, and 造る.",
            "性 ショウ uses 相性（あいしょう） from lesson_12.json, この二人は相性がいいです. しょう is 性.",
            "率 ソツ uses 軽率（けいそつ） from lesson_39.json, 彼女の態度は軽率です. そつ is 率.",
            "",
            "## For judgment",
            "",
            "- 桜 shows “cherry blossom”, Heisig’s keyword. KANJIDIC2’s only gloss is “cherry”. The separate Heisig line is omitted.",
            "- 経 shows “sutra; pass through”. “pass through” spells out the gloss “pass thru”.",
            "- 性 shows “sex; gender; nature”. All three are KANJIDIC glosses, so “gender” is not left on a Heisig-only line.",
            "- 製 shows “manufacture”. The first gloss “made in...” is not shown.",
            "- 破 shows “tear; break”. The first gloss “rend” is not shown.",
            "- 堂 shows “hall”, the KANJIDIC gloss. “public chamber” is the same sense. Heisig “public hall” is not shown.",
            "- 統 shows “unite; govern”. “unite” is Heisig’s keyword. “govern” is the editorial verb for “governing”.",
            "- 断 shows “cut off; decide; refuse”. “decide” is the editorial verb form of the gloss “decision”.",
            "- 設 shows “establish”, Heisig’s keyword. The KANJIDIC gloss is the noun “establishment”.",
            "- 旧 shows “old times; former”. Both are KANJIDIC glosses.",
            "- 営 shows “conduct (business); camp”. Both are KANJIDIC glosses, with 営業 first.",
            "- 可 shows “possible”, Heisig’s keyword on the KML lesson. It is not a KANJIDIC gloss. The glosses are “can”, “passable”, and “approval”.",
            "- 非 still shows “un-; negative”. “un-” is the KANJIDIC prefix gloss.",
            "- 因 still shows “cause”. Heisig “reason” is not a gloss.",
            "- 河 still shows “river”. Heisig “large river” is not a gloss.",
            "- 制 still shows “system”. Heisig “control” is not a gloss. Later glosses are “law” and “rule”.",
            "- 応 still shows “apply; answer”. Heisig “respond” is not a gloss.",
            "- 示 prints 示（しめす）. The shared radical table’s 礻 is the form in 社, and it is the same classical radical.",
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
            "The card uses the KANJIDIC2 classical radical, the same default as 10級 through 7級.",
            "Japanese names for radicals new at this level come from KANJIDIC2 `rad_name` where that element exists: 廾 にじゅうあし, 支 しんよう（じゅうまたとも）, 殳 ほこつくり（るまたとも）, 耒 らいすき, 豕 いのこ.",
            "比 くらべる, 片 かた, 玄 げん, and 臼 うす have no `rad_name`. The card uses the character’s ordinary reading.",
            "非 あらず has no `rad_name`. あらず is the school name of radical 175.",
            "罪 shows 罒（よんかしら）, the form inside the character. The classical head is 网.",
            "示 prints 示（しめす） because the character is the radical. 社 uses 礻, the same classical radical.",
            "These cards stay on the KANJIDIC2 radical where the joyo column names the radical of the traditional character: 弁 廾（辛, from 辨・辯・瓣）, 旧 日（臼, from 舊）, 舎 人（舌, from 舍）, 余 人（食, from 餘）, 営 口（火, from 營）.",
            "象 stays 豕（いのこ）. That is the KANJIDIC2 classification, and the joyo column agrees.",
            "着 is not in 6級. Its 8級 exception, 羊 rather than 目, is not copied onto other characters.",
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
        "grade": 5,
        "level": "6",
        "count": 193,
        "order": "五十音順",
        "reference": "学年別漢字配当表 via joyo_kanji.csv, checked against the grade 5 熟語 film cuts",
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
