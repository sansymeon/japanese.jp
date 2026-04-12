import csv
from pathlib import Path

INPUT = Path("data/kanji/kanji_master.csv")
OUTPUT = Path("data/kanji/kanji_master_strict.csv")

with open(INPUT, encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
expected_len = len(header)

print(f"Expected columns: {expected_len}")

cleaned = [header]

for i, row in enumerate(rows[1:], start=2):

    # --- Trim extra columns ---
    if len(row) > expected_len:
        print(f"Row {i}: trimming {len(row) - expected_len} extra columns")
        row = row[:expected_len]

    # --- Pad missing columns ---
    elif len(row) < expected_len:
        print(f"Row {i}: padding {expected_len - len(row)} missing columns")
        row += [""] * (expected_len - len(row))

    cleaned.append(row)

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(cleaned)

print("Done → kanji_master_strict.csv")