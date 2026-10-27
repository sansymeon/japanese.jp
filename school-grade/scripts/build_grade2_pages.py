#!/usr/bin/env python3
"""Write the eight 漢検9級 lesson pages and their compiled vocabulary pages.

Uses the 漢検10級 card layout. Output lives at kanken/level-9/.
The level entrance is written by kml/scripts/build_kanken_level_pages.py.
Word examples are taken only from kml/data/compounds/ and attached when the
reading match is mechanical. Anything uncertain is listed in VOCABULARY_REVIEW.md.
"""

from __future__ import annotations

import csv
import html
import importlib.util
import json
import re
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GRADE = REPO / "kanken/level-9"
LESSON_DIR = REPO / "kml/contents/books/book_01/lessons"
COMPOUND_DIR = REPO / "kml/data/compounds"
KANJIDIC = REPO / "kml/kanjidic2.xml"
JOYO = REPO / "kml/analytics/reference/joyo_kanji.csv"
INDEX = REPO / "kml/data/kanji/kanken_index.json"
FILM_DIR = REPO / "kml/tools/ambient/collections/grade_2"
DISCLAIMER = REPO / "school-grade/partials/disclaimer.html"
REVIEW = GRADE / "VOCABULARY_REVIEW.md"
ORDER = GRADE / "order.json"
HEROES = GRADE / "heroes.json"
STUDIES = REPO / "kml/assets/studies"

spec = importlib.util.spec_from_file_location(
    "build_grade_1", Path(__file__).with_name("build_grade_1.py")
)
grade1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grade1)

# Learner-facing radical form. Number is the KANJIDIC classical radical.
# A note is recorded when that form is the shape inside the character
# rather than the Kangxi head character itself.
RADICALS = {
    1: ("一", "いち", ""),
    2: ("丨", "ぼう", ""),
    3: ("丶", "てん", ""),
    4: ("丿", "の", ""),
    5: ("乙", "おつ", ""),
    7: ("二", "に", ""),
    8: ("亠", "なべぶた", ""),
    9: ("人", "ひと", ""),
    10: ("儿", "ひとあし", ""),
    11: ("入", "いる", ""),
    12: ("八", "はち", ""),
    13: ("冂", "けいがまえ", ""),
    15: ("冫", "にすい", ""),
    17: ("凵", "うけばこ", ""),
    18: ("刀", "かたな", ""),
    19: ("力", "ちから", ""),
    21: ("匕", "さじ", ""),
    24: ("十", "じゅう", ""),
    27: ("厂", "がんだれ", ""),
    29: ("又", "また", ""),
    30: ("口", "くち", ""),
    31: ("囗", "くにがまえ", ""),
    32: ("土", "つち", ""),
    33: ("士", "さむらい", ""),
    35: ("夊", "すいにょう", ""),
    36: ("夕", "ゆうべ", ""),
    37: ("大", "だい", ""),
    38: ("女", "おんな", ""),
    39: ("子", "こ", ""),
    40: ("宀", "うかんむり", ""),
    41: ("寸", "すん", ""),
    42: ("小", "しょう", ""),
    46: ("山", "やま", ""),
    47: ("川", "かわ", ""),
    48: ("工", "こう", ""),
    50: ("巾", "はば", ""),
    51: ("干", "ほす", ""),
    77: ("止", "とめる", ""),
    53: ("广", "まだれ", ""),
    57: ("弓", "ゆみ", ""),
    58: ("彐", "けいがしら", ""),
    59: ("彡", "さんづくり", ""),
    60: ("彳", "ぎょうにんべん", ""),
    61: ("心", "こころ", ""),
    63: ("戸", "と", "古典部首は戶です。カードは戸です。"),
    64: ("手", "て", ""),
    66: ("攵", "のぶん", "古典部首は攴です。教・数にある形は攵です。"),
    67: ("文", "ぶん", ""),
    69: ("斤", "おの", ""),
    70: ("方", "ほう", ""),
    72: ("日", "ひ", ""),
    73: ("曰", "ひらび", ""),
    74: ("月", "つき", ""),
    75: ("木", "き", ""),
    76: ("欠", "あくび", ""),
    80: ("毋", "なかれ", "母・毎は、学校で母部と呼ばれることがあります。"),
    82: ("毛", "け", ""),
    84: ("气", "きがまえ", ""),
    85: ("水", "みず", ""),
    86: ("火", "ひ", ""),
    88: ("父", "ちち", ""),
    93: ("牛", "うし", ""),
    94: ("犬", "いぬ", ""),
    96: ("玉", "たま", ""),
    100: ("生", "うまれる", ""),
    101: ("用", "もちいる", ""),
    102: ("田", "た", ""),
    106: ("白", "しろ", ""),
    109: ("目", "め", ""),
    111: ("矢", "や", ""),
    112: ("石", "いし", ""),
    113: ("礻", "しめすへん", "古典部首は示です。社にある形は礻です。"),
    115: ("禾", "のぎ", ""),
    116: ("穴", "あな", ""),
    117: ("立", "たつ", ""),
    118: ("竹", "たけ", ""),
    119: ("米", "こめ", ""),
    120: ("糸", "いと", ""),
    124: ("羽", "はね", ""),
    125: ("老", "おい", ""),
    128: ("耳", "みみ", ""),
    130: ("肉", "にく", ""),
    132: ("自", "みずから", ""),
    137: ("舟", "ふね", ""),
    139: ("色", "いろ", ""),
    140: ("艹", "くさかんむり", ""),
    142: ("虫", "むし", ""),
    144: ("行", "ゆきがしら", ""),
    146: ("襾", "おおいかんむり", "西の古典部首です。"),
    147: ("見", "みる", ""),
    148: ("角", "つの", ""),
    149: ("言", "ごんべん", ""),
    150: ("谷", "たに", ""),
    154: ("貝", "かい", ""),
    155: ("赤", "あか", ""),
    156: ("走", "はしる", ""),
    157: ("足", "あし", ""),
    159: ("車", "くるま", ""),
    162: ("辶", "しんにょう", "古典部首は辵です。カードは辶です。"),
    166: ("里", "さと", ""),
    167: ("金", "かね", ""),
    168: ("長", "ながい", ""),
    169: ("門", "もん", ""),
    173: ("雨", "あめ", ""),
    174: ("青", "あお", ""),
    180: ("音", "おと", ""),
    181: ("頁", "おおがい", ""),
    182: ("風", "かぜ", ""),
    184: ("食", "しょく", ""),
    185: ("首", "くび", ""),
    187: ("馬", "うま", ""),
    189: ("高", "たかい", ""),
    195: ("魚", "うお", ""),
    196: ("鳥", "とり", ""),
    199: ("麦", "むぎ", "古典部首は麥です。カードは麦です。"),
    201: ("黄", "き", "古典部首は黃です。カードは黄です。"),
    203: ("黒", "くろ", "古典部首は黑です。カードは黒です。"),
}

