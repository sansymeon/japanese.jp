#!/usr/bin/env python3
"""
PASS 9 — Expand KML Espanso shortcuts (Heisig editing-support layer).

Preserves all triggers from kml_espanso_shortcuts.v2.yml unchanged.
Adds aliases and missing hub/primitive triggers; writes v3 only.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
V2 = BASE / "data/kanji/kml_espanso_shortcuts.v2.yml"
V1 = BASE / "data/kanji/kml_espanso_shortcuts.yml"
OUT = BASE / "data/kanji/kml_espanso_shortcuts.v3.yml"
PRIM_V2 = BASE / "data/kanji/primitive_dictionary.v2.csv"
GLOSSARY = BASE / "data/kanji/glossary_family.csv"

# New triggers only (group, trigger, replace). Aliases allowed — same replace, new trigger.
ADDITIONS: list[tuple[str, str, str]] = [
    # layout & workflow (v3)
    ("layout & workflow", "3r", "3r"),
    # glossary hubs — KML + Heisig aliases
    ("glossary hubs", "beggar", "曷"),
    ("glossary hubs", "muchacho", "曷"),
    ("glossary hubs", "merchant", "啇"),
    ("glossary hubs", "shoko", "啇"),
    ("glossary hubs", "deal", "商"),
    ("glossary hubs", "trader", "商"),
    ("glossary hubs", "compete", "竟"),
    ("glossary hubs", "fin", "竟"),
    ("glossary hubs", "turbulence", "巟"),
    ("glossary hubs", "turb", "巟"),
    ("glossary hubs", "boundup", "𠔉"),
    ("glossary hubs", "jack", "𠔉"),
    # hidden reusables — Heisig aliases
    ("hidden anchors", "halberd", "戈"),
    ("hidden anchors", "yu", "俞"),
    ("hidden anchors", "tanned", "袁"),
    ("hidden anchors", "goslow", "夂"),
    ("hidden anchors", "go", "夂"),
    # human / body aliases
    ("human / body", "heart", "忄"),
    # enclosure & movement aliases
    ("enclosure & frames", "roof", "宀"),
    ("enclosure & frames", "bound", "勹"),
    ("enclosure & frames", "building", "广"),
    ("enclosure & frames", "enclosure", "囗"),
    ("water / fire", "water", "氵"),
    ("water / fire", "firedots", "灬"),
    ("road / movement", "goose", "⻌"),
    # nature & modifiers
    ("nature & modifiers", "flowers", "艹"),
    ("nets & misc primitives", "netting", "罒"),
    # difficult unicode / micro (from primitive_dictionary.v2)
    ("strokes & micro", "boundleft", "𠂇"),
    ("strokes & micro", "boundtop", "𠂊"),
    ("clothes family", "sleeve", "衤"),
    ("clothes family", "tunic", "𧘇"),
    ("structural components", "shell", "貝"),
    ("structural components", "speech", "言"),
    ("structural components", "see", "見"),
]

# Auto-add glossary anchor + high-priority hub triggers from CSV (if not already used).
AUTO_GLOSSARY_TRIGGERS = {
    "曷": ("siesta",),  # siesta already in v2
    "啇": ("merchant",),
    "商": ("deal",),
    "袁": ("robe",),
    "戈": ("spear",),
    "俞": ("meet",),
    "夂": ("winter",),
    "𧘇": ("koromo",),
    "竟": ("compete",),
}


def yaml_quote(s: str) -> str:
    if not s:
        return '""'
    if any(c in s for c in '":\n#[]{}&,*!|>%@`'):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def parse_espanso_yml(path: Path) -> list[tuple[str, str, str]]:
    """Return [(group, trigger, replace), ...] in file order."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    entries: list[tuple[str, str, str]] = []
    group = ""
    pending_trig: str | None = None
    for line in text.splitlines():
        gm = re.match(r"^#\s*---\s*(.+?)\s*---\s*$", line)
        if gm:
            group = gm.group(1).strip()
            continue
        tm = re.match(r'\s*-\s*trigger:\s*":([^"]+)"', line)
        if tm:
            pending_trig = tm.group(1)
            continue
        rm = re.match(r"\s*replace:\s*(.+)\s*$", line)
        if rm and pending_trig is not None:
            raw = rm.group(1).strip()
            if raw.startswith('"') and raw.endswith('"'):
                raw = raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
            entries.append((group or "preserved", pending_trig, raw))
            pending_trig = None
    return entries


