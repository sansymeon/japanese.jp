import csv
from pathlib import Path

MASTER = Path("data/kanji/kanji_master_with_freq.csv")
OUTPUT = Path("data/kanji/missing_frequency.txt")

missing = []

with open(MASTER, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        kanji = row.get("kanji", "").strip()
        freq = row.get("frequency_rank", "").strip()

        if not freq:
            missing.append(kanji)

# remove duplicates just in case
missing = sorted(set(missing))

with open(OUTPUT, "w", encoding="utf-8") as f:
    for k in missing:
        f.write(k + "\n")

print(f"Missing kanji: {len(missing)}")
print("Saved to:", OUTPUT)