#!/usr/bin/env python3
"""Revise Grade 1 lesson 1 and write its compiled vocabulary page.

Does not modify lessons 2–4, the twenty earlier readings pages, or any Heisig lesson.
Vocabulary lives in CHARACTERS so a later lesson can use the same compiled-page template.
"""

from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LESSON = REPO / "school-grade/grade-1/lesson-01.html"
COMPILED = REPO / "school-grade/grade-1/lesson-01-readings.html"
DISCLAIMER = REPO / "school-grade/partials/disclaimer.html"
ENTRANCE = REPO / "school-grade/grade-1/index.html"
HERO = "../../kml/assets/studies/daybreak.jpg"
LESSON_DIR = REPO / "kml/contents/books/book_01/lessons"
COMPOUND_DIR = REPO / "kml/data/compounds"
KANJIDIC = REPO / "kml/kanjidic2.xml"
MASTER = REPO / "kml/data/kanji/kanji_master.csv"

# Kangxi number from KANJIDIC classical → character shown, conventional Japanese name.
# Names with more than one traditional label are flagged in RADICAL_NOTES.
RADICALS = {
    1: ("一", "いち"),
    5: ("乙", "おつ"),
    9: ("人", "ひと"),
    13: ("冂", "けいがまえ"),
    30: ("口", "くち"),
    39: ("子", "こ"),
    74: ("月", "つき"),
    84: ("气", "きがまえ"),
    86: ("火", "ひ"),
    94: ("犬", "いぬ"),
    96: ("玉", "たま"),
    116: ("穴", "あな"),
    140: ("艹", "くさかんむり"),
    147: ("見", "みる"),
    154: ("貝", "かい"),
    167: ("金", "かね"),
    173: ("雨", "あめ"),
    180: ("音", "おと"),
}

RADICAL_NOTES = {
    5: "九: KANJIDIC classical radical is 5 乙. nelson_c is 4 丿. The card uses the classical radical.",
    13: "円: radical 13 冂. The name is also given as まきがまえ or どうがまえ. Some dictionaries use 囗 instead.",
    96: "王 and 玉: Kangxi radical 96 is 玉, so 王 is listed under 玉（たま）.",
    140: "花: classical radical is 艸. The card shows the usual form 艹 and the name くさかんむり.",
}

# Heisig keyword is shown only for these. The keyword text is read from the KML lesson.
DIFFERENT = {"玉", "空", "月"}

