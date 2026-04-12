import csv

MASTER = "data/kanji/kanji_master.csv"
HEISIG = "data/kanji/heisig_list.csv"
OUTPUT = "data/kanji/kanji_master_merged.csv"


# ------------------------------
# Primitive meanings (NEW)
# ------------------------------
PRIMITIVE_MEANINGS = {
    # Core strokes
    "一": "one", "丨": "line", "丶": "drop", "丿": "slash", "乙": "hook",

    # Basic forms
    "口": "mouth", "囗": "enclosure", "日": "sun", "月": "moon",
    "田": "field", "目": "eye",

    # Human / body
    "人": "person", "亻": "person", "儿": "legs", "女": "woman",
    "子": "child", "心": "heart", "忄": "heart",
    "手": "hand", "扌": "hand", "足": "foot",

    # Nature
    "水": "water", "氵": "water", "火": "fire", "灬": "fire dots",
    "木": "tree", "林": "forest", "山": "mountain",
    "川": "river", "土": "earth", "米": "rice",

    # Structure / covers
    "宀": "roof", "冖": "cover", "广": "building",
    "厂": "cliff", "几": "frame", "⺈": "bound", "勹": "wrap",

    # Tools / force
    "刀": "sword", "刂": "sword", "力": "power", "十": "ten",

    # Modifiers
    "艹": "grass", "竹": "bamboo", "⺍": "small",

    # Movement
    "辶": "walk",

    # Common semantic kanji
    "言": "speech", "貝": "shellfish", "車": "car",
    "門": "gate", "石": "stone",

    # Known clusters
    "見": "see", "古": "old", "早": "early",
    "明": "bright", "旦": "dawn", "占": "fortune"
}


# ------------------------------
# Normalize primitives
# ------------------------------
def normalize(text):
    if not text:
        return ""
    return (text
        .replace(";", "|")
        .replace(" ", "")
        .replace("⺉", "刂")
        .replace("⺃", "乙")
        .replace("⼇", "亠")
    )


# ------------------------------
# Load master (for keyword lookup)
# ------------------------------
master_lookup = {}

with open(MASTER, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        kanji = row.get("kanji", "").strip()
        keyword = row.get("keyword", "").strip()
        if kanji:
            master_lookup[kanji] = keyword


# ------------------------------
# Load Heisig
# ------------------------------
heisig_map = {}

with open(HEISIG, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        kanji = row.get("kanji", "").strip()
        if kanji:
            heisig_map[kanji] = row


# ------------------------------
# Build semantic cluster components
# ------------------------------
def build_cluster(primitives):
    parts = primitives.split("|")
    result = []

    for p in parts:
        if p in master_lookup and master_lookup[p]:
            result.append(master_lookup[p])  # use known kanji meaning
        elif p in PRIMITIVE_MEANINGS:
            result.append(PRIMITIVE_MEANINGS[p])  # use primitive meaning
        else:
            print("⚠️ Unknown primitive:", p)
            result.append(p)

    return "|".join(result)


# ------------------------------
# Merge
# ------------------------------
with open(MASTER, encoding="utf-8-sig") as infile, \
     open(OUTPUT, "w", newline="", encoding="utf-8-sig") as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    count = 0

    for row in reader:
        kanji = row.get("kanji", "").strip()

        if not kanji:
         continue

        # ✅ ADD THIS LINE HERE
        row["collapse_to"] = kanji

        if kanji in heisig_map:
            h = heisig_map[kanji]

            primitives = normalize(h.get("kml_primitives", "").strip())

            row["kml_primitives"] = primitives
            row["cluster_components"] = build_cluster(primitives)

        else:
            print("⚠️ Missing in heisig:", kanji)

        writer.writerow(row)
        count += 1


print("Merge complete →", OUTPUT)
print("Rows written:", count)