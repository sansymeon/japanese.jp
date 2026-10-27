#!/usr/bin/env python3
"""Write the sixteen 漢検4級 lesson pages and their compiled vocabulary pages.

Uses the 漢検4級 card layout. Output lives at kanken/level-4/.
The level entrance is written by kml/scripts/build_kanken_level_pages.py --level4.
The 313 characters are the 常用漢字表 grade-S rows whose 漢検 level is 4,
in 掲載順. There is no separate school-film cut for this level. The
post-elementary films are one collection shared by 漢検4級 through 漢検2級.
Lessons are fifteen groups of 20 and a last group of 13, in that order.

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
GRADE = REPO / "kanken/level-4"
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
}

# One existing 16:9 study image from a character in that lesson.
# The overview hero, 芋, is in lesson 1 and is not also that lesson's cover.
HERO_CHOICES = {
    1: ("fiber", "維"),
    2: ("reap", "刈"),
    3: ("pray", "祈"),
    4: ("dig", "掘"),
    5: ("sabre", "剣"),
    6: ("blossom", "咲"),
    7: ("boat", "舟"),
    8: ("tatami_mat", "畳"),
    9: ("fan", "扇"),
    10: ("hop", "跳"),
    11: ("mountain_pass", "峠"),
    12: ("hair", "髪"),
    13: ("seacoast", "浜"),
    14: ("summit", "峰"),
    15: ("wing", "翼"),
    16: ("dew", "露"),
}
OVERVIEW_HERO = ("potato", "芋")

# Each part is an exact KANJIDIC2 gloss, unless source is paraphrase.
# show_heisig is false when that keyword is already the displayed wording,
# or when it is not a gloss.
MEANING_CHOICES = {
    "奥": {
        "parts": (("interior", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “interior”. The first gloss “heart” is the sense of 奥義. Heisig “inner” restates “interior” and is not shown.",
    },
    "脚": {
        "parts": (("leg", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “leg”. The first gloss “skids” is an aircraft sense. Heisig “shins” is a narrower part of “leg” and is not a gloss.",
    },
    "旬": {
        "parts": (("ten-day period", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “ten-day period”. The first gloss “decameron” is the same sense in rare wording. Heisig “ten days” restates this gloss and is not shown.",
    },
    "薪": {
        "parts": (("firewood", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “firewood”. The first gloss “fuel” is broader. Heisig “firewood” is this gloss.",
    },
    "趣": {
        "parts": (("gist", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “gist”. The first gloss “purport” is the same sense in rarer wording. Heisig “gist” is this gloss.",
    },
    "更": {
        "parts": (("further", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “further”. The first gloss “grow late” is the night-watch sense. Heisig “further” is this gloss.",
    },
    "耐": {
        "parts": (("enduring", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “enduring”. The first gloss “-proof” is the suffix sense. Heisig “endure” restates “enduring” and is not shown.",
    },
    "淡": {
        "parts": (("faint", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “faint”. The first gloss “thin” hides 淡い. Heisig “faint” is this gloss.",
    },
    "致": {
        "parts": (("do", "kanjidic"), ("cause", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “doth” is archaic. Heisig “bring about” restates “cause” and is not a gloss.",
    },
    "峠": {
        "parts": (("mountain pass", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “mountain pass”. The first gloss “mountain peak” is a different sense. Heisig “mountain pass” is this gloss.",
    },
    "幅": {
        "parts": (("width", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “width”. The first gloss “hanging scroll” hides 幅 as a measurement. Heisig “breadth” restates “width” and is not shown.",
    },
    "雌": {
        "parts": (("female", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “female”. The first gloss “feminine” is the same sense. Heisig “female” is this gloss.",
    },
    "雄": {
        "parts": (("male", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “male”. The first gloss “masculine” is the same sense. Heisig “male” is this gloss.",
    },
    "殿": {
        "parts": (("Mr.", "kanjidic"), ("hall", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “Mr.” alone hides 殿 as a building. Heisig “mister” restates “Mr.” and is not shown.",
    },
    "弐": {
        "parts": (("formal two", "heisig"),),
        "show_heisig": False,
        "note": "Heisig keyword “formal two”, used as the card so the formal numeral is explicit. KANJIDIC glosses are “II”, “two”, and “second”. Paired with 壱.",
    },
    "壱": {
        "parts": (("formal one", "heisig"),),
        "show_heisig": False,
        "note": "Heisig keyword “formal one”, used as the card so the formal numeral is explicit. The KANJIDIC gloss is “one (in documents)”. Paired with 弐.",
    },
    "仰": {
        "parts": (("face-up", "kanjidic"), ("look up", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “look up” is the second gloss.",
    },
    "違": {
        "parts": (("difference", "kanjidic"), ("differ", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “differ” is the second gloss.",
    },
    "含": {
        "parts": (("contain", "kanjidic"), ("include", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “include” is the second gloss.",
    },
    "載": {
        "parts": (("ride", "kanjidic"), ("record", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “load” is not a gloss. The numeric gloss “10**44” is not shown.",
    },
    "訴": {
        "parts": (("accusation", "kanjidic"), ("sue", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “sue” is the second gloss. “complain of pain” is a separate gloss and is not on the card.",
    },
    "丹": {
        "parts": (("red", "kanjidic"), ("cinnabar", "heisig")),
        "show_heisig": False,
        "note": "“red” is a KANJIDIC gloss. “cinnabar” is the Heisig keyword and is not a gloss. The first gloss “rust-colored” is the same color sense as “red”. “red lead” is a gloss and is not on the card. No separate Heisig line.",
    },
    "唐": {
        "parts": (("Tang dynasty", "paraphrase"), ("China", "kanjidic")),
        "show_heisig": False,
        "note": "“Tang dynasty” is the editorial capitalization of the Heisig keyword “tang dynasty”. That keyword names the dynasty whose KANJIDIC gloss is “T'ang”. “China” is a KANJIDIC gloss. No separate Heisig line.",
    },
    "爆": {
        "parts": (("explode", "heisig"), ("burst", "paraphrase")),
        "show_heisig": False,
        "note": "“explode” is the Heisig keyword. “burst” is an editorial shortening of the KANJIDIC gloss “burst open”. The gloss “bomb” is not on the card. No separate Heisig line.",
    },
    "髪": {
        "parts": (("hair", "heisig"),),
        "show_heisig": False,
        "note": "Heisig keyword “hair”, the shorter form of the only KANJIDIC gloss “hair of the head”.",
    },
    "凡": {
        "parts": (("commonplace", "kanjidic"), ("mediocre", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “mediocre” is the second gloss on the card.",
    },
    "謡": {
        "parts": (("song", "kanjidic"), ("noh chanting", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “song” alone hides the Noh sense. Heisig “noh chanting” is the second gloss. The verb gloss “sing” is not on the card.",
    },
}

# First gloss kept. Heisig is the same sense and is not an exact gloss, so it is not shown.
MEANING_REVIEW = {
    "菓": "KANJIDIC gloss “candy”. Heisig “confectionery” is not a gloss and is not shown.",
    "箇": "KANJIDIC gloss “counter for articles”. Heisig “counters for things” is the same sense and is not an exact gloss.",
    "皆": "KANJIDIC gloss “all”. Heisig “everyone” is not a gloss and is not shown.",
    "儀": "KANJIDIC gloss “ceremony”. Heisig “ritual” is the same sense and is not an exact gloss.",
    "圏": "KANJIDIC gloss “sphere”. Heisig “sphere of influence” is the longer form of this gloss and is not shown.",
    "釈": "KANJIDIC gloss “explanation”. Heisig “interpretation” is not a gloss and is not shown.",
    "拓": "KANJIDIC gloss “clear (the land)”. Heisig “clear land” is the shorter form of this gloss and is not shown.",
    "桃": "KANJIDIC gloss “peach”. Heisig “peach tree” is the longer form of this gloss and is not shown.",
    "杯": "KANJIDIC gloss “counter for cupfuls”. Heisig “cupfuls” is the shorter form of this gloss and is not shown.",
    "泊": "KANJIDIC gloss “overnight stay”. Heisig “overnight” is the shorter form of this gloss and is not shown.",
}

RADICAL_CARD = {}

# Real classification differences. The card stays on the KANJIDIC2 classical radical.
CHARACTER_RADICAL_NOTES = {
    "為": "KANJIDIC2の古典部首は火です。joyo_kanji.csv は爪で、爲の部首です。カードは火のままです。",
    "尽": "KANJIDIC2の古典部首は尸です。joyo_kanji.csv は皿で、盡の部首です。カードは尸のままです。",
    "闘": "KANJIDIC2の古典部首は門です。joyo_kanji.csv は鬥で、鬪の部首です。カードは門のままです。",
    "弐": "KANJIDIC2の古典部首は弋です。joyo_kanji.csv は貝で、貳の部首です。カードは弋のままです。",
    "舗": "KANJIDIC2の古典部首は人です。joyo_kanji.csv は舌で、舖の部首です。カードは人のままです。",
    "与": "KANJIDIC2の古典部首は一です。joyo_kanji.csv は臼で、與の部首です。カードは一のままです。",
    "頼": "KANJIDIC2の古典部首は頁です。joyo_kanji.csv は貝で、賴の部首です。カードは頁のままです。",
}
SKIP_EXAMPLES = set()
# Dictionary form shown to the learner. The snippet is an existing KML sentence or verse.
# stem mode: the segment is the character alone, read as `stem`, and the next
# segment starts with `follows`, which has to be an inflection of this reading only.
# ruby mode: the HTML contains ruby for this character and this full reading.
VERIFIED_EXAMPLES = (
    {
        "kanji": "壊",
        "raw": "こわ-す",
        "surface": "壊す",
        "reading": "こわす",
        "snippet": "冷たい物を飲みすぎて胃腸を壊しました。",
        "source": "kml/data/compounds/lesson_30.json",
        "mode": "stem",
        "stem": "こわ",
        "follows": "しました。",
        "form": "壊しました is こわ-す. こわ-れる would be 壊れました",
    },
    {
        "kanji": "乾",
        "raw": "かわ-かす",
        "surface": "乾かす",
        "reading": "かわかす",
        "snippet": "濡れた靴下を、囲炉裏の傍で乾かします。",
        "source": "kml/data/compounds/lesson_103.json",
        "mode": "stem",
        "stem": "かわ",
        "follows": "かします。",
        "form": "乾かします is かわ-かす. かわ-く would be 乾きます",
    },
    {
        "kanji": "刺",
        "raw": "さ-さる",
        "surface": "刺さる",
        "reading": "ささる",
        "snippet": "蜂に刺されて、手が腫れました。",
        "source": "kml/data/compounds/lesson_91.json",
        "mode": "stem",
        "stem": "さ",
        "follows": "されて、",
        "form": "刺されて is さ-さる. さ-す would be 刺して",
    },
    {
        "kanji": "浮",
        "raw": "う-かべる",
        "surface": "浮かべる",
        "reading": "うかべる",
        "snippet": "風呂に柚子を浮かべた。",
        "source": "kml/data/compounds/lesson_128.json",
        "mode": "stem",
        "stem": "う",
        "follows": "かべた。",
        "form": "浮かべた is う-かべる. う-く would be 浮いた",
    },
    {
        "kanji": "浮",
        "raw": "う-く",
        "surface": "浮く",
        "reading": "うく",
        "snippet": "刃に薄い錆が浮いている。",
        "source": "kml/data/compounds/lesson_140.json",
        "mode": "stem",
        "stem": "う",
        "follows": "いている。",
        "form": "浮いている is う-く. う-かべる would be 浮かべている",
    },
    {
        "kanji": "脱",
        "raw": "ぬ-ぐ",
        "surface": "脱ぐ",
        "reading": "ぬぐ",
        "snippet": "靴は玄関で脱いでください。",
        "source": "kml/data/compounds/lesson_75.json",
        "mode": "stem",
        "stem": "ぬ",
        "follows": "いでください。",
        "form": "脱いでください is ぬ-ぐ. ぬ-げる would be 脱げて",
    },
    {
        "kanji": "狂",
        "raw": "くる-う",
        "surface": "狂う",
        "reading": "くるう",
        "snippet": "磁気の強い場所では、時計が狂います。",
        "source": "kml/data/compounds/lesson_75.json",
        "mode": "stem",
        "stem": "くる",
        "follows": "います。",
        "form": "狂います is くる-う. くる-おしい is the adjective",
    },
    {
        "kanji": "贈",
        "raw": "おく-る",
        "surface": "贈る",
        "reading": "おくる",
        "snippet": "敬老の日に、祖母へ花を贈りました。",
        "source": "kml/data/compounds/lesson_68.json",
        "mode": "stem",
        "stem": "おく",
        "follows": "りました。",
        "form": "贈りました is おく-る",
    },
    {
        "kanji": "載",
        "raw": "の-る",
        "surface": "載る",
        "reading": "のる",
        "snippet": "庭の松に雪が載っています。",
        "source": "kml/data/compounds/lesson_43.json",
        "mode": "stem",
        "stem": "の",
        "follows": "っています。",
        "form": "載っています is の-る. の-せる would be 載せています",
    },
    {
        "kanji": "逃",
        "raw": "に-げる",
        "surface": "逃げる",
        "reading": "にげる",
        "snippet": "村は高い所へ津波から逃げます。",
        "source": "kml/data/compounds/lesson_18.json",
        "mode": "stem",
        "stem": "に",
        "follows": "げます。",
        "form": "逃げます is に-げる. に-がす would be 逃がします",
    },
    {
        "kanji": "抜",
        "raw": "ぬ-ける",
        "surface": "抜ける",
        "reading": "ぬける",
        "snippet": "杉林を抜けると、風が変わります。",
        "source": "kml/data/compounds/lesson_93.json",
        "mode": "stem",
        "stem": "ぬ",
        "follows": "けると、",
        "form": "抜ける is ぬ-ける. ぬ-く would be 抜く",
    },
    {
        "kanji": "抱",
        "raw": "いだ-く",
        "surface": "抱く",
        "reading": "いだく",
        "snippet": "母は赤ん坊を優しく抱きます。",
        "source": "kml/data/compounds/lesson_35.json",
        "mode": "stem",
        "stem": "いだ",
        "follows": "きます。",
        "form": "抱きます is いだ-く. だ-く and かか-える are different readings",
    },
    {
        "kanji": "薪",
        "raw": "たきぎ",
        "surface": "薪",
        "reading": "たきぎ",
        "snippet": "樫の薪は火持ちが良い。",
        "source": "kml/data/compounds/lesson_128.json",
        "mode": "stem",
        "stem": "たきぎ",
        "follows": "は",
        "form": "薪 is read たきぎ. Verses that read 薪 as まき are a different reading and are not used",
    },
    {
        "kanji": "匹",
        "raw": "ひき",
        "surface": "匹",
        "reading": "ひき",
        "snippet": "今日の釣果は大きな魚二匹です。",
        "source": "kml/data/compounds/lesson_15.json",
        "mode": "stem",
        "stem": "ひき",
        "follows": "です。",
        "form": "二匹です is the counter ひき",
    },
    {
        "kanji": "薄",
        "raw": "うす-める",
        "surface": "薄める",
        "reading": "うすめる",
        "snippet": "実験では硫酸を薄めてから使うので、手順を間違えてはいけない。",
        "source": "kml/data/compounds/lesson_42.json",
        "mode": "stem",
        "stem": "うす",
        "follows": "めてから",
        "form": "薄めて is うす-める. うす-まる would be 薄まって",
    },
    {
        "kanji": "寝",
        "raw": "ね-かす",
        "surface": "寝かせる",
        "reading": "ねかす",
        "snippet": "味噌を樽で寝かせている。",
        "source": "kml/data/compounds/lesson_129.json",
        "mode": "stem",
        "stem": "ね",
        "follows": "かせている。",
        "form": "寝かせている is ね-かす. ね-る would be 寝ている",
    },
    {
        "kanji": "扇",
        "raw": "おうぎ",
        "surface": "扇",
        "reading": "おうぎ",
        "snippet": "A folding fan in summer",
        "source": "kml/contents/books/book_01/lessons/lesson_59.html",
        "mode": "ruby",
        "form": "The verse reads 扇 as おうぎ in 夏の扇, and its English is “A folding fan in summer”",
    },
    {
        "kanji": "沢",
        "raw": "さわ",
        "surface": "沢",
        "reading": "さわ",
        "snippet": "Through the mountain stream,",
        "source": "kml/contents/books/book_01/lessons/lesson_58.html",
        "mode": "ruby",
        "form": "The verse reads 沢 as さわ in 山の沢, and its English is “Through the mountain stream”",
    },
    {
        "kanji": "唐",
        "raw": "から",
        "surface": "唐",
        "reading": "から",
        "snippet": "Wisdom passed down from Tang China",
        "source": "kml/contents/books/book_01/lessons/lesson_63.html",
        "mode": "ruby",
        "form": "The verse reads 唐 as から in 唐から伝わった知恵, and its English is “Wisdom passed down from Tang China”. トウ is a different reading",
    },
)
HELD_BACK = ()

LEVEL_PAGE = "./"
NEXT_LEVEL = "../level-3/"
LESSON_COUNT = 16
LESSON_SIZES = [20] * 15 + [13]
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
        if record["introducedAt"] == "4"
    ]
    if len(records) != 313 or len({record["kanji"] for record in records}) != 313:
        raise SystemExit(f"漢検4級 has {len(records)} characters")
    records.sort(key=lambda record: int(joyo[record["kanji"]]["joyo_index"]))
    if {joyo[record["kanji"]]["grade"] for record in records} != {"S"}:
        raise SystemExit("漢検4級 is not entirely 常用漢字表 grade S")
    if sum(LESSON_SIZES) != 313 or LESSON_SIZES != [20] * 15 + [13]:
        raise SystemExit("4級 lessons are not fifteen of 20 and one of 13")
    lessons = []
    for number, size in enumerate(LESSON_SIZES, start=1):
        lessons.extend([number] * size)
    return records, joyo, lessons


def lesson_nav(number: int) -> str:
    left = (
        f'<a href="{LEVEL_PAGE}">← 漢検4級</a>'
        if number == 1
        else f'<a href="lesson-{number - 1:02d}.html">← 第{number - 1}課</a>'
    )
    right = (
        f'<a href="{NEXT_LEVEL}">漢検3級 →</a>'
        if number == LESSON_COUNT
        else f'<a href="lesson-{number + 1:02d}.html">第{number + 1}課 →</a>'
    )
    return f"""<div class="navbar">
  {left}
  <a href="{LEVEL_PAGE}">漢検4級</a>
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
<p class="school-kicker" lang="ja">漢検4級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">常用漢字表の中学校以降の漢字のうち313字</p>
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
    text = grade2.page_head(title, f"漢検4級レベルの漢字。常用漢字表の中学校以降の漢字のうち313字のうち、第{number}課。")
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
  <a href="{LEVEL_PAGE}">漢検4級</a>
