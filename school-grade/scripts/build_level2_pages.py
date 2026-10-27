#!/usr/bin/env python3
"""Write the nine 漢検2級 lesson pages and their compiled vocabulary pages.

Uses the 漢検2級 card layout. Output lives at kanken/level-2/.
The level entrance is written by kml/scripts/build_kanken_level_pages.py --level2.
The 185 characters are the 常用漢字表 grade-S rows whose 漢検 level is 2,
in 掲載順. There is no separate school-film cut for this level. The
post-elementary films are one collection shared by 漢検4級 through 漢検2級.
Lessons are four groups of 20 and five groups of 21, in that order.

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
import html
import re
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[2]
GRADE = REPO / "kanken/level-2"
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
    178: ("韋", "なめしがわ", ""),
    192: ("鬯", "かおりぐさ", "KANJIDIC2 に rad_name はありません。カードは鬯の訓です。音はチョウです。"),
    92: ("牙", "きばへん", ""),
    89: ("爻", "めめ", "KANJIDIC2 の rad_name はめめ、まじわるです。カードはめめです。"),
    153: ("豸", "むじなへん", ""),
}

# One existing 16:9 study image from a character in that lesson.
# The overview hero, 鶴, is in lesson 6 and is not that lesson’s cover.
# Covers are approved and are kept.
HERO_CHOICES = {
    1: ("storm", "嵐"),
    2: ("cliff", "崖"),
    3: ("tiger", "虎"),
    4: ("fence", "柵"),
    5: ("dining_tray", "膳"),
    6: ("bracing", "爽"),
    7: ("rainbow", "虹"),
    8: ("honey", "蜜"),
    9: ("indigo", "藍"),
}
OVERVIEW_HERO = ("crane", "鶴")

# Exact later glosses, or a pair of exact glosses when the first gloss alone is the wrong sense.
# show_heisig is false when the keyword is already displayed or restates a displayed sense.
MEANING_CHOICES = {
    '挨': {'parts': [('approach', 'kanjidic'), ('push open', 'kanjidic')], 'note': 'KANJIDIC2 glosses “approach” and “push open”. 挨拶 is the usual greeting and is not itself either gloss. The lesson-page keyword “push open” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '宛': {'parts': [('address', 'kanjidic'), ('just like', 'kanjidic')], 'note': 'KANJIDIC2 glosses “address” and “just like”. 宛てる is the address sense and 宛ら is just like. “fortunately” is another gloss and stays off the card. The lesson-page keyword “addressed to” restates “address”, so it is not a separate line.', 'show_heisig': False},
    '鬱': {'parts': [('gloom', 'kanjidic'), ('depression', 'kanjidic')], 'note': 'KANJIDIC2 glosses “gloom” and “depression”. The lesson-page keyword “depression” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '俺': {'parts': [('I', 'kanjidic'), ('myself', 'kanjidic')], 'note': 'KANJIDIC2 glosses “I” and “myself”. The lesson-page keyword “myself” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '蓋': {'parts': [('cover', 'kanjidic'), ('lid', 'kanjidic')], 'note': 'KANJIDIC2 glosses “cover” and “lid”. The lesson-page keyword “lid” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '顎': {'parts': [('jaw', 'kanjidic'), ('chin', 'kanjidic')], 'note': 'KANJIDIC2 glosses “jaw” and “chin”. The lesson-page keyword “chin” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '葛': {'parts': [('arrowroot', 'kanjidic'), ('kudzu', 'kanjidic')], 'note': 'KANJIDIC2 glosses “arrowroot” and “kudzu”. The lesson-page keyword “kudzu” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '釜': {'parts': [('kettle', 'kanjidic'), ('cauldron', 'kanjidic')], 'note': 'KANJIDIC2 glosses “kettle” and “cauldron”. The lesson-page keyword “cauldron” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '亀': {'parts': [('tortoise', 'kanjidic'), ('turtle', 'kanjidic')], 'note': 'KANJIDIC2 glosses “tortoise” and “turtle”. The lesson-page keyword “turtle” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '嗅': {'parts': [('smell', 'kanjidic'), ('sniff', 'kanjidic')], 'note': 'KANJIDIC2 glosses “smell” and “sniff”. The lesson-page keyword “sniff” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '串': {'parts': [('spit', 'kanjidic'), ('skewer', 'kanjidic')], 'note': 'KANJIDIC2 glosses “spit” and “skewer”. The lesson-page keyword “skewer” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '隙': {'parts': [('crevice', 'kanjidic'), ('fissure', 'kanjidic')], 'note': 'KANJIDIC2 glosses “crevice” and “fissure”. The lesson-page keyword “fissure” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '股': {'parts': [('thigh', 'kanjidic'), ('crotch', 'kanjidic')], 'note': 'KANJIDIC2 glosses “thigh” and “crotch”. 股関節 is the thigh sense. The lesson-page keyword “crotch” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '勾': {'parts': [('slope', 'kanjidic'), ('capture', 'kanjidic')], 'note': 'KANJIDIC2 glosses “be bent”, “slope”, and “capture”. “be bent” and “slope” are the 勾配 sense, so the card uses “slope”. “capture” is 勾留. The keyword “capture” is already displayed, so it is not a separate line.', 'show_heisig': False},
    '挫': {'parts': [('crush', 'kanjidic'), ('sprain', 'kanjidic')], 'note': 'KANJIDIC2 glosses “crush” and “sprain”. The lesson-page keyword “sprain” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '塞': {'parts': [('close', 'kanjidic'), ('obstruct', 'kanjidic')], 'note': 'KANJIDIC2 glosses “close” and “obstruct”. The lesson-page keyword “obstruct” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '柵': {'parts': [('stockade', 'kanjidic'), ('fence', 'kanjidic')], 'note': 'KANJIDIC2 glosses “stockade” and “fence”. The lesson-page keyword “fence” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '嫉': {'parts': [('jealous', 'kanjidic'), ('envy', 'kanjidic')], 'note': 'KANJIDIC2 glosses “jealous” and “envy”. The lesson-page keyword “envy” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '呪': {'parts': [('spell', 'kanjidic'), ('curse', 'kanjidic')], 'note': 'KANJIDIC2 glosses “spell” and “curse”. The lesson-page keyword “curse” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '裾': {'parts': [('cuff', 'kanjidic'), ('hem', 'kanjidic')], 'note': 'KANJIDIC2 glosses “cuff” and “hem”. 袖裾 is the clothing sense. “foot of mountain” is another gloss, the 山裾 sense, and stays off the card. The lesson-page keyword “hem” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '戚': {'parts': [('grieve', 'kanjidic'), ('relatives', 'kanjidic')], 'note': 'KANJIDIC2 glosses “grieve” and “relatives”. 哀戚 is grief and 親戚 is relatives. The lesson-page keyword “relatives” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '煎': {'parts': [('broil', 'kanjidic'), ('roast', 'kanjidic')], 'note': 'KANJIDIC2 glosses “broil” and “roast”. The lesson-page keyword “roast” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '爽': {'parts': [('refreshing', 'kanjidic'), ('bracing', 'kanjidic')], 'note': 'KANJIDIC2 glosses “refreshing” and “bracing”. The lesson-page keyword “bracing” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '踪': {'parts': [('remains', 'kanjidic'), ('footprint', 'kanjidic')], 'note': 'KANJIDIC2 glosses “remains” and “footprint”. The lesson-page keyword “footprints” restates “footprint”, so it is not a separate line.', 'show_heisig': False},
    '遜': {'parts': [('humble', 'kanjidic'), ('modest', 'kanjidic')], 'note': 'KANJIDIC2 glosses “humble” and “modest”. The lesson-page keyword “modest” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '旦': {'parts': [('daybreak', 'kanjidic'), ('dawn', 'kanjidic')], 'note': 'KANJIDIC2 glosses “daybreak” and “dawn”. The lesson-page keyword “dawn” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '綻': {'parts': [('unravel', 'kanjidic'), ('begin to open', 'kanjidic')], 'note': 'KANJIDIC2 gloss 1 is “be rent”, an archaic wording of the tear, so it stays off the card. “unravel” is gloss 3 and the lesson-page keyword. “begin to open” is gloss 5, the bud and smile sense; “smile” is that same sense. The joyo English “rip” is not itself a gloss. “ripped” is gloss 2 of the tear. The keyword is already displayed, so it is not a separate line.', 'show_heisig': False},
    '諦': {'parts': [('truth', 'kanjidic'), ('give up', 'kanjidic')], 'note': 'KANJIDIC2 glosses “truth” and “give up”. 真理 is the truth sense and 諦める is give up. “abandon” is another gloss of that second sense. The lesson-page keyword “renunciation” is not a gloss, so it is not a separate line.', 'show_heisig': False},
    '罵': {'parts': [('abuse', 'kanjidic'), ('insult', 'kanjidic')], 'note': 'KANJIDIC2 glosses “abuse” and “insult”. The lesson-page keyword “insult” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '斑': {'parts': [('spot', 'kanjidic'), ('blemish', 'kanjidic')], 'note': 'KANJIDIC2 glosses “spot” and “blemish”. The lesson-page keyword “blemish” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '哺': {'parts': [('nurse', 'kanjidic'), ('suckle', 'kanjidic')], 'note': 'KANJIDIC2 glosses “nurse” and “suckle”. The lesson-page keyword “suckle” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '貌': {'parts': [('form', 'kanjidic'), ('countenance', 'kanjidic')], 'note': 'KANJIDIC2 glosses “form” and “countenance”. The lesson-page keyword “countenance” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '弥': {'parts': [('all the more', 'kanjidic'), ('increasingly', 'kanjidic')], 'note': 'KANJIDIC2 glosses “all the more” and “increasingly”. The lesson-page keyword “increasingly” is the later gloss, so it is not a separate line.', 'show_heisig': False},
    '拉': {'parts': [('Latin', 'kanjidic'), ('kidnap', 'kanjidic'), ('crush', 'kanjidic')], 'note': 'KANJIDIC2 glosses “Latin”, “kidnap”, and “crush”. 拉丁 is Latin, 拉致 is kidnap, and “crush” is also the joyo English. They are different uses. The lesson-page keyword “yank” is not a gloss, so it is not a separate line.', 'show_heisig': False},
    '僅': {'parts': [('only a little', 'paraphrase')], 'note': 'The only KANJIDIC2 gloss, and the joyo English, is “a wee bit”. The card says “only a little”, an editorial paraphrase of 僅か. The Heisig keyword “trifle” is not a gloss, so it is not a separate line.', 'show_heisig': False},
    '汎': {'parts': [('pan-', 'kanjidic'), ('general', 'heisig')], 'note': 'KANJIDIC2 and the joyo English give only “pan-”, the prefix in 汎太平洋. “general” is the lesson-page Heisig keyword and the 汎用 sense. It is not a KANJIDIC2 gloss. Both are on the card, so there is no separate Heisig line.', 'show_heisig': False},
    '那': {'parts': [('what', 'paraphrase')], 'note': 'The only KANJIDIC2 gloss is “what?”. The card says “what”, dropping the question mark. The joyo English is “what”. The Heisig keyword “that” is not a gloss. 那覇 and 刹那 do not use this gloss.', 'show_heisig': False},
}

# First gloss kept. The keyword is not a KANJIDIC2 gloss, so it is not shown.
MEANING_REVIEW = {
    '曖': 'First gloss kept: “dark”. The Heisig keyword “unclear” is not a KANJIDIC2 gloss.',
    '畏': 'First gloss kept: “fear”. The Heisig keyword “apprehensive” is not a KANJIDIC2 gloss.',
    '萎': 'First gloss kept: “wither”. The Heisig keyword “numb” is not a KANJIDIC2 gloss.',
    '彙': 'First gloss kept: “same kind”. The Heisig keyword “glossary” is not a KANJIDIC2 gloss.',
    '咽': 'First gloss kept: “throat”. The Heisig keyword “gullet” is not a KANJIDIC2 gloss.',
    '唄': 'First gloss kept: “song”. The Heisig keyword “pop song” is not a KANJIDIC2 gloss.',
    '臆': 'First gloss kept: “timidity”. The Heisig keyword “cowardice” is not a KANJIDIC2 gloss.',
    '苛': 'First gloss kept: “torment”. The Heisig keyword “bullying” is not a KANJIDIC2 gloss.',
    '楷': 'First gloss kept: “square character style”. The Heisig keyword “block letters” is not a KANJIDIC2 gloss.',
    '潰': 'First gloss kept: “crush”. The Heisig keyword “defile” is not a KANJIDIC2 gloss.',
    '諧': 'First gloss kept: “harmony”. The Heisig keyword “orderliness” is not a KANJIDIC2 gloss.',
    '骸': 'First gloss kept: “bone”. The Heisig keyword “remains” is not a KANJIDIC2 gloss.',
    '玩': 'First gloss kept: “play”. The Heisig keyword “toy with” is not a KANJIDIC2 gloss.',
    '伎': 'First gloss kept: “deed”. The Heisig keyword “performing artist” is not a KANJIDIC2 gloss.',
    '畿': 'First gloss kept: “capital”. The Heisig keyword “capital area” is not a KANJIDIC2 gloss.',
    '惧': 'First gloss kept: “fear”. The Heisig keyword “disquieting” is not a KANJIDIC2 gloss.',
    '詣': 'First gloss kept: “visit a temple”. The Heisig keyword “visit shrine” is not a KANJIDIC2 gloss.',
    '憬': 'First gloss kept: “yearn for”. The Heisig keyword “long for” is not a KANJIDIC2 gloss.',
    '稽': 'First gloss kept: “think”. The Heisig keyword “examine” is not a KANJIDIC2 gloss.',
    '錮': 'First gloss kept: “confinement”. The Heisig keyword “weld” is not a KANJIDIC2 gloss.',
    '梗': 'First gloss kept: “for the most part”. The Heisig keyword “spiny” is not a KANJIDIC2 gloss.',
    '傲': 'First gloss kept: “be proud”. The Heisig keyword “arrogance” is not a KANJIDIC2 gloss.',
    '頃': 'First gloss kept: “time”. The Heisig keyword “about that time” is not a KANJIDIC2 gloss.',
    '痕': 'First gloss kept: “mark”. The Heisig keyword “scar” is not a KANJIDIC2 gloss.',
    '沙': 'First gloss kept: “sand”. The Heisig keyword “grains of sand” is not a KANJIDIC2 gloss.',
    '采': 'First gloss kept: “dice”. The Heisig keyword “grab” is not a KANJIDIC2 gloss.',
    '刹': 'First gloss kept: “temple”. The Heisig keyword “buddhist temple” is not a KANJIDIC2 gloss.',
    '拶': 'First gloss kept: “be imminent”. The Heisig keyword “imminent” is not a KANJIDIC2 gloss.',
    '斬': 'First gloss kept: “beheading”. The Heisig keyword “chop off” is not a KANJIDIC2 gloss.',
    '摯': 'First gloss kept: “gift”. The Heisig keyword “clasp” is not a KANJIDIC2 gloss.',
    '餌': 'First gloss kept: “food”. The Heisig keyword “feed” is not a KANJIDIC2 gloss.',
    '羞': 'First gloss kept: “feel ashamed”. The Heisig keyword “humiliate” is not a KANJIDIC2 gloss.',
    '憧': 'First gloss kept: “yearn after”. The Heisig keyword “desire” is not a KANJIDIC2 gloss.',
    '芯': 'First gloss kept: “wick”. The Heisig keyword “core” is not a KANJIDIC2 gloss.',
    '須': 'First gloss kept: “ought”. The Heisig keyword “must” is not a KANJIDIC2 gloss.',
    '凄': 'First gloss kept: “uncanny”. The Heisig keyword “nifty” is not a KANJIDIC2 gloss.',
    '醒': 'First gloss kept: “awake”. The Heisig keyword “awakening” is not a KANJIDIC2 gloss.',
    '詮': 'First gloss kept: “discussion”. The Heisig keyword “elucidate” is not a KANJIDIC2 gloss.',
    '箋': 'First gloss kept: “paper”. The Heisig keyword “stationery” is not a KANJIDIC2 gloss.',
    '膳': 'First gloss kept: “small low table”. The Heisig keyword “dining tray” is not a KANJIDIC2 gloss.',
    '痩': 'First gloss kept: “get thin”. The Heisig keyword “lose weight” is not a KANJIDIC2 gloss.',
    '捉': 'First gloss kept: “catch”. The Heisig keyword “nab” is not a KANJIDIC2 gloss.',
    '汰': 'First gloss kept: “washing”. The Heisig keyword “cleanse” is not a KANJIDIC2 gloss.',
    '戴': 'First gloss kept: “be crowned with”. The Heisig keyword “accept humbly” is not a KANJIDIC2 gloss.',
    '緻': 'First gloss kept: “fine (i.e. not coarse)”. The Heisig keyword “intricate” is not a KANJIDIC2 gloss.',
    '酎': 'First gloss kept: “sake”. The Heisig keyword “alcohol” is not a KANJIDIC2 gloss.',
    '貼': 'First gloss kept: “stick”. The Heisig keyword “post a bill” is not a KANJIDIC2 gloss.',
    '嘲': 'First gloss kept: “ridicule”. The Heisig keyword “derision” is not a KANJIDIC2 gloss.',
    '捗': 'First gloss kept: “make progress”. The Heisig keyword “make headway” is not a KANJIDIC2 gloss.',
    '椎': 'First gloss kept: “chinquapin”. The Heisig keyword “sweet oak” is not a KANJIDIC2 gloss.',
    '溺': 'First gloss kept: “drown”. The Heisig keyword “drowning” is not a KANJIDIC2 gloss.',
    '填': 'First gloss kept: “fill in”. The Heisig keyword “inlay” is not a KANJIDIC2 gloss.',
    '妬': 'First gloss kept: “jealous”. The Heisig keyword “jealousy” is not a KANJIDIC2 gloss.',
    '頓': 'First gloss kept: “suddenly”. The Heisig keyword “immediate” is not a KANJIDIC2 gloss.',
    '丼': 'First gloss kept: “bowl”. The Heisig keyword “donburi” is not a KANJIDIC2 gloss.',
    '匂': 'First gloss kept: “fragrant”. The Heisig keyword “scent” is not a KANJIDIC2 gloss.',
    '捻': 'First gloss kept: “twirl”. The Heisig keyword “wrench” is not a KANJIDIC2 gloss.',
    '剥': 'First gloss kept: “come off”. The Heisig keyword “peel off” is not a KANJIDIC2 gloss.',
    '氾': 'First gloss kept: “spread out”. The Heisig keyword “to overflow” is not a KANJIDIC2 gloss.',
    '蔽': 'First gloss kept: “cover”. The Heisig keyword “cover over” is not a KANJIDIC2 gloss.',
    '餅': 'First gloss kept: “mochi rice cake”. The Heisig keyword “mochi” is not a KANJIDIC2 gloss.',
    '璧': 'First gloss kept: “sphere”. The Heisig keyword “gem” is not a KANJIDIC2 gloss.',
    '蔑': 'First gloss kept: “ignore”. The Heisig keyword “disdain” is not a KANJIDIC2 gloss.',
    '勃': 'First gloss kept: “suddenness”. The Heisig keyword “uprising” is not a KANJIDIC2 gloss.',
    '昧': 'First gloss kept: “dark”. The Heisig keyword “obscure” is not a KANJIDIC2 gloss.',
    '冥': 'First gloss kept: “dark”. The Heisig keyword “hades” is not a KANJIDIC2 gloss.',
    '冶': 'First gloss kept: “melting”. The Heisig keyword “metallurgy” is not a KANJIDIC2 gloss.',
    '闇': 'First gloss kept: “get dark”. The Heisig keyword “pitch dark” is not a KANJIDIC2 gloss.',
    '湧': 'First gloss kept: “boil”. The Heisig keyword “gush” is not a KANJIDIC2 gloss.',
    '妖': 'First gloss kept: “attractive”. The Heisig keyword “bewitched” is not a KANJIDIC2 gloss.',
    '瘍': 'First gloss kept: “swelling”. The Heisig keyword “carbuncle” is not a KANJIDIC2 gloss.',
    '沃': 'First gloss kept: “fertility”. The Heisig keyword “fertile” is not a KANJIDIC2 gloss.',
    '辣': 'First gloss kept: “pungent”. The Heisig keyword “bitter” is not a KANJIDIC2 gloss.',
    '慄': 'First gloss kept: “fear”. The Heisig keyword “shudder” is not a KANJIDIC2 gloss.',
    '侶': 'First gloss kept: “companion”. The Heisig keyword “partner” is not a KANJIDIC2 gloss.',
    '瞭': 'First gloss kept: “clear”. The Heisig keyword “obvious” is not a KANJIDIC2 gloss.',
    '瑠': 'First gloss kept: “lapis lazuli”. The Heisig keyword “marine blue” is not a KANJIDIC2 gloss.',
    '賂': 'First gloss kept: “bribe”. The Heisig keyword “graft” is not a KANJIDIC2 gloss.',
    '弄': 'First gloss kept: “play with”. The Heisig keyword “tinker with” is not a KANJIDIC2 gloss.',
}

VERIFIED_EXAMPLES = [
    {
        "kanji": "畏",
        "raw": "おそ-れる",
        "surface": "畏れる",
        "reading": "おそれる",
        "snippet": "the traveller lowers his voice in reverence.",
        "source": "kml/contents/books/book_01/lessons/lesson_104.html",
        "mode": "ruby-stem",
        "stem": "おそ",
        "follows": "れる。",
        "form": "畏れる is おそ-れる. The verse’s English is “the traveller lowers his voice in reverence”",
    },
    {
        "kanji": "牙",
        "raw": "きば",
        "surface": "牙",
        "reading": "きば",
        "snippet": "A wolf bares its fangs in the forest shadows",
        "source": "kml/contents/books/book_01/lessons/lesson_103.html",
        "mode": "ruby",
        "form": "牙 is きば. The verse’s English is “A wolf bares its fangs in the forest shadows”",
    },
    {
        "kanji": "臼",
        "raw": "うす",
        "surface": "臼",
        "reading": "うす",
        "snippet": "echoes beneath the pestle.",
        "source": "kml/contents/books/book_01/lessons/lesson_133.html",
        "mode": "ruby",
        "form": "臼 is うす. The verse’s English is “The wooden mortar echoes beneath the pestle”",
    },
    {
        "kanji": "拳",
        "raw": "こぶし",
        "surface": "拳",
        "reading": "こぶし",
        "snippet": "than a clenched fist.",
        "source": "kml/contents/books/book_01/lessons/lesson_65.html",
        "mode": "ruby",
        "form": "拳 is こぶし. The verse’s English is “than a clenched fist”",
    },
    {
        "kanji": "籠",
        "raw": "ロウ",
        "surface": "籠",
        "reading": "ろう",
        "snippet": "Guided by lantern light, one quietly passes through the gate.",
        "source": "kml/contents/books/book_01/lessons/lesson_25.html",
        "mode": "ruby",
        "form": "灯籠の籠 is ロウ. The verse’s English is “Guided by lantern light, one quietly passes through the gate”",
    },
    {
        "kanji": "籠",
        "raw": "こ-もる",
        "surface": "籠る",
        "reading": "こもる",
        "snippet": "Over the weekend he secluded himself at home and wrote.",
        "source": "kml/data/compounds/lesson_151.json",
        "mode": "headword-boundary",
        "written": "る",
        "form": "籠る is こもる. The headword writes only る after 籠, so the ruby is こも, one kana past the hyphen in こ-もる. The sentence itself is 籠って, which does not spell こもる. い-える would not apply; no other reading is こもる",
    },
    {
        "kanji": "剥",
        "raw": "は-がす",
        "surface": "剥す",
        "reading": "はがす",
        "snippet": "I peeled the tape off the box.",
        "source": "kml/data/compounds/lesson_62.json",
        "mode": "headword-boundary",
        "written": "す",
        "form": "剥す is はがす. The headword writes only す after 剥, so the ruby is はが, past the hyphen in は-がす. The sentence is 剥しました. は-ぐ would be はぐ. The file notes that 剥がす is the newer spelling",
    },
    {
        "kanji": "蔑",
        "raw": "さげす-む",
        "surface": "蔑む",
        "reading": "さげすむ",
        "snippet": "to despise",
        "source": "kml/tools/ambient/collections/post_elementary/post_elementary_compounds_v2_03.json",
        "mode": "ruby-stem",
        "stem": "さげす",
        "follows": "む",
        "form": "蔑む is さげす-む. The ruby is さげす and む is written after it. The gloss is “to despise”",
    },
    {
        "kanji": "遡",
        "raw": "ソ",
        "surface": "遡及",
        "reading": "そきゅう",
        "snippet": "retroactive effect",
        "source": "kml/tools/ambient/collections/post_elementary/post_elementary_compounds_v2_21.json",
        "mode": "listed-word",
        "mark": "<ruby>遡及<rt>そきゅう</rt></ruby>",
        "form": "遡及 is ソ. The ruby on the whole word is そきゅう. The gloss is “retroactive effect”",
    },
]

HELD_BACK = (
    "罵（ののしれば） is the conditional, not ののしる, so that reading stays bare.",
    "呪い（のろい） does not spell のろう, so that reading stays bare.",
    "怨恨 is えんこん, so it does not lock オン. 刹那 is せつな, so it does not lock サツ. 憧憬 in KML is どうけい, so it does not lock ショウ. 眉間 is みけん, so it does not lock ビ. 怪しい is 怪, so it is not an example of 妖（あやしい）.",
    "はがれる, なえる, ぬぐう, いる, and あやしい have no verified citation form in KML.",
)

RADICAL_CARD = {}

# Real classification differences. The card stays on the KANJIDIC2 classical radical.
CHARACTER_RADICAL_NOTES = {
    "亀": "KANJIDIC2の古典部首は乙です。joyo_kanji.csv は龜で、龜の部首です。カードは乙のままです。",
}

LEVEL_PAGE = "./"
LESSON_COUNT = 9
LESSON_SIZES = [20] * 4 + [21] * 5
SAFE_HOW = {"okurigana", "whole word", "start", "end"}
SKIP_EXAMPLES = set()


TABLE_FORMS = {"剥": "剝", "叱": "𠮟", "填": "塡", "頬": "頰"}


def joyo_row(joyo: dict, kanji: str) -> dict:
    return joyo[TABLE_FORMS.get(kanji, kanji)]


def load_level() -> tuple[list[dict], dict, list[int]]:
    import csv

    joyo = {}
    with JOYO.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            joyo[row["kanji"]] = row
    records = [
        record
        for record in json.loads(INDEX.read_text(encoding="utf-8"))["characters"]
        if record["introducedAt"] == "2"
    ]
    if len(records) != 185 or len({record["kanji"] for record in records}) != 185:
        raise SystemExit(f"漢検2級 has {len(records)} characters")
    records.sort(key=lambda record: int(joyo_row(joyo, record["kanji"])["joyo_index"]))
    if {joyo_row(joyo, record["kanji"])["grade"] for record in records} != {"S"}:
        raise SystemExit("漢検2級 is not entirely 常用漢字表 grade S")
    if sum(LESSON_SIZES) != 185 or LESSON_SIZES != [20] * 4 + [21] * 5:
        raise SystemExit("2級 lessons are not four of 20 and five of 21")
    lessons = []
    for number, size in enumerate(LESSON_SIZES, start=1):
        lessons.extend([number] * size)
    return records, joyo, lessons


def lesson_nav(number: int) -> str:
    left = (
        f'<a href="{LEVEL_PAGE}">← 漢検2級</a>'
        if number == 1
        else f'<a href="lesson-{number - 1:02d}.html">← 第{number - 1}課</a>'
    )
    right = (
        f'<a href="{LEVEL_PAGE}">漢検2級へ戻る</a>'
        if number == LESSON_COUNT
        else f'<a href="lesson-{number + 1:02d}.html">第{number + 1}課 →</a>'
    )
    return f"""<div class="navbar">
  {left}
  <a href="{LEVEL_PAGE}">漢検2級</a>
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
<p class="school-kicker" lang="ja">漢検2級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">常用漢字表の中学校以降の漢字のうち185字</p>
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
    text = grade2.page_head(title, f"漢検2級レベルの漢字。常用漢字表の中学校以降の漢字のうち185字のうち、第{number}課。")
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
  <a href="{LEVEL_PAGE}">漢検2級</a>
