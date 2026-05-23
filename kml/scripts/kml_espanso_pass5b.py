#!/usr/bin/env python3
"""PASS 5B — Refine KML Espanso shortcuts for fast structural editing."""

from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT_YML = BASE / "data/kanji/kml_espanso_shortcuts.v2.yml"

LAYOUT_SHORTCUTS = {
    "a": "a",
    "h": "h",
    "v": "v",
    "2l": "2l",
    "2r": "2r",
    "2t": "2t",
    "2b": "2b",
    "e": "e",
    "ei": "ei",
}

WORKFLOW_SHORTCUTS = {
    "pipe": "|||",
    "csvh": "|||,,,h,,",
    "csva": "|||,,,a,,",
    "csvv": "|||,,,v,,",
}

# Curated whitelist: (group, trigger, symbol) in emission order.
SHORTCUTS: list[tuple[str, str, str]] = [
    # layout & workflow
    *(("layout & workflow", trig, repl) for trig, repl in LAYOUT_SHORTCUTS.items()),
    *(("layout & workflow", trig, repl) for trig, repl in WORKFLOW_SHORTCUTS.items()),
    # strokes & micro
    ("strokes & micro", "one", "一"),
    ("strokes & micro", "drop", "丶"),
    ("strokes & micro", "slash", "ノ"),
    ("strokes & micro", "prime", "´"),
    ("strokes & micro", "lid", "⼇"),
    ("strokes & micro", "slide", "ㇵ"),
    ("strokes & micro", "legs", "儿"),
    ("strokes & micro", "tusks", "丷"),
    ("strokes & micro", "hook", "乚"),
    ("strokes & micro", "two", "ニ"),
    # water / fire
    ("water / fire", "nami", "氵"),
    ("water / fire", "fire", "灬"),
    ("water / fire", "river", "巛"),
    # human / body
    ("human / body", "koko", "忄"),
    ("human / body", "hand", "扌"),
    ("human / body", "animal", "犭"),
    ("human / body", "winter", "夂"),
    # enclosure & frames
    ("enclosure & frames", "crown", "宀"),
    ("enclosure & frames", "cover", "冖"),
    ("enclosure & frames", "belt", "冂"),
    ("enclosure & frames", "cliff", "厂"),
    ("enclosure & frames", "table", "几"),
    ("enclosure & frames", "wrap", "勹"),
    ("enclosure & frames", "small", "⺌"),
    ("enclosure & frames", "fold", "𠂊"),
    ("enclosure & frames", "left", "𠂇"),
    ("enclosure & frames", "leftbar", "エ"),
    ("enclosure & frames", "bed", "丬"),
    ("enclosure & frames", "swift", "卂"),
    ("enclosure & frames", "level", "匀"),
    ("enclosure & frames", "full", "畐"),
    # road / movement
    ("road / movement", "walk", "辶"),
    ("road / movement", "road", "⻌"),
    # nature & modifiers
    ("nature & modifiers", "grass", "艹"),
    ("nature & modifiers", "sword", "刂"),
    # clothes family
    ("clothes family", "koromo", "𧘇"),
    ("clothes family", "cloth", "衤"),
    ("clothes family", "robe", "袁"),
    # nets & misc primitives
    ("nets & misc primitives", "net", "罒"),
    ("nets & misc primitives", "stride", "廴"),
    ("nets & misc primitives", "brush", "聿"),
    ("nets & misc primitives", "tiny", "戔"),
    # family anchors & hidden
    ("family anchors & hidden", "spear", "戈"),
    ("family anchors & hidden", "meet", "俞"),
    ("family anchors & hidden", "yu", "兪"),
    ("family anchors & hidden", "fishpipe", "田｜"),
    # structural (pipe-heavy; IME-friendly but kept for editing speed)
    ("structural components", "mouth", "口"),
    ("structural components", "thread", "糸"),
]


def yaml_quote(s: str) -> str:
    if not s:
        return '""'
    if any(c in s for c in '":\n#[]{}&,*!|>%@`'):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def main() -> None:
    used: dict[str, str] = {}
    final: list[tuple[str, str, str]] = []
    for group, base_trig, sym in SHORTCUTS:
        trig = base_trig
        if trig in used and used[trig] != sym:
            for suffix in ("2", "Alt", "V"):
                cand = f"{base_trig}{suffix}"
                if cand not in used:
                    trig = cand
                    break
        used[trig] = sym
        final.append((group, trig, sym))

    lines = [
        "# KML Espanso shortcuts v2 — PASS 5B (editor / structural typing)",
        "# Paste into Espanso config manually. Optimized for recognition + speed.",
        "# Drops ordinary IME-friendly kanji; keeps radicals, anchors, layout helpers.",
        "",
        "matches:",
    ]
    current_group = ""
    for group, trig, sym in final:
        if group != current_group:
            current_group = group
            lines.append("")
            lines.append(f"# --- {group} ---")
        lines.append(f"  - trigger: \":{trig}\"")
        lines.append(f"    replace: {yaml_quote(sym)}")

    OUT_YML.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_YML} ({len(final)} shortcuts)")


if __name__ == "__main__":
    main()
