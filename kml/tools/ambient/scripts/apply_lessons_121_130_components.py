#!/usr/bin/env python3
"""Apply Phase-1 component structures for lessons 121–130."""

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


# Shared nests
FENG = V("夂", "丰")  # 夆 / 逢 family
YAO = V("爪", "缶")  # 遥 / 揺 family
FU = V("一", "口", "田")  # 畐


STRUCTURES: dict[int, dict[str, object]] = {
    121: {
        "濠": H("氵", "豪"),
        "溌": H("氵", "発"),
        "湊": H("氵", "奏"),
        "淋": H("氵", "林"),
        "浩": H("氵", "告"),
        "汀": H("氵", "丁"),
        "鴻": H("氵", V("工", "鳥")),
        "潅": H("氵", V("艹", "隹")),
        "溢": H("氵", "益"),
        "湛": H("氵", "甚"),
        "淳": H("氵", "享"),
        "渥": H("氵", "屋"),
        "灘": H("氵", "難"),
        "汲": H("氵", "及"),
        "溜": H("氵", "留"),
        "渕": H("氵", "淵"),
        "沌": H("氵", "屯"),
        "濾": H("氵", "慮"),
        "濡": H("氵", "需"),
        "淀": H("氵", "延"),
    },
    122: {
        "涅": H("氵", V("日", "土")),
        "斧": H("父", "斤"),
        "爺": V("父", "耶"),
        "猾": H("犭", "骨"),
        "猥": H("犭", "畏"),
        "狡": H("犭", "交"),
        "狸": H("犭", "里"),
        "狼": H("犭", "良"),
        "狽": H("犭", "貝"),
        "狗": H("犭", "句"),
        "狐": H("犭", "瓜"),
        "狛": H("犭", "白"),
        "獅": H("犭", "師"),
        "狒": H("犭", "弗"),
        "莨": V("艹", "良"),
        "茉": V("艹", "末"),
        "莉": V("艹", "利"),
        "苺": V("艹", "母"),
        "萩": V("艹", "秋"),
        "藝": V("艹", H(V("土", "儿"), "丸"), "云"),
    },
    123: {
        "薙": V("艹", H("矢", "隹")),
        "蓑": V("艹", "衰"),
        "苔": V("艹", "台"),
        "蕩": V("艹", H("氵", "昜")),
        "蔓": V("艹", "曼"),
        "蓮": V("艹", "連"),
        "芙": V("艹", "夫"),
        "蓉": V("艹", "容"),
        "蘭": V("艹", V("門", "東")),
        "芦": V("艹", "戸"),
        "薯": V("艹", "署"),
        "菖": V("艹", "昌"),
        "蕉": V("艹", "焦"),
        "蕎": V("艹", V("夭", "高")),
        "蕗": V("艹", "路"),
        "茄": V("艹", "加"),
        "蔭": V("艹", "陰"),
        "蓬": V("艹", H("⻌", FENG)),
        "芥": V("艹", "介"),
        "萌": V("艹", "明"),
    },
    124: {
        "葡": V("艹", V("勹", "甫")),
        "萄": V("艹", V("勹", "缶")),
        "蘇": V("艹", H("魚", "禾")),
        "蕃": V("艹", "番"),
        "苓": V("艹", "令"),
        "菰": V("艹", "瓜"),
        "蒙": V("艹", "冡"),
        "茅": V("艹", "矛"),
        "芭": V("艹", "巴"),
        "苅": V("艹", H("乂", "刂")),
        "葱": V("艹", V("勿", "心")),
        "葵": V("艹", "癸"),
        "葺": V("艹", V("口", "耳")),
        "蕊": V("艹", V("心", "心", "心")),
        "茸": V("艹", "耳"),
        "蒔": V("艹", "時"),
        "芹": V("艹", "斤"),
        "苫": V("艹", "占"),
        "蒼": V("艹", "倉"),
        "藁": V("艹", H("木", "高")),
    },
    125: {
        "蕪": V("艹", "無"),
        "藷": V("艹", "諸"),
        "薮": V("艹", "数"),
        "蒜": V("艹", H("示", "示")),
        "蕨": V("艹", V("厂", "欮")),
        "蔚": V("艹", "尉"),
        "茜": V("艹", "西"),
        "莞": V("艹", "完"),
        "蒐": V("艹", "鬼"),
        "菅": V("艹", "官"),
        "葦": V("艹", "韋"),
        "迪": H("⻌", "由"),
        "辿": H("⻌", "才"),
        "這": H("⻌", "言"),
        "迂": H("⻌", "于"),
        "遁": H("⻌", "盾"),
        "逢": H("⻌", FENG),
        "遥": H("⻌", YAO),
        "遼": H("⻌", "尞"),
        "逼": H("⻌", FU),
    },
    126: {
        "迄": H("⻌", "乞"),
        "逗": H("⻌", "豆"),
        "鄭": H(V("丷", "酉", "大"), "⻏"),
        "隕": H("阝", "員"),
        "隈": H("阝", "畏"),
        "憑": V(H("冫", "馬"), "心"),
        "惹": V("若", "心"),
        "悉": V("釆", "心"),
        "忽": V("勿", "心"),
        "惣": V(H("牛", "勿"), "心"),
        "愈": V("俞", "心"),
        "恕": V("如", "心"),
        "昴": V("日", "卯"),
        "晋": V("亜", "日"),
        "晟": V("日", "成"),
        "暈": V("日", "軍"),
        "暉": H("日", "軍"),
        "旱": V("日", "干"),
        "晏": V("日", "安"),
        "晨": V("日", "辰"),
    },
    127: {
        "晒": H("日", "西"),
        "晃": V("日", "光"),
        "曝": H("日", "暴"),
        "曙": H("日", "署"),
        "昂": V("日", "卬"),
        "昏": V("氏", "日"),
        "晦": H("日", "毎"),
        "膿": H("月", "農"),
        "腑": H("月", "府"),
        "胱": H("月", "光"),
        "胚": H("月", "不"),
        "肛": H("月", "工"),
        "脆": H("月", "危"),
        "肋": H("月", "力"),
        "腔": H("月", "空"),
        "肱": H("月", V("𠂇", "厶")),
        "胡": H("古", "月"),
        "楓": H("木", "風"),
        "楊": H("木", "昜"),
        "椋": H("木", "京"),
    },
    128: {
        "榛": H("木", V("𡗗", "禾")),
        "櫛": H("木", "節"),
        "槌": H("木", "追"),
        "樵": H("木", "焦"),
        "梯": H("木", "弟"),
        "柑": H("木", "甘"),
        "杭": H("木", "亢"),
        "柊": H("木", "冬"),
        "柚": H("木", "由"),
        "椀": H("木", "宛"),
        "栂": H("木", "母"),
        "柾": H("木", "正"),
        "榊": H("木", "神"),
        "樫": H("木", "堅"),
        "槙": H("木", "真"),
        "楢": H("木", "酉"),
        "橘": H("木", V("矛", "冏")),
        "桧": H("木", "会"),
        "棲": H("木", "妻"),
        "栖": H("木", "西"),
    },
    129: {
        "桔": H("木", "吉"),
        "杜": H("木", "土"),
        "杷": H("木", "巴"),
        "梶": H("木", "尾"),
        "杵": H("木", "午"),
        "杖": H("木", "丈"),
        "樽": H("木", "尊"),
        "櫓": H("木", V("魚", "日")),
        "橿": H("木", V("一", "田", "一", "田")),
        "杓": H("木", "勺"),
        "李": V("木", "子"),
        "棉": H("木", V("白", "巾")),
        "楯": H("木", "盾"),
        "榎": H("木", "夏"),
        "樺": H("木", "華"),
        "槍": H("木", "倉"),
        "柘": H("木", "石"),
        "梱": H("木", "困"),
        "枇": H("木", "比"),
        "樋": H("木", "通"),
    },
    130: {
        "橇": H("木", V("毛", "毛", "毛")),
        "槃": V("般", "木"),
        "栞": V(H("干", "干"), "木"),
        "椰": H("木", H("耳", "⻏")),
        "檀": H("木", V("亠", "回", "旦")),
        "樗": H("木", "者"),
        "槻": H("木", "規"),
        "椙": H("木", "昌"),
        "彬": H("林", "彡"),
        "桶": H("木", "甬"),
        "楕": H("木", V("左", "月")),
        "樒": H("木", "密"),
        "毬": H("毛", "求"),
        "燿": H("火", V("羽", "隹")),
        "燎": H("火", "尞"),
        "炬": H("火", "巨"),
        "焚": V("林", "火"),
        "灸": V("久", "火"),
        "煽": H("火", "扇"),
        "煤": H("火", "某"),
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
        "淵": "abyss",
        "耶": "question",
        "弗": "dollar",
        "冡": "cover",
        "癸": "tenth",
        "数": "number",
        "厥": "impotent",
        "欮": "gasp",
        "于": "potato",
        "乞": "beg",
        "馮": "depend",
        "冏": "light rays",
        "勺": "ladle",
        "丈": "length",
        "尾": "tail",
        "魚": "fish",
        "時": "time",
        "占": "fortune-telling",
        "衰": "decline",
        "台": "pedestal",
        "曼": "mandala",
        "才": "genius",
        "韦": "tanned leather",
        "韋": "tanned leather",
        "甫": "dog tag",
        "禾": "wheat",
        "云": "say",
        "亚": "Asia",
        "亜": "Asia",
        "不": "negative",
        "工": "craft",
        "力": "power",
        "风": "wind",
        "風": "wind",
        "𡗗": "bonsai",
        "甬": "chop-seal",
        "求": "request",
        "巨": "gigantic",
        "久": "long time",
        "扇": "fan",
        "某": "so-and-so",
        "規": "standard",
        "密": "secrecy",
        "左": "left",
        "干": "dry",
        "毛": "fur",
        "般": "carrier",
        "耳": "ear",
        "回": "yonder",
        "旦": "nightbreak",
        "者": "someone",
        "昌": "prosperous",
        "彡": "bristle",
        "林": "grove",
        "火": "fire",
        "羽": "feather",
        "隹": "turkey",
        "尞": "companion",
    }.items():
        labels.setdefault(g, lab)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated catalog labels (no new intros)")


def main() -> None:
    for n in range(121, 131):
        text = (LESSONS / f"lesson_{n:02d}.html").read_text(encoding="utf-8")
        kanji = re.findall(r'data-kanji="([^"]+)"', text)
        missing = [k for k in kanji if k not in STRUCTURES[n]]
        extra = [k for k in STRUCTURES[n] if k not in kanji]
        if missing or extra:
            raise SystemExit(f"L{n} coverage error missing={missing} extra={extra}")

    update_catalog()
    for n in range(121, 131):
        changed = apply_lesson(n)
        print(f"L{n}: {len(changed)} applied")


if __name__ == "__main__":
    main()
