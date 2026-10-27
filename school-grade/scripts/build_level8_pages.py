#!/usr/bin/env python3
"""Write the ten 漢検8級 lesson pages and their compiled vocabulary pages.

Uses the 漢検9級 card layout. Output lives at kanken/level-8/.
The level entrance is written by kml/scripts/build_kanken_level_pages.py.
Word examples are taken only from kml/data/compounds/ and attached when the
reading match is mechanical. Anything uncertain is listed in VOCABULARY_REVIEW.md.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GRADE = REPO / "kanken/level-8"
FILM_DIR = REPO / "kml/tools/ambient/collections/grade_3"
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

# Names already used on 漢検9級, plus the classical radicals that first appear at 8級.
# A note is recorded when the card shows the in-character form, or when a second
# school name is common enough that the choice should be reviewed.
RADICALS = {
    **grade2.RADICALS,
    6: ("亅", "はねぼう", ""),
    14: ("冖", "わかんむり", ""),
    23: ("匸", "かくしがまえ", ""),
    28: ("厶", "む", ""),
    44: ("尸", "しかばね", ""),
    56: ("弋", "しきがまえ", ""),
    78: ("歹", "がつ", "かばねとも呼ばれます。"),
    104: ("疒", "やまいだれ", ""),
    105: ("癶", "はつがしら", ""),
    107: ("皮", "けがわ", ""),
    108: ("皿", "さら", ""),
    123: ("羊", "ひつじ", ""),
    143: ("血", "ち", ""),
    145: ("衣", "ころも", ""),
    151: ("豆", "まめ", ""),
    158: ("身", "み", ""),
    161: ("辰", "しんのたつ", ""),
    163: ("阝", "おおざと", "古典部首は邑です。都・部にある形は阝です。"),
    164: ("酉", "ひよみのとり", ""),
    170: ("阝", "こざとへん", "古典部首は阜です。院・階・陽にある形は阝です。"),
    172: ("隹", "ふるとり", ""),
    176: ("面", "めん", ""),
    209: ("鼻", "はな", ""),
}

# One existing study image from a character in that lesson.
HERO_CHOICES = {
    1: ("swim", "泳"),
    2: ("beach", "岸"),
    3: ("lake", "湖"),
    4: ("poem", "詩"),
    5: ("inn", "宿"),
    6: ("deep", "深"),
    7: ("courtyard", "庭"),
    8: ("waves", "波"),
    9: ("ice", "氷"),
    10: ("sheep", "羊"),
}
OVERVIEW_HERO = ("island", "島")

# Cross-filed compound headwords that the mechanical matcher accepts.
# Only these surfaces are shown. Other mechanical hits stay in the review.
CROSS_FILE_ALLOW = {
    ("主", "ぬし"): ("株主",),
    ("取", "シュ"): ("採取", "摂取"),
    ("重", "チョウ"): ("貴重", "慎重", "尊重", "重複"),
    ("相", "ショウ"): ("首相",),
    ("定", "ジョウ"): ("定規", "勘定"),
    ("笛", "テキ"): ("汽笛",),
    ("豆", "トウ"): ("豆腐", "納豆"),
    ("物", "モツ"): ("荷物", "貨物", "穀物", "禁物"),
    ("返", "かえ-る"): ("ひっくり返る", "若返る"),
    ("命", "ミョウ"): ("寿命",),
}

# Dictionary form of a 常用漢字表 reading that is not a compound headword.
# The snippet is an existing example sentence; an inflected sentence is noted.
SENTENCE_EXAMPLES = (
    {
        "kanji": "泳",
        "raw": "およ-ぐ",
        "surface": "泳ぐ",
        "reading": "およぐ",
        "snippet": "茨城の海で泳ぐのが好きです",
        "source": "kml/data/compounds/lesson_26.json",
        "form": "dictionary form",
    },
    {
        "kanji": "育",
        "raw": "そだ-てる",
        "surface": "育てる",
        "reading": "そだてる",
        "snippet": "農家は苗床で野菜を育てます",
        "source": "kml/data/compounds/lesson_13.json",
        "form": "sentence uses 育てます",
    },
    {
        "kanji": "温",
        "raw": "あたた-かい",
        "surface": "温かい",
        "reading": "あたたかい",
        "snippet": "冬には温かい服が必要です",
        "source": "kml/data/compounds/lesson_35.json",
        "form": "dictionary form",
    },
    {
        "kanji": "温",
        "raw": "あたた-まる",
        "surface": "温まる",
        "reading": "あたたまる",
        "snippet": "地面が温まります",
        "source": "kml/data/compounds/lesson_67.json",
        "form": "sentence uses 温まります",
    },
    {
        "kanji": "温",
        "raw": "あたた-める",
        "surface": "温める",
        "reading": "あたためる",
        "snippet": "火鉢のそばで手を温めました",
        "source": "kml/data/compounds/lesson_15.json",
        "form": "sentence uses 温めました",
    },
    {
        "kanji": "重",
        "raw": "かさ-ねる",
        "surface": "重ねる",
        "reading": "かさねる",
        "snippet": "年歳を重ねても学び続けます",
        "source": "kml/data/compounds/lesson_28.json",
        "form": "sentence uses 重ねても",
    },
    {
        "kanji": "調",
        "raw": "しら-べる",
        "surface": "調べる",
        "reading": "しらべる",
        "snippet": "わからない漢字は辞書で調べます",
        "source": "kml/data/compounds/lesson_18.json",
        "form": "sentence uses 調べます",
    },
    {
        "kanji": "転",
        "raw": "ころ-がす",
        "surface": "転がす",
        "reading": "ころがす",
        "snippet": "子供が、輪を転がして遊びます",
        "source": "kml/data/compounds/lesson_99.json",
        "form": "sentence uses 転がして",
    },
    {
        "kanji": "運",
        "raw": "はこ-ぶ",
        "surface": "運ぶ",
        "reading": "はこぶ",
        "snippet": "船で運んでいます",
        "source": "kml/data/compounds/lesson_106.json",
        "form": "sentence uses 運んでいます; the segment reads 運 as はこ. 常用漢字表 has only はこ-ぶ",
    },
    {
        "kanji": "育",
        "raw": "そだ-つ",
        "surface": "育つ",
        "reading": "そだつ",
        "snippet": "本を読んで育ちました",
        "source": "kml/data/compounds/lesson_30.json",
        "form": "育ちました is そだ-つ. そだ-てる would be 育てました",
    },
    {
        "kanji": "湖",
        "raw": "みずうみ",
        "surface": "湖",
        "reading": "みずうみ",
        "snippet": "月が湖に映ります",
        "source": "kml/data/compounds/lesson_01.json",
        "form": "the segment reads 湖 as みずうみ",
    },
    {
        "kanji": "始",
        "raw": "はじ-まる",
        "surface": "始まる",
        "reading": "はじまる",
        "snippet": "曲が始まります",
        "source": "kml/data/compounds/lesson_01.json",
        "form": "始まります is はじ-まる; the segment reads 始 as はじ. はじ-める would be 始めます",
    },
    {
        "kanji": "集",
        "raw": "あつ-まる",
        "surface": "集まる",
        "reading": "あつまる",
        "snippet": "会場に千人が集まりました",
        "source": "kml/data/compounds/lesson_02.json",
        "form": "集まりました is あつ-まる. あつ-める would be 集めました. つど-う would be 集う",
    },
    {
        "kanji": "助",
        "raw": "たす-かる",
        "surface": "助かる",
        "reading": "たすかる",
        "snippet": "全員が助かったのは奇跡です",
        "source": "kml/data/compounds/lesson_07.json",
        "form": "助かった is たす-かる; the segment reads 助 as たす. たす-ける would be 助けた",
    },
    {
        "kanji": "着",
        "raw": "き-る",
        "surface": "着る",
        "reading": "きる",
        "snippet": "厚いコートを着ます",
        "source": "kml/data/compounds/lesson_07.json",
        "form": "着ます is き-る; the segment reads 着 as き. き-せる would be 着せます",
    },
    {
        "kanji": "着",
        "raw": "つ-く",
        "surface": "着く",
        "reading": "つく",
        "snippet": "返事が昨日着きました",
        "source": "kml/data/compounds/lesson_100.json",
        "form": "着きました is つ-く; the segment reads 着 as つ",
    },
    {
        "kanji": "着",
        "raw": "つ-ける",
        "surface": "身に着ける",
        "reading": "みにつける",
        "snippet": "",
        "source": "JMdict, https://jisho.org/api/v1/search/words?keyword=身に着ける",
        "form": "JMdict marks 身に着ける（みにつける） as the spelling for “to wear; to put on”. 着 is つ, the 常用 reading つ-ける. Not in the KML compound files",
        "external": True,
    },
    {
        "kanji": "注",
        "raw": "そそ-ぐ",
        "surface": "注ぐ",
        "reading": "そそぐ",
        "snippet": "古い杯に酒を注ぎました",
        "source": "kml/data/compounds/lesson_66.json",
        "form": "注ぎました is そそ-ぐ. lesson_113.json also reads the segment 注 as そそ",
    },
    {
        "kanji": "世",
        "raw": "よ",
        "surface": "世の中",
        "reading": "よのなか",
        "snippet": "世の中は広いです",
        "source": "kml/data/compounds/lesson_02.json",
        "form": "recorded reading よのなか, so 世 is よ",
    },
    {
        "kanji": "館",
        "raw": "やかた",
        "surface": "館",
        "reading": "やかた",
        "snippet": "館の一室に並んでいます",
        "source": "kml/data/compounds/lesson_87.json",
        "form": "the segment reads 館 as やかた. The mansion sense; カン words such as 図書館 stay on the on reading",
    },
    {
        "kanji": "和",
        "raw": "なご-む",
        "surface": "和む",
        "reading": "なごむ",
        "snippet": "場が和みます",
        "source": "kml/data/compounds/lesson_120.json",
        "form": "和みます is なご-む; the segment reads 和 as なご. The full sentence is formal",
    },
    {
        "kanji": "流",
        "raw": "なが-れる",
        "surface": "流れる",
        "reading": "ながれる",
        "snippet": "畑の溝に、雨水が流れています",
        "source": "kml/data/compounds/lesson_99.json",
        "form": "sentence uses 流れています",
    },
    {
        "kanji": "和",
        "raw": "やわ-らぐ",
        "surface": "和らぐ",
        "reading": "やわらぐ",
        "snippet": "礼の言葉に、気持ちが和らぎました",
        "source": "kml/data/compounds/lesson_102.json",
        "form": "sentence uses 和らぎました",
    },
)

# In the compound files, but not shown. A different reading, or not a learner example.
HELD_BACK = (
    "悪 オ: 嫌悪（けんお）, 憎悪（ぞうお）. Real words, past this level.",
    "歯 シ: 臼歯（きゅうし）. A specialist word. 歯科 is not in the compound files.",
    "波 ハ: 波及（はきゅう） only. Abstract, and the only headword.",
    "鼻 ビ: 鼻孔（びこう） only.",
    "役 エキ: 懲役（ちょうえき） only.",
    "有 ウ: 未曽有（みぞう） only.",
    "落 おちる: 腑に落ちる（ふにおちる） only. 腑 is not a learner word.",
    "取 シュ also has 奪取, 拐取, 搾取, 取捨選択, 未成年者拐取. Those were not used.",
    "相 ショウ also has 丞相, 宰相, 蔵相. 首相 is the learner word.",
    "重 チョウ also has 荘重, 鄭重. Those were not used.",
    "着 つける: KML’s only sentence is 舟を岸に着けました (lesson_90.json), “bring a boat alongside”. The card shows 身に着ける instead.",
)

# A different 常用漢字表 reading of the same character already has a headword.
RELATED_NOT_SAME = (
    "開 ひらける: 開く（ひらく） is the other kun.",
    "起 おこる, おこす: 起きる（おきる） and 早起き（はやおき）.",
    "苦 くるしむ, くるしめる: 苦しい（くるしい）. にがる: 苦い（にがい）.",
    "係 かかる: 係（かかり） and 係わる（かかわる）.",
    "向 むける, むこう: 向く（むく） and 向かう（むかう）.",
    "始 はじめる is already shown. はじまる is now 始まる, from its own sentence.",
    "次 つぐ: 次（つぎ）.",
    "受 うかる: 受ける（うける）.",
    "集 あつめる is already shown. あつまる is now 集まる, from its own sentence.",
    "住 すまう: 住む（すむ）.",
    "宿 やどる, やどす: 宿（やど）.",
    "助 たすける: 助け合い（たすけあい） is not たすける. たすかる is now 助かる.",
    "乗 のせる: 乗る（のる）.",
    "植 うわる: 植える（うえる）.",
    "進 すすめる: 進む（すすむ）.",
    "整 ととのえる: 整う（ととのう）.",
    "速 はやめる, はやまる: 速い（はやい）.",
    "代 かわる, かえる: 代わり（かわり） and 代る（かわる）.",
    "着 きせる: 着る is now shown from lesson_07.json. きせる was not copied onto it.",
    "定 さだめる, さだまる, さだか: 品定め（しなさだめ） uses さだめ, not these three.",
    "動 うごかす: 動く（うごく）.",
    "表 あらわれる: 表す（あらわす）.",
    "返 かえる is now shown; 返す（かえす） is the other kun.",
    "味 あじわう: 味（あじ）.",
    "問 とう: 問い（とい）.",
    "落 おちる: 落とし穴 and 見落とす use おとす, not おちる.",
)

# Card English. Each part is an exact KANJIDIC2 gloss, the Heisig keyword, or a paraphrase.
# show_heisig keeps the separate “(Heisig: …)” line. steve marks a choice that is not a straight gloss.
MEANING_CHOICES = {
    "院": {
        "parts": (("institution", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “institution”. The first gloss “Inst.” is that word abbreviated. Heisig “institution” is the same gloss, so it is not repeated. Temple and school stay off the card.",
    },
    "感": {
        "parts": (("feeling", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “feeling”. Heisig “feeling” is that gloss.",
    },
    "漢": {
        "parts": (("China", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “China”. “Sino-” is the same prefix sense, so it is not a second line. Heisig “china” matches this gloss.",
    },
    "起": {
        "parts": (("get up", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “get up”. “rouse” and “wake up” are the same family. Heisig “wake up” is not repeated.",
    },
    "去": {
        "parts": (("leave", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “leave”.",
    },
    "研": {
        "parts": (("polish", "kanjidic"), ("study", "paraphrase")),
        "show_heisig": False,
        "steve": False,
        "note": "“polish” is a KANJIDIC gloss. “study” shortens the gloss “study of”. Heisig “sharpen” is the polish sense and is not a second card line.",
    },
    "主": {
        "parts": (("master", "kanjidic"), ("main", "paraphrase")),
        "show_heisig": False,
        "steve": False,
        "note": "“master” is a KANJIDIC gloss and the Heisig keyword, so the Heisig line is not repeated. “main” shortens “main thing”.",
    },
    "章": {
        "parts": (("chapter", "kanjidic"), ("badge", "kanjidic")),
        "show_heisig": False,
        "steve": False,
        "note": "Both are KANJIDIC glosses. Heisig “chapter” is the first, so it is not repeated. Composition, poem, and design stay off the card.",
    },
    "相": {
        "parts": (("mutual", "kanjidic"), ("minister", "paraphrase")),
        "show_heisig": False,
        "steve": False,
        "note": "“mutual” is a KANJIDIC gloss and the Heisig keyword. “minister” shortens “minister of state”.",
    },
    "対": {
        "parts": (("opposite", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “opposite”. Heisig “opposite” is that gloss.",
    },
    "着": {
        "parts": (("wear", "kanjidic"), ("arrive", "kanjidic")),
        "show_heisig": False,
        "steve": False,
        "note": "Both are KANJIDIC glosses. Heisig “wear” is the first, so it is not repeated. The counter for suits stays off the card.",
    },
    "悲": {
        "parts": (("sad", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “sad”. Heisig “sad” is that gloss.",
    },
    "氷": {
        "parts": (("ice", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “ice”. Heisig “ice” is that gloss. “icicle” was the first gloss and is narrower.",
    },
    "平": {
        "parts": (("flat", "kanjidic"), ("peace", "kanjidic")),
        "show_heisig": False,
        "steve": False,
        "note": "Both are KANJIDIC glosses. Heisig “flat” is the first, so it is not repeated.",
    },
    "放": {
        "parts": (("release", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “release”, the same family as “set free” and the Heisig keyword. The fire/shoot glosses stay off the card.",
    },
    "役": {
        "parts": (("duty", "kanjidic"), ("role", "kanjidic")),
        "show_heisig": False,
        "steve": False,
        "note": "Both are KANJIDIC glosses. Heisig “role” is the second, so it is not repeated.",
    },
    "礼": {
        "parts": (("thanks", "kanjidic"), ("ceremony", "kanjidic")),
        "show_heisig": False,
        "steve": False,
        "note": "Both are KANJIDIC glosses. Heisig “thanks” is the first of these, so it is not repeated. “salute” and “bow” stay off the card.",
    },
    "育": {
        "parts": (("raise", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “raise”. Heisig “nurture” is not a gloss and is not shown as the meaning.",
    },
    "階": {
        "parts": (("storey", "kanjidic"), ("stair", "kanjidic")),
        "show_heisig": False,
        "steve": False,
        "note": "Both are KANJIDIC glosses. Heisig “floor” is the storey sense in another dialect and is not a gloss, so it was not substituted and is not shown.",
    },
    "曲": {
        "parts": (("bend", "kanjidic"), ("music", "kanjidic")),
        "show_heisig": False,
        "steve": False,
        "note": "Both are KANJIDIC glosses. Heisig “musical composition” is the music sense, so it is not repeated.",
    },
    "君": {
        "parts": (("you", "kanjidic"), ("name suffix", "paraphrase")),
        "show_heisig": False,
        "steve": False,
        "note": "“you” is a KANJIDIC gloss. “name suffix” shortens “male name suffix”. “ruler” and Heisig “lord” stay off the card.",
    },
    "号": {
        "parts": (("number", "kanjidic"), ("title", "kanjidic")),
        "show_heisig": False,
        "steve": False,
        "note": "Both are KANJIDIC glosses, for 番号 and a title. “nickname” and Heisig “designation” stay off the card.",
    },
    "祭": {
        "parts": (("festival", "heisig"),),
        "show_heisig": False,
        "steve": False,
        "note": "Heisig keyword, not a KANJIDIC gloss. The glosses are “ritual”, “offer prayers”, and “celebrate”. “festival” is the learner’s noun for 祭り. The Heisig line is not repeated.",
    },
    "商": {
        "parts": (("merchant", "kanjidic"), ("deal", "paraphrase")),
        "show_heisig": False,
        "steve": False,
        "note": "“merchant” is a KANJIDIC gloss. “deal” shortens “make a deal” and matches the Heisig keyword, so the Heisig line is not repeated.",
    },
    "申": {
        "parts": (("say humbly", "paraphrase"),),
        "show_heisig": True,
        "steve": False,
        "note": "Editorial paraphrase of the KANJIDIC gloss “have the honor to”. “declare” on the Heisig line is not a gloss. The zodiac glosses stay off the card.",
    },
    "送": {
        "parts": (("send", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “send”. Heisig “send off” is the same sense and did not match the gloss string, so it is not shown.",
    },
    "住": {
        "parts": (("live", "kanjidic"),),
        "show_heisig": False,
        "steve": False,
        "note": "KANJIDIC gloss “live”. Heisig “dwelling” is the noun and is not a gloss.",
    },
    "第": {
        "parts": (("number", "paraphrase"),),
        "show_heisig": True,
        "steve": False,
        "note": "Editorial paraphrase of the label “No.”, for 第一. It is not the gloss “residence”, and it is not 数. Heisig “ordinal number” stays on its own line because it is not a gloss.",
    },
    "様": {
        "parts": (("way", "kanjidic"), ("polite suffix", "kanjidic")),
        "show_heisig": False,
        "steve": False,
        "note": "Both are KANJIDIC glosses. “Esq.” was the first gloss. Heisig “formal title” aligns with “polite suffix” and is not repeated.",
    },
    "軽": {
        "parts": (("light in weight", "paraphrase"),),
        "show_heisig": False,
        "steve": False,
        "note": "Editorial wording, not a KANJIDIC2 gloss. The glosses are “lightly”, “trifling”, and “unimportant”, and none of them says weight, so “light” alone can be read as illumination. “light in weight” states the 軽い sense. Heisig’s keyword is “light weight”; that separate line is omitted because it repeats this wording.",
    },
}

# 着 only. 10級 and 9級 do not teach 着, and their cards stay on the KANJIDIC2 classical radical.
RADICAL_EXCEPTIONS = {
    "着": ("羊", "ひつじ", "着の部首は羊（ひつじ）にしました。KANJIDIC2 の古典部首は目（め）です。"),
}

LEVEL_PAGE = "./"
NEXT_LEVEL = "../level-7/"
LESSON_COUNT = 10


def film_cuts() -> list[list[str]]:
    cuts = []
    for number in range(1, LESSON_COUNT + 1):
        path = FILM_DIR / f"grade_3_compounds_school_{number:02d}.json"
        seen: list[str] = []
        for scene in json.loads(path.read_text(encoding="utf-8"))["scenes"]:
            kanji = scene.get("kanji")
            if kanji and len(kanji) == 1 and kanji not in seen:
                seen.append(kanji)
        cuts.append(seen)
    if len(cuts) != LESSON_COUNT or any(len(cut) != 20 for cut in cuts):
        raise SystemExit("Grade 3 film cuts are not ten lessons of 20")
    return cuts


def load_level() -> tuple[list[dict], dict]:
    import csv

    joyo = {}
    with JOYO.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            joyo[row["kanji"]] = row
    records = [
        record
        for record in json.loads(INDEX.read_text(encoding="utf-8"))["characters"]
        if record["introducedAt"] == "8"
    ]
    if len(records) != 200:
        raise SystemExit(f"漢検8級 has {len(records)} characters")
    records.sort(key=lambda record: int(joyo[record["kanji"]]["joyo_index"]))
    cuts = film_cuts()
    got = [record["kanji"] for record in records]
    if [got[i : i + 20] for i in range(0, 200, 20)] != cuts:
        raise SystemExit("8級 order differs from the grade 3 熟語 film cuts")
    return records, joyo


def lesson_nav(number: int) -> str:
    left = (
        f'<a href="{LEVEL_PAGE}">← 漢検8級</a>'
        if number == 1
        else f'<a href="lesson-{number - 1:02d}.html">← 第{number - 1}課</a>'
    )
    right = (
        f'<a href="{NEXT_LEVEL}">漢検7級 →</a>'
        if number == LESSON_COUNT
        else f'<a href="lesson-{number + 1:02d}.html">第{number + 1}課 →</a>'
    )
    return f"""<div class="navbar">
  {left}
  <a href="{LEVEL_PAGE}">漢検8級</a>
  {right}
