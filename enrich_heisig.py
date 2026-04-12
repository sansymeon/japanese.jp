import csv

input_file = "data/kanji/heisig_clean.csv"
output_file = "data/kanji/heisig_enriched.csv"

PRIMITIVE_MAP = {
    "pent in": "enclosure",
    "human legs": "legs",
    "animal legs": "legs",
    "top hat": "lid",
    "diced": "cut"
}

def convert_components(text):
    if not text:
        return ""

    parts = [p.strip() for p in text.split(";")]
    mapped = [PRIMITIVE_MAP.get(p, p) for p in parts]

    return "; ".join(mapped)

def count_primitives(text):
    if not text:
        return 0
    return len([p for p in text.split(";") if p.strip()])

with open(input_file, newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)

    fieldnames = [
        "kanji",
        "heisig_number",
        "heisig_keyword",
        "heisig_components",
        "kml_primitives",
        "primitive_count"
    ]

    with open(output_file, "w", newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            heisig_comp = row.get("components", "").strip()

            kml = convert_components(heisig_comp)
            count = count_primitives(kml)

            writer.writerow({
                "kanji": row["kanji"],
                "heisig_number": row["heisig_number"],
                "heisig_keyword": row["heisig_keyword"],
                "heisig_components": heisig_comp,
                "kml_primitives": kml,
                "primitive_count": count
            })