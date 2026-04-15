import re
import csv
from html import unescape

INPUT_HTML = "contents/books/book_01/lessons/lesson_01.html"
OUTPUT_CSV = "data/kanji/lesson_01_stories.csv"


def clean_japanese(html):
    # Remove ruby tags but keep main text
    html = re.sub(r"<rt>.*?</rt>", "", html)
    html = re.sub(r"</?ruby.*?>", "", html)

    # Replace <br> with newline
    html = re.sub(r"<br\s*/?>", "\n", html)

    # Remove all remaining tags
    html = re.sub(r"<.*?>", "", html)

    return unescape(html).strip()


def clean_english(html):
    html = re.sub(r"<br\s*/?>", "\n", html)
    html = re.sub(r"<.*?>", "", html)
    return unescape(html).strip()


def extract_blocks(html):
    pattern = re.compile(
        r'<section class="kanji-entry".*?data-slug="(.*?)".*?'
        r'<p class="jp-verse">(.*?)</p>.*?'
        r'<p class="en-verse">(.*?)</p>',
        re.DOTALL
    )
    return pattern.findall(html)


with open(INPUT_HTML, encoding="utf-8") as f:
    html = f.read()

blocks = extract_blocks(html)

rows = []

for slug, jp, en in blocks:
    jp_clean = clean_japanese(jp)
    en_clean = clean_english(en)

    rows.append({
        "slug": slug,
        "jp_verse": jp_clean.replace("\n", "\\n"),
        "en_verse": en_clean.replace("\n", "\\n")
    })

with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["slug", "jp_verse", "en_verse"])
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Extracted {len(rows)} stories → {OUTPUT_CSV}")