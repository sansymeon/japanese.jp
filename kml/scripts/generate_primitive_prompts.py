import csv
import re
from pathlib import Path

# ===== CONFIG =====

CSV_FILE = Path("data/kanji/kanji_master.csv")
OUTPUT_FILE = Path("data/kanji/primitive_prompts.csv")

# Choose style
USE_PIXEL_STYLE = False  # True = pixel icons, False = clean minimal icons

PROMPT_TEMPLATE = (
    'Minimal educational icon for the concept "{keyword}", '
    'centered composition, simple shapes, clean edges, square format, '
    'no text, no letters, no border, quiet background, consistent style '
    'for a kanji learning system'
)

PIXEL_PROMPT_TEMPLATE = (
    '64x64 pixel-art educational icon for "{keyword}", '
    'centered object, very simple composition, 3-5 colors, '
    'no text, no border, clean pixel edges, square format'
)

# ===== CRITICAL OVERRIDES =====
# Prevents AI from going off the rails

OVERRIDES = {
    "month": "moon (representing month in kanji system)",
    "seal": "stamp seal (inkan), not animal",
    "capital": "capital city, not money",
    "charge": "fee or cost, not electricity",
    "present": "gift box, not current time",
    "right": "direction right, not correctness",
    "left": "direction left",
    "spring": "season spring, not coil",
    "fall": "autumn leaves, not falling motion",
}

# ===== HELPERS =====

def clean_primitive(p):
    p = p.strip().lower()
    p = re.sub(r"\s+", " ", p)
    return p


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text


def extract_primitives(csv_path):
    primitives = set()

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            raw = row.get("kml_primitives", "")
            if not raw:
                continue

            for p in raw.split("|"):
                p = clean_primitive(p)
                if p:
                    primitives.add(p)

    return sorted(primitives)


def apply_override(keyword):
    return OVERRIDES.get(keyword, keyword)


def build_prompt(keyword):
    keyword_for_prompt = apply_override(keyword)
    template = PIXEL_PROMPT_TEMPLATE if USE_PIXEL_STYLE else PROMPT_TEMPLATE
    return template.format(keyword=keyword_for_prompt)


def generate_unique_filenames(primitives):
    """Ensure no filename collisions."""
    seen = {}
    filenames = {}

    for p in primitives:
        base = slugify(p)
        name = base

        if base in seen:
            seen[base] += 1
            name = f"{base}_{seen[base]}"
        else:
            seen[base] = 1

        filenames[p] = f"{name}.png"

    return filenames


# ===== MAIN =====

def main():
    if not CSV_FILE.exists():
        print(f"ERROR: CSV not found at {CSV_FILE}")
        return

    primitives = extract_primitives(CSV_FILE)
    print(f"Found {len(primitives)} unique primitives.")

    filenames = generate_unique_filenames(primitives)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # FINAL HEADER
        writer.writerow(["primitive", "filename", "prompt"])

        for p in primitives:
            filename = filenames[p]
            prompt = build_prompt(p)
            writer.writerow([p, filename, prompt])

    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()