import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

input_file = BASE_DIR / "data/kanji/heisig_clean.csv"
output_file = BASE_DIR / "data/kanji/heisig_enriched.csv"

# --- NORMALIZATION MAP ---
PRIMITIVE_MAP = {
    "one": "line",
    "two": "line",
    "three": "line",
    "line": "line",
    "five": "five",
    "eight": "split",      # or "eight" if you prefer visual purity
    "concave": "concave",
    "convex": "convex",
    "small": "small",
    "little": "small",
    "eye": "eye",
    "mouth": "mouth",
    "sun": "sun",
    "day": "sun",
    "moon": "moon",
    "month": "moon",
    "flesh": "body",
    "part of the body": "body",
    "human legs": "legs",
    "animal legs": "legs",
    "pent in": "enclosure",
    "top hat": "lid",
    "diced": "cut",
    "baseball": "ball",
    "brains": "field",
    "needle": "ten",   # 🔥 critical fix
    "woman": "woman",
    "child": "child",
    "mother": "woman",
    "breasts": "body",
    "evening": "evening",
    "stone": "stone",
    "rock": "stone",
    "water": "water",
    "drop": "drop",
    "cliff": "cliff",
    "nose": "nose",
    "thread": "thread",
    "dot": "dot",
    "slash": "slash",
    "hook": "hook",
     "ground": "ground",
     "roof": "roof",
     "tree": "tree",
     "grass": "grass",
     "flower": "flower",
     "fire": "fire",
     "cut": "cut",     # already implied but good to lock
     "flow": "flow",
     "rise": "rise",
     "shellfish": "shell",
     "shell": "shell",
     "horns": "horns",
     "tail": "tail",
     "metal": "metal",
     "wood": "tree",   # normalize to tree (important decision)
     "person": "person",
     "side_ten": "side_ten"
}

# --- BLOCKED TERMS (🔥 NEW — removes unwanted meanings early) ---
BLOCKED = {
    "part of the body",
    "flesh",
    "needle",   # we already map it → ten, but block raw version
    "month"     # optional: forces moon-only system
}

# --- ALLOWED PRIMITIVES ---
ALLOWED = {
    # core strokes
    "line",
    "dot",
    "slash",
    "hook",

    # structure / abstract
    "ten",
    "side_ten",
    "split",
    "five",
    "concave",
    "convex",
    "enclosure",
    "roof",
    "field",
    "ground",
    "lid",

    # human / body
    "person",
    "woman",
    "child",
    "legs",
    "body",
    "mouth",
    "eye",
    "nose",

    # nature / world
    "sun",
    "moon",
    "water",
    "fire",
    "tree",
    "grass",
    "flower",
    "stone",
    "cliff",
    "evening",

    # materials / objects
    "metal",
    "shell",
    "ball",
    "thread",
    "drop",

    # animal / shape bases
    "horns",
    "tail",

    # size / form
    "small",

    # motion / action
    "cut",
    "flow",
    "rise"
}

# --- DEDUPLICATION ---
def dedupe_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

# --- MAIN CONVERSION ---
def convert_components(text):
    if not text:
        return ""

    parts = [p.strip().lower() for p in text.split(";") if p.strip()]
    mapped = []

    for p in parts:
        p = p.replace(":", "").strip()

        # 🔥 HARD BLOCK FIRST
        # ✅ correct
        if p in PRIMITIVE_MAP:
           p = PRIMITIVE_MAP[p]

        if p in BLOCKED:
           continue


        # strict filter
        if p in ALLOWED:
            mapped.append(p)

    # remove duplicates
    mapped = dedupe_preserve_order(mapped)

    return "; ".join(mapped)

def count_primitives(text):
    if not text:
        return 0
    return len([p for p in text.split(";") if p.strip()])

# --- PROCESS FILE ---
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
            heisig_comp = (row.get("components") or "").strip()

            # 🔥 MAIN
            kml = convert_components(heisig_comp)

            # 🔥 fallback
            if not kml:
                keyword = (row.get("heisig_keyword") or "").strip().lower()
                if keyword in PRIMITIVE_MAP:
                    kml = PRIMITIVE_MAP[keyword]

            # 🔥 always compute
            count = count_primitives(kml)

            # 🔥 write row
            writer.writerow({
                "kanji": row.get("kanji", ""),
                "heisig_number": row.get("heisig_number", ""),
                "heisig_keyword": row.get("heisig_keyword", ""),
                "heisig_components": heisig_comp,
                "kml_primitives": kml,
                "primitive_count": count
            })

print(f"✅ Enriched file written → {output_file}")