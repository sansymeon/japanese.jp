#!/usr/bin/env python3
"""Apply Phase-1 component structures for lessons 51–60."""

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


# Banner cluster helper: 方 over 𠂉 (Heisig banner), without new catalog glyph
BANNER = V("方", "𠂉")

STRUCTURES: dict[int, dict[str, object]] = {
    51: {
        "類": H(V("米", "大"), "頁"),
        "漆": H("氵", V("木", "人", "水")),  # approx 桼; see notes
        "膝": H("月", V("木", "人", "水")),
        "様": H("木", V("羊", "水")),
        "求": "求",
        "球": H("王", "求"),
        "救": H("求", "夂"),
        "竹": "竹",
        "笑": V("竹", "天"),
        "笠": V("竹", "立"),
        "笹": V("竹", "世"),
        "箋": V("竹", H("戈", "戈")),
        "筋": V("竹", H("月", "力")),
        "箱": V("竹", "相"),
        "筆": V("竹", "聿"),
        "筒": V("竹", "同"),
        "等": V("竹", "寺"),
        "算": V("竹", "目", "廾"),
        "答": V("竹", "合"),
        "策": V("竹", "束"),
    },
    52: {
        "簿": V("竹", H("氵", "専")),
        "築": V("竹", V(H("工", "凡"), "木")),
        "篭": V("竹", "竜"),
        "人": "人",
        "佐": H("亻", "左"),
        "侶": H("亻", V("口", "口")),
        "但": H("亻", "旦"),
        "住": H("亻", "主"),
        "位": H("亻", "立"),
        "仲": H("亻", "中"),
        "体": H("亻", "本"),
        "悠": V(H("亻", "攵"), "心"),  # simplified 攸
        "件": H("亻", "牛"),
        "仕": H("亻", "士"),
        "他": H("亻", "也"),
        "伏": H("亻", "犬"),
        "伝": H("亻", "云"),
        "仏": H("亻", "ム"),
        "休": H("亻", "木"),
        "仮": H("亻", "反"),
    },
    53: {
        "伎": H("亻", "支"),
        "伯": H("亻", "白"),
        "俗": H("亻", "谷"),
        "信": H("亻", "言"),
        "佳": H("亻", "圭"),
        "依": H("亻", "衣"),
        "例": H("亻", "列"),
        "個": H("亻", "固"),
        "健": H("亻", "建"),
        "側": H("亻", "則"),
        "侍": H("亻", "寺"),
        "停": H("亻", "亭"),
        "値": H("亻", "直"),
        "倣": H("亻", "放"),
        "傲": H("亻", V("土", "方", "夂")),  # approx
        "倒": H("亻", "到"),
        "偵": H("亻", "貞"),
        "僧": H("亻", "曽"),
        "億": H("亻", "意"),
        "儀": H("亻", "義"),
    },
    54: {
        "償": H("亻", "賞"),
        "仙": H("亻", "山"),
        "催": H("亻", V("山", "隹")),
        "仁": H("亻", "二"),
        "侮": H("亻", "毎"),
        "使": H("亻", "吏"),
        "便": H("亻", "更"),
        "倍": H("亻", "咅"),
        "優": H("亻", "憂"),
        "伐": H("亻", "戈"),
        "宿": V("宀", H("亻", "百")),
        "傷": H("亻", V("𠂉", "易")),  # reclining + easy-ish; alt 昜
        "保": H("亻", V("口", "木")),
        "褒": V("亠", H("亻", V("口", "木")), "𧘇"),  # too exotic
        "傑": H("亻", V("舛", "木")),
        "付": H("亻", "寸"),
        "符": V("竹", "付"),
        "府": V("广", "付"),
        "任": H("亻", "壬"),
        "賃": V("任", "貝"),
    },
    55: {
        "代": H("亻", "弋"),
        "袋": V("代", "衣"),
        "貸": V("代", "貝"),
        "化": H("亻", "匕"),
        "花": V("艹", "化"),
        "貨": V("化", "貝"),
        "傾": H("化", "頁"),
        "何": H("亻", "可"),
        "荷": V("艹", "何"),
        "俊": H("亻", V("允", "夂")),  # same streetwalker as 唆
        "傍": H("亻", V("立", "方")),  # approx bystander
        "俺": H("亻", "奄"),
        "久": "久",
        "畝": V("亩", "久"),  # weak; use V(H("亠","田"), "久")?
        "囚": V("囗", "人"),
        "内": V("冂", "人"),
        "丙": V("一", "人", "冂"),  # approx; often self
        "柄": H("木", "丙"),
        "肉": "肉",
        "腐": V("府", "肉"),
    },
    56: {
        "座": V("广", H("人", "人"), "土"),
        "挫": H("扌", V(H("人", "人"), "土")),
        "卒": V("亠", "人", "十"),
        "傘": V("人", H("人", "人", "人", "人"), "十"),  # show many people
        "匁": H("勹", "メ"),  # monme; approximate
        "以": H("亻", "丶"),  # by means of; often person+drop — use self better?
        "似": H("亻", "以"),
        "併": H("亻", "并"),
        "瓦": "瓦",
        "瓶": H("并", "瓦"),
        "宮": V("宀", V("口", "口", "口") if False else H(V("口", "口"), "口")),
        "営": V("⺍", "冖", H(V("口", "口"), "口")),
        "善": V("羊", V("丷", "口")),  # virtuous approx
        "膳": H("月", "善"),
        "年": "年",
        "夜": V("亠", H("亻", "夕")),
        "液": H("氵", "夜"),
        "塚": H("土", V("冖", "豕")),
        "幣": V(H("敝",), "巾") if False else V(V("㡀", "夂"), "巾"),
        "蔽": V("艹", V("㡀", "夂")),
    },
    57: {
        "弊": V(V("㡀", "夂"), "廾"),
        "喚": H("口", V("勹", "奂")),  # better expand
        "換": H("扌", V("勹", "大")),  # interchange approx bound+four+large
        "融": H(V("鬲",), "虫") if False else H(V("一", "口", "冂", "丷", "丨"), "虫"),
        "施": H(BANNER, "也"),
        "旋": H(BANNER, "疋"),
        "遊": H("⻌", H(BANNER, "子")),
        "旅": H(BANNER, H("人", "人")),  # trip: banner + persons
        "勿": "勿",
        "物": H("牛", "勿"),
        "易": V("日", "勿"),
        "賜": H("貝", "易"),
        "尿": V("尸", "水"),
        "尼": V("尸", "匕"),
        "尻": V("尸", "九"),
        "泥": H("氵", "尼"),
        "塀": H("土", V("尸", "并")),
        "履": V("尸", "復"),
        "屋": V("尸", "至"),
        "握": H("扌", "屋"),
    },
    58: {
        "屈": V("尸", "出"),
        "掘": H("扌", "屈"),
        "堀": H("土", "屈"),
        "居": V("尸", "古"),
        "据": H("扌", "居"),
        "裾": H("衤", "居"),
        "層": V("尸", "曽"),
        "局": V("尸", "句"),
        "遅": H("⻌", V("尸", "羊")),
        "漏": H("氵", V("尸", "雨")),
        "刷": H(V("尸", "巾"), "刂"),
        "尺": "尺",
        "尽": V("尺", "⺀"),  # ice dots; use 冫?
        "沢": H("氵", "尺"),
        "訳": H("言", "尺"),
        "択": H("扌", "尺"),
        "昼": V("尺", "旦"),
        "戸": "戸",
        "肩": V("戸", "月"),
        "房": V("戸", "方"),
    },
    59: {
        "扇": V("戸", "羽"),
        "炉": H("火", "戸"),
        "戻": V("戸", "大"),
        "涙": H("氵", "戻"),
        "雇": V("戸", "隹"),
        "顧": H("雇", "頁"),
        "啓": V(H("戸", "夂"), "口"),
        "示": "示",
        "礼": H("礻", "乚"),
        "祥": H("礻", "羊"),
        "祝": H("礻", "兄"),
        "福": H("礻", "畐"),
        "祉": H("礻", "止"),
        "社": H("礻", "土"),
        "視": H("礻", "見"),
        "奈": V("大", "示"),
        "尉": H(V("尸", "示"), "寸"),
        "慰": V("尉", "心"),
        "款": H(V("士", "示"), "欠"),
        "禁": V("林", "示"),
    },
    60: {
        "襟": H("衤", "禁"),
        "宗": V("宀", "示"),
        "崇": V("山", "宗"),
        "祭": V(H("月", "又"), "示"),
        "察": V("宀", "祭"),
        "擦": H("扌", "察"),
        "由": "由",
        "抽": H("扌", "由"),
        "油": H("氵", "由"),
        "袖": H("衤", "由"),
        "宙": V("宀", "由"),
        "届": V("尸", "由"),
        "笛": V("竹", "由"),
        "軸": H("車", "由"),
        "甲": "甲",
        "押": H("扌", "甲"),
        "岬": H("山", "甲"),
        "挿": H("扌", V("千", "甲")),
        "申": "申",
        "伸": H("亻", "申"),
    },
}

