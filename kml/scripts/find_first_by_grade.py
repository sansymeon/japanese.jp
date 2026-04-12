import csv

FILE = "data/kanji/kanji_master.csv"

rows = []

with open(FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# If already sorted in CSV, skip sorting
rows_sorted = rows

seen = set()

for row in rows_sorted:
    grade = row.get("grade")

    if grade in ["1","2","3","4","5","6"] and grade not in seen:
        print(f"Grade {grade}: {row['slug']}.html")
        seen.add(grade)