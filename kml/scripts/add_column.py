import csv

input_file = "data/kanji/heisig_clean_step2.csv"
output_file = "data/kanji/heisig_clean_step2b.csv"

with open(input_file, encoding="utf-8") as infile, \
     open(output_file, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ["collapse_to"]

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        row["collapse_to"] = ""  # initialize empty
        writer.writerow(row)

print("Added collapse_to column →", output_file)