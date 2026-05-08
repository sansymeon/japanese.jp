import csv
from pathlib import Path

BASE_DIR = Path("kml/data/kanji")

CSV_PATH = BASE_DIR / "kanji_production.csv"
MASK_DIR = BASE_DIR / "masks"
PROMPT_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = BASE_DIR / "outputs"

PROMPT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

TEMPLATE = """Japanese kanji: {kanji}

Use the provided kanji mask image as the exact shape reference:
{mask_path}

Do not alter, reinterpret, stylize, correct, or improve the kanji structure.
Preserve the original mask shape exactly.

Apply painterly impasto oil paint texture to the existing kanji form.
The result must look like paint integrated into the canvas surface, not sculpted relief.
No 3D extrusion, no carved edges, no beveling, no cast shadows.

Lesson palette:
{lesson_palette}

Background flow:
{flow}

Mode:
{mode}

The kanji and background should be created together as one cohesive painted surface.
The background must complement the kanji, not compete with it.

Allow natural paint imperfections, but never distort the kanji form.
Square composition, centered, balanced margins.
"""

def clean(value: str) -> str:
    return (value or "").strip()

with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        kanji = clean(row.get("kanji"))
        slug = clean(row.get("slug"))
        flow = clean(row.get("flow"))
        mode = clean(row.get("mode"))
        lesson_palette = clean(row.get("lesson_palette")) or clean(row.get("palette"))

        if not slug:
            print(f"SKIP: missing slug for {kanji}")
            continue

        mask_path = MASK_DIR / f"{slug}.png"

        if not mask_path.exists():
            print(f"MISSING MASK: {kanji} → {mask_path}")
            continue

        prompt = TEMPLATE.format(
            kanji=kanji,
            mask_path=mask_path.as_posix(),
            lesson_palette=lesson_palette,
            flow=flow,
            mode=mode,
        )

        prompt_file = PROMPT_DIR / f"{slug}.txt"
        prompt_file.write_text(prompt, encoding="utf-8")

        print(f"OK: {kanji} → {prompt_file}")

print("Done.")