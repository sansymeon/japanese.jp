import csv
import re
from pathlib import Path

FILE = Path("data/kanji/kanji_master.csv")
OUTPUT = Path("data/kanji/kanji_master_cleaned.csv")

def is_katakana(text):
    return re.fullmatch(r"[ァ-ヶー]+", text or "") is not None

with open(FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = []

    for i, row in enumerate(reader, start=2):
        if None in row:
            del row[None]

        on = row.get("on_reading", "")
        kun = row.get("kun_readings", "")

        # --- remove fake kun ---
        if kun:
            if is_katakana(kun) or kun == on:
                print(f"Row {i}: removing fake KUN → {kun}")
                row["kun_readings"] = ""

        rows.append(row)

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

print("Done → kanji_master_cleaned.csv")