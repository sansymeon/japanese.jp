import csv

TEMPLATE = open("lesson_template.html", encoding="utf-8").read()
KANJI_TEMPLATE = open("kanji_block.html", encoding="utf-8").read()


# ===== HELPERS =====

def build_anchor_list(kanji_list):
    return "\n".join([
        f'<a href="#kanji-{k["slug"]}">{k["kanji"]}</a>'
        for k in kanji_list
    ])


def build_primitives(primitives):
    if not primitives:
        return ""
    return "\n".join([
        f'<span data-primitive="{p}">{p}</span>'
        for p in primitives.split("|")
    ])


def format_multiline(text):
    if not text:
        return ""
    lines = [line.strip() for line in text.split("\\n") if line.strip()]
    return "<br>".join(lines)


def build_kanji_blocks(kanji_list):
    blocks = []

    for k in kanji_list:
        block = KANJI_TEMPLATE

        block = block.replace("{{KANJI}}", k["kanji"])
        block = block.replace("{{SLUG}}", k["slug"])
        block = block.replace("{{KEYWORD}}", k["keyword"])

        block = block.replace("{{ON}}", k.get("on_reading", ""))
        block = block.replace("{{KUN}}", k.get("kun_readings", ""))

        block = block.replace(
            "{{JP_VERSE}}",
            format_multiline(k.get("jp_verse", ""))
        )

        block = block.replace(
            "{{EN_VERSE}}",
            format_multiline(k.get("en_verse", ""))
        )

        block = block.replace(
            "{{PRIMITIVES}}",
            build_primitives(k.get("kml_primitives", ""))
        )

        blocks.append(block)

    return "\n\n".join(blocks)


def build_nav_links(lesson):
    prev_link = ""
    next_link = ""

    if lesson > 1:
        prev = str(lesson - 1).zfill(2)
        prev_link = f'<a href="contents/books/book_01/lessons/lesson_{prev}.html">⬅️ Lesson {prev}</a>'

    if lesson < 25:
        nxt = str(lesson + 1).zfill(2)
        next_link = f'<a href="contents/books/book_01/lessons/lesson_{nxt}.html">➡️ Lesson {nxt}</a>'

    return prev_link, next_link


# ===== CORE =====

def generate_lesson(lesson_number, kanji_list):
    html = TEMPLATE

    html = html.replace("{{LESSON_NUMBER}}", str(lesson_number))
    html = html.replace("{{LESSON_NUMBER_PAD}}", str(lesson_number).zfill(2))

    prev_link, next_link = build_nav_links(lesson_number)

    html = html.replace("{{PREV_LINK}}", prev_link)
    html = html.replace("{{NEXT_LINK}}", next_link)
    html = html.replace("{{ANCHOR_LIST}}", build_anchor_list(kanji_list))
    html = html.replace("{{KANJI_BLOCKS}}", build_kanji_blocks(kanji_list))

    with open(f"lesson_{lesson_number:02}.html", "w", encoding="utf-8") as f:
        f.write(html)


def load_csv(csv_file):
    with open(csv_file, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ===== RUN =====

data = load_csv("kanji_lesson_01.csv")
generate_lesson(1, data)
