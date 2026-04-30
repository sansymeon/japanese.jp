import csv
import os

# ===== CONFIG =====
CSV_PATH = "data/kanji/kanji_master.csv"
TEMPLATE_PATH = "templates/lesson_template.html"
OUTPUT_DIR = "contents/books/book_01/lessons/"

START_INDEX = 241  # zero-based (row 242 = 苛)
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
    keyword = " ".join(keyword.split())  # normalize spaces

    return keyword

def make_anchor_list(lesson_rows):
    anchors = []
    for r in lesson_rows:
        slug = r["slug"]
        kanji = r["kanji"]
        anchors.append(f'<a href="#kanji-{slug}">{kanji}</a>')
    return "\n".join(anchors)

def make_kanji_block(r):
    kanji = r["kanji"]
    slug = r["slug"]

    raw_keyword = r.get("keyword", "")
    keyword = clean_keyword(raw_keyword)

    on = r.get("on_reading", "").strip()
    kun = r.get("kun_readings", "").strip()

    # hide empty readings cleanly
    on_display = f"On: {on}" if on else ""
    kun_display = f"Kun: {kun}" if kun else ""

    readings = " ・ ".join([x for x in [on_display, kun_display] if x])

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

  <div class="mnemonic">
    <img src="../../../../assets/art/mnemonics/{slug}.png"
         onerror="this.style.display='none'">
  </div>

  <div class="kml-verses">
    <p class="jp-verse"></p>
    <p class="en-verse"></p>
  </div>

  <div class="kanji-readings">
    {readings}
  </div>

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

  <div class="kanji-primitives">
  </div>

  <div class="emoji-hint">
    <img src="../../../../assets/emoji/{slug}.png"
         onerror="this.style.display='none'">
  </div>

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

current = START_INDEX
lesson_number = START_LESSON_NUMBER

total_rows = len(rows)

remaining = total_rows - START_INDEX
total_lessons = (remaining // LESSON_SIZE) + 1
max_lesson_number = START_LESSON_NUMBER + total_lessons - 1

while current < total_rows:

    lesson_rows = rows[current:current + LESSON_SIZE]

    if not lesson_rows:
        break

    kanji_blocks = "\n".join([make_kanji_block(r) for r in lesson_rows])
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