# A word is (surface, reading) from that character's compound file,
# or (surface, reading, "added") when it is not in that file.
# panel_kun is None when the lesson card should not offer a 訓読み link.
CHARACTERS = [
    {
        "kanji": "一",
        "slug": "one",
        "panel_on": "イチ",
        "panel_kun": "ひと・ひとつ",
        "on": [{"label": "イチ", "words": [("一日", "いちにち"), ("一番", "いちばん")]}],
        "kun": [
            {"label": "ひと", "words": [("一人", "ひとり")]},
            {"label": "ひとつ", "words": [("一つ", "ひとつ")]},
        ],
        "skipped": ["一生", "一息", "イツ（均一などの音。一年生の例にはしない）"],
        "flags": [
            "一人（ひとり）は、一をひと、人をりと読む語です。小学校で教える形のままにしています。",
        ],
    },
    {
        "kanji": "右",
        "slug": "right",
        "panel_on": "ウ・ユウ",
        "panel_kun": "みぎ",
        "on": [
            {"label": "ウ", "words": [("右折", "うせつ")]},
            {"label": "ユウ", "words": [("左右", "さゆう")]},
        ],
        "kun": [{"label": "みぎ", "words": [("右", "みぎ"), ("右手", "みぎて")]}],
        "skipped": ["右翼（うよく。小学生向けではない）"],
        "flags": [
            "左右はサユウなので、右の音はユウです。ウの例にはしません。",
        ],
    },
    {
        "kanji": "雨",
        "slug": "rain",
        "panel_on": "ウ",
        "panel_kun": "あめ・あま",
        "on": [{"label": "ウ", "words": [("雨天", "うてん")]}],
        "kun": [
            {"label": "あめ", "words": [("雨", "あめ"), ("大雨", "おおあめ")]},
            {"label": "あま", "words": [("雨具", "あまぐ")]},
        ],
        "skipped": ["梅雨（つゆ。雨をウともあめとも読まない）"],
        "flags": [
            "音読みの例は雨天だけです。",
            "KANJIDIC の -さめ にあてはまることばは選んでいません。",
        ],
    },
    {
        "kanji": "円",
        "slug": "circle",
        "panel_on": "エン",
        "panel_kun": None,
        "on": [{"label": "エン", "words": [("円", "えん")]}],
        "kun": [],
        "skipped": [
            "円（まる）・円い（まるい）。丸・丸いが普通の表記",
            "まど・まどか・まろやか",
            "円周",
            "楕円",
        ],
        "flags": [
            "訓読みのパネルは出していません。まる・まるいの普通の漢字は丸です。円いは辞書にある別表記で、一年生の基本の書き方にはしません。",
        ],
    },
    {
        "kanji": "王",
        "slug": "king",
        "panel_on": "オウ",
        "panel_kun": None,
        "on": [{"label": "オウ", "words": [("王様", "おうさま"), ("王子", "おうじ"), ("女王", "じょおう")]}],
        "kun": [],
        "skipped": ["王国", "王者", "-ノウ（親王などの接尾。訓読みではない）"],
        "flags": ["訓読みはありません。訓のパネルは出していません。"],
    },
    {
        "kanji": "音",
        "slug": "sound",
        "panel_on": "オン",
        "panel_kun": "おと",
        "on": [{"label": "オン", "words": [("音楽", "おんがく"), ("発音", "はつおん")]}],
        "kun": [{"label": "おと", "words": [("音", "おと")]}],
        "skipped": ["騒音", "音声", "ね", "イン", "-ノン"],
        "flags": ["訓の例は音（おと）だけです。ね・イン・ノンは出していません。"],
    },
    {
        "kanji": "下",
        "slug": "below",
        "panel_on": "カ・ゲ",
        "panel_kun": "した・さがる・さげる",
        "on": [
            {"label": "カ", "words": [("地下", "ちか")]},
            {"label": "ゲ", "words": [("上下", "じょうげ", "added")]},
        ],
        "kun": [
            {"label": "した", "words": [("下", "した")]},
            {"label": "さがる", "words": [("下がる", "さがる")]},
            {"label": "さげる", "words": [("下げる", "さげる")]},
        ],
        "skipped": [
            "下手（へた）。ゲの例ではなく、語全体の特別な読み",
            "低下（ていか。カだが、地下より抽象的）",
            "しも・もと・くだる・おりる・おろす",
        ],
        "flags": [
            "下手（へた）は音読みゲの例にしていません。ゲは上下（じょうげ）です。上下は下の熟語一覧に無かったので足しました。",
            "訓はした・さがる・さげるにとどめています。",
        ],
    },
    {
        "kanji": "火",
        "slug": "fire",
        "panel_on": "カ",
        "panel_kun": "ひ",
        "on": [{"label": "カ", "words": [("火事", "かじ"), ("火山", "かざん"), ("火曜日", "かようび")]}],
        "kun": [{"label": "ひ", "words": [("火", "ひ", "added")]}],
        "skipped": ["出火", "火災"],
        "flags": [
            "熟語一覧の火はどれも音読みです。訓の火（ひ）は文字そのものの読みで、KANJIDIC と KML の訓にあります。",
            "ほ- にあてはまることばは選んでいません。",
        ],
    },
    {
        "kanji": "花",
        "slug": "flower",
        "panel_on": "カ",
        "panel_kun": "はな",
        "on": [{"label": "カ", "words": [("花瓶", "かびん")]}],
        "kun": [{"label": "はな", "words": [("花", "はな"), ("花火", "はなび"), ("花見", "はなみ")]}],
        "skipped": ["花嫁"],
        "flags": ["音読みの例は花瓶だけです。KANJIDIC の ケ は出していません。"],
    },
    {
        "kanji": "貝",
        "slug": "shellfish",
        "panel_on": "バイ",
        "panel_kun": "かい",
        "on": [{"label": "バイ", "words": []}],
        "kun": [{"label": "かい", "words": [("貝", "かい"), ("貝殻", "かいがら")]}],
        "skipped": ["巻貝（まきがい）", "二枚貝（にまいがい）", "貝類（かいるい）", "真珠貝（しんじゅがい）"],
        "flags": [
            "バイの例は出していません。熟語一覧の巻貝・貝類・真珠貝は、どれも貝をかいと読みます。",
        ],
    },
    {
        "kanji": "学",
        "slug": "study",
        "panel_on": "ガク",
        "panel_kun": "まなぶ",
        "on": [{"label": "ガク", "words": [("学校", "がっこう"), ("学生", "がくせい"), ("大学", "だいがく")]}],
        "kun": [{"label": "まなぶ", "words": [("学ぶ", "まなぶ", "added")]}],
        "skipped": ["文学", "留学"],
        "flags": ["熟語一覧に訓読みがありません。学ぶは KANJIDIC の訓 まな.ぶ そのものです。"],
    },
    {
        "kanji": "気",
        "slug": "spirit",
        "panel_on": "キ・ケ",
        "panel_kun": None,
        "on": [
            {"label": "キ", "words": [("天気", "てんき"), ("気持ち", "きもち"), ("空気", "くうき")]},
            {"label": "ケ", "words": []},
        ],
        "kun": [],
        "skipped": ["気分", "本気", "いき", "き（辞書の訓。学校の読みとしては出さない）"],
        "flags": [
            "訓読みのパネルは出していません。いき・きは辞書の訓で、一年生にふつうの読みとして出していません。",
            "ケの、一年生向けのことばは熟語一覧にありません。読みだけ出して、例は入れていません。",
        ],
    },
    {
        "kanji": "九",
        "slug": "nine",
        "panel_on": "キュウ・ク",
        "panel_kun": "ここのつ",
        "on": [
            {"label": "キュウ", "words": [("九人", "きゅうにん"), ("九回", "きゅうかい")]},
            {"label": "ク", "words": [("九月", "くがつ"), ("九時", "くじ", "added")]},
        ],
        "kun": [{"label": "ここのつ", "words": [("九つ", "ここのつ", "added")]}],
        "skipped": ["第九", "ここの（語幹。語としては出さない）"],
        "flags": [
            "訓の見出しは語幹のここのではなく、語の読みここのつです。例は九つ。",
            "九時（くじ）は時計の読みです。キュウジではありません。熟語一覧に無かったので足しました。",
        ],
    },
    {
        "kanji": "休",
        "slug": "rest",
        "panel_on": "キュウ",
        "panel_kun": "やす",
        "on": [{"label": "キュウ", "words": [("休暇", "きゅうか")]}],
        "kun": [{"label": "やす", "words": [("休む", "やすむ"), ("休み", "やすみ"), ("夏休み", "なつやすみ")]}],
        "skipped": ["昼休み"],
        "flags": ["音読みの例は休暇だけです。やす.まる・やす.める のことは選んでいません。"],
    },
    {
        "kanji": "玉",
        "slug": "ball",
        "panel_on": "ギョク",
        "panel_kun": "たま",
        "on": [{"label": "ギョク", "words": []}],
        "kun": [{"label": "たま", "words": [("水玉", "みずたま"), ("目玉", "めだま")]}],
        "skipped": ["玉子（たまご。普通の表記は卵）", "宝玉", "玉石"],
        "flags": [
            "ギョクの例は出していません。宝玉・玉石は一年生にはまれです。",
            "玉子は使いません。たまごの普通の漢字は卵です。",
        ],
    },
    {
        "kanji": "金",
        "slug": "gold",
        "panel_on": "キン",
        "panel_kun": "かね",
        "on": [{"label": "キン", "words": [("金曜日", "きんようび"), ("金魚", "きんぎょ")]}],
        "kun": [{"label": "かね", "words": [("お金", "おかね")]}],
        "skipped": ["料金", "現金"],
        "flags": ["訓の例はお金だけです。KANJIDIC の コン・ゴン・かな-・がね は出していません。"],
    },
    {
        "kanji": "空",
        "slug": "sky",
        "panel_on": "クウ",
        "panel_kun": "そら・あく",
        "on": [{"label": "クウ", "words": [("空気", "くうき"), ("空港", "くうこう")]}],
        "kun": [
            {"label": "そら", "words": [("空", "そら")]},
            {"label": "あく", "words": [("空く", "あく")]},
        ],
        "skipped": ["空く（すく。あくとまぎれるため）"],
        "flags": ["KANJIDIC の から・あける・むなしい などにあてはまることばは選んでいません。"],
    },
    {
        "kanji": "月",
        "slug": "moon",
        "panel_on": "ゲツ・ガツ",
        "panel_kun": "つき",
        "on": [
            {"label": "ゲツ", "words": [("月曜日", "げつようび"), ("今月", "こんげつ"), ("満月", "まんげつ")]},
            {"label": "ガツ", "words": [("正月", "しょうがつ", "added")]},
        ],
        "kun": [{"label": "つき", "words": [("月", "つき"), ("お月見", "おつきみ")]}],
        "skipped": ["月明かり"],
        "flags": ["正月は月の熟語一覧にありません。ガツのふつうの例として足しました。"],
    },
    {
        "kanji": "犬",
        "slug": "dog",
        "panel_on": "ケン",
        "panel_kun": "いぬ",
        "on": [{"label": "ケン", "words": [("番犬", "ばんけん")]}],
        "kun": [{"label": "いぬ", "words": [("犬", "いぬ"), ("子犬", "こいぬ"), ("犬小屋", "いぬごや")]}],
        "skipped": ["野犬"],
        "flags": ["音読みの例は番犬だけです。一年生にはまだ早いかもしれません。"],
    },
    {
        "kanji": "見",
        "slug": "see",
        "panel_on": "ケン",
        "panel_kun": "みる・みえる・みせる",
        "on": [{"label": "ケン", "words": [("見学", "けんがく"), ("発見", "はっけん")]}],
        "kun": [
            {"label": "みる", "words": [("見る", "みる")]},
            {"label": "みえる", "words": [("見える", "みえる")]},
            {"label": "みせる", "words": [("見せる", "みせる")]},
        ],
        "skipped": ["意見"],
        "flags": [],
    },
]


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def load_kanjidic(wanted: set[str]) -> tuple[dict, dict]:
    root = ET.parse(KANJIDIC).getroot()
    header = root.find("header")
    meta = {
        "database": header.findtext("database_version"),
        "date": header.findtext("date_of_creation"),
    }
    found = {}
    for char in root.findall("character"):
        literal = char.findtext("literal")
        if literal not in wanted or literal in found:
            continue
        misc = char.find("misc")
        classical = None
        nelson = None
        for rad in char.findall("radical/rad_value"):
            if rad.get("rad_type") == "classical":
                classical = int(rad.text)
            elif rad.get("rad_type") == "nelson_c":
                nelson = int(rad.text)
        strokes = int(misc.findtext("stroke_count"))
        glosses = []
        for meaning in char.findall("reading_meaning/rmgroup/meaning"):
            if meaning.get("m_lang") in (None, "", "en") and meaning.text:
                glosses.append(meaning.text.strip())
        found[literal] = {
            "strokes": strokes,
            "classical": classical,
            "nelson": nelson,
            "meaning": glosses[0],
        }
    missing = wanted - set(found)
    if missing:
        raise SystemExit(f"KANJIDIC2 missing {missing}")
    return found, meta