# One existing study image from a character in that lesson. All are 1672×941.
HERO_CHOICES = {
    1: ("sea", "海"),
    2: ("face", "顔"),
    3: ("valley", "谷"),
    4: ("autumn", "秋"),
    5: ("snow", "雪"),
    6: ("morning", "朝"),
    7: ("horse", "馬"),
    8: ("plains", "野"),
}

LEVEL_PAGE = "./"
NEXT_LEVEL = "../level-8/"
MAX_EXAMPLES = 3

RENDAKU = {
    "か": "が", "き": "ぎ", "く": "ぐ", "け": "げ", "こ": "ご",
    "さ": "ざ", "し": "じ", "す": "ず", "せ": "ぜ", "そ": "ぞ",
    "た": "だ", "ち": "ぢ", "つ": "づ", "て": "で", "と": "ど",
    "は": "ば", "ひ": "び", "ふ": "ぶ", "へ": "べ", "ほ": "ぼ",
}


def esc(text: str) -> str:
    return html.escape(text or "", quote=True)


def hiragana(ch: str) -> bool:
    return "ぁ" <= ch <= "ん"


def kata_to_hira(text: str) -> str:
    out = []
    for ch in text:
        code = ord(ch)
        if 0x30A1 <= code <= 0x30F6:
            out.append(chr(code - 0x60))
        else:
            out.append(ch)
    return "".join(out)