# --- refinements for pedagogical clarity ---
STRUCTURES[54]["褒"] = V("亠", "保", "衣")
STRUCTURES[54]["傷"] = H("亻", V("𠂉", "昜"))

STRUCTURES[55]["畝"] = V(H("亠", "田"), "久")
STRUCTURES[55]["丙"] = "丙"
STRUCTURES[55]["傍"] = H("亻", V("立", "冖", "方"))
STRUCTURES[55]["俺"] = H("亻", "奄")
STRUCTURES[55]["俊"] = H("亻", V("允", "夂"))
STRUCTURES[55]["傾"] = H("化", "頁")  # Heisig: change + page

STRUCTURES[56]["以"] = "以"
STRUCTURES[56]["宮"] = V("宀", V("口", "口", "口"))
STRUCTURES[56]["営"] = V("⺍", "冖", V("口", "口", "口"))
STRUCTURES[56]["善"] = V("羊", "口")
STRUCTURES[56]["併"] = H("亻", V("丷", "开"))
STRUCTURES[56]["瓶"] = H(V("丷", "开"), "瓦")
STRUCTURES[56]["幣"] = V("敝", "巾")
STRUCTURES[56]["蔽"] = V("艹", "敝")
STRUCTURES[56]["匁"] = "匁"
STRUCTURES[56]["傘"] = V(H("人", "人", "人", "人", "人"), "十")
STRUCTURES[56]["座"] = V("广", H("人", "人"), "土")
STRUCTURES[56]["挫"] = H("扌", V(H("人", "人"), "土"))