def load_entries() -> dict[str, dict]:
    """slug → lesson number, anchor id, Heisig keyword, from the live lesson HTML."""
    found = {}
    for path in sorted(LESSON_DIR.glob("lesson_*.html")):
        if not re.fullmatch(r"lesson_\d+\.html", path.name):
            continue
        lesson_no = int(path.stem.split("_")[1])
        text = path.read_text(encoding="utf-8")
        pos = 0
        while True:
            start = text.find('<section class="kanji-entry"', pos)
            if start < 0:
                break
            end = text.find("</section>", start)
            if end < 0:
                break
            block = text[start:end]
            slug = re.search(r'data-slug="([^"]+)"', block)
            anchor = re.search(r'\bid="([^"]+)"', block)
            keyword = re.search(r'<span class="kanji-keyword">(.*?)</span>', block, re.S)
            kanji = re.search(r'data-kanji="([^"]+)"', block)
            if slug and anchor and keyword and kanji:
                found.setdefault(slug.group(1), []).append(
                    {
                        "lesson": lesson_no,
                        "anchor": anchor.group(1),
                        "keyword": re.sub(r"\s+", " ", html.unescape(keyword.group(1))).strip(),
                        "kanji": kanji.group(1),
                    }
                )
            pos = end
    return found


def load_compounds(kanji: str) -> set[tuple[str, str]]:
    pool = set()
    for path in COMPOUND_DIR.glob("lesson_*.json"):
        if not re.fullmatch(r"lesson_\d+\.json", path.name):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for character in data.get("characters") or []:
            if character.get("kanji") != kanji:
                continue
            for compound in character.get("compounds") or []:
                pool.add((compound.get("surface") or "", compound.get("reading") or ""))
    return pool


