import csv
from pathlib import Path

FILE = Path("data/kanji/kanji_master.csv")

with open(FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    issues = 0

    for i, row in enumerate(reader, start=2):
        kanji = row.get("kanji", "")
        slug = (row.get("slug") or "").strip()
        kid = (row.get("keyword_id") or "").strip()
        keyword = (row.get("keyword") or "").strip()

        # normalize for comparison
        slug_n = slug.lower().replace(" ", "_")
        kid_n = kid.lower().replace(" ", "_")
        keyword_n = keyword.lower().replace(" ", "_")

        # check missing
        if not slug or not kid or not keyword:
            print(f"Row {i} [{kanji}] → missing field(s): slug='{slug}' kid='{kid}' keyword='{keyword}'")
            issues += 1
            continue

        # check mismatch
        if not (slug_n == kid_n == keyword_n):
            print(f"Row {i} [{kanji}] → mismatch:")
            print(f"   slug       = {slug}")
            print(f"   keyword_id = {kid}")
            print(f"   keyword    = {keyword}")
            issues += 1

    print(f"\nDone. Found {issues} issue(s).")