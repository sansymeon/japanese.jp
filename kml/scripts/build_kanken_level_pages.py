#!/usr/bin/env python3
"""Build the Japanese-only 漢検 level pages from existing KML data.

Reads:
  kml/data/kanji/kanken_index.json        level, lesson link, stroke page, readings
  kml/analytics/reference/joyo_kanji.csv  常用漢字表 (2010) 掲載順
  kml/tools/ambient/collections/grade_2/grade_2_compounds_school_0[1-8].json
                                          9級 lesson cuts (checked, not copied)
  kml/tools/ambient/collections/grade_3/grade_3_compounds_school_[01-10].json
                                          8級 lesson cuts (checked, not copied)
  kml/tools/ambient/collections/grade_4/grade_4_compounds_school_[01-10].json
                                          7級 lesson cuts (checked, not copied)
  kml/tools/ambient/collections/grade_5/grade_5_compounds_school_[01-10].json
                                          6級 lesson cuts (checked, not copied)
  kml/tools/ambient/collections/grade_6/grade_6_compounds_school_[01-10].json
                                          5級 lesson sizes (checked, not copied)

Writes kanken/level-{9,8,7,6,5,4,3,jun2,2}/index.html.
漢検9級 through 漢検2級 are lesson entrances: hero, lesson doors, and the
music and video review. They do not include the character index. 漢検10級
is written separately at /kanken/level-10/ in that same shape.
漢検4級 lessons are fifteen groups of 20 and one of 13, in 常用漢字表 order.
漢検3級 lessons are ten groups of 20 and four groups of 21, in that same order.
漢検準2級 lessons are eight groups of 20 and eight groups of 21, in that same order.
漢検2級 lessons are four groups of 20 and five groups of 21, in that same order.
There is no separate school-film cut for those levels.
Lesson cards are written by school-grade/scripts/build_grade2_pages.py,
build_level8_pages.py, build_level7_pages.py, build_level6_pages.py, and build_level5_pages.py. A full run of this
script rewrites every level index from 9級 through 2級.

Order within a level: the 常用漢字表 掲載順, which is 五十音順 by each
character's representative reading (音読み, or 訓読み when it has no 音).
The 級別漢字表 (2020) PDF lists every level in this same order. 剥 叱 填 頬
take the position of 剝 𠮟 塡 頰, the forms printed in the 常用漢字表.

Readings are the 常用漢字表 音訓 from joyo_kanji.csv (2,352 音 and 2,036 訓,
the table's own totals), not the broader readings in kanji_production.csv.
Parentheses are kept: they mark the table's indented 音訓, the special or
narrowly used readings. The bracketed footnote marks "[6]" on 茨 岡 埼 栃 阜
are not readings and are not shown.

Pages show only the kanji, its readings, its KML lesson, and 書き順.
No English keywords and no YouTube links. Source data is not modified.

To verify against the official 常用漢字表 (not yet confirmed; do not correct
speculatively):
- Nine readings in joyo_kanji.csv are absent from KANJIDIC2 and are shown as
  given: 塞 ふさ-がる, 羨 うらや-ましい, 曽 ゾ, 速 はや-まる, 中 （ジュウ）,
  丼 どん, 務 つと-まる, 踊 おど-り, 絡 から-める.
- "[6]" on 茨 岡 埼 栃 阜 has no footnote text in the data. Confirm what the
  official 備考 says before adding any note.
- Parentheses are read as the table's 一字下げ音訓. joyo_kanji.csv has no
  recorded source, so the legend on each page rests on that reading.
"""

from __future__ import annotations

import csv
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "kml/data/kanji/kanken_index.json"
JOYO = ROOT / "kml/analytics/reference/joyo_kanji.csv"
GRADE_2_CUTS = ROOT / "kml/tools/ambient/collections/grade_2"
GRADE_3_CUTS = ROOT / "kml/tools/ambient/collections/grade_3"
GRADE_4_CUTS = ROOT / "kml/tools/ambient/collections/grade_4"
GRADE_5_CUTS = ROOT / "kml/tools/ambient/collections/grade_5"
GRADE_6_CUTS = ROOT / "kml/tools/ambient/collections/grade_6"
OUT = ROOT / "kanken"

TABLE_FORMS = {"剥": "剝", "叱": "𠮟", "填": "塡", "頬": "頰"}
EXPECTED = {"10": 80, "9": 160, "8": 200, "7": 202, "6": 193, "5": 191,
            "4": 313, "3": 284, "pre2": 328, "2": 185}
CUMULATIVE = {"10": 80, "9": 240, "8": 440, "7": 642, "6": 835, "5": 1026,
              "4": 1339, "3": 1623, "pre2": 1951, "2": 2136}
LABEL = {"10": "10級", "9": "9級", "8": "8級", "7": "7級", "6": "6級", "5": "5級",
         "4": "4級", "3": "3級", "pre2": "準2級", "2": "2級"}
SLUG = {"9": "level-9", "8": "level-8", "7": "level-7", "6": "level-6", "5": "level-5",
        "4": "level-4", "3": "level-3", "pre2": "level-jun2", "2": "level-2"}
CHAIN = ["10", "9", "8", "7", "6", "5", "4", "3", "pre2", "2"]
LESSON_SIZE = 20
LESSON_LEVELS = {"9", "8", "7", "6", "5", "4", "3", "pre2", "2"}
PENDING_LESSONS: set[str] = set()
HERO_IMAGE = "/kanken/kanken_hero_image.jpg"
EN_LEAD = {
    "9": "Level 9. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.",
    "8": "Level 8. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.",
    "7": "Level 7. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.",
    "6": "Level 6. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.",
    "5": "Level 5. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.",
    "4": "Level 4. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.",
    "3": "Level 3. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.",
    "pre2": "Level Pre-2. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.",
    "2": "Level 2, the advanced end. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.",
}
EN_ORIENT = {
    "9": "Eight lessons are ready, with readings and words.",
    "8": "Ten lessons are ready, with readings and words.",
    "7": "Ten lessons are ready, with readings and words.",
    "6": "Ten lessons are ready, with readings and words.",
    "5": "Ten lessons are ready, with readings and words.",
    "4": "Sixteen lessons are ready, with readings and words.",
    "3": "Fourteen lessons are ready, with readings and words.",
    "pre2": "Sixteen lessons are ready, with readings and words.",
    "2": "Nine lessons are ready, with readings and words.",
}
PREFIX = "../.."
ALLOWED_LATIN = {"Kanji", "Music", "Landscape", "KML"}
JOYO_TOTALS = {"on": 2352, "kun": 2036}
FOOTNOTE = re.compile(r"\[\d+\]")
READING = re.compile(r"^（?[\u3041-\u3096\u30a1-\u30fa\u30fc-]+）?$")
PAREN_NOTE = "（　）内は、常用漢字表で一字下げの音訓（特別なもの、または用法のごく狭いもの）です。"


def fail(message: str) -> None:
    print(f"VALIDATION FAILED: {message}", file=sys.stderr)
    sys.exit(1)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def split_readings(kanji: str, field: str) -> list[str]:
    items = [FOOTNOTE.sub("", item).strip() for item in field.split("、")]
    items = [item for item in items if item]
    for item in items:
        if not READING.match(item):
            fail(f"{kanji} has an unparsed reading {item!r}")
    if len(items) != len(set(items)):
        fail(f"{kanji} repeats a reading")
    return items


