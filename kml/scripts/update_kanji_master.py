import csv

INPUT = "data/kanji/kanji_master.csv"
OUTPUT = "data/kanji/kanji_master_updated.csv"

NEW_COLUMNS = ["kml_primitives", "cluster_components", "collapse_to"]

with open(INPUT, encoding="utf-8") as infile, \
     open(OUTPUT, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)

    # extend fieldnames
    fieldnames = reader.fieldnames + NEW_COLUMNS

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        for col in NEW_COLUMNS:
            row[col] = ""  # initialize empty

        writer.writerow(row)

print("Columns added →", OUTPUT)