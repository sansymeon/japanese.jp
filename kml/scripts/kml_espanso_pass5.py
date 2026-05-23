#!/usr/bin/env python3
"""PASS 5 — Generate kml_espanso_shortcuts.yml from KML primitive/component data."""

from __future__ import annotations

import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PRIM_CSV = BASE / "data/kanji/primitive_dictionary.csv"
KANJI_CSV = BASE / "data/kanji/kanji_master_with_components.v4.csv"
OUT_YML = BASE / "data/kanji/kml_espanso_shortcuts.yml"

# Family-oriented / memorable triggers (override keyword fallbacks).
TRIGGER_OVERRIDES: dict[str, str] = {
    # --- user examples / radicals ---
    "氵": "nami",
    "忄": "kokoro",
    "⻌": "road",
    "辶": "walk",
    "道": "michi",
    "𧘇": "koromo",
    "艹": "kusa",
    "扌": "hand",
    "宀": "kanmuri",
    "犭": "inu",
    "刂": "ritto",
    "冖": "wa",
    "冂": "madogawa",
    "灬": "rekka",
    "厂": "gan",
    "衤": "koromesc",
    "礻": "shimesu",  # not in primitive dict; common extra
    "⺌": "shao",
    "⼇": "nabe",
    "ㇵ": "hane",
    "𠂊": "legs2",
    "𠂇": "hidari",
    "丷": "hachi",
    "乚": "kane",
    "勹": "tsutsumi",
    "几": "tsukue",
    "卂": "nobori",
    "巛": "kawa",
    "丬": "shou",
    "ニ": "nikkei",
    "´": "accent",
    "田｜": "fishpipe",
    "夂": "winter",
    "戈": "halberd",
    "俞": "yu",
    "袁": "robe",
    "兪": "yu2",
    "戔": "sen",
    "疋": "shitaji",
    "廴": "innyou",
    "聿": "fude",
    "罒": "ami",
    "匀": "kin",
    "エ": "eleft",
    "丶": "dot",
    "ノ": "no",
    "儿": "legs",
    # --- extras used in v4 but absent from primitive_dictionary ---
    "三": "san",
    "忄": "kokoro",
    "扌": "hand",
    "⻌": "road",
}

# Radicals / tokens used in KML but not listed in primitive_dictionary.csv.
EXTRA_SYMBOLS = ["三", "忄", "扌", "⻌"]

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

STRUCTURE_SHORTCUTS = {
    "bar": "|",
}


def sanitize_trigger(name: str) -> str:
    s = (name or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s[:20]


def yaml_quote(s: str) -> str:
    if not s:
        return '""'
    if any(c in s for c in '":\n#[]{}&,*!|>%@`'):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def load_kanji_keywords() -> dict[str, str]:
    keywords: dict[str, str] = {}
    with open(KANJI_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            k = (row.get("kanji") or "").strip()
            kw = (row.get("keyword") or "").strip()
            if k and kw and k not in keywords:
                keywords[k] = kw
    return keywords


def pick_trigger(
    symbol: str,
    preferred: str,
    first_kanji: str,
    status: str,
    keywords: dict[str, str],
) -> str:
    if symbol in TRIGGER_OVERRIDES:
        return TRIGGER_OVERRIDES[symbol]
    if preferred:
        return sanitize_trigger(preferred)
    if symbol in keywords:
        return sanitize_trigger(keywords[symbol])
    if first_kanji and first_kanji in keywords:
        fk = sanitize_trigger(keywords[first_kanji])
        if status in ("hidden_component", "primitive_only"):
            return fk + "p" if fk else ""
        return fk
    return sanitize_trigger(symbol) or f"u{ord(symbol[0]):04x}"


def reserve_trigger(base: str, used: dict[str, str]) -> str:
    if not base:
        base = "x"
    if base not in used:
        return base
    n = 2
    while f"{base}{n}" in used:
        n += 1
    return f"{base}{n}"


def main() -> None:
    keywords = load_kanji_keywords()
    entries: list[tuple[str, str, str]] = []  # (section, trigger, replace)

    for label, mapping in (
        ("layout", LAYOUT_SHORTCUTS),
        ("workflow", WORKFLOW_SHORTCUTS),
        ("structure", STRUCTURE_SHORTCUTS),
    ):
        for trig, repl in mapping.items():
            entries.append((label, trig, repl))

    with open(PRIM_CSV, encoding="utf-8") as f:
        prim_rows = list(csv.DictReader(f))

    seen_symbols: set[str] = set()
    for row in prim_rows:
        sym = (row.get("symbol") or "").strip()
        if not sym:
            continue
        seen_symbols.add(sym)
        trig = pick_trigger(
            sym,
            (row.get("preferred_name") or "").strip(),
            (row.get("first_kanji") or "").strip(),
            (row.get("status") or "").strip(),
            keywords,
        )
        entries.append(("primitive", trig, sym))

    for sym in EXTRA_SYMBOLS:
        if sym not in seen_symbols:
            entries.append(
                ("primitive", pick_trigger(sym, "", "", "primitive_only", keywords), sym)
            )

    # Hidden reusables / anchors from kanji master (skip if already emitted).
    with open(KANJI_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            notes = (row.get("notes") or "")
            if "hidden_reusable" not in notes:
                continue
            k = (row.get("kanji") or "").strip()
            kw = (row.get("keyword") or "").strip()
            if k and k not in seen_symbols:
                entries.append(("anchor", sanitize_trigger(kw) or k, k))

    used_triggers: dict[str, str] = {}
    final: list[tuple[str, str, str]] = []

    for section, base_trig, replace in entries:
        trig = reserve_trigger(base_trig, used_triggers)
        if trig in used_triggers and used_triggers[trig] != replace:
            trig = reserve_trigger(base_trig + "x", used_triggers)
        used_triggers[trig] = replace
        final.append((section, trig, replace))

    lines = [
        "# KML Espanso shortcuts — PASS 5 (typing acceleration only)",
        "# Paste into your Espanso config; merge manually — do not overwrite wholesale.",
        "# Source: primitive_dictionary.csv + kanji_master_with_components.v4.csv",
        "",
        "matches:",
        "",
        "# --- layout codes ---",
    ]
    section_headers = {
        "workflow": "# --- CSV / editing workflow ---",
        "structure": "# --- structure tokens ---",
        "primitive": "# --- primitives & components ---",
        "anchor": "# --- family anchors (hidden reusables) ---",
    }
    current = "layout"
    for section, trig, replace in final:
        if section != current:
            current = section
            if section in section_headers:
                lines.append("")
                lines.append(section_headers[section])
        lines.append(f"  - trigger: \":{trig}\"")
        lines.append(f"    replace: {yaml_quote(replace)}")

    OUT_YML.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_YML} ({len(final)} shortcuts)")


if __name__ == "__main__":
    main()
