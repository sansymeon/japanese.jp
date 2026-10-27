#!/usr/bin/env python3
"""Write the ten 漢検5級 lesson pages and their compiled vocabulary pages.

Uses the 漢検5級 card layout. Output lives at kanken/level-5/.
The level entrance is written by kml/scripts/build_kanken_level_pages.py --level5.
Groups follow 常用漢字表 order in the grade 6 熟語 film sizes:
nine lessons of 20 and one of 11. Lessons 1–8 match those films.
補 stays before 暮. The films place 補 after 論.

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
GRADE = REPO / "kanken/level-5"
FILM_DIR = REPO / "kml/tools/ambient/collections/grade_6"
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
}

# One existing 16:9 study image from a character in that lesson.
# The overview hero, 窓, is in lesson 6 and is not also that lesson's cover.
HERO_CHOICES = {
    1: ("eaves", "宇"),
    2: ("silk", "絹"),
    3: ("crimson", "紅"),
    4: ("young", "若"),
    5: ("steam", "蒸"),
    6: ("dye", "染"),
    7: ("warmth", "暖"),
    8: ("bag", "俵"),
    9: ("curtain", "幕"),
    10: ("infancy", "幼"),
}
OVERVIEW_HERO = ("window", "窓")

# Each part is an exact KANJIDIC2 gloss, unless source is paraphrase.
# show_heisig is false when that keyword is already the displayed wording,
# or when it is not a gloss.
MEANING_CHOICES = {
    "我": {
        "parts": (("I", "kanjidic"), ("ego", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “I” alone hides 自我. Heisig “ego” is the second gloss.",
    },
    "供": {
        "parts": (("offer", "kanjidic"), ("submit", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “submit” hides 提供. Heisig “offer” is the second gloss.",
    },
    "敬": {
        "parts": (("respect", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “respect”. The first gloss “awe” is the same sense. Heisig “awe” is that gloss and is not shown.",
    },
    "権": {
        "parts": (("authority", "kanjidic"), ("rights", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “authority” alone hides 権利. Heisig “rights” is the second gloss.",
    },
    "骨": {
        "parts": (("bone", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “bone”. The first gloss “skeleton” is a narrower sense. Heisig “bone” is this gloss.",
    },
    "座": {
        "parts": (("sit", "kanjidic"), ("seat", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “squat” is not the learner sense of 座る. Heisig “sit” is the gloss “sit”.",
    },
    "裁": {
        "parts": (("judge", "kanjidic"), ("tailor", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “judge” is placed first for 裁判. “tailor” remains for 裁つ. Heisig “judge” is the gloss “judge”.",
    },
    "冊": {
        "parts": (("volume", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “volume”. The first gloss “tome” is rare in learner English. Heisig “volume” is this gloss.",
    },
    "私": {
        "parts": (("private", "kanjidic"), ("I", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “private” alone hides the reading of 私 as “I”. Heisig “me” restates “I” and is not shown.",
    },
    "従": {
        "parts": (("obey", "kanjidic"), ("follow", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “accompany” is 従える. Heisig “obey” is the gloss “obey”.",
    },
    "熟": {
        "parts": (("ripen", "kanjidic"),),
        "show_heisig": False,
        "note": "KANJIDIC gloss “ripen”. The first gloss “mellow” is a narrower sense. Heisig “ripe” is not a gloss and is not shown.",
    },
    "署": {
        "parts": (("signature", "kanjidic"), ("government office", "paraphrase")),
        "show_heisig": False,
        "note": "“signature” is a KANJIDIC gloss. “government office” spells out the gloss “govt office”. Heisig “government bureau” is not a gloss and is not shown.",
    },
    "推": {
        "parts": (("infer", "kanjidic"), ("support", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “conjecture” is the same sense as “infer”. Heisig “infer” is this gloss.",
    },
    "値": {
        "parts": (("price", "kanjidic"), ("value", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. Heisig “value” is the second gloss.",
    },
    "宙": {
        "parts": (("mid-air", "kanjidic"), ("space", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “mid-air” alone hides 宇宙. Heisig “midair” restates the first gloss and is not shown.",
    },
    "頂": {
        "parts": (("top", "kanjidic"), ("receive", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “place on the head” is the same sense as “top” in longer wording. Heisig “top” is the gloss “top”.",
    },
    "背": {
        "parts": (("back", "kanjidic"), ("stature", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “stature” hides 背中. Heisig “back” is the gloss “back”.",
    },
    "暮": {
        "parts": (("evening", "kanjidic"), ("livelihood", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “evening” alone hides 暮らす. Heisig “livelihood” is the second gloss.",
    },
    "枚": {
        "parts": (("counter for flat objects", "paraphrase"),),
        "show_heisig": False,
        "note": "“counter for flat objects” is an editorial paraphrase of the KANJIDIC gloss “counter for flat thin objects or sheets”, dropping “thin” and “or sheets”. 大辞泉 describes 枚 as the counter for thin flat things such as paper, boards, and plates. Heisig “sheet of” restates the unfinished gloss “sheet of...” and is not shown.",
    },
    "裏": {
        "parts": (("reverse", "kanjidic"), ("back", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. “reverse” is placed first so the card is not only “back”, which is also 背. Heisig “reverse side” restates “reverse” and is not shown.",
    },
    "律": {
        "parts": (("law", "kanjidic"), ("rhythm", "kanjidic")),
        "show_heisig": False,
        "note": "Both are KANJIDIC glosses. The first gloss “rhythm” hides 法律. Heisig “law” is the gloss “law”.",
    },
}

# No 5級 character is itself a radical whose printed form differs from the shared table.
RADICAL_CARD = {}

# Real classification differences. The card stays on the KANJIDIC2 classical radical.
CHARACTER_RADICAL_NOTES = {
    "厳": "KANJIDIC2の古典部首は厂です。joyo_kanji.csv は口で、嚴の部首です。カードは厂のままです。",
    "収": "KANJIDIC2の古典部首は又です。joyo_kanji.csv は攴で、收の部首です。カードは又のままです。",
    "党": "KANJIDIC2の古典部首は儿です。joyo_kanji.csv は黑で、黨の部首です。カードは儿のままです。",
    "秘": "KANJIDIC2の古典部首は禾です。joyo_kanji.csv は示で、祕の部首です。カードは禾のままです。",
    "並": "KANJIDIC2の古典部首は一です。joyo_kanji.csv は立です。カードは一のままです。",
    "巻": "KANJIDIC2の古典部首は己です。joyo_kanji.csv は卩で、卷の部首です。カードは己のままです。",
    "処": "KANJIDIC2の古典部首は几です。joyo_kanji.csv は虍で、處の部首です。KANJIDICのネルソン部首は夂です。カードは几のままです。",
}
SKIP_EXAMPLES = set()

# Reviewed, and the card wording was left as the dictionary gloss.
MEANING_REVIEW = {
    "郷": "KANJIDIC gloss “home town”. Heisig “hometown” is the same wording.",
    "存": "KANJIDIC gloss “exist”. Heisig “remain” is not a gloss and is not shown.",
    "党": "KANJIDIC gloss “party”. Heisig “political party” is the longer form of this gloss and is not shown.",
    "翌": "KANJIDIC gloss “the following”. Heisig “following day” is the same sense in a fuller phrase. The shorter gloss stays.",
}

# Dictionary form shown to the learner. The snippet is an existing KML sentence.
# stem mode: the segment is the character alone, read as `stem`, and the next
# segment starts with `follows`, which has to be an inflection of this reading only.
# word mode: a segment's surface and reading assign to this 常用漢字表 reading.
# ruby mode: the HTML contains ruby for this character and reading.
VERIFIED_EXAMPLES = (
    {
        "kanji": "洗",
        "raw": "あら-う",
        "surface": "洗う",
        "reading": "あらう",
        "snippet": "夕食の後で食器を洗いました。",
        "source": "kml/data/compounds/lesson_07.json",
        "mode": "stem",
        "stem": "あら",
        "follows": "いました。",
        "form": "洗いました is あら-う",
    },
    {
        "kanji": "訪",
        "raw": "たず-ねる",
        "surface": "訪ねる",
        "reading": "たずねる",
        "snippet": "旅の途中で静かな古寺を訪ねました。",
        "source": "kml/data/compounds/lesson_09.json",
        "mode": "stem",
        "stem": "たず",
        "follows": "ねました。",
        "form": "訪ねました is たず-ねる. おとず-れる would be 訪れました",
    },
    {
        "kanji": "供",
        "raw": "そな-える",
        "surface": "供える",
        "reading": "そなえる",
        "snippet": "朝、仏壇に水を供えます。",
        "source": "kml/data/compounds/lesson_32.json",
        "mode": "stem",
        "stem": "そな",
        "follows": "えます。",
        "form": "供えます is そな-える. とも is a different reading",
    },
    {
        "kanji": "済",
        "raw": "す-ます",
        "surface": "済ます",
        "reading": "すます",
        "snippet": "駅の前で用事を済ませてから帰りました。",
        "source": "kml/data/compounds/lesson_64.json",
        "mode": "stem",
        "stem": "す",
        "follows": "ませてから",
        "form": "済ませて is す-ます. す-む would be 済んで",
    },
    {
        "kanji": "退",
        "raw": "しりぞ-く",
        "surface": "退く",
        "reading": "しりぞく",
        "snippet": "車が来るので、道から退いてください。",
        "source": "kml/data/compounds/lesson_79.json",
        "mode": "stem",
        "stem": "しりぞ",
        "follows": "いてください。",
        "form": "退いて is しりぞ-く. しりぞ-ける would be 退けて",
    },
    {
        "kanji": "垂",
        "raw": "た-らす",
        "surface": "垂らす",
        "reading": "たらす",
        "snippet": "余暇には、川で糸を垂らしています。",
        "source": "kml/data/compounds/lesson_102.json",
        "mode": "stem",
        "stem": "た",
        "follows": "らしています。",
        "form": "垂らしています is た-らす. た-れる would be 垂れています",
    },
    {
        "kanji": "延",
        "raw": "の-びる",
        "surface": "延びる",
        "reading": "のびる",
        "snippet": "予算の審議は、夜まで延びました。",
        "source": "kml/data/compounds/lesson_103.json",
        "mode": "stem",
        "stem": "の",
        "follows": "びました。",
        "form": "延びました is の-びる. の-べる would be 延べました. の-ばす would be 延ばしました",
    },
    {
        "kanji": "延",
        "raw": "の-ばす",
        "surface": "延ばす",
        "reading": "のばす",
        "snippet": "荒天を避ける作戦で、出漁を一日延ばしました。",
        "source": "kml/data/compounds/lesson_104.json",
        "mode": "stem",
        "stem": "の",
        "follows": "ばしました。",
        "form": "延ばしました is の-ばす. The sentence uses 出漁. の-びる would be 延びました",
    },
    {
        "kanji": "傷",
        "raw": "いた-む",
        "surface": "傷む",
        "reading": "いたむ",
        "snippet": "港の住宅は、潮風で傷みやすいです。",
        "source": "kml/data/compounds/lesson_104.json",
        "mode": "stem",
        "stem": "いた",
        "follows": "み",
        "form": "傷みやすい is いた-む. いた-める would be 傷め",
    },
    {
        "kanji": "染",
        "raw": "そ-まる",
        "surface": "染まる",
        "reading": "そまる",
        "snippet": "西の空が茜に染まった。",
        "source": "kml/data/compounds/lesson_125.json",
        "mode": "stem",
        "stem": "そ",
        "follows": "まった。",
        "form": "染まった is そ-まる. そ-める would be 染めた. し-みる would be 染みる",
    },
    {
        "kanji": "痛",
        "raw": "いた-む",
        "surface": "痛む",
        "reading": "いたむ",
        "snippet": "大きな音で鼓膜が痛みました。",
        "source": "kml/data/compounds/lesson_13.json",
        "mode": "stem",
        "stem": "いた",
        "follows": "みました。",
        "form": "痛みました is いた-む. いた-める would be 痛めました. いた-い would be 痛かった",
    },
    {
        "kanji": "痛",
        "raw": "いた-める",
        "surface": "痛める",
        "reading": "いためる",
        "snippet": "転んで脊椎を痛めました。",
        "source": "kml/data/compounds/lesson_14.json",
        "mode": "stem",
        "stem": "いた",
        "follows": "めました。",
        "form": "痛めました is いた-める. いた-む would be 痛みました",
    },
    {
        "kanji": "担",
        "raw": "かつ-ぐ",
        "surface": "担ぐ",
        "reading": "かつぐ",
        "snippet": "逞しい腕で荷物を担いだ。",
        "source": "kml/data/compounds/lesson_149.json",
        "mode": "stem",
        "stem": "かつ",
        "follows": "いだ。",
        "form": "担いだ is かつ-ぐ. にな-う would be 担う",
    },
    {
        "kanji": "装",
        "raw": "よそお-う",
        "surface": "装う",
        "reading": "よそおう",
        "snippet": "清楚な装いが式に似合う。",
        "source": "kml/data/compounds/lesson_153.json",
        "mode": "stem",
        "stem": "よそお",
        "follows": "いが",
        "form": "装い is よそお-う",
    },
    {
        "kanji": "裁",
        "raw": "さば-く",
        "surface": "裁く",
        "reading": "さばく",
        "snippet": "裁きは感情ではなく、公允でなければならないと先輩は言った。",
        "source": "kml/data/compounds/lesson_42.json",
        "mode": "stem",
        "stem": "さば",
        "follows": "きは",
        "form": "裁き is さば-く. た-つ would be 裁つ",
    },
    {
        "kanji": "俵",
        "raw": "たわら",
        "surface": "俵",
        "reading": "たわら",
        "snippet": "俵を藁で編んだ。",
        "source": "kml/data/compounds/lesson_124.json",
        "mode": "stem",
        "stem": "たわら",
        "follows": "を",
        "form": "俵を is たわら",
    },
    {
        "kanji": "革",
        "raw": "かわ",
        "surface": "革",
        "reading": "かわ",
        "snippet": "shine on the old leather bag.",
        "source": "kml/contents/books/book_01/lessons/lesson_140.html",
        "mode": "ruby",
        "form": "The verse reads 革 as かわ in 古い革の鞄, and its English is “the old leather bag”",
    },
    {
        "kanji": "源",
        "raw": "みなもと",
        "surface": "源",
        "reading": "みなもと",
        "snippet": "A pure source never runs dry.",
        "source": "kml/contents/books/book_01/lessons/lesson_98.html",
        "mode": "ruby",
        "form": "The verse reads 源 as みなもと in 清らかな源は, and its English is “A pure source”",
    },
    {
        "kanji": "紅",
        "raw": "くれない",
        "surface": "紅",
        "reading": "くれない",
        "snippet": "floated a crimson leaf.",
        "source": "kml/contents/books/book_01/lessons/lesson_32.html",
        "mode": "ruby",
        "form": "The verse reads 紅 as くれない in 紅の葉, and its English is “a crimson leaf”. べに is a different reading",
    },
    {
        "kanji": "縦",
        "raw": "たて",
        "surface": "縦",
        "reading": "たて",
        "snippet": "Tall cedars rise straight upward,",
        "source": "kml/contents/books/book_01/lessons/lesson_72.html",
        "mode": "ruby",
        "form": "The verse reads 縦 as たて in 高い杉が縦に伸び, and its English is “Tall cedars rise straight upward”",
    },
    {
        "kanji": "泉",
        "raw": "いずみ",
        "surface": "泉",
        "reading": "いずみ",
        "snippet": "A mountain spring wells up,",
        "source": "kml/contents/books/book_01/lessons/lesson_76.html",
        "mode": "ruby",
        "form": "The verse reads 泉 as いずみ in 山の泉が湧き, and its English is “A mountain spring”",
    },
    {
        "kanji": "頂",
        "raw": "いただき",
        "surface": "頂",
        "reading": "いただき",
        "snippet": "the summit draws near.",
        "source": "kml/contents/books/book_01/lessons/lesson_86.html",
        "mode": "ruby",
        "form": "The verse reads 頂 as いただき, and its English is “the summit”. いただ-く would be 頂く",
    },
    {
        "kanji": "暖",
        "raw": "あたた-か",
        "surface": "暖かい",
        "reading": "あたたかい",
        "snippet": "猫は暖かい場所を喜びます。",
        "source": "kml/data/compounds/lesson_78.json",
        "mode": "stem",
        "stem": "あたた",
        "follows": "か",
        "form": "暖かい is あたた-か. あたた-まる would be 暖まる. あたた-める would be 暖める",
    },
    {
        "kanji": "巻",
        "raw": "カン",
        "surface": "巻末",
        "reading": "かんまつ",
        "snippet": "作家の年譜を、巻末で確認しました。",
        "source": "kml/data/compounds/lesson_97.json",
        "mode": "word",
        "form": "巻末 is カン. ま-く would be 巻く. まき would be 巻",
    },
)

HELD_BACK = (
    "異 こと: 二つの地図は、境界が異なります. The segment reads 異 as こと, and なります is not okurigana of that bare reading, so it does not lock.",
    "我 わ: lesson_112.html reads 我 in これ我が道. That is a classical inscription, so わ stays bare.",
    "優 すぐれる: 藩校には、詩文に優れた才媛がいました. 藩校 and 才媛 are not learner wording.",
    "討 うつ: 将軍は逆賊を討ちました and 海難の仇を討つ話. Both are historical tales, so うつ stays bare.",
    "乱 みだれる: 詩人は世の乱れを歎いた. The sentence is literary, and the word is the noun 乱れ.",
    "乳 ちち: lesson_40.html reads 乳のような泉 as ちち. That verse is poetic, so ちち stays bare.",
    "否 いな: a nearby verse reads 否む, which is いなむ, not いな.",
    "延 のべる: 延べ百人が展覧会に来ました. The segment is 延べ（のべ）, and the lock requires the full okurigana べる.",
    "射 いる: 的を射ていました. 射て does not lock い-る.",
    "危 あやぶむ: 出漁が危ぶまれます. 危ぶまれます does not lock あや-ぶむ, and the sentence uses 出漁.",
)

LEVEL_PAGE = "./"
NEXT_LEVEL = "../level-4/"
LESSON_COUNT = 10
SAFE_HOW = {"okurigana", "whole word", "start", "end"}


def film_cuts() -> list[list[str]]:
    cuts = []
    for number in range(1, LESSON_COUNT + 1):
        path = FILM_DIR / f"grade_6_compounds_school_{number:02d}.json"
        seen: list[str] = []
        for scene in json.loads(path.read_text(encoding="utf-8"))["scenes"]:
            kanji = scene.get("kanji")
            if kanji and len(kanji) == 1 and kanji not in seen:
                seen.append(kanji)
        cuts.append(seen)
    if len(cuts) != LESSON_COUNT or sum(len(cut) for cut in cuts) != 191:
        raise SystemExit("Grade 6 film cuts are not 191 characters in ten lessons")
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
        if record["introducedAt"] == "5"
    ]
    if len(records) != 191:
        raise SystemExit(f"漢検5級 has {len(records)} characters")
    records.sort(key=lambda record: int(joyo[record["kanji"]]["joyo_index"]))
    cuts = film_cuts()
    seq = [record["kanji"] for record in records]
    flat = [kanji for cut in cuts for kanji in cut]
    if [len(cut) for cut in cuts] != [20] * 9 + [11]:
        raise SystemExit("Grade 6 films are not nine lessons of 20 and one of 11")
    if seq[:160] != flat[:160]:
        raise SystemExit("5級 lessons 1–8 differ from the grade 6 熟語 films")
    joyo_from_film = flat[:164] + ["補"] + [kanji for kanji in flat[164:] if kanji != "補"]
    if seq != joyo_from_film:
        raise SystemExit("5級 order is not the 常用漢字表 order")
    lessons = []
    for number, cut in enumerate(cuts, start=1):
        lessons.extend([number] * len(cut))
    return records, joyo, lessons


def lesson_nav(number: int) -> str:
    left = (
        f'<a href="{LEVEL_PAGE}">← 漢検5級</a>'
        if number == 1
        else f'<a href="lesson-{number - 1:02d}.html">← 第{number - 1}課</a>'
    )
    right = (
        f'<a href="{NEXT_LEVEL}">漢検4級 →</a>'
        if number == LESSON_COUNT
        else f'<a href="lesson-{number + 1:02d}.html">第{number + 1}課 →</a>'
    )
    return f"""<div class="navbar">
  {left}
  <a href="{LEVEL_PAGE}">漢検5級</a>
  {right}
