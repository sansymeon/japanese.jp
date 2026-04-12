import csv
from pathlib import Path

INPUT = Path("data/kanji/kanji_master.csv")
OUTPUT = Path("data/kanji/kanji_master_checked.csv")

with open(INPUT, encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
expected_len = len(header)

print(f"Expected columns: {expected_len}")

# --- Duplicate tracking ---
slug_map = {}
keyword_id_map = {}
keyword_map = {}

fixed_rows = [header]

for i, row in enumerate(rows[1:], start=2):

    # --- Fix 27-column rows ---
    if len(row) == expected_len + 1:
        if row[-1] == "":
            print(f"Row {i}: removing trailing empty column")
            row = row[:-1]

    # --- Detect bad length ---
    if len(row) != expected_len:
        print(f"Row {i}: BAD COLUMN COUNT = {len(row)}")

    # --- Extract fields safely ---
    row_dict = dict(zip(header, row))

    slug = row_dict.get("slug", "")
    keyword_id = row_dict.get("keyword_id", "")
    keyword = row_dict.get("keyword", "")
    kanji = row_dict.get("kanji", "")

    # --- Check duplicates ---
    def check_duplicate(map_obj, value, label):
        if not value:
            return
        if value in map_obj:
            print(f"Duplicate {label}: '{value}' → rows {map_obj[value]} & {i} (kanji {kanji})")
        else:
            map_obj[value] = i

    check_duplicate(slug_map, slug, "slug")
    check_duplicate(keyword_id_map, keyword_id, "keyword_id")
    check_duplicate(keyword_map, keyword, "keyword")

    fixed_rows.append(row)

# --- Write cleaned file ---
with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(fixed_rows)

print("\nDone → kanji_master_checked.csv")