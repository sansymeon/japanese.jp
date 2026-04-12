#!/usr/bin/env python3
"""
Extract stroke counts from kanjidic2.xml and fill empty strokes in kanji_master.csv.
Output: kanji_master_updated.csv
"""
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
KANJIDIC_PATH = Path.home() / "Downloads" / "kanjidic2.xml"
CSV_IN = SCRIPT_DIR / "kanji_master.csv"
CSV_OUT = SCRIPT_DIR / "kanji_master_updated.csv"

# Column index for strokes in kanji_master.csv (0-based: kanji, joyo_index, heisig_number, strokes, ...)
STROKES_COL = 3


def extract_stroke_counts(xml_path):
    """Parse kanjidic2.xml and return dict of literal -> stroke_count (first value only)."""
    stroke_map = {}
    for event, elem in ET.iterparse(xml_path, events=("end",)):
        if elem.tag != "character":
            continue
        literal = None
        stroke_count = None
        for child in elem:
            if child.tag == "literal":
                literal = (child.text or "").strip()
            elif child.tag == "misc":
                for sub in child:
                    if sub.tag == "stroke_count":
                        stroke_count = (sub.text or "").strip()
                        break  # use first stroke_count only
                break
        if literal and stroke_count:
            stroke_map[literal] = stroke_count
        elem.clear()
    return stroke_map


def main():
    if not KANJIDIC_PATH.exists():
        raise SystemExit(f"kanjidic2.xml not found at {KANJIDIC_PATH}")

    print("Reading stroke counts from kanjidic2.xml...")
    stroke_map = extract_stroke_counts(KANJIDIC_PATH)
    print(f"  Loaded {len(stroke_map)} kanji stroke counts.")

    print(f"Reading {CSV_IN}...")
    with open(CSV_IN, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    if not rows:
        raise SystemExit("CSV is empty.")

    filled = 0
    for i in range(1, len(rows)):
        row = rows[i]
        if len(row) <= STROKES_COL:
            continue
        if not (row[STROKES_COL] or row[STROKES_COL].strip()):
            kanji = (row[0] or "").strip()
            if kanji and kanji in stroke_map:
                row[STROKES_COL] = stroke_map[kanji]
                filled += 1

    print(f"Filled {filled} empty stroke counts.")

    print(f"Writing {CSV_OUT}...")
    with open(CSV_OUT, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)

    print("Done.")


if __name__ == "__main__":
    main()
