#!/usr/bin/env python3
"""Build the compact kanji lookup used by KML lesson pages.

The lookup is derived from the published 漢検 lesson cards and, for characters
those cards do not include, from the KML lesson entries. It does not copy
compounds or vocabulary.

Writes kml/assets/site/data/kanji-lookup.json.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KANKEN = ROOT / "kanken"
KML_LESSONS = ROOT / "kml/contents/books/book_01/lessons"
OUT = ROOT / "kml/assets/site/data/kanji-lookup.json"

LEVEL_LABEL = {
    "level-10": "10級",
    "level-9": "9級",
    "level-8": "8級",
    "level-7": "7級",
    "level-6": "6級",
    "level-5": "5級",
    "level-4": "4級",
    "level-3": "3級",
    "level-jun2": "準2級",
    "level-2": "2級",
}

ARTICLE_RE = re.compile(r'<article class="sg-card"[^>]*>.*?(?=<article class="sg-card"|</body>)', re.S)
SECTION_RE = re.compile(r'<section class="kanji-entry"[^>]*>.*?(?=<section class="kanji-entry"|</body>)', re.S)
PANEL_RE = re.compile(
    r'<span class="sg-panel-label"[^>]*>([^<]*)</span>\s*'
    r'<span class="sg-panel-yomi"[^>]*>([^<]*)</span>',
    re.S,
)


def clean(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def record(meaning: str, on: str, kun: str, href: str, kind: str, level: str = "") -> dict:
    item = {"m": meaning, "href": href, "kind": kind}
    if on:
        item["on"] = on
    if kun:
        item["kun"] = kun
    if level:
        item["level"] = level
    return item


def kanken_entries() -> dict[str, dict]:
    found: dict[str, dict] = {}
    for path in sorted(KANKEN.glob("level-*/lesson-*.html")):
        if path.name.endswith("-readings.html"):
            continue
        level = LEVEL_LABEL.get(path.parent.name, "")
        html = path.read_text(encoding="utf-8")
        for article in ARTICLE_RE.findall(html):
            opening = article.split(">", 1)[0]
            kanji_match = re.search(r'data-kanji="([^"]+)"', opening)
            id_match = re.search(r'id="([^"]+)"', opening)
            if not kanji_match or not id_match:
                continue
            kanji = kanji_match.group(1)
            meaning_match = re.search(r'<p class="sg-meaning"[^>]*>([^<]*)</p>', article)
            ons = []
            kuns = []
            for label, yomi in PANEL_RE.findall(article):
                yomi = clean(yomi)
                if not yomi:
                    continue
                if "訓" in label:
                    kuns.append(yomi)
                elif "音" in label:
                    ons.append(yomi)
            href = "/" + path.relative_to(ROOT).as_posix() + "#" + id_match.group(1)
            item = record(
                clean(meaning_match.group(1) if meaning_match else ""),
                " ・ ".join(ons),
                " ・ ".join(kuns),
                href,
                "kanken",
                level,
            )
            previous = found.get(kanji)
            if previous and previous != item:
                raise SystemExit(f"{kanji} has two different 漢検 cards")
            found[kanji] = item
    return found


def kml_entries() -> dict[str, dict]:
    found: dict[str, dict] = {}
    for path in sorted(KML_LESSONS.glob("lesson_*.html")):
        html = path.read_text(encoding="utf-8")
        for section in SECTION_RE.findall(html):
            opening = section.split(">", 1)[0]
            kanji_match = re.search(r'data-kanji="([^"]+)"', opening)
            id_match = re.search(r'id="([^"]+)"', opening)
            if not kanji_match or not id_match:
                continue
            kanji = kanji_match.group(1)
            if kanji in found:
                continue
            meaning_match = re.search(r'<span class="kanji-keyword">([^<]*)</span>', section)
            readings_match = re.search(r'<div class="kanji-readings">\s*(.*?)\s*</div>', section, re.S)
            readings = clean(readings_match.group(1) if readings_match else "")
            on_match = re.search(r"On:\s*([^・]+)", readings)
            kun_match = re.search(r"Kun:\s*(.+)", readings)
            href = "/" + path.relative_to(ROOT).as_posix() + "#" + id_match.group(1)
            found[kanji] = record(
                clean(meaning_match.group(1) if meaning_match else ""),
                clean(on_match.group(1) if on_match else ""),
                clean(kun_match.group(1) if kun_match else ""),
                href,
                "kml",
            )
    return found


def main() -> None:
    kanken = kanken_entries()
    kml = kml_entries()
    lookup = dict(kanken)
    fallback = 0
    for kanji, item in kml.items():
        if kanji in lookup:
            continue
        lookup[kanji] = item
        fallback += 1
    ordered = {kanji: lookup[kanji] for kanji in sorted(lookup)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ordered, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    fan = ordered.get("扇")
    sample = next((k for k, item in ordered.items() if item["kind"] == "kml"), "")
    print(f"kanken {len(kanken)}")
    print(f"kml-only {fallback}")
    print(f"total {len(ordered)}")
    print("扇", json.dumps(fan, ensure_ascii=False))
    if sample:
        print("fallback", sample, json.dumps(ordered[sample], ensure_ascii=False))


if __name__ == "__main__":
    main()
