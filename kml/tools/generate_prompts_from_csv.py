import csv
import json
from pathlib import Path

# ===== PATHS (match your structure) =====
ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "data/kanji/kanji_master.csv"
PRIMITIVE_FILE = ROOT / "config/kml_primitive_map.json"
OUTPUT_JSON = ROOT / "assets/prompts/kml_prompts.json"

# ===== LOAD DATA =====
with open(PRIMITIVE_FILE, "r", encoding="utf-8") as f:
    PRIMITIVES = json.load(f)

# ===== BASE TEMPLATE =====
BASE_TEMPLATE = """
Minimal educational icon representing the kanji "{kanji}", built strictly from its primitive components.

Visual composition:
{composition}

Style:
- Flat vector style
- Clean edges, uniform line weight
- 3–5 muted colors maximum
- No gradients, no textures
- No facial expressions, no characters, no storytelling

Background:
- Soft, quiet, low-contrast neutral tone
- No patterns, no borders, no shadows

Constraints:
- No text, no kanji, no letters, no numbers
- Must visually reinforce structure, not concept

Output:
- Square format (1:1)
- Centered composition
- Consistent style for a kanji learning system
"""

# ===== HELPERS =====
def parse_components(row):
    """
    Priority:
    1. kml_primitives
    2. cluster_components
    """
    raw = row.get("kml_primitives") or row.get("cluster_components") or ""
    
    # split on common separators
    parts = [
    p.strip()
    for p in raw.replace(",", " ")
               .replace("、", " ")
               .replace("|", " ")
               .split()
]
    
    return [p for p in parts if p]


def build_composition(components):
    lines = []
    seen = []

    for c in components:
        if c not in seen:
            seen.append(c)

    for primitive in seen:
        count = components.count(primitive)

        if primitive not in PRIMITIVES:
            print(f"⚠️ Unknown primitive: {primitive} in {components}")
            continue

        data = PRIMITIVES[primitive]

        if count == 1:
            lines.append(
                f"- one {data['name']} represented as a {data['shape']}"
            )
        else:
            lines.append(
                f"- {count} identical {data['name']} shapes, each as a {data['shape']}, repeated in original order"
            )

    return "\n".join(lines)

def generate_prompt(kanji, components):
    composition = build_composition(components)

    return BASE_TEMPLATE.format(
        kanji=kanji,
        composition=composition
    ).strip()


def generate_filename(slug):
    return f"{slug}.png"


# ===== MAIN PIPELINE =====
def run():
    results = []

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            kanji = row.get("kanji", "").strip()
            slug = row.get("slug", "").strip()

            if not kanji or not slug:
                continue

            components = parse_components(row)

            # skip if no primitives (prevents garbage prompts)
            if not components:
                continue

            prompt = generate_prompt(kanji, components)
            filename = generate_filename(slug)

            results.append({
                "kanji": kanji,
                "slug": slug,
                "components": components,
                "filename": filename,
                "prompt": prompt
            })

    # ensure output folder exists
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated {len(results)} prompts → {OUTPUT_JSON}")


# ===== RUN =====
if __name__ == "__main__":
    run()