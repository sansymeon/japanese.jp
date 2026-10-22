#!/usr/bin/env python3
"""Build the Japanese-only 漢検 level pages from existing KML data.

Reads:
  kml/data/kanji/kanken_index.json        level, lesson link, stroke page, readings
  kml/analytics/reference/joyo_kanji.csv  常用漢字表 (2010) 掲載順
  kml/tools/ambient/collections/grade_2/grade_2_compounds_school_0[1-8].json
                                          9級 lesson cuts (checked, not copied)

Writes kanken/level-{9,8,7,6,5,4,3,jun2,2}/index.html. 漢検10級 is the
school-grade pathway at /school-grade/grade-1/ and is not written here.

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
LESSON_LEVELS = {"9"}
PENDING_LESSONS = {"8", "7", "6", "5"}
HERO_IMAGE = "/kanken/kanken_hero_image.jpg"
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


def lessons_for(level: str, rows: list[dict]) -> list[list[dict]]:
    lessons = [rows[i:i + LESSON_SIZE] for i in range(0, len(rows), LESSON_SIZE)]
    if level == "9":
        cuts = film_cuts()
        if [[r["kanji"] for r in lesson] for lesson in lessons] != cuts:
            fail("9級 lessons differ from the grade 2 熟語 film cuts")
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
        return f"{PREFIX}/school-grade/grade-1/"
    return f"../{SLUG[level]}/"


def body_for(level: str, rows: list[dict]) -> str:
    label = LABEL[level]
    if level in LESSON_LEVELS:
        units = []
        for number, lesson in enumerate(lessons_for(level, rows), start=1):
            items = "\n".join(row_html(record) for record in lesson)
            units.append(f"""        <section class="kanken-unit" aria-labelledby="unit-{number}">
          <header class="kanken-unit-head">
            <h3 id="unit-{number}">第{number}課</h3>
            <span class="kanken-unit-range" lang="ja">{esc(lesson[0]["kanji"])} 〜 {esc(lesson[-1]["kanji"])} · {len(lesson)}字</span>
          </header>
          <ul class="kanken-index">
{items}
          </ul>
        </section>""")
        return (
            f"""        <header class="room-section-head reveal">
          <p class="room-eyebrow">全{len(units)}課</p>
          <h2 id="characters-heading">漢検{label}で新しく学ぶ漢字</h2>
          <p>各字から、KMLの学習ページと書き順を開けます。<span class="kanken-pending-note">読み方とことばのページは準備中です。</span></p>
        </header>
{reading_note(rows)}
        <div class="kanken-lessons">
"""
            + "\n".join(units)
            + "\n        </div>"
        )
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
  <script src="{PREFIX}/assets/js/museum-room.js" defer></script>
  <script src="{PREFIX}/assets/js/grade-index-hero.js" defer></script>
</head>
<body class="museum-page">
  <a class="skip-link" href="#characters">漢字一覧へスキップ</a>
  <header class="museum-header">
    <div class="museum-header-inner">
      <a class="museum-brand" href="{PREFIX}/ja/index.html">Kanji・Music・Landscape</a>
      <nav aria-label="メインナビ">
        <ul class="museum-nav">
          <li><a href="{PREFIX}/ja/journey/">学びの道</a></li>
          <li><a href="{PREFIX}/kml/contents/books/">漢字の学び</a></li>
          <li><a href="{PREFIX}/kanken/" aria-current="page">漢検への道</a></li>
          <li><a href="{PREFIX}/ja/collections/">映像コレクション</a></li>
          <li><a href="{PREFIX}/ja/publications/">出版物</a></li>
          <li><a href="{PREFIX}/ja/index.html">ホーム</a></li>
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
        <a href="{PREFIX}/ja/index.html">ホーム</a>
        <a href="../">漢検への道</a>
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
    target = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page.resolve()
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
        if found != [r["kanji"] for r in by_level[level]]:
            fail(f"漢検{LABEL[level]} lists {len(found)} characters, expected {EXPECTED[level]} in order")
        if re.search(r"youtube|playlist", text, re.I):
            fail(f"漢検{LABEL[level]} links YouTube")
        if "kanken-keyword" in text:
            fail(f"漢検{LABEL[level]} still shows English keywords")
        main = re.search(r"<main>(.*)</main>", text, re.S).group(1)
        latin = set(re.findall(r"[A-Za-z]{2,}", re.sub(r"<[^>]+>", " ", main))) - ALLOWED_LATIN
        if latin:
            fail(f"漢検{LABEL[level]} shows Latin text: {sorted(latin)[:8]}")
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
            if href.startswith("https://fonts."):
                continue
            check_target(path, html.unescape(href))
    for kind in ("on", "kun"):
        expected = sum(len(reference_readings(r["kanji"])[kind]) for level in SLUG for r in by_level[level])
        if counted[kind] != expected:
            fail(f"pages show {counted[kind]} {kind} readings, expected {expected}")
    print(f"readings shown: 音 {counted['on']}, 訓 {counted['kun']} (10級 adds the rest of 2,352 / 2,036)")


def build() -> None:
    by_level = level_rows()
    for level, slug in SLUG.items():
        folder = OUT / slug
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(page_for(level, by_level[level]))
    verify(by_level)
    for level in CHAIN:
        print(f"漢検{LABEL[level]} {len(by_level[level])}字")
    print("validation passed")


if __name__ == "__main__":
    build()
