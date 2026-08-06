#!/usr/bin/env python3
"""Apply Phase-1 component structures for lessons 131–140."""

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


FENG = V("夂", "丰")
FU = V("一", "口", "田")
PI = H("尸", "辛")
ZUI = H("又", "又", "又")


STRUCTURES: dict[int, dict[str, object]] = {
    131: {
        "煉": H("火", "東"),
        "燦": H("火", V("歹", "又", "米")),
        "灼": H("火", "勺"),
        "烙": H("火", "各"),
        "焔": H("火", V("⺈", "臼")),
        "烹": V("亨", "灬"),
        "牽": V("玄", H("冖", "牛")),
        "牝": H("牛", "匕"),
        "牡": H("牛", "土"),
        "琳": H("王", "林"),
        "琉": H("王", V("亠", "ム", "川")),
        "瑳": H("王", "差"),
        "琢": H("王", "豕"),
        "珊": H("王", "冊"),
        "瑚": H("王", "胡"),
        "瑞": H("王", V("山", "而")),
        "玖": H("王", "久"),
        "瑛": H("王", "英"),
        "玲": H("王", "令"),
        "畢": "畢",
    },
    132: {
        "畦": H("田", "圭"),
        "痒": V("疒", "羊"),
        "痰": V("疒", "炎"),
        "疹": V("疒", V("人", "彡")),
        "痔": V("疒", "寺"),
        "癌": V("疒", V("品", "山")),
        "痺": V("疒", "卑"),
        "眸": H("目", "牟"),
        "眩": H("目", "玄"),
        "雉": H("矢", "隹"),
        "矩": H("矢", "巨"),
        "磐": V("般", "石"),
        "碇": H("石", "定"),
        "碧": H(V("王", "白"), "石"),
        "硯": H("石", "見"),
        "砥": H("石", "氏"),
        "碗": H("石", "宛"),
        "碍": H("石", "疑"),
        "碩": H("石", "頁"),
        "磯": H("石", "幾"),
    },
    133: {
        "砺": H("石", "万"),
        "碓": H("石", "隹"),
        "禦": V("御", "示"),
        "祷": H("礻", "寿"),
        "祐": H("礻", "右"),
        "祇": H("礻", "氏"),
        "祢": H("礻", V("𠂉", "小")),
        "禄": H("礻", V("ヨ", "水")),
        "禎": H("礻", "貞"),
        "秤": H("禾", "平"),
        "黍": "黍",
        "禿": V("禾", "儿"),
        "稔": H("禾", "念"),
        "稗": H("禾", "卑"),
        "穣": H("禾", "襄"),
        "稜": H("禾", V("土", "夂")),
        "稀": H("禾", "希"),
        "穆": H("禾", V("白", "小", "彡")),
        "窺": V("穴", "規"),
        "窄": V("穴", "乍"),
    },
    134: {
        "穿": V("穴", "牙"),
        "竃": V("穴", "土", "亀"),
        "竪": V(H("臣", "又"), "立"),
        "颯": H("立", "風"),
        "站": H("立", "占"),
        "靖": H("立", "青"),
        "妾": V("立", "女"),
        "衿": H("衤", "今"),
        "袷": H("衤", "合"),
        "袴": H("衤", V("大", "丂")),
        "襖": H("衤", "奥"),
        "笙": V("竹", "生"),
        "筏": V("竹", "伐"),
        "簾": V("竹", "廉"),
        "箪": V("竹", "単"),
        "竿": V("竹", "干"),
        "箆": V("竹", V("尸", "比")),
        "箔": V("竹", H("氵", "白")),
        "笥": V("竹", "司"),
        "箭": V("竹", "前"),
    },
    135: {
        "筑": V("竹", H("工", "凡")),
        "篠": V("竹", H(H("亻", "丨", "攵"), "木")),
        "纂": V("竹", V("目", "大"), "糸"),
        "竺": V("竹", "二"),
        "箕": V("竹", "其"),
        "笈": V("竹", "及"),
        "篇": V("竹", "扁"),
        "筈": V("竹", "害"),
        "簸": V("竹", H("其", "皮")),
        "粕": H("米", "白"),
        "糟": H("米", "曹"),
        "糊": H("米", "胡"),
        "籾": H("米", "刀"),
        "糠": H("米", "康"),
        "糞": V("米", "異"),
        "粟": V("西", "米"),
        "繋": V(H("車", "殳"), "糸"),
        "綸": H("糸", "侖"),
        "絨": H("糸", H("戈", "𠂇")),
        "絆": H("糸", "半"),
    },
    136: {
        "緋": H("糸", "非"),
        "綜": H("糸", "宗"),
        "紐": H("糸", "丑"),
        "紘": H("糸", V("𠂇", "厶")),
        "纏": H("糸", V("广", "里", "土")),
        "絢": H("糸", "旬"),
        "繍": H("糸", "粛"),
        "紬": H("糸", "由"),
        "綺": H("糸", "奇"),
        "綾": H("糸", V("土", "夂")),
        "絃": H("糸", "玄"),
        "縞": H("糸", "高"),
        "綬": H("糸", "受"),
        "紗": H("糸", "少"),
        "舵": H("舟", V("宀", "匕")),
        "聯": H("耳", H("幺", "幺")),
        "聡": H("耳", V("公", "心")),
        "聘": H("耳", V("由", "丂")),
        "耽": H("耳", "冘"),
        "耶": H("耳", "⻏"),
    },
    137: {
        "蚤": V("又", "虫"),
        "蟹": H("解", "虫"),
        "蛋": V("疋", "虫"),
        "蟄": V("執", "虫"),
        "蝿": H("虫", V("口", "电")),
        "蟻": H("虫", "義"),
        "蝋": H("虫", "昔"),
        "蝦": H("虫", "叚"),
        "蛸": H("虫", "肖"),
        "螺": H("虫", "累"),
        "蝉": H("虫", "単"),
        "蛙": H("虫", "圭"),
        "蛾": H("虫", "我"),
        "蛤": H("虫", "合"),
        "蛭": H("虫", "至"),
        "蛎": H("虫", "万"),
        "罫": H(V("罒", "圭"), "刂"),
        "袈": V("加", "衣"),
        "裟": V("沙", "衣"),
        "截": H(V("十", "隹"), "戈"),
    },
    138: {
        "哉": H(V("十", "戈"), "口"),
        "詢": H("言", "旬"),
        "諄": H("言", "享"),
        "讐": V(H("隹", "隹"), "言"),
        "諌": H("言", "東"),
        "諒": H("言", "京"),
        "讃": H("言", V(H("先", "先"), "貝")),
        "訊": H("言", V("十", "乚")),
        "訣": H("言", "夬"),
        "詫": H("言", "宅"),
        "誼": H("言", "宜"),
        "謬": H("言", V("羽", V("人", "彡"))),
        "訝": H("言", "牙"),
        "諺": H("言", "彦"),
        "誹": H("言", "非"),
        "謂": H("言", "胃"),
        "諜": H("言", V("世", "木")),
        "註": H("言", "主"),
        "譬": H("言", PI),
        "轟": V("車", "車", "車"),
    },
    139: {
        "輔": H("車", "甫"),
        "輻": H("車", FU),
        "輯": H("車", V("口", "耳")),
        "豹": H("豸", "勺"),
        "賎": H("貝", H("戈", "戈")),
        "貰": V("世", "貝"),
        "賑": H("貝", "辰"),
        "贖": H("貝", "売"),
        "躓": H("足", "質"),
        "蹄": H("足", "帝"),
        "蹟": H("足", "責"),
        "跨": H("足", V("大", "丂")),
        "跪": H("足", "危"),
        "醤": V("将", "酉"),
        "醍": H("酉", "是"),
        "醐": H("酉", "胡"),
        "醇": H("酉", "享"),
        "麹": H("麦", V("勹", "米")),
        "釦": H("金", "口"),
        "銚": H("金", "兆"),
    },
    140: {
        "鋤": H("金", "助"),
        "鋸": H("金", "居"),
        "錐": H("金", "隹"),
        "鍬": H("金", "秋"),
        "鋲": H("金", "兵"),
        "錫": H("金", "易"),
        "錨": H("金", V("艹", "田")),
        "釘": H("金", "丁"),
        "鑓": H("金", "遣"),
        "鋒": H("金", FENG),
        "鎚": H("金", "追"),
        "鉦": H("金", "正"),
        "錆": H("金", "青"),
        "鍾": H("金", "重"),
        "鋏": H("金", V("大", H("人", "人"))),
        "閃": V("門", "人"),
        "悶": V("門", "心"),
        "閤": V("門", "合"),
        "雫": V("雨", "下"),
        "霞": V("雨", "叚"),
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
        "畢": "lastly",
        "亨": "perfect",
        "它": "other",
        "夸": "boast",
        "戎": "warrior",
        "电": "electric",
        "昔": "once upon a time",
        "牟": "moo",
        "貞": "upright",
        "黍": "millet",
        "襄": "porter",
        "希": "hope",
        "奥": "core",
        "廉": "bargain",
        "扁": "door-flat",
        "康": "ease",
        "異": "uncommon",
        "侖": "scrapbook",
        "粛": "solemn",
        "少": "few",
        "丱": "braids",
        "黽": "toad",
        "鼠": "rat",
        "累": "accumulate",
        "万": "ten thousand",
        "沙": "gravel",
        "賛": "approve",
        "先": "before",
        "胃": "stomach",
        "世": "generation",
        "主": "lord",
        "甫": "dog tag",
        "質": "substance",
        "帝": "sovereign",
        "将": "leader",
        "是": "just so",
        "兆": "portent",
        "助": "help",
        "居": "reside",
        "兵": "soldier",
        "易": "easy",
        "遣": "dispatch",
        "正": "correct",
        "重": "heavy",
        "下": "below",
        "叚": "borrow",
        "差": "distinction",
        "胡": "barbarian",
        "炎": "inflammation",
        "品": "goods",
        "疑": "doubt",
        "幾": "how many",
        "寿": "longevity",
        "右": "right",
        "御": "honorable",
        "規": "standard",
        "乍": "saw",
        "亀": "turtle",
        "占": "fortune-telling",
        "今": "now",
        "合": "fit",
        "生": "life",
        "伐": "fell",
        "単": "simple",
        "干": "dry",
        "司": "director",
        "前": "in front",
        "其": "that",
        "及": "reach",
        "害": "harm",
        "皮": "skin",
        "白": "white",
        "曹": "cadet",
        "麦": "wheat",
        "半": "half",
        "非": "un-",
        "宗": "religion",
        "丑": "sign of the cow",
        "旬": "decameron",
        "由": "wherefore",
        "奇": "strange",
        "玄": "mysterious",
        "高": "tall",
        "冘": "float",
        "解": "unravel",
        "執": "tenacious",
        "食": "eat",
        "肖": "resemble",
        "圭": "squared jewel",
        "我": "ego",
        "至": "climax",
        "加": "add",
        "衣": "garment",
        "享": "receive",
        "京": "capital",
        "宅": "home",
        "宜": "best regards",
        "牙": "tusk",
        "彦": "lad",
        "辰": "sign of the dragon",
        "売": "sell",
        "責": "blame",
        "危": "dangerous",
        "秋": "autumn",
        "丁": "street",
        "追": "chase",
        "青": "blue",
        "心": "heart",
        "雨": "rain",
        "門": "gates",
        "人": "person",
    }.items():
        labels.setdefault(g, lab)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated catalog labels (no new intros)")


def main() -> None:
    for n in range(131, 141):
        text = (LESSONS / f"lesson_{n:02d}.html").read_text(encoding="utf-8")
        kanji = re.findall(r'data-kanji="([^"]+)"', text)
        missing = [k for k in kanji if k not in STRUCTURES[n]]
        extra = [k for k in STRUCTURES[n] if k not in kanji]
        if missing or extra:
            raise SystemExit(f"L{n} coverage error missing={missing} extra={extra}")

    update_catalog()
    for n in range(131, 141):
        changed = apply_lesson(n)
        print(f"L{n}: {len(changed)} applied")


if __name__ == "__main__":
    main()
