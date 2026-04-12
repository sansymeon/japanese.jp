import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "data/kanji/kanji_master.csv"
OUTPUT = ROOT / "data/kanji/kanji_master_normalized.csv"


def clean_reading(s):
    s = (s or "").strip()

    # remove quotes
    s = s.replace('"', "").replace("（", "").replace("）", "")

    # normalize Japanese commas
    s = s.replace("、", ",")

    # remove weird spacing
    s = re.sub(r"\s*,\s*", ",", s)

    # remove duplicate commas
    s = re.sub(r",+", ",", s)

    return s.strip(",")


rows_out = []

with open(MASTER, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    for row in reader:
        if None in row:
            continue

        row["on_reading"] = clean_reading(row.get("on_reading", ""))
        row["kun_readings"] = clean_reading(row.get("kun_readings", ""))

        rows_out.append(row)


with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames,
        extrasaction="ignore"
    )
    writer.writeheader()
    writer.writerows(rows_out)

print("Done → kanji_master_normalized.csv created")