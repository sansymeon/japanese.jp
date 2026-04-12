import csv
import re
from pathlib import Path

CSV_FILE = Path("data/kanji/kanji_master.csv")

def has_space(text):
    return " " in text if text else False

def has_upper(text):
    return any(c.isupper() for c in text) if text else False

def has_bad_chars(text):
    return bool(re.search(r"[;,]", text)) if text else False

def has_hyphen(text):
    return "-" in text if text else False

def has_double_underscore(text):
    return "__" in text if text else False

def is_missing(text):
    return not text or text.strip() == ""

with open(CSV_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    for i, row in enumerate(reader, start=2):
        issues = []

        kanji = row.get("kanji", "").strip()
        slug = row.get("slug", "").strip()
        keyword = row.get("keyword", "").strip()
        keyword_id = row.get("keyword_id", "").strip()

        # --- Missing ---
        if is_missing(keyword):
            issues.append("MISSING_KEYWORD")
        if is_missing(slug):
            issues.append("MISSING_SLUG")

        # --- Lowercase ---
        if has_upper(keyword):
            issues.append("KEYWORD_NOT_LOWERCASE")
        if has_upper(slug):
            issues.append("SLUG_NOT_LOWERCASE")

        # --- Underscore rules ---
        if has_space(keyword):
            issues.append("KEYWORD_HAS_SPACE")
        if has_space(slug):
            issues.append("SLUG_HAS_SPACE")

        # --- Format violations ---
        if has_bad_chars(keyword):
            issues.append("KEYWORD_MULTI_MEANING")
        if has_bad_chars(slug):
            issues.append("SLUG_BAD_CHARS")

        if has_hyphen(keyword):
            issues.append("KEYWORD_HAS_HYPHEN")
        if has_hyphen(slug):
            issues.append("SLUG_HAS_HYPHEN")

        if has_double_underscore(keyword):
            issues.append("KEYWORD_DOUBLE_UNDERSCORE")
        if has_double_underscore(slug):
            issues.append("SLUG_DOUBLE_UNDERSCORE")

        # --- Alignment ---
        if keyword and keyword_id and keyword != keyword_id:
            issues.append("KEYWORD_ID_MISMATCH")

        if keyword and slug and keyword != slug:
            issues.append("SLUG_MISMATCH")

        # --- Print only bad rows ---
        if issues:
            print(f"Line {i}: {kanji} → {', '.join(issues)}")