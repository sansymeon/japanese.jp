#!/usr/bin/env python3
"""Apply Phase-1 component structures for lessons 71–80."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LESSONS = ROOT / "contents" / "books" / "book_01" / "lessons"
CATALOG = ROOT / "tools" / "ambient" / "data" / "kanji_components_catalog.json"


def render(node, indent: int = 2) -> str:
    pad = " " * indent
    if isinstance(node, str):
        return f'{pad}<span class="kanji-part">{node}</span>\n'
    kind, children = node
    cls = "stack-horizontal" if kind == "h" else "stack-vertical"
    out = [f'{pad}<div class="component-layout {cls}">\n']
    for c in children:
        out.append(render(c, indent + 2))
    out.append(f"{pad}</div>\n")
    return "".join(out)


def box(node) -> str:
    if isinstance(node, str):
        return (
            '<div class="component-box">\n'
            f'  <span class="kanji-part">{node}</span>\n'
            "</div>"
        )
    kind = node[0]
    attr = ' data-render-layout="h"' if kind == "h" else ' data-render-layout="v"'
    return (
        f'<div class="component-box"{attr}>\n'
        f"{render(node, 2)}"
        "</div>"
    )


def H(*xs):
    return ("h", list(xs))


def V(*xs):
    return ("v", list(xs))


# Shared clusters (nested; not new catalog glyphs)
ROLL = V("丷", "夫")
TRIPOD = V("一", "口", "冂", "儿")  # same approx as 融 left / 隔
ZI = V(H("幺", "幺"))  # double short thread ≈ 兹
BROOM = V("ヨ", "巾")


STRUCTURES: dict[int, dict[str, object]] = {
    71: {
        "附": H("阝", "付"),
        "院": H("阝", "完"),
        "陣": H("阝", "車"),
        "隊": H("阝", V("丷", "豕")),
        "墜": V("隊", "土"),
        "降": H("阝", V("夂", "ヰ")),
        "階": H("阝", "皆"),
        "陛": H("阝", V("比", "土")),
        "隣": H("阝", V("米", "舛")),
        "隔": H("阝", TRIPOD),
        "隠": H("阝", V("ヨ", "工", "心")),
        "堕": V(H("阝", "有"), "土"),
        "陥": H("阝", V("勹", "旧")),
        "穴": "穴",
        "空": V("穴", "工"),
        "控": H("扌", "空"),
        "突": V("穴", "犬"),
        "究": V("穴", "九"),
        "窒": V("穴", "至"),
        "窃": V("穴", "切"),
    },
    72: {
        "窟": V("穴", "屈"),
        "窪": V("穴", H("氵", "圭")),
        "搾": H("扌", V("穴", "乍")),
        "窯": V("穴", V("羊", "灬")),
        "窮": V("穴", H("身", "弓")),
        "探": H("扌", V("⺍", "木")),
        "深": H("氵", V("⺍", "木")),
        "丘": "丘",
        "岳": V("丘", "山"),
        "兵": V("丘", "八"),
        "浜": H("氵", "兵"),
        "糸": "糸",
        "織": H("糸", V("音", "戈")),
        "繕": H("糸", "善"),
        "縮": H("糸", "宿"),
        "繁": V("敏", "糸"),
        "縦": H("糸", "従"),
        "緻": H("糸", "致"),
        "線": H("糸", "泉"),
        "綻": H("糸", "定"),
    },
    73: {
        "締": H("糸", "帝"),
        "維": H("糸", "隹"),
        "羅": V("罒", "維"),
        "練": H("糸", "東"),
        "緒": H("糸", "者"),
        "続": H("糸", "売"),
        "絵": H("糸", "会"),
        "統": H("糸", "充"),
        "絞": H("糸", "交"),
        "給": H("糸", "合"),
        "絡": H("糸", "各"),
        "結": H("糸", "吉"),
        "終": H("糸", "冬"),
        "級": H("糸", "及"),
        "紀": H("糸", "己"),
        "紅": H("糸", "工"),
        "納": H("糸", "内"),
        "紡": H("糸", "方"),
        "紛": H("糸", "分"),
        "紹": H("糸", "召"),
    },
    74: {
        "経": H("糸", V("又", "土")),
        "紳": H("糸", "申"),
        "約": H("糸", "勺"),
        "細": H("糸", "田"),
        "累": V("田", "糸"),
        "索": V("十", "冖", "糸"),
        "総": H("糸", V("公", "心")),
        "綿": H("糸", V("白", "巾")),
        "絹": H("糸", V("口", "月")),
        "繰": H("糸", V("品", "木")),
        "継": H("糸", V("米", "乚")),
        "緑": H("糸", V("ヨ", "水")),
        "縁": H("糸", V("ヨ", "豕")),
        "網": H("糸", V("冂", "亡")),
        "緊": V(H("臣", "又"), "糸"),
        "紫": V("此", "糸"),
        "縛": H("糸", V("甫", "寸")),
        "縄": H("糸", "亀"),
        "幼": H("幺", "力"),
        "後": H("彳", V("幺", "夂")),
    },
    75: {
        "幽": V(H("幺", "幺"), "山"),
        "幾": V(H("幺", "幺"), H("戈", "人")),
        "機": H("木", "幾"),
        "畿": H("幾", "田"),
        "玄": "玄",
        "畜": V("玄", "田"),
        "蓄": V("艹", "畜"),
        "弦": H("弓", "玄"),
        "擁": H("扌", "雍"),
        "滋": H("氵", "兹"),
        "慈": V("兹", "心"),
        "磁": H("石", "兹"),
        "系": "系",
        "係": H("亻", "系"),
        "孫": H("子", "系"),
        "懸": V(H("県", "系"), "心"),
        "遜": H("⻌", "孫"),
        "却": H("去", "卩"),
        "脚": H("月", "却"),
        "卸": H(V("午", "止"), "卩"),
    },
    76: {
        "御": H("彳", "卸"),
        "服": H("月", V("卩", "又")),
        "命": V("𠆢", H("卩", "口")),
        "令": V("𠆢", "卩"),
        "零": V("雨", "令"),
        "齢": H("歯", "令"),
        "冷": H("冫", "令"),
        "領": H("令", "頁"),
        "鈴": H("金", "令"),
        "勇": V("甬", "力"),
        "湧": H("氵", "勇"),
        "通": H("⻌", "甬"),
        "踊": H("足", "甬"),
        "疑": "疑",
        "擬": H("扌", "疑"),
        "凝": H("冫", "疑"),
        "範": V("竹", H("車", "㔾")),
        "犯": H("犭", "㔾"),
        "氾": H("氵", "㔾"),
        "厄": V("厂", "㔾"),
    },
    77: {
        "危": V("⺈", "厄"),
        "宛": V("宀", V("夕", "㔾")),
        "腕": H("月", "宛"),
        "苑": V("艹", "宛"),
        "怨": V(V("夕", "㔾"), "心"),
        "柳": H("木", "卯"),
        "卵": "卵",
        "留": V("卯", "田"),
        "瑠": H("王", "留"),
        "貿": V("卯", "貝"),
        "印": "印",
        "臼": "臼",
        "毀": H(V("臼", "土"), "殳"),
        "興": "興",
        "酉": "酉",
        "酒": H("氵", "酉"),
        "酌": H("酉", "勺"),
        "酎": H("酉", "寸"),
        "酵": H("酉", "孝"),
        "酷": H("酉", "告"),
    },
    78: {
        "酬": H("酉", "州"),
        "酪": H("酉", "各"),
        "酢": H("酉", "乍"),
        "酔": H("酉", "卒"),
        "配": H("酉", "己"),
        "酸": H("酉", V("允", "夂")),
        "猶": H("犭", "酋"),
        "尊": V("酋", "寸"),
        "豆": "豆",
        "頭": H("豆", "頁"),
        "短": H("矢", "豆"),
        "豊": V("曲", "豆"),
        "鼓": H(V("十", "豆"), "支"),
        "喜": V(V("十", "豆"), "口"),
        "樹": H("木", H(V("十", "豆"), "寸")),
        "皿": "皿",
        "血": "血",
        "盆": V("分", "皿"),
        "盟": V("明", "皿"),
        "盗": V("次", "皿"),
    },
    79: {
        "温": H("氵", V("日", "皿")),
        "蓋": V("艹", V("去", "皿")),
        "監": V(H("臣", "丿"), "皿"),
        "濫": H("氵", "監"),
        "鑑": H("金", "監"),
        "藍": V("艹", "監"),
        "猛": H("犭", V("子", "皿")),
        "盛": V("成", "皿"),
        "塩": H("土", V("𠂉", "口", "皿")),
        "銀": H("金", "艮"),
        "恨": H("忄", "艮"),
        "根": H("木", "艮"),
        "即": H("艮", "卩"),
        "爵": "爵",
        "節": V("竹", "即"),
        "退": H("⻌", "艮"),
        "限": H("阝", "艮"),
        "眼": H("目", "艮"),
        "良": "良",
        "朗": H("良", "月"),
    },
    80: {
        "浪": H("氵", "良"),
        "娘": H("女", "良"),
        "食": "食",
        "飯": H("食", "反"),
        "飲": H("食", "欠"),
        "飢": H("食", "几"),
        "餓": H("食", "我"),
        "飾": H("食", V("𠂉", "巾")),
        "餌": H("食", "耳"),
        "館": H("食", "官"),
        "餅": H("食", V("丷", "开")),
        "養": V("羊", "食"),
        "飽": H("食", "包"),
        "既": H("艮", "旡"),
        "概": H("木", "既"),
        "慨": H("忄", "既"),
        "平": "平",
        "呼": H("口", "乎"),
        "坪": H("土", "平"),
        "評": H("言", "平"),
    },
}


def extract_component_box(section: str) -> tuple[int, int] | None:
    m = re.search(r'<div class="component-box\b[^>]*>', section)
    if not m:
        return None
    start = m.start()
    pos = start
    depth = 0
    while pos < len(section):
        open_at = section.find("<div", pos)
        close_at = section.find("</div>", pos)
        if close_at < 0:
            return None
        if open_at >= 0 and open_at < close_at:
            depth += 1
            pos = open_at + 4
        else:
            depth -= 1
            pos = close_at + 6
            if depth == 0:
                return start, pos
    return None


def replace_component_box(section: str, new_box: str) -> str:
    span = extract_component_box(section)
    if span:
        start, end = span
        rest = section[end:]
        m = re.match(r"(?:\s*</div>)*\s*(?=\n\n|\n</section>|$)", rest)
        if m:
            end = end + m.end()
        return section[:start] + new_box + "\n\n" + section[end:]
    orphan = re.search(
        r'<div class="kanji-right[\s\S]*?</div>\s*</div>\s*</div>',
        section,
    )
    if orphan:
        return section[: orphan.start()] + new_box + "\n\n" + section[orphan.end() :]
    style = list(re.finditer(r'<div class="style-row">[\s\S]*?</div>\s*</div>', section))
    if style:
        pos = style[-1].end()
        return section[:pos] + "\n\n  \n" + new_box + "\n\n\n" + section[pos:]
    end = section.find("</section>")
    return section[:end] + "\n" + new_box + "\n\n" + section[end:]


def strip_after_box(section: str) -> str:
    span = extract_component_box(section)
    if not span:
        return section
    start, end = span
    head = section[start:end]
    tail = section[end:]
    before = section[:start]
    if re.search(
        r"inner-kanji|outer-kanji|kanji-right|kanji-left|kanji-part-wrapper|"
        r"middle-section|bottom-section|top-section|enclosure-layout|kanji-composite",
        tail,
    ):
        return before + head + "\n\n\n"
    return section


def apply_lesson(n: int) -> list[str]:
    path = LESSONS / f"lesson_{n:02d}.html"
    text = path.read_text(encoding="utf-8")
    structs = STRUCTURES[n]
    changed: list[str] = []
    parts = re.split(r'(<section\s+class="kanji-entry")', text)
    out = [parts[0]]
    i = 1
    while i < len(parts):
        tag = parts[i]
        body = parts[i + 1]
        i += 2
        m = re.match(r"([^>]*>)([\s\S]*)", body)
        open_rest, rest = m.group(1), m.group(2)
        attrs = dict(re.findall(r'([^\s=]+)="([^"]*)"', open_rest))
        kanji = attrs.get("data-kanji", "")
        sec_end = rest.find("</section>")
        section, after = rest[:sec_end], rest[sec_end:]
        if kanji in structs:
            section = replace_component_box(section, box(structs[kanji]))
            section = strip_after_box(section)
            changed.append(kanji)
        out.extend([tag, open_rest + section + after])
    path.write_text("".join(out), encoding="utf-8")
    return changed


def update_catalog() -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    labels = data.setdefault("componentLabels", {})
    for g, lab in {
        "穴": "hole",
        "糸": "thread",
        "幺": "short thread",
        "玄": "mysterious",
        "系": "lineage",
        "兹": "double mysterious",
        "雍": "pop song",
        "令": "orders",
        "𠆢": "meeting",
        "卩": "stamp",
        "㔾": "fingerprint",
        "甬": "chop-seal",
        "疑": "doubt",
        "卯": "signs of the hare",
        "酉": "sign of the bird",
        "酋": "chieftain",
        "豆": "beans",
        "皿": "dish",
        "艮": "stopping",
        "良": "good",
        "食": "eat",
        "平": "flat",
        "乎": "question mark",
        "旡": "yawn",
        "甫": "dog tag",
        "ヰ": "toothbrush",
        "丘": "hill",
        "爵": "baron",
        "興": "entertain",
        "印": "stamp",
        "臼": "mortar",
        "卵": "egg",
        "血": "blood",
        "殳": "missile",
    }.items():
        labels.setdefault(g, lab)

    intros = data.setdefault("introductions", [])
    existing = {(int(i["lesson"]), i["glyph"]) for i in intros}
    for item in [
        {
            "lesson": 74,
            "beforeKanji": "幼",
            "glyph": "幺",
            "label": "short thread",
            "heisig": "short thread",
        },
        {
            "lesson": 79,
            "beforeKanji": "銀",
            "glyph": "艮",
            "label": "stopping",
            "heisig": "stopping",
        },
    ]:
        key = (item["lesson"], item["glyph"])
        if key not in existing:
            intros.append(item)
            existing.add(key)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated catalog")


def main() -> None:
    for n in range(71, 81):
        text = (LESSONS / f"lesson_{n:02d}.html").read_text(encoding="utf-8")
        kanji = re.findall(r'data-kanji="([^"]+)"', text)
        missing = [k for k in kanji if k not in STRUCTURES[n]]
        extra = [k for k in STRUCTURES[n] if k not in kanji]
        if missing or extra:
            raise SystemExit(f"L{n} coverage error missing={missing} extra={extra}")

    update_catalog()
    for n in range(71, 81):
        changed = apply_lesson(n)
        print(f"L{n}: {len(changed)} applied")


if __name__ == "__main__":
    main()
