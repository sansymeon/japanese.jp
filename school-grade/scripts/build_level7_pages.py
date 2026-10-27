#!/usr/bin/env python3
"""Write the ten 漢検7級 lesson pages and their compiled vocabulary pages.

Uses the 漢検8級 card layout. Output lives at kanken/level-7/.
The level entrance is written by kml/scripts/build_kanken_level_pages.py --level7.
Groups are the grade 4 熟語 film cuts, which match 常用漢字表 order:
eight lessons of 20 and two of 21.

English starts from the first KANJIDIC2 gloss. MEANING_CHOICES may name a
clearer gloss from that same entry, or a marked paraphrase. Heisig stays on
its own line only when that keyword is not already the displayed wording.
Radicals stay on the KANJIDIC2 classical radical. 着 is not in this level.

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
GRADE = REPO / "kanken/level-7"
FILM_DIR = REPO / "kml/tools/ambient/collections/grade_4"
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
    122: ("罒", "よんかしら", "古典部首は网（あみがしら）です。置にある形は罒です。"),
    131: ("臣", "しん", ""),
    138: ("艮", "ねづくり", "こんとも呼ばれます。"),
    160: ("辛", "からい", ""),
    183: ("飛", "とぶ", ""),
    186: ("香", "かおり", ""),
    198: ("鹿", "しか", ""),
}

# One existing 16:9 study image from a character in that lesson.
HERO_CHOICES = {
    1: ("love", "愛"),
    2: ("lagoon", "潟"),
    3: ("fishing", "漁"),
    4: ("vegetable", "菜"),
    5: ("deer", "鹿"),
    6: ("well", "井"),
    7: ("nest", "巣"),
    8: ("ume", "梅"),
    9: ("breed", "牧"),
    10: ("wheel", "輪"),
}
OVERVIEW_HERO = ("scenery", "景")

# Each part is an exact KANJIDIC2 gloss. show_heisig is false when that keyword
# is already one of the displayed glosses, or when it is not a gloss.
MEANING_CHOICES = {
    "岡": {
        "parts": (("hill", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “hill”. The first gloss is “mount”. Heisig “hills” is the same sense and is not repeated.",
    },
    "機": {
        "parts": (("machine", "kanjidic"), ("opportunity", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “loom” is the first gloss and is the historical sense. Heisig “machine” is the first of these, so it is not repeated.",
    },
    "協": {
        "parts": (("cooperation", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “cooperation”. The first gloss “co-” is the same word abbreviated. Heisig “cooperation” is that gloss.",
    },
    "芸": {
        "parts": (("art", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “art”. Heisig “art” is that gloss. “technique” is the first gloss and stays off the card.",
    },
    "完": {
        "parts": (("completion", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “completion”, for 完成. Heisig “complete” is not the gloss string, so it is not shown as a dictionary meaning.",
    },
    "参": {
        "parts": (("visit", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “visit”. The first gloss “nonplussed” is not the learner’s sense. Heisig “participate” is not a gloss and is not shown.",
    },
    "産": {
        "parts": (("products", "kanjidic"), ("give birth", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “produce” is not a gloss and is not shown.",
    },
    "児": {
        "parts": (("child", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “child”. The first gloss is “newborn babe”. Heisig “newborn” is not the gloss string and is not shown.",
    },
    "順": {
        "parts": (("order", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “order”, for 順番. Heisig “follow” is not a gloss and is not shown.",
    },
    "成": {
        "parts": (("become", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “become”. Heisig “become” is that gloss. “turn into” is the first gloss of the same family.",
    },
    "説": {
        "parts": (("explanation", "kanjidic"), ("theory", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “theory” is the second, so it is not repeated. “opinion” is the first gloss and stays off the card.",
    },
    "倉": {
        "parts": (("warehouse", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “warehouse”. The first gloss “godown” is the same sense. Heisig “warehouse” is that gloss.",
    },
    "達": {
        "parts": (("reach", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “reach”. Heisig “attain” is also a gloss of the same family and is not repeated. “accomplished” is the first gloss.",
    },
    "的": {
        "parts": (("bull's eye", "kanjidic"), ("adjective ending", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “bulls eye” is the target sense without the apostrophe, so it is not repeated.",
    },
    "典": {
        "parts": (("ceremony", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “ceremony”. Heisig “ceremony” is that gloss. “code” is the first gloss and stays off the card.",
    },
    "徒": {
        "parts": (("on foot", "kanjidic"), ("junior", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. 徒歩 is the first, 生徒 the second. Heisig “junior” is the second, so it is not repeated.",
    },
    "博": {
        "parts": (("broad; extensive", "paraphrase"),),
        "show_heisig": True,
        "note": "Editorial paraphrase of 小学館『デジタル大辞泉』, as given on コトバンク (https://kotobank.jp/word/博-600045): 〈ハク〉１「広く行き渡る」. “broad; extensive” is not a KANJIDIC2 gloss. Those glosses are “Dr.”, “command”, “esteem”, “win acclaim”, “Ph.D.”, “exposition”, and “fair”. Heisig “knowledgeable” matches the same entry’s next words, 「広く諸事に通ずる」, and is not a gloss, so it stays on its own line. 大辞泉 also lists the kun ひろい. The 常用漢字表 lists only ハク and （バク）, so ひろい is not added as a reading.",
    },
    "課": {
        "parts": (("lesson", "kanjidic"), ("section", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “chapter” is the first gloss. Heisig “sub-division” is not a gloss (“division” is) and is not shown.",
    },
    "競": {
        "parts": (("compete with", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “compete with”. “emulate” is the first gloss. Heisig “compete” is this sense without “with”, so it is not repeated.",
    },
    "観": {
        "parts": (("view", "kanjidic"),),
        "show_heisig": True,
        "note": "KANJIDIC gloss “view”. “outlook” is the first gloss. Heisig “observe” is not a gloss, so it stays on its own line.",
    },
    "固": {
        "parts": (("harden", "kanjidic"),),
        "show_heisig": True,
        "note": "KANJIDIC gloss “harden”, the first gloss, for 固める and 固まる. Heisig “hard” is the 固い sense and is not a gloss, so it stays on its own line.",
    },
    "康": {
        "parts": (("ease", "kanjidic"),),
        "show_heisig": True,
        "note": "KANJIDIC gloss “ease”, the first gloss. The other gloss is “peace”. Heisig “health” is the 健康 sense learners meet, is not a gloss, and stays on its own line.",
    },
    "不": {
        "parts": (("negative", "kanjidic"),),
        "show_heisig": True,
        "note": "KANJIDIC gloss “negative”, the first gloss. Heisig “not” is the learner’s sense of 不, is not a gloss, and stays on its own line.",
    },
    "府": {
        "parts": (("urban prefecture", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “urban prefecture”, for 大阪府. “borough” is the first gloss. Heisig “municipality” is not a gloss and is not shown.",
    },
    "争": {
        "parts": (("dispute", "kanjidic"),),
        "show_heisig": True,
        "note": "KANJIDIC gloss “dispute”. “contend” is the first gloss. Heisig “conflict” is not a gloss, so it stays on its own line.",
    },
    "積": {
        "parts": (("pile up", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “pile up”, for 積む. “volume” is the first gloss and “product (x*y)” is the math sense. Heisig “accumulate” is not a gloss and is not shown.",
    },
    "未": {
        "parts": (("not yet", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “not yet”. The first gloss “un-” is the same prefix sense. Heisig “not yet” is that gloss.",
    },
}

# Real classification differences. The card stays on the KANJIDIC2 classical radical.
CHARACTER_RADICAL_NOTES = {
    "塩": "KANJIDIC2の古典部首は土です。joyo_kanji.csv は鹵で、鹽の部首です。カードは土のままです。",
    "欠": "KANJIDIC2の古典部首は欠です。joyo_kanji.csv は缶で、缺の部首です。カードは欠のままです。",
    "争": "KANJIDIC2の古典部首は亅です。joyo_kanji.csv は爪で、爭の部首です。カードは亅のままです。",
    "単": "KANJIDIC2の古典部首は十です。joyo_kanji.csv は口で、單の部首です。カードは十のままです。",
    "変": "KANJIDIC2の古典部首は夂です。joyo_kanji.csv は言で、變の部首です。カードは夂のままです。",
}
SKIP_EXAMPLES = {("巣", "巣窟")}

# Reviewed, and the card wording was left as the dictionary gloss.
# Heisig is not shown when it only restates that gloss in other words.
MEANING_REVIEW = {
    "媛": "Kept “beautiful woman”, the first gloss. “princess” is the other gloss. Heisig “maiden” is not a gloss and is not shown.",
    "好": "Kept “fond”, the first gloss. Heisig “fond of” is the same sense in more words and is not shown.",
    "梅": "Kept “plum”, the only gloss. Heisig “ume” names the same fruit and is not a gloss, so it is not shown.",
    "昨": "Kept “yesterday”, the first gloss. “previous” is the other gloss. Heisig “previous day” is that sense and is not shown.",
    "末": "Kept “end”, the first gloss, for 週末. Heisig “extremity” is not a gloss and is not shown.",
    "極": "Kept “extreme”, the first gloss. “pole” is a later gloss. The Heisig line “poles” stays, because it names that other gloss.",
    "阜": "Kept “hill”, the first gloss. Heisig “mound” matches a later gloss, so that line stays.",
}

# Dictionary form shown to the learner. The snippet is an existing KML sentence.
# stem mode: the segment is the character alone, read as `stem`, and the next
# segment starts with `follows`, which has to be an inflection of this reading only.
# word mode: a segment's surface and reading assign to this 常用漢字表 reading.
VERIFIED_EXAMPLES = (
    {
        "kanji": "改",
        "raw": "あらた-める",
        "surface": "改める",
        "reading": "あらためる",
        "snippet": "一票の重さを、改めて感じました",
        "source": "kml/data/compounds/lesson_87.json",
        "mode": "stem",
        "stem": "あらた",
        "follows": "めて",
        "form": "改めて is あらた-める. あらた-まる would be 改まり or 改まっ",
    },
    {
        "kanji": "加",
        "raw": "くわ-わる",
        "surface": "加わる",
        "reading": "くわわる",
        "snippet": "新しい版には地図が加わりました",
        "source": "kml/data/compounds/lesson_65.json",
        "mode": "stem",
        "stem": "くわ",
        "follows": "わりました",
        "form": "加わりました is くわ-わる. くわ-える would be 加えました",
    },
    {
        "kanji": "建",
        "raw": "た-てる",
        "surface": "建てる",
        "reading": "たてる",
        "snippet": "大工が家を建てます",
        "source": "kml/data/compounds/lesson_05.json",
        "mode": "stem",
        "stem": "た",
        "follows": "てます",
        "form": "建てます is た-てる. た-つ would be 建ちます",
    },
    {
        "kanji": "建",
        "raw": "た-つ",
        "surface": "建つ",
        "reading": "たつ",
        "snippet": "火事の跡に、新しい家が建ちました",
        "source": "kml/data/compounds/lesson_95.json",
        "mode": "stem",
        "stem": "た",
        "follows": "ちました",
        "form": "建ちました is た-つ. た-てる would be 建てました",
    },
    {
        "kanji": "固",
        "raw": "かた-い",
        "surface": "固い",
        "reading": "かたい",
        "snippet": "古い箱の錠前が固いです",
        "source": "kml/data/compounds/lesson_21.json",
        "mode": "stem",
        "stem": "かた",
        "follows": "いです",
        "form": "固いです is かた-い. かた-まる would be 固まります",
    },
    {
        "kanji": "固",
        "raw": "かた-まる",
        "surface": "固まる",
        "reading": "かたまる",
        "snippet": "冷えて固まった溶岩の上を、注意しながら歩いた",
        "source": "kml/data/compounds/lesson_42.json",
        "mode": "stem",
        "stem": "かた",
        "follows": "まった",
        "form": "固まった is かた-まる. 溶岩 is a harder word than the rest of this lesson. かた-い would be 固い",
    },
    {
        "kanji": "治",
        "raw": "なお-る",
        "surface": "治る",
        "reading": "なおる",
        "snippet": "病気が治ってから、仕事に戻ります",
        "source": "kml/data/compounds/lesson_91.json",
        "mode": "stem",
        "stem": "なお",
        "follows": "って",
        "form": "治って is なお-る. なお-す would be 治して",
    },
    {
        "kanji": "周",
        "raw": "まわ-り",
        "surface": "周り",
        "reading": "まわり",
        "snippet": "勇敢な人ほど、よく周りを見ます",
        "source": "kml/data/compounds/lesson_76.json",
        "mode": "stem",
        "stem": "まわ",
        "follows": "りを",
        "form": "周り is まわ-り",
    },
    {
        "kanji": "初",
        "raw": "はじ-め",
        "surface": "初め",
        "reading": "はじめ",
        "snippet": "祖父は平成の初めにこの家を建てました",
        "source": "kml/data/compounds/lesson_20.json",
        "mode": "stem",
        "stem": "はじ",
        "follows": "めに",
        "form": "初めに is はじ-め. 初めて is the separate reading はじ-めて and was not used here",
    },
    {
        "kanji": "伝",
        "raw": "つた-わる",
        "surface": "伝わる",
        "reading": "つたわる",
        "snippet": "手紙から彼女の感情が伝わりました",
        "source": "kml/data/compounds/lesson_34.json",
        "mode": "stem",
        "stem": "つた",
        "follows": "わりました",
        "form": "伝わりました is つた-わる. つた-える would be 伝えました. つた-う would be 伝いました",
    },
    {
        "kanji": "伝",
        "raw": "つた-う",
        "surface": "伝う",
        "reading": "つたう",
        "snippet": "涙が頬を伝いました",
        "source": "kml/data/compounds/lesson_68.json",
        "mode": "stem",
        "stem": "つた",
        "follows": "いました",
        "form": "伝いました is つた-う. A clear sentence, a little literary",
    },
    {
        "kanji": "冷",
        "raw": "ひ-やす",
        "surface": "冷やす",
        "reading": "ひやす",
        "snippet": "夏は麦茶を冷やして飲みます",
        "source": "kml/data/compounds/lesson_83.json",
        "mode": "stem",
        "stem": "ひ",
        "follows": "やして",
        "form": "冷やして is ひ-やす. ひ-やかす would be 冷やかし. ひ-や does not continue して",
    },
    {
        "kanji": "冷",
        "raw": "さ-ます",
        "surface": "冷ます",
        "reading": "さます",
        "snippet": "湯が熱いので、冷まします",
        "source": "kml/data/compounds/lesson_82.json",
        "mode": "stem",
        "stem": "さ",
        "follows": "まします",
        "form": "冷まします is さ-ます. さ-める would be 冷めます",
    },
    {
        "kanji": "覚",
        "raw": "さ-める",
        "surface": "覚める",
        "reading": "さめる",
        "snippet": "今朝、鳥の声で目が覚めました",
        "source": "kml/data/compounds/lesson_86.json",
        "mode": "stem",
        "stem": "さ",
        "follows": "めました",
        "form": "覚めました is さ-める. さ-ます would be 覚ましました. おぼ-える would be 覚えました",
    },
    {
        "kanji": "覚",
        "raw": "さ-ます",
        "surface": "覚ます",
        "reading": "さます",
        "snippet": "子どもが悪夢で目を覚ましました",
        "source": "kml/data/compounds/lesson_17.json",
        "mode": "stem",
        "stem": "さ",
        "follows": "ましました",
        "form": "覚ましました is さ-ます. さ-める would be 覚めました",
    },
    {
        "kanji": "産",
        "raw": "う-む",
        "surface": "産む",
        "reading": "うむ",
        "snippet": "鶏が朝、卵を産みました",
        "source": "kml/data/compounds/lesson_77.json",
        "mode": "stem",
        "stem": "う",
        "follows": "みました",
        "form": "産みました is う-む. う-まれる would be 産まれました",
    },
    {
        "kanji": "散",
        "raw": "ち-らかる",
        "surface": "散らかる",
        "reading": "ちらかる",
        "snippet": "散らかった部屋の始末をしました",
        "source": "kml/data/compounds/lesson_12.json",
        "mode": "stem",
        "stem": "ち",
        "follows": "らかった",
        "form": "散らかった is ち-らかる. ち-らかす would be 散らかしました. 散らしました is 散らす, not this reading",
    },
    {
        "kanji": "試",
        "raw": "ため-す",
        "surface": "試す",
        "reading": "ためす",
        "snippet": "新しい製品を店で試しました",
        "source": "kml/data/compounds/lesson_23.json",
        "mode": "stem",
        "stem": "ため",
        "follows": "しました",
        "form": "試しました is ため-す",
    },
    {
        "kanji": "量",
        "raw": "はか-る",
        "surface": "量る",
        "reading": "はかる",
        "snippet": "米を升で量ります",
        "source": "kml/data/compounds/lesson_03.json",
        "mode": "stem",
        "stem": "はか",
        "follows": "ります",
        "form": "量ります is はか-る. 升 is the traditional measure in the sentence",
    },
    {
        "kanji": "結",
        "raw": "むす-ぶ",
        "surface": "結ぶ",
        "reading": "むすぶ",
        "snippet": "二つの国が条約を結びました",
        "source": "kml/data/compounds/lesson_16.json",
        "mode": "stem",
        "stem": "むす",
        "follows": "びました",
        "form": "結びました is むす-ぶ. ゆう and ゆわえる are other readings",
    },
    {
        "kanji": "無",
        "raw": "な-い",
        "surface": "無くなる",
        "reading": "なくなる",
        "snippet": "棚の米が、無くなりました",
        "source": "kml/data/compounds/lesson_96.json",
        "mode": "stem",
        "stem": "な",
        "follows": "くなりました",
        "form": "無く is the な-い continuative inside 無くなる. ぶ would be ぶじ or ぶれい",
    },
    {
        "kanji": "末",
        "raw": "すえ",
        "surface": "末",
        "reading": "すえ",
        "snippet": "色々考えた末、残ることにしました",
        "source": "kml/data/compounds/lesson_95.json",
        "mode": "stem",
        "stem": "すえ",
        "follows": "、",
        "form": "末 is read すえ. バツ is the other reading",
    },
    {
        "kanji": "昨",
        "raw": "サク",
        "surface": "昨夜",
        "reading": "さくや",
        "snippet": "昨夜、短い小説を読みました",
        "source": "kml/data/compounds/lesson_06.json",
        "mode": "word",
        "form": "The segment reads 昨夜 as さくや, so 昨 is サク. Headwords that read 昨夜 as ゆうべ were not used",
    },
    {
        "kanji": "折",
        "raw": "おり",
        "surface": "折鶴",
        "reading": "おりづる",
        "snippet": "枕元に、小さな折鶴が置いてありました",
        "source": "kml/data/compounds/lesson_105.json",
        "mode": "word",
        "form": "折鶴 is filed as おりづる. The mechanical pass skipped it because the kun sits inside the compound rather than as okurigana",
    },
    {
        "kanji": "倉",
        "raw": "くら",
        "surface": "倉",
        "reading": "くら",
        "snippet": "Within the old storehouse",
        "source": "kml/contents/books/book_01/lessons/lesson_88.html",
        "mode": "ruby",
        "form": "The verse reads 倉 as くら in 古い倉には, and its English is “storehouse”. 倉庫 is ソウ. 鎌倉（かまくら） is a place name; 倉 does not mean a storehouse there, so it is not the example",
    },
    {
        "kanji": "飯",
        "raw": "めし",
        "surface": "朝飯",
        "reading": "あさめし",
        "snippet": "朝飯に干物を焼きました",
        "source": "kml/data/compounds/lesson_89.json",
        "mode": "word",
        "form": "The segment reads 朝飯 as あさめし, so 飯 is めし",
    },
    {
        "kanji": "無",
        "raw": "ブ",
        "surface": "無事",
        "reading": "ぶじ",
        "snippet": "無事の知らせを聞いて安心しました",
        "source": "kml/data/compounds/lesson_32.json",
        "mode": "word",
        "form": "The segment reads 無事 as ぶじ. One-mora on readings are not filled automatically; this word was added because the segment locks ブ",
    },
)

# Found in KML, and not shown. The reading did not lock, or the sentence is not a learner example.
HELD_BACK = (
    "栄 はえ, はえる: no KML segment. 栄える as さかえる is already on the card.",
    "改 あらたまる: no segment continues あらた with まり or まっ. 改める is shown.",
    "好 すく: 好き（すき） is attested, including 子どもは小さな冒険が好きです in lesson_01.json, where 好 is read す. The table form is す-く（好く）. 好き was not copied onto it.",
    "散 ちらかす: 散らしました is 散らす, not 散らかす. 散らかる is shown from 散らかった.",
    "冷 ひや: 冷やして belongs to ひやす, which is shown. No segment is the noun ひや.",
    "冷 ひやかす, さめる: no segment locks these. さます is shown from 冷まします.",
    "産 うまれる, うぶ: 産みました is うむ, which is shown. No 産まれ or うぶ segment.",
    "共 とも: 苦楽を共にした and 午餐を共にしました. The reading is right; the sentences are not learner examples.",
    "願 ねがう: 昌盛を願います and 平和の永続を願いました. The reading is right; the sentences are not learner examples.",
    "説 とく: 忠恕を説く. Not a learner sentence.",
    "便 たより: 洛中の便りは、船便で十日かかります. Not a learner sentence.",
    "戦 いくさ: その王朝の末期は戦が続きました. Not a learner sentence.",
    "民 たみ: 辺境の民を夷と呼んだ. Not a learner sentence.",
    "清 きよめる: 沐浴してからだを清めます. Not a learner sentence. きよまる has no separate lock.",
    "静 しずめる: 席の揖譲が、会議の空気を静めました. Not a learner sentence.",
    "欠 かく: 欠けた and 欠けています are かける, which is a different reading.",
    "満 みたす: 満ちる and 満ちました are みちる, not みたす.",
    "巣 ソウ: 巣窟 was held back as unsuitable for this level.",
    "倉 くら: 鎌倉（かまくら）, lesson_87.json, is a place name. It was not used as the storehouse example.",
)

LEVEL_PAGE = "./"
NEXT_LEVEL = "../level-6/"
LESSON_COUNT = 10
SAFE_HOW = {"okurigana", "whole word", "start", "end"}


def film_cuts() -> list[list[str]]:
    cuts = []
    for number in range(1, LESSON_COUNT + 1):
        path = FILM_DIR / f"grade_4_compounds_school_{number:02d}.json"
        seen: list[str] = []
        for scene in json.loads(path.read_text(encoding="utf-8"))["scenes"]:
            kanji = scene.get("kanji")
            if kanji and len(kanji) == 1 and kanji not in seen:
                seen.append(kanji)
        cuts.append(seen)
    if len(cuts) != LESSON_COUNT or sum(len(cut) for cut in cuts) != 202:
        raise SystemExit("Grade 4 film cuts are not 202 characters in ten lessons")
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
        if record["introducedAt"] == "7"
    ]
    if len(records) != 202:
        raise SystemExit(f"漢検7級 has {len(records)} characters")
    records.sort(key=lambda record: int(joyo[record["kanji"]]["joyo_index"]))
    cuts = film_cuts()
    if [record["kanji"] for record in records] != [kanji for cut in cuts for kanji in cut]:
        raise SystemExit("7級 order differs from the grade 4 熟語 film cuts")
    lessons = []
    for number, cut in enumerate(cuts, start=1):
        lessons.extend([number] * len(cut))
    return records, joyo, lessons


def lesson_nav(number: int) -> str:
    left = (
        f'<a href="{LEVEL_PAGE}">← 漢検7級</a>'
        if number == 1
        else f'<a href="lesson-{number - 1:02d}.html">← 第{number - 1}課</a>'
    )
    right = (
        f'<a href="{NEXT_LEVEL}">漢検6級 →</a>'
        if number == LESSON_COUNT
        else f'<a href="lesson-{number + 1:02d}.html">第{number + 1}課 →</a>'
    )
    return f"""<div class="navbar">
  {left}
  <a href="{LEVEL_PAGE}">漢検7級</a>
  {right}
