#!/usr/bin/env python3
"""Build the 漢検 pointer index and the public pathway pages.

Reads the February 2020 級別漢字表 and existing KML records.
Writes pointers only. Does not copy compounds, component trees, or verses,
and does not modify lessons, films, or playlists.
"""

from __future__ import annotations

import csv
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
PDF = Path("/tmp/kanken_2020_levels.pdf")
PDF_URL = "https://www.kanken.or.jp/kanken/outline/data/outline_degree_national_list20200217.pdf"
OFFICIAL_PATH = ROOT / "kml/data/kanji/kanken_official_2020.json"
INDEX_PATH = ROOT / "kml/data/kanji/kanken_index.json"
COMPONENT_DB = ROOT / "kml/data/kanji/kml_component_database.json"
PRODUCTION = ROOT / "kml/data/kanji/kanji_production.csv"
LESSON_HTML = ROOT / "kml/contents/books/book_01/lessons"
COMPOUNDS = ROOT / "kml/data/compounds"
STROKE_PAGES = ROOT / "kml/tools/strokes/pages"
COLLECTIONS = ROOT / "kml/tools/ambient/collections"

LEVEL_ORDER = ["10", "9", "8", "7", "6", "5", "4", "3", "pre2", "2"]
EXPECTED = {
    "10": 80,
    "9": 160,
    "8": 200,
    "7": 202,
    "6": 193,
    "5": 191,
    "4": 313,
    "3": 284,
    "pre2": 328,
    "2": 185,
}
LABEL = {
    "10": "10級",
    "9": "9級",
    "8": "8級",
    "7": "7級",
    "6": "6級",
    "5": "5級",
    "4": "4級",
    "3": "3級",
    "pre2": "準2級",
    "2": "2級",
}
CUMULATIVE = {
    "10": 80,
    "9": 240,
    "8": 440,
    "7": 642,
    "6": 835,
    "5": 1026,
    "4": 1339,
    "3": 1623,
    "pre2": 1951,
    "2": 2136,
}
GRADE_FOR_LEVEL = {"10": 1, "9": 2, "8": 3, "7": 4, "6": 5, "5": 6}
LEVEL_FOR_GRADE = {v: k for k, v in GRADE_FOR_LEVEL.items()}
UPPER = ["4", "3", "pre2", "2"]
PAGE = {"4": "level-4", "3": "level-3", "pre2": "level-jun2", "2": "level-2"}

HEISIG_ONLY = set("介塔暦朱枯桃燥狂狩薄迫黙膜苗鎮呈寛朴栓棚漠猫珠眺迅釣鉢銘旺昧椅沃玩脊苛")
TABLE_FORMS = {
    "剥": {"kanji": "剝", "slug": "peel"},
    "叱": {"kanji": "𠮟", "slug": "scold_old"},
    "填": {"kanji": "塡", "slug": "fill_in"},
    "頬": {"kanji": "頰", "slug": "cheek_old"},
}
BEYOND = {
    "剥": {"entry": "剥", "note": "compound"},
    "叱": {"entry": "叱", "note": "compound"},
    "填": {"entry": "填", "note": "compound"},
    "頬": {"entry": "頬杖", "note": "word-entry"},
}

ACTIVITY_KINDS = [
    ("bushuSong", "bushu-song"),
    ("listenWrite", "listen-write"),
    ("componentSong", "component-song"),
    ("jukugoSong", "jukugo-song"),
    ("worksheet", "worksheet"),
    ("listeningCloze", "listening-cloze"),
    ("musicalReview", "musical-review"),
]

POST_PLAYLIST = "PLI-ULFjSKz58"
BEYOND_PLAYLIST = "PLFcXrI1lQAqI"
# Shared by every 漢検 pathway hero. Root-absolute so page depth does not matter.
HERO_IMAGE = "/kanken/kanken_hero_image.jpg"


def fail(message: str) -> None:
    print(f"VALIDATION FAILED: {message}", file=sys.stderr)
    sys.exit(1)


def is_ideo(text: str) -> bool:
    if len(text) != 1:
        return False
    code = ord(text)
    return (0x3400 <= code <= 0x9FFF) or code > 0x20000


def lesson_filename(lesson: int) -> str:
    if lesson < 10:
        return f"lesson_{lesson:02d}.html"
    return f"lesson_{lesson}.html"


def url_slug(slug: str) -> str:
    """Encode a reviewed slug for a public URL. The source slug is unchanged."""
    return quote(slug, safe="")


def activity_id(level: str, kanji: str, kind_slug: str) -> str:
    return f"kanken.{level}.{ord(kanji):04x}.{kind_slug}"


