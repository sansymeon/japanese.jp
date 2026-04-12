import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent

MASTER = ROOT / "data/kanji/kanji_master.csv"
KANJI_EXTRA = ROOT / "data/kanji/heisig_extra_readings.csv"
OUTPUT = ROOT / "data/kanji/kanji_master_enriched.csv"

# --- load kanjidic readings ---
reading_map = {}

with open(KANJI_EXTRA, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        k = row.get("kanji")
        if not k:
            continue

        reading_map[k] = {
            "on": (row.get("on_reading") or "").strip(),
            "kun": (row.get("kun_readings") or "").strip()
        }

print(f"Loaded readings for {len(reading_map)} kanji")

# --- process master ---
rows_out = []
filled_on = 0
filled_kun = 0
skipped_bad = 0

with open(MASTER, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    fieldnames = reader.fieldnames
    if not fieldnames:
        raise ValueError("Header issue in kanji_master.csv")

    for row in reader:

        # 🔴 skip structurally broken rows
        if None in row:
            skipped_bad += 1
            continue

        kanji = row.get("kanji")
        if not kanji:
            continue

        if kanji in reading_map:

            # fill ON
            if not (row.get("on_reading") or "").strip():
                if reading_map[kanji]["on"]:
                    row["on_reading"] = reading_map[kanji]["on"]
                    filled_on += 1

            # fill KUN
            if not (row.get("kun_readings") or "").strip():
                if reading_map[kanji]["kun"]:
                    row["kun_readings"] = reading_map[kanji]["kun"]
                    filled_kun += 1

        rows_out.append(row)

# --- write output ---
with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames,
        extrasaction="ignore"   # 🔴 critical safety
    )
    writer.writeheader()
    writer.writerows(rows_out)

print("Done → kanji_master_enriched.csv created")
print(f"Filled on_reading → {filled_on}")
print(f"Filled kun_readings → {filled_kun}")
print(f"Skipped bad rows → {skipped_bad}")