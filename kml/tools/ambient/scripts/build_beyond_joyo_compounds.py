#!/usr/bin/env python3
"""Build Beyond Jōyō Kanji Compounds (常用外漢字熟語) collections.

Source corpus: kml/data/kanji/kanji_master.csv (grade H / heisig_extra).
Familiarity-ordered volumes in groups of 50.
Same japaneseVocabulary exhibition engine as Jr High compounds.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(SCRIPTS))

from collection_paths import write_collection_path  # noqa: E402
from compounds_ruby import ruby_compound, ruby_word  # noqa: E402
from beyond_joyo_remaining import (  # noqa: E402
    assemble_series_entries,
    build_remaining_entries,
)

COLLECTIONS = ROOT / "collections" / "beyond_joyo"
JUKUGO = COLLECTIONS / "beyond_joyo_jukugo_list.json"
MANIFEST = ROOT / "collections" / "manifest.json"
MASTER_CSV = REPO / "data" / "kanji" / "kanji_master.csv"

PART_SIZE = 50
SOUNDTRACK_CYCLE = 3
SOUNDTRACK_FALLBACK = "audio/jr_high_compounds_soundtrack_1.mp3"
SERIES_SOUNDTRACK = "audio/beyond_joyo_{part}.mp3"
SERIES_ID = "beyond_joyo_compounds"
SERIES_TITLE = "Beyond Jōyō Kanji Compounds"
SERIES_TITLE_JA = "常用外漢字熟語"

STEP = 19400
LAST_BODY = STEP - 1400
OPEN = 800 + 1200 + 3200
REVIEW = 22000
FADE = 4000
BLACK = 600

# Series entries in familiarity order (50 per part).
# Each row: anchor, reading, en, ruby parts [(surface, reading|"" for okurigana)],
# masterKanji (non-Jōyō characters newly introduced by this entry).
SERIES_ENTRIES: list[dict] = [
    # --- Part 1 ---
    {
        "anchor": "綺麗",
        "reading": "きれい",
        "en": "pretty / clean",
        "ruby": [("綺", "き"), ("麗", "れい")],
        "masterKanji": ["綺"],
    },
    {
        "anchor": "醤油",
        "reading": "しょうゆ",
        "en": "soy sauce",
        "ruby": [("醤", "しょう"), ("油", "ゆ")],
        "masterKanji": ["醤"],
    },
    {
        "anchor": "味噌",
        "reading": "みそ",
        "en": "miso",
        "ruby": [("味", "み"), ("噌", "そ")],
        "masterKanji": ["噌"],
    },
    {
        "anchor": "茶碗",
        "reading": "ちゃわん",
        "en": "teacup / rice bowl",
        "ruby": [("茶", "ちゃ"), ("碗", "わん")],
        "masterKanji": ["碗"],
    },
    {
        "anchor": "石鹸",
        "reading": "せっけん",
        "en": "soap",
        "ruby": [("石", "せっ"), ("鹸", "けん")],
        "masterKanji": ["鹸"],
    },
    {
        "anchor": "柴犬",
        "reading": "しばいぬ",
        "en": "Shiba Inu",
        "ruby": [("柴", "しば"), ("犬", "いぬ")],
        "masterKanji": ["柴"],
    },
    {
        "anchor": "蝶々",
        "reading": "ちょうちょう",
        "en": "butterfly",
        "ruby": [("蝶", "ちょう"), ("々", "ちょう")],
        "masterKanji": ["蝶"],
    },
    {
        "anchor": "蓮根",
        "reading": "れんこん",
        "en": "lotus root",
        "ruby": [("蓮", "れん"), ("根", "こん")],
        "masterKanji": ["蓮"],
    },
    {
        "anchor": "葡萄",
        "reading": "ぶどう",
        "en": "grape(s)",
        "ruby": [("葡", "ぶ"), ("萄", "どう")],
        "masterKanji": ["葡", "萄"],
    },
    {
        "anchor": "喧嘩",
        "reading": "けんか",
        "en": "quarrel / fight",
        "ruby": [("喧", "けん"), ("嘩", "か")],
        "masterKanji": ["喧", "嘩"],
    },
    {
        "anchor": "遥か",
        "reading": "はるか",
        "en": "far / distant",
        "ruby": [("遥", "はる"), ("か", "")],
        "masterKanji": ["遥"],
    },
    {
        "anchor": "龍神",
        "reading": "りゅうじん",
        "en": "dragon deity",
        "ruby": [("龍", "りゅう"), ("神", "じん")],
        "masterKanji": ["龍"],
    },
    {
        "anchor": "琉球",
        "reading": "りゅうきゅう",
        "en": "Ryukyu",
        "ruby": [("琉", "りゅう"), ("球", "きゅう")],
        "masterKanji": ["琉"],
    },
    {
        "anchor": "鷹派",
        "reading": "たかは",
        "en": "hawks (hardliners)",
        "ruby": [("鷹", "たか"), ("派", "は")],
        "masterKanji": ["鷹"],
    },
    {
        "anchor": "麒麟",
        "reading": "きりん",
        "en": "giraffe / qilin",
        "ruby": [("麒", "き"), ("麟", "りん")],
        "masterKanji": ["麒", "麟"],
    },
    {
        "anchor": "珊瑚礁",
        "reading": "さんごしょう",
        "en": "coral reef",
        "ruby": [("珊", "さん"), ("瑚", "ご"), ("礁", "しょう")],
        "masterKanji": ["珊", "瑚"],
    },
    {
        "anchor": "烏賊",
        "reading": "いか",
        "en": "squid",
        "ruby": [("烏賊", "いか")],
        "masterKanji": ["烏"],
    },
    {
        "anchor": "獅子",
        "reading": "しし",
        "en": "lion",
        "ruby": [("獅", "し"), ("子", "し")],
        "masterKanji": ["獅"],
    },
    {
        "anchor": "鯉幟",
        "reading": "こいのぼり",
        "en": "carp streamers",
        "ruby": [("鯉", "こい"), ("幟", "のぼり")],
        "masterKanji": ["鯉", "幟"],
    },
    {
        "anchor": "札幌",
        "reading": "さっぽろ",
        "en": "Sapporo",
        "ruby": [("札幌", "さっぽろ")],
        "masterKanji": ["幌"],
    },
    {
        "anchor": "函館",
        "reading": "はこだて",
        "en": "Hakodate",
        "ruby": [("函", "はこ"), ("館", "だて")],
        "masterKanji": ["函"],
    },
    {
        "anchor": "倶楽部",
        "reading": "くらぶ",
        "en": "club",
        "ruby": [("倶楽部", "くらぶ")],
        "masterKanji": ["倶"],
    },
    {
        "anchor": "噂話",
        "reading": "うわさばなし",
        "en": "gossip",
        "ruby": [("噂", "うわさ"), ("話", "ばなし")],
        "masterKanji": ["噂"],
    },
    {
        "anchor": "釘付け",
        "reading": "くぎづけ",
        "en": "nailed down / riveted",
        "ruby": [("釘", "くぎ"), ("付", "づ"), ("け", "")],
        "masterKanji": ["釘"],
    },
    {
        "anchor": "槍玉",
        "reading": "やりだま",
        "en": "target of attack",
        "ruby": [("槍", "やり"), ("玉", "だま")],
        "masterKanji": ["槍"],
    },
    {
        "anchor": "鷲掴み",
        "reading": "わしづかみ",
        "en": "rough grab",
        "ruby": [("鷲", "わし"), ("掴", "づか"), ("み", "")],
        "masterKanji": ["鷲", "掴"],
    },
    {
        "anchor": "頬杖",
        "reading": "ほおづえ",
        "en": "chin on hand",
        "ruby": [("頬", "ほお"), ("杖", "づえ")],
        "masterKanji": ["頬", "杖"],
    },
    {
        "anchor": "鎧兜",
        "reading": "よろいかぶと",
        "en": "armor and helmet",
        "ruby": [("鎧", "よろい"), ("兜", "かぶと")],
        "masterKanji": ["鎧", "兜"],
    },
    {
        "anchor": "柏餅",
        "reading": "かしわもち",
        "en": "oak-leaf rice cake",
        "ruby": [("柏", "かしわ"), ("餅", "もち")],
        "masterKanji": ["柏"],
    },
    {
        "anchor": "鯛焼き",
        "reading": "たいやき",
        "en": "tai-shaped cake",
        "ruby": [("鯛", "たい"), ("焼", "や"), ("き", "")],
        "masterKanji": ["鯛"],
    },
    {
        "anchor": "鴨居",
        "reading": "かもい",
        "en": "door lintel",
        "ruby": [("鴨", "かも"), ("居", "い")],
        "masterKanji": ["鴨"],
    },
    {
        "anchor": "蒲公英",
        "reading": "たんぽぽ",
        "en": "dandelion",
        "ruby": [("蒲公英", "たんぽぽ")],
        "masterKanji": ["蒲"],
    },
    {
        "anchor": "鰯雲",
        "reading": "いわしぐも",
        "en": "cirrocumulus clouds",
        "ruby": [("鰯", "いわし"), ("雲", "ぐも")],
        "masterKanji": ["鰯"],
    },
    {
        "anchor": "一匹狼",
        "reading": "いっぴきおおかみ",
        "en": "lone wolf",
        "ruby": [("一", "いっ"), ("匹", "ぴき"), ("狼", "おおかみ")],
        "masterKanji": ["狼"],
    },
    {
        "anchor": "雀躍",
        "reading": "じゃくやく",
        "en": "jumping for joy",
        "ruby": [("雀", "じゃく"), ("躍", "やく")],
        "masterKanji": ["雀"],
    },
    {
        "anchor": "蘇生",
        "reading": "そせい",
        "en": "resuscitation / revival",
        "ruby": [("蘇", "そ"), ("生", "せい")],
        "masterKanji": ["蘇"],
    },
    {
        "anchor": "剥離",
        "reading": "はくり",
        "en": "detachment / peeling away",
        "ruby": [("剥", "はく"), ("離", "り")],
        "masterKanji": ["剥"],
    },
    {
        "anchor": "叱責",
        "reading": "しっせき",
        "en": "reprimand",
        "ruby": [("叱", "しっ"), ("責", "せき")],
        "masterKanji": ["叱"],
    },
    {
        "anchor": "竣工",
        "reading": "しゅんこう",
        "en": "completion (construction)",
        "ruby": [("竣", "しゅん"), ("工", "こう")],
        "masterKanji": ["竣"],
    },
    {
        "anchor": "稀少",
        "reading": "きしょう",
        "en": "scarce / rare",
        "ruby": [("稀", "き"), ("少", "しょう")],
        "masterKanji": ["稀"],
    },
    {
        "anchor": "蒼白",
        "reading": "そうはく",
        "en": "pallor",
        "ruby": [("蒼", "そう"), ("白", "はく")],
        "masterKanji": ["蒼"],
    },
    {
        "anchor": "逢瀬",
        "reading": "おうせ",
        "en": "secret rendezvous",
        "ruby": [("逢", "おう"), ("瀬", "せ")],
        "masterKanji": ["逢"],
    },
    {
        "anchor": "磐石",
        "reading": "ばんじゃく",
        "en": "bedrock / unshakable",
        "ruby": [("磐", "ばん"), ("石", "じゃく")],
        "masterKanji": ["磐"],
    },
    {
        "anchor": "蘭学",
        "reading": "らんがく",
        "en": "Dutch Learning",
        "ruby": [("蘭", "らん"), ("学", "がく")],
        "masterKanji": ["蘭"],
    },
    {
        "anchor": "吾輩",
        "reading": "わがはい",
        "en": "I (literary)",
        "ruby": [("吾", "わが"), ("輩", "はい")],
        "masterKanji": ["吾"],
    },
    {
        "anchor": "菩薩",
        "reading": "ぼさつ",
        "en": "bodhisattva",
        "ruby": [("菩", "ぼ"), ("薩", "さつ")],
        "masterKanji": ["菩", "薩"],
    },
    {
        "anchor": "袈裟",
        "reading": "けさ",
        "en": "kasaya (Buddhist robe)",
        "ruby": [("袈", "け"), ("裟", "さ")],
        "masterKanji": ["袈", "裟"],
    },
    {
        "anchor": "涅槃",
        "reading": "ねはん",
        "en": "nirvana",
        "ruby": [("涅", "ね"), ("槃", "はん")],
        "masterKanji": ["涅", "槃"],
    },
    {
        "anchor": "躊躇",
        "reading": "ちゅうちょ",
        "en": "hesitation",
        "ruby": [("躊", "ちゅう"), ("躇", "ちょ")],
        "masterKanji": ["躊", "躇"],
    },
    {
        "anchor": "智慧",
        "reading": "ちえ",
        "en": "wisdom",
        "ruby": [("智", "ち"), ("慧", "え")],
        "masterKanji": ["智", "慧"],
    },
    # --- Part 2 ---
    {
        "anchor": "鞄",
        "reading": "かばん",
        "en": "bag / briefcase",
        "ruby": [("鞄", "かばん")],
        "masterKanji": ["鞄"],
    },
    {
        "anchor": "錆び",
        "reading": "さび",
        "en": "rust",
        "ruby": [("錆", "さ"), ("び", "")],
        "masterKanji": ["錆"],
    },
    {
        "anchor": "蛙",
        "reading": "かえる",
        "en": "frog",
        "ruby": [("蛙", "かえる")],
        "masterKanji": ["蛙"],
    },
    {
        "anchor": "蟻",
        "reading": "あり",
        "en": "ant",
        "ruby": [("蟻", "あり")],
        "masterKanji": ["蟻"],
    },
    {
        "anchor": "蟹",
        "reading": "かに",
        "en": "crab",
        "ruby": [("蟹", "かに")],
        "masterKanji": ["蟹"],
    },
    {
        "anchor": "鮭",
        "reading": "さけ",
        "en": "salmon",
        "ruby": [("鮭", "さけ")],
        "masterKanji": ["鮭"],
    },
    {
        "anchor": "栗",
        "reading": "くり",
        "en": "chestnut",
        "ruby": [("栗", "くり")],
        "masterKanji": ["栗"],
    },
    {
        "anchor": "笹",
        "reading": "ささ",
        "en": "bamboo grass",
        "ruby": [("笹", "ささ")],
        "masterKanji": ["笹"],
    },
    {
        "anchor": "杏",
        "reading": "あんず",
        "en": "apricot",
        "ruby": [("杏", "あんず")],
        "masterKanji": ["杏"],
    },
    {
        "anchor": "桐箱",
        "reading": "きりばこ",
        "en": "paulownia box",
        "ruby": [("桐", "きり"), ("箱", "ばこ")],
        "masterKanji": ["桐"],
    },
    {
        "anchor": "萩",
        "reading": "はぎ",
        "en": "bush clover",
        "ruby": [("萩", "はぎ")],
        "masterKanji": ["萩"],
    },
    {
        "anchor": "牡丹",
        "reading": "ぼたん",
        "en": "peony",
        "ruby": [("牡", "ぼ"), ("丹", "たん")],
        "masterKanji": ["牡"],
    },
    {
        "anchor": "猪",
        "reading": "いのしし",
        "en": "wild boar",
        "ruby": [("猪", "いのしし")],
        "masterKanji": ["猪"],
    },
    {
        "anchor": "鮎",
        "reading": "あゆ",
        "en": "sweetfish / ayu",
        "ruby": [("鮎", "あゆ")],
        "masterKanji": ["鮎"],
    },
    {
        "anchor": "繋がる",
        "reading": "つながる",
        "en": "to be connected",
        "ruby": [("繋", "つな"), ("が", ""), ("る", "")],
        "masterKanji": ["繋"],
    },
    {
        "anchor": "揃い",
        "reading": "そろい",
        "en": "matching set",
        "ruby": [("揃", "そろ"), ("い", "")],
        "masterKanji": ["揃"],
    },
    {
        "anchor": "叩く",
        "reading": "たたく",
        "en": "to hit / knock",
        "ruby": [("叩", "たた"), ("く", "")],
        "masterKanji": ["叩"],
    },
    {
        "anchor": "馴染む",
        "reading": "なじむ",
        "en": "to become familiar",
        "ruby": [("馴", "な"), ("染", "じ"), ("む", "")],
        "masterKanji": ["馴"],
    },
    {
        "anchor": "胡散臭い",
        "reading": "うさんくさい",
        "en": "fishy / suspicious",
        "ruby": [("胡", "う"), ("散", "さん"), ("臭", "くさ"), ("い", "")],
        "masterKanji": ["胡"],
    },
    {
        "anchor": "瑞穂",
        "reading": "みずほ",
        "en": "Mizuho / abundant rice",
        "ruby": [("瑞", "みず"), ("穂", "ほ")],
        "masterKanji": ["瑞"],
    },
    {
        "anchor": "聡明",
        "reading": "そうめい",
        "en": "clever / wise",
        "ruby": [("聡", "そう"), ("明", "めい")],
        "masterKanji": ["聡"],
    },
    {
        "anchor": "曙光",
        "reading": "しょこう",
        "en": "dawn light",
        "ruby": [("曙", "しょ"), ("光", "こう")],
        "masterKanji": ["曙"],
    },
    {
        "anchor": "欧州",
        "reading": "おうしゅう",
        "en": "Europe",
        "ruby": [("欧", "おう"), ("洲", "しゅう")],
        "masterKanji": ["洲"],
    },
    {
        "anchor": "四つ辻",
        "reading": "よつつじ",
        "en": "crossroads",
        "ruby": [("四", "よっ"), ("つ", ""), ("辻", "つじ")],
        "masterKanji": ["辻"],
    },
    {
        "anchor": "磯辺",
        "reading": "いそべ",
        "en": "rocky shore",
        "ruby": [("磯", "いそ"), ("辺", "べ")],
        "masterKanji": ["磯"],
    },
    {
        "anchor": "芦屋",
        "reading": "あしや",
        "en": "Ashiya",
        "ruby": [("芦", "あし"), ("屋", "や")],
        "masterKanji": ["芦"],
    },
    {
        "anchor": "橘",
        "reading": "たちばな",
        "en": "tachibana citrus",
        "ruby": [("橘", "たちばな")],
        "masterKanji": ["橘"],
    },
    {
        "anchor": "楠",
        "reading": "くすのき",
        "en": "camphor tree",
        "ruby": [("楠", "くすのき")],
        "masterKanji": ["楠"],
    },
    {
        "anchor": "鳳",
        "reading": "ほう",
        "en": "phoenix",
        "ruby": [("鳳", "ほう")],
        "masterKanji": ["鳳"],
    },
    {
        "anchor": "鞍",
        "reading": "くら",
        "en": "saddle",
        "ruby": [("鞍", "くら")],
        "masterKanji": ["鞍"],
    },
    {
        "anchor": "鞭",
        "reading": "むち",
        "en": "whip",
        "ruby": [("鞭", "むち")],
        "masterKanji": ["鞭"],
    },
    {
        "anchor": "斧",
        "reading": "おの",
        "en": "axe",
        "ruby": [("斧", "おの")],
        "masterKanji": ["斧"],
    },
    {
        "anchor": "鰐",
        "reading": "わに",
        "en": "crocodile",
        "ruby": [("鰐", "わに")],
        "masterKanji": ["鰐"],
    },
    {
        "anchor": "蝦夷",
        "reading": "えぞ",
        "en": "Ezo",
        "ruby": [("蝦", "え"), ("夷", "ぞ")],
        "masterKanji": ["蝦", "夷"],
    },
    {
        "anchor": "隼",
        "reading": "はやぶさ",
        "en": "peregrine falcon",
        "ruby": [("隼", "はやぶさ")],
        "masterKanji": ["隼"],
    },
    {
        "anchor": "庵",
        "reading": "いおり",
        "en": "hermitage",
        "ruby": [("庵", "いおり")],
        "masterKanji": ["庵"],
    },
    {
        "anchor": "讃美",
        "reading": "さんび",
        "en": "praise / hymn",
        "ruby": [("讃", "さん"), ("美", "び")],
        "masterKanji": ["讃"],
    },
    {
        "anchor": "復讐",
        "reading": "ふくしゅう",
        "en": "revenge",
        "ruby": [("復", "ふく"), ("讐", "しゅう")],
        "masterKanji": ["讐"],
    },
    {
        "anchor": "旭日",
        "reading": "きょくじつ",
        "en": "rising sun",
        "ruby": [("旭", "きょく"), ("日", "じつ")],
        "masterKanji": ["旭"],
    },
    {
        "anchor": "駿馬",
        "reading": "しゅんめ",
        "en": "swift horse",
        "ruby": [("駿", "しゅん"), ("馬", "め")],
        "masterKanji": ["駿"],
    },
    {
        "anchor": "深淵",
        "reading": "しんえん",
        "en": "abyss",
        "ruby": [("深", "しん"), ("淵", "えん")],
        "masterKanji": ["淵"],
    },
    {
        "anchor": "長篇",
        "reading": "ちょうへん",
        "en": "full-length work",
        "ruby": [("長", "ちょう"), ("篇", "へん")],
        "masterKanji": ["篇"],
    },
    {
        "anchor": "藝術",
        "reading": "げいじゅつ",
        "en": "the arts (old form)",
        "ruby": [("藝", "げい"), ("術", "じゅつ")],
        "masterKanji": ["藝"],
    },
    {
        "anchor": "萌芽",
        "reading": "ほうが",
        "en": "germination / beginnings",
        "ruby": [("萌", "ほう"), ("芽", "が")],
        "masterKanji": ["萌"],
    },
    {
        "anchor": "狡猾",
        "reading": "こうかつ",
        "en": "cunning / sly",
        "ruby": [("狡", "こう"), ("猾", "かつ")],
        "masterKanji": ["狡", "猾"],
    },
    {
        "anchor": "齟齬",
        "reading": "そご",
        "en": "discrepancy / mismatch",
        "ruby": [("齟", "そ"), ("齬", "ご")],
        "masterKanji": ["齟", "齬"],
    },
    {
        "anchor": "狼狽",
        "reading": "ろうばい",
        "en": "consternation / panic",
        "ruby": [("狼", "ろう"), ("狽", "ばい")],
        "masterKanji": ["狽"],
    },
    {
        "anchor": "梁",
        "reading": "はり",
        "en": "beam / girder",
        "ruby": [("梁", "はり")],
        "masterKanji": ["梁"],
    },
    {
        "anchor": "綾",
        "reading": "あや",
        "en": "twill / patterned weave",
        "ruby": [("綾", "あや")],
        "masterKanji": ["綾"],
    },
    {
        "anchor": "曰く",
        "reading": "いわく",
        "en": "according to",
        "ruby": [("曰", "いわ"), ("く", "")],
        "masterKanji": ["曰"],
    },
    # --- Part 3 ---
    {
        "anchor": "嘘",
        "reading": "うそ",
        "en": "lie",
        "ruby": [("嘘", "うそ")],
        "masterKanji": ["嘘"],
    },
    {
        "anchor": "蕎麦",
        "reading": "そば",
        "en": "soba / buckwheat noodles",
        "ruby": [("蕎麦", "そば")],
        "masterKanji": ["蕎"],
    },
    {
        "anchor": "琵琶",
        "reading": "びわ",
        "en": "biwa",
        "ruby": [("琵", "び"), ("琶", "わ")],
        "masterKanji": ["琵", "琶"],
    },
    {
        "anchor": "樽",
        "reading": "たる",
        "en": "barrel",
        "ruby": [("樽", "たる")],
        "masterKanji": ["樽"],
    },
    {
        "anchor": "鳩",
        "reading": "はと",
        "en": "pigeon",
        "ruby": [("鳩", "はと")],
        "masterKanji": ["鳩"],
    },
    {
        "anchor": "燕",
        "reading": "つばめ",
        "en": "swallow",
        "ruby": [("燕", "つばめ")],
        "masterKanji": ["燕"],
    },
    {
        "anchor": "椿",
        "reading": "つばき",
        "en": "camellia",
        "ruby": [("椿", "つばき")],
        "masterKanji": ["椿"],
    },
    {
        "anchor": "霞",
        "reading": "かすみ",
        "en": "haze / mist",
        "ruby": [("霞", "かすみ")],
        "masterKanji": ["霞"],
    },
    {
        "anchor": "湊",
        "reading": "みなと",
        "en": "port",
        "ruby": [("湊", "みなと")],
        "masterKanji": ["湊"],
    },
    {
        "anchor": "笠",
        "reading": "かさ",
        "en": "bamboo hat",
        "ruby": [("笠", "かさ")],
        "masterKanji": ["笠"],
    },
    {
        "anchor": "李",
        "reading": "すもも",
        "en": "Japanese plum",
        "ruby": [("李", "すもも")],
        "masterKanji": ["李"],
    },
    {
        "anchor": "桂",
        "reading": "かつら",
        "en": "katsura tree",
        "ruby": [("桂", "かつら")],
        "masterKanji": ["桂"],
    },
    {
        "anchor": "菱",
        "reading": "ひし",
        "en": "water chestnut / diamond shape",
        "ruby": [("菱", "ひし")],
        "masterKanji": ["菱"],
    },
    {
        "anchor": "翔る",
        "reading": "かける",
        "en": "to soar",
        "ruby": [("翔", "かけ"), ("る", "")],
        "masterKanji": ["翔"],
    },
    {
        "anchor": "篠",
        "reading": "しの",
        "en": "thin bamboo",
        "ruby": [("篠", "しの")],
        "masterKanji": ["篠"],
    },
    {
        "anchor": "紗",
        "reading": "しゃ",
        "en": "gauze",
        "ruby": [("紗", "しゃ")],
        "masterKanji": ["紗"],
    },
    {
        "anchor": "向日葵",
        "reading": "ひまわり",
        "en": "sunflower",
        "ruby": [("向日葵", "ひまわり")],
        "masterKanji": ["葵"],
    },
    {
        "anchor": "淀み",
        "reading": "よどみ",
        "en": "stagnation / eddy",
        "ruby": [("淀", "よど"), ("み", "")],
        "masterKanji": ["淀"],
    },
    {
        "anchor": "叶える",
        "reading": "かなえる",
        "en": "to grant (a wish)",
        "ruby": [("叶", "かな"), ("え", ""), ("る", "")],
        "masterKanji": ["叶"],
    },
    {
        "anchor": "捧げる",
        "reading": "ささげる",
        "en": "to devote / offer up",
        "ruby": [("捧", "ささ"), ("げ", ""), ("る", "")],
        "masterKanji": ["捧"],
    },
    {
        "anchor": "牽引",
        "reading": "けんいん",
        "en": "traction / towing",
        "ruby": [("牽", "けん"), ("引", "いん")],
        "masterKanji": ["牽"],
    },
    {
        "anchor": "毅然",
        "reading": "きぜん",
        "en": "resolute",
        "ruby": [("毅", "き"), ("然", "ぜん")],
        "masterKanji": ["毅"],
    },
    {
        "anchor": "哨戒",
        "reading": "しょうかい",
        "en": "patrol",
        "ruby": [("哨", "しょう"), ("戒", "かい")],
        "masterKanji": ["哨"],
    },
    {
        "anchor": "洛中",
        "reading": "らくちゅう",
        "en": "central Kyoto",
        "ruby": [("洛", "らく"), ("中", "ちゅう")],
        "masterKanji": ["洛"],
    },
    {
        "anchor": "砦",
        "reading": "とりで",
        "en": "fort",
        "ruby": [("砦", "とりで")],
        "masterKanji": ["砦"],
    },
    {
        "anchor": "樋",
        "reading": "とい",
        "en": "gutter / downspout",
        "ruby": [("樋", "とい")],
        "masterKanji": ["樋"],
    },
    {
        "anchor": "畠",
        "reading": "はたけ",
        "en": "dry field",
        "ruby": [("畠", "はたけ")],
        "masterKanji": ["畠"],
    },
    {
        "anchor": "杜",
        "reading": "もり",
        "en": "grove / woods",
        "ruby": [("杜", "もり")],
        "masterKanji": ["杜"],
    },
    {
        "anchor": "楊",
        "reading": "やなぎ",
        "en": "willow",
        "ruby": [("楊", "やなぎ")],
        "masterKanji": ["楊"],
    },
    {
        "anchor": "荻",
        "reading": "おぎ",
        "en": "reed",
        "ruby": [("荻", "おぎ")],
        "masterKanji": ["荻"],
    },
    {
        "anchor": "茅",
        "reading": "かや",
        "en": "miscanthus / thatch",
        "ruby": [("茅", "かや")],
        "masterKanji": ["茅"],
    },
    {
        "anchor": "苑",
        "reading": "その",
        "en": "garden / park",
        "ruby": [("苑", "その")],
        "masterKanji": ["苑"],
    },
    {
        "anchor": "棲む",
        "reading": "すむ",
        "en": "to roost / dwell",
        "ruby": [("棲", "す"), ("む", "")],
        "masterKanji": ["棲"],
    },
    {
        "anchor": "廻る",
        "reading": "まわる",
        "en": "to go around",
        "ruby": [("廻", "まわ"), ("る", "")],
        "masterKanji": ["廻"],
    },
    {
        "anchor": "樺",
        "reading": "かば",
        "en": "birch",
        "ruby": [("樺", "かば")],
        "masterKanji": ["樺"],
    },
    {
        "anchor": "粟",
        "reading": "あわ",
        "en": "foxtail millet",
        "ruby": [("粟", "あわ")],
        "masterKanji": ["粟"],
    },
    {
        "anchor": "巴",
        "reading": "ともえ",
        "en": "comma swirl / tomoe",
        "ruby": [("巴", "ともえ")],
        "masterKanji": ["巴"],
    },
    {
        "anchor": "諏訪",
        "reading": "すわ",
        "en": "Suwa",
        "ruby": [("諏訪", "すわ")],
        "masterKanji": ["諏"],
    },
    {
        "anchor": "嶺",
        "reading": "みね",
        "en": "mountain peak",
        "ruby": [("嶺", "みね")],
        "masterKanji": ["嶺"],
    },
    {
        "anchor": "隈",
        "reading": "くま",
        "en": "nook / shaded recess",
        "ruby": [("隈", "くま")],
        "masterKanji": ["隈"],
    },
    {
        "anchor": "播種",
        "reading": "はしゅ",
        "en": "sowing",
        "ruby": [("播", "は"), ("種", "しゅ")],
        "masterKanji": ["播"],
    },
    {
        "anchor": "窪地",
        "reading": "くぼち",
        "en": "hollow / depression",
        "ruby": [("窪", "くぼ"), ("地", "ち")],
        "masterKanji": ["窪"],
    },
    {
        "anchor": "叢",
        "reading": "くさむら",
        "en": "thicket",
        "ruby": [("叢", "くさむら")],
        "masterKanji": ["叢"],
    },
    {
        "anchor": "癌",
        "reading": "がん",
        "en": "cancer",
        "ruby": [("癌", "がん")],
        "masterKanji": ["癌"],
    },
    {
        "anchor": "祭祀",
        "reading": "さいし",
        "en": "ritual worship",
        "ruby": [("祭", "さい"), ("祀", "し")],
        "masterKanji": ["祀"],
    },
    {
        "anchor": "家禄",
        "reading": "かろく",
        "en": "family stipend",
        "ruby": [("家", "か"), ("禄", "ろく")],
        "masterKanji": ["禄"],
    },
    {
        "anchor": "公卿",
        "reading": "くぎょう",
        "en": "court nobles",
        "ruby": [("公", "く"), ("卿", "ぎょう")],
        "masterKanji": ["卿"],
    },
    {
        "anchor": "萬",
        "reading": "まん",
        "en": "ten thousand (old form)",
        "ruby": [("萬", "まん")],
        "masterKanji": ["萬"],
    },
    {
        "anchor": "國",
        "reading": "くに",
        "en": "country (old form)",
        "ruby": [("國", "くに")],
        "masterKanji": ["國"],
    },
    {
        "anchor": "於いて",
        "reading": "おいて",
        "en": "at / in (literary)",
        "ruby": [("於", "おい"), ("て", "")],
        "masterKanji": ["於"],
    },
    # --- Part 4 ---
    {
        "anchor": "絆",
        "reading": "きずな",
        "en": "bonds / ties",
        "ruby": [("絆", "きずな")],
        "masterKanji": ["絆"],
    },
    {
        "anchor": "狐",
        "reading": "きつね",
        "en": "fox",
        "ruby": [("狐", "きつね")],
        "masterKanji": ["狐"],
    },
    {
        "anchor": "苺",
        "reading": "いちご",
        "en": "strawberry",
        "ruby": [("苺", "いちご")],
        "masterKanji": ["苺"],
    },
    {
        "anchor": "柚",
        "reading": "ゆず",
        "en": "yuzu",
        "ruby": [("柚", "ゆず")],
        "masterKanji": ["柚"],
    },
    {
        "anchor": "楓",
        "reading": "かえで",
        "en": "maple",
        "ruby": [("楓", "かえで")],
        "masterKanji": ["楓"],
    },
    {
        "anchor": "噛む",
        "reading": "かむ",
        "en": "to chew / bite",
        "ruby": [("噛", "か"), ("む", "")],
        "masterKanji": ["噛"],
    },
    {
        "anchor": "貰う",
        "reading": "もらう",
        "en": "to receive",
        "ruby": [("貰", "もら"), ("う", "")],
        "masterKanji": ["貰"],
    },
    {
        "anchor": "喋る",
        "reading": "しゃべる",
        "en": "to chatter",
        "ruby": [("喋", "しゃべ"), ("る", "")],
        "masterKanji": ["喋"],
    },
    {
        "anchor": "騙す",
        "reading": "だます",
        "en": "to deceive",
        "ruby": [("騙", "だま"), ("す", "")],
        "masterKanji": ["騙"],
    },
    {
        "anchor": "殆ど",
        "reading": "ほとんど",
        "en": "almost",
        "ruby": [("殆", "ほとん"), ("ど", "")],
        "masterKanji": ["殆"],
    },
    {
        "anchor": "惚れる",
        "reading": "ほれる",
        "en": "to fall in love",
        "ruby": [("惚", "ほ"), ("れ", ""), ("る", "")],
        "masterKanji": ["惚"],
    },
    {
        "anchor": "纏める",
        "reading": "まとめる",
        "en": "to summarize / put together",
        "ruby": [("纏", "まと"), ("め", ""), ("る", "")],
        "masterKanji": ["纏"],
    },
    {
        "anchor": "溜まる",
        "reading": "たまる",
        "en": "to accumulate",
        "ruby": [("溜", "た"), ("ま", ""), ("る", "")],
        "masterKanji": ["溜"],
    },
    {
        "anchor": "吊り橋",
        "reading": "つりばし",
        "en": "suspension bridge",
        "ruby": [("吊", "つ"), ("り", ""), ("橋", "ばし")],
        "masterKanji": ["吊"],
    },
    {
        "anchor": "凌ぐ",
        "reading": "しのぐ",
        "en": "to endure / outdo",
        "ruby": [("凌", "しの"), ("ぐ", "")],
        "masterKanji": ["凌"],
    },
    {
        "anchor": "綴る",
        "reading": "つづる",
        "en": "to spell / bind together",
        "ruby": [("綴", "つづ"), ("る", "")],
        "masterKanji": ["綴"],
    },
    {
        "anchor": "甥",
        "reading": "おい",
        "en": "nephew",
        "ruby": [("甥", "おい")],
        "masterKanji": ["甥"],
    },
    {
        "anchor": "惣菜",
        "reading": "そうざい",
        "en": "prepared side dishes",
        "ruby": [("惣", "そう"), ("菜", "ざい")],
        "masterKanji": ["惣"],
    },
    {
        "anchor": "鵜飼い",
        "reading": "うかい",
        "en": "cormorant fishing",
        "ruby": [("鵜", "う"), ("飼", "か"), ("い", "")],
        "masterKanji": ["鵜"],
    },
    {
        "anchor": "榊",
        "reading": "さかき",
        "en": "sakaki tree",
        "ruby": [("榊", "さかき")],
        "masterKanji": ["榊"],
    },
    {
        "anchor": "榎",
        "reading": "えのき",
        "en": "hackberry / enoki",
        "ruby": [("榎", "えのき")],
        "masterKanji": ["榎"],
    },
    {
        "anchor": "樫",
        "reading": "かし",
        "en": "evergreen oak",
        "ruby": [("樫", "かし")],
        "masterKanji": ["樫"],
    },
    {
        "anchor": "鱗",
        "reading": "うろこ",
        "en": "scale (of a fish)",
        "ruby": [("鱗", "うろこ")],
        "masterKanji": ["鱗"],
    },
    {
        "anchor": "翠",
        "reading": "すい",
        "en": "jade green",
        "ruby": [("翠", "すい")],
        "masterKanji": ["翠"],
    },
    {
        "anchor": "塵",
        "reading": "ちり",
        "en": "dust",
        "ruby": [("塵", "ちり")],
        "masterKanji": ["塵"],
    },
    {
        "anchor": "庇",
        "reading": "ひさし",
        "en": "eaves / overhang",
        "ruby": [("庇", "ひさし")],
        "masterKanji": ["庇"],
    },
    {
        "anchor": "尖る",
        "reading": "とがる",
        "en": "to be pointed / sharp",
        "ruby": [("尖", "と"), ("が", ""), ("る", "")],
        "masterKanji": ["尖"],
    },
    {
        "anchor": "仇",
        "reading": "あだ",
        "en": "foe / grudge",
        "ruby": [("仇", "あだ")],
        "masterKanji": ["仇"],
    },
    {
        "anchor": "掻く",
        "reading": "かく",
        "en": "to scratch",
        "ruby": [("掻", "か"), ("く", "")],
        "masterKanji": ["掻"],
    },
    {
        "anchor": "跨ぐ",
        "reading": "またぐ",
        "en": "to straddle / step over",
        "ruby": [("跨", "また"), ("ぐ", "")],
        "masterKanji": ["跨"],
    },
    {
        "anchor": "凱旋",
        "reading": "がいせん",
        "en": "triumphal return",
        "ruby": [("凱", "がい"), ("旋", "せん")],
        "masterKanji": ["凱"],
    },
    {
        "anchor": "彗星",
        "reading": "すいせい",
        "en": "comet",
        "ruby": [("彗", "すい"), ("星", "せい")],
        "masterKanji": ["彗"],
    },
    {
        "anchor": "祇園",
        "reading": "ぎおん",
        "en": "Gion",
        "ruby": [("祇", "ぎ"), ("園", "おん")],
        "masterKanji": ["祇"],
    },
    {
        "anchor": "巫女",
        "reading": "みこ",
        "en": "shrine maiden",
        "ruby": [("巫", "み"), ("女", "こ")],
        "masterKanji": ["巫"],
    },
    {
        "anchor": "伽藍",
        "reading": "がらん",
        "en": "temple complex",
        "ruby": [("伽", "が"), ("藍", "らん")],
        "masterKanji": ["伽"],
    },
    {
        "anchor": "鸚鵡",
        "reading": "おうむ",
        "en": "parrot",
        "ruby": [("鸚", "おう"), ("鵡", "む")],
        "masterKanji": ["鸚", "鵡"],
    },
    {
        "anchor": "灘",
        "reading": "なだ",
        "en": "open sea / Nada",
        "ruby": [("灘", "なだ")],
        "masterKanji": ["灘"],
    },
    {
        "anchor": "憑く",
        "reading": "つく",
        "en": "to possess",
        "ruby": [("憑", "つ"), ("く", "")],
        "masterKanji": ["憑"],
    },
    {
        "anchor": "碧",
        "reading": "へき",
        "en": "blue-green",
        "ruby": [("碧", "へき")],
        "masterKanji": ["碧"],
    },
    {
        "anchor": "凛",
        "reading": "りん",
        "en": "stately / coldly elegant",
        "ruby": [("凛", "りん")],
        "masterKanji": ["凛"],
    },
    {
        "anchor": "燈",
        "reading": "とう",
        "en": "lamp (old form)",
        "ruby": [("燈", "とう")],
        "masterKanji": ["燈"],
    },
    {
        "anchor": "蝋",
        "reading": "ろう",
        "en": "wax",
        "ruby": [("蝋", "ろう")],
        "masterKanji": ["蝋"],
    },
    {
        "anchor": "填める",
        "reading": "はめる",
        "en": "to fit into / put on",
        "ruby": [("填", "は"), ("め", ""), ("る", "")],
        "masterKanji": ["填"],
    },
    {
        "anchor": "杵",
        "reading": "きね",
        "en": "wooden pestle",
        "ruby": [("杵", "きね")],
        "masterKanji": ["杵"],
    },
    {
        "anchor": "梓",
        "reading": "あずさ",
        "en": "catalpa",
        "ruby": [("梓", "あずさ")],
        "masterKanji": ["梓"],
    },
    {
        "anchor": "輿",
        "reading": "こし",
        "en": "palanquin",
        "ruby": [("輿", "こし")],
        "masterKanji": ["輿"],
    },
    {
        "anchor": "註",
        "reading": "ちゅう",
        "en": "footnote / annotation",
        "ruby": [("註", "ちゅう")],
        "masterKanji": ["註"],
    },
    {
        "anchor": "蒙る",
        "reading": "こうむる",
        "en": "to suffer / receive",
        "ruby": [("蒙", "こうむ"), ("る", "")],
        "masterKanji": ["蒙"],
    },
    {
        "anchor": "曳く",
        "reading": "ひく",
        "en": "to tow / drag",
        "ruby": [("曳", "ひ"), ("く", "")],
        "masterKanji": ["曳"],
    },
    {
        "anchor": "鵬",
        "reading": "ほう",
        "en": "peng / roc",
        "ruby": [("鵬", "ほう")],
        "masterKanji": ["鵬"],
    },
]


def load_master() -> dict[str, dict]:
    by_kanji: dict[str, dict] = {}
    with MASTER_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_kanji[row["kanji"]] = row
    return by_kanji


def soundtrack_for_part(part: int) -> tuple[str, int]:
    """Prefer beyond_joyo_{part}.mp3; else cycle available beyond_joyo_*.mp3; else Jr High."""
    series_rel = SERIES_SOUNDTRACK.format(part=part)
    series_path = ROOT / series_rel
    if series_path.is_file():
        rel = series_rel
        path = series_path
    else:
        available = sorted(
            ROOT.glob("audio/beyond_joyo_*.mp3"),
            key=lambda p: int(p.stem.rsplit("_", 1)[-1])
            if p.stem.rsplit("_", 1)[-1].isdigit()
            else 9999,
        )
        available = [p for p in available if p.stem.rsplit("_", 1)[-1].isdigit()]
        if available:
            path = available[(part - 1) % len(available)]
            rel = f"audio/{path.name}"
        else:
            slot = ((part - 1) % SOUNDTRACK_CYCLE) + 1
            rel = f"audio/jr_high_compounds_soundtrack_{slot}.mp3"
            path = ROOT / rel
            if not path.is_file():
                rel = SOUNDTRACK_FALLBACK
                path = ROOT / rel
    duration_ms = 1005035
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                str(path),
            ],
            text=True,
        ).strip()
        if out:
            duration_ms = int(float(out) * 1000)
    except Exception:
        pass
    return rel, duration_ms


def content_runtime_ms(n: int) -> int:
    if n < 1:
        return OPEN + REVIEW + FADE + BLACK
    if n == 1:
        return OPEN + LAST_BODY + REVIEW + FADE + BLACK
    return OPEN + (n - 1) * STEP + LAST_BODY + REVIEW + FADE + BLACK


def exhibition(is_finale: bool = False) -> dict:
    return {
        "artworkArrivalMs": 0,
        "artworkArrivalFadeMs": 1200,
        "artworkAloneMs": 0,
        "exhibitionBlackBeforeMs": 800,
        "compoundsPauseBeforeMs": 3200,
        "compoundsStepRevealMs": 1400,
        "compoundsFuriganaEnterDelayMs": 900,
        "compoundsFuriganaEnterMs": 2200,
        "compoundsFuriganaHoldMs": 3000,
        "compoundsFuriganaFadeMs": 2200,
        "compoundsNativeHoldMs": 2200,
        "compoundsReadingRevealMs": 1200,
        "compoundsReadingHoldMs": 1800,
        "compoundsEnRevealMs": 1200,
        "compoundsEnHoldMs": 3500,
        "compoundsEnFadeMs": 1400,
        "compoundsStepFadeMs": 1400,
        "compoundsFinalReviewHoldMs": 22000,
        "compoundsFinalFadeToBlackMs": 4000,
        # Party-kanji rewards: one restrained wave of gold flakes as the meaning
        # lands, drifting on through the hold. Identical for all twelve rewards.
        "compoundsRewardFlakeCount": 30,
        "compoundsRewardFlakeSpreadMs": 1600,
        "compoundsRewardFlakeDriftMinMs": 10000,
        "compoundsRewardFlakeDriftMaxMs": 16000,
        # biáng finale: the reward wave, a breath, a second gentler wave — then a
        # longer shower over the last of the kanji hold that keeps settling through
        # the fade to black while the crest appears, and fades out over the crest.
        "compoundsFinaleFlakeWaveCount": 40,
        "compoundsFinaleFlakeSecondWaveCount": 26,
        "compoundsFinaleFlakeWaveGapMs": 3200,
        "compoundsFinaleFlakeSpreadMs": 2200,
        "compoundsFinaleFlakeDriftMinMs": 9000,
        "compoundsFinaleFlakeDriftMaxMs": 15000,
        "compoundsFinaleConfettiLeadMs": 9000,
        "compoundsFinaleConfettiCount": 96,
        "compoundsFinaleConfettiSpreadMs": 5000,
        "compoundsFinaleConfettiFallMinMs": 4500,
        "compoundsFinaleConfettiFallMaxMs": 7500,
        "compoundsFinaleConfettiRestHoldMs": 4500,
        "compoundsFinaleConfettiFadeMs": 3500,
        "vocabArtworkExhaleMs": 2800,
        "exhibitTransitionMs": 0,
        "kenBurnsDurationMs": 1200000,
        "closingBlackBeforeMs": 800,
        "closingRevealMs": 4200 if is_finale else 3200,
        # The series ends here — let the crest sit noticeably longer than a part close.
        "closingHoldMs": 7000 if is_finale else 2800,
        "closingExhaleMs": 5000 if is_finale else 3500,
        "closingSilenceHoldMs": 0,
        "closingBlackAfterMs": 800,
        "closingFadeToBlackMs": 3500,
    }


def display() -> dict:
    return {
        "loop": False,
        "hideChrome": True,
        "family": "japaneseVocabulary",
        "showKeyword": False,
        "showKanji": False,
        "showEnglish": True,
        "exhibitProfile": "japaneseVocabulary",
        "verseMode": "sequential",
        "typography": "mobile-refine",
        "typographyStyle": "foundations",
        "bookendStyle": "galleryCrest",
        "cameraMotionScale": 1.0,
    }


def bookends() -> dict:
    """Silent gold 漢 crest after the final compound review fades to black."""
    return {
        "mode": "silentCrest",
        "closing": {
            "image": "images/gold_closing.png",
            "bookendSize": "small",
            "silentAfterSoundtrack": True,
        },
    }


def jp_html_for(ruby: list[tuple[str, str]]) -> str:
    if len(ruby) == 1 and ruby[0][1]:
        return ruby_word(ruby[0][0], ruby[0][1])
    return ruby_compound(ruby)


def enrich_entries(master: dict[str, dict]) -> list[dict]:
    # Curated opener + remaining regulars; party rewards scattered (parts 2, 4…);
    # 𰻞 (biáng) absolute finale.
    used_preview = {
        mk for raw in SERIES_ENTRIES for mk in raw["masterKanji"]
    }
    remaining = build_remaining_entries(used_preview)
    all_raw = assemble_series_entries(list(SERIES_ENTRIES), remaining)

    entries: list[dict] = []
    seen_master: set[str] = set()
    for i, raw in enumerate(all_raw, start=1):
        masters = raw["masterKanji"]
        for mk in masters:
            if mk not in master:
                raise SystemExit(f"{raw['anchor']}: master kanji {mk} not in kanji_master.csv")
            if master[mk].get("category") == "joyo":
                raise SystemExit(f"{raw['anchor']}: {mk} is joyo, not in beyond corpus")
            if mk in seen_master:
                raise SystemExit(
                    f"{raw['anchor']}: master kanji {mk} already introduced earlier"
                )
            seen_master.add(mk)
        primary = masters[0]
        row = master[primary]
        entry = {
            "kanji": "".join(masters),
            "anchor": raw["anchor"],
            "reading": raw["reading"],
            "en": raw["en"],
            "jpHtml": jp_html_for(raw["ruby"]),
            "heisigNumber": int(row["heisig_number"] or 0),
            "slug": row["slug"],
            "displayOrder": i,
            "masterKanji": masters,
            "part": (i - 1) // PART_SIZE + 1,
        }
        if raw.get("reward"):
            entry["reward"] = True
        if raw.get("celebration"):
            entry["celebration"] = raw["celebration"]
        if raw.get("finale"):
            entry["finale"] = True
        entries.append(entry)
    return entries


def write_jukugo_list(entries: list[dict]) -> None:
    COLLECTIONS.mkdir(parents=True, exist_ok=True)
    part_count = (len(entries) + PART_SIZE - 1) // PART_SIZE
    part_sizes = [
        len(entries[i : i + PART_SIZE]) for i in range(0, len(entries), PART_SIZE)
    ]
    doc = {
        "type": "jukugo",
        "scope": "beyond_joyo",
        "title": SERIES_TITLE,
        "titleJa": SERIES_TITLE_JA,
        "volume": 1,
        "source": "kml/data/kanji/kanji_master.csv",
        "corpus": "grade=H / heisig_extra / party_kanji (rewards + biáng finale)",
        "totalEntries": len(entries),
        "kanjiPerPart": PART_SIZE,
        "partCount": part_count,
        "partSizes": part_sizes,
        "anchorRule": "mostUsefulCompoundByFamiliarity",
        "notes": [
            "Beyond Jōyō Kanji Compounds (常用外漢字熟語).",
            "Source corpus exclusively from kanji_master.csv non-Jōyō.",
            "Parts 1–4: curated familiarity arc (rewards may land in parts 2+).",
            "Party-kanji rewards scattered through the series (parts 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18).",
            "Series finale: 𰻞 (biáng biáng noodles) with fireworks celebration.",
        ],
        "entries": entries,
    }
    JUKUGO.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {JUKUGO.relative_to(ROOT)}")


def build_part(part: int, batch: list[dict], part_count: int) -> dict:
    n = len(batch)
    first, last = batch[0], batch[-1]
    runtime = content_runtime_ms(n)
    soundtrack, soundtrack_ms = soundtrack_for_part(part)
    steps = []
    for e in batch:
        step = {
            "jp": e["anchor"],
            "reading": e["reading"],
            "en": e["en"],
            "jpHtml": e["jpHtml"],
            "meta": {
                "kanji": e["kanji"],
                "masterKanji": e["masterKanji"],
                "heisigNumber": e["heisigNumber"],
                "slug": e.get("slug"),
                "displayOrder": e["displayOrder"],
            },
        }
        if e.get("reward"):
            step["reward"] = True
            step["meta"]["reward"] = True
        if e.get("celebration"):
            step["celebration"] = e["celebration"]
            step["meta"]["celebration"] = e["celebration"]
        if e.get("finale"):
            step["meta"]["finale"] = True
        steps.append(step)
    cid = f"{SERIES_ID}_{part:02d}"
    is_finale_part = any(e.get("finale") for e in batch)
    notes = (
        f"Beyond Jōyō compounds Volume 1 Part {part}/{part_count}: "
        f"{n} compounds ({first['anchor']}→{last['anchor']}), "
        "from kanji_master.csv non-Jōyō corpus. "
        "No individual kanji showcase, no scenic images. Vocabulary typography. "
    )
    if is_finale_part:
        notes += (
            "SERIES FINALE: ends with 𰻞 (biáng biáng noodles). Gold flakes in two "
            "waves as the meaning lands, then a longer shower over the last kanji "
            "hold that settles while the crest fades in and dims over it. Crest "
            "holds longer than a normal part close. "
        )
    elif any(e.get("reward") for e in batch):
        notes += (
            "Ends on a party-kanji reward: one restrained wave of gold flakes as the "
            "meaning lands, drifting on through the hold. "
        )
    notes += (
        "Ending: final compound review ~22s → 4s fade to black → gold 漢 crest. "
        f"Soundtrack: {soundtrack} (~{soundtrack_ms // 1000}s)."
    )
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": cid,
        "title": f"{SERIES_TITLE} — Part {part}",
        "titleJa": f"{SERIES_TITLE_JA} — 第{part}部",
        "notes": notes,
        "soundtrack": {"main": soundtrack},
        "bookends": bookends(),
        "exhibition": exhibition(is_finale=is_finale_part),
        "display": display(),
        "meta": {
            "series": SERIES_ID,
            "volume": 1,
            "curriculum": "beyond_joyo",
            "scope": "beyond_joyo",
            "titleJa": SERIES_TITLE_JA,
            "part": part,
            "partCount": part_count,
            "stage": "compounds",
            "format": "anchorCompoundsGrouped",
            "sceneCount": 1,
            "compoundCount": n,
            "kanjiRange": [first["kanji"], last["kanji"]],
            "anchorRange": [first["anchor"], last["anchor"]],
            "heisigRange": [first["heisigNumber"], last["heisigNumber"]],
            "sourceOrder": "familiarity",
            "soundtrackDurationMs": soundtrack_ms if n >= 50 else min(soundtrack_ms, runtime + 5000),
            "estimatedContentRuntimeMs": runtime,
            "timingNote": (
                f"{n} compounds ≈ {runtime / 1000:.0f}s "
                f"({int(runtime // 60000)}:{int(runtime % 60000) // 1000:02d}) "
                "including review+fade."
            ),
            "ending": "finalCompoundReviewThenGoldCrest",
            "anchorRule": "mostUsefulCompoundByFamiliarity",
            "jukugoList": "beyond_joyo_jukugo_list.json",
            "masterCsv": "kml/data/kanji/kanji_master.csv",
            "hasReward": any(e.get("reward") for e in batch),
            "isFinale": is_finale_part,
        },
        "scenes": [
            {
                "id": f"BJ_compounds_{part:02d}",
                "image": "images/black.png",
                "galleryCamera": {
                    "motion": "still",
                    "focus": "50% 50%",
                    "motionScale": 1.0,
                },
                "compounds": {"steps": steps},
            }
        ],
    }


def update_manifest(part_count: int) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = list(manifest["collections"])
    keep = [
        item
        for item in items
        if not str(item.get("id", "")).startswith(f"{SERIES_ID}_")
    ]
    new_entries = [
        {
            "id": f"{SERIES_ID}_{part:02d}",
            "title": f"{SERIES_TITLE} — Part {part}",
            "url": (
                f"./exhibition.html?collection={SERIES_ID}_{part:02d}"
                "&typography=mobile-refine&verseMode=sequential"
            ),
            "sceneCount": 1,
            "family": "japaneseVocabulary",
            "presentation": "exhibition",
            "notes": (
                f"Beyond Jōyō compounds (常用外漢字熟語) part {part}/{part_count}. "
                f"Soundtrack: {soundtrack_for_part(part)[0]}."
            ),
        }
        for part in range(1, part_count + 1)
    ]
    # Insert after post_elementary compounds blocks when present.
    insert_at = len(keep)
    for i, item in enumerate(keep):
        item_id = str(item.get("id", ""))
        if item_id.startswith("post_elementary_compounds"):
            insert_at = i + 1
    keep[insert_at:insert_at] = new_entries
    manifest["collections"] = keep
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"manifest: inserted {part_count} beyond_joyo compounds at index {insert_at}")


def main() -> int:
    if not MASTER_CSV.is_file():
        raise SystemExit(f"Missing master CSV: {MASTER_CSV}")
    master = load_master()
    entries = enrich_entries(master)
    write_jukugo_list(entries)

    part_count = (len(entries) + PART_SIZE - 1) // PART_SIZE
    for part in range(1, part_count + 1):
        start = (part - 1) * PART_SIZE
        batch = entries[start : start + PART_SIZE]
        collection = build_part(part, batch, part_count)
        path = write_collection_path(ROOT, collection["id"])
        path.write_text(
            json.dumps(collection, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            f"wrote {path.relative_to(ROOT)}: {len(batch)} "
            f"{batch[0]['anchor']}→{batch[-1]['anchor']}  "
            f"~{collection['meta']['estimatedContentRuntimeMs'] / 1000:.0f}s"
        )

    update_manifest(part_count)
    print(f"done: {part_count} part(s), {len(entries)} compounds (Volume 1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
