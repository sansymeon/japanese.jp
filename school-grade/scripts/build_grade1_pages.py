#!/usr/bin/env python3
"""Write the 漢検10級 overview, four lesson pages, and compiled readings.

Output lives at kanken/level-10/. School grade stays explanatory context.
The overview is the lesson doors and the music and video review. It does not
include a character index.
Does not modify Heisig lessons or the older readings/*.html pages.
"""

from __future__ import annotations

import html
import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GRADE = REPO / "kanken/level-10"
LESSON_DIR = REPO / "kml/contents/books/book_01/lessons"
COMPOUND_DIR = REPO / "kml/data/compounds"
KANJIDIC = REPO / "kml/kanjidic2.xml"
ORDER = GRADE / "order.json"
HEROES = GRADE / "heroes.json"
DISCLAIMER = REPO / "school-grade/partials/disclaimer.html"
REVIEW = GRADE / "VOCABULARY_REVIEW.md"

spec = importlib.util.spec_from_file_location(
    "grade1_vocabulary", Path(__file__).with_name("grade1_vocabulary.py")
)
vocab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vocab)

# Heisig is shown only where the keyword differs from the first KANJIDIC gloss.
DIFFERENT = {"玉", "空", "月", "日"}

RANGES = {1: "一 〜 見", 2: "五 〜 森", 3: "人 〜 虫", 4: "町 〜 六"}

# Kangxi number → glyph, conventional Japanese name.
RADICALS = {
    1: ("一", "いち"),
    2: ("丨", "ぼう"),
    5: ("乙", "おつ"),
    7: ("二", "に"),
    9: ("人", "ひと"),
    10: ("儿", "ひとあし"),
    11: ("入", "いる"),
    12: ("八", "はち"),
    13: ("冂", "けいがまえ"),
    17: ("凵", "うけばこ"),
    19: ("力", "ちから"),
    24: ("十", "じゅう"),
    30: ("口", "くち"),
    31: ("囗", "くにがまえ"),
    32: ("土", "つち"),
    36: ("夕", "ゆうべ"),
    37: ("大", "だい"),
    38: ("女", "おんな"),
    39: ("子", "こ"),
    42: ("小", "しょう"),
    46: ("山", "やま"),
    47: ("川", "かわ"),
    48: ("工", "こう"),
    51: ("干", "ほす"),
    64: ("手", "て"),
    67: ("文", "ぶん"),
    72: ("日", "ひ"),
    74: ("月", "つき"),
    75: ("木", "き"),
    77: ("止", "とめる"),
    84: ("气", "きがまえ"),
    85: ("水", "みず"),
    86: ("火", "ひ"),
    94: ("犬", "いぬ"),
    96: ("玉", "たま"),
    100: ("生", "うまれる"),
    102: ("田", "た"),
    106: ("白", "しろ"),
    109: ("目", "め"),
    112: ("石", "いし"),
    116: ("穴", "あな"),
    117: ("立", "たつ"),
    118: ("竹", "たけ"),
    120: ("糸", "いと"),
    128: ("耳", "みみ"),
    140: ("艹", "くさかんむり"),
    142: ("虫", "むし"),
    147: ("見", "みる"),
    154: ("貝", "かい"),
    155: ("赤", "あか"),
    157: ("足", "あし"),
    159: ("車", "くるま"),
    167: ("金", "かね"),
    173: ("雨", "あめ"),
    174: ("青", "あお"),
    180: ("音", "おと"),
}

RADICAL_NOTES = {
    5: "九の古典部首は乙です。Nelson は丿です。カードは古典部首です。",
    7: "五の古典部首は二です。",
    10: "先の部首は儿（ひとあし）です。にんにょうとも呼びます。",
    13: "円の部首は冂です。まきがまえ・どうがまえとも呼び、囗とする辞書もあります。",
    17: "出の部首は凵（うけばこ）です。かんにょうとも呼びます。",
    47: "川の部首は川です。古典の形は巛とも書きます。",
    51: "年の部首は干（ほす）です。",
    96: "王も玉も玉部です。",
    140: "花の古典部首は艸です。カードは艹（くさかんむり）です。",
}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def hiragana(ch: str) -> bool:
    return "ぁ" <= ch <= "ん"