</div>"""


def review_block() -> str:
    return """
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLTQM6H4rynCk" target="_blank" rel="noopener noreferrer">漢検8級の漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLc8WHOv0GQ7w" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 10 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLQ2GcmPXGpTQ" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 8 films</span></a>
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
<p class="school-kicker" lang="ja">漢検8級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学3年生で習う200字</p>
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
    text = grade2.page_head(title, f"漢検8級レベルの漢字。小学3年生で習う200字のうち、第{number}課。")
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
  <a href="{LEVEL_PAGE}">漢検8級</a>
</div>
<p class="school-kicker" lang="ja">漢検8級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学3年生で習う200字</p>
<h1 class="school-title">{esc(title)}</h1>
{grade2.furigana_bar()}
<nav class="anchor-list">
{anchors}
</nav>
{chr(10).join(articles)}
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="{LEVEL_PAGE}">漢検8級</a>
</div>
{notice}
{grade2.furigana_script()}
</body>
</html>
"""
    text = grade2.page_head(title, f"漢検8級 第{number}課の読み方とことば。小学3年生で習う200字。")
    (GRADE / f"lesson-{number:02d}-readings.html").write_text(text + body, encoding="utf-8")


REVIEW_APPENDIX = """
## 部首

The card uses the KANJIDIC2 classical radical of the joyo glyph, the same rule as 10級 and 9級. 着 is the one exception and is recorded above.