STRUCTURES[57]["喚"] = H("口", V("勹", "四", "大"))
STRUCTURES[57]["換"] = H("扌", V("勹", "四", "大"))
STRUCTURES[57]["融"] = H(V("一", "口", "冂", "儿"), "虫")
STRUCTURES[57]["旅"] = H(BANNER, H("人", "人"))
STRUCTURES[57]["遊"] = H("⻌", H(BANNER, "子"))
STRUCTURES[57]["弊"] = V("敝", "廾")
STRUCTURES[57]["塀"] = H("土", V("尸", V("丷", "开")))

STRUCTURES[58]["尽"] = V("尺", "冫")
STRUCTURES[58]["戸"] = "戸"

STRUCTURES[59]["福"] = H("礻", V("一", "口", "田"))


def extract_component_box(section: str) -> tuple[int, int] | None:
    """Return [start, end) of the first balanced component-box, if any."""
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
        m = re.match(r'([^>]*>)([\s\S]*)', body)
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
        "亻": "person",
        "尸": "flag",
        "礻": "altar",
        "竹": "bamboo",
        "求": "request",
        "勿": "not",
        "尺": "shaku",
        "戸": "door",
        "由": "wherefore",
        "甲": "armor",
        "申": "declare",
        "敝": "shredder",
        "并": "put together",
        "咅": "muzzle",
        "畐": "wealth",
        "弋": "arrow",
        "奄": "hitherto",
        "开": "open",
    }.items():
        labels.setdefault(g, lab)

    intros = data.setdefault("introductions", [])
    existing = {(int(i["lesson"]), i["glyph"]) for i in intros}
    for item in [
        {"lesson": 52, "beforeKanji": "佐", "glyph": "亻", "label": "person", "heisig": "person"},
        {"lesson": 56, "beforeKanji": "幣", "glyph": "敝", "label": "shredder", "heisig": "shredder"},
        {"lesson": 57, "beforeKanji": "尿", "glyph": "尸", "label": "flag", "heisig": "flag"},
        {"lesson": 59, "beforeKanji": "礼", "glyph": "礻", "label": "altar", "heisig": "altar"},
    ]:
        key = (item["lesson"], item["glyph"])
        if key not in existing:
            intros.append(item)
            existing.add(key)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated catalog")


def main() -> None:
    update_catalog()
    for n in range(51, 61):
        changed = apply_lesson(n)
        print(f"L{n}: {len(changed)} applied")


if __name__ == "__main__":
    main()
