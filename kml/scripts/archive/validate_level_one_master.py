import csv
import re
from pathlib import Path

CSV_FILE = Path("data/kanji/kanji_master_level_one.csv")

EXPECTED_COLUMNS = 27

def is_katakana(text):
    return bool(re.fullmatch(r'[ァ-ヶー, ]*', text or ""))

def is_hiragana(text):
    return bool(re.fullmatch(r'[ぁ-ゖー,\- ]*', text or ""))

def check_row(row_num, row):
    issues = []

    def get(i):
        return row[i] if i < len(row) else ""

    # --- Column count ---
    if len(row) != EXPECTED_COLUMNS:
        issues.append(f"Column count = {len(row)} (expected {EXPECTED_COLUMNS})")

    # --- Key fields ---
    kanji = get(0)
    slug = get(5)
    keyword = get(7)
    on = get(8)
    kun = get(9)

    # --- Structural checks ---
    if any('"' in col for col in row):
        issues.append("Stray quote found")

    if any('、' in col for col in row):
        issues.append("Japanese comma (、) used")

    # --- Slug checks (do NOT modify, just report) ---
    if not slug.strip():
        issues.append("Missing slug")

    if slug and not re.fullmatch(r'[a-z0-9_]+', slug):
        issues.append(f"Bad slug format: {slug}")

    if "__" in slug:
        issues.append("Double underscore in slug")

    # --- Keyword check (read-only) ---
    if slug and keyword and slug != keyword:
        issues.append(f"Slug != keyword ({slug} vs {keyword})")

    # --- Reading validation (split-safe) ---
    for r in (on or "").split(","):
        r = r.strip()
        if r and not is_katakana(r):
            issues.append(f"ON not katakana: {r}")

    for r in (kun or "").split(","):
        r = r.strip()
        if r and not is_hiragana(r):
            issues.append(f"KUN not hiragana: {r}")

    # --- Detect fake KUN (important) ---
    if on and kun and on == kun:
        issues.append("KUN duplicated from ON (likely missing KUN)")

    # --- Detect 'joyo' leakage ---
    if any(r.strip() == "joyo" for r in (on or "").split(",")) \
    or any(r.strip() == "joyo" for r in (kun or "").split(",")):
        issues.append("‘joyo’ leaked into readings")

    return issues


def main():
    print(f"Checking: {CSV_FILE}\n")

    total = 0
    bad = 0

    with open(CSV_FILE, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        for i, row in enumerate(reader, start=2):
            total += 1
            issues = check_row(i, row)

            if issues:
                bad += 1
                print(f"Row {i}: {row[0]}")
                for issue in issues:
                    print(f"  - {issue}")
                print()

    print(f"\nChecked {total} rows")
    print(f"Issues found in {bad} rows")
    print("Done.")


if __name__ == "__main__":
    main()