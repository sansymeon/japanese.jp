import re
import csv

# Load your raw primitive text file
with open("data/kanji/primitives_raw.txt", encoding="utf-8") as f:
    raw = f.read()

entries = re.split(r"===\s*(.*?)\s*===", raw)
# entries = ["", "刃", "...html...", "切", "..."]

kanji_map = {}

for i in range(1, len(entries), 2):
    kanji = entries[i].strip()
    html = entries[i+1]

    primitives = re.findall(r'data-primitive="(.*?)"', html)
    kanji_map[kanji] = "|".join(primitives)

# Load master CSV
with open("data/kanji/kanji_master.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Add primitives
for row in rows:
    k = row["kanji"]
    if k in kanji_map:
        row["kml_primitives"] = kanji_map[k]

# Save updated CSV
with open("data/kanji/kanji_master_updated.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)