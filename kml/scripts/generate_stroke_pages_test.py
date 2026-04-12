import csv
import re
from pathlib import Path

# =====================================================
# ROOT (script is now in /kml/)
# =====================================================
ROOT = Path(__file__).resolve().parent

# =====================================================
# PATHS
# =====================================================
TEMPLATE = ROOT / "tools/strokes/template/stroke_template.html"
OUTPUT_DIR = ROOT / "tools/strokes/pages"
CSV_FILE = ROOT / "data/kanji/kanji_master.csv"
SVG_DIR = ROOT / "data/kanjivg"

# =====================================================
# DEBUG (safe now)
# =====================================================
print("ROOT:", ROOT)
print("TEMPLATE EXISTS:", TEMPLATE.exists())
print("CSV EXISTS:", CSV_FILE.exists())
print("SVG DIR EXISTS:", SVG_DIR.exists())

# ensure output folder exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# BUILD CONTROL (CHANGE THIS ONLY)
# =====================================================
MODE = "test"   # "single", "test", "full"

TARGET = {"二"}     # used when MODE = "single"
TEST_COUNT = 5      # used when MODE = "test"

# =====================================================
# HELPERS
# =====================================================
def clean_field(val):
    if not val:
        return ""
    return str(val).replace('"', '').strip()

def get_slug(row):
    slug = clean_field(row.get("slug"))
    if not slug:
        raise ValueError(f"Missing slug for kanji: {row.get('kanji')}")
    return slug

def get_reading(row):
    on = clean_field(row.get("on_reading"))
    kun = clean_field(row.get("kun_readings"))
    return on or kun or ""

# =====================================================
# SORTING
# =====================================================
def sort_key(row):
    grade = clean_field(row.get("grade"))
    heisig = clean_field(row.get("heisig_number")) or "999999"
    freq = clean_field(row.get("frequency_rank")) or "999999"

    if grade in ["1", "2", "3", "4", "5", "6"]:
        return (0, int(grade), int(heisig))
    else:
        return (1, int(freq))

# =====================================================
# SVG CLEANING
# =====================================================
def clean_svg(svg):
    svg = re.sub(r'<\?xml.*?\?>', '', svg)
    svg = re.sub(r'<!DOCTYPE.*?\]>', '', svg, flags=re.DOTALL)
    svg = re.sub(r'style="[^"]*"', '', svg)
    svg = re.sub(r'<g id="kvg:StrokeNumbers.*?</g>', '', svg, flags=re.DOTALL)
    return svg.strip()

def load_svg_inline(unicode_val):
    if not unicode_val:
        return ""

    # Extract hex safely (handles U+4E00, 4E00, etc.)
    match = re.search(r'([0-9A-Fa-f]{4,5})', unicode_val)
    if not match:
        print(f"⚠️ Bad unicode: {unicode_val}")
        return ""

    code = match.group(1).lower().zfill(5)

    svg_path = SVG_DIR / f"{code}.svg"

    if not svg_path.exists():
        print(f"⚠️ Missing SVG: {code}.svg")
        return ""

    svg = svg_path.read_text(encoding="utf-8")
    return clean_svg(svg)

# =====================================================
# LOAD DATA
# =====================================================
template = TEMPLATE.read_text(encoding="utf-8")

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = [row for row in reader if clean_field(row.get("kanji"))]

rows_sorted = sorted(rows, key=sort_key)

# =====================================================
# GENERATE
# =====================================================
count = 0

for i, row in enumerate(rows_sorted):
    kanji = clean_field(row.get("kanji"))

    # --- MODE: single ---
    if MODE == "single" and kanji not in TARGET:
        continue

    # --- MODE: test ---
    if MODE == "test" and count >= TEST_COUNT:
        break

    slug = get_slug(row)
    reading = get_reading(row)
    keyword = (clean_field(row.get("keyword")) or slug).replace("_", " ")
    unicode_val = clean_field(row.get("unicode"))

    svg_inline = load_svg_inline(unicode_val)

    if not svg_inline:
        print(f"⚠️ Skipping {kanji} (no SVG)")
        continue

    count += 1

    # --- navigation ---
    prev_slug = rows_sorted[i - 1]["slug"] if i > 0 else ""
    next_slug = rows_sorted[i + 1]["slug"] if i < len(rows_sorted) - 1 else ""

    prev_link = f"{prev_slug}.html" if prev_slug else ""
    next_link = f"{next_slug}.html" if next_slug else ""

    # --- build html ---
    html = template
    html = html.replace("{{KANJI}}", kanji)
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{READING}}", reading)
    html = html.replace("{{SLUG}}", slug)
    html = html.replace("{{SVG_INLINE}}", svg_inline)
    html = html.replace("{{PREV_LINK}}", prev_link)
    html = html.replace("{{NEXT_LINK}}", next_link)

    output_file = OUTPUT_DIR / f"{slug}.html"
    output_file.write_text(html, encoding="utf-8")

    print(f"✅ Generated: {slug}.html")

print(f"🎉 Done ({MODE.upper()})")