def word_parts(item: tuple) -> tuple[str, str, bool]:
    surface, reading = item[0], item[1]
    added = len(item) > 2 and item[2] == "added"
    return surface, reading, added


def ruby(surface: str, reading: str) -> str:
    n = 0
    while n < len(surface) and hiragana(surface[-1 - n]):
        n += 1
    # Split only when one kanji is followed by its own okurigana.
    # Compounds such as 夏休み keep a single ruby over the whole word.
    if (
        n
        and len(surface) - n == 1
        and not hiragana(surface[0])
        and reading.endswith(surface[-n:])
        and len(reading) > n
    ):
        stem = surface[:-n]
        okuri = surface[-n:]
        stem_reading = reading[:-n]
        return f"<ruby>{esc(stem)}<rt>{esc(stem_reading)}</rt></ruby>{esc(okuri)}"
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
            "</li>"
        )
    return '<ul class="sg-words">\n' + "\n".join(lis) + "\n</ul>"


def reading_groups(groups: list[dict]) -> str:
    chunks = []
    for group in groups:
        klass = "sg-read-label" if group["words"] else "sg-read-label sg-read-bare"
        chunks.append(f'<h4 class="{klass}" lang="ja">{esc(group["label"])}</h4>\n' + word_list(group["words"]))
    return "\n".join(chunks)


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
        glosses = []
        for meaning in char.findall("reading_meaning/rmgroup/meaning"):
            if meaning.get("m_lang") in (None, "", "en") and meaning.text:
                glosses.append(meaning.text.strip())
        found[literal] = {"strokes": strokes, "classical": classical, "meaning": glosses[0]}
    missing = wanted - set(found)
    if missing:
        raise SystemExit(f"KANJIDIC2 missing {missing}")
    return found, meta


def load_entries() -> dict[str, list[dict]]:
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


def page_head(title: str, description: str, restore_furigana: bool = True) -> str:
    furigana = ""
    if restore_furigana:
        furigana = """<script>
try {
  if (localStorage.getItem("kml-compounds-furigana") === "off") {
    document.documentElement.classList.add("furigana-off");
  }
} catch (err) {}
</script>
"""
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
{furigana}</head>
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


def furigana_bar() -> str:
    return """<div class="furigana-bar">
  <button type="button" class="furigana-toggle" id="furigana-toggle" aria-pressed="true" aria-label="ふりがな オン">
    ふりがな
    <span class="furigana-mark" aria-hidden="true"></span>
  </button>
</div>"""


def lesson_nav(number: int) -> str:
    left = '<a href="./">← 漢検10級</a>' if number == 1 else f'<a href="lesson-{number - 1:02d}.html">← 第{number - 1}課</a>'
    right = '<a href="../level-9/">漢検9級 →</a>' if number == 4 else f'<a href="lesson-{number + 1:02d}.html">第{number + 1}課 →</a>'
    return f"""<div class="navbar">
  {left}
  <a href="./">漢検10級</a>
  {right}
</div>"""


def review_block() -> str:
    return """
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLDqZ_saSB25k" target="_blank" rel="noopener noreferrer">漢検10級の漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 2 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLUK4NyqFdNMw" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLYpgcBuk0PGg" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 4 films</span></a>
  </div>
</section>
"""


def anchor_nav(characters: list[dict], slug_of: dict[str, str]) -> str:
    links = "\n".join(
        f'<a href="#kanji-{esc(slug_of[item["kanji"]])}">{esc(item["kanji"])}</a>' for item in characters
    )
    return f'<nav class="anchor-list">\n{links}\n</nav>'