def load_reference() -> tuple[dict[str, int], dict[str, dict[str, list[str]]]]:
    with JOYO.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    order = {row["kanji"]: int(row["joyo_index"]) for row in rows}
    if sorted(order.values()) != list(range(1, 2137)):
        fail("joyo_kanji.csv is not a contiguous 1–2136 sequence")
    readings = {
        row["kanji"]: {
            "on": split_readings(row["kanji"], row["on_kana"]),
            "kun": split_readings(row["kanji"], row["kun_kana"]),
        }
        for row in rows
    }
    for kind, total in JOYO_TOTALS.items():
        found = sum(len(item[kind]) for item in readings.values())
        if found != total:
            fail(f"joyo_kanji.csv holds {found} {kind} readings, the 常用漢字表 has {total}")
    empty = [kanji for kanji, item in readings.items() if not item["on"] and not item["kun"]]
    if empty:
        fail(f"no readings for {''.join(empty)}")
    return order, readings


READINGS: dict[str, dict[str, list[str]]] = {}


def level_rows() -> dict[str, list[dict]]:
    order, readings = load_reference()
    READINGS.update(readings)
    records = json.loads(INDEX.read_text())["characters"]
    by_level: dict[str, list[dict]] = {level: [] for level in CHAIN}
    for record in records:
        by_level[record["introducedAt"]].append(record)
    for level, rows in by_level.items():
        if len(rows) != EXPECTED[level] or len({r["kanji"] for r in rows}) != EXPECTED[level]:
            fail(f"漢検{LABEL[level]} has {len(rows)} characters, expected {EXPECTED[level]}")
        for row in rows:
            if TABLE_FORMS.get(row["kanji"], row["kanji"]) not in order:
                fail(f"{row['kanji']} is not in the 常用漢字表 order")
        rows.sort(key=lambda r: order[TABLE_FORMS.get(r["kanji"], r["kanji"])])
    if sum(len(rows) for rows in by_level.values()) != 2136:
        fail("index does not hold 2,136 characters")
    return by_level


def film_cuts() -> list[list[str]]:
    cuts = []
    for path in sorted(GRADE_2_CUTS.glob("grade_2_compounds_school_0[1-8].json")):
        seen: list[str] = []
        for scene in json.loads(path.read_text())["scenes"]:
            kanji = scene.get("kanji")
            if kanji and len(kanji) == 1 and kanji not in seen and kanji != "朋":
                seen.append(kanji)
        cuts.append(seen)
    return cuts


def grade3_cuts() -> list[list[str]]:
    cuts = []
    for number in range(1, 11):
        path = GRADE_3_CUTS / f"grade_3_compounds_school_{number:02d}.json"
        seen: list[str] = []
        for scene in json.loads(path.read_text())["scenes"]:
            kanji = scene.get("kanji")
            if kanji and len(kanji) == 1 and kanji not in seen:
                seen.append(kanji)
        cuts.append(seen)
    return cuts


def grade4_cuts() -> list[list[str]]:
    cuts = []
    for number in range(1, 11):
        path = GRADE_4_CUTS / f"grade_4_compounds_school_{number:02d}.json"
        seen: list[str] = []
        for scene in json.loads(path.read_text())["scenes"]:
            kanji = scene.get("kanji")
            if kanji and len(kanji) == 1 and kanji not in seen:
                seen.append(kanji)
        cuts.append(seen)
    return cuts


def grade5_cuts() -> list[list[str]]:
    cuts = []
    for number in range(1, 11):
        path = GRADE_5_CUTS / f"grade_5_compounds_school_{number:02d}.json"
        seen: list[str] = []
        for scene in json.loads(path.read_text())["scenes"]:
            kanji = scene.get("kanji")
            if kanji and len(kanji) == 1 and kanji not in seen:
                seen.append(kanji)
        cuts.append(seen)
    return cuts


def grade6_cuts() -> list[list[str]]:
    cuts = []
    for number in range(1, 11):
        path = GRADE_6_CUTS / f"grade_6_compounds_school_{number:02d}.json"
        seen: list[str] = []
        for scene in json.loads(path.read_text())["scenes"]:
            kanji = scene.get("kanji")
            if kanji and len(kanji) == 1 and kanji not in seen:
                seen.append(kanji)
        cuts.append(seen)
    return cuts


def lessons_for(level: str, rows: list[dict]) -> list[list[dict]]:
    if level == "3":
        sizes = [20] * 10 + [21] * 4
        lessons = []
        index = 0
        for size in sizes:
            lessons.append(rows[index:index + size])
            index += size
        if [len(lesson) for lesson in lessons] != sizes or index != len(rows):
            fail("3級 lessons are not ten of 20 and four of 21")
        return lessons
    if level == "pre2":
        sizes = [20] * 8 + [21] * 8
        lessons = []
        index = 0
        for size in sizes:
            lessons.append(rows[index:index + size])
            index += size
        if [len(lesson) for lesson in lessons] != sizes or index != len(rows):
            fail("準2級 lessons are not eight of 20 and eight of 21")
        return lessons
    if level == "2":
        sizes = [20] * 4 + [21] * 5
        lessons = []
        index = 0
        for size in sizes:
            lessons.append(rows[index:index + size])
            index += size
        if [len(lesson) for lesson in lessons] != sizes or index != len(rows):
            fail("2級 lessons are not four of 20 and five of 21")
        return lessons
    if level == "4":
        lessons = [rows[i:i + LESSON_SIZE] for i in range(0, len(rows), LESSON_SIZE)]
        if [len(lesson) for lesson in lessons] != [20] * 15 + [13]:
            fail("4級 lessons are not fifteen of 20 and one of 13")
        return lessons
    if level == "5":
        cuts = grade6_cuts()
        seq = [record["kanji"] for record in rows]
        flat = [kanji for cut in cuts for kanji in cut]
        if [len(cut) for cut in cuts] != [20] * 9 + [11]:
            fail("5級 film sizes are not nine lessons of 20 and one of 11")
        if seq[:160] != flat[:160]:
            fail("5級 lessons 1–8 differ from the grade 6 熟語 films")
        joyo_from_film = flat[:164] + ["補"] + [kanji for kanji in flat[164:] if kanji != "補"]
        if seq != joyo_from_film:
            fail("5級 order is not the 常用漢字表 order")
        lessons = []
        index = 0
        for cut in cuts:
            lessons.append(rows[index:index + len(cut)])
            index += len(cut)
        if index != len(rows):
            fail("5級 film sizes do not cover the level")
        return lessons
    if level == "6":
        cuts = grade5_cuts()
        lessons = []
        index = 0
        for cut in cuts:
            lesson = rows[index:index + len(cut)]
            if [record["kanji"] for record in lesson] != cut:
                fail("6級 lessons differ from the grade 5 熟語 film cuts")
            lessons.append(lesson)
            index += len(cut)
        if index != len(rows):
            fail("6級 film cuts do not cover the level")
        return lessons
    if level == "7":
        cuts = grade4_cuts()
        lessons = []
        index = 0
        for cut in cuts:
            lesson = rows[index:index + len(cut)]
            if [record["kanji"] for record in lesson] != cut:
                fail("7級 lessons differ from the grade 4 熟語 film cuts")
            lessons.append(lesson)
            index += len(cut)
        if index != len(rows):
            fail("7級 film cuts do not cover the level")
        return lessons
    lessons = [rows[i:i + LESSON_SIZE] for i in range(0, len(rows), LESSON_SIZE)]
    if level == "9":
        cuts = film_cuts()
        if [[r["kanji"] for r in lesson] for lesson in lessons] != cuts:
            fail("9級 lessons differ from the grade 2 熟語 film cuts")
    if level == "8":
        cuts = grade3_cuts()
        if [[r["kanji"] for r in lesson] for lesson in lessons] != cuts:
            fail("8級 lessons differ from the grade 3 熟語 film cuts")
    return lessons


