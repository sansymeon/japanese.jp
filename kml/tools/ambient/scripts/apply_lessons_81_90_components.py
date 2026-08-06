#!/usr/bin/env python3
"""Apply Phase-1 component structures for lessons 81–90."""

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


# Shared nested clusters
BONSAI = "𡗗"  # catalog
GROWING = "龶"  # catalog
PI = H("尸", "辛")  # 辟 without new catalog


STRUCTURES: dict[int, dict[str, object]] = {
    81: {
        "刈": H("乂", "刂"),
        "刹": H(V("㐅", "木"), "刂"),
        "希": V("㐅", "布"),
        "凶": V("㐅", "凵"),
        "胸": H("月", "凶"),
        "離": H("离", "隹"),
        "璃": H("王", "离"),
        "殺": H(V("㐅", "木"), "殳"),
        "爽": H("大", H("㐅", "㐅")),
        "純": H("糸", "屯"),
        "頓": H("屯", "頁"),
        "鈍": H("金", "屯"),
        "辛": "辛",
        "辞": H("舌", "辛"),
        "梓": H("木", "辛"),
        "宰": V("宀", "辛"),
        "壁": V(PI, "土"),
        "璧": H(PI, "玉"),
        "避": H("⻌", PI),
        "新": H(V("立", "木"), "斤"),
    },
    82: {
        "薪": V("艹", "新"),
        "親": H(V("立", "木"), "見"),
        "幸": "幸",
        "執": H("幸", "丸"),
        "摯": H("執", "手"),
        "報": H("幸", V("卩", "又")),
        "叫": H("口", "丩"),
        "糾": H("糸", "丩"),
        "収": H("丩", "又"),
        "卑": "卑",
        "碑": H("石", "卑"),
        "陸": H("阝", V("土", "儿")),
        "睦": H("目", V("土", "儿")),
        "勢": V(H(V("土", "儿"), "丸"), "力"),
        "熱": V(H(V("土", "儿"), "丸"), "灬"),
        "菱": V("艹", V("土", "夂")),
        "陵": H("阝", V("土", "夂")),
        "亥": "亥",
        "核": H("木", "亥"),
        "刻": H("亥", "刂"),
    },
    83: {
        "該": H("言", "亥"),
        "骸": H("骨", "亥"),
        "劾": H("亥", "力"),
        "述": H("⻌", "朮"),
        "術": H("行", "朮"),
        "寒": V("宀", "井", "冫"),
        "塞": V("宀", "井", "土"),
        "醸": H("酉", "襄"),
        "譲": H("言", "襄"),
        "壌": H("土", "襄"),
        "嬢": H("女", "襄"),
        "毒": V(GROWING, "毋"),
        "素": V(GROWING, "糸"),
        "麦": V(GROWING, "夂"),
        "青": V(GROWING, "月"),
        "精": H("米", "青"),
        "請": H("言", "青"),
        "情": H("忄", "青"),
        "晴": H("日", "青"),
        "清": H("氵", "青"),
    },
    84: {
        "静": H("青", "争"),
        "責": V(GROWING, "貝"),
        "績": H("糸", "責"),
        "積": H("禾", "責"),
        "債": H("亻", "責"),
        "漬": H("氵", "責"),
        "表": V(GROWING, "衣"),
        "俵": H("亻", "表"),
        "潔": H("氵", V(H("丰", "刀"), "糸")),
        "契": V(H("丰", "刀"), "大"),
        "喫": H("口", "契"),
        "害": V("宀", "丰", "口"),
        "轄": H("車", "害"),
        "割": H("害", "刂"),
        "憲": V("宀", "丰", "罒", "心"),
        "生": "生",
        "星": V("日", "生"),
        "醒": H("酉", "星"),
        "姓": H("女", "生"),
        "性": H("忄", "生"),
    },
    85: {
        "牲": H("牛", "生"),
        "産": V("立", "厂", "生"),
        "隆": H("阝", V("夂", "生")),
        "峰": H("山", V("夂", "丰")),
        "蜂": H("虫", V("夂", "丰")),
        "縫": H("糸", H("⻌", V("夂", "丰"))),
        "拝": H("扌", H("丰", "丰")),
        "寿": V("丰", "寸"),
        "鋳": H("金", "寿"),
        "籍": V("竹", H("耒", "昔")),
        "春": V(BONSAI, "日"),
        "椿": H("木", "春"),
        "泰": V(BONSAI, "水"),
        "奏": V(BONSAI, "天"),
        "実": V("宀", BONSAI),
        "奉": V(BONSAI, "手"),
        "俸": H("亻", "奉"),
        "棒": H("木", "奉"),
        "謹": H("言", "堇"),
        "僅": H("亻", "堇"),
    },
    86: {
        "勤": H("堇", "力"),
        "漢": H("氵", "堇"),
        "嘆": H("口", "堇"),
        "難": H("堇", "隹"),
        "華": "華",
        "垂": "垂",
        "唾": H("口", "垂"),
        "睡": H("目", "垂"),
        "錘": H("金", "垂"),
        "乗": "乗",
        "剰": H("乗", "刂"),
        "今": "今",
        "含": V("今", "口"),
        "貪": V("今", "貝"),
        "吟": H("口", "今"),
        "念": V("今", "心"),
        "捻": H("扌", "念"),
        "琴": V(H("王", "王"), "今"),
        "陰": H("阝", V("今", "云")),
        "予": "予",
    },
    87: {
        "序": V("广", "予"),
        "預": H("予", "頁"),
        "野": H("里", "予"),
        "兼": "兼",
        "嫌": H("女", "兼"),
        "鎌": H("金", "兼"),
        "謙": H("言", "兼"),
        "廉": V("广", "兼"),
        "西": "西",
        "価": H("亻", "西"),
        "要": V("西", "女"),
        "腰": H("月", "要"),
        "票": V("西", "示"),
        "漂": H("氵", "票"),
        "標": H("木", "票"),
        "栗": V("西", "木"),
        "慄": H("忄", "栗"),
        "遷": H("⻌", V("西", "大", "巳")),
        "覆": V("西", "復"),
        "煙": H("火", V("西", "土")),
    },
    88: {
        "南": "南",
        "楠": H("木", "南"),
        "献": H("南", "犬"),
        "門": "門",
        "問": V("門", "口"),
        "閲": V("門", "兌"),
        "閥": V("門", "伐"),
        "間": V("門", "日"),
        "闇": V("門", "音"),
        "簡": V("竹", "間"),
        "開": V("門", V("一", "廾")),
        "閉": V("門", "才"),
        "閣": V("門", "各"),
        "閑": V("門", "木"),
        "聞": V("門", "耳"),
        "潤": H("氵", V("門", "王")),
        "欄": H("木", V("門", "東")),
        "闘": V("門", H("豆", "寸")),
        "倉": "倉",
        "創": H("倉", "刂"),
    },
    89: {
        "非": "非",
        "俳": H("亻", "非"),
        "排": H("扌", "非"),
        "悲": V("非", "心"),
        "罪": V("罒", "非"),
        "輩": H("非", "車"),
        "扉": H("戸", "非"),
        "侯": H("亻", V("𠂉", "矢")),
        "喉": H("口", "侯"),
        "候": H("侯", "丨"),
        "決": H("氵", "夬"),
        "快": H("忄", "夬"),
        "偉": H("亻", "韋"),
        "違": H("⻌", "韋"),
        "緯": H("糸", "韋"),
        "衛": H("行", "韋"),
        "韓": H(V("十", "早"), "韋"),
        "干": "干",
        "肝": H("月", "干"),
        "刊": H("干", "刂"),
    },
    90: {
        "汗": H("氵", "干"),
        "軒": H("車", "干"),
        "岸": V("山", "厂", "干"),
        "幹": H(V("十", "早"), "干"),
        "芋": V("艹", "于"),
        "宇": V("宀", "于"),
        "余": "余",
        "除": H("阝", "余"),
        "徐": H("彳", "余"),
        "叙": H("余", "又"),
        "途": H("⻌", "余"),
        "斜": H("余", "斗"),
        "塗": V(H("氵", "余"), "土"),
        "束": "束",
        "頼": H("束", "頁"),
        "瀬": H("氵", "頼"),
        "勅": H("束", "力"),
        "疎": H("疋", "束"),
        "辣": H("辛", "束"),
        "速": H("⻌", "束"),
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
        "辛": "spicy",
        "青": "blue",
        "生": "life",
        "門": "gates",
        "非": "un-",
        "干": "dry",
        "今": "now",
        "西": "west",
        "兼": "concurrently",
        "予": "beforehand",
        "余": "too much",
        "束": "bundle",
        "麦": "wheat",
        "毒": "poison",
        "素": "elementary",
        "表": "surface",
        "責": "blame",
        "春": "springtime",
        "奉": "dedicate",
        "寿": "longevity",
        "垂": "droop",
        "乗": "ride",
        "幸": "happiness",
        "亥": "sign of the hog",
        "倉": "godown",
        "南": "south",
        "侯": "marquis",
        "龶": "growing",
        "𡗗": "bonsai",
        "堇": "celery",
        "韋": "tanned leather",
        "襄": "porter",
        "屯": "barracks",
        "丩": "banana",
        "离": "birdhouse",
        "朮": "pup",
        "丰": "bushes",
        "夬": "guillotine",
        "于": "potato",
        "毋": "mother",
        "井": "well",
        "耒": "plow",
        "㐅": "mowed",
        "乂": "mowed",
    }.items():
        labels.setdefault(g, lab)

    intros = data.setdefault("introductions", [])
    existing = {(int(i["lesson"]), i["glyph"]) for i in intros}
    for item in [
        {
            "lesson": 83,
            "beforeKanji": "毒",
            "glyph": "龶",
            "label": "growing",
            "heisig": "growing",
        },
        {
            "lesson": 85,
            "beforeKanji": "春",
            "glyph": "𡗗",
            "label": "bonsai",
            "heisig": "bonsai",
        },
        {
            "lesson": 85,
            "beforeKanji": "謹",
            "glyph": "堇",
            "label": "celery",
            "heisig": "celery",
        },
        {
            "lesson": 89,
            "beforeKanji": "偉",
            "glyph": "韋",
            "label": "tanned leather",
            "heisig": "tanned leather",
        },
    ]:
        key = (item["lesson"], item["glyph"])
        if key not in existing:
            intros.append(item)
            existing.add(key)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated catalog")


def main() -> None:
    for n in range(81, 91):
        text = (LESSONS / f"lesson_{n:02d}.html").read_text(encoding="utf-8")
        kanji = re.findall(r'data-kanji="([^"]+)"', text)
        missing = [k for k in kanji if k not in STRUCTURES[n]]
        extra = [k for k in STRUCTURES[n] if k not in kanji]
        if missing or extra:
            raise SystemExit(f"L{n} coverage error missing={missing} extra={extra}")

    update_catalog()
    for n in range(81, 91):
        changed = apply_lesson(n)
        print(f"L{n}: {len(changed)} applied")


if __name__ == "__main__":
    main()
