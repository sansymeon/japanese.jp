#!/usr/bin/env python3
"""Build the local Grade 1 school-grade prototype from existing KML sources.

Reads lesson HTML, compound JSON, kanji_master.csv, and KANJIDIC2.
Writes pages under school-grade/grade-1/. Does not modify Heisig lessons.
"""

from __future__ import annotations

import csv
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "school-grade" / "grade-1"
LESSON_DIR = REPO / "kml/contents/books/book_01/lessons"
COMPOUND_DIR = REPO / "kml/data/compounds"
MASTER_CSV = REPO / "kml/data/kanji/kanji_master.csv"
KANJIDIC = REPO / "kml/kanjidic2.xml"

# 学年別漢字配当表, grade 1, 五十音順. Machine-checked against joyo_index.
# Four lessons of 20, the same cuts already used by the Grade 1 熟語 films.
GRADE_1 = (
    "一右雨円王音下火花貝学気九休玉金空月犬見"
    "五口校左三山子四糸字耳七車手十出女小上森"
    "人水正生青夕石赤千川先早草足村大男竹中虫"
    "町天田土二日入年白八百文木本名目立力林六"
)
LESSON_SIZE = 20

YOUTUBE = {
    "kanji": {
        "label": "1学年で学ぶ漢字",
        "meta": "Kanji · musical review · 2 films",
        "href": "https://www.youtube.com/playlist?list=PLDqZ_saSB25k",
    },
    "compounds": {
        "label": "熟語",
        "meta": "Compounds · 4 films",
        "href": "https://www.youtube.com/playlist?list=PLUK4NyqFdNMw",
    },
    "strokes": {
        "label": "書き順",
        "meta": "Stroke order · 4 films",
        "href": "https://www.youtube.com/playlist?list=PLYpgcBuk0PGg",
    },
}

# Hero art already published for the Grade 1 musical films. 1672×941.
HERO = {
    1: ("../../kml/assets/youtube_thumbnails/grade_1_.jpg", "Grade 1 kanji, part 1"),
    2: ("../../kml/assets/youtube_thumbnails/grade_1_.jpg", "Grade 1 kanji, part 1"),
    3: ("../../kml/assets/youtube_thumbnails/grade_1_part_2.jpg", "Grade 1 kanji, part 2"),
    4: ("../../kml/assets/youtube_thumbnails/grade_1_part_2.jpg", "Grade 1 kanji, part 2"),
}

# Different words that may be the same sense. Not treated as a match or a split.
NEAR_SYNONYMS = {
    frozenset({"little", "small"}),
    frozenset({"above", "up"}),
    frozenset({"man", "male"}),
    frozenset({"before", "previous"}),
    frozenset({"stream", "river"}),
    frozenset({"grove", "woods"}),
    frozenset({"grove", "forest"}),
    frozenset({"woods", "forest"}),
    frozenset({"in", "middle"}),
    frozenset({"in", "inside"}),
    frozenset({"inside", "middle"}),
    frozenset({"character", "letter"}),
    frozenset({"center", "middle"}),
    frozenset({"centre", "middle"}),
}

HEISIG_ASSUMPTION = re.compile(
    r"lesson\s+\d+|primitive|heisig|already\s+(?:learned|studied|seen|know)|"
    r"you\s+(?:learned|studied|saw)|earlier\s+lesson|as\s+we\s+",
    re.I,
)

ASSET_PREFIX = "../../kml/"


def esc(text: str) -> str:
    return html.escape(text or "", quote=True)


def normalize(text: str) -> str:
    text = text.replace("_", " ").replace("-", " ")
    text = text.lower()
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\b(?:a|an|the)\b", " ", text)
    text = re.sub(r"\bto\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fold_plural(text: str) -> str:
    words = []
    for word in text.split():
        if len(word) > 4 and word.endswith("ies"):
            word = word[:-3] + "y"
        elif len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]
        words.append(word)
    return " ".join(words)


def same_wording(a: str, b: str) -> bool:
    left, right = normalize(a), normalize(b)
    return bool(left) and (left == right or fold_plural(left) == fold_plural(right))


def tokens(text: str) -> set[str]:
    return set(fold_plural(normalize(text)).split())


