import csv

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(BASE_DIR, "../data/kanji/heisig_enriched_updated.csv")
output_file = os.path.join(BASE_DIR, "../data/kanji/heisig_enriched_updated2.csv")

with open(input_file, encoding="utf-8") as infile:
    reader = csv.reader(infile)
    rows = list(reader)

header = rows[0]

# find all cluster_components indices
indices = [i for i, col in enumerate(header) if col == "cluster_components"]

# keep only the first
remove_index = indices[1]  # second occurrence

# remove from header
new_header = [col for i, col in enumerate(header) if i != remove_index]

clean_rows = [new_header]

for row in rows[1:]:
    new_row = [val for i, val in enumerate(row) if i != remove_index]
    clean_rows.append(new_row)

with open(output_file, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerows(clean_rows)

print("Removed duplicate column.")