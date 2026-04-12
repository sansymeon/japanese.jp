import csv
from pathlib import Path

MASTER = Path("data/kanji/kanji_master.csv")
READINGS = Path("data/kanji/kanji_readings_all.csv")
OUTPUT = Path("data/kanji/kanji_readings_subset.csv")

# --- collect kanji from master ---
master_kanji = set()

with open(MASTER, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        k = row.get("kanji")
        if k:
            master_kanji.add(k)

print(f"Master kanji count: {len(master_kanji)}")

# --- filter readings ---
filtered = []

with open(READINGS, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["kanji"] in master_kanji:
            filtered.append(row)

print(f"Filtered readings: {len(filtered)}")

# --- write output ---
with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["kanji", "on_readings", "kun_readings"]
    )
    writer.writeheader()
    writer.writerows(filtered)

print("Done → kanji_readings_subset.csv")