def activities_for(level: str, kanji: str) -> dict:
    return {
        key: {"id": activity_id(level, kanji, slug), "href": None}
        for key, slug in ACTIVITY_KINDS
    }


def extract_official() -> dict[str, list[str]]:
    if not PDF.exists():
        fail(f"missing official PDF at {PDF}")
    xml = subprocess.check_output(
        ["pdftotext", "-bbox-layout", str(PDF), "-"], text=True, errors="replace"
    )
    pages = xml.split("<page ")[1:]
    word_re = re.compile(
        r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>',
        re.S,
    )
    sequences = []
    for page in pages:
        items = []
        for xmin, ymin, xmax, ymax, text in word_re.findall(page):
            text = text.strip()
            if not is_ideo(text):
                continue
            width = round(float(xmax) - float(xmin), 1)
            height = round(float(ymax) - float(ymin), 1)
            if (width, height) in ((20.0, 24.5), (24.0, 29.4)):
                items.append((float(ymin), float(xmin), text))
        items.sort()
        seen = set()
        sequence = []
        for _y, _x, text in items:
            if text not in seen:
                seen.add(text)
                sequence.append(text)
        sequences.append(sequence)
    levels = {
        "10": sequences[1],
        "9": sequences[2],
        "8": sequences[3],
        "7": sequences[4],
        "6": sequences[5],
        "5": sequences[6],
        "4": sequences[7] + sequences[8],
        "3": sequences[9] + sequences[10],
        "pre2": sequences[11] + sequences[12],
        "2": sequences[13] + sequences[14],
    }
    for key, expected in EXPECTED.items():
        if len(levels[key]) != expected or len(set(levels[key])) != expected:
            fail(f"level {key} extracted {len(levels[key])} unique {len(set(levels[key]))}, expected {expected}")
    flat = [ch for key in LEVEL_ORDER for ch in levels[key]]
    if len(flat) != 2136 or len(set(flat)) != 2136:
        fail(f"official inventory is {len(set(flat))} unique / {len(flat)} listed")
    return levels


def load_csv(path: Path) -> dict[str, dict]:
    rows = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            rows.setdefault(row["kanji"], row)
    return rows


def soundtrack_kanji(directory: Path, pattern: str) -> list[str]:
    found = []
    for path in sorted(directory.glob(pattern)):
        data = json.loads(path.read_text())
        found.extend(scene["kanji"] for scene in data["scenes"] if "kanji" in scene)
    return found


def lesson_playlist(path: Path, cache: dict) -> str:
    if path not in cache:
        match = re.search(r"playlist\?list=([A-Za-z0-9_-]+)", path.read_text(errors="replace"))
        cache[path] = match.group(1) if match else ""
    return cache[path]