</div>
<p class="school-kicker" lang="ja">漢検4級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">常用漢字表の中学校以降の漢字のうち313字</p>
<h1 class="school-title">{esc(title)}</h1>
{grade2.furigana_bar()}
<nav class="anchor-list">
{anchors}
</nav>
{chr(10).join(articles)}
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="{LEVEL_PAGE}">漢検4級</a>
</div>
{notice}
{grade2.furigana_script()}
</body>
</html>
"""
    text = grade2.page_head(title, f"漢検4級 第{number}課の読み方とことば。常用漢字表の中学校以降の漢字のうち313字。")
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
        "# 漢検4級 vocabulary review",
        "",
        "Learner pages do not explain these choices. The covers below are approved, including the ones with lettering.",
        "Some show the lesson character on a sign. Nothing here has been deployed.",
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
        "Order is the 常用漢字表 掲載順 of the 313 grade-S characters at 漢検4級.",
        "There is no 4級 school-film cut. Lessons are fifteen of 20 and one of 13.",
        "The music link is the existing post-elementary collection, shared by 漢検4級 through 漢検2級.",
        "",
        "The overview hero is 芋 `kml/assets/studies/potato.jpg`. It is in 第1課 and is not that lesson’s cover.",
        "Lesson covers are existing study images, one character from each lesson:",
        "",
    ]
    for number, (slug, kanji) in HERO_CHOICES.items():
        hero = heroes[number]
        note = ""
        lettering = {
            "pray": " — 南無阿弥陀仏 and 奉納 are lettered in the temple",
            "sabre": " — 剣 is lettered on the scroll",
            "boat": " — 舟 is lettered on the sign",
            "hop": " — 跳 is lettered on the post",
            "summit": " — 峰 is lettered on the stone",
            "wing": " — 翼 is lettered on the sign",
            "dew": " — 露 is lettered on the post",
        }
        if slug in lettering:
            note = lettering[slug]
        elif hero["width"] != 1672 or hero["height"] != 941:
            note = f" — native 16:9 at {hero['width']}×{hero['height']}"
        lines.append(f"- 第{number}課 {kanji} `kml/assets/studies/{slug}.jpg`{note}")
    lines.extend(
        [
            "",
            "Not used: 鬼 `ghost.jpg` is a festival scene lettered 祭. 環 `ring.jpg` is a labeled water cycle. 稲 `rice_plant.jpg` carries a long vertical text. 鼓 `drum.jpg` letters 鼓 and 心に響く.",
            "",
            "## Cross-file examples",
            "",
            "Each attached word contains its target character once, and the matcher locks that character’s reading.",
            "A dictionary form is added when a sentence segment or a verse ruby locks that exact reading.",
            "A reading without that lock stays bare.",
            "",
            "## Kept",
            "",
            "- Clearer exact KANJIDIC glosses, with the Heisig line omitted when it restates the card: 奥 interior, 脚 leg, 旬 ten-day period, 薪 firewood, 趣 gist, 更 further, 耐 enduring, 淡 faint, 致 do; cause, 峠 mountain pass, 幅 width, 雌 female, 雄 male, 殿 Mr.; hall, 仰 face-up; look up, 違 difference; differ, 含 contain; include, 載 ride; record, 訴 accusation; sue, 凡 commonplace; mediocre, 謡 song; noh chanting.",
            "- Formal numerals use the Heisig keyword as the card, with no second Heisig line: 壱 formal one, 弐 formal two. KANJIDIC says “one (in documents)” and “II; two”.",
            "- 丹 is “red; cinnabar”. “red” is a KANJIDIC gloss. “cinnabar” is the Heisig keyword. No separate Heisig line.",
            "- 唐 is “Tang dynasty; China”. “Tang dynasty” capitalizes the Heisig keyword “tang dynasty”, which names the KANJIDIC gloss “T'ang”. “China” is a KANJIDIC gloss. No separate Heisig line.",
            "- 爆 is “explode; burst”. “explode” is the Heisig keyword. “burst” shortens the KANJIDIC gloss “burst open”. “bomb” is not on the card. No separate Heisig line.",
            "- 髪 is “hair”, the Heisig keyword, shorter than the only gloss “hair of the head”.",
            "- First gloss kept, Heisig not shown: 菓 candy, 箇 counter for articles, 皆 all, 儀 ceremony, 圏 sphere, 釈 explanation, 拓 clear (the land), 桃 peach, 杯 counter for cupfuls, 泊 overnight stay.",
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
            "The card uses the KANJIDIC2 classical radical, the same default as 10級 through 5級.",
            "Names new at this level with a KANJIDIC2 `rad_name`: 卜 ぼくのと, 舛 まいあし, 釆 のごめ, 隶 れいづくり, 髟 かみがしら（かみかんむりとも）.",
            "甘 あまい, 矛 ほこ, 而 しこうして, 鬼 おに, 鼓 つづみ, and 齒 は have no `rad_name`. The card uses that character’s ordinary reading.",
            "These cards stay on the KANJIDIC2 radical where the joyo column names the radical of the traditional character: 為 火（爪, from 爲）, 尽 尸（皿, from 盡）, 闘 門（鬥, from 鬪）, 弐 弋（貝, from 貳）, 舗 人（舌, from 舖）, 与 一（臼, from 與）, 頼 頁（貝, from 賴）.",
            "辶, 阝, 攵, 艹, 戸, 罒, 川, and 黒 on these cards are the printed forms of 辵, 阜 or 邑, 攴, 艸, 戶, 网, 巛, and 黑.",
            "着 is not in 4級. Its 8級 exception, 羊 rather than 目, is not copied onto other characters.",
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
        "level": "4",
        "count": 313,
        "order": "五十音順",
        "reference": "常用漢字表 grade S via joyo_kanji.csv, the 313 characters introduced at 漢検4級",
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