def reference_readings(kanji: str) -> dict[str, list[str]]:
    return READINGS[TABLE_FORMS.get(kanji, kanji)]


def readings(record: dict) -> str:
    item = reference_readings(record["kanji"])
    parts = []
    for kind, label in (("on", "音"), ("kun", "訓")):
        if item[kind]:
            parts.append(
                f'<span class="kanken-{kind}"><span class="kanken-reading-kind">{label}</span>'
                f'{esc("、".join(item[kind]))}</span>'
            )
    return "".join(parts)


def row_html(record: dict) -> str:
    alt = ""
    other = record.get("alternateForm")
    if other:
        alt = (
            f'\n            <p class="kanken-alt">字形 <a href="{esc(PREFIX + other["lessonPage"])}" lang="ja">'
            f'{esc(other["kanji"])}</a> は、レッスン {other["lesson"]} にあります。</p>'
        )
    return f"""          <li class="kanken-row" data-kanji="{esc(record["kanji"])}">
            <a class="kanken-row-link" href="{esc(PREFIX + record["lessonPage"])}">
              <span class="kanken-glyph" lang="ja">{esc(record["kanji"])}</span>
              <span class="kanken-readings">{readings(record)}</span>
              <span class="kanken-lesson">レッスン {record["lesson"]}</span>
            </a>
            <a class="kanken-stroke" href="{esc(PREFIX + record["strokePage"])}">書き順</a>{alt}
          </li>"""


def reading_note(rows: list[dict]) -> str:
    marked = any(
        reading.startswith("（")
        for record in rows
        for kind in ("on", "kun")
        for reading in reference_readings(record["kanji"])[kind]
    )
    if not marked:
        return ""
    return f'        <p class="kanken-reading-note">{PAREN_NOTE}</p>'


def level_href(level: str) -> str:
    if level == "10":
        return "../level-10/"
    return f"../{SLUG[level]}/"


def body_for(level: str, rows: list[dict]) -> str:
    label = LABEL[level]
    if level in LESSON_LEVELS:
        fail(f"漢検{LABEL[level]} overview is a lesson entrance and does not include the character index")
    pending = ""
    if level in PENDING_LESSONS:
        pending = '<span class="kanken-pending-note">この級の課は準備中です。</span>'
    items = "\n".join(row_html(record) for record in rows)
    return f"""        <header class="room-section-head reveal">
          <p class="room-eyebrow">漢字一覧</p>
          <h2 id="characters-heading">漢検{label}で新しく学ぶ漢字</h2>
          <p>各字から、KMLの学習ページと書き順を開けます。{pending}</p>
        </header>
{reading_note(rows)}
        <ul class="kanken-index">
{items}
        </ul>"""


def level9_entrance(rows: list[dict]) -> str:
    """漢検9級 overview: the same entrance shape as 漢検10級."""
    hero = ROOT / "kml/assets/studies/sea.jpg"
    if not hero.is_file():
        fail(f"Missing 9級 hero {hero}")
    try:
        from PIL import Image
    except ImportError:
        fail("Cannot read the 9級 hero size")
    with Image.open(hero) as image:
        width, height = image.size
    if abs(width / height - 16 / 9) > 0.015:
        fail(f"9級 hero is {width}×{height}, not 16:9")
    doors = []
    for number, lesson in enumerate(lessons_for("9", rows), start=1):
        kanji = " ".join(record["kanji"] for record in lesson)
        doors.append(
            f'<a class="school-door" href="lesson-{number:02d}.html">\n'
            f'  <span class="school-door-kicker">第{number}課 · 20字</span>\n'
            f'  <span class="school-door-title">{esc(lesson[0]["kanji"])} 〜 {esc(lesson[-1]["kanji"])}</span>\n'
            f'  <span class="school-door-kanji" lang="ja">{esc(kanji)}</span>\n'
            "</a>"
        )
    notice = (ROOT / "school-grade/partials/disclaimer.html").read_text(encoding="utf-8").strip()
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="漢検9級。小学2年生で習う160字。累計240字。">
<title>漢検9級</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Yomogi&family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/compounds-lesson.css">
<link rel="stylesheet" href="{PREFIX}/school-grade/css/school-grade.css?v=levelnav">
<script>
  if (new URLSearchParams(location.search).get("lang") === "en") {{
    document.documentElement.setAttribute("data-kanken-lang", "en");
  }}
</script>
<script src="{PREFIX}/assets/js/kanken-lang.js" defer></script>
</head>
<body id="top">
<div class="navbar navbar-levels">
  <a href="../level-10/">← 漢検10級</a>
  <a href="../">漢検への道</a>
  <a href="#review">音楽と動画</a>
  <a href="../level-8/">漢検8級 →</a>
</div>
<div class="lesson-art">
  <img src="{PREFIX}/kml/assets/studies/sea.jpg" alt="海" width="{width}" height="{height}">
</div>
<h1 class="school-title">漢検9級</h1>
<p class="school-range">小学2年生で習う160字 · 累計240字</p>
<p class="school-path">漢字を学ぶ → 読み方とことば → 音楽と動画で復習</p>
<p class="kanken-en" lang="en">Level 9. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.</p>
<p class="kanken-en kanken-orient" lang="en">Eight lessons are ready, with readings and words. <a href="../?lang=en">All levels</a> · <a href="/learn/">English learning choices</a></p>
<main>
<nav class="school-doors" aria-label="漢検9級の課">
{chr(10).join(doors)}
</nav>
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLZZOWGAZaws0" target="_blank" rel="noopener noreferrer">漢検9級の漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLC4BEkURnrGU" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 8 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLIhlrvcFkelo" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 8 films</span></a>
  </div>