def build() -> None:
    levels = extract_official()
    components = json.loads(COMPONENT_DB.read_text())["kanji"]
    production = load_csv(PRODUCTION)
    compound_cache: dict[int, set[str]] = {}
    html_cache: dict[Path, str] = {}
    playlist_cache: dict[Path, str] = {}

    elementary: dict[str, int] = {}
    for grade in range(1, 7):
        chars = soundtrack_kanji(
            COLLECTIONS / f"grade_{grade}",
            f"grade_{grade}_0[1-9].json",
        )
        for char in chars:
            if char in elementary:
                fail(f"{char} appears in more than one elementary grade")
            elementary[char] = grade

    post = soundtrack_kanji(COLLECTIONS / "post_elementary", "post_elementary_[0-9][0-9].json")
    if len(post) != len(set(post)):
        fail("post-elementary soundtrack repeats a character")
    post_set = set(post)

    records = []
    for level in LEVEL_ORDER:
        for kanji in levels[level]:
            component = components.get(kanji)
            if not component:
                fail(f"{kanji} missing from component database")
            lesson = int(component["lesson"])
            slug = component["slug"]
            keyword = component.get("keyword") or ""
            if not keyword:
                fail(f"{kanji} has no reviewed keyword")
            row = production.get(kanji)
            if not row:
                fail(f"{kanji} missing from kanji_production.csv")
            heisig = int(row["heisig_number"])
            lesson_path = LESSON_HTML / lesson_filename(lesson)
            if not lesson_path.exists():
                fail(f"{kanji} lesson file missing: {lesson_path.name}")
            if lesson_path not in html_cache:
                html_cache[lesson_path] = lesson_path.read_text(errors="replace")
            page = html_cache[lesson_path]
            anchor = f'id="kanji-{slug}"'
            if anchor not in page or f'data-kanji="{kanji}"' not in page:
                fail(f"{kanji} anchor missing in {lesson_path.name}")
            stroke = STROKE_PAGES / f"{slug}.html"
            if not stroke.exists():
                fail(f"{kanji} stroke page missing: {slug}.html")
            playlist = lesson_playlist(lesson_path, playlist_cache)
            if not playlist:
                fail(f"{kanji} lesson page has no playlist id")
            if lesson not in compound_cache:
                compound_name = f"lesson_{lesson:02d}.json" if lesson < 10 else f"lesson_{lesson}.json"
                compound_path = COMPOUNDS / compound_name
                if compound_path.exists():
                    data = json.loads(compound_path.read_text())
                    compound_cache[lesson] = {item["kanji"] for item in data.get("characters", [])}
                else:
                    compound_cache[lesson] = set()
            compounds_ref = None
            if kanji in compound_cache[lesson]:
                compound_name = f"lesson_{lesson:02d}.json" if lesson < 10 else f"lesson_{lesson}.json"
                compounds_ref = f"kml/data/compounds/{compound_name}#{kanji}"

            if kanji in elementary:
                grade = elementary[kanji]
                if LEVEL_FOR_GRADE[grade] != level:
                    fail(f"{kanji} is grade {grade} in the films and {LABEL[level]} in the table")
                membership = "elementary"
                elementary_grade = grade
            elif kanji in post_set:
                if level not in UPPER:
                    fail(f"{kanji} is in the post-elementary films and also {LABEL[level]}")
                membership = "post-elementary"
                elementary_grade = None
            elif kanji in TABLE_FORMS:
                membership = "table-form-filmed-as-alternate"
                elementary_grade = None
            else:
                membership = "heisig-lesson-only"
                elementary_grade = None

            alternate = None
            beyond = None
            if kanji in TABLE_FORMS:
                other = TABLE_FORMS[kanji]["kanji"]
                other_component = components.get(other)
                if not other_component:
                    fail(f"alternate {other} missing from component database")
                other_row = production.get(other)
                if not other_row:
                    fail(f"alternate {other} missing from kanji_production.csv")
                if other not in post_set:
                    fail(f"alternate {other} is not in the post-elementary films")
                other_lesson = int(other_component["lesson"])
                other_slug = other_component["slug"]
                alternate = {
                    "kanji": other,
                    "heisigNumber": int(other_row["heisig_number"]),
                    "lesson": other_lesson,
                    "slug": other_slug,
                    "lessonPage": (
                        f"/kml/contents/books/book_01/lessons/{lesson_filename(other_lesson)}"
                        f"#kanji-{url_slug(other_slug)}"
                    ),
                    "inPostElementaryFilms": True,
                }
                beyond = BEYOND[kanji]

            public_lesson = (
                f"/kml/contents/books/book_01/lessons/{lesson_filename(lesson)}#kanji-{url_slug(slug)}"
            )
            records.append(
                {
                    "kanji": kanji,
                    "introducedAt": level,
                    "heisigNumber": heisig,
                    "lesson": lesson,
                    "slug": slug,
                    "keyword": keyword,
                    "on": (row.get("on_reading") or "").strip(),
                    "kun": (row.get("kun_readings") or "").strip(),
                    "lessonPage": public_lesson,
                    "strokePage": f"/kml/tools/strokes/pages/{url_slug(slug)}.html",
                    "componentsRef": f"kml/data/kanji/kml_component_database.json#{kanji}",
                    "compoundsRef": compounds_ref,
                    "readingsRef": f"kml/data/kanji/kanji_production.csv#{kanji}",
                    "filmMembership": membership,
                    "elementaryGrade": elementary_grade,
                    "lessonPlaylist": {"id": playlist, "scope": "complete-lesson"},
                    "alternateForm": alternate,
                    "beyondJoyo": beyond,
                    "activities": activities_for(level, kanji),
                }
            )

    by_kanji = {record["kanji"]: record for record in records}
    if len(by_kanji) != 2136:
        fail(f"index has {len(by_kanji)} characters")
    only = {record["kanji"] for record in records if record["filmMembership"] == "heisig-lesson-only"}
    if only != HEISIG_ONLY:
        fail(f"heisig-lesson-only set differs: extra {''.join(sorted(only - HEISIG_ONLY))} missing {''.join(sorted(HEISIG_ONLY - only))}")
    filmed_alt = {record["kanji"] for record in records if record["filmMembership"] == "table-form-filmed-as-alternate"}
    if filmed_alt != set(TABLE_FORMS):
        fail(f"table-form set is {''.join(sorted(filmed_alt))}")
    for banned in ["朋", "剝", "𠮟", "塡", "頰"]:
        if banned in by_kanji:
            fail(f"{banned} must not be an index key")
    for level, expected in EXPECTED.items():
        count = sum(1 for record in records if record["introducedAt"] == level)
        if count != expected:
            fail(f"{LABEL[level]} count {count} != {expected}")
    missing_compounds = [record["kanji"] for record in records if not record["compoundsRef"]]
    if missing_compounds:
        fail(f"{len(missing_compounds)} characters have no compounds record, starting {''.join(missing_compounds[:20])}")

    activity_ids = [item["id"] for record in records for item in record["activities"].values()]
    if len(activity_ids) != len(set(activity_ids)):
        fail("activity identifiers are not unique")

    official_doc = {
        "meta": {
            "title": "日本漢字能力検定 級別漢字表（１０級～２級）",
            "sourceDocument": "outline_degree_national_list20200217.pdf",
            "sourceUrl": PDF_URL,
            "publisher": "公益財団法人 日本漢字能力検定協会",
            "version": "2020年2月発表",
            "published": "2020-02",
            "appliesFrom": "2020年度",
            "note": "2020年度からの新配当漢字。10～5級の配当漢字は、2020年度全面実施の小学校学習指導要領の学年別漢字配当表による。",
            "counts": EXPECTED,
            "cumulative": CUMULATIVE,
            "total": 2136,
        },
        "levels": levels,
    }
    index_doc = {
        "meta": {
            "characterCount": 2136,
            "officialSource": official_doc["meta"],
            "activityIdPattern": "kanken.{introducedAt}.{unicodeHex}.{kind}",
            "activityKinds": {key: slug for key, slug in ACTIVITY_KINDS},
            "activityHref": "null until a resource is published at that stable id",
            "lessonPlaylistScope": "complete-lesson means the playlist is the whole Heisig lesson, not a film of one character",
            "postElementaryPlaylist": POST_PLAYLIST,
            "beyondJoyoPlaylist": BEYOND_PLAYLIST,
            "deferred": [
                "lesson_13.json stores a garbled keyword for 眺; the index uses the reviewed keyword stare",
                "沃 has a blank category cell in kanji_master.csv",
                "Lesson 151 study images are missing: peel.jpg, scold_old.jpg, fill_in.jpg, cheek_old.jpg",
                "Compound lists are shorter than the usual five for 漠, 昧, and the Lesson 151 forms",
            ],
        },
        "characters": records,
    }
    OFFICIAL_PATH.write_text(json.dumps(official_doc, ensure_ascii=False, indent=2) + "\n")
    INDEX_PATH.write_text(json.dumps(index_doc, ensure_ascii=False, indent=2) + "\n")
    write_pages(records)
    verify_pages(records)
    print(f"official {OFFICIAL_PATH.relative_to(ROOT)}")
    print(f"index {INDEX_PATH.relative_to(ROOT)} characters {len(records)}")
    print("membership", {key: sum(1 for record in records if record["filmMembership"] == key) for key in ("elementary", "post-elementary", "heisig-lesson-only", "table-form-filmed-as-alternate")})
    print("validation passed")


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def readings(record: dict) -> str:
    parts = [part for part in (record["on"], record["kun"]) if part]
    return " · ".join(parts)


