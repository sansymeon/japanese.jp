import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CSV_FILE = ROOT / "data/kanji/kanji_master.csv"
SVG_DIR = ROOT / "data/kanjivg"
PAGE_DIR = ROOT / "tools/strokes/pages"

slugs = set()
duplicates = []
missing_svg = []
missing_pages = []
missing_strokes = []

with CSV_FILE.open(encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for row in reader:

        kanji = row["kanji"].strip()
        slug = row["slug"].strip()
        strokes = row["strokes"].strip()

        # duplicate slug check
        if slug in slugs:
            duplicates.append(slug)
        slugs.add(slug)

        # stroke count check
        if not strokes:
            missing_strokes.append(kanji)

        # svg check
        hex_code = format(ord(kanji), "x")
        svg_path = SVG_DIR / f"{hex_code}.svg"

        if not svg_path.exists():
            missing_svg.append(kanji)

        # html page check
        page = PAGE_DIR / f"{slug}.html"

        if not page.exists():
            missing_pages.append(slug)

print("\nKANJI SYSTEM CHECK\n")

print("Duplicate slugs:")
for s in duplicates:
    print(" ", s)

print("\nMissing stroke SVG:")
for k in missing_svg:
    print(" ", k)

print("\nMissing stroke count:")
for k in missing_strokes:
    print(" ", k)

print("\nMissing stroke page:")
for p in missing_pages:
    print(" ", p)

print("\nCheck complete.")