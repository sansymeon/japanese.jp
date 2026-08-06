#!/usr/bin/env python3
"""Apply Phase-1 component structures for lessons 111–120."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LESSONS = ROOT / "contents" / "books" / "book_01" / "lessons"
CATALOG = ROOT / "tools" / "ambient" / "data" / "kanji_components_catalog.json"

ROLL = None  # set after H/V


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


ROLL = V("丷", "夫")
JUN = V("允", "夂")  # 夋 family
RIN = V("米", "舛")  # 粦 cluster
ZUI = H("又", "又", "又")  # 叕


STRUCTURES: dict[int, dict[str, object]] = {
    111: {
        "巳": "巳",
        "此": H("止", "匕"),
        "柴": H("木", "此"),
        "些": H("此", "二"),
        "砦": V("此", "石"),
        "髭": H("髟", "此"),
        "禽": V("人", "离"),
        "檎": H("木", "禽"),
        "憐": H("忄", RIN),
        "燐": H("火", RIN),
        "麟": H("鹿", RIN),
        "鱗": H("魚", RIN),
        "奄": "奄",
        "庵": V("广", "奄"),
        "掩": H("扌", "奄"),
        "悛": H("忄", JUN),
        "駿": H("馬", JUN),
        "峻": H("山", JUN),
        "竣": H("立", JUN),
        "犀": "犀",
    },
    112: {
        "皐": V("白", "大", "十"),
        "畷": H("田", ZUI),
        "綴": H("糸", ZUI),
        "鎧": H("金", "豈"),
        "凱": H("豈", "几"),
        "呑": V("天", "口"),
        "韮": V("艹", "韭"),
        "籤": V("竹", "韱"),
        "懺": H("忄", "韱"),
        "芻": "芻",
        "雛": H("芻", "隹"),
        "趨": H("走", "芻"),
        "尤": "尤",
        "厖": V("厂", H("尤", "彡")),
        "或": H("戈", V("口", "一")),
        "兎": "兎",
        "也": "也",
        "巴": "巴",
        "疋": "疋",
        "菫": V("艹", "堇"),
    },
    113: {
        "曼": "曼",
        "云": "云",
        "莫": V("艹", "日", "大"),
        "而": "而",
        "倭": H("亻", "委"),
        "侠": H("亻", V("大", H("人", "人"))),
        "倦": H("亻", V(ROLL, "㔾")),
        "俄": H("亻", "我"),
        "佃": H("亻", "田"),
        "仔": H("亻", "子"),
        "仇": H("亻", "九"),
        "伽": H("亻", "加"),
        "儲": H("亻", "諸"),
        "僑": H("亻", V("夭", "高")),
        "倶": H("亻", "具"),
        "侃": H("亻", "川"),
        "偲": H("亻", "思"),
        "侭": H("亻", "尽"),
        "脩": H(H("亻", "丨", "攵"), "月"),
        "倅": H("亻", "卒"),
    },
    114: {
        "做": H("亻", "故"),
        "冴": H("冫", "牙"),
        "凋": H("冫", "周"),
        "凌": H("冫", V("土", "夂")),
        "凛": H("冫", V("亠", "回", "禾")),
        "凧": H("几", "巾"),
        "凪": V("几", "止"),
        "夙": V("夕", "凡"),
        "鳳": V("几", "鳥"),
        "剽": H("票", "刂"),
        "劉": H(V("卯", "金"), "刂"),
        "剃": H("弟", "刂"),
        "厭": V("厂", H(V("日", "月"), "犬")),
        "雁": V("厂", H("亻", "隹")),
        "贋": H("雁", "貝"),
        "厨": V("厂", H(V("十", "豆"), "寸")),
        "仄": V("厂", "人"),
        "哨": H("口", "肖"),
        "咎": H(V("夂", "人"), "口"),
        "囁": H("口", V("耳", "耳", "耳")),
    },
    115: {
        "喋": H("口", "葉"),
        "嘩": H("口", "華"),
        "噂": H("口", "尊"),
        "咳": H("口", "亥"),
        "喧": H("口", "宣"),
        "叩": H("口", "卩"),
        "嘘": H("口", "虚"),
        "啄": H("口", "豕"),
        "吠": H("口", "犬"),
        "吊": H("口", "巾"),
        "噛": H("口", "齒"),
        "叶": H("口", "十"),
        "吻": H("口", "勿"),
        "吃": H("口", "乞"),
        "噺": H("口", "新"),
        "噌": H("口", "曾"),
        "邑": "邑",
        "呆": V("口", "木"),
        "喰": H("口", "食"),
        "埴": H("土", "直"),
    },
    116: {
        "坤": H("土", "申"),
        "壕": H("土", "豪"),
        "垢": H("土", "后"),
        "坦": H("土", "旦"),
        "埠": H("土", "阜"),
        "堰": H("土", "匽"),
        "堵": H("土", "者"),
        "嬰": V(H("貝", "貝"), "女"),
        "姦": V("女", "女", "女"),
        "婢": H("女", "卑"),
        "婉": H("女", "宛"),
        "娼": H("女", "昌"),
        "妓": H("女", "支"),
        "娃": H("女", "圭"),
        "姪": H("女", "至"),
        "嬬": H("女", "需"),
        "姥": H("女", "老"),
        "姑": H("女", "古"),
        "姐": H("女", "且"),
        "嬉": H("女", "喜"),
    },
    117: {
        "孕": V("乃", "子"),
        "孜": H("子", "攵"),
        "宥": V("宀", "有"),
        "寓": V("宀", "禺"),
        "宏": V("宀", V("𠂇", "厶")),
        "牢": V("宀", "牛"),
        "宋": V("宀", "木"),
        "宍": V("宀", "肉"),
        "屠": H("尸", "者"),
        "屁": V("尸", "比"),
        "屑": V("尸", "肖"),
        "屡": V("尸", V("米", "女")),
        "屍": V("尸", "死"),
        "屏": V("尸", V("丷", "开")),
        "嵩": V("山", "高"),
        "崚": H("山", V("土", "夂")),
        "嶺": H("山", "領"),
        "嵌": H("山", V("甘", "欠")),
        "帖": H("巾", "占"),
        "幡": H("巾", "番"),
    },
    118: {
        "幟": H("巾", V("音", "戈")),
        "庖": V("广", "包"),
        "廓": V("广", "郭"),
        "庇": V("广", "比"),
        "鷹": V("广", H("亻", "隹"), "鳥"),
        "庄": V("广", "土"),
        "廟": V("广", "朝"),
        "彊": H("弓", V("一", "田", "一", "田")),
        "弛": H("弓", "也"),
        "粥": H("弓", "米", "弓"),
        "挽": H("扌", "免"),
        "撞": H("扌", "童"),
        "扮": H("扌", "分"),
        "捏": H("扌", V("日", "土")),
        "掴": H("扌", "国"),
        "捺": H("扌", "奈"),
        "掻": H("扌", V("又", "虫")),
        "撰": H("扌", "巽"),
        "揃": H("扌", "前"),
        "捌": H("扌", "別"),
    },
    119: {
        "按": H("扌", "安"),
        "播": H("扌", "番"),
        "揖": H("扌", V("口", "耳")),
        "托": H("扌", "乇"),
        "捧": H("扌", "奉"),
        "撚": H("扌", "然"),
        "挺": H("扌", "廷"),
        "擾": H("扌", "憂"),
        "撫": H("扌", "無"),
        "撒": H("扌", "散"),
        "擢": H("扌", V("羽", "隹")),
        "摺": H("扌", "習"),
        "捷": H("扌", "疌"),
        "抉": H("扌", "夬"),
        "怯": H("忄", "去"),
        "惟": H("忄", "隹"),
        "惚": H("忄", "忽"),
        "怜": H("忄", "令"),
        "惇": H("忄", "享"),
        "恰": H("忄", "合"),
    },
    120: {
        "恢": H("忄", "灰"),
        "悌": H("忄", "弟"),
        "澪": H("氵", "零"),
        "洸": H("氵", "光"),
        "滉": H("氵", "晃"),
        "漱": H("氵", H("束", "欠")),
        "洲": H("氵", "州"),
        "洵": H("氵", "旬"),
        "滲": H("氵", "参"),
        "洒": H("氵", "西"),
        "沐": H("氵", "木"),
        "泪": H("氵", "目"),
        "渾": H("氵", "軍"),
        "涜": H("氵", "売"),
        "梁": V(H("氵", "刀"), "木"),
        "澱": H("氵", "殿"),
        "洛": H("氵", "各"),
        "汝": H("氵", "女"),
        "漉": H("氵", "鹿"),
        "瀕": H("氵", "頻"),
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
        "巳": "sign of the snake",
        "此": "this",
        "禽": "fowl",
        "奄": "hitherto",
        "犀": "rhinoceros",
        "芻": "hay",
        "尤": "furthermore",
        "或": "or",
        "兎": "rabbit",
        "也": "scorpion",
        "巴": "comma-shaped",
        "疋": "critters",
        "曼": "mandala",
        "云": "say",
        "莫": "must not",
        "而": "rake",
        "邑": "village",
        "豈": "tasty",
        "韭": "leek",
        "韱": "wild onion",
        "曾": "formerly",
        "匽": "conceal",
        "疌": "swift",
        "夬": "guillotine",
        "忽": "in a flash",
        "乞": "beg",
        "齒": "tooth",
        "肖": "resemble",
        "占": "fortune-telling",
        "朝": "morning",
        "乃": "from",
        "频": "frequently",
        "頻": "frequently",
        "晃": "clear",
        "旬": "decameron",
        "灰": "ashes",
        "魚": "fish",
        "离": "birdhouse",
        "凡": "mediocre",
        "回": "yonder",
        "葉": "leaf",
        "華": "splendor",
        "宣": "proclaim",
        "虚": "void",
        "新": "new",
        "豪": "overpowering",
        "后": "empress",
        "阜": "pinnacle",
        "昌": "prosperous",
        "需": "need",
        "喜": "rejoice",
        "領": "jurisdiction",
        "奈": "Nara",
        "別": "separate",
        "国": "country",
        "習": "learn",
        "然": "sort of thing",
        "廷": "courts",
        "憂": "melancholy",
        "散": "scatter",
        "零": "zero",
        "光": "ray",
        "軍": "army",
        "殿": "Mr.",
        "尽": "exhaust",
        "具": "tool",
        "加": "add",
        "諸": "various",
        "故": "happenstance",
        "周": "circumference",
        "牙": "tusk",
        "几": "table",
        "走": "run",
        "夭": "sapling",
        "夾": "squeeze",
    }.items():
        labels.setdefault(g, lab)

    # No new introductions: no primitive in this block has strong multi-lesson payoff
    # beyond existing catalog (堇, 彡, 米, 舛, etc.).

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated catalog labels (no new intros)")


def main() -> None:
    for n in range(111, 121):
        text = (LESSONS / f"lesson_{n:02d}.html").read_text(encoding="utf-8")
        kanji = re.findall(r'data-kanji="([^"]+)"', text)
        missing = [k for k in kanji if k not in STRUCTURES[n]]
        extra = [k for k in STRUCTURES[n] if k not in kanji]
        if missing or extra:
            raise SystemExit(f"L{n} coverage error missing={missing} extra={extra}")

    update_catalog()
    for n in range(111, 121):
        changed = apply_lesson(n)
        print(f"L{n}: {len(changed)} applied")


if __name__ == "__main__":
    main()
