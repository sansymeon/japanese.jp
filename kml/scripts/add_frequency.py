import csv
from pathlib import Path

MASTER = Path("kml/data/kanji/kanji_master.csv")
FREQ = Path("kml/data/kanji/supported_frequency_order.txt")
OUTPUT = Path("kml/data/kanji/kanji_master_with_freq.csv")

# -----------------------------
# Load frequency list
# -----------------------------
freq_map = {}

with open(FREQ, encoding="utf-8") as f:
    for i, line in enumerate(f, start=1):
        kanji = line.strip()
        if kanji:
            freq_map[kanji] = i

print(f"Loaded {len(freq_map)} frequency entries")

# -----------------------------
# Process master CSV
# -----------------------------
with open(MASTER, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    # Avoid duplicate column
    fieldnames = reader.fieldnames.copy()
    if "frequency_rank" not in fieldnames:
        fieldnames.append("frequency_rank")

    rows = []
    missing = 0

    for row in reader:
        kanji = row.get("kanji", "").strip()

        if kanji in freq_map:
            row["frequency_rank"] = freq_map[kanji]
        else:
            row["frequency_rank"] = ""
            missing += 1

        rows.append(row)

print(f"Missing frequency: {missing}")

# -----------------------------
# Write output safely
# -----------------------------
with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Done:", OUTPUT)