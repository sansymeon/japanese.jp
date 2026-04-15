import csv

INPUT = "data/kanji/kanji_master.csv"
OUTPUT = "data/kanji/kanji_master_with_stories.csv"

NEW_COLUMNS = ["jp_verse", "en_verse"]

with open(INPUT, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames.copy()

# Add new columns if not present
for col in NEW_COLUMNS:
    if col not in fieldnames:
        fieldnames.append(col)

# Ensure every row has the new fields
for row in rows:
    for col in NEW_COLUMNS:
        if col not in row:
            row[col] = ""

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("✅ Created:", OUTPUT)