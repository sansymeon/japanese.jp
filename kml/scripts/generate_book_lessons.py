import csv
import os
import math
import json
from pathlib import Path

# ===== BASE PATH =====
BASE_DIR = Path(__file__).resolve().parent.parent

# ===== CONFIG =====
CSV_PATH = BASE_DIR / "data/kanji/kanji_master_with_components.csv"
TEMPLATE_PATH = BASE_DIR / "templates/lesson_template.html"
OUTPUT_DIR = BASE_DIR / "contents/books/book_01/lessons/"
GALLERY_URLS_PATH = BASE_DIR / "data/lesson_gallery_urls.json"

START_KANJI = "昌"
LESSON_SIZE = 20
START_LESSON_NUMBER = 2

# ===== LOAD TEMPLATE =====
with open(TEMPLATE_PATH, encoding="utf-8") as f:
    template = f.read()

# ===== GALLERY URLS (optional Ambient Study doorway) =====
GALLERY_URLS: dict[str, str] = {}
if GALLERY_URLS_PATH.exists():
    with open(GALLERY_URLS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    GALLERY_URLS = {
        str(k): v.strip()
        for k, v in raw.items()
        if not str(k).startswith("_") and isinstance(v, str) and v.strip()
    }


# ===== LOAD CSV =====
rows = []
with open(CSV_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

# ===== FIND START INDEX =====
start_index = next(
    i for i, r in enumerate(rows)
    if r["kanji"] == START_KANJI
)

print(f"Start index found: {start_index} ({START_KANJI})")

current = start_index

# ===== HELPERS =====

def pad(n):
    return str(n).zfill(2)


def build_lesson_art(lesson_number: int) -> str:
    pad_n = pad(lesson_number)
    img = (
        f'<img src="../../../../assets/covers/lesson_{pad_n}.jpg"\n'
        f'       alt="Lesson {lesson_number} cover"\n'
        f'       width="380" height="250"\n'
        f'       fetchpriority="high">'
    )
    url = GALLERY_URLS.get(str(lesson_number))
    if not url:
        return img
    return (
        f'<a class="lesson-art-link"\n'
        f'     href="{url}"\n'
        f'     target="_blank"\n'
        f'     rel="noopener noreferrer"\n'
        f'     aria-label="Open Ambient Study Gallery for Lesson {lesson_number}">\n'
        f'  {img}\n'
        f'  <span class="lesson-art-gallery-label" aria-hidden="true">'
        f'▶ Ambient Study Gallery</span>\n'
        f'</a>'
    )

def clean_keyword(raw):
    if not raw:
        return ""
    keyword = raw.strip()
    keyword = keyword.replace("_", " ")
    keyword = keyword.replace("variant", "")
    keyword = keyword.replace("form", "")
    keyword = " ".join(keyword.split())
    return keyword

def make_anchor_list(lesson_rows):
    return "\n".join(
        f'<a href="#kanji-{r["slug"]}">{r["kanji"]}</a>'
        for r in lesson_rows
    )

# ===== COMPONENT LAYOUTS =====

def make_component_block(r):

    layout = r.get("layout_type", "").strip()

    # ===== UNKNOWN / EMPTY =====
    if not layout or layout == "unknown":
        return ""

    # ===== COMPONENT SOURCE =====
    components_raw = (
        r.get("cluster_components", "")
        or r.get("kml_primitives", "")
    ).strip()

    # ===== PLACEHOLDER FALLBACK =====
    if not components_raw:

        kanji = r.get("kanji", "").strip()

        if layout == "horizontal":
            components = [kanji, kanji]

        elif layout == "vertical":
            components = [kanji, kanji]

        elif layout == "box":
            components = [kanji, kanji]

        else:
            return ""

    # ===== REAL COMPONENTS =====
    else:

        components = [
            c.strip()
            for c in components_raw.split("|")
            if c.strip()
        ]

    # ===== HORIZONTAL =====
    if layout == "horizontal":

        spans = "\n".join(
            f'<span class="kanji-part">{c}</span>'
            for c in components
        )

        return f"""
<div class="component-box">
  <div class="component-layout stack-horizontal">
    {spans}
  </div>
</div>
"""

    # ===== VERTICAL =====
    elif layout == "vertical":

        spans = "\n".join(
            f'<span class="kanji-part">{c}</span>'
            for c in components
        )

        return f"""
<div class="component-box">
  <div class="component-layout stack-vertical">
    {spans}
  </div>
</div>
"""

    # ===== BOX =====
    elif layout == "box":

        if len(components) < 2:
            return ""

        outer = components[0]
        inner = components[1]

        return f"""
<div class="component-box">
  <div class="component-layout enclosure-layout">

    <div class="outer-kanji">
      {outer}
    </div>

    <div class="inner-kanji">
      {inner}
    </div>

  </div>
</div>
"""

    return ""

def make_kanji_block(r):
    kanji = r["kanji"]
    slug = r["slug"]
    print(f"Building block: {kanji}")
    components_html = make_component_block(r)


    keyword = clean_keyword(r.get("keyword", ""))

    on = r.get("on_reading", "").strip()
    kun = r.get("kun_readings", "").strip()

    # ===== READINGS (hide if empty)
    on_display = f"On: {on}" if on else ""
    kun_display = f"Kun: {kun}" if kun else ""
    readings = " ・ ".join([x for x in [on_display, kun_display] if x])

    readings_html = f"""
  <div class="kanji-readings">
    {readings}
  </div>
""" if readings else ""

# ===== VERSES =====
    jp_verse = r.get("jp_verse", "").strip()
    en_verse = r.get("en_verse", "").strip()

# Convert escaped CSV newlines
    jp_verse = jp_verse.replace("\\n", "<br>")
    en_verse = en_verse.replace("\\n", "<br>")

# Collapse excessive breaks
    jp_verse = jp_verse.replace("<br><br><br>", "<br><br>")
    en_verse = en_verse.replace("<br><br><br>", "<br><br>")

    jp_html = f'<p class="jp-verse">{jp_verse}</p>' if jp_verse else ""
    en_html = f'<p class="en-verse">{en_verse}</p>' if en_verse else ""
    verses_html = f"""
  <div class="kml-verses">
    {jp_html}
    {en_html}
  </div>
""" if jp_html or en_html else ""
    
    # ===== KANJI STUDY (auto-hide via onerror)
    study_html = f"""
  <div class="kanji-study">
    <img src="../../../../assets/studies/{slug}.jpg"
         alt="Kanji study for {kanji}"
         loading="lazy"
         onerror="this.style.display='none'">
  </div>
"""

    return f"""
<section class="kanji-entry"
         id="kanji-{slug}"
         data-kanji="{kanji}"
         data-slug="{slug}">

  <h2 class="kanji-header">
    <a target="_blank"
       class="stroke-link"
       href="../../../../tools/strokes/pages/{slug}.html">

      <span class="kanji-main-font">{kanji}</span>
      <span class="kanji-keyword">{keyword}</span>
    </a>
  </h2>

  {study_html}

  {verses_html}

  {readings_html}

    <div class="style-row">
    <div>
      <span class="kanji-font kanji-font-printed">{kanji}</span>
      <div class="style-label">Printed</div>
    </div>

    <div>
      <span class="kanji-font kanji-font-handwritten">{kanji}</span>
      <div class="style-label">Written</div>
    </div>
  </div>

  {components_html}


</section>
"""

def make_nav_links(lesson_number, max_lesson):
    prev_link = ""
    next_link = ""

    if lesson_number > START_LESSON_NUMBER:
        prev_link = f'<a href="lesson_{pad(lesson_number-1)}.html">⬅️ Lesson {lesson_number-1}</a>'

    if lesson_number < max_lesson:
        next_link = f'<a href="lesson_{pad(lesson_number+1)}.html">➡️ Lesson {lesson_number+1}</a>'

    return prev_link, next_link

# ===== GENERATION =====

lesson_number = START_LESSON_NUMBER
total_rows = len(rows)

remaining = total_rows - start_index
total_lessons = math.ceil(remaining / LESSON_SIZE)
max_lesson_number = START_LESSON_NUMBER + total_lessons - 1

while current < total_rows:

    lesson_rows = rows[current:current + LESSON_SIZE]

    if not lesson_rows:
        break

    print(
        f"Lesson {lesson_number} starts with "
        f"{lesson_rows[0]['kanji']}"
    )

    kanji_blocks = "\n".join(
        make_kanji_block(r)
        for r in lesson_rows
    )

    anchor_list = make_anchor_list(
        lesson_rows
    )

    prev_link, next_link = make_nav_links(
        lesson_number,
        max_lesson_number
    )

    html = template

    html = html.replace(
        "{{LESSON_NUMBER}}",
        str(lesson_number)
    )

    html = html.replace(
        "{{LESSON_NUMBER_PAD}}",
        pad(lesson_number)
    )

    html = html.replace(
        "{{KANJI_BLOCKS}}",
        kanji_blocks
    )

    html = html.replace(
        "{{ANCHOR_LIST}}",
        anchor_list
    )

    html = html.replace(
        "{{PREV_LINK}}",
        prev_link
    )

    html = html.replace(
        "{{NEXT_LINK}}",
        next_link
    )

    html = html.replace(
        "{{LESSON_ART}}",
        build_lesson_art(lesson_number)
    )

    output_file = os.path.join(
        OUTPUT_DIR,
        f"lesson_{pad(lesson_number)}.html"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)

    print(
        f"Generated: {output_file}"
    )

    current += LESSON_SIZE
    lesson_number += 1

print("✅ All lessons generated.")