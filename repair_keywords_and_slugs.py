import csv
import re
from pathlib import Path
from collections import defaultdict

file = Path("kml/data/kanji/kanji_master_clean.csv")

def clean_text(text):
    return (text or "").strip()

def normalize_slug(text):
    text = text.lower()
    text = re.sub(r"\(.*?\)", "", text)     # remove parentheses
    text = re.sub(r"[^\w\s-]", "", text)    # remove punctuation
    text = re.sub(r"\s+", "_", text.strip())
    return text

rows = []
slug_count = defaultdict(int)

with file.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    for row in reader:
        slug_field = clean_text(row.get("slug"))
        keyword_id = clean_text(row.get("keyword_id"))

        # Step 1: recover true keyword
        if slug_field:
            keyword = slug_field
        elif keyword_id:
            keyword = keyword_id
        else:
            keyword = f"kanji_{row.get('joyo_index')}"

        # Step 2: assign corrected fields
        row["keyword"] = keyword

        # Step 3: regenerate slug from keyword (FIRST WORD ONLY)
        base = normalize_slug(keyword).split("_")[0]

        if not base:
            base = f"kanji_{row.get('joyo_index')}"

        slug_count[base] += 1
        count = slug_count[base]

        if count == 1:
            new_slug = base
        else:
            new_slug = f"{base}_{count}"

        row["slug"] = new_slug

        rows.append(row)

# Step 4: write clean file
with file.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)