def compare_meanings(keyword: str, glosses: list[str]) -> dict:
    """Compare the Heisig keyword with the first KANJIDIC2 English gloss."""
    primary = glosses[0]
    if same_wording(keyword, primary):
        kind = "equivalent"
        reason = "same wording as the first KANJIDIC2 gloss"
    elif frozenset({normalize(keyword), normalize(primary)}) in NEAR_SYNONYMS:
        kind = "uncertain"
        reason = "different words that may be the same sense"
    elif tokens(keyword) and tokens(keyword) < tokens(primary):
        kind = "uncertain"
        reason = "the keyword is a shorter form of the first gloss"
    elif tokens(primary) and tokens(primary) < tokens(keyword):
        kind = "uncertain"
        reason = "the first gloss is a shorter form of the keyword"
    elif any(same_wording(keyword, gloss) for gloss in glosses[1:]):
        matched = next(gloss for gloss in glosses[1:] if same_wording(keyword, gloss))
        kind = "differs"
        reason = f"keyword matches a later gloss ({matched}), not the first"
    else:
        kind = "uncertain"
        reason = "keyword does not match a KANJIDIC2 gloss closely enough to decide"
    return {
        "standard": primary,
        "glosses": glosses,
        "keyword": keyword,
        "kind": kind,
        "reason": reason,
        "show_heisig": kind != "equivalent",
    }


def load_master() -> list[dict]:
    rows = []
    with MASTER_CSV.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("category") == "joyo" and row.get("grade") == "1":
                rows.append(row)
    rows.sort(key=lambda row: int(row["joyo_index"]))
    sequence = "".join(row["kanji"] for row in rows)
    if sequence != GRADE_1:
        raise SystemExit("joyo_index order does not match the Grade 1 reference sequence")
    if len(rows) != len(set(sequence)):
        raise SystemExit("Grade 1 sequence has duplicates or a length mismatch")
    return rows


def load_kanjidic(wanted: set[str]) -> tuple[dict[str, list[str]], dict]:
    tree = ET.parse(KANJIDIC)
    root = tree.getroot()
    header = root.find("header")
    meta = {
        "file": "kml/kanjidic2.xml",
        "fileVersion": header.findtext("file_version"),
        "databaseVersion": header.findtext("database_version"),
        "dateOfCreation": header.findtext("date_of_creation"),
    }
    found: dict[str, list[str]] = {}
    for char in root.findall("character"):
        literal = char.findtext("literal")
        if literal not in wanted or literal in found:
            continue
        glosses: list[str] = []
        reading = char.find("reading_meaning")
        if reading is not None:
            for group in reading.findall("rmgroup"):
                for meaning in group.findall("meaning"):
                    if meaning.get("m_lang") in (None, "", "en") and meaning.text:
                        glosses.append(meaning.text.strip())
        found[literal] = glosses
    missing = sorted(wanted - set(found))
    if missing:
        raise SystemExit(f"KANJIDIC2 is missing Grade 1 characters: {missing}")
    return found, meta


def extract_sections() -> dict[str, list[dict]]:
    found: dict[str, list[dict]] = {}
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
            end += len("</section>")
            block = text[start:end]
            match = re.search(r'data-kanji="([^"]+)"', block)
            if match:
                found.setdefault(match.group(1), []).append(
                    {"lesson": lesson_no, "path": path, "html": block}
                )
            pos = end
    return found


def load_compounds() -> dict[str, list[dict]]:
    by_kanji: dict[str, list[dict]] = {}
    for path in sorted(COMPOUND_DIR.glob("lesson_*.json")):
        if not re.fullmatch(r"lesson_\d+\.json", path.name):
            continue
        lesson_no = int(path.stem.split("_")[1])
        data = json.loads(path.read_text(encoding="utf-8"))
        for character in data.get("characters") or []:
            kanji = character.get("kanji")
            if not kanji:
                continue
            by_kanji.setdefault(kanji, []).append(
                {"lesson": lesson_no, "character": character}
            )
    return by_kanji


def choose_section(kanji: str, heisig_number: int, sections: dict[str, list[dict]]) -> dict:
    options = sections.get(kanji) or []
    if not options:
        raise SystemExit(f"No lesson HTML entry for {kanji}")
    expected = (int(heisig_number) - 1) // 20 + 1
    for option in options:
        if option["lesson"] == expected:
            return option
    return options[0]


def choose_compounds(kanji: str, lesson_no: int, compounds: dict[str, list[dict]]) -> tuple[list[dict], int | None]:
    options = compounds.get(kanji) or []
    for option in options:
        if option["lesson"] == lesson_no:
            return option["character"].get("compounds") or [], lesson_no
    if options:
        first = options[0]
        return first["character"].get("compounds") or [], first["lesson"]
    return [], None


