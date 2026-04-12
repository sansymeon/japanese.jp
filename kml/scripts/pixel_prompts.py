import csv
from pathlib import Path

INPUT = Path("data/kanji/kanji_master.csv")
OUTPUT = Path("data/kanji/pixel_prompts.csv")

# --- STYLE BASE ---
BASE = "64x64 pixel art, minimal style, 3-5 colors, no text, clean pixel edges, simple composition"

# --- HIGH QUALITY OVERRIDES (manual, small set) ---
OVERRIDE_MAP = {
    "sun": "a glowing sun inside a square frame",
    "moon": "a crescent moon glowing softly in a dark sky",
    "bright": "sun and moon side by side emitting strong light",
    "sparkle": "three glowing lights forming a triangular cluster",
}

# --- CATEGORY ASSIGNMENT ---
CATEGORY_MAP = {
    "sun": "sky",
    "moon": "sky",
    "day": "sky",
    "dawn": "sky",

    "eye": "body",
    "mouth": "body",
    "spine": "body",

    "person": "person",
    "woman": "person",
    "child": "person",

    "tree": "nature_object",
    "forest": "nature_group",
    "woods": "nature_group",
    "rice_field": "grid",

    "bright": "light",
    "early": "time",
    "old": "age",
    "risk": "danger",
    "goods": "objects",
    "chant": "sound",
    "sparkle": "light_cluster",
}

# --- CATEGORY TEMPLATES ---
TEMPLATES = {
    "sky": "a glowing {keyword} in a simple sky with soft gradient background",
    "body": "a simplified human {keyword}, bold outline, centered composition",
    "person": "a simple human figure representing {keyword}, minimal pose",
    "nature_object": "a simple {keyword} with clean shape and natural colors",
    "nature_group": "a cluster of {keyword}s grouped together",
    "grid": "a square divided into sections representing {keyword}",
    "light": "a glowing light source representing {keyword}, strong contrast",
    "light_cluster": "multiple glowing points forming a cluster",
    "time": "sun near horizon suggesting {keyword}",
    "age": "an old worn object representing {keyword}, cracked texture",
    "danger": "a small figure approaching danger representing {keyword}",
    "objects": "stacked simple items representing {keyword}",
    "sound": "open mouth with sound waves radiating outward",
}

# --- FALLBACK ---
def fallback(keyword):
    return f"a symbolic representation of {keyword}, simple abstract form"

# --- MAIN PROMPT BUILDER ---
def build_prompt(keyword):
    k = keyword.lower()

    # 1. override (highest quality)
    if k in OVERRIDE_MAP:
        concept = OVERRIDE_MAP[k]

    # 2. category template (main system)
    elif k in CATEGORY_MAP:
        category = CATEGORY_MAP[k]
        template = TEMPLATES.get(category)
        if template:
            concept = template.format(keyword=k)
        else:
            concept = fallback(k)

    # 3. fallback (last resort)
    else:
        concept = fallback(k)

    return f"{BASE}, {concept}"

rows = []

with open(INPUT, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        kanji = row.get("kanji")
        slug = row.get("slug")
        keyword = (row.get("keyword") or slug).strip()

        prompt = build_prompt(keyword)

        rows.append({
            "kanji": kanji,
            "slug": slug,
            "keyword": keyword,
            "prompt": prompt
        })

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["kanji", "slug", "keyword", "prompt"])
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Generated {len(rows)} prompts → {OUTPUT}")