def word_parts(item: tuple) -> tuple[str, str, bool]:
    surface, reading = item[0], item[1]
    added = len(item) > 2 and item[2] == "added"
    return surface, reading, added


def ruby(surface: str, reading: str) -> str:
    return f"<ruby>{esc(surface)}<rt>{esc(reading)}</rt></ruby>"


def word_list(words: list[tuple]) -> str:
    if not words:
        return ""
    lis = []
    for item in words:
        surface, reading, _added = word_parts(item)
        lis.append(
            "<li>"
            f'<p class="sg-word" lang="ja">{ruby(surface, reading)}</p>'
            f'<p class="sg-kana" lang="ja">{esc(reading)}</p>'
            "</li>"
        )
    return '<ul class="sg-words">\n' + "\n".join(lis) + "\n</ul>"


def reading_groups(groups: list[dict]) -> str:
    chunks = []
    for group in groups:
        bare = "" if group["words"] else ' class="sg-read-label sg-read-bare"'
        label_class = bare or ' class="sg-read-label"'
        chunks.append(
            f'<h4{label_class} lang="ja">{esc(group["label"])}</h4>\n' + word_list(group["words"])
        )
    return "\n".join(chunks)


def page_head(title: str, description: str, css_prefix: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="{esc(description)}">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Noto+Serif+JP&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css_prefix}kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="{css_prefix}school-grade/css/school-grade.css">
<script>
try {{
  if (localStorage.getItem("kml-compounds-furigana") === "off") {{
    document.documentElement.classList.add("furigana-off");
  }}
}} catch (err) {{}}
</script>
</head>
"""


def furigana_script() -> str:
    return """
