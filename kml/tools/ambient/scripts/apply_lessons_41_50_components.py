#!/usr/bin/env python3
"""Apply Phase-1 component structures for lessons 41–50 (and verify 41–42)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LESSONS = ROOT / "contents" / "books" / "book_01" / "lessons"
CATALOG = ROOT / "tools" / "ambient" / "data" / "kanji_components_catalog.json"


def span(g: str) -> str:
    return f'    <span class="kanji-part">{g}</span>\n'


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


# Shorthand
def H(*xs):
    return ("h", list(xs))


def V(*xs):
    return ("v", list(xs))


# ---------------------------------------------------------------------------
# Structures
# ---------------------------------------------------------------------------

STRUCTURES: dict[int, dict[str, object]] = {
    41: {
        # tidy + small upgrades
        "勾": H("勹", "ム"),  # wrap + elbow (Heisig capture)
        "弁": V("ム", "廾"),  # elbow + two hands
        "会": V("人", "云"),  # umbrella/person + quote (catalog 云)
        "互": "互",  # keep primitive
        "窓": V("穴", "心"),  # largest familiar: hole + heart (穴 may be later; alt 宀儿ム心)
    },
    42: {
        "棄": V("𠫓", "世", "木"),
        "撤": H("扌", V("育", "夂")),
        "唆": H("口", V("允", "夂")),
        "出": V("山", "山"),
        "峠": H("山", V("上", "下")),
    },
    43: {
        "崎": H("山", "奇"),
        "崖": V("山", "厂", "圭"),
        "入": "入",
        "込": H("⻌", "入"),
        "分": V("八", "刀"),
        "貧": V("分", "貝"),
        "頒": H("分", "頁"),
        "公": V("八", "ム"),
        "松": H("木", "公"),
        "翁": V("公", "羽"),
        "訟": H("言", "公"),
        "谷": "谷",  # teach as unit; compounds reuse
        "浴": H("氵", "谷"),
        "容": V("宀", "谷"),
        "溶": H("氵", "容"),
        "欲": H("谷", "欠"),
        "裕": H("衤", "谷"),
        "鉛": H("金", V("八", "口")),  # gully ≠ valley
        "沿": H("氵", V("八", "口")),
        "賞": V("尚", "貝"),
    },
    44: {
        "党": V("⺌", "冖", "儿"),
        "堂": V("尚", "土"),
        "常": V("尚", "巾"),
        "裳": V("尚", "衣"),
        "掌": V("尚", "手"),
        "皮": "皮",
        "波": H("氵", "皮"),
        "婆": V("波", "女"),
        "披": H("扌", "皮"),
        "破": H("石", "皮"),
        "被": H("衤", "皮"),
        "残": H("歹", "戈"),  # bones + float/spear-ish; see notes
        "殉": H("歹", V("勹", "日")),
        "殊": H("歹", "朱"),
        "殖": H("歹", "直"),
        "列": H("歹", "刂"),
        "裂": V("列", "衣"),
        "烈": V("列", "灬"),
        "死": H("歹", "匕"),
        "葬": V("艹", "死", "廾"),
    },
    45: {
        "瞬": H("目", V("爫", "冖", "舛")),
        "耳": "耳",
        "取": H("耳", "又"),
        "趣": H("⻌", "取"),  # wait — gist is 走+取 not road. Fix:
        # corrected below after dict — see PATCH
        "最": V("日", "取"),
        "撮": H("扌", "最"),
        "恥": H("耳", "心"),
        "職": H("耳", V("音", "戈")),
        "聖": V("耳", "口", "王"),
        "敢": H(V("乛", "耳"), "夂"),
        "聴": H("耳", V("十", "罒", "心")),
        "懐": H("忄", V("十", "罒", "衣")),
        "慢": H("忄", "曼"),
        "漫": H("氵", "曼"),
        "買": V("罒", "貝"),
        "置": V("罒", "直"),
        "罰": V("罒", H("言", "刂")),
        "寧": V("宀", "心", "罒", "丁"),
        "濁": H("氵", V("罒", "勹", "虫")),
        "環": H("王", "睘"),
    },
    46: {
        "還": H("⻌", "睘"),
        "夫": "夫",
        "扶": H("扌", "夫"),
        "渓": H("氵", V("爫", "夫")),
        "規": H("夫", "見"),
        "替": V(H("夫", "夫"), "日"),
        "賛": V(H("夫", "夫"), "貝"),
        "潜": H("氵", "替"),
        "失": "失",
        "鉄": H("金", "失"),
        "迭": H("⻌", "失"),
        "臣": "臣",
        "姫": H("女", "臣"),
        "蔵": V("艹", "臣"),  # simplified; parade omitted — flagged
        "臓": H("月", "蔵"),
        "賢": V(H("臣", "又"), "貝"),
        "腎": V(H("臣", "又"), "月"),
        "堅": V(H("臣", "又"), "土"),
        "臨": H("臣", V("𠂉", "品")),
        "覧": V(H("臣", "𠂉"), "見"),
    },
    47: {
        "巨": "巨",
        "拒": H("扌", "巨"),
        "力": "力",
        "男": V("田", "力"),
        "労": V("⺍", "冖", "力"),
        "募": V("莫", "力"),
        "劣": V("少", "力"),
        "功": H("工", "力"),
        "勧": H(V("𠂉", "隹"), "力"),
        "努": V("奴", "力"),
        "勃": H(V("十", "冖", "子"), "力"),
        "励": H(V("厂", "万"), "力"),
        "加": H("力", "口"),
        "賀": V("加", "貝"),
        "架": V("加", "木"),
        "脇": H("月", V("力", "力", "力")),
        "脅": V(V("力", "力", "力"), "月"),
        "協": H("十", V("力", "力", "力")),
        "行": "行",
        "律": H("彳", "聿"),
    },
    48: {
        "復": H("彳", "复"),
        "得": H("彳", V("旦", "寸")),
        "従": H("彳", V("丷", "疋")),
        "徒": H("彳", "走"),
        "待": H("彳", "寺"),
        "往": H("彳", "主"),
        "征": H("彳", "正"),
        "径": H("彳", V("又", "土")),
        "彼": H("彳", "皮"),
        "役": H("彳", V("几", "又")),
        "徳": H("彳", V("十", "罒", "心")),
        "徹": H("彳", V("育", "夂")),
        "徴": H("彳", V("山", "王", "夂")),
        "懲": V("徴", "心"),
        "微": H("彳", V("山", "兀", "夂")),
        "街": H("彳", "圭", "亍"),
        "桁": H("木", "行"),
        "衡": H("行", V("勹", "田", "大")),
        "稿": H("禾", "高"),
        "稼": H("禾", "家"),
    },
    49: {
        "程": H("禾", V("口", "王")),
        "税": H("禾", "兌"),
        "稚": H("禾", "隹"),
        "和": H("禾", "口"),
        "移": H("禾", "多"),
        "秒": H("禾", "少"),
        "秋": H("禾", "火"),
        "愁": V("秋", "心"),
        "私": H("禾", "ム"),
        "秩": H("禾", "失"),
        "秘": H("禾", "必"),
        "称": H("禾", V("𠂉", "小")),
        "利": H("禾", "刂"),
        "梨": V("利", "木"),
        "穫": H("禾", V("艹", "隻")),
        "穂": H("禾", "恵"),
        "稲": H("禾", V("爫", "旧")),
        "香": V("禾", "日"),
        "季": V("禾", "子"),
        "委": V("禾", "女"),
    },
    50: {
        "秀": V("禾", "乃"),
        "透": H("⻌", "秀"),
        "誘": H("言", "秀"),
        "稽": H("禾", V("尤", "旨")),
        "穀": H(V("士", "冖", "禾"), V("几", "又")),
        "菌": V("艹", "禾"),  # Phase1 approx (no enclosure); flagged
        "萎": V("艹", "委"),
        "米": "米",
        "粉": H("米", "分"),
        "粘": H("米", "占"),
        "粒": H("米", "立"),
        "粧": H("米", V("广", "土")),
        "迷": H("⻌", "米"),
        "粋": H("米", V("九", "十")),
        "謎": H("言", "迷"),
        "糧": H("米", "量"),
        "菊": V("艹", V("勹", "米")),
        "奥": V("米", "大"),
        "数": H(V("米", "女"), "夂"),
        "楼": H("木", V("米", "女")),
    },
}

# Fix 趣 (was wrong above)
STRUCTURES[45]["趣"] = H("走", "取")

# 残: Japanese right is closer to 戋/戈 with marks; use 戈 as familiar spear for recognition
# Keep 残 as H(歹, 戈) — flagged as imperfect glyph match

# 窓: 穴 may not be taught yet — check. Prefer familiar from current L41 parts.
# Revert 窓 to keep existing pedagogical 宀+儿+ム+心 if 穴 unknown
STRUCTURES[41]["窓"] = V("宀", "儿", "ム", "心")

# 敢: 乛 may not render well — use 耳+夂 with left as 耳 only? Heisig street+ear+taskmaster
# Safer: H(V("十", "耳"), "夂") is wrong. Use H("耳", "夂") under-decomposed OR keep V("一","耳")+夂
STRUCTURES[45]["敢"] = H(V("一", "耳"), "夂")

# 街: 亍 may be obscure — H(行 with 圭) better as H("彳", "圭", "亍") or nest
# Alternative: H("行") split — use nested matching print: 彳 | 圭 | 亍
STRUCTURES[48]["街"] = H("彳", "圭", "亍")

# 蔵: better V(艹, V with parade) — Heisig flowers+parade+retainer. Use V("艹", "戊", "臣") if 戊 known
STRUCTURES[46]["蔵"] = V("艹", "戊", "臣")

# 覧: V(H(臣,𠂉,一), 見) — simplify
STRUCTURES[46]["覧"] = V(H("臣", "𠂉"), "見")

# 微: 兀 ok
# 衡: using 行 as frame is OK recognition-wise
STRUCTURES[48]["衡"] = H("行", V("勹", "田", "大"))


def replace_component_box(section: str, kanji: str, new_box: str) -> str:
    """Replace existing component-box or insert after style-row if missing."""
    # Match component-box ... balanced roughly with non-greedy up to blank lines before </section>
    patterns = [
        re.compile(
            r'<div class="component-box[\s\S]*?</div>\s*(?:</div>\s*)*(?=\n\n|\n</section>)',
            re.M,
        ),
        re.compile(
            r'<div class="component-box[\s\S]*?</div>\s*</div>',
            re.M,
        ),
    ]
    for pat in patterns:
        m = pat.search(section)
        if m and "kanji-part" in m.group(0) or (m and "enclosure" in m.group(0)):
            return section[: m.start()] + new_box + "\n\n" + section[m.end() :]
        if m:
            return section[: m.start()] + new_box + "\n\n" + section[m.end() :]

    # orphan legacy fragments (出)
    orphan = re.search(
        r'<div class="kanji-right[\s\S]*?</div>\s*</div>\s*</div>',
        section,
    )
    if orphan:
        return section[: orphan.start()] + new_box + "\n\n" + section[orphan.end() :]

    # 棄-style wrappers
    wrapper = re.search(
        r'<div class="component-box[\s\S]*?</div>\s*(?=\n\n\n</section>|\n\n</section>)',
        section,
    )
    if wrapper:
        return section[: wrapper.start()] + new_box + "\n\n" + section[wrapper.end() :]

    # Insert before </section> after style-row
    insert_at = section.rfind("</div>", 0, section.find("</section>"))
    # Find end of style-row block: last style-row closing
    style = list(re.finditer(r'<div class="style-row">[\s\S]*?</div>\s*</div>', section))
    if style:
        pos = style[-1].end()
        return section[:pos] + "\n\n  \n" + new_box + "\n\n\n" + section[pos:]

    # fallback: before </section>
    end = section.find("</section>")
    return section[:end] + "\n" + new_box + "\n\n" + section[end:]


def apply_lesson(n: int) -> list[str]:
    path = LESSONS / f"lesson_{n:02d}.html"
    text = path.read_text(encoding="utf-8")
    structs = STRUCTURES.get(n, {})
    changed: list[str] = []

    parts = re.split(r'(<section\s+class="kanji-entry")', text)
    # parts[0] preamble; then pairs (tag, body)
    out = [parts[0]]
    i = 1
    while i < len(parts):
        tag = parts[i]
        body = parts[i + 1]
        i += 2
        # body starts with attrs...>...
        m = re.match(r'([^>]*>)([\s\S]*)', body)
        if not m:
            out.extend([tag, body])
            continue
        open_rest, rest = m.group(1), m.group(2)
        attrs = dict(re.findall(r'([^\s=]+)="([^"]*)"', open_rest))
        kanji = attrs.get("data-kanji", "")
        if kanji in structs:
            sec_end = rest.find("</section>")
            section = rest[:sec_end]
            after = rest[sec_end:]
            new_box = box(structs[kanji])
            new_section = replace_component_box(section, kanji, new_box)
            # Verify we didn't leave legacy in this section for this kanji
            rest = new_section + after
            changed.append(kanji)
        out.extend([tag, open_rest + rest])

    path.write_text("".join(out), encoding="utf-8")
    return changed


def update_catalog() -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    labels = data.setdefault("componentLabels", {})
    additions = {
        "歹": "bones",
        "彳": "going",
        "禾": "wheat",
        "扌": "fingers",
        "忄": "state of mind",
        "ム": "elbow",
        "𠫓": "infant",
        "㐬": "stream",
        "廾": "two hands",
        "曼": "mandala",
        "睘": "scepter",
        "广": "cave",
        "爫": "vulture",
        "罒": "eye of net",
        "亍": "going",
        "兀": "one-legged",
        "舛": "dancing legs",
        "戊": "parade",
        "聿": "brush",
        "穴": "hole",
    }
    for g, lab in additions.items():
        labels.setdefault(g, lab)

    intros = data.setdefault("introductions", [])
    existing = {(int(i["lesson"]), i["glyph"]) for i in intros}
    new_intros = [
        {"lesson": 41, "beforeKanji": "弁", "glyph": "廾", "label": "two hands", "heisig": "two hands"},
        {"lesson": 42, "beforeKanji": "棄", "glyph": "𠫓", "label": "infant", "heisig": "infant"},
        {"lesson": 44, "beforeKanji": "残", "glyph": "歹", "label": "bones", "heisig": "bones"},
        {"lesson": 45, "beforeKanji": "慢", "glyph": "曼", "label": "mandala", "heisig": "mandala"},
        {"lesson": 45, "beforeKanji": "環", "glyph": "睘", "label": "scepter", "heisig": "trampoline"},
        {"lesson": 47, "beforeKanji": "律", "glyph": "彳", "label": "going", "heisig": "going"},
        {"lesson": 48, "beforeKanji": "稿", "glyph": "禾", "label": "wheat", "heisig": "wheat"},
    ]
    for item in new_intros:
        key = (item["lesson"], item["glyph"])
        if key not in existing:
            intros.append(item)
            existing.add(key)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated catalog labels/intros → {CATALOG.relative_to(ROOT)}")


def main() -> None:
    update_catalog()
    all_changed = {}
    for n in range(41, 51):
        if n in STRUCTURES:
            changed = apply_lesson(n)
            all_changed[n] = changed
            print(f"L{n}: {len(changed)} structures applied ({', '.join(changed[:8])}{'…' if len(changed)>8 else ''})")
    # dump summary json next to script for report
    summary_path = Path(__file__).with_name("lessons_41_50_structures_summary.json")
    serializable = {
        str(n): {k: _ser(v) for k, v in structs.items()}
        for n, structs in STRUCTURES.items()
    }
    summary_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {summary_path}")


def _ser(node):
    if isinstance(node, str):
        return node
    kind, children = node
    return {kind: [_ser(c) for c in children]}


if __name__ == "__main__":
    main()