</div>"""


def review_block() -> str:
    return """
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLe8oWSTMK85g" target="_blank" rel="noopener noreferrer">漢検7級の漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLf9LPdcxbNnI" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 10 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLQfscrAlbAYo" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 8 films</span></a>
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
<p class="school-kicker" lang="ja">漢検7級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学4年生で習う202字</p>
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
    text = grade2.page_head(title, f"漢検7級レベルの漢字。小学4年生で習う202字のうち、第{number}課。")
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
  <a href="{LEVEL_PAGE}">漢検7級</a>
</div>
<p class="school-kicker" lang="ja">漢検7級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学4年生で習う202字</p>
<h1 class="school-title">{esc(title)}</h1>
{grade2.furigana_bar()}
<nav class="anchor-list">
{anchors}
</nav>
{chr(10).join(articles)}
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="{LEVEL_PAGE}">漢検7級</a>
</div>
{notice}
{grade2.furigana_script()}
</body>
</html>
"""
    text = grade2.page_head(title, f"漢検7級 第{number}課の読み方とことば。小学4年生で習う202字。")
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
        "# 漢検7級 vocabulary review",
        "",
        "Learner pages do not explain these choices. The lesson covers are approved, including 鹿 with the character lettered on the sign.",
        "Meanings, Heisig lines, and the new examples below are waiting for Steve. Nothing here has been deployed.",
        "",
        f"KANJIDIC2 {meta['database']}, {meta['date']}.",
        "English on a card is the first KANJIDIC2 gloss, unless MEANING_CHOICES names a clearer gloss from that same list or a marked paraphrase.",
        "A displayed meaning tagged kanjidic is that exact gloss. A paraphrase is editorial.",
        "Heisig stays on its own line only when the keyword is not already the displayed wording.",
        "Readings are the 常用漢字表 音訓. Parentheses are the table’s indented readings.",
        "Example words come from `kml/data/compounds/`. A word filed under another character is used only when",
        "the same matcher used on 8級 locks it to that reading, and the word is a verb or a headword of at most three kanji.",
        "One-mora on readings are not filled that way. A dictionary form is added only when a sentence segment",
        "locks that exact reading. A reading with no suitable word stays bare.",
        f"Bare readings remaining: {bare}.",
        "",
        "The overview hero is 景 `kml/assets/studies/scenery.jpg`.",
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
            "城 `castle.jpg` is 1536×1024, not 16:9, so it is not a cover.",
            "These cover choices are approved and are not edited by the content review.",
            "",
            "## For judgment",
            "",
            "- 康 keeps “ease” and adds the Heisig line “health”. 不 keeps “negative” and adds “not”. 固 keeps “harden” and adds “hard”.",
            "- 観 shows “view”, with the Heisig line “observe”. 争 shows “dispute”, with the Heisig line “conflict”.",
            "- 課 shows “lesson; section”. 競 shows “compete with”. 府 shows “urban prefecture”. 積 shows “pile up”.",
            "- 量る is exemplified by 米を升で量ります. 固まる uses the 溶岩 sentence.",
            "- 好 すく stays bare. 好き（すき） is attested and was not copied onto す-く.",
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
            "The card uses the KANJIDIC2 classical radical, the same default as 10級, 9級, and 8級.",
            "Japanese names for radicals new at this level come from KANJIDIC2 `rad_name` where that element exists: 勹 つつみがまえ, 卩 ふしづくり, 夂 ふゆがしら, 廴 えんにょう（いんにょうとも）, 戈 かのほこ, 斗 とます, 网 あみがしら, 艮 ねづくり.",
            "Where the radical is the character itself, the card uses its ordinary name: 氏 うじ, 臣 しん, 辛 からい, 飛 とぶ, 香 かおり, 鹿 しか.",
            "置 shows 罒（よんかしら）, the form inside the character. The classical head is 网.",
            "These cards stay on the KANJIDIC2 radical where the joyo column names the radical of the traditional character: 塩 土（鹵, from 鹽）, 欠 欠（缶, from 缺）, 争 亅（爪, from 爭）, 単 十（口, from 單）, 変 夂（言, from 變）.",
            "For the character a learner writes, that KANJIDIC2 radical is the suitable one. 塩 shows a 土偏, not 鹵. 欠 is its own radical. 変 ends in 夂. 単 is classified under 十, which is visible at the bottom. 争 stays 亅（はねぼう）. 爪, the radical of 爭, is the recorded alternative.",
            "着 is not in 7級. Its 8級 exception, 羊 rather than 目, is not copied onto other characters.",
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
        "grade": 4,
        "level": "7",
        "count": 202,
        "order": "五十音順",
        "reference": "学年別漢字配当表 via joyo_kanji.csv, checked against the grade 4 熟語 film cuts",
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
