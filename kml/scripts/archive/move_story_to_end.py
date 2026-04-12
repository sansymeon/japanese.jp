import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "data/kanji/kanji_master.csv"
OUTPUT = ROOT / "data/kanji/kanji_master_restructured.csv"

NEW_HEADER = [
    "kanji","joyo_index","heisig_number","strokes","grade",
    "slug","keyword_id","keyword",
    "on_reading","kun_readings","category",
    "k_code","joyo_rank","radical","radical_index",
    "stroke_group","unicode","svg_file",
    "reserved1","reserved2","status",
    "lesson_start","lesson_end","book_number",
    "image","display_keyword",
    "story"
]

rows_out = []

with open(MASTER, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        if None in row:
            continue

        new_row = {}

        for col in NEW_HEADER:
            if col == "story":
                new_row[col] = ""  # initialize empty
            else:
                new_row[col] = row.get(col, "")

        rows_out.append(new_row)

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=NEW_HEADER)
    writer.writeheader()
    writer.writerows(rows_out)

print("Done → kanji_master_restructured.csv created")