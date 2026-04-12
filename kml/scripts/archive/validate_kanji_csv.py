import csv
import re
from pathlib import Path

CSV_FILE = Path("data/kanji/kanji_master_level_one_1000.csv")

EXPECTED_COLUMNS = 27

def is_katakana(text):
    return bool(re.fullmatch(r'[ァ-ヶー, ]*', text or ""))

def is_hiragana(text):
    return bool(re.fullmatch(r'[ぁ-ゖー,\- ]*', text or ""))

def check_row(row_num, row):
    issues = []

    # 1. Column count
    if len(row) != EXPECTED_COLUMNS:
        issues.append(f"Column count = {len(row)} (expected {EXPECTED_COLUMNS})")

    def get(i):
        return row[i] if i < len(row) else ""

    slug = get(5)
    keyword = get(7)
    on = get(8)
    kun = get(9)

    # 2. Stray quotes
    if any('"' in col for col in row):
        issues.append("Stray quote found")

    # 3. Japanese comma
    if any('、' in col for col in row):
        issues.append("Japanese comma (、) used")

    # 4. Missing slug
    if not slug.strip():
        issues.append("Missing slug")

    # 5. Slug format
    if slug and not re.fullmatch(r'[a-z0-9_]+', slug):
        issues.append(f"Bad slug format: {slug}")

    # 6. Slug vs keyword mismatch (strict for Level 1)
    if slug and keyword and slug != keyword:
        issues.append(f"Slug != keyword ({slug} vs {keyword})")

    # 7. Double underscores
    if "__" in slug:
        issues.append("Double underscore in slug")

    # 8. Reading validation
    if on and not is_katakana(on):
        issues.append(f"ON reading not katakana: {on}")

    if kun and not is_hiragana(kun):
        issues.append(f"KUN reading not hiragana: {kun}")

    # 9. Known bad tokens
    if "joyo" in on or "joyo" in kun:
        issues.append("‘joyo’ leaked into readings")

    # 10. Trailing empty columns
    if len(row) > EXPECTED_COLUMNS:
        issues.append(f"Too many columns ({len(row)} > {EXPECTED_COLUMNS})")

        return issues


def main():
    print(f"Checking: {CSV_FILE}\n")

    with open(CSV_FILE, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        for i, row in enumerate(reader, start=2):
            issues = check_row(i, row)

            if issues:
                print(f"Row {i}: {row[0]}")
                for issue in issues:
                    print(f"  - {issue}")
                print()

    print("Done.")


if __name__ == "__main__":
    main()