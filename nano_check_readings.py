import csv

with open("kml/data/kanji/kanji_master.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for i, row in enumerate(reader, start=2):
        category = row.get("category", "").strip()
        on = row.get("on_reading", "").strip()
        kun = row.get("kun_readings", "").strip()
        kanji = row.get("kanji", "")

        if category == "joyo" and not (on or kun):
            print(f"Missing reading → line {i}: {kanji}")