1. KANJIDIC2 classical radical of the joyo glyph (database 2026-074). This is the radical on the card, with the Japanese name used on the 10級 and 9級 cards. `school-grade/grade-1/LESSON_01_NOTES.md` records that choice.
2. The `radical` column of `kml/analytics/reference/joyo_kanji.csv`. For the characters below, that column matches the 部首 on the Japanese Wikipedia 常用漢字一覧, which says its 部首 follow 康熙字典, and for characters absent from 康熙字典 follow it with the 当用漢字表 as a guide. Checked rows: 医 164酉, 県 120糸, 号 141虍, 歯 211齒, 写 040宀, 州 047巛, 着 123羊, 予 152豕, 両 011入. The Cabinet 常用漢字表 itself lists 音訓 and examples. It does not print a radical number in the main table.

Same radical, different printed glyph. The card shows the form inside the character. This is the 9級 practice and is not a change of classification: 辵/辶, 艸/艹, 示/礻, 阜/阝, 邑/阝, 攴/攵, 戶/戸. 州 is Kangxi 47. The card prints 川 and the Wikipedia row prints 巛. Those are two ways of writing radical 47.

The glyph and the traditional character really do get different radicals. Left on the card as KANJIDIC2 classifies the joyo glyph:

- 医: card 匸（かくしがまえ）. Wikipedia / csv, from 醫: 酉.
- 県: card 目. Wikipedia / csv, from 縣: 糸. 三省堂例解小学漢字辞典, as ranked on benricho.org, puts 県 under 目, with the card.
- 号: card 口. Wikipedia / csv, from 號: 虍. The same elementary ranking puts 号 under 口.
- 歯: card 止. Wikipedia / csv, from 齒: 齒. Nelson’s classical number in KANJIDIC (`nelson_c` 211) also points at 齒.
- 写: card 冖. Wikipedia / csv, from 寫: 宀.
- 着: card now 羊. KANJIDIC2 classical of the joyo glyph is 目, radical 109. Wikipedia / csv and Nelson (`nelson_c` 123) say 羊. 著 is a different Kangxi case (艸) and was not used as a reason to change other cards.
- 予: card 亅（はねぼう）. Wikipedia / csv, from 豫: 豕. joyokanji.info also lists the joyo glyph 予 under 亅. Both placements are published.
- 両: card 一. Wikipedia / csv, from 兩: 入.
- 死: card 歹（がつ）. The csv column is also 歹. かばね is a second school name for the same radical, not a second classification.

