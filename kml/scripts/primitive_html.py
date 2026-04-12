import csv

INPUT_FILE = "data/kanji/heisig_clean_step2b.csv"
LIMIT = 100


def build_primitives_html(primitives):
    if not primitives:
        return '<div class="kanji-primitives"></div>'

    # normalize separators just in case
    primitives = primitives.replace(";", "|").replace(" ", "")

    parts = [p for p in primitives.split("|") if p]

    html_lines = ['<div class="kanji-primitives">']

    for p in parts:
        html_lines.append(f'  <span data-primitive="{p}">{p}</span>')

    html_lines.append('</div>')

    return "\n".join(html_lines)


with open(INPUT_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for i, row in enumerate(reader):
        if i >= LIMIT:
            break

        kanji = row.get("kanji", "").strip()
        primitives = row.get("kml_primitives", "").strip()

        if not kanji:
            print(f"⚠️ Skipping row {i} (missing kanji)")
            continue

        html = build_primitives_html(primitives)

        print(f"\n=== {kanji} ===")
        print(html)