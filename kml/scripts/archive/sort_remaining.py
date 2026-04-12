import csv

FILE = "data/kanji/kanji_master.csv"

rows = []

with open(FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

rows_sorted = rows  # assume already sorted

# --- SETS ---
non_grade = [
    r for r in rows_sorted
    if r.get("grade") not in ["1","2","3","4","5","6"]
]

SET_SIZE = 200

sets = [
    non_grade[i:i + SET_SIZE]
    for i in range(0, len(non_grade), SET_SIZE)
]

for i, s in enumerate(sets):
    first = s[0]
    print(f"Set {i+1}: {first['slug']}.html")