def card_html(character: dict, info: dict, entry: dict, slug: str) -> str:
    kanji = character["kanji"]
    glyph, name = RADICALS[info["classical"]]
    heisig = ""
    if kanji in DIFFERENT:
        heisig = f'\n  <p class="sg-heisig">(Heisig: {esc(entry["keyword"])})</p>'
    single = "" if character["panel_kun"] else " sg-panels-single"
    kun = ""
    if character["panel_kun"]:
        kun = f"""
    <a class="sg-panel" href="lesson-{{n}}-readings.html#kanji-{esc(slug)}-kun">
      <span class="sg-panel-label" lang="ja">訓読み</span>
      <span class="sg-panel-yomi" lang="ja">{esc(character["panel_kun"])}</span>
    </a>"""
    return f"""<article class="sg-card" id="kanji-{esc(slug)}" data-kanji="{esc(kanji)}">
  <a class="sg-kanji-link" href="../../kml/tools/strokes/pages/{esc(slug)}.html">
    <span class="sg-kanji" lang="ja">{esc(kanji)}</span>
  </a>
  <p class="sg-meaning" lang="en">{esc(info["meaning"])}</p>{heisig}
  <div class="sg-panels{single}">
    <a class="sg-panel" href="lesson-{{n}}-readings.html#kanji-{esc(slug)}-on">
      <span class="sg-panel-label" lang="ja">音読み</span>
      <span class="sg-panel-yomi" lang="ja">{esc(character["panel_on"])}</span>
    </a>{kun}
  </div>
  <p class="sg-facts">
    <span lang="ja">部首 <b>{esc(glyph)}</b>（{esc(name)}）</span>
    <span lang="ja">画数 <b>{info["strokes"]}</b></span>
  </p>
  <a class="sg-kml-link" href="../../kml/contents/books/book_01/lessons/lesson_{entry["lesson"]:02d}.html#{esc(entry["anchor"])}">KMLで詳しく見る</a>
</article>
"""


def side_html(character: dict, side: str, slug: str) -> str:
    groups = character[side]
    if not groups:
        return ""
    title = "音読み" if side == "on" else "訓読み"
    return f"""<div class="sg-read-block" id="kanji-{esc(slug)}-{side}">
    <h3 class="sg-side" lang="ja">{title}</h3>
    {reading_groups(groups)}
  </div>"""


def hero_for(number: int) -> tuple[str, str, int, int]:
    data = json.loads(HEROES.read_text(encoding="utf-8"))
    chosen = data["lessons"].get(str(number)) or data["neutral"]
    src = chosen["src"]
    path = (GRADE / src).resolve()
    if not path.is_file():
        raise SystemExit(f"Missing hero {path}")
    try:
        from PIL import Image
    except ImportError:
        Image = None
    if Image is None:
        raise SystemExit(f"Cannot read hero size: {path}")
    with Image.open(path) as im:
        width, height = im.size
    return src, chosen["alt"], width, height


def write_lesson(number: int, cards: str, meta: dict, notice: str, characters: list[dict], slug_of: dict[str, str]) -> None:
    src, alt, width, height = hero_for(number)
    title = f"第{number}課 — {RANGES[number]}"
    body = f"""<body class="sg-lesson" id="top">
{lesson_nav(number)}
<div class="lesson-art">
  <img src="{esc(src)}" alt="{esc(alt)}" width="{width}" height="{height}">
</div>
<p class="school-kicker" lang="ja">漢検10級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学1年生で習う80字</p>
<h1 class="school-title">{esc(title)}</h1>
<p class="sg-to-words"><a href="lesson-{number:02d}-readings.html">読み方とことば</a></p>
{anchor_nav(characters, slug_of)}
{cards}
{review_block()}
{lesson_nav(number)}
<p class="school-footer-note">意味・画数・部首は KANJIDIC2（EDRDG、{esc(meta["database"])}、{esc(meta["date"])}）によります。</p>
{notice}
</body>
</html>
"""
    text = page_head(title, f"漢検10級レベルの漢字。小学1年生で習う80字のうち、第{number}課。")
    filled = (text + body).replace("lesson-{n}-readings.html", f"lesson-{number:02d}-readings.html")
    (GRADE / f"lesson-{number:02d}.html").write_text(filled, encoding="utf-8")