Nelson numbers that disagree with both of the above are not used: 医 `nelson_c` 22, 県 42, 州 2.
"""


def write_review(entries: list[dict], meta: dict, heroes: dict[int, dict]) -> None:
    lines = [
        "# 漢検8級 vocabulary review",
        "",
        "Learner pages do not explain these choices.",
        "",
        f"KANJIDIC2 {meta['database']}, {meta['date']}.",
        "English on a card is the first KANJIDIC2 gloss, unless MEANING_CHOICES names a clearer gloss, two glosses, or a marked paraphrase.",
        "Heisig stays on its own line only when that keyword is not already the displayed meaning.",
        "Readings are the 常用漢字表 音訓. Parentheses are the table’s indented readings.",
        "Example words come from `kml/data/compounds/`. A word is attached when its reading",
        "matches that 音訓 at the edge of the word, including 連濁 and 促音.",
        "Compounds filed under another character are used only when listed in CROSS_FILE_ALLOW.",
        "A few bare readings use a dictionary form attested in an example sentence.",
        "The sentence is cited below. At most three examples are shown for each reading.",
        "",
        "The overview hero is 島 `kml/assets/studies/island.jpg`.",
        "Lesson covers are existing study images, one character from each lesson:",
        "",
    ]
    for number, (slug, kanji) in HERO_CHOICES.items():
        hero = heroes[number]
        note = ""
        if slug == "poem":
            note = " — 詩 and a poem are lettered on the board"
        elif slug == "inn":
            note = " — 宿 is lettered on the lantern and the sign"
        elif slug == "deep":
            note = " — a deep mountain lake; the character itself is not lettered"
        elif hero["width"] != 1672 or hero["height"] != 941:
            note = f" — native 16:9 at {hero['width']}×{hero['height']}"
        lines.append(f"- 第{number}課 {kanji} `kml/assets/studies/{slug}.jpg`{note}")
    lines.extend(["", "## Needs review", ""])
    for entry in entries:
        flags = []
        if entry["meaning_steve"]:
            flags.append("意味（要確認）: " + entry["meaning_note"])
        elif not entry["meaning_note"] and entry["meaning_kind"] != "equivalent":
            flags.append(
                f"Meaning “{entry['meaning']}”, Heisig “{entry['keyword']}” ({entry['meaning_kind']}: {entry['meaning_reason']})"
            )
        if entry["joyo_strokes"] != entry["strokes"]:
            flags.append(f"画数: KANJIDIC {entry['strokes']}, 常用漢字表 {entry['joyo_strokes']}")
        if entry["radical_note"] and entry["radical_source"] != "exception":
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
    lines.extend(["## Readings added or held back", ""])
    lines.append("Added on the page from a compound filed under another character, or from a cited sentence.")
    lines.append("Held back: present in `kml/data/compounds/`, not shown.")
    lines.append("")
    lines.append("Before this set, 104 readings had no example. Twelve of those now have one:")
    lines.append("はこぶ, そだつ, みずうみ, はじまる, あつまる, たすかる, きる, つく, そそぐ, よ, やかた, なごむ.")
    lines.append("身に着ける replaced 舟を岸に着けました for つける. That reading already had an example, so it is a thirteenth row in the list and not part of the drop.")
    lines.append("104 − 12 = 92 bare readings remain.")
    lines.append("")
    for item in HELD_BACK:
        lines.append(f"- {item}")
    lines.extend(["", "A different 常用漢字表 reading already has a headword. That headword was not copied onto the bare reading.", ""])
    for item in RELATED_NOT_SAME:
        lines.append(f"- {item}")
    lines.extend(["", "## English now on the cards", ""])
    lines.append("Listed characters are set in `MEANING_CHOICES` in `school-grade/scripts/build_level8_pages.py`.")
    lines.append("`kanjidic` is that exact KANJIDIC2 gloss. `heisig` is the keyword and not a gloss. `paraphrase` is editorial.")
    lines.append("An unlisted character still uses the first KANJIDIC2 gloss. Its Heisig line appears only when the keyword matches a later gloss.")
    lines.append("")
    for entry in entries:
        if not entry["meaning_note"]:
            continue
        shown = "Heisig line kept" if entry["show_heisig"] else "no separate Heisig line"
        lines.append(
            f"- {entry['kanji']}: “{entry['meaning']}” ({entry['meaning_sources']}; {shown}). {entry['meaning_note']}"
        )
    lines.extend(["", "## Approved", ""])
    lines.append("Steve approved these card meanings, including the paraphrases and the Heisig keyword used for 祭.")
    lines.append("着 on this level uses 羊（ひつじ）. The KANJIDIC2 classical radical remains 目（め）, number 109, and is not the card radical.")
    lines.append("Nelson’s `nelson_c` in that file is 123. `joyo_kanji.csv` and the Japanese Wikipedia 常用漢字一覧 (康熙字典) also say 羊.")
    lines.append("KML lesson 30 draws 着 as 羊 over 目. That drawing is a component breakdown, not a radical label.")
    lines.append("着 is not on the 10級 or 9級 cards, so those levels stay on the KANJIDIC2 classical radical. 医, 県, 号, 歯, 写, 予, and 両 stay there too.")
    lines.extend(["", "Left on the first KANJIDIC2 gloss:", ""])
    lines.append("- 球 “ball”. Heisig “sphere” stays on its own line.")
    lines.append("- 館 “building”. 期 “period”. 庫 “warehouse”. 事 “matter”. 想 “idea”.")
    lines.append("- 部 “section”. Heisig “department” is close to the gloss “dept”, so no Heisig line was added.")
    lines.append("- 予 “beforehand”. The gloss “I” is not the grade-3 sense.")
    lines.append("- 昔 “once upon a time”. “old times” is a later gloss. Heisig “long ago” is not a gloss and is not shown.")
    lines.extend(["", REVIEW_APPENDIX])
    REVIEW.write_text("\n".join(lines), encoding="utf-8")


def write_order(entries: list[dict], meta: dict) -> None:
    lessons = []
    for number in range(1, LESSON_COUNT + 1):
        group = [entry for entry in entries if entry["lesson"] == number]
        lessons.append({"lesson": number, "characters": [entry["kanji"] for entry in group]})
    payload = {
        "grade": 3,
        "level": "8",
        "count": 200,
        "order": "五十音順",
        "reference": "学年別漢字配当表 via joyo_kanji.csv, checked against the grade 3 熟語 film cuts",
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


def compounds_by_kanji(wanted: set[str]) -> dict[str, list[tuple[str, str]]]:
    """Every lesson compound whose surface contains the character, once."""
    import re

    found: dict[str, list[tuple[str, str]]] = {kanji: [] for kanji in wanted}
    seen: dict[str, set[tuple[str, str]]] = {kanji: set() for kanji in wanted}
    for path in sorted((REPO / "kml/data/compounds").glob("lesson_*.json")):
        if not re.fullmatch(r"lesson_\d+\.json", path.name):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for character in data.get("characters") or []:
            for compound in character.get("compounds") or []:
                surface = compound.get("surface") or ""
                reading = compound.get("reading") or ""
                if not surface or not reading:
                    continue
                for kanji in wanted:
                    if kanji not in surface or surface.count(kanji) != 1:
                        continue
                    key = (surface, reading)
                    if key in seen[kanji]:
                        continue
                    seen[kanji].add(key)
                    found[kanji].append(key)
    return found


def supplement_examples(entry: dict, pool: list[tuple[str, str]]) -> None:
    """Fill bare readings from allowed cross-filed headwords, then sentence forms."""
    kanji = entry["kanji"]
    notes = []
    for raw in list(entry["on"] + entry["kun"]):
        label = grade2.display_reading(raw)
        if label not in entry["bare"]:
            continue
        allowed = CROSS_FILE_ALLOW.get((kanji, raw))
        if not allowed:
            continue
        added = []
        for surface, reading in pool:
            if surface not in allowed:
                continue
            assigned = grade2.assign_compound(kanji, surface, reading, entry["on"], entry["kun"])
            if assigned is None or assigned[1] != raw:
                raise SystemExit(f"{surface}（{reading}） does not match {kanji} {label}")
            added.append((surface, reading, assigned[2]))
        if len(added) != len(allowed):
            raise SystemExit(f"{kanji} {label} found {[item[0] for item in added]}, expected {allowed}")
        order = {surface: index for index, surface in enumerate(allowed)}
        added.sort(key=lambda item: order[item[0]])
        entry["words"][raw] = [(surface, reading) for surface, reading, _how in added[: grade2.MAX_EXAMPLES]]
        entry["bare"].remove(label)
        for surface, reading, how in added[: grade2.MAX_EXAMPLES]:
            notes.append(
                f"Added {surface}（{reading}） for {label} from a compound filed under another character ({how})."
            )
    for item in SENTENCE_EXAMPLES:
        if item["kanji"] != kanji:
            continue
        if item["raw"] not in entry["on"] + entry["kun"]:
            raise SystemExit(f"{kanji} sentence example uses {item['raw']}, which is not a 常用漢字表 reading")
        label = grade2.display_reading(item["raw"])
        if label not in entry["bare"]:
            continue
        if item.get("external"):
            if not item["source"] or not item["form"]:
                raise SystemExit(f"{kanji} {label} needs a dictionary citation")
        else:
            source = REPO / item["source"]
            if item["snippet"] not in source.read_text(encoding="utf-8"):
                raise SystemExit(f"Missing sentence for {kanji} {label}: {item['snippet']}")
        entry["words"][item["raw"]] = [(item["surface"], item["reading"])]
        entry["bare"].remove(label)
        snippet = f" Snippet: {item['snippet']}。" if item["snippet"] else ""
        notes.append(
            f"Added {item['surface']}（{item['reading']}） for {label} from {item['source']} ({item['form']}).{snippet}"
        )
    entry["example_notes"] = notes


def prepare(records: list[dict], joyo: dict, kanjidic: dict, compounds: dict) -> list[dict]:
    wider = compounds_by_kanji({record["kanji"] for record in records})
    entries = []
    for index, record in enumerate(records):
        kanji = record["kanji"]
        info = kanjidic[kanji]
        if info["classical"] not in RADICALS:
            raise SystemExit(f"No radical name for {kanji} classical {info['classical']}")
        glyph, name, note = RADICALS[info["classical"]]
        radical_source = "kanjidic"
        if info["classical"] == 47 and not note:
            note = "康熙字典の47は川です。巛は同じ部の別の字形です。"
        if kanji in RADICAL_EXCEPTIONS:
            glyph, name, note = RADICAL_EXCEPTIONS[kanji]
            radical_source = "exception"
        lesson_no, anchor, keyword = grade2.keyword_from_page(record)
        compared = grade2.grade1.compare_meanings(keyword, info["glosses"])
        row = joyo[kanji]
        ons = grade2.split_joyo(row["on_kana"])
        kuns = grade2.split_joyo(row["kun_kana"])
        words, bare, unmatched, match_notes = grade2.attach_words(
            kanji, ons, kuns, compounds.get(kanji, [])
        )
        stroke_path = record["strokePage"].lstrip("/")
        lesson_path = record["lessonPage"].lstrip("/")
        if not (REPO / stroke_path).is_file():
            raise SystemExit(f"Missing stroke page for {kanji}")
        if not (REPO / lesson_path.split("#", 1)[0]).is_file():
            raise SystemExit(f"Missing KML lesson for {kanji}")
        hero_slug, hero_kanji = HERO_CHOICES[index // 20 + 1]
        if index % 20 == 0 and hero_kanji not in [item["kanji"] for item in records[index : index + 20]]:
            raise SystemExit(f"Cover {hero_kanji} is not in lesson {index // 20 + 1}")
        entries.append(
            {
                "kanji": kanji,
                "slug": record["slug"],
                "lesson": index // 20 + 1,
                "meaning": compared["standard"],
                "keyword": keyword,
                "meaning_kind": compared["kind"],
                "meaning_reason": compared["reason"],
                "meaning_sources": "kanjidic",
                "meaning_note": "",
                "meaning_steve": False,
                "show_heisig": compared["kind"] == "differs",
                "strokes": info["strokes"],
                "joyo_strokes": int(row["strokes"]),
                "radical": glyph,
                "radical_name": name,
                "radical_note": note,
                "radical_number": info["classical"],
                "radical_source": radical_source,
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
        supplement_examples(entries[-1], wider[kanji])
    return entries


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
        if source == "heisig" and text.lower() != entry["keyword"].lower():
            raise SystemExit(f"{entry['kanji']} Heisig meaning “{text}” is not the keyword")
    entry["meaning"] = "; ".join(text for text, _source in choice["parts"])
    entry["meaning_sources"] = "+".join(dict.fromkeys(source for _text, source in choice["parts"]))
    entry["meaning_note"] = choice["note"]
    entry["meaning_steve"] = choice["steve"]
    entry["show_heisig"] = choice["show_heisig"]


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
    records, joyo = load_level()
    kanjidic, meta = grade2.load_kanjidic({record["kanji"] for record in records})
    compounds = grade2.load_compounds()
    entries = prepare(records, joyo, kanjidic, compounds)
    heroes = {
        number: checked_hero(slug, kanji, entries, number)
        for number, (slug, kanji) in HERO_CHOICES.items()
    }
    overview = checked_hero(*OVERVIEW_HERO, entries, None)
    GRADE.mkdir(parents=True, exist_ok=True)
    for number in range(1, LESSON_COUNT + 1):
        group = [entry for entry in entries if entry["lesson"] == number]
        write_lesson(number, group, heroes[number], notice)
        write_compiled(number, group, notice)
        print(f"Wrote lesson {number}")
    write_order(entries, meta)
    write_heroes(heroes, overview)
    write_review(entries, meta, heroes)
    differs = [entry["kanji"] for entry in entries if entry["meaning_kind"] == "differs"]
    uncertain = [entry["kanji"] for entry in entries if entry["meaning_kind"] == "uncertain"]
    bare = sum(len(entry["bare"]) for entry in entries)
    print(f"meanings differ {len(differs)} uncertain {len(uncertain)} bare readings {bare}")
    print("validation passed")


if __name__ == "__main__":
    main()