def jpeg_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        raise SystemExit(f"Not a JPEG: {path}")
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5 : i + 9])
            return width, height
        if marker in (0xD8, 0xD9):
            i += 2
            continue
        segment = int.from_bytes(data[i + 2 : i + 4], "big")
        if segment < 2:
            break
        i += 2 + segment
    raise SystemExit(f"Cannot read JPEG size: {path}")


def split_joyo(field: str) -> list[str]:
    return [item.strip() for item in field.split("、") if item.strip()]


def parse_reading(raw: str) -> tuple[bool, str, str]:
    special = raw.startswith("（") and raw.endswith("）")
    body = raw[1:-1] if special else raw
    if "-" in body:
        stem, okuri = body.split("-", 1)
    else:
        stem, okuri = body, ""
    return special, stem, okuri


def display_reading(raw: str) -> str:
    special, stem, okuri = parse_reading(raw)
    shown = stem + okuri
    return f"（{shown}）" if special else shown


def voiced(stem: str) -> str:
    if not stem or stem[0] not in RENDAKU:
        return ""
    return RENDAKU[stem[0]] + stem[1:]


def film_cuts() -> list[list[str]]:
    cuts = []
    for path in sorted(FILM_DIR.glob("grade_2_compounds_school_0[1-8].json")):
        seen: list[str] = []
        for scene in json.loads(path.read_text(encoding="utf-8"))["scenes"]:
            kanji = scene.get("kanji")
            if kanji and len(kanji) == 1 and kanji not in seen and kanji != "朋":
                seen.append(kanji)
        cuts.append(seen)
    if len(cuts) != 8 or any(len(cut) != 20 for cut in cuts):
        raise SystemExit("Grade 2 film cuts are not eight lessons of 20")
    return cuts


def load_level() -> tuple[list[dict], dict]:
    joyo = {}
    with JOYO.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            joyo[row["kanji"]] = row
    records = [
        record
        for record in json.loads(INDEX.read_text(encoding="utf-8"))["characters"]
        if record["introducedAt"] == "9"
    ]
    if len(records) != 160:
        raise SystemExit(f"漢検9級 has {len(records)} characters")
    records.sort(key=lambda record: int(joyo[record["kanji"]]["joyo_index"]))
    cuts = film_cuts()
    got = [record["kanji"] for record in records]
    if [got[i : i + 20] for i in range(0, 160, 20)] != cuts:
        raise SystemExit("9級 order differs from the grade 2 熟語 film cuts")
    return records, joyo


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
        classical = None
        for rad in char.findall("radical/rad_value"):
            if rad.get("rad_type") == "classical":
                classical = int(rad.text)
        strokes = int(char.find("misc").findtext("stroke_count"))
        glosses = [
            meaning.text.strip()
            for meaning in char.findall("reading_meaning/rmgroup/meaning")
            if meaning.get("m_lang") in (None, "", "en") and meaning.text
        ]
        if classical is None or not glosses:
            raise SystemExit(f"KANJIDIC2 incomplete for {literal}")
        found[literal] = {"strokes": strokes, "classical": classical, "glosses": glosses}
    missing = wanted - set(found)
    if missing:
        raise SystemExit(f"KANJIDIC2 missing {''.join(sorted(missing))}")
    return found, meta


def load_compounds() -> dict[str, list[tuple[str, str]]]:
    pools: dict[str, list[tuple[str, str]]] = {}
    seen: dict[str, set[tuple[str, str]]] = {}
    for path in sorted(COMPOUND_DIR.glob("lesson_*.json")):
        if not re.fullmatch(r"lesson_\d+\.json", path.name):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for character in data.get("characters") or []:
            kanji = character.get("kanji")
            if not kanji:
                continue
            for compound in character.get("compounds") or []:
                surface = compound.get("surface") or ""
                reading = compound.get("reading") or ""
                if not surface or not reading or kanji not in surface:
                    continue
                key = (surface, reading)
                if key in seen.setdefault(kanji, set()):
                    continue
                seen[kanji].add(key)
                pools.setdefault(kanji, []).append(key)
    return pools