def write_compiled(number: int, characters: list[dict], slug_of: dict[str, str], notice: str) -> None:
    entries = []
    for character in characters:
        slug = slug_of[character["kanji"]]
        kanji = character["kanji"]
        entries.append(
            f'<article class="sg-entry" id="kanji-{esc(slug)}">\n'
            f'  <h2 class="sg-entry-kanji" lang="ja">{esc(kanji)}</h2>\n'
            f'  <a class="sg-entry-back" href="lesson-{number:02d}.html#kanji-{esc(slug)}">第{number}課の{esc(kanji)}</a>\n'
            f"  {side_html(character, 'on', slug)}\n"
            f"  {side_html(character, 'kun', slug)}\n"
            "</article>"
        )
    title = f"第{number}課 — 読み方とことば"
    body = f"""<body class="sg-readings sg-compiled" id="top">
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="./">漢検10級</a>
</div>
<p class="school-kicker" lang="ja">漢検10級レベルの漢字を学ぶ</p>
<p class="school-range" lang="ja">小学1年生で習う80字</p>
<h1 class="school-title">{esc(title)}</h1>
{furigana_bar()}
{anchor_nav(characters, slug_of)}
{chr(10).join(entries)}
<div class="navbar">
  <a href="lesson-{number:02d}.html">← 第{number}課</a>
  <a href="./">漢検10級</a>
</div>
{notice}
{furigana_script()}
</body>
</html>
"""
    text = page_head(title, f"漢検10級 第{number}課の読み方とことば。小学1年生で習う80字。")
    (GRADE / f"lesson-{number:02d}-readings.html").write_text(text + body, encoding="utf-8")


def write_review(rows: list[dict], meta: dict) -> None:
    lines = [
        "# Grade 1 vocabulary review",
        "",
        "Learner pages do not explain these choices.",
        "",
        f"KANJIDIC2 {meta['database']}, {meta['date']}. "
        "English meaning is the first English gloss. "
        "部首 is the classical radical. "
        "Heisig appears only for 玉, 空, 月, and 日.",
        "",
        "Lessons 2–4 use the neutral scenic hero until gold-on-blue filenames are supplied. "
        "The mapping is `kanken/level-10/heroes.json`.",
        "",
    ]
    for row in rows:
        lines.append(f"### {row['kanji']}（第{row['lesson']}課）")
        lines.append("")
        lines.append(
            f"- 部首 {row['radical']}（{row['radical_name']}）, Kangxi {row['radical_number']}, {row['strokes']}画"
        )
        lines.append(f"- KML lesson {row['source']} `#{row['anchor']}`")
        if row["kanji"] in DIFFERENT:
            lines.append(f"- Meaning “{row['meaning']}”, Heisig “{row['keyword']}”")
        else:
            lines.append(f"- Meaning “{row['meaning']}”")
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
    REVIEW.write_text("\n".join(lines), encoding="utf-8")


def write_overview() -> None:
    doors = []
    for number in range(1, 5):
        characters = vocab.LESSONS[number]
        kanji = " ".join(item["kanji"] for item in characters)
        title = f'{characters[0]["kanji"]} 〜 {characters[-1]["kanji"]}'
        doors.append(
            f'<a class="school-door" href="lesson-{number:02d}.html">\n'
            f'  <span class="school-door-kicker">第{number}課 · 20字</span>\n'
            f'  <span class="school-door-title">{esc(title)}</span>\n'
            f'  <span class="school-door-kanji" lang="ja">{esc(kanji)}</span>\n'
            "</a>"
        )
    notice = DISCLAIMER.read_text(encoding="utf-8").strip()
    text = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="漢検10級。小学1年生で習う80字。">