def png_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        import struct
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        import struct
        index = 2
        while index < len(data) - 8:
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack(">HH", data[index + 5 : index + 9])
                return width, height
            if marker in (0xD8, 0xD9):
                index += 2
                continue
            segment = struct.unpack(">H", data[index + 2 : index + 4])[0]
            index += 2 + segment
    return None


def is_sixteen_nine(size: tuple[int, int] | None) -> bool:
    if not size or not size[1]:
        return False
    return abs((size[0] / size[1]) - (16 / 9)) < 0.02


def repo_path_from_lesson_src(src: str) -> Path | None:
    if src.startswith("../../../../"):
        return REPO / "kml" / src[len("../../../../") :]
    return None


def rewrite_assets(block: str) -> str:
    return block.replace("../../../../", ASSET_PREFIX)


def apply_meaning(block: str, decision: dict) -> str:
    pattern = re.compile(r'(<span class="kanji-keyword">)(.*?)(</span>)', re.S)
    shown = {"done": False}

    def replace(match: re.Match) -> str:
        if shown["done"]:
            return match.group(0)
        shown["done"] = True
        extra = ""
        if decision["show_heisig"]:
            extra = (
                '\n      <span class="kanji-heisig-keyword">'
                f'(Heisig: {esc(decision["keyword"])})</span>'
            )
        return match.group(1) + esc(decision["standard"]) + match.group(3) + extra

    updated, count = pattern.subn(replace, block, count=1)
    if count != 1:
        raise SystemExit(f"Could not place the meaning for {decision['keyword']}")
    return updated


def add_build_heading(block: str) -> str | bool:
    match = re.search(r'<div class="component-box"', block)
    if not match:
        return False
    heading = (
        '<h3 class="kanji-build-heading">'
        '<span lang="ja">漢字のしくみ</span> — How This Kanji Is Built</h3>\n'
    )
    return block[: match.start()] + heading + block[match.start() :]


def component_glyphs(block: str) -> list[str]:
    glyphs = []
    for part in re.findall(r'<span class="kanji-part">(.*?)</span>', block, re.S):
        text = re.sub(r"<[^>]+>", "", part)
        text = html.unescape(text).strip()
        if text:
            glyphs.append(text)
    return glyphs


def assumption_hits(block: str) -> list[str]:
    plain = re.sub(r"<[^>]+>", " ", block)
    plain = html.unescape(plain)
    hits = []
    for match in HEISIG_ASSUMPTION.finditer(plain):
        start = max(0, match.start() - 40)
        end = min(len(plain), match.end() + 40)
        excerpt = re.sub(r"\s+", " ", plain[start:end]).strip()
        hits.append(excerpt)
    return hits


def render_compounds(compounds: list[dict]) -> str:
    if not compounds:
        return ""
    rows = []
    for compound in compounds:
        example = compound.get("example") or {}
        segments = example.get("segments") or []
        ruby = []
        for segment in segments:
            text = segment.get("text") or ""
            reading = segment.get("reading") or ""
            if reading:
                ruby.append(f"<ruby>{esc(text)}<rt>{esc(reading)}</rt></ruby>")
            else:
                ruby.append(esc(text))
        ruby_html = "".join(ruby) if ruby else esc(example.get("ja") or "")
        rows.append(
            "    <article class=\"compound-row\">\n"
            "      <div class=\"compound-entry\">\n"
            f"        <p class=\"compound-surface\" lang=\"ja\">{esc(compound.get('surface') or '')}</p>\n"
            f"        <p class=\"compound-reading\" lang=\"ja\">{esc(compound.get('reading') or '')}</p>\n"
            f"        <p class=\"compound-meaning\">{esc(compound.get('meaning') or '')}</p>\n"
            "      </div>\n"
            "      <div class=\"compound-example\">\n"
            "        <p class=\"compound-ja\" lang=\"ja\">"
            f"<span class=\"ja-ruby\">{ruby_html}</span>"
            f"<span class=\"ja-plain\">{esc(example.get('ja') or '')}</span></p>\n"
            f"        <p class=\"compound-en\" lang=\"en\">{esc(example.get('en') or '')}</p>\n"
            "      </div>\n"
            "    </article>"
        )
    inner = "\n".join(rows)
    return (
        '<div class="school-compounds">\n'
        '  <h3 class="school-compounds-heading"><span lang="ja">熟語</span></h3>\n'
        '  <div class="compounds-sheet">\n'
        f"{inner}\n"
        "  </div>\n"
        "</div>\n"
    )


