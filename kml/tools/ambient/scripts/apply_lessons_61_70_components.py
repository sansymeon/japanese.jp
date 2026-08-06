#!/usr/bin/env python3
"""Apply Phase-1 component structures for lessons 61–70."""

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


# Shared pedagogical clusters (no new catalog glyphs unless noted)
BANNER = V("方", "𠂉")
# Rolling / clasp top seen in 券巻勝… and 峡狭挟頬 (丷 + 夫)
ROLL = V("丷", "夫")
# Broom-ish (彐/ヨ + towel) for 婦掃
BROOM = V("ヨ", "巾")
# Old-man lock (catalog 耂)
# Jawbone (catalog 咼)
# Pinnacle radical (catalog 阝)


STRUCTURES: dict[int, dict[str, object]] = {
    61: {
        "神": H("礻", "申"),
        "捜": H("扌", V("申", "又")),
        "果": V("田", "木"),
        "菓": V("艹", "果"),
        "課": H("言", "果"),
        "裸": H("衤", "果"),
        "斤": "斤",
        "析": H("木", "斤"),
        "所": H("戸", "斤"),
        "祈": H("礻", "斤"),
        "近": H("⻌", "斤"),
        "折": H("扌", "斤"),
        "哲": V("折", "口"),
        "逝": H("⻌", "折"),
        "誓": V("折", "言"),
        "斬": H("車", "斤"),
        "暫": V("斬", "日"),
        "漸": H("氵", "斬"),
        "断": H("米", "斤"),
        "質": V(H("斤", "斤"), "貝"),
    },
    62: {
        "斥": H("斤", "丶"),
        "訴": H("言", "斥"),
        "昨": H("日", "乍"),
        "詐": H("言", "乍"),
        "作": H("亻", "乍"),
        "雪": V("雨", "ヨ"),
        "録": H("金", V("ヨ", "水")),
        "剥": H(V("ヨ", "水"), "刂"),
        "尋": V(H("ヨ", "工", "口"), "寸"),
        "急": V("⺈", "ヨ", "心"),
        "穏": H("禾", V("⺍", "工", "心")),
        "侵": H("亻", V("ヨ", "冖", "又")),
        "浸": H("氵", V("ヨ", "冖", "又")),
        "寝": V("宀", H("丬", V("ヨ", "冖", "又"))),
        "婦": H("女", BROOM),
        "掃": H("扌", BROOM),
        "当": V("⺌", "ヨ"),
        "彙": V("ヨ", "果"),
        "争": V("⺈", "ヨ"),
        "浄": H("氵", "争"),
    },
    63: {
        "事": "事",
        "唐": V("广", "ヨ", "口"),
        "糖": H("米", "唐"),
        "康": V("广", "ヨ", "水"),
        "逮": H("⻌", V("ヨ", "水")),
        "伊": H("亻", "尹"),
        "君": V("尹", "口"),
        "群": H("君", "羊"),
        "耐": H("而", "寸"),
        "需": V("雨", "而"),
        "儒": H("亻", "需"),
        "端": H("立", V("山", "而")),
        "両": "両",
        "満": H("氵", V("艹", "両")),
        "画": V("一", "田", "凵"),
        "歯": V("止", "米", "凵"),
        "曲": "曲",
        "曹": V("一", "曲", "日"),
        "遭": H("⻌", "曹"),
        "漕": H("氵", "曹"),
    },
    64: {
        "槽": H("木", "曹"),
        "斗": "斗",
        "料": H("米", "斗"),
        "科": H("禾", "斗"),
        "図": V("囗", "乂"),
        "用": "用",
        "庸": V("广", "ヨ", "用"),
        "備": H("亻", V("艹", "用")),
        "昔": V("龷", "日"),
        "錯": H("金", "昔"),
        "借": H("亻", "昔"),
        "惜": H("忄", "昔"),
        "措": H("扌", "昔"),
        "散": H(V("龷", "月"), "夂"),
        "廿": "廿",
        "庶": V("广", "廿", "灬"),
        "遮": H("⻌", "庶"),
        "席": V("广", "廿", "巾"),
        "度": V("广", "廿", "又"),
        "渡": H("氵", "度"),
    },
    65: {
        "奔": V("大", H("十", "廾")),
        "噴": H("口", V(H("十", "廾"), "貝")),
        "墳": H("土", V(H("十", "廾"), "貝")),
        "憤": H("忄", V(H("十", "廾"), "貝")),
        "焼": H("火", V("卄", "兀")),
        "暁": H("日", V("卄", "兀")),
        "半": "半",
        "伴": H("亻", "半"),
        "畔": H("田", "半"),
        "判": H("半", "刂"),
        "拳": V(ROLL, "手"),
        "券": V(ROLL, "刀"),
        "巻": V(ROLL, "己"),
        "圏": V("囗", "巻"),
        "勝": H("月", V(ROLL, "力")),
        "藤": V("艹", H("月", V(ROLL, "水"))),
        "謄": H(V(ROLL, "月"), "言"),
        "片": "片",
        "版": H("片", "反"),
        "之": "之",
    },
    66: {
        "乏": "乏",
        "芝": V("艹", "之"),
        "不": "不",
        "否": V("不", "口"),
        "杯": H("木", "不"),
        "矢": "矢",
        "矯": H("矢", V("夭", "高")),
        "族": H(BANNER, "矢"),
        "知": H("矢", "口"),
        "智": V("知", "日"),
        "挨": H("扌", V("ム", "矢")),
        "矛": "矛",
        "柔": V("矛", "木"),
        "務": H(V("矛", "夂"), "力"),
        "霧": V("雨", "務"),
        "班": H("王", "刀", "王"),
        "帰": H(V("丿", "止"), BROOM),
        "弓": "弓",
        "引": H("弓", "丨"),
        "弔": H("弓", "丨"),
    },
    67: {
        "弘": H("弓", "ム"),
        "強": H("弓", V("ム", "虫")),
        "弥": H("弓", V("𠂉", "小")),
        "弱": H(V("弓", "冫"), V("弓", "冫")),
        "溺": H("氵", "弱"),
        "沸": H("氵", "弗"),
        "費": V("弗", "貝"),
        "第": V("竹", "弟"),
        "弟": "弟",
        "巧": H("工", "丂"),
        "号": V("口", "丂"),
        "朽": H("木", "丂"),
        "誇": H("言", V("大", "丂")),
        "顎": H(V(H("口", "口"), "丂"), "頁"),
        "汚": H("氵", "丂"),
        "与": "与",
        "写": V("冖", "与"),
        "身": "身",
        "射": H("身", "寸"),
        "謝": H("言", "射"),
    },
    68: {
        "老": V("耂", "匕"),
        "考": V("耂", "丂"),
        "孝": V("耂", "子"),
        "教": H("孝", "夂"),
        "拷": H("扌", "考"),
        "者": V("耂", "日"),
        "煮": V("者", "灬"),
        "著": V("艹", "者"),
        "箸": V("竹", "者"),
        "署": V("罒", "者"),
        "暑": V("日", "者"),
        "諸": H("言", "者"),
        "猪": H("犭", "者"),
        "渚": H("氵", "者"),
        "賭": H("貝", "者"),
        "峡": H("山", ROLL),
        "狭": H("犭", ROLL),
        "挟": H("扌", ROLL),
        "頬": H(ROLL, "頁"),
        "追": H("⻌", V("丿", "止")),
    },
    69: {
        "阜": "阜",
        "師": H(V("𠂤", "一"), "巾"),
        "帥": H("𠂤", "巾"),
        "官": V("宀", "㠯"),
        "棺": H("木", "官"),
        "管": V("竹", "官"),
        "父": "父",
        "釜": V("父", "金"),
        "交": "交",
        "効": H("交", "力"),
        "較": H("車", "交"),
        "校": H("木", "交"),
        "足": "足",
        "促": H("亻", "足"),
        "捉": H("扌", "足"),
        "距": H("足", "巨"),
        "路": H("足", "各"),
        "露": V("雨", "路"),
        "跳": H("足", "兆"),
        "躍": H("足", V("羽", "隹")),
    },
    70: {
        "践": H("足", H("戈", "戈")),
        "踏": H("足", V("水", "日")),
        "踪": H("足", "宗"),
        "骨": "骨",
        "滑": H("氵", "骨"),
        "髄": H("骨", H("⻌", "有")),
        "禍": H("礻", "咼"),
        "渦": H("氵", "咼"),
        "鍋": H("金", "咼"),
        "過": H("⻌", "咼"),
        "阪": H("阝", "反"),
        "阿": H("阝", "可"),
        "際": H("阝", "祭"),
        "障": H("阝", "章"),
        "隙": H("阝", V("小", "日", "小")),
        "随": H("阝", H("⻌", "有")),
        "陪": H("阝", "咅"),
        "陽": H("阝", "昜"),
        "陳": H("阝", "東"),
        "防": H("阝", "方"),
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
            new_box = box(structs[kanji])
            section = replace_component_box(section, new_box)
            section = strip_after_box(section)
            changed.append(kanji)
        out.extend([tag, open_rest + section + after])
    path.write_text("".join(out), encoding="utf-8")
    return changed


def update_catalog() -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    labels = data.setdefault("componentLabels", {})
    for g, lab in {
        "斤": "axe",
        "果": "fruit",
        "乍": "saw",
        "ヨ": "broom",
        "而": "rake",
        "斗": "Big Dipper",
        "用": "utilize",
        "廿": "twenty",
        "龷": "salad",
        "半": "half",
        "片": "one-sided",
        "之": "of",
        "乏": "beggar",
        "不": "negative",
        "矢": "dart",
        "矛": "halberd",
        "弓": "bow",
        "弟": "younger brother",
        "丂": "aesop",
        "弗": "dollar",
        "与": "bestow",
        "身": "somebody",
        "耂": "old man",
        "者": "someone",
        "阜": "pinnacle",
        "阝": "pinnacle",
        "𠂤": "puppet",
        "㠯": "pipeline",
        "父": "father",
        "交": "mingle",
        "足": "leg",
        "骨": "skeleton",
        "咼": "jawbone",
        "卄": "twenty",
        "乂": "mowed",
        "丨": "stick",
        "夭": "sapling",
        "尹": "commanding",
    }.items():
        labels.setdefault(g, lab)

    intros = data.setdefault("introductions", [])
    existing = {(int(i["lesson"]), i["glyph"]) for i in intros}
    for item in [
        {
            "lesson": 68,
            "beforeKanji": "老",
            "glyph": "耂",
            "label": "old man",
            "heisig": "old man",
        },
        {
            "lesson": 70,
            "beforeKanji": "禍",
            "glyph": "咼",
            "label": "jawbone",
            "heisig": "jawbone",
        },
        {
            "lesson": 70,
            "beforeKanji": "阪",
            "glyph": "阝",
            "label": "pinnacle",
            "heisig": "pinnacle",
        },
    ]:
        key = (item["lesson"], item["glyph"])
        if key not in existing:
            intros.append(item)
            existing.add(key)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated catalog")


def main() -> None:
    # coverage check
    for n in range(61, 71):
        text = (LESSONS / f"lesson_{n:02d}.html").read_text(encoding="utf-8")
        kanji = re.findall(r'data-kanji="([^"]+)"', text)
        missing = [k for k in kanji if k not in STRUCTURES[n]]
        extra = [k for k in STRUCTURES[n] if k not in kanji]
        if missing or extra:
            raise SystemExit(f"L{n} coverage error missing={missing} extra={extra}")

    update_catalog()
    for n in range(61, 71):
        changed = apply_lesson(n)
        print(f"L{n}: {len(changed)} applied")


if __name__ == "__main__":
    main()
