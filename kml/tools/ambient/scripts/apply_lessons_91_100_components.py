#!/usr/bin/env python3
"""Apply Phase-1 component structures for lessons 91–100."""

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


# Labeled / nested clusters (not new catalog unless listed in intros)
AWNING_PEOPLE = V(H("人", "人"), "一", "人")  # ≈ 㑒 in 剣検険倹
PI = H("尸", "辛")


STRUCTURES: dict[int, dict[str, object]] = {
    91: {
        "整": V("敕", "正"),  # or H("束","攵") + 正
        "剣": H(AWNING_PEOPLE, "刂"),
        "険": H("阝", AWNING_PEOPLE),
        "検": H("木", AWNING_PEOPLE),
        "倹": H("亻", AWNING_PEOPLE),
        "重": "重",
        "動": H("重", "力"),
        "腫": H("月", "重"),
        "勲": V("動", "灬"),
        "働": H("亻", "動"),
        "種": H("禾", "重"),
        "衝": H("行", "重"),
        "薫": V("艹", V("重", "灬")),
        "病": V("疒", "丙"),
        "痴": V("疒", "知"),
        "痘": V("疒", "豆"),
        "症": V("疒", "正"),
        "瘍": V("疒", "昜"),
        "痩": V("疒", V("米", "女")),
        "疾": V("疒", "矢"),
    },
    92: {
        "嫉": H("女", "疾"),
        "痢": V("疒", "利"),
        "痕": V("疒", "艮"),
        "疲": V("疒", "皮"),
        "疫": V("疒", "殳"),
        "痛": V("疒", "甬"),
        "癖": V("疒", PI),
        "匿": V("匸", "若"),
        "匠": V("匚", "斤"),
        "医": V("匚", "矢"),
        "匹": V("匚", "儿"),
        "区": V("匚", "㐅"),
        "枢": H("木", "区"),
        "殴": H("区", "殳"),
        "欧": H("区", "欠"),
        "抑": H("扌", "卬"),
        "仰": H("亻", "卬"),
        "迎": H("⻌", "卬"),
        "登": V("癶", "豆"),
        "澄": H("氵", "登"),
    },
    93: {
        "発": V("癶", V("二", "儿")),
        "廃": V("广", "発"),
        "僚": H("亻", "尞"),
        "瞭": H("目", "尞"),
        "寮": V("宀", "尞"),
        "療": V("疒", "尞"),
        "彫": H("周", "彡"),
        "形": H("开", "彡"),
        "影": H("景", "彡"),
        "杉": H("木", "彡"),
        "彩": H("采", "彡"),
        "彰": H("章", "彡"),
        "彦": V(H("立", "厂"), "彡"),
        "顔": H("彦", "頁"),
        "須": H("彡", "頁"),
        "膨": H("月", H(V("十", "豆"), "彡")),
        "参": V("ム", "大", "彡"),
        "惨": H("忄", "参"),
        "修": H("亻", "丨", "攵", "彡"),
        "珍": H("王", V("人", "彡")),
    },
    94: {
        "診": H("言", V("人", "彡")),
        "文": "文",
        "対": "対",
        "紋": H("糸", "文"),
        "蚊": H("虫", "文"),
        "斑": H("王", "文", "王"),
        "斉": "斉",
        "剤": H("斉", "刂"),
        "済": H("氵", "斉"),
        "斎": V("斉", "小"),
        "粛": "粛",
        "塁": V("田", "八", "土"),
        "楽": V("⺍", "白", "木"),
        "薬": V("艹", "楽"),
        "率": "率",
        "渋": H("氵", V("止", "止", "止")),
        "摂": H("扌", V("耳", H("丷", "丷"))),
        "央": "央",
        "英": V("艹", "央"),
        "映": H("日", "央"),
    },
    95: {
        "赤": "赤",
        "赦": H("赤", "夂"),
        "変": V("亦", "夂"),
        "跡": H("足", "亦"),
        "蛮": V("亦", "虫"),
        "恋": V("亦", "心"),
        "湾": H("氵", V("亦", "弓")),
        "黄": "黄",
        "横": H("木", "黄"),
        "把": H("扌", "巴"),
        "色": "色",
        "絶": H("糸", "色"),
        "艶": H("豊", "色"),
        "肥": H("月", "巴"),
        "甘": "甘",
        "紺": H("糸", "甘"),
        "某": V("甘", "木"),
        "謀": H("言", "某"),
        "媒": H("女", "某"),
        "欺": H("其", "欠"),
    },
    96: {
        "棋": H("木", "其"),
        "旗": H("方", "其"),
        "期": H("其", "月"),
        "碁": V("其", "石"),
        "基": V("其", "土"),
        "甚": V("其", "匹"),
        "勘": H("甚", "力"),
        "堪": H("土", "甚"),
        "貴": "貴",
        "遺": H("⻌", "貴"),
        "遣": H("⻌", V("中", "一", "㔾")),
        "潰": H("氵", "貴"),
        "舞": "舞",
        "無": "無",
        "組": H("糸", "且"),
        "粗": H("米", "且"),
        "租": H("禾", "且"),
        "狙": H("犭", "且"),
        "祖": H("礻", "且"),
        "阻": H("阝", "且"),
    },
    97: {
        "査": V("木", "且"),
        "助": H("且", "力"),
        "宜": V("宀", "且"),
        "畳": V("田", V("冖", "且")),
        "並": "並",
        "普": V("並", "日"),
        "譜": H("言", "普"),
        "湿": H("氵", V("日", "业")),
        "顕": H(V("日", "业"), "頁"),
        "繊": H("糸", V("业", "㐱")),
        "霊": V("雨", V("一", "二", "口", "口", "口")),
        "業": "業",
        "撲": H("扌", "菐"),
        "僕": H("亻", "菐"),
        "共": "共",
        "供": H("亻", "共"),
        "異": "異",
        "翼": V("羽", "異"),
        "戴": H("異", "戈"),
        "洪": H("氵", "共"),
    },
    98: {
        "港": H("氵", V("共", "己")),
        "暴": V("日", "共", "水"),
        "爆": H("火", "暴"),
        "恭": V("共", "心"),
        "選": H("⻌", "巽"),
        "殿": H(V("尸", "共"), "殳"),
        "井": "井",
        "丼": V("井", "丶"),
        "囲": V("囗", "井"),
        "耕": H("耒", "井"),
        "亜": "亜",
        "悪": V("亜", "心"),
        "円": "円",
        "角": "角",
        "触": H("角", "虫"),
        "解": H("角", V("刀", "牛")),
        "再": "再",
        "講": H("言", "冓"),
        "購": H("貝", "冓"),
        "構": H("木", "冓"),
    },
    99: {
        "溝": H("氵", "冓"),
        "論": H("言", "侖"),
        "倫": H("亻", "侖"),
        "輪": H("車", "侖"),
        "偏": H("亻", "扁"),
        "遍": H("⻌", "扁"),
        "編": H("糸", "扁"),
        "冊": "冊",
        "柵": H("木", "冊"),
        "典": "典",
        "氏": "氏",
        "紙": H("糸", "氏"),
        "婚": H("女", V("氏", "日")),
        "低": H("亻", "氐"),
        "抵": H("扌", "氐"),
        "底": V("广", "氐"),
        "民": "民",
        "眠": H("目", "民"),
        "捕": H("扌", "甫"),
        "哺": H("口", "甫"),
    },
    100: {
        "浦": H("氵", "甫"),
        "蒲": V("艹", "浦"),
        "舗": H("舎", "甫"),
        "補": H("衤", "甫"),
        "邸": H("氐", "⻏"),
        "郭": H("享", "⻏"),
        "郡": H("君", "⻏"),
        "郊": H("交", "⻏"),
        "部": H("咅", "⻏"),
        "都": H("者", "⻏"),
        "郵": H("垂", "⻏"),
        "邦": H("丰", "⻏"),
        "那": H("二", "⻏"),
        "郷": "郷",
        "響": V("郷", "音"),
        "郎": H("良", "⻏"),
        "廊": V("广", "郎"),
        "盾": "盾",
        "循": H("彳", "盾"),
        "派": H("氵", "𠂢"),
    },
}

