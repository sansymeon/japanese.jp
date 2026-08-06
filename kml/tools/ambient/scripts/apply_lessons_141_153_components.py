#!/usr/bin/env python3
"""Apply Phase-1 component structures for lessons 141–153 (end of Book 1)."""

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


ROLL = V("丷", "夫")
BONSAI = "𡗗"
MIST = V("十", "早")
FENG = V("夂", "丰")


STRUCTURES: dict[int, dict[str, object]] = {
    141: {
        "翰": H(MIST, "羽"),
        "斡": H(MIST, "斗"),
        "鞍": H("革", "安"),
        "鞭": H("革", "便"),
        "鞘": H("革", "肖"),
        "鞄": H("革", "包"),
        "靭": H("革", "刃"),
        "鞠": H("革", V("勹", "米")),
        "顛": H("真", "頁"),
        "穎": H(V("匕", "禾"), "頁"),
        "頗": H("皮", "頁"),
        "頌": H("公", "頁"),
        "頚": H(V("又", "土"), "頁"),
        "餐": V(H("夕", "又"), "食"),
        "饗": V("郷", "食"),
        "蝕": H("食", "虫"),
        "飴": H("食", "台"),
        "駕": V("加", "馬"),
        "騨": H("馬", "単"),
        "馳": H("馬", "也"),
    },
    142: {
        "騙": H("馬", "扁"),
        "馴": H("馬", "川"),
        "駁": H("馬", "爻"),
        "駈": H("馬", "丘"),
        "驢": H("馬", V("虍", "田")),
        "鰻": H("魚", "曼"),
        "鯛": H("魚", "周"),
        "鰯": H("魚", "弱"),
        "鱒": H("魚", "尊"),
        "鮭": H("魚", "圭"),
        "鮪": H("魚", "有"),
        "鮎": H("魚", "占"),
        "鯵": H("魚", "参"),
        "鱈": H("魚", "雪"),
        "鯖": H("魚", "青"),
        "鮫": H("魚", "交"),
        "鰹": H("魚", "堅"),
        "鰍": H("魚", "秋"),
        "鰐": H("魚", V(H("口", "口"), "亏")),
        "鮒": H("魚", "付"),
    },
    143: {
        "鮨": H("魚", "旨"),
        "鰭": H("魚", V("老", "日")),
        "鴎": H("区", "鳥"),
        "鵬": H("朋", "鳥"),
        "鸚": H(H("貝", "貝"), "鳥"),
        "鵡": H("武", "鳥"),
        "鵜": H("弟", "鳥"),
        "鷺": H("路", "鳥"),
        "鷲": H("就", "鳥"),
        "鴨": H("甲", "鳥"),
        "鳶": H("弋", "鳥"),
        "梟": H("木", "鳥"),
        "塵": V("鹿", "土"),
        "麒": H("鹿", "其"),
        "舅": V("臼", "男"),
        "鼠": "鼠",
        "鑿": V(V("业", "羊"), H("殳", "金")),
        "艘": H("舟", V("臼", "又")),
        "瞑": H("目", "冥"),
        "暝": H("日", "冥"),
    },
    144: {
        "坐": V(H("人", "人"), "土"),
        "朔": H("屰", "月"),
        "曳": "曳",
        "洩": H("氵", "曳"),
        "彗": V(H("丰", "丰"), "ヨ"),
        "慧": V(H("丰", "丰"), "ヨ", "心"),
        "爾": "爾",
        "嘉": V(V("十", "豆"), "加"),
        "兇": V("凶", "儿"),
        "兜": "兜",
        "靄": V("雨", H("言", "曷")),
        "劫": H("去", "力"),
        "歎": H("堇", "欠"),
        "輿": V(H("臼", "同"), "車"),
        "歪": V("不", "正"),
        "翠": V("羽", "卒"),
        "黛": V("代", "黒"),
        "鼎": "鼎",
        "鹵": "鹵",
        "鹸": H("鹵", V(ROLL, "㔾")),
    },
    145: {
        "虔": V("虍", "文"),
        "燕": "燕",
        "嘗": V("尚", "旨"),
        "殆": H("歹", "台"),
        "牌": H("片", "卑"),
        "覗": H("司", "見"),
        "齟": H("齒", "且"),
        "齬": H("齒", "吾"),
        "秦": V(BONSAI, "禾"),
        "雀": V("小", "隹"),
        "隼": V("隹", "十"),
        "耀": H("光", V("羽", "隹")),
        "夷": "夷",
        "嚢": "嚢",
        "暢": H("申", "昜"),
        "廻": H("廴", "回"),
        "欣": H("斤", "欠"),
        "毅": H(V("立", "豕"), "殳"),
        "斯": H("其", "斤"),
        "匙": H("是", "匕"),
    },
    146: {
        "匡": V("匚", "王"),
        "肇": V("戸", H("攵", "聿")),
        "麿": V("麻", H("口", "口")),
        "叢": V(H("业", "羊"), "又"),
        "肴": V("乂", "有"),
        "斐": H("非", "文"),
        "卿": "卿",
        "翫": H("習", "元"),
        "於": H("方", V("人", "丶")),
        "套": V("大", "長"),
        "叛": H("半", "反"),
        "尖": V("小", "大"),
        "壷": "壷",
        "叡": H(V("穴", "目", "又"), "又"),
        "酋": V("丷", "酉"),
        "鴬": V("⺍", "鳥"),
        "赫": H("赤", "赤"),
        "臥": H("臣", "人"),
        "甥": H("生", "男"),
        "瓢": H("票", "瓜"),
    },
    147: {
        "琵": H("王", "比"),
        "琶": H("王", "巴"),
        "叉": "叉",
        "乖": "乖",
        "畠": V("白", "田"),
        "圃": V("囗", "甫"),
        "丞": "丞",
        "亮": V("亠", "口", "儿"),
        "胤": V("儿", "幺", "月"),
        "疏": H("疋", V("亠", "ム", "川")),
        "膏": V("高", "月"),
        "魁": H("鬼", "斗"),
        "馨": V(H("声", "殳"), "香"),
        "牒": H("片", V("世", "木")),
        "瞥": V("敝", "目"),
        "睾": V("目", "幸"),
        "巫": "巫",
        "敦": H("享", "攵"),
        "奎": V("大", "圭"),
        "翔": H("羊", "羽"),
    },
    148: {
        "皓": H("白", "告"),
        "黎": V(H("禾", "勹"), "氺"),
        "赳": H("走", "丩"),
        "已": "已",
        "棘": H("朿", "朿"),
        "祟": V("出", "示"),
        "甦": H("更", "生"),
        "剪": H("前", "刀"),
        "躾": H("身", "美"),
        "夥": H("果", "多"),
        "鼾": H("鼻", "干"),
        "陀": H("阝", V("宀", "匕")),
        "粁": H("米", "千"),
        "糎": H("米", "厘"),
        "粍": H("米", "毛"),
        "噸": H("口", "頓"),
        "哩": H("口", "里"),
        "浬": H("氵", "里"),
        "吋": H("口", "寸"),
        "呎": H("口", "尺"),
    },
    149: {
        "梵": H("林", "凡"),
        "薩": V("艹", H("阝", "産")),
        "菩": V("艹", "咅"),
        "唖": H("口", "亜"),
        "牟": "牟",
        "迦": H("⻌", "加"),
        "珈": H("王", "加"),
        "琲": H("王", "非"),
        "檜": H("木", "会"),
        "轡": H("車", V("爫", "臼")),
        "淵": "淵",
        "伍": H("亻", "五"),
        "什": H("亻", "十"),
        "萬": "萬",
        "邁": H("⻌", "萬"),
        "燭": H("火", "蜀"),
        "逞": H("⻌", "呈"),
        "燈": H("火", "登"),
        "裡": H("衤", "里"),
        "薗": V("艹", "園"),
    },
    150: {
        "鋪": H("金", "甫"),
        "嶋": H("山", "鳥"),
        "峯": V("山", FENG),
        "埜": V("林", "土"),
        "龍": "龍",
        "寵": V("宀", "龍"),
        "聾": V("龍", "耳"),
        "慾": V("欲", "心"),
        "嶽": V("山", "獄"),
        "國": V("囗", "或"),
        "脛": H("月", V("又", "土")),
        "勁": H(V("又", "土"), "力"),
        "祀": H("礻", "巳"),
        "祓": H("礻", "犮"),
        "躇": H("足", "著"),
        "壽": "壽",
        "躊": H("足", "壽"),
        "饅": H("食", "曼"),
        "嘔": H("口", "区"),
        "鼈": V("敝", "黽"),
    },
    151: {
        "𠮟": H("口", "七"),
        "塡": H("土", "真"),
        "剝": H(V("彐", "水"), "刂"),
        "頰": H(V("大", H("人", "人")), "頁"),
        "籠": V("竹", "龍"),
        "亙": "亙",
        "亨": "亨",
        "伶": H("亻", "令"),
        "佑": H("亻", "右"),
        "佼": H("亻", "交"),
        "侑": H("亻", "有"),
        "俣": H("亻", V("口", "天")),
        "倖": H("亻", "幸"),
        "傭": H("亻", "庸"),
        "僻": H("亻", H("尸", "辛")),
        "喬": V("夭", "高"),
        "孟": V("子", "皿"),
        "尭": V("卄", "兀"),
        "峨": H("山", "我"),
        "嵯": H("山", "差"),
    },
    152: {
        "巌": V("山", "厳"),
        "巽": V(H("己", "己"), "共"),
        "彪": H("虎", "彡"),
        "掟": H("扌", "定"),
        "掠": H("扌", "京"),
        "撹": H("扌", "覚"),
        "梧": H("木", "吾"),
        "欝": "欝",
        "欽": H("金", "欠"),
        "煕": V(H("臣", "己"), "灬"),
        "熔": H("火", "容"),
        "珪": H("王", "圭"),
        "瑶": H("王", V("爪", "缶")),
        "甫": "甫",
        "聚": V("取", H("人", "人", "人")),
        "舘": H("舎", "官"),
        "舜": "舜",
        "詑": H("言", "它"),
        "諏": H("言", "取"),
        "躯": H("身", "区"),
    },
    153: {
        "郁": H("有", "⻏"),
        "鏑": H("金", "啇"),
        "子": "子",
        "午": "午",
        "未": "未",
        "申": "申",
        "酉": "酉",
        "戌": "戌",
        "亥": "亥",
        "苟": V("艹", "句"),
        "戉": "戉",
        "楚": V(H("木", "木"), "疋"),
        "此": H("止", "匕"),
        "其": "其",
        "肆": H("長", "聿"),
        "昜": V("日", "勿"),
        "卦": H("圭", "卜"),
        "孚": V("爫", "子"),
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
        # Units kept opaque in this block
        "鼠": "rat",
        "曳": "pull",
        "爾": "you",
        "兜": "helmet",
        "鼎": "tripod",
        "鹵": "salt",
        "燕": "swallow",
        "夷": "barbarian",
        "嚢": "pouch",
        "壷": "pot",
        "叉": "forked",
        "乖": "defy",
        "丞": "help",
        "巫": "sorcerer",
        "已": "stop",
        "牟": "moo",
        "淵": "abyss",
        "萬": "ten thousand",
        "龍": "dragon",
        "壽": "longevity",
        "亙": "range",
        "甫": "dog tag",
        "舜": "ancient emperor",
        "戌": "sign of the dog",
        "亥": "sign of the hog",
        "戉": "halberd",
        "卿": "minister",
        "犮": "dog's leg",
        "欝": "gloom",
        "朿": "thorn",
        "亏": "deficiency",
        "卄": "twenty",
        "屰": "upside down",
        "啇": "antique",
        # Familiar wholes reused as parts
        "曷": "siesta",
        "它": "other",
        "黒": "black",
        "香": "incense",
        "美": "beauty",
        "多": "many",
        "鼻": "nose",
        "厘": "rin",
        "頓": "sudden",
        "五": "five",
        "園": "park",
        "欲": "longing",
        "獄": "prison",
        "或": "or",
        "著": "renowned",
        "曼": "mandala",
        "庸": "commonplace",
        "厳": "stern",
        "覚": "memorize",
        "吾": "I",
        "取": "take",
        "舎": "cottage",
        "句": "phrase",
        "長": "long",
        "朋": "companion",
        "武": "warrior",
        "就": "concerning",
        "弋": "arrow",
        "冥": "dark",
        "尚": "furthermore",
        "旨": "delicious",
        "廴": "stretch",
        "習": "learn",
        "元": "beginning",
        "票": "ballot",
        "瓜": "melon",
        "享": "receive",
        "走": "run",
        "更": "grow late",
        "果": "fruit",
        "凡": "mediocre",
        "産": "products",
        "咅": "muzzle",
        "亜": "Asia",
        "蜀": "green caterpillar",
        "呈": "display",
        "登": "ascend",
        "巳": "sign of the snake",
        "七": "seven",
        "令": "orders",
        "夭": "sapling",
        "皿": "dish",
        "兀": "table",
        "我": "ego",
        "共": "together",
        "虎": "tiger",
        "容": "contain",
        "官": "bureaucrat",
        "区": "ward",
        "声": "voice",
        "会": "meeting",
    }.items():
        labels.setdefault(g, lab)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated catalog labels (no new intros)")


def main() -> None:
    for n in range(141, 154):
        text = (LESSONS / f"lesson_{n:02d}.html").read_text(encoding="utf-8")
        kanji = re.findall(r'data-kanji="([^"]+)"', text)
        missing = [k for k in kanji if k not in STRUCTURES[n]]
        extra = [k for k in STRUCTURES[n] if k not in kanji]
        if missing or extra:
            raise SystemExit(f"L{n} coverage error missing={missing} extra={extra}")
        if n < 153 and len(kanji) != 20:
            print(f"note: L{n} has {len(kanji)} kanji")
        if n == 153:
            print(f"L153 has {len(kanji)} kanji (expected 18)")

    update_catalog()
    for n in range(141, 154):
        changed = apply_lesson(n)
        print(f"L{n}: {len(changed)} applied")


if __name__ == "__main__":
    main()