<script>
(function () {
  var toggle = document.getElementById("furigana-toggle");
  if (!toggle) return;
  function on() { return !document.documentElement.classList.contains("furigana-off"); }
  function set(next) {
    document.documentElement.classList.toggle("furigana-off", !next);
    toggle.setAttribute("aria-pressed", next ? "true" : "false");
    toggle.setAttribute("aria-label", next ? "ふりがな オン" : "ふりがな オフ");
    try { localStorage.setItem("kml-compounds-furigana", next ? "on" : "off"); } catch (err) {}
  }
  toggle.addEventListener("click", function () { set(!on()); });
  set(on());
})();
</script>
"""


def disclaimer_html() -> str:
    text = DISCLAIMER.read_text(encoding="utf-8").strip()
    if "日本漢字能力検定協会" not in text:
        raise SystemExit(f"Disclaimer file is missing the required notice: {DISCLAIMER}")
    return text


def side_html(character: dict, side: str) -> str:
    groups = character[side]
    if not groups:
        return ""
    slug = character["slug"]
    kanji = character["kanji"]
    title = "音読み" if side == "on" else "訓読み"
    back = (
        f'<a class="sg-entry-back" href="lesson-01.html#kanji-{esc(slug)}">第1課の{esc(kanji)}</a>'
    )
    head = ""
    if side == "on":
        head = f'<h2 class="sg-entry-kanji" lang="ja">{esc(kanji)}</h2>\n    {back}'
    else:
        head = back
    return f"""<div class="sg-read-block" id="kanji-{esc(slug)}-{side}">
    {head}
    <h3 class="sg-side" lang="ja">{title}</h3>
    {reading_groups(groups)}
  </div>"""


def anchor_nav() -> str:
    links = "\n".join(
        f'<a href="#kanji-{esc(item["slug"])}">{esc(item["kanji"])}</a>' for item in CHARACTERS
    )
    return f'<nav class="anchor-list">\n{links}\n</nav>'


def furigana_bar() -> str:
    return """<div class="furigana-bar">
  <button type="button" class="furigana-toggle" id="furigana-toggle" aria-pressed="true" aria-label="ふりがな オン">
    ふりがな
    <span class="furigana-mark" aria-hidden="true"></span>
  </button>