def keyword_from_page(record: dict) -> tuple[int, str, str]:
    page, anchor = record["lessonPage"].split("#", 1)
    path = REPO / page.lstrip("/")
    text = path.read_text(encoding="utf-8")
    if f'id="{anchor}"' not in text:
        raise SystemExit(f"Missing {anchor} in {path.name}")
    start = text.find(f'id="{anchor}"')
    block = text[start : text.find("</section>", start)]
    keyword = re.search(r'<span class="kanji-keyword">(.*?)</span>', block, re.S)
    if not keyword:
        raise SystemExit(f"No keyword for {record['kanji']} in {path.name}")
    lesson_no = int(path.stem.split("_")[1])
    cleaned = re.sub(r"\s+", " ", html.unescape(keyword.group(1))).strip()
    return lesson_no, anchor, cleaned


def assign_compound(kanji: str, surface: str, reading: str, ons: list[str], kuns: list[str]):
    if surface.count(kanji) != 1:
        return None
    index = surface.index(kanji)
    after = surface[index + 1 :]
    best = None

    def consider(score: tuple, kind: str, raw: str, how: str) -> None:
        nonlocal best
        item = (score, kind, raw, how)
        if best is None or item[0] > best[0]:
            best = item

    for raw in kuns:
        special, stem, okuri = parse_reading(raw)
        if special or not stem:
            continue
        spoken = stem + okuri
        altered = voiced(stem) + okuri if voiced(stem) else ""
        if okuri:
            if not after.startswith(okuri):
                continue
            if spoken in reading:
                consider((5, len(spoken)), "kun", raw, "okurigana")
            elif altered and altered in reading:
                consider((4, len(altered)), "kun", raw, "rendaku")
        elif reading == spoken:
            consider((5, len(spoken)), "kun", raw, "whole word")
        elif altered and reading == altered:
            consider((4, len(altered)), "kun", raw, "rendaku")
        elif all(not hiragana(ch) for ch in surface):
            forms = [(spoken, "compound", 3)]
            if altered:
                forms.append((altered, "rendaku", 2))
            for form, how, rank in forms:
                if reading.startswith(form) or reading.endswith(form):
                    consider((rank, len(form)), "kun", raw, how)

    if all(not hiragana(ch) for ch in surface):
        for raw in ons:
            special, stem, _okuri = parse_reading(raw)
            if special:
                continue
            spoken = kata_to_hira(stem)
            if not spoken:
                continue
            stopped = spoken[:-1] + "っ" if len(spoken) >= 2 else ""
            at_start = index == 0
            at_end = index == len(surface) - 1
            if at_start and reading.startswith(spoken):
                consider((4, len(spoken)), "on", raw, "start")
            elif at_end and reading.endswith(spoken):
                consider((4, len(spoken)), "on", raw, "end")
            elif at_start and stopped and reading.startswith(stopped):
                consider((3, len(spoken)), "on", raw, "sokuon")
            elif at_end and stopped and len(reading) > len(stopped) and reading.endswith(stopped):
                consider((3, len(spoken)), "on", raw, "sokuon")
    if best is None:
        return None
    _score, kind, raw, how = best
    return kind, raw, how


def attach_words(kanji: str, ons: list[str], kuns: list[str], compounds: list[tuple[str, str]]):
    groups = {raw: [] for raw in ons + kuns}
    notes = []
    unmatched = []
    for surface, reading in compounds:
        assigned = assign_compound(kanji, surface, reading, ons, kuns)
        if assigned is None:
            unmatched.append(f"{surface}（{reading}）")
            continue
        kind, raw, how = assigned
        groups[raw].append((surface, reading, how))
        if how not in {"okurigana", "whole word", "start", "end"}:
            notes.append(f"{surface}（{reading}）を{display_reading(raw)}に付けました（{how}）。")
    bare = []
    trimmed = {}
    for raw, words in groups.items():
        special, _stem, _okuri = parse_reading(raw)
        ordered = sorted(words, key=lambda item: (len(item[0]), item[0]))
        trimmed[raw] = [(surface, reading) for surface, reading, _how in ordered[:MAX_EXAMPLES]]
        if not trimmed[raw] and not special:
            bare.append(display_reading(raw))
        if len(ordered) > MAX_EXAMPLES:
            notes.append(
                f"{display_reading(raw)}の例は{MAX_EXAMPLES}語までです。残り{len(ordered) - MAX_EXAMPLES}語は出していません。"
            )
    return trimmed, bare, unmatched, notes


