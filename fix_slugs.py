import csv
import re
from pathlib import Path

CSV_FILE = Path("kml/data/kanji/kanji_master.csv")
OUTPUT_FILE = Path("kml/data/kanji/kanji_master_fixed.csv")

def clean_slug(text):
    if not text:
        return ""
    text = text.lower()
    text = text.replace(" ", "_")
    text = re.sub(r"[^\w_]", "", text)
    return text.strip("_")

def clean_keyword(text):
    if not text:
        return ""
    text = text.replace('"', '').replace("'", "")
    text = text.strip()
    return text

with open(CSV_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    rows = []

    for row in reader:
        kanji = row.get("kanji", "").strip()

        keyword = clean_keyword(row.get("keyword"))
        slug = clean_slug(row.get("slug"))

        # ---- FIX KEYWORD ----
        if not keyword:
            keyword = slug if slug else kanji

        # ---- FIX SLUG ----
        if not slug:
            slug = clean_slug(keyword) if keyword else kanji

        # ---- FINAL CLEAN ----
        slug = clean_slug(slug)
        keyword = clean_keyword(keyword)

        # ---- OPTIONAL: sync display_keyword ----
        if not row.get("display_keyword"):
            row["display_keyword"] = keyword

        row["slug"] = slug
        row["keyword"] = keyword

        rows.append(row)

with open(OUTPUT_FILE, "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Fixed file written to:", OUTPUT_FILE)