<title>漢検10級</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Yomogi&family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="../../kml/assets/site/css/compounds-lesson.css">
<link rel="stylesheet" href="../../school-grade/css/school-grade.css?v=levelnav">
<script>
try {{
  if (localStorage.getItem("kml-compounds-furigana") === "off") {{
    document.documentElement.classList.add("furigana-off");
  }}
}} catch (err) {{}}
</script>
<script>
  if (new URLSearchParams(location.search).get("lang") === "en") {{
    document.documentElement.setAttribute("data-kanken-lang", "en");
  }}
</script>
<script src="../../assets/js/kanken-lang.js" defer></script>
</head>
<body id="top">

<div class="navbar navbar-levels">
  <a href="../">漢検への道</a>
  <a href="../../kml/">Kanji・Music・Landscape</a>
  <a href="#review">音楽と動画</a>
  <a href="../level-9/">漢検9級 →</a>
</div>
<div class="lesson-art">
  <img src="../../kml/assets/covers/lesson_01.jpg" alt="月" width="1672" height="941">
</div>
<h1 class="school-title">漢検10級</h1>
<p class="school-range">小学1年生で習う80字</p>
<p class="school-path">漢字を学ぶ → 読み方とことば → 音楽と動画で復習</p>
<p class="kanken-en" lang="en">Level 10, beginner. Four lessons are ready here. The lessons themselves are in Japanese.</p>
<p class="kanken-en kanken-en-links" lang="en"><a href="../?lang=en">All levels</a> · <a href="/learn/">English learning choices</a></p>
<nav class="school-doors" aria-label="漢検10級の課">
{chr(10).join(doors)}
</nav>
{review_block()}
<p class="sg-disclaimer">{notice}</p>

<script src="../../kml/assets/site/js/kml.js"></script>
</body>
</html>
"""
    (GRADE / "index.html").write_text(text, encoding="utf-8")
    print("Wrote 漢検10級 overview")


def main() -> None:
    import sys

    only = {int(arg) for arg in sys.argv[1:]} or {1, 2, 3, 4}
    notice = DISCLAIMER.read_text(encoding="utf-8").strip()
    if "日本漢字能力検定協会" not in notice:
        raise SystemExit("Disclaimer partial is incomplete")
    order = json.loads(ORDER.read_text(encoding="utf-8"))
    by_kanji = {item["kanji"]: item for item in order["characters"]}
    entries = load_entries()
    wanted = set()
    for number in only:
        wanted.update(item["kanji"] for item in vocab.LESSONS[number])
    kanjidic, meta = load_kanjidic(wanted)
    notes = []
    for number in sorted(only):
        characters = vocab.LESSONS[number]
        expected = order["lessons"][number - 1]["characters"]
        got = [item["kanji"] for item in characters]
        if got != expected:
            raise SystemExit(f"Lesson {number} order mismatch:\n{got}\n{expected}")
        if len(got) != 20 or len(set(got)) != 20:
            raise SystemExit(f"Lesson {number} does not have 20 unique kanji")
        cards = []
        slug_of = {}
        for character in characters:
            kanji = character["kanji"]
            meta_row = by_kanji[kanji]
            slug = meta_row["slug"]
            slug_of[kanji] = slug
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
            cards.append(card_html(character, info, entry, slug).replace("{n}", f"{number:02d}"))
            glyph, name = RADICALS[info["classical"]]
            notes.append(
                {
                    "lesson": number,
                    "kanji": kanji,
                    "meaning": info["meaning"],
                    "keyword": entry["keyword"],
                    "strokes": info["strokes"],
                    "radical": glyph,
                    "radical_name": name,
                    "radical_number": info["classical"],
                    "source": entry["lesson"],
                    "anchor": entry["anchor"],
                    "flags": character["flags"],
                    "added": added,
                    "skipped": character["skipped"],
                }
            )
        write_lesson(number, "\n".join(cards), meta, notice, characters, slug_of)
        write_compiled(number, characters, slug_of, notice)
        print(f"Wrote lesson {number}")
    if only == {1, 2, 3, 4}:
        write_review(notes, meta)
        print(f"Wrote {REVIEW.name}")
    write_overview()


if __name__ == "__main__":
    main()