</section>
</main>
<p class="sg-disclaimer">{notice}</p>
<script src="{PREFIX}/kml/assets/site/js/kml.js"></script>
</body>
</html>
"""


def level8_entrance(rows: list[dict]) -> str:
    """漢検8級 overview: the same entrance shape as 漢検9級."""
    hero = ROOT / "kml/assets/studies/island.jpg"
    if not hero.is_file():
        fail(f"Missing 8級 hero {hero}")
    try:
        from PIL import Image
    except ImportError:
        fail("Cannot read the 8級 hero size")
    with Image.open(hero) as image:
        width, height = image.size
    if abs(width / height - 16 / 9) > 0.015:
        fail(f"8級 hero is {width}×{height}, not 16:9")
    doors = []
    for number, lesson in enumerate(lessons_for("8", rows), start=1):
        kanji = " ".join(record["kanji"] for record in lesson)
        doors.append(
            f'<a class="school-door" href="lesson-{number:02d}.html">\n'
            f'  <span class="school-door-kicker">第{number}課 · 20字</span>\n'
            f'  <span class="school-door-title">{esc(lesson[0]["kanji"])} 〜 {esc(lesson[-1]["kanji"])}</span>\n'
            f'  <span class="school-door-kanji" lang="ja">{esc(kanji)}</span>\n'
            "</a>"
        )
    notice = (ROOT / "school-grade/partials/disclaimer.html").read_text(encoding="utf-8").strip()
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="漢検8級。小学3年生で習う200字。累計440字。">
<title>漢検8級</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Yomogi&family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/compounds-lesson.css">
<link rel="stylesheet" href="{PREFIX}/school-grade/css/school-grade.css?v=levelnav">
<script>
  if (new URLSearchParams(location.search).get("lang") === "en") {{
    document.documentElement.setAttribute("data-kanken-lang", "en");
  }}
</script>
<script src="{PREFIX}/assets/js/kanken-lang.js" defer></script>
</head>
<body id="top">
<div class="navbar navbar-levels">
  <a href="../level-9/">← 漢検9級</a>
  <a href="../">漢検への道</a>
  <a href="#review">音楽と動画</a>
  <a href="../level-7/">漢検7級 →</a>
</div>
<div class="lesson-art">
  <img src="{PREFIX}/kml/assets/studies/island.jpg" alt="島" width="{width}" height="{height}">
</div>
<h1 class="school-title">漢検8級</h1>
<p class="school-range">小学3年生で習う200字 · 累計440字</p>
<p class="school-path">漢字を学ぶ → 読み方とことば → 音楽と動画で復習</p>
<p class="kanken-en" lang="en">Level 8. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.</p>
<p class="kanken-en kanken-orient" lang="en">Ten lessons are ready, with readings and words. <a href="../?lang=en">All levels</a> · <a href="/learn/">English learning choices</a></p>
<main>
<nav class="school-doors" aria-label="漢検8級の課">
{chr(10).join(doors)}
</nav>
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLTQM6H4rynCk" target="_blank" rel="noopener noreferrer">漢検8級の漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLc8WHOv0GQ7w" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 10 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLQ2GcmPXGpTQ" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 8 films</span></a>
  </div>
</section>
</main>
<p class="sg-disclaimer">{notice}</p>
<script src="{PREFIX}/kml/assets/site/js/kml.js"></script>
</body>
</html>
"""


def level7_entrance(rows: list[dict]) -> str:
    """漢検7級 overview: the same entrance shape as 漢検8級."""
    hero = ROOT / "kml/assets/studies/scenery.jpg"
    if not hero.is_file():
        fail(f"Missing 7級 hero {hero}")
    try:
        from PIL import Image
    except ImportError:
        fail("Cannot read the 7級 hero size")
    with Image.open(hero) as image:
        width, height = image.size
    if abs(width / height - 16 / 9) > 0.015:
        fail(f"7級 hero is {width}×{height}, not 16:9")
    doors = []
    for number, lesson in enumerate(lessons_for("7", rows), start=1):
        kanji = " ".join(record["kanji"] for record in lesson)
        doors.append(
            f'<a class="school-door" href="lesson-{number:02d}.html">\n'
            f'  <span class="school-door-kicker">第{number}課 · {len(lesson)}字</span>\n'
            f'  <span class="school-door-title">{esc(lesson[0]["kanji"])} 〜 {esc(lesson[-1]["kanji"])}</span>\n'
            f'  <span class="school-door-kanji" lang="ja">{esc(kanji)}</span>\n'
            "</a>"
        )
    notice = (ROOT / "school-grade/partials/disclaimer.html").read_text(encoding="utf-8").strip()
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="漢検7級。小学4年生で習う202字。累計642字。">
<title>漢検7級</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Yomogi&family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/compounds-lesson.css">
<link rel="stylesheet" href="{PREFIX}/school-grade/css/school-grade.css?v=levelnav">
<script>
  if (new URLSearchParams(location.search).get("lang") === "en") {{
    document.documentElement.setAttribute("data-kanken-lang", "en");
  }}
</script>
<script src="{PREFIX}/assets/js/kanken-lang.js" defer></script>
</head>
<body id="top">
<div class="navbar navbar-levels">
  <a href="../level-8/">← 漢検8級</a>
  <a href="../">漢検への道</a>
  <a href="#review">音楽と動画</a>
  <a href="../level-6/">漢検6級 →</a>
</div>
<div class="lesson-art">
  <img src="{PREFIX}/kml/assets/studies/scenery.jpg" alt="景" width="{width}" height="{height}">
</div>
<h1 class="school-title">漢検7級</h1>
<p class="school-range">小学4年生で習う202字 · 累計642字</p>
<p class="school-path">漢字を学ぶ → 読み方とことば → 音楽と動画で復習</p>
<p class="kanken-en" lang="en">Level 7. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.</p>
<p class="kanken-en kanken-orient" lang="en">Ten lessons are ready, with readings and words. <a href="../?lang=en">All levels</a> · <a href="/learn/">English learning choices</a></p>
<main>
<nav class="school-doors" aria-label="漢検7級の課">
{chr(10).join(doors)}
</nav>
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLe8oWSTMK85g" target="_blank" rel="noopener noreferrer">漢検7級の漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLf9LPdcxbNnI" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 10 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLQfscrAlbAYo" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 8 films</span></a>
  </div>
</section>
</main>
<p class="sg-disclaimer">{notice}</p>
<script src="{PREFIX}/kml/assets/site/js/kml.js"></script>
</body>
</html>
"""


def level6_entrance(rows: list[dict]) -> str:
    """漢検6級 overview: the same entrance shape as 漢検7級."""
    hero = ROOT / "kml/assets/studies/cherry_blossom.jpg"
    if not hero.is_file():
        fail(f"Missing 6級 hero {hero}")
    try:
        from PIL import Image
    except ImportError:
        fail("Cannot read the 6級 hero size")
    with Image.open(hero) as image:
        width, height = image.size
    if abs(width / height - 16 / 9) > 0.015:
        fail(f"6級 hero is {width}×{height}, not 16:9")
    doors = []
    for number, lesson in enumerate(lessons_for("6", rows), start=1):
        kanji = " ".join(record["kanji"] for record in lesson)
        doors.append(
            f'<a class="school-door" href="lesson-{number:02d}.html">\n'
            f'  <span class="school-door-kicker">第{number}課 · {len(lesson)}字</span>\n'
            f'  <span class="school-door-title">{esc(lesson[0]["kanji"])} 〜 {esc(lesson[-1]["kanji"])}</span>\n'
            f'  <span class="school-door-kanji" lang="ja">{esc(kanji)}</span>\n'
            "</a>"
        )
    notice = (ROOT / "school-grade/partials/disclaimer.html").read_text(encoding="utf-8").strip()
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="漢検6級。小学5年生で習う193字。累計835字。">
<title>漢検6級</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Yomogi&family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/compounds-lesson.css">
<link rel="stylesheet" href="{PREFIX}/school-grade/css/school-grade.css?v=levelnav">
<script>
  if (new URLSearchParams(location.search).get("lang") === "en") {{
    document.documentElement.setAttribute("data-kanken-lang", "en");
  }}
</script>
<script src="{PREFIX}/assets/js/kanken-lang.js" defer></script>
</head>
<body id="top">
<div class="navbar navbar-levels">
  <a href="../level-7/">← 漢検7級</a>
  <a href="../">漢検への道</a>
  <a href="#review">音楽と動画</a>
  <a href="../level-5/">漢検5級 →</a>
</div>
<div class="lesson-art">
  <img src="{PREFIX}/kml/assets/studies/cherry_blossom.jpg" alt="桜" width="{width}" height="{height}">
</div>
<h1 class="school-title">漢検6級</h1>
<p class="school-range">小学5年生で習う193字 · 累計835字</p>
<p class="school-path">漢字を学ぶ → 読み方とことば → 音楽と動画で復習</p>
<p class="kanken-en" lang="en">Level 6. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.</p>
<p class="kanken-en kanken-orient" lang="en">Ten lessons are ready, with readings and words. <a href="../?lang=en">All levels</a> · <a href="/learn/">English learning choices</a></p>
<main>
<nav class="school-doors" aria-label="漢検6級の課">
{chr(10).join(doors)}
</nav>
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLKeIGzGuv0ZU" target="_blank" rel="noopener noreferrer">漢検6級の漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLBy3SmUyWUa0" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 10 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLLPec_9jQnEc" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 8 films</span></a>
  </div>
</section>
</main>
<p class="sg-disclaimer">{notice}</p>
<script src="{PREFIX}/kml/assets/site/js/kml.js"></script>
</body>
</html>
"""