</div>"""


def write_compiled(notice: str) -> None:
    entries = []
    for character in CHARACTERS:
        slug = character["slug"]
        entries.append(
            f'<article class="sg-entry" id="kanji-{esc(slug)}">\n'
            f"  {side_html(character, 'on')}\n"
            f"  {side_html(character, 'kun')}\n"
            "</article>"
        )
    body = f"""<body class="sg-readings sg-compiled" id="top">
<div class="navbar">
  <a href="lesson-01.html">← 第1課</a>
  <a href="./">小学1年生</a>
</div>
<p class="school-kicker" lang="ja">漢検10級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学1年生で習う80字</p>
<h1 class="school-title">第1課 — 読み方とことば</h1>
{furigana_bar()}
{anchor_nav()}
{chr(10).join(entries)}
<div class="navbar">
  <a href="lesson-01.html">← 第1課</a>
  <a href="./">小学1年生</a>
</div>
{notice}
{furigana_script()}
</body>
</html>
"""
    text = page_head(
        "第1課 — 読み方とことば",
        "小学1年生 第1課の読み方とことば。一から見まで。",
        "../../",
    )
    COMPILED.write_text(text + body, encoding="utf-8")


def write_lesson(cards: str, meta: dict, notice: str) -> None:
    review = """
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">復習</span></h2>
  <p>この学年の動画です。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLDqZ_saSB25k" target="_blank" rel="noopener noreferrer">1学年で学ぶ漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 2 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLUK4NyqFdNMw" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLYpgcBuk0PGg" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 4 films</span></a>
  </div>
</section>
"""
    body = f"""<body class="sg-lesson" id="top">
<div class="navbar">
  <a href="./">← 小学1年生</a>
  <a href="./">小学1年生</a>
  <a href="lesson-02.html">第2課 →</a>
</div>
<div class="lesson-art">
  <img src="{HERO}" alt="朝焼けの山里" width="1672" height="941">
