import csv
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data/kanji/heisig_enriched.csv"

# --- NORMALIZATION MAP (core control layer) ---
NORMALIZE = {
    "day": "sun",
    "month": "moon",
    "flesh": "body",
    "part of the body": "body",
    "human legs": "legs",
    "animal legs": "legs",
    "pent in": "enclosure",
    "top hat": "lid",
    "diced": "cut",
    "baseball": "ball",
    "brains": "field",
    "ceiling": "line",
    "floor": "line"
}

primitive_counter = Counter()

with open(INPUT, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        primitives = row.get("kml_primitives", "")
        
        if primitives:
            parts = [p.strip() for p in primitives.split(";") if p.strip()]
            
            for p in parts:
                p = NORMALIZE.get(p, p)  # normalize here
                primitive_counter[p] += 1

# --- OUTPUT RESULTS ---

print("\n=== ALL PRIMITIVES (sorted by frequency) ===\n")

for primitive, count in primitive_counter.most_common():
    print(f"{primitive:20} {count}")

print("\n=== TOTAL UNIQUE PRIMITIVES ===")
print(len(primitive_counter))


# --- DEBUG: find garbage / bad primitives ---

print("\n=== SUSPICIOUS PRIMITIVES (long or multi-word) ===\n")

for p in primitive_counter:
    if " " in p or len(p) > 12:
        print(p)


print("\n=== RARE PRIMITIVES (count = 1) ===\n")

for primitive, count in primitive_counter.items():
    if count == 1:
        print(primitive)