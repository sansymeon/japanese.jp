import csv
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KANJIDIC = ROOT / "kanjidic2.xml"
MASTER = ROOT / "data/kanji/kanji_master.csv"

# Old kanjidic JLPT (1=hardest, 4=easiest) → current N1–N5 labels.
# Level 2 spans N3 and N2; split by school grade from master CSV.
N2_GRADES = {"9", "10", "S", "H", "J"}


def load_jlpt_levels() -> dict[str, str]:
    levels: dict[str, str] = {}
    for _, elem in ET.iterparse(KANJIDIC, events=("end",)):
        if elem.tag != "character":
            continue

        kanji = elem.findtext("literal")
        misc = elem.find("misc")
        if kanji and misc is not None:
            jlpt = misc.find("jlpt")
            if jlpt is not None and jlpt.text:
                levels[kanji] = jlpt.text.strip()

        elem.clear()

    return levels


def map_jlpt(old_level: str, grade: str) -> str:
    if old_level == "4":
        return "N5"
    if old_level == "3":
        return "N4"
    if old_level == "2":
        return "N2" if grade in N2_GRADES else "N3"
    if old_level == "1":
        return "N1"
    return ""


def main() -> None:
    jlpt_levels = load_jlpt_levels()
    print(f"Loaded JLPT for {len(jlpt_levels)} kanji from kanjidic2.xml")

    with open(MASTER, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError("kanji_master.csv has no header")

        if "jlpt" not in fieldnames:
            grade_idx = fieldnames.index("grade")
            fieldnames = fieldnames[: grade_idx + 1] + ["jlpt"] + fieldnames[grade_idx + 1 :]

        rows = []
        filled = 0
        for row in reader:
            if None in row:
                del row[None]

            kanji = (row.get("kanji") or "").strip()
            old_level = jlpt_levels.get(kanji, "")
            row["jlpt"] = map_jlpt(old_level, (row.get("grade") or "").strip()) if old_level else ""
            if row["jlpt"]:
                filled += 1
            rows.append(row)

    with open(MASTER, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {MASTER}")
    print(f"Filled jlpt → {filled}")
    print(f"Empty jlpt → {len(rows) - filled}")


if __name__ == "__main__":
    main()