</div>
<p class="school-kicker" lang="ja">漢検10級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学1年生で習う80字</p>
<h1 class="school-title">第1課 — 一 〜 見</h1>
<p class="sg-to-words"><a href="lesson-01-readings.html">読み方とことば</a></p>
<nav class="anchor-list">
<a href="#kanji-one">一</a>
<a href="#kanji-right">右</a>
<a href="#kanji-rain">雨</a>
<a href="#kanji-circle">円</a>
<a href="#kanji-king">王</a>
<a href="#kanji-sound">音</a>
<a href="#kanji-below">下</a>
<a href="#kanji-fire">火</a>
<a href="#kanji-flower">花</a>
<a href="#kanji-shellfish">貝</a>
<a href="#kanji-study">学</a>
<a href="#kanji-spirit">気</a>
<a href="#kanji-nine">九</a>
<a href="#kanji-rest">休</a>
<a href="#kanji-ball">玉</a>
<a href="#kanji-gold">金</a>
<a href="#kanji-sky">空</a>
<a href="#kanji-moon">月</a>
<a href="#kanji-dog">犬</a>
<a href="#kanji-see">見</a>
</nav>
{cards}
{review}
<div class="navbar">
  <a href="./">← 小学1年生</a>
  <a href="./">小学1年生</a>
  <a href="lesson-02.html">第2課 →</a>
</div>
<p class="school-footer-note">意味・画数・部首は KANJIDIC2（EDRDG、{esc(meta["database"])}、{esc(meta["date"])}）によります。</p>
{notice}
</body>
</html>
"""
    text = page_head(
        "第1課 — 一 〜 見",
        "漢検10級レベルの漢字。小学1年生で習う80字のうち、第1課。",
        "../../",
    )
    # Lesson page mixes English meanings, so keep the document language as Japanese
    # for the labels and mark English meanings with lang="en" on the element.
    LESSON.write_text(text + body, encoding="utf-8")


def card_html(character: dict, info: dict, entry: dict) -> str:
    kanji = character["kanji"]
    number = info["classical"]
    glyph, name = RADICALS[number]
    heisig = ""
    if kanji in DIFFERENT:
        heisig = f'\n  <p class="sg-heisig">(Heisig: {esc(entry["keyword"])})</p>'
    return f"""<article class="sg-card" id="kanji-{esc(character["slug"])}" data-kanji="{esc(kanji)}">
  <a class="sg-kanji-link" href="../../kml/tools/strokes/pages/{esc(character["slug"])}.html">
    <span class="sg-kanji" lang="ja">{esc(kanji)}</span>
  </a>
  <p class="sg-meaning" lang="en">{esc(info["meaning"])}</p>{heisig}
  <div class="sg-panels{"" if character["panel_kun"] else " sg-panels-single"}">
    <a class="sg-panel" href="lesson-01-readings.html#kanji-{esc(character["slug"])}-on">
      <span class="sg-panel-label" lang="ja">音読み</span>
      <span class="sg-panel-yomi" lang="ja">{esc(character["panel_on"])}</span>
    </a>{"" if not character["panel_kun"] else f'''
    <a class="sg-panel" href="lesson-01-readings.html#kanji-{esc(character["slug"])}-kun">
      <span class="sg-panel-label" lang="ja">訓読み</span>
      <span class="sg-panel-yomi" lang="ja">{esc(character["panel_kun"])}</span>
    </a>'''}
  </div>
  <p class="sg-facts">
    <span lang="ja">部首 <b>{esc(glyph)}</b>（{esc(name)}）</span>
    <span lang="ja">画数 <b>{info["strokes"]}</b></span>
  </p>
  <a class="sg-kml-link" href="../../kml/contents/books/book_01/lessons/lesson_{entry["lesson"]:02d}.html#{esc(entry["anchor"])}">KMLで詳しく見る</a>