</div>"""


def review_block() -> str:
    return """
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLWU0EpkddEOk" target="_blank" rel="noopener noreferrer">漢検5級の漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLbjp2j5SAHGs" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 10 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLLpAPKufLmCc" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 8 films</span></a>
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
<p class="school-kicker" lang="ja">漢検5級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学6年生で習う191字</p>
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
    text = grade2.page_head(title, f"漢検5級レベルの漢字。小学6年生で習う191字のうち、第{number}課。")
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
  <a href="{LEVEL_PAGE}">漢検5級</a>
</div>
<p class="school-kicker" lang="ja">漢検5級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学6年生で習う191字</p>
<h1 class="school-title">{esc(title)}</h1>
{grade2.furigana_bar()}
<nav class="anchor-list">
{anchors}
</nav>
{chr(10).join(articles)}
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="{LEVEL_PAGE}">漢検5級</a>
</div>
{notice}
{grade2.furigana_script()}
</body>
</html>
"""
    text = grade2.page_head(title, f"漢検5級 第{number}課の読み方とことば。小学6年生で習う191字。")
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
        "# 漢検5級 vocabulary review",
        "",
        "Learner pages do not explain these choices. The lesson covers are approved, including the lettering on 蒸 and 俵.",
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
        "Order is the 常用漢字表 掲載順. Lessons use the grade 6 熟語 film sizes: nine of 20 and one of 11.",
        "Lessons 1–8 match those films. 補 stays before 暮, in 第9課. The films place 補 after 論, at the end of film 10.",
        "",
        "The overview hero is 窓 `kml/assets/studies/window.jpg`.",
        "Lesson covers are existing study images, one character from each lesson:",
        "",
    ]
    for number, (slug, kanji) in HERO_CHOICES.items():
        hero = heroes[number]
        note = ""
        if slug == "steam":
            note = " — 蒸 is lettered on the banner"
        elif slug == "bag":
            note = " — 俵 is lettered on the wooden post"
        elif hero["width"] != 1672 or hero["height"] != 941:
            note = f" — native 16:9 at {hero['width']}×{hero['height']}"
        lines.append(f"- 第{number}課 {kanji} `kml/assets/studies/{slug}.jpg`{note}")
    lines.extend(
        [
            "",
            "乳 `milk.jpg` is a spring labeled 乳白の泉, so it is not a cover. 泉 `spring.jpg` is a fountain. 卵 `egg.jpg` letters 卵; 第10課 uses 幼.",
            "砂 `sand.jpg` is an hourglass in a lettered study, so it is not a cover.",
            "",
            "## Cross-file examples",
            "",
            "Each attached word contains its target character once, and the matcher locks that character’s reading.",
            "",
            "## Kept",
            "",
            "- 翌 stays “the following”. Heisig “following day” is the same sense in a fuller phrase.",
            "- 署 stays “signature; government office”. “government office” spells out the gloss “govt office”.",
            "- 枚 is “counter for flat objects”. That is an editorial paraphrase of the KANJIDIC gloss “counter for flat thin objects or sheets”, dropping “thin” and “or sheets”. Heisig “sheet of” is not shown.",
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
            "The card uses the KANJIDIC2 classical radical, the same default as 10級 through 6級.",
            "Japanese names for radicals new at this level come from KANJIDIC2 `rad_name` where that element exists: 几 つくえ, 尢 だいのまげあし（もっともとも）, 幺 いとがしら（ようへんとも）.",
            "己 おのれ, 至 いたる, 舌 した, and 骨 ほね have no `rad_name`. The card uses the character’s ordinary reading.",
            "疋 ひき has no `rad_name`. ひき is the school name of radical 103.",
            "革 かわ has no `rad_name`. かわ is the reading of the radical character. かくのかわ is the other name.",
            "署 shows 罒（よんかしら）, the form inside the character. The classical head is 网.",
            "These cards stay on the KANJIDIC2 radical where the joyo column names the radical of the traditional character: 厳 厂（口, from 嚴）, 収 又（攴, from 收）, 党 儿（黑, from 黨）, 秘 禾（示, from 祕）, 巻 己（卩, from 卷）, 処 几（虍, from 處）.",
            "処 also has Nelson radical 夂 in KANJIDIC2. The card stays 几.",
            "並 stays 一（いち）. The joyo column says 立. The card stays on the KANJIDIC2 radical.",
            "辶, 阝, 攵, and 艹 on these cards are the printed forms of 辵, 阜 or 邑, 攴, and 艸.",
            "着 is not in 5級. Its 8級 exception, 羊 rather than 目, is not copied onto other characters.",
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
        "grade": 6,
        "level": "5",
        "count": 191,
        "order": "五十音順",
        "reference": "学年別漢字配当表 via joyo_kanji.csv, checked against the grade 6 熟語 film cuts",
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
