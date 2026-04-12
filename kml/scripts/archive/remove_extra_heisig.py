import csv
from pathlib import Path

INPUT = Path("data/kanji/kanji_master.csv")
OUTPUT = Path("data/kanji/kanji_master_fixed.csv")

with open(INPUT, encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
expected_len = len(header)

fixed_rows = [header]

for i, row in enumerate(rows[1:], start=2):

    new_row = []
    skip_next = False

    for j in range(len(row)):
        if skip_next:
            skip_next = False
            continue

        # remove duplicate heisig_extra
        if (
            j < len(row) - 1 and
            row[j] == "heisig_extra" and
            row[j+1] == "heisig_extra"
        ):
            new_row.append("heisig_extra")
            skip_next = True
        else:
            new_row.append(row[j])

    # --- fix length ---
    if len(new_row) < expected_len:
        new_row += [""] * (expected_len - len(new_row))

    elif len(new_row) > expected_len:
        new_row = new_row[:expected_len]

    fixed_rows.append(new_row)

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(fixed_rows)

print("Done → kanji_master_fixed.csv")