</article>
"""


def write_notes(rows: list[dict], meta: dict) -> None:
    lines = [
        "# 第1課 revision notes",
        "",
        "Lesson 1 only. Lessons 2–4 were not rewritten. The twenty earlier readings pages were left in place.",
        "",
        "Learner pages do not explain missing examples. Those choices are recorded here.",
        "",
        f"KANJIDIC2 database {meta['database']}, created {meta['date']}. "
        "English meaning is the first English gloss. "
        "部首 is the KANJIDIC classical (Kangxi) radical, with the usual Japanese name. "
        "画数 is the KANJIDIC stroke count.",
        "",
        "The Heisig keyword is shown only when it was already classed as a different meaning: 玉, 空, 月.",
        "",
        "## Flags",
        "",
    ]
    for row in rows:
        lines.append(f"### {row['kanji']}")
        lines.append("")
        lines.append(
            f"- 部首 {row['radical']}（{row['radical_name']}）, Kangxi {row['radical_number']}, {row['strokes']}画"
        )
        lines.append(f"- KML lesson {row['lesson']} `#{row['anchor']}`")
        if row["kanji"] in DIFFERENT:
            lines.append(f"- Meaning “{row['meaning']}”, Heisig “{row['keyword']}”")
        else:
            lines.append(f"- Meaning “{row['meaning']}” only")
        for flag in row["flags"]:
            lines.append(f"- {flag}")
        if row["added"]:
            lines.append("- Added outside the compound file: " + ", ".join(row["added"]))
        if row["skipped"]:
            lines.append("- Not used: " + ", ".join(row["skipped"]))
        note = RADICAL_NOTES.get(row["radical_number"])
        if note:
            lines.append(f"- {note}")
        lines.append("")
    (REPO / "school-grade/grade-1/LESSON_01_NOTES.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    raise SystemExit(
        "Lesson pages are written by school-grade/scripts/build_grade1_pages.py. "
        "This script is kept so the 第1課 vocabulary record is not lost."
    )
    notice = disclaimer_html()
    if notice not in ENTRANCE.read_text(encoding="utf-8"):
        raise SystemExit("Entrance page is missing the shared disclaimer")
    wanted = {item["kanji"] for item in CHARACTERS}
    kanjidic, meta = load_kanjidic(wanted)
    entries = load_entries()
    cards = []
    notes = []
    for character in CHARACTERS:
        kanji = character["kanji"]
        slug = character["slug"]
        matches = [item for item in entries.get(slug, []) if item["kanji"] == kanji]
        if len(matches) != 1:
            raise SystemExit(f"{kanji}/{slug} matched {len(matches)} KML entries")
        entry = matches[0]
        info = kanjidic[kanji]
        if info["classical"] not in RADICALS:
            raise SystemExit(f"No radical name for {kanji} classical {info['classical']}")
        pool = load_compounds(kanji)
        added = []
        for group in character["on"] + character["kun"]:
            for item in group["words"]:
                surface, reading, is_added = word_parts(item)
                if is_added:
                    added.append(f"{surface}（{reading}）")
                elif (surface, reading) not in pool:
                    raise SystemExit(f"{kanji}: {surface}/{reading} is not in the compound files")
        stroke = REPO / f"kml/tools/strokes/pages/{slug}.html"
        lesson_file = LESSON_DIR / f"lesson_{entry['lesson']:02d}.html"
        if not stroke.is_file():
            raise SystemExit(f"Missing stroke page {stroke}")
        if f'id="{entry["anchor"]}"' not in lesson_file.read_text(encoding="utf-8"):
            raise SystemExit(f"Anchor {entry['anchor']} missing in {lesson_file.name}")
        if kanji in DIFFERENT and not entry["keyword"]:
            raise SystemExit(f"Missing Heisig keyword for {kanji}")
        cards.append(card_html(character, info, entry))
        glyph, name = RADICALS[info["classical"]]
        notes.append(
            {
                "kanji": kanji,
                "meaning": info["meaning"],
                "keyword": entry["keyword"],
                "strokes": info["strokes"],
                "radical": glyph,
                "radical_name": name,
                "radical_number": info["classical"],
                "lesson": entry["lesson"],
                "anchor": entry["anchor"],
                "flags": character["flags"],
                "added": added,
                "skipped": character["skipped"],
            }
        )
    write_lesson("\n".join(cards), meta, notice)
    write_compiled(notice)
    write_notes(notes, meta)
    old_pages = list((REPO / "school-grade/grade-1/readings").glob("*.html"))
    print(f"Wrote lesson 1 and the compiled readings page. Left {len(old_pages)} earlier readings pages in place.")


if __name__ == "__main__":
    main()
