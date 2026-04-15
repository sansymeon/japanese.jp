import csv
import unicodedata

INPUT = "data/kanji/kanji_master.csv"

# Characters that commonly break CSV / HTML / generators silently
SUSPECTS = {
    "\u2028": "LINE SEPARATOR",
    "\u2029": "PARAGRAPH SEPARATOR",
    "\u00A0": "NO-BREAK SPACE",
    "\u200B": "ZERO WIDTH SPACE",
    "\u200C": "ZERO WIDTH NON-JOINER",
    "\u200D": "ZERO WIDTH JOINER",
    "\u2060": "WORD JOINER",
    "\uFEFF": "BOM / ZERO WIDTH NO-BREAK SPACE",
    "\r": "CARRIAGE RETURN",
}

def visible_repr(text: str) -> str:
    return (
        text.replace("\u2028", "\\u2028")
            .replace("\u2029", "\\u2029")
            .replace("\u00A0", "\\u00A0")
            .replace("\u200B", "\\u200B")
            .replace("\u200C", "\\u200C")
            .replace("\u200D", "\\u200D")
            .replace("\u2060", "\\u2060")
            .replace("\uFEFF", "\\uFEFF")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
    )

def find_suspects(text: str):
    found = []
    for ch, name in SUSPECTS.items():
        if ch in text:
            found.append((ch, name, text.count(ch)))
    return found

with open(INPUT, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames or []

print(f"Scanning: {INPUT}")
print(f"Columns: {len(fieldnames)}")
print(f"Rows: {len(rows)}")
print("-" * 60)

problems = 0

for row_num, row in enumerate(rows, start=2):  # header is row 1
    for col in fieldnames:
        value = row.get(col, "")
        if value is None:
            continue

        suspects = find_suspects(value)
        if suspects:
            problems += 1
            print(f"Row {row_num}, column '{col}':")
            for ch, name, count in suspects:
                codepoint = f"U+{ord(ch):04X}"
                print(f"  - {name} ({codepoint}) x{count}")

            print(f"  Value: {visible_repr(value)}")
            print()

        # Optional extra warning for any other control chars
        for ch in value:
            cat = unicodedata.category(ch)
            if cat.startswith("C") and ch not in SUSPECTS and ch not in ("\n", "\t"):
                problems += 1
                print(f"Row {row_num}, column '{col}':")
                print(f"  - OTHER CONTROL CHAR U+{ord(ch):04X} ({unicodedata.name(ch, 'UNKNOWN')})")
                print(f"  Value: {visible_repr(value)}")
                print()
                break

if problems == 0:
    print("✅ No hidden Unicode troublemakers found.")
else:
    print(f"⚠️ Found {problems} suspicious field(s).")