# Fix 整: 敕 may be unfamiliar — use 束+攵+正
STRUCTURES[91]["整"] = V(H("束", "攵"), "正")

# 顕 appears in both 94 and 97 in lesson lists — keep same structure
# (L94 list included 顕; L97 also has 顕 — verify coverage)

# 繊: 㐱 = person+bristles
STRUCTURES[97]["繊"] = H("糸", V("业", V("人", "彡")))


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
        "重": "heavy",
        "疒": "sickness",
        "匚": "box",
        "匸": "hiding enclosure",
        "卬": "exalted",
        "癶": "tent",
        "尞": "companion",
        "彡": "bristle",
        "文": "sentence",
        "斉": "adjusted",
        "楽": "music",
        "央": "center",
        "赤": "red",
        "亦": "dancing legs",
        "黄": "yellow",
        "色": "color",
        "巴": "comma-shaped",
        "甘": "sweet",
        "其": "that",
        "貴": "precious",
        "無": "nothing",
        "且": "alongside",
        "並": "row",
        "業": "profession",
        "共": "together",
        "異": "uncommon",
        "井": "well",
        "亜": "Asia",
        "円": "circle",
        "角": "angle",
        "再": "again",
        "冓": "funnel",
        "侖": "scrapbook",
        "扁": "door-flat",
        "冊": "tome",
        "典": "code",
        "氏": "family name",
        "氐": "foundation",
        "民": "people",
        "甫": "dog tag",
        "⻏": "city walls",
        "郷": "hometown",
        "盾": "shield",
        "菐": "bushes under",
        "巽": "obedience",
        "享": "receive",
        "舎": "cottage",
        "𠂢": "water's edge",
        "业": "business",
        "若": "young",
        "采": "dice",
        "景": "scenery",
        "周": "circumference",
        "利": "profit",
        "皮": "skin",
        "知": "know",
        "丙": "third",
    }.items():
        labels.setdefault(g, lab)

    intros = data.setdefault("introductions", [])
    existing = {(int(i["lesson"]), i["glyph"]) for i in intros}
    for item in [
        {
            "lesson": 91,
            "beforeKanji": "病",
            "glyph": "疒",
            "label": "sickness",
            "heisig": "sickness",
        },
        {
            "lesson": 93,
            "beforeKanji": "彫",
            "glyph": "彡",
            "label": "bristle",
            "heisig": "bristle",
        },
        {
            "lesson": 95,
            "beforeKanji": "変",
            "glyph": "亦",
            "label": "dancing legs",
            "heisig": "dancing legs",
        },
        {
            "lesson": 96,
            "beforeKanji": "棋",
            "glyph": "其",
            "label": "that",
            "heisig": "that",
        },
        {
            "lesson": 96,
            "beforeKanji": "組",
            "glyph": "且",
            "label": "alongside",
            "heisig": "alongside",
        },
        {
            "lesson": 100,
            "beforeKanji": "邸",
            "glyph": "⻏",
            "label": "city walls",
            "heisig": "city walls",
        },
    ]:
        key = (item["lesson"], item["glyph"])
        if key not in existing:
            intros.append(item)
            existing.add(key)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated catalog")


def main() -> None:
    for n in range(91, 101):
        text = (LESSONS / f"lesson_{n:02d}.html").read_text(encoding="utf-8")
        kanji = re.findall(r'data-kanji="([^"]+)"', text)
        missing = [k for k in kanji if k not in STRUCTURES[n]]
        extra = [k for k in STRUCTURES[n] if k not in kanji]
        if missing or extra:
            raise SystemExit(f"L{n} coverage error missing={missing} extra={extra}")

    update_catalog()
    for n in range(91, 101):
        changed = apply_lesson(n)
        print(f"L{n}: {len(changed)} applied")


if __name__ == "__main__":
    main()