def write_pages(records: list[dict]) -> None:
    """Public pages list only published resources. Activity ids stay in the index JSON."""
    by_level = {level: [record for record in records if record["introducedAt"] == level] for level in LEVEL_ORDER}
    for lang in ("en", "ja"):
        write_entrance(lang, by_level)
        for level in UPPER:
            write_level(lang, level, by_level[level])


def rel_prefix(lang: str, level_page: bool) -> str:
    if lang == "en" and not level_page:
        return ".."
    if lang == "en" and level_page:
        return "../.."
    if lang == "ja" and not level_page:
        return "../.."
    return "../../.."


def write_entrance(lang: str, by_level: dict) -> None:
    root = ROOT / ("kanken" if lang == "en" else "ja/kanken")
    prefix = rel_prefix(lang, False)
    other = f"{prefix}/ja/kanken/" if lang == "en" else f"{prefix}/kanken/"
    home = f"{prefix}/index.html" if lang == "en" else f"{prefix}/ja/index.html"
    elementary = f"{prefix}/elementary/" if lang == "en" else f"{prefix}/ja/elementary/"
    title = "漢検への道 — Kanji・Music・Landscape"
    if lang == "en":
        description = "Path through the 2,136 jōyō kanji of 漢検10級–2級, with music and image. KML is independent of the 日本漢字能力検定協会."
        nav = en_nav(prefix, current=True)
        footer_lang = f'<a href="{esc(other)}" hreflang="ja" lang="ja">日本語</a>'
        skip = "Skip to levels"
        lead = "The 2,136 jōyō kanji through 漢検2級, with music and image."
        notice = "KML is independent of the 日本漢字能力検定協会. This path does not cover every exam task, and it does not guarantee a pass."
        early_heading = "漢検10級–5級"
        early_copy = "Kanji, 熟語, and 書き順. 漢検10級 is the first set. The 漢検9級 films also include 朋, which is outside the table."
        upper_heading = "漢検4級–2級"
        upper_copy = "One published collection. Each character opens its existing lesson."
        beyond_heading = "Beyond Jōyō"
        beyond_copy = "Its own collection. Not a 準1級 or 1級 curriculum."
    else:
        description = "漢検への道。漢検2級までの常用漢字2,136字を学べる。KMLは日本漢字能力検定協会とは関係がありません。"
        nav = ja_nav(prefix, current=True)
        footer_lang = f'<a href="{esc(other)}" hreflang="en" lang="en">English</a>'
        skip = "級へスキップ"
        lead = "漢検2級までの常用漢字2,136字を学べる。"
        notice = "KMLは日本漢字能力検定協会とは関係がありません。検定のすべての出題分野を教えるものではなく、合格を保証するものでもありません。"
        early_heading = "漢検10級–5級"
        early_copy = "漢字・熟語・書き順。漢検10級は最初の配当です。漢検9級の映像には、級別漢字表にない「朋」も含まれます。"
        upper_heading = "漢検4級–2級"
        upper_copy = "映像は一つのコレクションです。各字は、すでにあるレッスンを開きます。"
        beyond_heading = "Beyond Jōyō"
        beyond_copy = "独立したコレクションです。準1級や1級のカリキュラムではありません。"
    grades = []
    for level, grade in (("10", 1), ("9", 2), ("8", 3), ("7", 4), ("6", 5), ("5", 6)):
        count = len(by_level[level])
        school = f"小学{grade}年生の漢字"
        if level == "9":
            school += " · 映像に朋" if lang == "ja" else " · films include 朋"
        grades.append(
            f"""<li class="guidance-item reveal">
            <a class="guidance-link" href="{esc(elementary)}grade-{grade}/">
              <span class="guidance-label">{count}字</span>
              <span>
                <h3 class="guidance-title">漢検{esc(LABEL[level])}</h3>
                <p class="guidance-meta">{esc(school)}</p>
              </span>
            </a>
          </li>
"""
        )
    upper = []
    for level in UPPER:
        count = len(by_level[level])
        upper.append(
            f"""<li class="guidance-item reveal">
            <a class="guidance-link" href="./{PAGE[level]}/">
              <span class="guidance-label">{CUMULATIVE[level]:,}</span>
              <span>
                <h3 class="guidance-title">漢検{esc(LABEL[level])}</h3>
                <p class="guidance-meta">{f'この級で加わる{count}字' if lang == 'ja' else f'{count} new characters'}</p>
              </span>
            </a>
          </li>
"""
        )
    collections = f"{prefix}/collections/" if lang == "en" else f"{prefix}/ja/collections/"
    beyond_label = "Open the collection" if lang == "en" else "コレクションを見る"
    page = f"""<!DOCTYPE html>
<html lang="{lang}" class="museum-page">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <meta name="theme-color" content="#171512" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{prefix}/assets/css/museum-room.css" />
  <script src="{prefix}/assets/js/museum-room.js" defer></script>
</head>
<body class="museum-page">
  <a class="skip-link" href="#levels">{esc(skip)}</a>
  <header class="museum-header">
    <div class="museum-header-inner">
      <a class="museum-brand" href="{esc(home)}">Kanji・Music・Landscape</a>
      <nav aria-label="{'Primary' if lang == 'en' else 'メインナビ'}">
        <ul class="museum-nav">
          {nav}
        </ul>
      </nav>
    </div>
  </header>
  <main>
    <section class="room-hero" aria-labelledby="pathway-heading">
      <div class="room-hero-media" aria-hidden="true">
        <img src="{HERO_IMAGE}" alt="" width="1672" height="941" fetchpriority="high" />
        <div class="room-hero-veil"></div>
      </div>
      <div class="room-hero-inner">
        <p class="room-hero-brand">Kanji・Music・Landscape</p>
        <p class="room-eyebrow">音楽と映像で楽しく学ぶ漢字</p>
        <h1 id="pathway-heading">漢検への道</h1>
        <p class="room-hero-lead">{esc(lead)}</p>
      </div>
      <a class="room-hero-scroll" href="#levels" aria-label="{'Continue' if lang == 'en' else '先へ進む'}">
        <span class="room-hero-scroll-line" aria-hidden="true"></span>
      </a>
    </section>
    <section class="room-section" id="levels" aria-labelledby="early-heading">
      <div class="room-container">
        <p class="kanken-notice">{esc(notice)}</p>
        <header class="room-section-head reveal">
          <p class="room-eyebrow">10級–5級</p>
          <h2 id="early-heading">{esc(early_heading)}</h2>
          <p>{esc(early_copy)}</p>
        </header>
        <ul class="guidance-list">
          {''.join(grades)}
        </ul>
        <header class="room-section-head reveal" id="upper">
          <p class="room-eyebrow">4級–2級</p>
          <h2>{esc(upper_heading)}</h2>
          <p>{esc(upper_copy)}</p>
        </header>
        <ul class="guidance-list">
          {''.join(upper)}
        </ul>
        <header class="room-section-head reveal" id="beyond">
          <p class="room-eyebrow">準1級 · 1級</p>
          <h2>{esc(beyond_heading)}</h2>
          <p>{esc(beyond_copy)}</p>
        </header>
        <div class="room-actions">
          <a class="museum-btn museum-btn--quiet" href="{esc(collections)}">{esc(beyond_label)}</a>
          <a class="museum-btn museum-btn--quiet" href="https://www.youtube.com/playlist?list={BEYOND_PLAYLIST}" target="_blank" rel="noopener noreferrer">YouTube</a>
        </div>
      </div>
    </section>
  </main>
  <footer class="museum-footer">
    <div class="museum-footer-inner">
      <nav aria-label="{'Footer' if lang == 'en' else 'フッター'}">
        <a href="{esc(home)}">{'Home' if lang == 'en' else 'ホーム'}</a>
        <a href="{prefix}/{'ja/' if lang == 'ja' else ''}kanken/" aria-current="page">漢検への道</a>
        {footer_lang}
      </nav>
      <p>© <span id="copyrightYear">2026</span> SanSymeon Productions</p>
    </div>
  </footer>
</body>
</html>
"""
    path = root / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page)


