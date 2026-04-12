import csv
import xml.etree.ElementTree as ET
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent

KANJIDIC = ROOT / "kanjidic2.xml"
OUTPUT = ROOT / "data/kanji/kanji_readings_all.csv"

def clean_kun(text):
    return text.replace(".", "-")

def is_katakana(text):
    # allow only clean katakana ON readings
    return re.fullmatch(r"[ァ-ヶー]+", text or "") is not None

def is_hiragana(text):
    return re.fullmatch(r"[ぁ-ゖー\-]+", text or "") is not None

tree = ET.parse(KANJIDIC)
root = tree.getroot()

rows = []

for char in root.findall("character"):
    literal = char.findtext("literal")

    on_readings = []
    kun_readings = []

    rmgroup = char.find("reading_meaning/rmgroup")

    if rmgroup is not None:
        for r in rmgroup.findall("reading"):
            r_type = r.get("r_type")
            text = r.text

            if not text:
                continue

            if r_type == "ja_on":
                if is_katakana(text):
                    on_readings.append(text)

            elif r_type == "ja_kun":
                cleaned = clean_kun(text)
                if is_hiragana(cleaned):
                    kun_readings.append(cleaned)

    # remove duplicates while preserving order
    on_readings = list(dict.fromkeys(on_readings))
    kun_readings = list(dict.fromkeys(kun_readings))

    rows.append({
        "kanji": literal,
        "on_readings": "|".join(on_readings),
        "kun_readings": "|".join(kun_readings)
    })

print(f"Extracted {len(rows)} kanji")

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["kanji", "on_readings", "kun_readings"]
    )
    writer.writeheader()
    writer.writerows(rows)

print("Done → kanji_readings_all.csv created")