def level5_entrance(rows: list[dict]) -> str:
    """漢検5級 overview: the same entrance shape as 漢検6級."""
    hero = ROOT / "kml/assets/studies/window.jpg"
    if not hero.is_file():
        fail(f"Missing 5級 hero {hero}")
    try:
        from PIL import Image
    except ImportError:
        fail("Cannot read the 5級 hero size")
    with Image.open(hero) as image:
        width, height = image.size
    if abs(width / height - 16 / 9) > 0.015:
        fail(f"5級 hero is {width}×{height}, not 16:9")
    doors = []
    for number, lesson in enumerate(lessons_for("5", rows), start=1):
        kanji = " ".join(record["kanji"] for record in lesson)
        doors.append(
            f'<a class="school-door" href="lesson-{number:02d}.html">\n'
            f'  <span class="school-door-kicker">第{number}課 · {len(lesson)}字</span>\n'
            f'  <span class="school-door-title">{esc(lesson[0]["kanji"])} 〜 {esc(lesson[-1]["kanji"])}</span>\n'
            f'  <span class="school-door-kanji" lang="ja">{esc(kanji)}</span>\n'
            "</a>"
        )
    notice = (ROOT / "school-grade/partials/disclaimer.html").read_text(encoding="utf-8").strip()
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="漢検5級。小学6年生で習う191字。累計1,026字。">
<title>漢検5級</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Yomogi&family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/compounds-lesson.css">
<link rel="stylesheet" href="{PREFIX}/school-grade/css/school-grade.css?v=levelnav">
<script>
  if (new URLSearchParams(location.search).get("lang") === "en") {{
    document.documentElement.setAttribute("data-kanken-lang", "en");
  }}
</script>
<script src="{PREFIX}/assets/js/kanken-lang.js" defer></script>
</head>
<body id="top">
<div class="navbar navbar-levels">
  <a href="../level-6/">← 漢検6級</a>
  <a href="../">漢検への道</a>
  <a href="#review">音楽と動画</a>
  <a href="../level-4/">漢検4級 →</a>
</div>
<div class="lesson-art">
  <img src="{PREFIX}/kml/assets/studies/window.jpg" alt="窓" width="{width}" height="{height}">
</div>
<h1 class="school-title">漢検5級</h1>
<p class="school-range">小学6年生で習う191字 · 累計1,026字</p>
<p class="school-path">漢字を学ぶ → 読み方とことば → 音楽と動画で復習</p>
<p class="kanken-en" lang="en">Level 5. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.</p>
<p class="kanken-en kanken-orient" lang="en">Ten lessons are ready, with readings and words. <a href="../?lang=en">All levels</a> · <a href="/learn/">English learning choices</a></p>
<main>
<nav class="school-doors" aria-label="漢検5級の課">
{chr(10).join(doors)}
</nav>
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLWU0EpkddEOk" target="_blank" rel="noopener noreferrer">漢検5級の漢字<br><span style="font-size:0.82rem;font-weight:400">Kanji · 4 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLbjp2j5SAHGs" target="_blank" rel="noopener noreferrer">熟語<br><span style="font-size:0.82rem;font-weight:400">Compounds · 10 films</span></a>
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLLpAPKufLmCc" target="_blank" rel="noopener noreferrer">書き順<br><span style="font-size:0.82rem;font-weight:400">Stroke order · 8 films</span></a>
  </div>
</section>
</main>
<p class="sg-disclaimer">{notice}</p>
<script src="{PREFIX}/kml/assets/site/js/kml.js"></script>
</body>
</html>
"""


def level4_entrance(rows: list[dict]) -> str:
    """漢検4級 overview: the same entrance shape as 漢検5級."""
    hero = ROOT / "kml/assets/studies/potato.jpg"
    if not hero.is_file():
        fail(f"Missing 4級 hero {hero}")
    try:
        from PIL import Image
    except ImportError:
        fail("Cannot read the 4級 hero size")
    with Image.open(hero) as image:
        width, height = image.size
    if abs(width / height - 16 / 9) > 0.015:
        fail(f"4級 hero is {width}×{height}, not 16:9")
    doors = []
    for number, lesson in enumerate(lessons_for("4", rows), start=1):
        kanji = " ".join(record["kanji"] for record in lesson)
        doors.append(
            f'<a class="school-door" href="lesson-{number:02d}.html">\n'
            f'  <span class="school-door-kicker">第{number}課 · {len(lesson)}字</span>\n'
            f'  <span class="school-door-title">{esc(lesson[0]["kanji"])} 〜 {esc(lesson[-1]["kanji"])}</span>\n'
            f'  <span class="school-door-kanji" lang="ja">{esc(kanji)}</span>\n'
            "</a>"
        )
    notice = (ROOT / "school-grade/partials/disclaimer.html").read_text(encoding="utf-8").strip()
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="漢検4級。常用漢字表の中学校以降の漢字のうち313字。累計1,339字。">
<title>漢検4級</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Yomogi&family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/compounds-lesson.css">
<link rel="stylesheet" href="{PREFIX}/school-grade/css/school-grade.css?v=levelnav">
<script>
  if (new URLSearchParams(location.search).get("lang") === "en") {{
    document.documentElement.setAttribute("data-kanken-lang", "en");
  }}
</script>
<script src="{PREFIX}/assets/js/kanken-lang.js" defer></script>
</head>
<body id="top">
<div class="navbar navbar-levels">
  <a href="../level-5/">← 漢検5級</a>
  <a href="../">漢検への道</a>
  <a href="#review">音楽と動画</a>
  <a href="../level-3/">漢検3級 →</a>
</div>
<div class="lesson-art">
  <img src="{PREFIX}/kml/assets/studies/potato.jpg" alt="芋" width="{width}" height="{height}">
</div>
<h1 class="school-title">漢検4級</h1>
<p class="school-range">常用漢字表の中学校以降の漢字のうち313字 · 累計1,339字</p>
<p class="school-path">漢字を学ぶ → 読み方とことば → 音楽と動画で復習</p>
<p class="kanken-en" lang="en">Level 4. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.</p>
<p class="kanken-en kanken-orient" lang="en">Sixteen lessons are ready, with readings and words. <a href="../?lang=en">All levels</a> · <a href="/learn/">English learning choices</a></p>
<main>
<nav class="school-doors" aria-label="漢検4級の課">
{chr(10).join(doors)}
</nav>
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLI-ULFjSKz58" target="_blank" rel="noopener noreferrer">小学校以降の常用漢字<br><span style="font-size:0.82rem;font-weight:400">漢検4級–2級 · one collection</span></a>
  </div>
</section>
</main>
<p class="sg-disclaimer">{notice}</p>
<script src="{PREFIX}/kml/assets/site/js/kml.js"></script>
</body>
</html>
"""


