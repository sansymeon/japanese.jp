import csv

PRIMITIVE_TO_KANJI = {
    # ===== CORE NATURAL ELEMENTS =====
    "water": "水",
    "fire": "火",
    "earth": "土",
    "ground": "土",
    "wind": "風",
    "air": "気",
    "tree": "木",
    "wood": "木",
    "forest": "林",
    "rice field": "田",
    "field": "田",
    "mountain": "山",
    "river": "川",
    "stone": "石",
    "metal": "金",
    "gold": "金",

    # ===== BODY PARTS =====
    "eye": "目",
    "ear": "耳",
    "mouth": "口",
    "nose": "鼻",
    "hand": "手",
    "foot": "足",
    "leg": "足",
    "heart": "心",
    "body": "体",
    "head": "頭",
    "face": "顔",

    # ===== PEOPLE =====
    "person": "人",
    "man": "男",
    "woman": "女",
    "child": "子",
    "father": "父",
    "mother": "母",
    "friend": "友",

    # ===== BASIC FORMS =====
    "one": "一",
    "two": "二",
    "three": "三",
    "ten": "十",
    "hundred": "百",
    "thousand": "千",

    # ===== SHAPES / STRUCTURE =====
    "line": "一",
    "stick": "丨",
    "hook": "乙",
    "drop": "丶",
    "dot": "丶",
    "box": "口",
    "enclosure": "囗",

    # ===== TIME / NATURE =====
    "sun": "日",
    "day": "日",
    "moon": "月",
    "month": "月",
    "light": "光",

    # ===== COMMON COMPONENT KANJI =====
    "shell": "貝",
    "money": "貝",
    "fish": "魚",
    "bird": "鳥",
    "horse": "馬",
    "dog": "犬",
    "insect": "虫",

    # ===== ACTION / CONCEPT =====
    "see": "見",
    "say": "言",
    "speak": "言",
    "go": "行",
    "come": "来",
    "enter": "入",
    "exit": "出",

    # ===== COMMON BUILDING BLOCKS =====
    "temple": "寺",
    "gate": "門",
    "roof": "宀",
    "house": "家",

    # ===== MATERIALS =====
    "rice": "米",
    "thread": "糸",
    "cloth": "衣",

    # ===== DIRECTIONS =====
    "up": "上",
    "down": "下",
    "left": "左",
    "right": "右",
    "middle": "中",

    # ===== NUMERIC / ABSTRACT =====
    "many": "多",
    "few": "少",
    "big": "大",
    "small": "小",

    # ===== COMMON RADICAL-LIKE =====
    "knife": "刀",
    "sword": "刀",
    "power": "力",
    "strength": "力",

    # ===== WATER VARIANTS =====
    "water radical": "水",

    # ===== FIRE VARIANTS =====
    "fire radical": "火",

    # ===== EARTH VARIANTS =====
    "soil": "土",

    # ===== ADDITIONAL SAFE =====
    "village": "村",
    "book": "本",
    "origin": "本",
    "car": "車",
    "road": "道",

    # ===== VERY COMMON =====
    "king": "王",
    "jade": "玉",
    "work": "工",
    "craft": "工",

    # ===== EXTRA SAFE EXTENSIONS =====
    "blue": "青",
    "red": "赤",
    "white": "白",
    "black": "黒",

    "rain": "雨",
    "snow": "雪",

    "grass": "草",
    "flower": "花",
}
def split_field(val):
    if not val:
        return []
    return [v.strip() for v in val.split("|") if v.strip()]

input_file = "data/kanji/heisig_clean_step1.csv"
output_file = "data/kanji/heisig_clean_step2.csv"

with open(input_file, encoding="utf-8") as infile, \
     open(output_file, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        primitives = split_field(row.get("kml_primitives", ""))

        new_primitives = []
        for p in primitives:
            p_clean = p.strip()
            key = p_clean.lower()

            # keep existing kanji as-is
            if len(p_clean) == 1 and '\u4e00' <= p_clean <= '\u9fff':
                new_primitives.append(p_clean)
                continue

            if key in PRIMITIVE_TO_KANJI:
                mapped = PRIMITIVE_TO_KANJI[key]

                # protect first appearance
                if mapped == row["kanji"]:
                    new_primitives.append(p_clean)
                else:
                    new_primitives.append(mapped)
            else:
                new_primitives.append(p_clean)

        row["kml_primitives"] = "|".join(new_primitives)
        writer.writerow(row)

print("Step 2 complete →", output_file)