def write_level(lang: str, level: str, rows: list[dict]) -> None:
    folder = ROOT / ("kanken" if lang == "en" else "ja/kanken") / PAGE[level]
    prefix = rel_prefix(lang, True)
    home = f"{prefix}/index.html" if lang == "en" else f"{prefix}/ja/index.html"
    other_root = f"{prefix}/ja/kanken/{PAGE[level]}/" if lang == "en" else f"{prefix}/kanken/{PAGE[level]}/"
    label = LABEL[level]
    index_href = "../"
    position = UPPER.index(level)
    prev_href = "../" if position == 0 else f"../{PAGE[UPPER[position - 1]]}/"
    next_href = None if position == len(UPPER) - 1 else f"../{PAGE[UPPER[position + 1]]}/"
    prev_label = "漢検への道" if position == 0 else f"漢検{LABEL[UPPER[position - 1]]}"
    next_label = "" if next_href is None else f"漢検{LABEL[UPPER[position + 1]]}"
    if lang == "en":
        title = f"漢検{label} — Kanji・Music・Landscape"
        description = f"漢検{label}. {len(rows):,} characters new at this level. {CUMULATIVE[level]:,} including earlier levels. Each character opens an existing KML lesson."
        nav = en_nav(prefix, current=True)
        skip = "Skip to characters"
        lead = f"{len(rows):,} new characters · {CUMULATIVE[level]:,} in all"
        film = "The post-elementary films are one collection. They are not split by level."
        film_btn = "Jōyō collection"
        list_heading = f"Characters new at 漢検{label}"
        list_copy = "Each character opens its lesson and stroke-order page."
        lesson_word = "Lesson"
        stroke_word = "Stroke order"
        notice = "KML is independent of the 日本漢字能力検定協会."
    else:
        title = f"漢検{label} — Kanji・Music・Landscape"
        description = f"漢検{label}。この級で加わる{len(rows)}字。累計{CUMULATIVE[level]:,}字。各字は、すでにあるレッスンを開きます。"
        nav = ja_nav(prefix, current=True)
        skip = "漢字一覧へスキップ"
        lead = f"この級で加わる{len(rows)}字 · 累計{CUMULATIVE[level]:,}字"
        film = "小学校以降の常用漢字の映像は、一つのコレクションです。級ごとには分かれていません。"
        film_btn = "常用漢字コレクション"
        list_heading = f"漢検{label}で加わる漢字"
        list_copy = "各字から、レッスンと書き順を開けます。"
        lesson_word = "レッスン"
        stroke_word = "書き順"
        notice = "KMLは日本漢字能力検定協会とは関係がありません。"
    items = []
    for record in rows:
        alt = ""
        if record["alternateForm"]:
            other = record["alternateForm"]
            other_href = prefix + other["lessonPage"]
            if lang == "en":
                alt = f'<p class="kanken-alt">The published post-elementary films use <a href="{esc(other_href)}">{esc(other["kanji"])}</a>, Lesson {other["lesson"]}.</p>'
            else:
                alt = f'<p class="kanken-alt">公開中の映像では <a href="{esc(other_href)}">{esc(other["kanji"])}</a> を使っています。レッスン{other["lesson"]}です。</p>'
        items.append(
            f"""<li class="kanken-row" data-kanji="{esc(record["kanji"])}">
            <a class="kanken-row-link" href="{esc(prefix + record["lessonPage"])}">
              <span class="kanken-glyph" lang="ja">{esc(record["kanji"])}</span>
              <span class="kanken-keyword">{esc(record["keyword"])}</span>
              <span class="kanken-readings">{esc(readings(record))}</span>
              <span class="kanken-lesson">{esc(lesson_word)} {record["lesson"]}</span>
            </a>
            <a class="kanken-stroke" href="{esc(prefix + record["strokePage"])}">{esc(stroke_word)}</a>
            {alt}
          </li>
"""
        )
    next_link = ""
    if next_href:
        next_link = f'<a class="pathway-nav-next" href="{esc(next_href)}">{esc(next_label)}</a>'
    else:
        next_link = '<span class="pathway-nav-next"></span>'
    page = f"""<!DOCTYPE html>
<html lang="{lang}" class="museum-page">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <meta name="theme-color" content="#171512" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{prefix}/assets/css/museum-room.css" />
  <script src="{prefix}/assets/js/museum-room.js" defer></script>
</head>
<body class="museum-page">
  <a class="skip-link" href="#characters">{esc(skip)}</a>
  <header class="museum-header">
    <div class="museum-header-inner">
      <a class="museum-brand" href="{esc(home)}">Kanji・Music・Landscape</a>
      <nav aria-label="{'Primary' if lang == 'en' else 'メインナビ'}">
        <ul class="museum-nav">
          {nav}
        </ul>
      </nav>
    </div>
  </header>
  <main>
    <section class="room-hero" aria-labelledby="pathway-heading">
      <div class="room-hero-media" aria-hidden="true">
        <img src="{HERO_IMAGE}" alt="" width="1672" height="941" fetchpriority="high" />
        <div class="room-hero-veil"></div>
      </div>
      <div class="room-hero-inner">
        <p class="room-hero-brand">Kanji・Music・Landscape</p>
        <p class="room-eyebrow">漢検への道</p>
        <h1 id="pathway-heading">漢検{esc(label)}</h1>
        <p class="room-hero-lead">{esc(lead)}</p>
      </div>
      <a class="room-hero-scroll" href="#characters" aria-label="{'Continue' if lang == 'en' else '先へ進む'}">
        <span class="room-hero-scroll-line" aria-hidden="true"></span>
      </a>
    </section>
    <section class="room-section" id="characters" aria-labelledby="characters-heading">
      <div class="room-container">
        <nav class="pathway-nav" aria-label="{'Levels' if lang == 'en' else '級'}">
          <a class="pathway-nav-back" href="{esc(prev_href)}">{esc(prev_label)}</a>
          <span class="pathway-nav-status">漢検{esc(label)}</span>
          {next_link}
        </nav>
        <p class="kanken-notice">{esc(notice)}</p>
        <p>{esc(film)}</p>
        <div class="room-actions">
          <a class="museum-btn museum-btn--quiet" href="https://www.youtube.com/playlist?list={POST_PLAYLIST}" target="_blank" rel="noopener noreferrer">{esc(film_btn)}</a>
          <a class="museum-btn museum-btn--quiet" href="{esc(index_href)}">漢検への道</a>
        </div>
        <header class="room-section-head reveal">
          <p class="room-eyebrow">{len(rows)}</p>
          <h2 id="characters-heading">{esc(list_heading)}</h2>
          <p>{esc(list_copy)}</p>
        </header>
        <ul class="kanken-index">
          {''.join(items)}
        </ul>
      </div>
    </section>
  </main>
  <footer class="museum-footer">
    <div class="museum-footer-inner">
      <nav aria-label="{'Footer' if lang == 'en' else 'フッター'}">
        <a href="{esc(home)}">{'Home' if lang == 'en' else 'ホーム'}</a>
        <a href="{esc(index_href)}">漢検への道</a>
        <a href="{esc(other_root)}" hreflang="{'ja' if lang == 'en' else 'en'}" lang="{'ja' if lang == 'en' else 'en'}">{'日本語' if lang == 'en' else 'English'}</a>
      </nav>
      <p>© <span id="copyrightYear">2026</span> SanSymeon Productions</p>
    </div>
  </footer>
</body>
</html>
"""
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.html").write_text(page)