def level3_entrance(rows: list[dict]) -> str:
    """漢検3級 overview: the same entrance shape as 漢検4級."""
    hero = ROOT / "kml/assets/studies/whale.jpg"
    if not hero.is_file():
        fail(f"Missing 3級 hero {hero}")
    try:
        from PIL import Image
    except ImportError:
        fail("Cannot read the 3級 hero size")
    with Image.open(hero) as image:
        width, height = image.size
    if abs(width / height - 16 / 9) > 0.015:
        fail(f"3級 hero is {width}×{height}, not 16:9")
    doors = []
    for number, lesson in enumerate(lessons_for("3", rows), start=1):
        kanji = " ".join(record["kanji"] for record in lesson)
        doors.append(
            f'<a class="school-door" href="lesson-{number:02d}.html">\n'
            f'  <span class="school-door-kicker">第{number}課 · {len(lesson)}字</span>\n'
            f'  <span class="school-door-title">{esc(lesson[0]["kanji"])} 〜 {esc(lesson[-1]["kanji"])}</span>\n'
            f'  <span class="school-door-kanji" lang="ja">{esc(kanji)}</span>\n'
            "</a>"
        )
    notice = (ROOT / "school-grade/partials/disclaimer.html").read_text(encoding="utf-8").strip()
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="漢検3級。常用漢字表の中学校以降の漢字のうち284字。累計1,623字。">
<title>漢検3級</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Yomogi&family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/compounds-lesson.css">
<link rel="stylesheet" href="{PREFIX}/school-grade/css/school-grade.css?v=levelnav">
<script>
  if (new URLSearchParams(location.search).get("lang") === "en") {{
    document.documentElement.setAttribute("data-kanken-lang", "en");
  }}
</script>
<script src="{PREFIX}/assets/js/kanken-lang.js" defer></script>
</head>
<body id="top">
<div class="navbar navbar-levels">
  <a href="../level-4/">← 漢検4級</a>
  <a href="../">漢検への道</a>
  <a href="#review">音楽と動画</a>
  <a href="../level-jun2/">漢検準2級 →</a>
</div>
<div class="lesson-art">
  <img src="{PREFIX}/kml/assets/studies/whale.jpg" alt="鯨" width="{width}" height="{height}">
</div>
<h1 class="school-title">漢検3級</h1>
<p class="school-range">常用漢字表の中学校以降の漢字のうち284字 · 累計1,623字</p>
<p class="school-path">漢字を学ぶ → 読み方とことば → 音楽と動画で復習</p>
<p class="kanken-en" lang="en">Level 3. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.</p>
<p class="kanken-en kanken-orient" lang="en">Fourteen lessons are ready, with readings and words. <a href="../?lang=en">All levels</a> · <a href="/learn/">English learning choices</a></p>
<main>
<nav class="school-doors" aria-label="漢検3級の課">
{chr(10).join(doors)}
</nav>
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLI-ULFjSKz58" target="_blank" rel="noopener noreferrer">小学校以降の常用漢字<br><span style="font-size:0.82rem;font-weight:400">漢検4級–2級 · one collection</span></a>
  </div>
</section>
</main>
<p class="sg-disclaimer">{notice}</p>
<script src="{PREFIX}/kml/assets/site/js/kml.js"></script>
</body>
</html>
"""


def level_pre2_entrance(rows: list[dict]) -> str:
    """漢検準2級 overview: the same entrance shape as 漢検3級."""
    hero = ROOT / "kml/assets/studies/dragon.jpg"
    if not hero.is_file():
        fail(f"Missing 準2級 hero {hero}")
    try:
        from PIL import Image
    except ImportError:
        fail("Cannot read the 準2級 hero size")
    with Image.open(hero) as image:
        width, height = image.size
    if abs(width / height - 16 / 9) > 0.015:
        fail(f"準2級 hero is {width}×{height}, not 16:9")
    doors = []
    for number, lesson in enumerate(lessons_for("pre2", rows), start=1):
        kanji = " ".join(record["kanji"] for record in lesson)
        doors.append(
            f'<a class="school-door" href="lesson-{number:02d}.html">\n'
            f'  <span class="school-door-kicker">第{number}課 · {len(lesson)}字</span>\n'
            f'  <span class="school-door-title">{esc(lesson[0]["kanji"])} 〜 {esc(lesson[-1]["kanji"])}</span>\n'
            f'  <span class="school-door-kanji" lang="ja">{esc(kanji)}</span>\n'
            "</a>"
        )
    notice = (ROOT / "school-grade/partials/disclaimer.html").read_text(encoding="utf-8").strip()
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="漢検準2級。常用漢字表の中学校以降の漢字のうち328字。累計1,951字。">
<title>漢検準2級</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Yomogi&family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/compounds-lesson.css">
<link rel="stylesheet" href="{PREFIX}/school-grade/css/school-grade.css?v=levelnav">
<script>
  if (new URLSearchParams(location.search).get("lang") === "en") {{
    document.documentElement.setAttribute("data-kanken-lang", "en");
  }}
</script>
<script src="{PREFIX}/assets/js/kanken-lang.js" defer></script>
</head>
<body id="top">
<div class="navbar navbar-levels">
  <a href="../level-3/">← 漢検3級</a>
  <a href="../">漢検への道</a>
  <a href="#review">音楽と動画</a>
  <a href="../level-2/">漢検2級 →</a>
</div>
<div class="lesson-art">
  <img src="{PREFIX}/kml/assets/studies/dragon.jpg" alt="竜" width="{width}" height="{height}">
</div>
<h1 class="school-title">漢検準2級</h1>
<p class="school-range">常用漢字表の中学校以降の漢字のうち328字 · 累計1,951字</p>
<p class="school-path">漢字を学ぶ → 読み方とことば → 音楽と動画で復習</p>
<p class="kanken-en" lang="en">Level Pre-2. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.</p>
<p class="kanken-en kanken-orient" lang="en">Sixteen lessons are ready, with readings and words. <a href="../?lang=en">All levels</a> · <a href="/learn/">English learning choices</a></p>
<main>
<nav class="school-doors" aria-label="漢検準2級の課">
{chr(10).join(doors)}
</nav>
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLI-ULFjSKz58" target="_blank" rel="noopener noreferrer">小学校以降の常用漢字<br><span style="font-size:0.82rem;font-weight:400">漢検4級–2級 · one collection</span></a>
  </div>
</section>
</main>
<p class="sg-disclaimer">{notice}</p>
<script src="{PREFIX}/kml/assets/site/js/kml.js"></script>
</body>
</html>
"""


