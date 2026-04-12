import csv
import os

input_file = "data/kanji/heisig_enriched.csv"
output_file = "data/kanji/heisig_clean_step1.csv"

def normalize_primitives(val):
    if not val:
        return ""

    # unify separators → "|"
    val = val.replace(";", "|").replace(",", "|")

    # split, trim, dedupe while preserving order
    seen = set()
    cleaned = []
    for p in val.split("|"):
        p = p.strip()
        if not p:
            continue
        if p not in seen:
            seen.add(p)
            cleaned.append(p)

    return "|".join(cleaned)

with open(input_file, encoding="utf-8") as infile, \
     open(output_file, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        row["kml_primitives"] = normalize_primitives(
            row.get("kml_primitives", "")
        )
        writer.writerow(row)

print("Step 1 complete →", output_file)