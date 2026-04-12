import csv
from pathlib import Path
from collections import defaultdict

FILE = Path("data/kanji/kanji_master.csv")

slug_map = defaultdict(list)
keyword_map = defaultdict(list)
mismatch = []

with open(FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for i, row in enumerate(reader, start=2):

        if None in row:
            del row[None]

        kanji = row.get("kanji", "")
        slug = (row.get("slug") or "").strip()
        keyword_id = (row.get("keyword_id") or "").strip()
        keyword = (row.get("keyword") or "").strip()

        # --- duplicates ---
        if slug:
            slug_map[slug].append(i)

        if keyword:
            keyword_map[keyword].append(i)

        # --- alignment check ---
        if not (slug == keyword_id == keyword):
            mismatch.append(
                f"Row {i} [{kanji}] → slug='{slug}', keyword_id='{keyword_id}', keyword='{keyword}'"
            )

# --- report ---
print("\n===== KEYWORD VALIDATION =====\n")

# duplicates
dup_slug = [k for k, v in slug_map.items() if len(v) > 1]
dup_keyword = [k for k, v in keyword_map.items() if len(v) > 1]

if dup_slug:
    print("⚠ Duplicate slugs:")
    for k in dup_slug:
        print(f" - '{k}' → rows {slug_map[k]}")
else:
    print("✅ No duplicate slugs")

print()

if dup_keyword:
    print("⚠ Duplicate keywords:")
    for k in dup_keyword:
        print(f" - '{k}' → rows {keyword_map[k]}")
else:
    print("✅ No duplicate keywords")

print()

# mismatches
if mismatch:
    print("⚠ Alignment issues (slug ≠ keyword_id ≠ keyword):")
    for m in mismatch[:50]:
        print(" -", m)
    if len(mismatch) > 50:
        print(f"...and {len(mismatch)-50} more")
else:
    print("✅ slug, keyword_id, keyword fully aligned")

print("\nDone.\n")