import csv
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent

ALPHA = ROOT / "data/kanji/kanji_master_level_one_alpha.csv"
XML = ROOT / "data/kanji/kanjidic2.xml"
OUT = ROOT / "data/kanji/level_one_kanji_master.csv"

# --- load XML readings (first only) ---
tree = ET.parse(XML)
root = tree.getroot()

reading_map = {}

for char in root.findall("character"):
    literal = char.findtext("literal")
    rmgroup = char.find("reading_meaning/rmgroup")

    on_list = []
    kun_list = []

    if rmgroup is not None:
        for r in rmgroup.findall("reading"):
            t = r.get("r_type")
            txt = r.text
            if t == "ja_on":
                on_list.append(txt)
            elif t == "ja_kun":
                kun_list.append(txt)

    on = on_list[0] if on_list else ""
    kun = kun_list[0] if kun_list else ""

    # normalize KUN (KANJIDIC format → your format)
    kun = kun.replace(".", "-")

    # prevent duplicated ON→KUN
    if kun == on:
        kun = ""

    reading_map[literal] = (on, kun)

print(f"Loaded XML readings: {len(reading_map)}")

# --- build new file from alpha ---
rows_out = []

with open(ALPHA, encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows_out.append(header)

    for row in reader:
        kanji = row[0]

        if kanji in reading_map:
            on, kun = reading_map[kanji]

            # adjust if your columns differ
            row[8] = on
            row[9] = kun

        rows_out.append(row)

# --- write output ---
with open(OUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows_out)

print("Done → level_one_kanji_master.csv created")