def ruby(surface: str, reading: str) -> str:
    n = 0
    while n < len(surface) and hiragana(surface[-1 - n]):
        n += 1
    if (
        n
        and len(surface) - n == 1
        and not hiragana(surface[0])
        and reading.endswith(surface[-n:])
        and len(reading) > n
    ):
        stem = surface[:-n]
        okuri = surface[-n:]
        return f"<ruby>{esc(stem)}<rt>{esc(reading[:-n])}</rt></ruby>{esc(okuri)}"
    return f"<ruby>{esc(surface)}<rt>{esc(reading)}</rt></ruby>"


def word_list(words: list[tuple[str, str]]) -> str:
    if not words:
        return ""
    items = "\n".join(
        f'<li><p class="sg-word" lang="ja">{ruby(surface, reading)}</p></li>'
        for surface, reading in words
    )
    return f'<ul class="sg-words">\n{items}\n</ul>'


def reading_groups(groups: list[tuple[str, list[tuple[str, str]]]]) -> str:
    chunks = []
    for label, words in groups:
        klass = "sg-read-label" if words else "sg-read-label sg-read-bare"
        chunks.append(f'<h4 class="{klass}" lang="ja">{esc(label)}</h4>\n{word_list(words)}')
    return "\n".join(chunks)


def page_head(title: str, description: str) -> str:
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
<link rel="stylesheet" href="../../kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="../../school-grade/css/school-grade.css">
<script>
try {{
  if (localStorage.getItem("kml-compounds-furigana") === "off") {{
    document.documentElement.classList.add("furigana-off");
  }}
}} catch (err) {{}}
</script>
</head>
"""


def lesson_nav(number: int) -> str:
    left = (
        f'<a href="{LEVEL_PAGE}">← 漢検9級</a>'
        if number == 1
        else f'<a href="lesson-{number - 1:02d}.html">← 第{number - 1}課</a>'
    )
    right = (
        f'<a href="{NEXT_LEVEL}">漢検8級 →</a>'
        if number == 8
        else f'<a href="lesson-{number + 1:02d}.html">第{number + 1}課 →</a>'
    )
    return f"""<div class="navbar">
  {left}
  <a href="{LEVEL_PAGE}">漢検9級</a>
  {right}
</div>"""


def review_block() -> str:
    return """
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLZZOWGAZaws0" target="_blank" rel="noopener noreferrer">漢検9級の漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLC4BEkURnrGU" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 8 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLIhlrvcFkelo" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 8 films</span></a>
  </div>
</section>
"""


def furigana_bar() -> str:
    return """<div class="furigana-bar">
  <button type="button" class="furigana-toggle" id="furigana-toggle" aria-pressed="true" aria-label="ふりがな オン">
    ふりがな
    <span class="furigana-mark" aria-hidden="true"></span>
  </button>
</div>"""


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


def card_html(entry: dict) -> str:
    slug = entry["slug"]
    number = f"{entry['lesson']:02d}"
    heisig = ""
    if entry["meaning_kind"] == "differs":
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
  <p class="sg-meaning" lang="en">{esc(entry["meaning"])}</p>{heisig}
  {chr(10).join(panels)}
  <p class="sg-facts">
    <span lang="ja">部首 <b>{esc(entry["radical"])}</b>（{esc(entry["radical_name"])}）</span>
    <span lang="ja">画数 <b>{entry["strokes"]}</b></span>
  </p>
  <a class="sg-kml-link" href="../../{esc(entry["lesson_path"])}">KMLで詳しく見る</a>
</article>
"""


