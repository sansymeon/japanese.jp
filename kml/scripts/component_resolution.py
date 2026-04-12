import csv
import os

def split_field(val):
    if not val:
        return []
    return [v.strip() for v in val.split("|") if v.strip()]

def load_data(path):
    data = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def build_kanji_map(data):
    return {row["kanji"]: row for row in data}

def resolve_components(row, kanji_map, learned):
    comps = split_field(row["kml_primitives"])
    result = []

    for c in comps:
        if c in learned and c in kanji_map:
            cluster = kanji_map[c]["cluster_components"]
            if cluster:
                result.append(cluster)
            else:
                result.append(c)
        else:
            result.append(c)

    return result

# --- main ---
data = load_data("data/kanji/heisig_enriched.csv")
kanji_map = build_kanji_map(data)

learned = set()

for row in data:
    comps = resolve_components(row, kanji_map, learned)

    print(row["kanji"], "→", " | ".join(comps))

    learned.add(row["kanji"])