def en_nav(prefix: str, current: bool) -> str:
    current_attr = ' aria-current="page"' if current else ""
    return f"""<li><a href="{prefix}/journey/">About KML</a></li>
          <li><a href="{prefix}/kml/contents/books/">Kanji Studies</a></li>
          <li><a href="{prefix}/kanken/"{current_attr}>漢検への道</a></li>
          <li><a href="{prefix}/collections/">Video Collections</a></li>
          <li><a href="{prefix}/publications/">Publications</a></li>
          <li><a href="{prefix}/statistics/">Statistics</a></li>
          <li><a href="{prefix}/index.html">Home</a></li>"""


def ja_nav(prefix: str, current: bool) -> str:
    current_attr = ' aria-current="page"' if current else ""
    home = f"{prefix}/ja/index.html"
    return f"""<li><a href="{prefix}/ja/journey/">学びの道</a></li>
          <li><a href="{prefix}/kml/contents/books/">漢字の学び</a></li>
          <li><a href="{prefix}/ja/kanken/"{current_attr}>漢検への道</a></li>
          <li><a href="{prefix}/ja/collections/">映像コレクション</a></li>
          <li><a href="{prefix}/ja/publications/">出版物</a></li>
          <li><a href="{home}">ホーム</a></li>"""


def resolved_target(page: Path, href: str) -> tuple[Path, str] | None:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        return None
    if " " in href:
        fail(f"{page.relative_to(ROOT)} leaves a space unencoded in {href}")
    location = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page.resolve()
    try:
        location.relative_to(ROOT)
    except ValueError:
        fail(f"{page.relative_to(ROOT)} points outside the site: {href}")
    if location.is_dir():
        location = location / "index.html"
    if not location.is_file():
        fail(f"{page.relative_to(ROOT)} missing target for {href}")
    fragment = unquote(parsed.fragment)
    if fragment and f'id="{fragment}"' not in location.read_text(errors="replace"):
        fail(f"{page.relative_to(ROOT)} fragment #{fragment} is missing from {location.relative_to(ROOT)}")
    return location, fragment