def write_lesson(number: int, entries: list[dict], hero: dict, notice: str) -> None:
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
<p class="school-kicker" lang="ja">漢検9級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学2年生で習う160字</p>
<h1 class="school-title">{esc(title)}</h1>
<p class="sg-to-words"><a href="lesson-{number:02d}-readings.html">読み方とことば</a></p>
<nav class="anchor-list">
{anchors}
</nav>
{cards}
{review_block()}
{lesson_nav(number)}
<p class="school-footer-note">意味・画数・部首は KANJIDIC2（EDRDG、2026-074、2026-03-15）によります。読み方は常用漢字表の音訓です。</p>
{notice}
</body>
</html>
"""
    text = page_head(title, f"漢検9級レベルの漢字。小学2年生で習う160字のうち、第{number}課。")
    (GRADE / f"lesson-{number:02d}.html").write_text(text + body, encoding="utf-8")


def write_compiled(number: int, entries: list[dict], notice: str) -> None:
    articles = []
    for entry in entries:
        slug = entry["slug"]
        on_html = ""
        kun_html = ""
        if entry["on"]:
            groups = [(display_reading(raw), entry["words"][raw]) for raw in entry["on"]]
            on_html = f"""  <div class="sg-read-block" id="kanji-{esc(slug)}-on">
    <h3 class="sg-side" lang="ja">音読み</h3>
    {reading_groups(groups)}
  </div>"""
        if entry["kun"]:
            groups = [(display_reading(raw), entry["words"][raw]) for raw in entry["kun"]]
            kun_html = f"""  <div class="sg-read-block" id="kanji-{esc(slug)}-kun">
    <h3 class="sg-side" lang="ja">訓読み</h3>
    {reading_groups(groups)}
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
  <a href="{LEVEL_PAGE}">漢検9級</a>
