import csv
import os
import math

# ===== CONFIG =====
CSV_PATH = "data/kanji/kanji_master.csv"
TEMPLATE_PATH = "templates/lesson_template.html"
OUTPUT_DIR = "contents/books/book_01/lessons/"

START_KANJI = "苛"
LESSON_SIZE = 20
START_LESSON_NUMBER = 13

# ===== LOAD TEMPLATE =====
with open(TEMPLATE_PATH, encoding="utf-8") as f:
    template = f.read()

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

def make_kanji_block(r):
    kanji = r["kanji"]
    slug = r["slug"]

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

    # ===== MNEMONIC (auto-hide via onerror)
    mnemonic_html = f"""
  <div class="mnemonic">
    <img src="../../../../assets/art/mnemonics/{slug}.png"
         onerror="this.style.display='none'">
  </div>
"""

    # ===== EMOJI (auto-hide via onerror)
    emoji_html = f"""
  <div class="emoji-hint">
    <img src="../../../../assets/emoji/{slug}.png"
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

  {mnemonic_html}

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

  {emoji_html}

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

    print(f"Lesson {lesson_number} starts with {lesson_rows[0]['kanji']}")

    kanji_blocks = "\n".join(make_kanji_block(r) for r in lesson_rows)
    anchor_list = make_anchor_list(lesson_rows)
    prev_link, next_link = make_nav_links(lesson_number, max_lesson_number)

    html = template
    html = html.replace("{{LESSON_NUMBER}}", str(lesson_number))
    html = html.replace("{{LESSON_NUMBER_PAD}}", pad(lesson_number))
    html = html.replace("{{KANJI_BLOCKS}}", kanji_blocks)
    html = html.replace("{{ANCHOR_LIST}}", anchor_list)
    html = html.replace("{{PREV_LINK}}", prev_link)
    html = html.replace("{{NEXT_LINK}}", next_link)

    output_file = os.path.join(
        OUTPUT_DIR,
        f"lesson_{pad(lesson_number)}.html"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated: {output_file}")

    current += LESSON_SIZE
    lesson_number += 1

print("✅ All lessons generated.")