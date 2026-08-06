#!/usr/bin/env python3
"""Apply Phase-1 component structures for lessons 101–110."""

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


AWNING_PEOPLE = V(H("人", "人"), "一", "人")  # 㑒 nest (験 etc.)


STRUCTURES: dict[int, dict[str, object]] = {
    101: {
        "脈": H("月", "永"),
        "衆": V("血", H("人", "人")),
        "逓": H("⻌", V("厂", "䒑", "巾")),
        "段": H(V("丨", "几"), "殳"),
        "鍛": H("金", "段"),
        "后": V("厂", "口"),
        "幻": H("幺", "𠃌"),
        "司": V("𠃌", "一", "口"),
        "伺": H("亻", "司"),
        "詞": H("言", "司"),
        "飼": H("食", "司"),
        "嗣": H(V("口", "冊"), "司"),
        "舟": "舟",
        "舶": H("舟", "白"),
        "航": H("舟", "亢"),
        "舷": H("舟", "玄"),
        "般": H("舟", "殳"),
        "盤": V("般", "皿"),
        "搬": H("扌", "般"),
        "船": H("舟", V("八", "口")),
    },
    102: {
        "艦": H("舟", "監"),
        "艇": H("舟", "廷"),
        "瓜": "瓜",
        "弧": H("弓", "瓜"),
        "孤": H("子", "瓜"),
        "繭": V("艹", H("糸", "虫")),
        "益": V("丷", "八", "皿"),
        "暇": H("日", "叚"),
        "敷": H(V("甫", "方"), "攵"),
        "来": "来",
        "気": V("气", "㐅"),
        "汽": H("氵", "气"),
        "飛": "飛",
        "沈": H("氵", "冘"),
        "枕": H("木", "冘"),
        "妻": V("十", "ヨ", "女"),
        "凄": H("冫", "妻"),
        "衰": "衰",
        "衷": V("亠", "中", "𧘇"),
        "面": "面",
    },
    103: {
        "麺": H("麦", "面"),
        "革": "革",
        "靴": H("革", "化"),
        "覇": V("西", H("革", "月")),
        "声": V("士", "尸"),
        "眉": V("𠃜", "目"),
        "呉": "呉",
        "娯": H("女", "呉"),
        "誤": H("言", "呉"),
        "蒸": V("艹", V("丞", "灬")),
        "承": "承",
        "函": V("一", "水", "凵"),
        "極": H("木", "亟"),
        "牙": "牙",
        "芽": V("艹", "牙"),
        "邪": H("牙", "⻏"),
        "雅": H("牙", "隹"),
        "釈": H("釆", "尺"),
        "番": V("釆", "田"),
        "審": V("宀", "番"),
    },
    104: {
        "翻": H("番", "羽"),
        "藩": V("艹", H("氵", "番")),
        "毛": "毛",
        "耗": H("耒", "毛"),
        "尾": V("尸", "毛"),
        "宅": V("宀", "乇"),
        "託": H("言", "乇"),
        "為": "為",
        "偽": H("亻", "為"),
        "畏": V("田", "一", "𧰨"),
        "長": "長",
        "張": H("弓", "長"),
        "帳": H("巾", "長"),
        "脹": H("月", "長"),
        "髪": V("髟", "友"),
        "展": V("尸", "龷", "𧰨"),
        "喪": "喪",
        "巣": V("⺍", "果"),
        "単": "単",
        "戦": H("単", "戈"),
    },
    105: {
        "禅": H("礻", "単"),
        "弾": H("弓", "単"),
        "桜": H("木", V("⺍", "女")),
        "獣": H("単", "犬"),
        "脳": H("月", V("⺍", "囟")),
        "悩": H("忄", V("⺍", "囟")),
        "厳": V("⺍", "厂", "敢"),
        "鎖": H("金", V("⺌", "貝")),
        "挙": V("⺍", "手"),
        "誉": V("⺍", "言"),
        "猟": H("犭", V("⺍", "用")),
        "鳥": "鳥",
        "鳴": H("口", "鳥"),
        "鶴": H("寉", "鳥"),
        "烏": "烏",
        "蔦": V("艹", "鳥"),
        "鳩": H("九", "鳥"),
        "鶏": H("奚", "鳥"),
        "島": V("山", "鳥"),
        "暖": H("日", "爰"),
    },
    106: {
        "媛": H("女", "爰"),
        "援": H("扌", "爰"),
        "緩": H("糸", "爰"),
        "属": V("尸", "禹"),
        "嘱": H("口", "属"),
        "偶": H("亻", "禺"),
        "遇": H("⻌", "禺"),
        "愚": V("禺", "心"),
        "隅": H("阝", "禺"),
        "逆": H("⻌", "屰"),
        "塑": V("朔", "土"),
        "遡": H("⻌", "朔"),
        "岡": "岡",
        "鋼": H("金", "岡"),
        "綱": H("糸", "岡"),
        "剛": H("岡", "刂"),
        "缶": "缶",
        "陶": H("阝", V("勹", "缶")),
        "揺": H("扌", V("爪", "缶")),
        "謡": H("言", V("爪", "缶")),
    },
    107: {
        "鬱": "鬱",
        "就": H("京", "尤"),
        "蹴": H("足", "就"),
        "懇": V(H("豸", "艮"), "心"),
        "墾": V(H("豸", "艮"), "土"),
        "貌": H("豸", V("白", "儿")),
        "免": "免",
        "逸": H("⻌", "免"),
        "晩": H("日", "免"),
        "勉": H("免", "力"),
        "象": "象",
        "像": H("亻", "象"),
        "馬": "馬",
        "駒": H("馬", "句"),
        "験": H("馬", AWNING_PEOPLE),
        "騎": H("馬", "奇"),
        "駐": H("馬", "主"),
        "駆": H("馬", "区"),
        "駅": H("馬", "尺"),
        "騒": H("馬", V("又", "虫")),
    },
    108: {
        "駄": H("馬", "太"),
        "驚": H("敬", "馬"),
        "篤": V("竹", "馬"),
        "罵": V("罒", "馬"),
        "騰": H("朕", "馬"),
        "虎": V("虍", "儿"),
        "虜": V("虍", "男"),
        "膚": V("虍", "胃"),
        "虚": V("虍", "业"),
        "戯": H("虚", "戈"),
        "虞": V("虍", "呉"),
        "慮": V("虍", "思"),
        "劇": H(V("虍", "豕"), "刂"),
        "虐": V("虍", "乚"),
        "鹿": "鹿",
        "麓": V("林", "鹿"),
        "薦": V("艹", "廌"),
        "慶": "慶",
        "麗": V("丽", "鹿"),
        "熊": V("能", "灬"),
    },
    109: {
        "能": "能",
        "態": V("能", "心"),
        "寅": "寅",
        "演": H("氵", "寅"),
        "辰": "辰",
        "辱": V("辰", "寸"),
        "震": V("雨", "辰"),
        "振": H("扌", "辰"),
        "娠": H("女", "辰"),
        "唇": V("辰", "口"),
        "農": V("曲", "辰"),
        "濃": H("氵", "農"),
        "送": H("⻌", V("丷", "天")),
        "関": V("門", V("丷", "天")),
        "咲": H("口", V("丷", "天")),
        "鬼": "鬼",
        "醜": H("酉", "鬼"),
        "魂": H("云", "鬼"),
        "魔": H("麻", "鬼"),
        "魅": H("鬼", "未"),
    },
    110: {
        "塊": H("土", "鬼"),
        "襲": V("龍", "衣"),
        "嚇": H("口", H("赤", "赤")),
        "朕": "朕",
        "雰": V("雨", "分"),
        "箇": V("竹", "固"),
        "錬": H("金", "東"),
        "遵": H("⻌", "尊"),
        "罷": V("罒", "能"),
        "屯": "屯",
        "且": "且",
        "藻": V("艹", H("氵", V("品", "木"))),
        "隷": H(V("士", "示"), "隶"),
        "癒": V("疒", V("俞", "心")),
        "璽": V("爾", "玉"),
        "潟": H("氵", "舄"),
        "丹": "丹",
        "丑": "丑",
        "羞": V("羊", "丑"),
        "卯": "卯",
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
        "舟": "boat",
        "司": "director",
        "瓜": "melon",
        "来": "come",
        "気": "spirit",
        "气": "steam",
        "飛": "fly",
        "面": "mask",
        "革": "leather",
        "牙": "tusk",
        "番": "turn",
        "毛": "fur",
        "長": "long",
        "単": "simple",
        "鳥": "bird",
        "烏": "crow",
        "馬": "horse",
        "象": "elephant",
        "虎": "tiger",
        "虍": "tiger stripes",
        "鹿": "deer",
        "能": "ability",
        "寅": "sign of the tiger",
        "辰": "sign of the dragon",
        "鬼": "ghost",
        "缶": "can",
        "岡": "hill",
        "禺": "long-tailed monkey",
        "豸": "snake / badger",
        "爰": "monkey",
        "冘": "float",
        "乇": "home",
        "髟": "hair",
        "囱": "brain",
        "囟": "brains",
        "隹": "turkey",
        "寉": "crane nest",
        "奚": "servant",
        "禹": "serpent",
        "屰": "upside down",
        "朔": "first day of month",
        "隶": "slave",
        "俞": "transport",
        "爾": "you",
        "舄": "magpie",
        "龙": "dragon",
        "龍": "dragon",
        "丽": "lovely",
        "廌": "unicorn",
        "敢": "daring",
        "亟": "urgency",
        "叚": "borrow",
        "廷": "courts",
        "亢": "high spirits",
        "𠃌": "hook",
        "丞": "helping hand",
        "𠃜": "eyebrow top",
        "𧰨": "animal legs",
        "采": "dice",
        "甫": "dog tag",
        "朕": "I (emperor)",
        "丹": "cinnabar",
        "丑": "sign of the cow",
        "卯": "sign of the hare",
        "屯": "barracks",
        "且": "alongside",
        "免": "excuse",
        "就": "concerning",
        "呉": "give",
        "声": "voice",
        "眉": "eyebrow",
        "為": "do",
        "巣": "nest",
        "厳": "stern",
        "挙": "raise",
        "島": "island",
        "属": "belong",
        "鬱": "gloom",
        "慶": "jubilation",
        "喪": "miss",
        "衰": "decline",
        "承": "acquiesce",
        "面": "mask",
    }.items():
        labels.setdefault(g, lab)

    intros = data.setdefault("introductions", [])
    existing = {(int(i["lesson"]), i["glyph"]) for i in intros}
    for item in [
        {
            "lesson": 108,
            "beforeKanji": "虎",
            "glyph": "虍",
            "label": "tiger stripes",
            "heisig": "tiger",
        },
    ]:
        key = (item["lesson"], item["glyph"])
        if key not in existing:
            intros.append(item)
            existing.add(key)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated catalog")


def main() -> None:
    for n in range(101, 111):
        text = (LESSONS / f"lesson_{n:02d}.html").read_text(encoding="utf-8")
        kanji = re.findall(r'data-kanji="([^"]+)"', text)
        missing = [k for k in kanji if k not in STRUCTURES[n]]
        extra = [k for k in STRUCTURES[n] if k not in kanji]
        if missing or extra:
            raise SystemExit(f"L{n} coverage error missing={missing} extra={extra}")

    update_catalog()
    for n in range(101, 111):
        changed = apply_lesson(n)
        print(f"L{n}: {len(changed)} applied")


if __name__ == "__main__":
    main()