</div>
<p class="school-kicker" lang="ja">漢検9級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学2年生で習う160字</p>
<h1 class="school-title">{esc(title)}</h1>
{furigana_bar()}
<nav class="anchor-list">
{anchors}
</nav>
{chr(10).join(articles)}
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="{LEVEL_PAGE}">漢検9級</a>
</div>
{notice}
{furigana_script()}
</body>
</html>
"""
    text = page_head(title, f"漢検9級 第{number}課の読み方とことば。小学2年生で習う160字。")
    (GRADE / f"lesson-{number:02d}-readings.html").write_text(text + body, encoding="utf-8")


def write_review(entries: list[dict], meta: dict) -> None:
    lines = [
        "# Grade 2 vocabulary review",
        "",
        "Learner pages do not explain these choices.",
        "",
        f"KANJIDIC2 {meta['database']}, {meta['date']}.",
        "English meaning on the card is the first English gloss.",
        "Heisig is shown on the card only when the keyword matches a later gloss and not the first.",
        "Readings are the 常用漢字表 音訓. Parentheses are the table’s indented readings.",
        "Example words come from `kml/data/compounds/`. A word is attached only when its reading",
        "matches that 音訓 at the edge of the word, including 連濁 and 促音. Unmatched words are not shown.",
        "At most three examples are shown for each reading.",
        "",
        "Covers are existing study images, one character from each lesson:",
        "",
    ]
    for number, (slug, kanji) in HERO_CHOICES.items():
        lines.append(f"- 第{number}課 {kanji} `kml/assets/studies/{slug}.jpg`")
    lines.extend(["", "## Needs review", ""])
    for entry in entries:
        flags = []
        if entry["meaning_kind"] != "equivalent":
            flags.append(
                f"Meaning “{entry['meaning']}”, Heisig “{entry['keyword']}” ({entry['meaning_kind']}: {entry['meaning_reason']})"
            )
        if entry["joyo_strokes"] != entry["strokes"]:
            flags.append(f"画数: KANJIDIC {entry['strokes']}, 常用漢字表 {entry['joyo_strokes']}")
        if entry["radical_note"]:
            flags.append(entry["radical_note"])
        if entry["joyo_radical"] != entry["radical"]:
            flags.append(f"常用漢字表の部首は{entry['joyo_radical']}、カードは{entry['radical']}（{entry['radical_name']}）")
        if entry["bare"]:
            flags.append("例のない読み: " + "、".join(entry["bare"]))
        if entry["unmatched"]:
            flags.append("例にしていない語: " + "、".join(entry["unmatched"][:8]))
            if len(entry["unmatched"]) > 8:
                flags.append(f"ほか{len(entry['unmatched']) - 8}語")
        flags.extend(entry["match_notes"])
        if not flags:
            continue
        lines.append(f"### {entry['kanji']}（第{entry['lesson']}課）")
        lines.append("")
        for flag in flags:
            lines.append(f"- {flag}")
        lines.append("")
    REVIEW.write_text("\n".join(lines), encoding="utf-8")


def write_order(entries: list[dict], meta: dict) -> None:
    lessons = []
    for number in range(1, 9):
        group = [entry for entry in entries if entry["lesson"] == number]
        lessons.append({"lesson": number, "characters": [entry["kanji"] for entry in group]})
    payload = {
        "grade": 2,
        "count": 160,
        "order": "五十音順",
        "reference": "学年別漢字配当表 via joyo_kanji.csv, checked against the grade 2 熟語 film cuts",
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


def write_heroes(heroes: dict[int, dict]) -> None:
    payload = {
        "lessons": {
            str(number): {"src": hero["src"], "alt": hero["alt"]}
            for number, hero in heroes.items()
        }
    }
    HEROES.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare(records: list[dict], joyo: dict, kanjidic: dict, compounds: dict) -> list[dict]:
    entries = []
    for index, record in enumerate(records):
        kanji = record["kanji"]
        info = kanjidic[kanji]
        if info["classical"] not in RADICALS:
            raise SystemExit(f"No radical name for {kanji} classical {info['classical']}")
        glyph, name, note = RADICALS[info["classical"]]
        lesson_no, anchor, keyword = keyword_from_page(record)
        compared = grade1.compare_meanings(keyword, info["glosses"])
        row = joyo[kanji]
        ons = split_joyo(row["on_kana"])
        kuns = split_joyo(row["kun_kana"])
        words, bare, unmatched, match_notes = attach_words(
            kanji, ons, kuns, compounds.get(kanji, [])
        )
        stroke_path = record["strokePage"].lstrip("/")
        lesson_path = record["lessonPage"].lstrip("/")
        stroke_file = REPO / stroke_path
        if not stroke_file.is_file():
            raise SystemExit(f"Missing stroke page for {kanji}")
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
                "strokes": info["strokes"],
                "joyo_strokes": int(row["strokes"]),
                "radical": glyph,
                "radical_name": name,
                "radical_note": note,
                "radical_number": info["classical"],
                "joyo_radical": row["radical"],
                "joyo_index": int(row["joyo_index"]),
                "heisig_number": record["heisigNumber"],
                "source_lesson": lesson_no,
                "anchor": anchor,
                "on": ons,
                "kun": kuns,
                "panel_on": "・".join(display_reading(item) for item in ons),
                "panel_kun": "・".join(display_reading(item) for item in kuns),
                "words": words,
                "bare": bare,
                "unmatched": unmatched,
                "match_notes": match_notes,
                "stroke_path": stroke_path,
                "lesson_path": lesson_path,
                "cover_slug": hero_slug,
            }
        )
    return entries


def main() -> None:
    notice = DISCLAIMER.read_text(encoding="utf-8").strip()
    if "日本漢字能力検定協会" not in notice:
        raise SystemExit("Disclaimer partial is incomplete")
    records, joyo = load_level()
    kanjidic, meta = load_kanjidic({record["kanji"] for record in records})
    compounds = load_compounds()
    entries = prepare(records, joyo, kanjidic, compounds)
    heroes = {}
    for number, (slug, kanji) in HERO_CHOICES.items():
        path = STUDIES / f"{slug}.jpg"
        if not path.is_file():
            raise SystemExit(f"Missing cover {path}")
        width, height = jpeg_size(path)
        if abs(width / height - 16 / 9) > 0.015:
            raise SystemExit(f"Cover {slug}.jpg is {width}×{height}, not 16:9")
        owner = next(entry for entry in entries if entry["slug"] == slug)
        if owner["lesson"] != number or owner["kanji"] != kanji:
            raise SystemExit(f"Cover {kanji}/{slug} is not lesson {number}")
        heroes[number] = {
            "src": f"../../kml/assets/studies/{slug}.jpg",
            "alt": kanji,
            "width": width,
            "height": height,
        }
    GRADE.mkdir(parents=True, exist_ok=True)
    for number in range(1, 9):
        group = [entry for entry in entries if entry["lesson"] == number]
        write_lesson(number, group, heroes[number], notice)
        write_compiled(number, group, notice)
        print(f"Wrote lesson {number}")
    write_order(entries, meta)
    write_heroes(heroes)
    write_review(entries, meta)
    differs = [entry["kanji"] for entry in entries if entry["meaning_kind"] == "differs"]
    uncertain = [entry["kanji"] for entry in entries if entry["meaning_kind"] == "uncertain"]
    bare = sum(len(entry["bare"]) for entry in entries)
    print(f"meanings differ {len(differs)} uncertain {len(uncertain)} bare readings {bare}")
    print("validation passed")


if __name__ == "__main__":
    main()