def prepare_entry(row: dict, sections: dict, compounds: dict, glosses: dict[str, list[str]]) -> dict:
    kanji = row["kanji"]
    section = choose_section(kanji, row["heisig_number"], sections)
    block = section["html"]
    keyword_match = re.search(r'<span class="kanji-keyword">(.*?)</span>', block, re.S)
    keyword = re.sub(r"\s+", " ", html.unescape(keyword_match.group(1))).strip() if keyword_match else row["keyword"]
    decision = compare_meanings(keyword, glosses[kanji])
    decision["csv_keyword"] = row["keyword"]
    decision["keyword_source"] = "lesson HTML" if keyword_match else "kanji_master.csv"
    if keyword != row["keyword"]:
        decision["csv_mismatch"] = True
    block = apply_meaning(block, decision)
    headed = add_build_heading(block)
    if headed:
        block = headed
    compound_list, compound_lesson = choose_compounds(kanji, section["lesson"], compounds)
    compound_html = render_compounds(compound_list)
    if compound_html:
        block = block.replace("</section>", compound_html + "</section>", 1)
    block = rewrite_assets(block)
    source = f"kml/contents/books/book_01/lessons/lesson_{section['lesson']:02d}.html"
    block = f"<!-- source: {source} #{kanji} -->\n" + block

    images = []
    for src in re.findall(r'<img[^>]+src="([^"]+)"', block):
        original = src.replace(ASSET_PREFIX, "../../../../")
        path = repo_path_from_lesson_src(original)
        size = png_size(path) if path and path.is_file() else None
        images.append(
            {
                "src": src,
                "exists": bool(path and path.is_file()),
                "size": size,
                "sixteen_nine": is_sixteen_nine(size),
            }
        )
    strokes = []
    for href in re.findall(r'href="([^"]*strokes/pages/[^"]+)"', block):
        original = href.replace(ASSET_PREFIX, "../../../../")
        path = repo_path_from_lesson_src(original)
        strokes.append({"href": href, "exists": bool(path and path.is_file())})

    return {
        "kanji": kanji,
        "slug": row["slug"],
        "heisig_number": int(row["heisig_number"]),
        "joyo_index": int(row["joyo_index"]),
        "source_lesson": section["lesson"],
        "source_copies": len(sections.get(kanji) or []),
        "other_sources": [
            {
                "lesson": option["lesson"],
                "keyword": re.sub(
                    r"\s+",
                    " ",
                    html.unescape(
                        re.search(r'<span class="kanji-keyword">(.*?)</span>', option["html"], re.S).group(1)
                    ),
                ).strip(),
            }
            for option in sections.get(kanji) or []
            if option["lesson"] != section["lesson"]
        ],
        "html": block,
        "meaning": decision,
        "compound_count": len(compound_list),
        "compound_lesson": compound_lesson,
        "has_component_box": '<div class="component-box"' in block,
        "component_glyphs": component_glyphs(block),
        "assumption_hits": assumption_hits(section["html"]),
        "has_verse": "kml-verses" in block,
        "images": images,
        "strokes": strokes,
        "on": row.get("on_reading") or "",
        "kun": row.get("kun_readings") or "",
    }


