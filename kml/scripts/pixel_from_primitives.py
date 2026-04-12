import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT = BASE_DIR / "data/kanji/kanji_master.csv"
OUTPUT = BASE_DIR / "data/kanji/pixel_prompts_primitives.csv"

BASE = "64x64 pixel art, minimal style, 3-5 colors, clean pixel edges"

PRIMITIVE_VISUAL_MAP = {
    "sun": "a glowing sun",
    "moon": "a crescent moon",
    "mouth": "a square mouth shape",
    "eye": "an eye shape",
    "line": "a straight line",
    "enclosure": "a square boundary",
    "legs": "two downward strokes",
    "lid": "a flat top covering",
    "cut": "a diagonal slash",
    "split": "two diverging lines"
}

def build_from_primitives(primitives):
    if not primitives:
        return "simple abstract symbol"

    parts = []
    for p in primitives.split(";"):
        p = p.strip()
        parts.append(PRIMITIVE_VISUAL_MAP.get(p, p))

    return ", ".join(parts)

rows = []

with open(INPUT, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        kanji = row["kanji"]
        slug = row["slug"]
        primitives = row.get("kml_primitives", "")

        concept = build_from_primitives(primitives)
        prompt = f"{BASE}, {concept}"

        rows.append({
            "kanji": kanji,
            "slug": slug,
            "prompt": prompt
        })

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["kanji", "slug", "prompt"])
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Generated {len(rows)} primitive prompts")