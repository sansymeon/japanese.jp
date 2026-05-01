import csv
import re
from pathlib import Path

# =====================================================
# ROOT
# =====================================================
ROOT = Path(__file__).resolve().parent.parent

# =====================================================
# PATHS
# =====================================================
TEMPLATE = ROOT / "tools/strokes/template/stroke_template.html"
OUTPUT_DIR = ROOT / "tools/strokes/pages"
CSV_FILE = ROOT / "data/kanji/kanji_master.csv"
SVG_DIR = ROOT.parent / "data/archive/kanjivg"

# =====================================================
# DEBUG
# =====================================================
print("ROOT:", ROOT)
print("TEMPLATE EXISTS:", TEMPLATE.exists())
print("CSV EXISTS:", CSV_FILE.exists())
print("SVG DIR EXISTS:", SVG_DIR.exists())
print((ROOT / "data/archive/kanjivg/04e00.svg").exists())

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# BUILD CONTROL
# =====================================================
MODE = "full"   # "single", "test", "full"
TARGET = {"二"}
TEST_COUNT = 5

# =====================================================
# HELPERS
# =====================================================
def clean_field(val):
    return val.strip() if val else ""

def get_slug(row):
    slug = clean_field(row.get("slug", ""))
    if not slug:
        raise ValueError(f"Missing slug for kanji: {row.get('kanji')}")
    return slug

def get_reading(row):
    on = clean_field(row.get("on_reading"))
    kun = clean_field(row.get("kun_readings"))
    return on or kun or ""

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

    # extract unicode hex safely
    match = re.search(r'U\+?([0-9A-Fa-f]{4,5})', unicode_val)
    if not match:
        print(f"⚠️ Bad unicode: {unicode_val}")
        return ""

    code = match.group(1).lower()

    # try multiple filename formats (covers all your cases)
    candidates = [
        SVG_DIR / f"{code.zfill(5)}.svg",   # 04ea5.svg
        SVG_DIR / f"{code}.svg",            # 4ea5.svg
        SVG_DIR / f"u{code}.svg",           # u4ea5.svg
        SVG_DIR / f"u{code.zfill(5)}.svg"   # u04ea5.svg
    ]

    for path in candidates:
        print("TRYING:", path)
        if path.exists():
            svg = path.read_text(encoding="utf-8")
            return clean_svg(svg)

    print(f"❌ Missing SVG: {code}")
    return ""
# =====================================================
# LOAD DATA
# =====================================================
template = TEMPLATE.read_text(encoding="utf-8")

with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

    print("HEADERS:", reader.fieldnames)

# remove empty kanji rows
rows = [row for row in rows if clean_field(row.get("kanji"))]

# KEEP CSV ORDER (important)
rows_sorted = rows

# =====================================================
# GENERATE
# =====================================================
count = 0

for i, row in enumerate(rows_sorted):
    kanji = clean_field(row.get("kanji"))

    print("LOOP HIT:", kanji)

    if MODE == "single" and kanji not in TARGET:
        continue

    if MODE == "test" and count >= TEST_COUNT:
        break

    slug = get_slug(row)
    reading = get_reading(row)
    keyword = (clean_field(row.get("keyword")) or slug).replace("_", " ")
    unicode_val = clean_field(row.get("unicode"))

    print("UNICODE:", unicode_val)

    svg_inline = load_svg_inline(unicode_val)

    print("SVG FOUND:", bool(svg_inline))

    if not svg_inline:
        print(f"⚠️ Skipping {kanji} (no SVG)")
        continue

    count += 1

    # =====================================================
    # NAVIGATION (FIXED — SAFE SLUG ACCESS)
    # =====================================================
    prev_slug = get_slug(rows_sorted[i - 1]) if i > 0 else ""
    next_slug = get_slug(rows_sorted[i + 1]) if i < len(rows_sorted) - 1 else ""

    prev_link = f"{prev_slug}.html" if prev_slug else ""
    next_link = f"{next_slug}.html" if next_slug else ""

    # =====================================================
    # BUILD HTML
    # =====================================================
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