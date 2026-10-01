#!/usr/bin/env python3
"""Resolve the 11 L1–10 lexical REVIEW items. Does not regenerate the corpus."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from _build_lessons_01_10 import ruby_segments

HERE = Path(__file__).resolve().parent
REMOVED: list[dict] = []


def load(n: int) -> dict:
    return json.loads((HERE / f"lesson_{n:02d}.json").read_text(encoding="utf-8"))


def save(n: int, data: dict) -> None:
    (HERE / f"lesson_{n:02d}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def find(data: dict, kanji: str, surface: str) -> tuple[list, int, dict]:
    for ch in data["characters"]:
        if ch["kanji"] != kanji:
            continue
        for i, c in enumerate(ch["compounds"]):
            if c["surface"] == surface:
                return ch["compounds"], i, c
    raise KeyError(f"{kanji}/{surface}")


def remove(n: int, kanji: str, surface: str, classification: str, cause: str, decision: str) -> None:
    data = load(n)
    compounds, i, c = find(data, kanji, surface)
    REMOVED.append(
        {
            "lesson": n,
            "anchorKanji": kanji,
            "classification": classification,
            "cause": cause,
            "decision": decision,
            "record": {
                "id": c.get("id"),
                "surface": c["surface"],
                "reading": c["reading"],
                "meaning": c["meaning"],
                "sourceGloss": c.get("sourceGloss", ""),
            },
        }
    )
    compounds.pop(i)
    save(n, data)
    print("removed", n, surface)


def main() -> int:
    # 晶: intentional given-name entry in the legacy HTML
    data = load(2)
    _, _, c = find(data, "晶", "晶")
    c["meaning"] = "Akira (given name)"
    c["kind"] = "name"
    c["sourceGloss"] = "(used as a given name, kunyomi reading)"
    c.pop("qa", None)
    save(2, data)
    print("named 晶")

    # 背筋（脊呂） → 背筋
    data = load(2)
    _, _, c = find(data, "呂", "背筋（脊呂）")
    c["id"] = "l02_背筋"
    c["surface"] = "背筋"
    c["reading"] = "せすじ"
    c["meaning"] = "spine; back muscles"
    c["sourceGloss"] = "Spinal column (compound use of 呂 component)"
    c["example"]["ja"] = "運動のあと、背筋を伸ばします。"
    c["example"]["en"] = "After exercise, I stretch my back."
    c["example"]["segments"] = ruby_segments(c["example"]["ja"], "背筋", "せすじ")
    c["qa"] = {
        "legacySurface": "背筋（脊呂）",
        "migrationNote": "（脊呂） was a teaching note tying the 呂 component to 脊, not part of the word.",
    }
    save(2, data)
    print("corrected 背筋")

    # 少女如 → 少女の如く
    data = load(6)
    _, _, c = find(data, "如", "少女如")
    c["id"] = "l06_少女の如く"
    c["surface"] = "少女の如く"
    c["reading"] = "しょうじょのごとく"
    c["meaning"] = "like a young girl"
    c["sourceGloss"] = "Like a young girl (poetic/formal)"
    c["example"]["ja"] = "彼女は少女の如く踊ります。"
    c["example"]["en"] = "She dances like a young girl."
    c["example"]["segments"] = ruby_segments(c["example"]["ja"], "少女の如く", "しょうじょのごとく")
    c["qa"] = {
        "grammarException": True,
        "reason": "如く is literary; the listed reading already included のごとく.",
        "legacySurface": "少女如",
        "migrationNote": "Surface omitted の; the reading was already しょうじょのごとく.",
    }
    save(6, data)
    print("corrected 少女の如く")

    # 守る gloss only
    data = load(10)
    _, _, c = find(data, "守", "守る")
    c["meaning"] = "to protect; to keep"
    c["sourceGloss"] = "To protect, to守 keep (a promise, law, etc.)"
    c.pop("qa", None)
    save(10, data)
    print("gloss 守る")

    remove(
        1,
        "吾",
        "自吾",
        "NON_LEXICAL",
        "Legacy HTML: Oneself (archaic or poetic usage) under 吾. "
        "The real word 自我 / じが is taught under 我 in Lesson 35. "
        "じご is an onyomi concatenation of 自+吾, not a reconstructible misspelling of 自我.",
        "Removed. Do not replace with 自我 in the 吾 block.",
    )
    remove(
        2,
        "晶",
        "発光晶体",
        "NON_LEXICAL",
        "Legacy HTML: Luminescent crystal (Onyomi compound). "
        "晶体 is Chinese for crystal; Japanese is 結晶 (already the previous entry). "
        "Reading しょうたい matches 晶体, not けっしょう, so this is not a misspelling of 発光結晶.",
        "Removed. Not rewritten as 発光結晶.",
    )
    remove(
        2,
        "昌",
        "昌市",
        "NON_LEXICAL",
        "Legacy HTML: Prosperous city (rare compound). "
        "Sibling 昌 / 昌子 / 昌平 are labeled as names; 昌市 is not. "
        "The name 昌市 would normally be しょういち, not しょうし.",
        "Removed. Not treated as a place or personal name.",
    )
    remove(
        2,
        "亘",
        "年亘",
        "NON_LEXICAL",
        "Legacy HTML: Over the years (compound with time context). "
        "Sibling entries already include 長年に亘り and 全国に亘る. "
        "ねんこう is an invented onyomi compound, not a scrape of those phrases.",
        "Removed.",
    )
    remove(
        3,
        "舌",
        "早口舌",
        "NON_LEXICAL",
        "Legacy HTML concatenates 早口 (already Lesson 2) with the lesson kanji 舌. "
        "The real word is 早口 or 早口言葉, neither of which is this surface.",
        "Removed.",
    )
    remove(
        3,
        "舌",
        "甘舌",
        "NON_LEXICAL",
        "Legacy HTML: Sweet tongue (sweet talker), analog of 毒舌. "
        "Not 甘言 (かんげん). Reading あまじた does not support reconstructing 甘言.",
        "Removed.",
    )
    remove(
        6,
        "如",
        "権利如",
        "NON_LEXICAL",
        "Legacy HTML: As in the case of rights (legal usage), reading けんりにょ. "
        "Unlike 少女如, the reading is not のごとく, so this is not a missing-の form of 権利の如く.",
        "Removed. Not rewritten as 権利の如く.",
    )

    # Do not let 甘舌 survive in later selection as a compounds-book identity.
    sel_path = HERE / "selection" / "lesson_95.json"
    sel = json.loads(sel_path.read_text(encoding="utf-8"))
    for ch in sel["characters"]:
        if ch.get("kanji") != "甘":
            continue
        before = len(ch["compounds"])
        ch["compounds"] = [x for x in ch["compounds"] if x.get("surface") != "甘舌"]
        print("L95 甘舌 removed", before, "->", len(ch["compounds"]))
    sel_path.write_text(json.dumps(sel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "removed": REMOVED,
        "holes": [
            {"lesson": 1, "kanji": "吾", "remaining": 5, "removed": ["自吾"]},
            {"lesson": 2, "kanji": "晶", "remaining": 5, "removed": ["発光晶体"]},
            {"lesson": 2, "kanji": "昌", "remaining": 5, "removed": ["昌市"]},
            {"lesson": 2, "kanji": "亘", "remaining": 5, "removed": ["年亘"]},
            {
                "lesson": 3,
                "kanji": "舌",
                "remaining": 4,
                "removed": ["早口舌", "甘舌"],
                "note": "Largest hole. Original block had six items.",
            },
            {"lesson": 6, "kanji": "如", "remaining": 3, "removed": ["権利如"], "corrected": ["少女の如く"]},
            {
                "lesson": 95,
                "kanji": "甘",
                "note": "甘舌 dropped from later selection so the malformed identity does not recur. Replacement not chosen.",
            },
        ],
    }
    (HERE / "_lexical_review_l01_10.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote _lexical_review_l01_10.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