def level2_entrance(rows: list[dict]) -> str:
    """漢検2級 overview: the same entrance shape as 漢検準2級. This is the last level."""
    hero = ROOT / "kml/assets/studies/crane.jpg"
    if not hero.is_file():
        fail(f"Missing 2級 hero {hero}")
    try:
        from PIL import Image
    except ImportError:
        fail("Cannot read the 2級 hero size")
    with Image.open(hero) as image:
        width, height = image.size
    if abs(width / height - 16 / 9) > 0.015:
        fail(f"2級 hero is {width}×{height}, not 16:9")
    doors = []
    for number, lesson in enumerate(lessons_for("2", rows), start=1):
        kanji = " ".join(record["kanji"] for record in lesson)
        doors.append(
            f'<a class="school-door" href="lesson-{number:02d}.html">\n'
            f'  <span class="school-door-kicker">第{number}課 · {len(lesson)}字</span>\n'
            f'  <span class="school-door-title">{esc(lesson[0]["kanji"])} 〜 {esc(lesson[-1]["kanji"])}</span>\n'
            f'  <span class="school-door-kanji" lang="ja">{esc(kanji)}</span>\n'
            "</a>"
        )
    notice = (ROOT / "school-grade/partials/disclaimer.html").read_text(encoding="utf-8").strip()
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="漢検2級。常用漢字表の中学校以降の漢字のうち185字。累計2,136字。">
<title>漢検2級</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Yomogi&family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="{PREFIX}/kml/assets/site/css/compounds-lesson.css">
<link rel="stylesheet" href="{PREFIX}/school-grade/css/school-grade.css?v=levelnav">
<script>
  if (new URLSearchParams(location.search).get("lang") === "en") {{
    document.documentElement.setAttribute("data-kanken-lang", "en");
  }}
</script>
<script src="{PREFIX}/assets/js/kanken-lang.js" defer></script>
</head>
<body id="top">
<div class="navbar navbar-levels">
  <a href="../level-jun2/">← 漢検準2級</a>
  <a href="../">漢検への道</a>
  <a href="#review">音楽と動画</a>
</div>
<div class="lesson-art">
  <img src="{PREFIX}/kml/assets/studies/crane.jpg" alt="鶴" width="{width}" height="{height}">
</div>
<h1 class="school-title">漢検2級</h1>
<p class="school-range">常用漢字表の中学校以降の漢字のうち185字 · 累計2,136字</p>
<p class="school-path">漢字を学ぶ → 読み方とことば → 音楽と動画で復習</p>
<p class="kanken-en" lang="en">Level 2, the advanced end. Level 10 is beginner and Level 2 is advanced. This page is in Japanese.</p>
<p class="kanken-en kanken-orient" lang="en">Nine lessons are ready, with readings and words. <a href="../?lang=en">All levels</a> · <a href="/learn/">English learning choices</a></p>
<main>
<nav class="school-doors" aria-label="漢検2級の課">
{chr(10).join(doors)}
</nav>
<section class="school-review" id="review" aria-labelledby="review-heading">
  <h2 id="review-heading"><span lang="ja">音楽と動画で復習</span></h2>
  <p>勉強したあとで、この級の歌と動画を見ます。</p>
  <div class="cta">
  <a class="btn-compounds" href="https://www.youtube.com/playlist?list=PLI-ULFjSKz58" target="_blank" rel="noopener noreferrer">小学校以降の常用漢字<br><span style="font-size:0.82rem;font-weight:400">漢検4級–2級 · one collection</span></a>
  </div>
</section>
</main>
<p class="sg-disclaimer">{notice}</p>
<script src="{PREFIX}/kml/assets/site/js/kml.js"></script>
</body>
</html>
"""


def page_for(level: str, rows: list[dict]) -> str:
    label = LABEL[level]
    position = CHAIN.index(level)
    prev_level = CHAIN[position - 1]
    prev_link = f'<a class="pathway-nav-back" href="{esc(level_href(prev_level))}">漢検{LABEL[prev_level]}</a>'
    if position + 1 < len(CHAIN):
        next_level = CHAIN[position + 1]
        next_link = f'<a class="pathway-nav-next" href="{esc(level_href(next_level))}">漢検{LABEL[next_level]}</a>'
    else:
        next_link = '<span class="pathway-nav-next"></span>'
    count = len(rows)
    description = f"漢検{label}。新しく学ぶ{count}字。累計{CUMULATIVE[level]:,}字。各字から、KMLの学習ページと書き順を開けます。"
    return f"""<!DOCTYPE html>
<html lang="ja" class="museum-page">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>漢検{esc(label)} — Kanji・Music・Landscape</title>
  <meta name="description" content="{esc(description)}" />
  <meta name="theme-color" content="#171512" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{PREFIX}/assets/css/museum-room.css" />
  <script>
    if (new URLSearchParams(location.search).get("lang") === "en") {{
      document.documentElement.setAttribute("data-kanken-lang", "en");
    }}
  </script>
  <script src="{PREFIX}/assets/js/museum-room.js" defer></script>
  <script src="{PREFIX}/assets/js/kanken-lang.js" defer></script>
  <script src="{PREFIX}/assets/js/grade-index-hero.js" defer></script>
</head>
<body class="museum-page">
  <a class="skip-link" href="#characters">漢字一覧へスキップ</a>
  <header class="museum-header">
    <div class="museum-header-inner">
      <a class="museum-brand" href="{PREFIX}/ja/index.html">Kanji・Music・Landscape</a>
      <nav aria-label="メインナビ">
        <ul class="museum-nav">
          <li><a href="/start-here/rooms/">はじめに</a></li>
          <li><a href="/kml/vocabulary/">語彙</a></li>
          <li><a href="/kanken/" aria-current="page">漢検への道</a></li>
          <li><a href="/kml/contents/books/">漢字の学び</a></li>
          <li><a href="/ja/collections/">映像コレクション</a></li>
          <li><a href="/ja/">ホーム</a></li>
        </ul>
      </nav>
    </div>
  </header>
  <main>
    <section class="room-hero" data-grade-index="kanken/{SLUG[level]}" aria-labelledby="pathway-heading">
      <div class="room-hero-media" aria-hidden="true">
        <img src="{HERO_IMAGE}" alt="" width="1672" height="941" fetchpriority="high" />
        <div class="room-hero-veil"></div>
      </div>
      <div class="room-hero-inner">
        <p class="room-hero-brand">Kanji・Music・Landscape</p>
        <p class="room-eyebrow">漢検への道</p>
        <h1 id="pathway-heading">漢検{esc(label)}</h1>
        <p class="room-hero-lead">新しく学ぶ{count}字 · 累計{CUMULATIVE[level]:,}字</p>
        <p class="room-hero-lead kanken-en" lang="en">{esc(EN_LEAD[level])}</p>
      </div>
      <a class="room-hero-scroll" href="#characters" aria-label="先へ進む">
        <span class="room-hero-scroll-line" aria-hidden="true"></span>
      </a>
    </section>
    <section class="room-section" id="characters" aria-labelledby="characters-heading">
      <div class="room-container">
        <nav class="pathway-nav" aria-label="級">
          {prev_link}
          <span class="pathway-nav-status">漢検{esc(label)}</span>
          {next_link}
        </nav>
        <p class="kanken-notice">KMLは日本漢字能力検定協会とは関係がありません。</p>
        <p class="kanken-en kanken-orient" lang="en">{esc(EN_ORIENT.get(level, "This level’s own lessons are still in preparation. Each character opens an existing KML lesson in Japanese."))} <a href="/kanken/?lang=en">All levels</a> · <a href="/learn/">English learning choices</a></p>
{body_for(level, rows)}
        <div class="room-actions">
          <a class="museum-btn museum-btn--quiet" href="../">漢検への道</a>
        </div>
      </div>
    </section>
  </main>
  <footer class="museum-footer">
    <div class="museum-footer-inner">
      <nav aria-label="フッター">
        <a href="/ja/journey/">学びの道</a>
        <a href="/statistics/">統計</a>
        <a href="/" hreflang="en" lang="en">English</a>
      </nav>
      <p>© <span id="copyrightYear">2026</span> SanSymeon Productions</p>
    </div>
  </footer>
