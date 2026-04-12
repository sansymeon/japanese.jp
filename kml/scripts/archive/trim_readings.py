import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "data/kanji/kanji_master.csv"
OUTPUT = ROOT / "data/kanji/kanji_master_trimmed.csv"

HEADER = [
    "kanji","joyo_index","heisig_number","strokes","grade","slug","keyword_id","keyword",
    "on_reading","kun_readings","category","k_code","joyo_rank","radical","radical_index",
    "stroke_group","unicode","svg_file","reserved1","reserved2","status",
    "lesson_start","lesson_end","book_number","image","display_keyword"
]

CATEGORY_VALUES = {"joyo", "heisig_extra"}


def is_katakana_piece(s: str) -> bool:
    s = s.strip().replace("（", "").replace("）", "")
    if not s:
        return False
    for ch in s:
        if ch in "・.()（）-ー":
            continue
        if not ("\u30A0" <= ch <= "\u30FF"):
            return False
    return True


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        x = x.strip()
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


rows_out = []
bad_rows = 0

with open(MASTER, encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)

    for row in reader:
        if not row:
            continue

        # Need at least keyword area
        if len(row) < 11:
            bad_rows += 1
            continue

        # First 8 fixed fields
        fixed_start = row[:8]

        # Find category position after keyword
        category_idx = None
        for i in range(8, len(row)):
            if row[i].strip() in CATEGORY_VALUES:
                category_idx = i
                break

        if category_idx is None:
            bad_rows += 1
            continue

        reading_parts = [x.strip() for x in row[8:category_idx] if x.strip()]
        tail = row[category_idx:]  # category onward

        # Split readings into on / kun
        on_parts = []
        kun_parts = []

        for part in reading_parts:
            if is_katakana_piece(part):
                on_parts.append(part)
            else:
                kun_parts.append(part)

        on_parts = dedupe_keep_order(on_parts)[:2]
        kun_parts = dedupe_keep_order(kun_parts)[:2]

        new_row = (
            fixed_start
            + [",".join(on_parts), ",".join(kun_parts)]
            + tail
        )

        # Normalize row length to match header
        if len(new_row) < len(HEADER):
            new_row += [""] * (len(HEADER) - len(new_row))
        elif len(new_row) > len(HEADER):
            new_row = new_row[:len(HEADER)]

        rows_out.append(new_row)

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(HEADER)
    writer.writerows(rows_out)

print(f"Done → {OUTPUT.name} created")
print(f"Rows written → {len(rows_out)}")
print(f"Bad rows skipped → {bad_rows}")