def verify_pages(records: list[dict]) -> None:
    by_level = {}
    for record in records:
        by_level.setdefault(record["introducedAt"], []).append(record["kanji"])
    for lang, root in (("en", ROOT / "kanken"), ("ja", ROOT / "ja/kanken")):
        entrance = (root / "index.html").read_text()
        if "漢検への道" not in entrance or "2,136" not in entrance:
            fail(f"{lang} entrance missing the pathway claim")
        if f"list={BEYOND_PLAYLIST}" not in entrance:
            fail(f"{lang} entrance missing the Beyond Jōyō playlist")
        hidden = ("guidance-link--plain", "Not yet published", "Later along this path", "まだ公開", "これから加わる")
        for phrase in hidden:
            if phrase in entrance:
                fail(f"{lang} entrance still shows an unpublished resource")
        for level in UPPER:
            page = (root / PAGE[level] / "index.html").read_text()
            for phrase in hidden:
                if phrase in page:
                    fail(f"{lang} {level} still shows an unpublished resource")
            if page.count(f"list={POST_PLAYLIST}") != 1:
                fail(f"{lang} {level} should link the post-elementary playlist once")
            found = re.findall(r'data-kanji="([^"]+)"', page)
            if found != by_level[level]:
                fail(f"{lang} {LABEL[level]} lists {len(found)} characters, expected {len(by_level[level])}")
            for chunk in page.split('<li class="kanken-row"')[1:]:
                row = chunk.split("</li>", 1)[0]
                if "youtube.com" in row or "playlist?list=" in row:
                    fail(f"{lang} {level} links a character row to a playlist")
            page_path = root / PAGE[level] / "index.html"
            for href in re.findall(r'href="([^"]+)"', page):
                resolved_target(page_path, html.unescape(href))
    for level in UPPER:
        en_path = ROOT / "kanken" / PAGE[level] / "index.html"
        ja_path = ROOT / "ja/kanken" / PAGE[level] / "index.html"
        en_rows = character_targets(en_path, en_path.read_text())
        ja_rows = character_targets(ja_path, ja_path.read_text())
        if list(en_rows) != list(ja_rows) or en_rows != ja_rows:
            fail(f"{LABEL[level]} Japanese character links do not match the English links")


def character_targets(page: Path, text: str) -> dict[str, list[tuple[str, str]]]:
    rows = {}
    for chunk in text.split('<li class="kanken-row"')[1:]:
        row = chunk.split("</li>", 1)[0]
        kanji = re.search(r'data-kanji="([^"]+)"', row).group(1)
        targets = []
        for href in re.findall(r'href="([^"]+)"', row):
            location, fragment = resolved_target(page, html.unescape(href))
            targets.append((str(location.relative_to(ROOT)), fragment))
        rows[kanji] = targets
    return rows


if __name__ == "__main__":
    build()
