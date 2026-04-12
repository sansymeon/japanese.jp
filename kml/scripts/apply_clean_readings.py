import csv
from pathlib import Path

MASTER = Path("data/kanji/kanji_master.csv")
READINGS = Path("data/kanji/kanji_readings_subset.csv")
OUTPUT = Path("data/kanji/kanji_master_final.csv")

# --- load readings ---
reading_map = {}

with open(READINGS, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        kanji = row["kanji"]

        on = row["on_readings"].split("|")[0] if row["on_readings"] else ""
        kun = row["kun_readings"].split("|")[0] if row["kun_readings"] else ""

        reading_map[kanji] = (on, kun)

print(f"Loaded {len(reading_map)} readings")

# --- apply ---
with open(MASTER, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = []

    for i, row in enumerate(reader, start=2):

        # 🔥 remove any leftover corruption
        if None in row:
            print(f"Row {i}: removing overflow data")
            del row[None]

        k = row.get("kanji", "")

        if k in reading_map:
            row["on_reading"], row["kun_readings"] = reading_map[k]
        else:
            # optional: flag missing
            print(f"Row {i}: no reading found for {k}")

        rows.append(row)

# --- write clean file ---
with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames,
        extrasaction="ignore"
    )
    writer.writeheader()
    writer.writerows(rows)

print("Done → kanji_master_final.csv")