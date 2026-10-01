#!/usr/bin/env python3
"""Scan authoritative compound curricula and report a usage index.

This is a prototype. It prints a summary. It does not write
usage_index.json and it does not build the lexical overlay.

Teaching files stay authoritative. Film JSON under
kml/tools/ambient/collections is treated as a render of those files,
so this scan does not index it. Vocabulary exhibitions are phrases,
not a compound curriculum, so they are not indexed either.

Identity is surface + reading. Pass a surface to print its appearances:

    python3 kml/data/compounds/index_compound_usage.py
    python3 kml/data/compounds/index_compound_usage.py 古寺
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMPOUNDS_HTML = ROOT / "kml/contents/books/book_01/compounds"
LESSON_JSON = Path(__file__).resolve().parent
COLLECTIONS = ROOT / "kml/tools/ambient/collections"

BLOCK_RE = re.compile(
    r'<span class="kanji-compound-font">([^<]+)</span>.*?<ul>(.*?)</ul>',
    re.DOTALL,
)
ITEM_STRONG_RE = re.compile(
    r"<li>\s*<strong>([^<]+)</strong>【([^】]+)】\s*(?:<br\s*/?>)?\s*[–-]\s*([^<]+)",
    re.IGNORECASE,
)
ITEM_PLAIN_RE = re.compile(
    r"<li>([^<【]+)【([^】]+)】\s*<br\s*/?>\s*[–-]\s*([^<]+)",
    re.IGNORECASE,
)
PLACEHOLDER = "Common compounds for this character will be added here."
KANJI_RE = re.compile(r"[\u4e00-\u9fff]")


def clean_reading(raw: str) -> str:
    text = unicodedata.normalize("NFKC", raw).strip()
    text = text.split("／")[0].split("/")[0].strip()
    return "".join(chr(ord(c) - 96) if "ァ" <= c <= "ヶ" else c for c in text)


def entry_id(surface: str, reading: str) -> str:
    return f"{surface}\t{clean_reading(reading)}"


def add(index: dict, surface: str, reading: str, appearance: dict) -> None:
    surface = unicodedata.normalize("NFKC", surface).strip()
    reading = clean_reading(reading)
    if not surface or not reading:
        return
    key = entry_id(surface, reading)
    row = index[key]
    row["surface"] = surface
    row["reading"] = reading
    row["kanji"] = KANJI_RE.findall(surface)
    row["appearances"].append(appearance)


def scan_book_html(index: dict) -> None:
    for path in sorted(COMPOUNDS_HTML.glob("lesson_*.html")):
        lesson = int(re.search(r"(\d+)", path.name).group(1))
        if (LESSON_JSON / f"lesson_{lesson}.json").is_file():
            continue
        html = path.read_text(encoding="utf-8")
        for kanji, ul in BLOCK_RE.findall(html):
            if PLACEHOLDER in ul:
                continue
            matches = ITEM_STRONG_RE.findall(ul) or ITEM_PLAIN_RE.findall(ul)
            for surface, reading, gloss in matches:
                add(
                    index,
                    surface,
                    reading,
                    {
                        "system": "book_compounds",
                        "role": "target",
                        "source": str(path.relative_to(ROOT)),
                        "lesson": lesson,
                        "anchorKanji": kanji.strip(),
                        "gloss": re.sub(r"\s+", " ", gloss).strip(" .–-"),
                    },
                )


def scan_lesson_json(index: dict) -> list[tuple[str, str, dict]]:
    pending: list[tuple[str, str, dict]] = []
    for path in sorted(LESSON_JSON.glob("lesson_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        lesson = int(data["lesson"])
        source = str(path.relative_to(ROOT))
        for character in data.get("characters", []):
            anchor = character.get("kanji", "")
            for compound in character.get("compounds", []):
                add(
                    index,
                    compound["surface"],
                    compound["reading"],
                    {
                        "system": "book_compounds",
                        "role": "target",
                        "source": source,
                        "lesson": lesson,
                        "anchorKanji": anchor,
                        "gloss": compound.get("meaning", ""),
                        "sentenceRef": compound.get("id", ""),
                    },
                )
                target = compound["surface"]
                for segment in compound.get("example", {}).get("segments", []):
                    text = segment.get("text", "")
                    seg_reading = segment.get("reading")
                    if not seg_reading or text == target or not KANJI_RE.search(text):
                        continue
                    pending.append(
                        (
                            text,
                            seg_reading,
                            {
                                "system": "book_compounds",
                                "role": "incidental",
                                "source": source,
                                "lesson": lesson,
                                "sentenceRef": compound.get("id", ""),
                            },
                        )
                    )
    return pending


def apply_incidental(index: dict, pending: list[tuple[str, str, dict]]) -> None:
    # A ruby span is often one kanji inside a longer word (上/あ inside 上がり).
    # Count it only when that surface and reading are already a taught word.
    for surface, reading, appearance in pending:
        key = entry_id(surface, reading)
        if key not in index:
            continue
        index[key]["appearances"].append(appearance)


def scan_jukugo_file(index: dict, path: Path, system: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return
    source = str(path.relative_to(ROOT))

    def take(surface: str, reading: str, anchor: str = "", gloss: str = "") -> None:
        add(
            index,
            surface,
            reading,
            {
                "system": system,
                "role": "target",
                "source": source,
                "anchorKanji": anchor,
                "gloss": gloss,
            },
        )

    entries = data.get("entries")
    if isinstance(entries, list):
        for item in entries:
            if isinstance(item, dict) and item.get("anchor") and item.get("reading"):
                take(item["anchor"], item["reading"], item.get("kanji", ""), item.get("en", ""))
    jukugo = data.get("jukugo")
    if isinstance(jukugo, dict):
        for rows in jukugo.values():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if isinstance(row, list) and len(row) >= 3:
                    take(str(row[1]), str(row[2]), str(row[0]))
    for part in data.get("parts") or []:
        if not isinstance(part, dict):
            continue
        for item in part.get("entries") or []:
            if isinstance(item, dict) and item.get("jukugo") and item.get("reading"):
                take(item["jukugo"], item["reading"], item.get("kanji", ""), item.get("en", ""))


def scan_jukugo_lists(index: dict) -> None:
    mapping = {
        "grade_jukugo": COLLECTIONS.glob("grade_*/grade_*jukugo*.json"),
        "post_elementary_jukugo": COLLECTIONS.glob("post_elementary/*jukugo*.json"),
        "beyond_joyo_jukugo": COLLECTIONS.glob("beyond_joyo/*jukugo*.json"),
    }
    for system, paths in mapping.items():
        for path in paths:
            if path.suffix != ".json":
                continue
            scan_jukugo_file(index, path, system)


def summarize(index: dict) -> None:
    by_system: dict[str, int] = defaultdict(int)
    by_role: dict[str, int] = defaultdict(int)
    surfaces: dict[str, set[str]] = defaultdict(set)
    for row in index.values():
        surfaces[row["surface"]].add(row["reading"])
        for appearance in row["appearances"]:
            by_system[appearance["system"]] += 1
            by_role[appearance["role"]] += 1
    homographs = {s: readings for s, readings in surfaces.items() if len(readings) > 1}
    print(f"entries {len(index)}")
    print(f"appearances {sum(by_system.values())}")
    print("by system:")
    for name, count in sorted(by_system.items()):
        print(f"  {name} {count}")
    print("by role:")
    for name, count in sorted(by_role.items()):
        print(f"  {name} {count}")
    print(f"same surface, different readings {len(homographs)}")


def show(index: dict, surface: str) -> None:
    found = [row for row in index.values() if row["surface"] == surface]
    if not found:
        print(f"no entry for {surface}")
        return
    for row in found:
        print(f"{row['surface']} [{row['reading']}] kanji={''.join(row['kanji'])}")
        for appearance in row["appearances"]:
            where = appearance.get("source", "")
            lesson = appearance.get("lesson", "")
            role = appearance["role"]
            system = appearance["system"]
            gloss = appearance.get("gloss", "")
            print(f"  {role:11} {system:24} lesson={lesson} {where} {gloss}")


def scan_selection(index: dict) -> None:
    """Lessons 43–100 vocabulary selection. No example sentences yet."""
    folder = LESSON_JSON / "selection"
    if not folder.is_dir():
        return
    for path in sorted(folder.glob("lesson_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        lesson = int(data["lesson"])
        if (LESSON_JSON / f"lesson_{lesson:02d}.json").is_file():
            continue
        source = str(path.relative_to(ROOT))
        for character in data.get("characters", []):
            anchor = character.get("kanji", "")
            for compound in character.get("compounds", []):
                add(
                    index,
                    compound["surface"],
                    compound["reading"],
                    {
                        "system": "book_compounds",
                        "role": "target",
                        "source": source,
                        "lesson": lesson,
                        "anchorKanji": anchor,
                        "gloss": compound.get("meaning", ""),
                    },
                )


def write_index(index: dict) -> None:
    entries = []
    for key in sorted(index):
        row = index[key]
        entries.append(
            {
                "id": f"{row['surface']}/{row['reading']}",
                "surface": row["surface"],
                "reading": row["reading"],
                "kanji": row.get("kanji") or [],
                "appearances": row["appearances"],
            }
        )
    out = {
        "schema": "kml.compounds.usage_index.v1",
        "scanner": "kml/data/compounds/index_compound_usage.py",
        "filmsExcluded": True,
        "entryCount": len(entries),
        "appearanceCount": sum(len(e["appearances"]) for e in entries),
        "entries": entries,
    }
    path = LESSON_JSON / "usage_index.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote", path.relative_to(ROOT), "entries", out["entryCount"], "appearances", out["appearanceCount"])


def main() -> None:
    index: dict[str, dict] = defaultdict(lambda: {"appearances": []})
    scan_book_html(index)
    pending = scan_lesson_json(index)
    scan_jukugo_lists(index)
    apply_incidental(index, pending)
    scan_selection(index)
    if len(sys.argv) > 1:
        show(index, sys.argv[1])
        return
    summarize(index)
    write_index(index)


if __name__ == "__main__":
    main()