</div>
<p class="school-kicker" lang="ja">漢検2級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">常用漢字表の中学校以降の漢字のうち185字</p>
<h1 class="school-title">{esc(title)}</h1>
{grade2.furigana_bar()}
<nav class="anchor-list">
{anchors}
</nav>
{chr(10).join(articles)}
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="{LEVEL_PAGE}">漢検2級</a>
</div>
{notice}
{grade2.furigana_script()}
</body>
</html>
"""
    text = grade2.page_head(title, f"漢検2級 第{number}課の読み方とことば。常用漢字表の中学校以降の漢字のうち185字。")
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
    if item["mode"] == "headword-boundary":
        data = json.loads(text)
        found = False
        for character in data.get("characters") or []:
            for compound in character.get("compounds") or []:
                if compound.get("surface") != item["surface"]:
                    continue
                reading = grade2.kata_to_hira(compound.get("reading") or "")
                if reading != item["reading"]:
                    continue
                example = compound.get("example") or {}
                blob = (example.get("ja") or "") + (example.get("en") or "")
                if item["snippet"] not in blob:
                    continue
                found = True
        if not found:
            raise SystemExit(f"Missing headword {item['surface']} for {kanji} {item['raw']}")
        after = item["surface"][item["surface"].index(kanji) + 1 :]
        if after != item["written"]:
            raise SystemExit(f"{item['surface']} does not write {item['written']} after {kanji}")
        special, stem, okuri = grade2.parse_reading(item["raw"])
        whole = "" if special else grade2.kata_to_hira(stem + okuri)
        okuri_h = grade2.kata_to_hira(okuri)
        stem_h = grade2.kata_to_hira(stem)
        if whole != item["reading"] or not whole.startswith(stem_h):
            raise SystemExit(f"{kanji} headword {item['reading']} is not {item['raw']}")
        if not okuri_h.endswith(after) or not (0 < len(after) < len(okuri_h)):
            raise SystemExit(f"{kanji} written {after} does not fall inside the okurigana of {item['raw']}")
        locked = []
        for raw in entry["on"] + entry["kun"]:
            other_special, other_stem, other_okuri = grade2.parse_reading(raw)
            if other_special:
                continue
            if grade2.kata_to_hira(other_stem + other_okuri) == item["reading"]:
                locked.append(raw)
        if locked != [item["raw"]]:
            raise SystemExit(f"{item['surface']} locks {locked}, not {item['raw']}")
        return
    if item["mode"] == "listed-word":
        if item["snippet"] not in text or item["mark"] not in text:
            raise SystemExit(f"Missing listed word for {kanji} {item['raw']}")
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


def keyword_from_page(record: dict) -> tuple[int, str, str]:
    """Resolve the lesson-page keyword. 伎's index anchor uses %20; the page id uses an underscore."""
    page, anchor = record["lessonPage"].split("#", 1)
    path = REPO / page.lstrip("/")
    page_text = path.read_text(encoding="utf-8")
    found = None
    for cand in (anchor, unquote(anchor), unquote(anchor).replace(" ", "_")):
        if f'id="{cand}"' in page_text:
            found = cand
            break
    if found is None:
        raise SystemExit(f"Missing {anchor} in {path.name}")
    start = page_text.find(f'id="{found}"')
    block = page_text[start : page_text.find("</section>", start)]
    keyword = re.search(r'<span class="kanji-keyword">(.*?)</span>', block, re.S)
    if not keyword:
        raise SystemExit(f"No keyword for {record['kanji']} in {path.name}")
    lesson_no = int(path.stem.split("_")[1])
    cleaned = re.sub(r"\s+", " ", html.unescape(keyword.group(1))).strip()
    return lesson_no, found, cleaned


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
        lesson_no, anchor, keyword = keyword_from_page(record)
        compared = grade2.grade1.compare_meanings(keyword, info["glosses"])
        row = joyo_row(joyo, kanji)
        ons = grade2.split_joyo(re.sub(r"\[\d+\]", "", row["on_kana"]))
        kuns = grade2.split_joyo(re.sub(r"\[\d+\]", "", row["kun_kana"]))
        words, bare, unmatched, match_notes = grade2.attach_words(
            kanji, ons, kuns, compounds.get(kanji, [])
        )
        stroke_path = unquote(record["strokePage"].lstrip("/"))
        lesson_path = record["lessonPage"].lstrip("/").split("#", 1)[0] + "#" + anchor
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
                "slug": record["slug"].replace(" ", "_"),
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
        "# 漢検2級 vocabulary review",
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
        "Order is the 常用漢字表 掲載順 of the 185 grade-S characters at 漢検2級.",
        "There is no separate school-film cut. Lessons are four of 20 and five of 21.",
        "The music link is the existing post-elementary collection, shared by 漢検4級 through 漢検2級.",
        "",
        "The overview hero is 鶴 `kml/assets/studies/crane.jpg`. It is in 第6課 and is not that lesson’s cover.",
        "Lesson covers are existing study images, one character from each lesson:",
        "",
    ]
    for number, (slug, kanji) in HERO_CHOICES.items():
        hero = heroes[number]
        note = ""
        lettering = {
            "tiger": " — 虎 is lettered on the wooden sign",
            "dining_tray": " — 家族 is lettered on the scroll",
        }
        if slug in lettering:
            note = lettering[slug]
        elif hero["width"] != 1672 or hero["height"] != 941:
            note = f" — native 16:9 at {hero['width']}×{hero['height']}"
        lines.append(f"- 第{number}課 {kanji} `kml/assets/studies/{slug}.jpg`{note}")
    lines.extend(
        [
            "",
            "Not used for a cover: 駒 `pony.jpg` has 駒 on the stable, 藤 `wisteria.jpg` has 藤 on the post, 蜂 `bee.jpg` has 蜂, 餅 `mochi.jpg` has 餅 and the English word mochi, 枕 `pillow.jpg` has book titles, and 麓 `foot_of_mountain.jpg` has 麓 on the sign.",
            "",
            "## Cross-file examples",
            "",
            "Each attached word contains its target character once, and the matcher locks that character’s reading.",
            "A dictionary form is added when a sentence segment or a verse ruby locks that exact reading.",
            "The ruby may end after the 常用漢字表 hyphen. It locks when the ruby plus the kana written after it spell that whole reading and no other reading.",
            "A headword can do the same when its recorded reading is exactly one 常用漢字表 reading and the kana written after the character is only the end of that okurigana.",
            "A reading with no suitable lock stays bare.",
            "",
            "## Kept",
            "",
            "Clearer exact KANJIDIC glosses, with the Heisig line omitted when it restates the card:",
            "",
        ]
    )
    for kanji, choice in MEANING_CHOICES.items():
        wording = "; ".join(part for part, _source in choice["parts"])
        lines.append(f"- {kanji} “{wording}”")
    lines.extend(
        [
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
            "Names new at this level: 韋 なめしがわ, 牙 きばへん, 爻 めめ, 豸 むじなへん. 鬯 has no KANJIDIC2 rad_name, so the card uses its kun かおりぐさ. Its on is チョウ.",
            "亀 stays on the KANJIDIC2 radical 乙. joyo_kanji.csv names 龜, the radical of the traditional character 龜.",
            "辶, 阝, 攵, 艹, 礻, and 戸 on these cards are the printed forms of 辵, 阜 or 邑, 攴, 艸, 示, and 戶.",
            "着 is not in 2級. Its 8級 exception, 羊 rather than 目, is not copied onto other characters. 艹, 阝, 辶, 罒, and 麦 on these cards are the printed forms of 艸, 阜 or 邑, 辵, 网, and 麥.",
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
        "level": "2",
        "count": 185,
        "order": "五十音順",
        "reference": "常用漢字表 grade S via joyo_kanji.csv, the 185 characters introduced at 漢検2級",
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
