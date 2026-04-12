import csv

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(BASE_DIR, "../data/kanji/heisig_enriched.csv")
output_file = os.path.join(BASE_DIR, "../data/kanji/heisig_enriched_updated.csv")


with open(input_file, encoding="utf-8") as infile, \
     open(output_file, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)

    # add new field
    fieldnames = reader.fieldnames + ["cluster_components"]

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        # default: use keyword as initial cluster
        row["cluster_components"] = row.get("heisig_keyword", "").strip()
        writer.writerow(row)

print("Done. New file created:", output_file)