def load_glossary_anchors() -> dict[str, str]:
    anchors: dict[str, str] = {}
    with open(GLOSSARY, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row.get("glossary_priority") or "") in ("high", "medium"):
                sym = (row.get("anchor_symbol") or "").strip()
                pref = (row.get("family_id") or "").replace("_family", "")
                if sym and pref:
                    anchors[sym] = pref
    return anchors


def main() -> None:
    preserved = parse_espanso_yml(V2)
    if not preserved:
        preserved = parse_espanso_yml(V1)

    locked_triggers = {trig for _, trig, _ in preserved}
    locked_pairs = {(trig, repl) for _, trig, repl in preserved}
    used_triggers = set(locked_triggers)
    replace_to_primary = {repl: trig for _, trig, repl in preserved}

    final: list[tuple[str, str, str]] = list(preserved)
    added = 0
    skipped = 0

    def try_add(group: str, trig: str, repl: str) -> None:
        nonlocal added, skipped
        if trig in used_triggers:
            existing = next(r for _, t, r in final if t == trig)
            if existing != repl:
                skipped += 1
            return
        if trig in locked_triggers:
            skipped += 1
            return
        # Do not steal trigger name from preserved with different replace
        for _, t, r in preserved:
            if t == trig and r != repl:
                skipped += 1
                return
        used_triggers.add(trig)
        final.append((group, trig, repl))
        added += 1

    for group, trig, repl in ADDITIONS:
        try_add(group, trig, repl)

    # Preferred names from glossary for anchors missing any trigger
    glossary = load_glossary_anchors()
    for sym, pref in sorted(glossary.items()):
        if sym not in {r for _, _, r in final} and pref not in used_triggers:
            try_add("glossary hubs", pref, sym)

    # primitive_dictionary.v2: primitive_only / hidden only
    IME_SKIP = set("口日月木水人女土火十大中小王白田目石金言")
    with open(PRIM_V2, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sym = (row.get("symbol") or "").strip()
            status = (row.get("status") or "").strip()
            pref = (row.get("preferred_name") or "").strip().replace(" ", "_")
            if not sym or not pref or status not in ("primitive_only", "hidden_component"):
                continue
            if len(sym) == 1 and sym in IME_SKIP:
                continue
            if sym in {r for _, _, r in final}:
                continue
            if pref in used_triggers:
                continue
            try_add("primitives (dictionary v2)", pref, sym)

    lines = [
        "# KML Espanso shortcuts v3 — PASS 9 (KML cognition editing layer + Heisig aliases)",
        "# Preserves ALL v2 triggers unchanged. Paste into Espanso manually; do not overwrite wholesale.",
        "# Heisig/RTK names are editor shorthand only — KML cognition remains authoritative.",
        "",
        "matches:",
    ]
    current = ""
    for group, trig, repl in final:
        if group != current:
            current = group
            lines.append("")
            lines.append(f"# --- {group} ---")
        lines.append(f'  - trigger: ":{trig}"')
        lines.append(f"    replace: {yaml_quote(repl)}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Preserved: {len(preserved)} triggers from v2")
    print(f"Added:     {added} new triggers/aliases")
    print(f"Skipped:   {skipped} (conflict with preserved)")
    print(f"Total:     {len(final)} -> {OUT}")


if __name__ == "__main__":
    main()