</body>
</html>
"""


def check_target(page: Path, href: str) -> None:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        fail(f"{page.relative_to(ROOT)} links off-site: {href}")
    if parsed.path.startswith("/"):
        target = (ROOT / unquote(parsed.path).lstrip("/")).resolve()
    elif parsed.path:
        target = (page.parent / unquote(parsed.path)).resolve()
    else:
        target = page.resolve()
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        fail(f"{page.relative_to(ROOT)} missing target {href}")
    fragment = unquote(parsed.fragment)
    if fragment and f'id="{fragment}"' not in target.read_text(errors="replace"):
        fail(f"{page.relative_to(ROOT)} missing #{fragment} in {target.relative_to(ROOT)}")


def verify(by_level: dict[str, list[dict]]) -> None:
    counted = {"on": 0, "kun": 0}
    for level, slug in SLUG.items():
        path = OUT / slug / "index.html"
        text = path.read_text()
        found = re.findall(r'data-kanji="([^"]+)"', text)
        if level in LESSON_LEVELS:
            if found or 'class="kanken-reference"' in text or 'id="characters"' in text:
                fail(f"漢検{LABEL[level]} overview still includes the character index")
            if 'class="lesson-art"' not in text or 'class="school-doors"' not in text or 'id="review"' not in text:
                fail(f"漢検{LABEL[level]} entrance is missing the hero, lesson doors, or review")
        elif found != [r["kanji"] for r in by_level[level]]:
            fail(f"漢検{LABEL[level]} lists {len(found)} characters, expected {EXPECTED[level]} in order")
        scanned = text
        if level in LESSON_LEVELS:
            scanned = re.sub(r'<section class="school-review".*?</section>', " ", text, count=1, flags=re.S)
        if re.search(r"youtube|playlist", scanned, re.I):
            fail(f"漢検{LABEL[level]} links YouTube outside its lesson review")
        if "kanken-keyword" in text:
            fail(f"漢検{LABEL[level]} still shows English keywords")
        main = re.search(r"<main>(.*)</main>", scanned, re.S).group(1)
        visible = re.sub(
            r"<([a-z0-9]+)\b[^>]*class=\"[^\"]*kanken-en[^\"]*\"[^>]*>.*?</\1>",
            " ",
            main,
            flags=re.S,
        )
        latin = set(re.findall(r"[A-Za-z]{2,}", re.sub(r"<[^>]+>", " ", visible))) - ALLOWED_LATIN
        if latin:
            fail(f"漢検{LABEL[level]} shows Latin text: {sorted(latin)[:8]}")
        if level not in LESSON_LEVELS:
            for chunk in text.split('<li class="kanken-row"')[1:]:
                row = chunk.split("</li>", 1)[0]
                kanji = re.search(r'data-kanji="([^"]+)"', row).group(1)
                expected = reference_readings(kanji)
                for kind in ("on", "kun"):
                    shown = re.search(rf'<span class="kanken-{kind}"><span class="kanken-reading-kind">.</span>([^<]*)</span>', row)
                    shown_list = html.unescape(shown.group(1)).split("、") if shown else []
                    if shown_list != expected[kind]:
                        fail(f"{kanji} shows {kind} {shown_list}, the reference has {expected[kind]}")
                    counted[kind] += len(shown_list)
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("https://fonts.", "https://www.youtube.com/")):
                continue
            check_target(path, html.unescape(href))
    for kind in ("on", "kun"):
        expected = sum(
            len(reference_readings(r["kanji"])[kind])
            for level in SLUG
            if level not in LESSON_LEVELS
            for r in by_level[level]
        )
        if counted[kind] != expected:
            fail(f"pages show {counted[kind]} {kind} readings, expected {expected}")
    print(f"readings shown: 音 {counted['on']}, 訓 {counted['kun']} (10級 adds the rest of 2,352 / 2,036)")


def build() -> None:
    by_level = level_rows()
    for level, slug in SLUG.items():
        folder = OUT / slug
        folder.mkdir(parents=True, exist_ok=True)
        if level == "9":
            page = level9_entrance(by_level[level])
        elif level == "8":
            page = level8_entrance(by_level[level])
        elif level == "7":
            page = level7_entrance(by_level[level])
        elif level == "6":
            page = level6_entrance(by_level[level])
        elif level == "5":
            page = level5_entrance(by_level[level])
        elif level == "4":
            page = level4_entrance(by_level[level])
        elif level == "3":
            page = level3_entrance(by_level[level])
        elif level == "pre2":
            page = level_pre2_entrance(by_level[level])
        elif level == "2":
            page = level2_entrance(by_level[level])
        else:
            page = page_for(level, by_level[level])
        (folder / "index.html").write_text(page)
    verify(by_level)
    for level in CHAIN:
        print(f"漢検{LABEL[level]} {len(by_level[level])}字")
    print("validation passed")


def write_level9() -> None:
    by_level = level_rows()
    path = OUT / "level-9" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(level9_entrance(by_level["9"]))
    print(f"Wrote {path.relative_to(ROOT)}")


def write_level6() -> None:
    by_level = level_rows()
    path = OUT / "level-6" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(level6_entrance(by_level["6"]))
    print(f"Wrote {path.relative_to(ROOT)}")


def write_level3() -> None:
    by_level = level_rows()
    path = OUT / "level-3" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(level3_entrance(by_level["3"]))
    print(f"Wrote {path.relative_to(ROOT)}")


def write_level_pre2() -> None:
    by_level = level_rows()
    path = OUT / "level-jun2" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(level_pre2_entrance(by_level["pre2"]))
    print(f"Wrote {path.relative_to(ROOT)}")


def write_level2() -> None:
    by_level = level_rows()
    path = OUT / "level-2" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(level2_entrance(by_level["2"]))
    print(f"Wrote {path.relative_to(ROOT)}")


def write_level4() -> None:
    by_level = level_rows()
    path = OUT / "level-4" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(level4_entrance(by_level["4"]))
    print(f"Wrote {path.relative_to(ROOT)}")


def write_level5() -> None:
    by_level = level_rows()
    path = OUT / "level-5" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(level5_entrance(by_level["5"]))
    print(f"Wrote {path.relative_to(ROOT)}")


def write_level7() -> None:
    by_level = level_rows()
    path = OUT / "level-7" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(level7_entrance(by_level["7"]))
    print(f"Wrote {path.relative_to(ROOT)}")


def write_level8() -> None:
    by_level = level_rows()
    path = OUT / "level-8" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(level8_entrance(by_level["8"]))
    print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    if "--level9" in sys.argv:
        write_level9()
    elif "--level8" in sys.argv:
        write_level8()
    elif "--level7" in sys.argv:
        write_level7()
    elif "--level6" in sys.argv:
        write_level6()
    elif "--level5" in sys.argv:
        write_level5()
    elif "--level4" in sys.argv:
        write_level4()
    elif "--level3" in sys.argv:
        write_level3()
    elif "--levelpre2" in sys.argv:
        write_level_pre2()
    elif "--level2" in sys.argv:
        write_level2()
    else:
        build()