def page_shell(title: str, body: str, description: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="{esc(description)}">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&family=Yomogi&family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../kml/assets/site/css/kml_style.css">
<link rel="stylesheet" href="../../kml/assets/site/css/compounds-lesson.css">
<link rel="stylesheet" href="../css/school-grade.css">
<script>
try {{
  if (localStorage.getItem("kml-compounds-furigana") === "off") {{
    document.documentElement.classList.add("furigana-off");
  }}
}} catch (err) {{}}
</script>
</head>
<body id="top">
{body}
<script src="../../kml/assets/site/js/kml.js"></script>
<script>
(function () {{
  var toggle = document.getElementById("furigana-toggle");
  if (!toggle) return;
  function on() {{ return !document.documentElement.classList.contains("furigana-off"); }}
  function set(next) {{
    document.documentElement.classList.toggle("furigana-off", !next);
    toggle.setAttribute("aria-pressed", next ? "true" : "false");
    toggle.setAttribute("aria-label", next ? "Furigana on" : "Furigana off");
    try {{ localStorage.setItem("kml-compounds-furigana", next ? "on" : "off"); }} catch (err) {{}}
  }}
  toggle.addEventListener("click", function () {{ set(!on()); }});
  set(on());
}})();
</script>
</body>
</html>
"""


def review_html() -> str:
    links = []
    for item in YOUTUBE.values():
        links.append(
            f'  <a class="btn-compounds" href="{esc(item["href"])}" target="_blank" rel="noopener noreferrer">'
            f'{esc(item["label"])}<br><span style="font-size:0.82rem;font-weight:400">{esc(item["meta"])}</span></a>'
        )
    return (
        '<section class="school-review" id="review" aria-labelledby="review-heading">\n'
        '  <h2 id="review-heading"><span lang="ja">復習</span> — Grade 1 on YouTube</h2>\n'
        "  <p>Musical review for this grade. These are the existing elementary collections.</p>\n"
        '  <div class="cta">\n'
        + "\n".join(links)
        + "\n  </div>\n</section>"
    )


def write_entrance(lessons: list[list[dict]]) -> None:
    doors = []
    for index, entries in enumerate(lessons, start=1):
        image, alt = HERO[index]
        chars = " ".join(entry["kanji"] for entry in entries)
        doors.append(
            f'<a class="school-door" href="lesson-{index:02d}.html">\n'
            f'  <img src="{image}" alt="{esc(alt)}" width="1672" height="941">\n'
            f'  <span class="school-door-kicker">第{index}課 · 20字</span>\n'
            f'  <span class="school-door-title">{esc(entries[0]["kanji"])} → {esc(entries[-1]["kanji"])}</span>\n'
            f'  <span class="school-door-kanji" lang="ja">{esc(chars)}</span>\n'
            "</a>"
        )
    body = f"""
<div class="navbar">
  <a href="../../kml/">Kanji・Music・Landscape</a>
  <a href="#review">YouTube</a>
</div>
<div class="lesson-art">
  <img src="../../kml/assets/youtube_thumbnails/grade_1_.jpg" alt="Grade 1" width="1672" height="941">
</div>
<p class="school-kicker" lang="ja">小学1年生 — 80字</p>
<h1>Grade 1</h1>
<p class="school-range" lang="ja">五十音順</p>
<nav class="school-doors" aria-label="Grade 1 lessons">
{chr(10).join(doors)}
</nav>
{review_html()}
<p class="school-footer-note">School-grade order of the existing KML lessons. Local preview.</p>
"""
    text = page_shell(
        "小学1年生 — 80字 — Kanji・Music・Landscape",
        body,
        "小学1年生の漢字 80字 in 五十音順. Four lessons reusing existing KML entries.",
    )
    (OUT / "index.html").write_text(text, encoding="utf-8")


def write_lesson(number: int, entries: list[dict], lesson_count: int) -> None:
    image, alt = HERO[number]
    prev_link = (
        f'<a href="lesson-{number - 1:02d}.html">← 第{number - 1}課</a>'
        if number > 1
        else '<a href="./">← 小学1年生</a>'
    )
    next_link = (
        f'<a href="lesson-{number + 1:02d}.html">第{number + 1}課 →</a>'
        if number < lesson_count
        else '<a href="./">小学1年生 →</a>'
    )
    anchors = "\n".join(
        f'<a href="#kanji-{esc(entry["slug"])}">{esc(entry["kanji"])}</a>' for entry in entries
    )
    span = f'{entries[0]["kanji"]} → {entries[-1]["kanji"]}'
    body = f"""
<div class="navbar">
  {prev_link}
  <a href="./">小学1年生</a>
  {next_link}
</div>
<div class="lesson-art">
  <a class="lesson-art-link" href="{esc(YOUTUBE["kanji"]["href"])}" target="_blank" rel="noopener noreferrer" aria-label="Open the Grade 1 kanji playlist on YouTube">
    <img src="{image}" alt="{esc(alt)}" width="1672" height="941">
    <span class="lesson-art-gallery-label" aria-hidden="true">▶ 1学年で学ぶ漢字</span>
  </a>
</div>
<p class="school-kicker" lang="ja">小学1年生 — 80字</p>
<h1>第{number}課</h1>
<p class="school-range" lang="ja">{esc(span)}</p>
<nav class="anchor-list">
{anchors}
</nav>
<div class="furigana-bar">
  <button type="button" class="furigana-toggle" id="furigana-toggle" aria-pressed="true" aria-label="Furigana on">
    Furigana
    <span class="furigana-mark" aria-hidden="true"></span>
  </button>
</div>
<p class="stroke-hint">Click the featured kanji to view stroke order.</p>
{chr(10).join(entry["html"] for entry in entries)}
{review_html()}
<div class="navbar">
  {prev_link}
  <a href="./">小学1年生</a>
  {next_link}
</div>
<div class="stamps">
  <img src="../../kml/assets/site/stamps/symeon_stamp.png" alt="Symeon Stamp" width="48" loading="lazy" decoding="async">
  <img src="../../kml/assets/site/stamps/chatgpt_stamp.png" alt="ChatGPT Stamp" width="48" loading="lazy" decoding="async">
</div>
"""
    text = page_shell(
        f"小学1年生 第{number}課 — Kanji・Music・Landscape",
        body,
        f"小学1年生 第{number}課. {span}. Existing KML entries in school order.",
    )
    (OUT / f"lesson-{number:02d}.html").write_text(text, encoding="utf-8")


def write_report(entries: list[dict], kanjidic_meta: dict) -> None:
    equivalent = [e for e in entries if e["meaning"]["kind"] == "equivalent"]
    differs = [e for e in entries if e["meaning"]["kind"] == "differs"]
    uncertain = [e for e in entries if e["meaning"]["kind"] == "uncertain"]
    missing_images = []
    off_ratio = []
    missing_strokes = []
    missing_compounds = []
    missing_components = []
    missing_verses = []
    assumptions = []
    outside = []
    grade_set = {e["kanji"] for e in entries}
    duplicates = [e for e in entries if e["source_copies"] > 1]
    csv_mismatch = [e for e in entries if e["meaning"].get("csv_mismatch")]

    for entry in entries:
        for image in entry["images"]:
            if not image["exists"]:
                missing_images.append(f'{entry["kanji"]} {image["src"]}')
            elif not image["sixteen_nine"]:
                size = image["size"]
                off_ratio.append(f'{entry["kanji"]} {image["src"]} {size[0]}×{size[1]}')
        for stroke in entry["strokes"]:
            if not stroke["exists"]:
                missing_strokes.append(f'{entry["kanji"]} {stroke["href"]}')
        if entry["compound_count"] == 0:
            missing_compounds.append(entry["kanji"])
        if not entry["has_component_box"]:
            missing_components.append(entry["kanji"])
        if not entry["has_verse"]:
            missing_verses.append(entry["kanji"])
        if entry["assumption_hits"]:
            assumptions.append(entry)
        extra = []
        for glyph in entry["component_glyphs"]:
            if glyph != entry["kanji"] and glyph not in grade_set:
                extra.append(glyph)
        if extra:
            outside.append((entry, extra))

    def meaning_line(entry: dict) -> str:
        meaning = entry["meaning"]
        glosses = "; ".join(meaning["glosses"])
        return (
            f'- {entry["kanji"]} — standard “{meaning["standard"]}”; '
            f'Heisig “{meaning["keyword"]}”; other glosses: {glosses}. {meaning["reason"]}.'
        )

    lessons = [entries[i : i + LESSON_SIZE] for i in range(0, len(entries), LESSON_SIZE)]
    lesson_lines = []
    for index, group in enumerate(lessons, start=1):
        lesson_lines.append(
            f'- Lesson {index}: {group[0]["kanji"]} → {group[-1]["kanji"]} '
            f'({len(group)} characters)'
        )

    outside_lines = []
    for entry, glyphs in outside:
        shown = " ".join(glyphs)
        outside_lines.append(
            f'- {entry["kanji"]} (Heisig lesson {entry["source_lesson"]}): {shown}'
        )

    assumption_lines = ["None found in the reused entry text."]
    if assumptions:
        assumption_lines = []
        for entry in assumptions:
            for hit in entry["assumption_hits"]:
                assumption_lines.append(f'- {entry["kanji"]}: “{hit}”')

    problem_lines = []
    if missing_images:
        problem_lines.append("Missing study images:\n" + "\n".join(f"- {item}" for item in missing_images))
    if missing_strokes:
        problem_lines.append("Missing stroke-order pages:\n" + "\n".join(f"- {item}" for item in missing_strokes))
    if missing_compounds:
        problem_lines.append("No compounds in the lesson JSON: " + " ".join(missing_compounds))
    if missing_components:
        problem_lines.append("No component diagram: " + " ".join(missing_components))
    if missing_verses:
        problem_lines.append("No Japanese/English verse: " + " ".join(missing_verses))
    if csv_mismatch:
        problem_lines.append(
            "The lesson page already spells the keyword differently from `kanji_master.csv`. "
            "The comparison uses the lesson page. "
            + ", ".join(
                f'{e["kanji"]}: page “{e["meaning"]["keyword"]}”, table “{e["meaning"]["csv_keyword"]}”'
                for e in csv_mismatch
            )
        )
    if duplicates:
        notes = []
        for entry in duplicates:
            others = ", ".join(
                f'lesson {item["lesson"]} “{item["keyword"]}”' for item in entry["other_sources"]
            )
            notes.append(
                f'{entry["kanji"]}: kept lesson {entry["source_lesson"]} “{entry["meaning"]["keyword"]}”; also {others}'
            )
        problem_lines.append(
            "The same character also has another Heisig entry. The grade list keeps the entry whose lesson matches its Heisig number.\n"
            + "\n".join(f"- {note}" for note in notes)
        )
    if off_ratio:
        problem_lines.append(
            "Study images already on the Heisig pages that are not 16:9. Left as they are:\n"
            + "\n".join(f"- {item}" for item in off_ratio)
        )
    if not problem_lines:
        problem_lines.append("No missing verses, compounds, component diagrams, images, or stroke pages.")

    text = f"""# Grade 1 school-grade prototype

Local preview: `school-grade/grade-1/index.html`

The Heisig lessons, the live 漢検 pages, and the YouTube collections were not modified.

## Ordering reference

The sequence is the grade 1 list of the 学年別漢字配当表 (elementary school kanji allocation, 五十音順), as stored in `kml/data/kanji/kanji_master.csv`.

Characters with `category=joyo` and `grade=1` were taken in `joyo_index` order. That column is the character’s place in the 常用漢字表, which is itself in 五十音順. They were not sorted again by reading, stroke count, or Heisig number.

The resulting 80 characters match the conventional grade 1 sequence, including the opening 一 → 右 → 雨 → 円 → 王 → 音 → 下 → 火 → 花 → 貝. The same four groups are already used by the Grade 1 熟語 films.

{chr(10).join(lesson_lines)}

All 80 characters appear once.

Recorded in `school-grade/grade-1/order.json` so later grades can follow the same rule: filter the master table to the grade, keep `joyo_index` order, and do not re-sort.

## English meanings

Source: KANJIDIC2 `{kanjidic_meta["file"]}`, database {kanjidic_meta["databaseVersion"]}, created {kanjidic_meta["dateOfCreation"]}.

The standard meaning is the first English `<meaning>` (no `m_lang`) in document order. The Heisig keyword is the text already shown in the lesson HTML. The Heisig pages were not edited.

Comparison, in order:

1. Same wording after case, punctuation, underscores, articles, and a simple plural fold. Show only the KANJIDIC2 wording.
2. Otherwise, if the pair is a near-synonym or one phrase is only a shorter form of the other, show both and flag it here. Those were not treated as a match or as a split.
3. Otherwise, if the keyword matches a later KANJIDIC2 gloss exactly, show the first gloss and then `(Heisig: …)`.
4. Otherwise show both and flag the comparison. The keyword was not forced into either decision.

### Same meaning ({len(equivalent)})

Only the standard meaning is shown.

{chr(10).join(meaning_line(e) for e in equivalent)}

### Meaningfully different ({len(differs)})

The standard meaning is shown first. The original keyword follows in smaller type.

{chr(10).join(meaning_line(e) for e in differs)}

### Uncertain — review ({len(uncertain)})

Both are shown, in the same way as a difference, so neither source is hidden. These still need a human decision before the Heisig line is removed or kept as a real difference.

{chr(10).join(meaning_line(e) for e in uncertain)}

Later KANJIDIC2 glosses are not added to the page when the keyword already matches the first gloss. For school reading, the ones most worth a second look are 校 (first gloss “exam”, later “school”), 円 (later “yen”), 青 (later “green”), and 足 (later “foot”).

## Source material

Each page reuses the Heisig `<section class="kanji-entry">` for that character: landscape study, verse, readings, printed and written forms, component diagram, and stroke-order link. Compounds and their example sentences come from that character’s lesson file in `kml/data/compounds/`. Asset files are linked, not copied.

{chr(10).join(problem_lines)}

YouTube links are the three Grade 1 playlists already published on `elementary/grade-1/index.html`:

- 1学年で学ぶ漢字 — {YOUTUBE["kanji"]["href"]}
- 熟語 — {YOUTUBE["compounds"]["href"]}
- 書き順 — {YOUTUBE["strokes"]["href"]}

Individual film URLs are not stored in the repository, so the prototype uses those playlists. The musical kanji set is two films of 40 characters; 熟語 and 書き順 are four films of 20, matching these lessons. The playlist ids are the ones already on the 漢検 grade page. They are shorter than a typical current YouTube playlist id, and that page was not changed.

## Component explanations

The diagrams are kept. The school-grade pages add the heading 漢字のしくみ — How This Kanji Is Built, so the diagram is a construction note rather than a step in the Heisig sequence.

Prose that assumes a component was already studied in Heisig order:

{chr(10).join(assumption_lines)}

Diagrams that include a glyph outside this grade (or a non-character part). No new explanation was written for these. They are the items most likely to need a plain label if the pathway is taught without Heisig:

{chr(10).join(outside_lines) if outside_lines else "- None."}

## What can be automated for Grades 2–6

The generator can be reused as it stands for the extraction, meaning comparison, compound attachment, component heading, and lesson navigation.

What is already general:

- Lesson HTML is the entry source. One character is lifted from whichever Heisig lesson contains it.
- Compounds are taken from the matching `kml/data/compounds/lesson_NN.json` character.
- KANJIDIC2 supplies the standard English meaning with the same comparison rules.
- `joyo_index` within a grade reproduces 五十音順 without a hand-built sort.

What Grade 1 does not settle:

- Grades 2–6 are 160, 200, 202, 193, and 191 characters. Equal lessons of 20 do not come out even. The existing films already split those grades on their own boundaries, including gojūon sections in the later grades. Those boundaries should be recorded the way Grade 1’s four groups of 20 are recorded here.
- The near-synonym list in the meaning comparison is a review aid for uncertain pairs, not a complete dictionary. Later grades will add pairs this list does not know. Those should stay in the uncertain report.
- Component diagrams that point outside the current grade will be more common from Grade 2 on. The heading is in place; plain-language labels for those parts are still an editorial pass, not something the generator should invent.
"""
    (REPO / "school-grade" / "GRADE_1_PROTOTYPE.md").write_text(text, encoding="utf-8")


def write_order(entries: list[dict], kanjidic_meta: dict) -> None:
    payload = {
        "grade": 1,
        "count": len(entries),
        "order": "五十音順",
        "reference": "学年別漢字配当表 (elementary allocation), via kanji_master.csv joyo_index",
        "source": "kml/data/kanji/kanji_master.csv",
        "kanjidic2": kanjidic_meta,
        "lessons": [
            {
                "lesson": index,
                "characters": [entry["kanji"] for entry in entries[start : start + LESSON_SIZE]],
            }
            for index, start in enumerate(range(0, len(entries), LESSON_SIZE), start=1)
        ],
        "characters": [
            {
                "kanji": entry["kanji"],
                "slug": entry["slug"],
                "joyoIndex": entry["joyo_index"],
                "heisigNumber": entry["heisig_number"],
                "sourceLesson": entry["source_lesson"],
                "standardMeaning": entry["meaning"]["standard"],
                "heisigKeyword": entry["meaning"]["keyword"],
                "meaningKind": entry["meaning"]["kind"],
                "meaningReason": entry["meaning"]["reason"],
            }
            for entry in entries
        ],
    }
    (OUT / "order.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = load_master()
    glosses, kanjidic_meta = load_kanjidic({row["kanji"] for row in rows})
    sections = extract_sections()
    compounds = load_compounds()
    entries = [prepare_entry(row, sections, compounds, glosses) for row in rows]
    if "".join(entry["kanji"] for entry in entries) != GRADE_1:
        raise SystemExit("Built sequence drifted from the reference")
    OUT.mkdir(parents=True, exist_ok=True)
    lessons = [entries[i : i + LESSON_SIZE] for i in range(0, len(entries), LESSON_SIZE)]
    write_entrance(lessons)
    for number, lesson in enumerate(lessons, start=1):
        write_lesson(number, lesson, len(lessons))
    write_order(entries, kanjidic_meta)
    write_report(entries, kanjidic_meta)
    kinds = {}
    for entry in entries:
        kinds[entry["meaning"]["kind"]] = kinds.get(entry["meaning"]["kind"], 0) + 1
    print(f"Wrote {len(entries)} characters in {len(lessons)} lessons → {OUT}")
    print("meanings", kinds)


if __name__ == "__main__":
    main()
