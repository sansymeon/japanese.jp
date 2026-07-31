#!/usr/bin/env python3
"""Build the master KML component database from lesson HTML.

Policy
------
- Lesson HTML is the canonical source for decompositions and layouts.
- Do not rewrite or "fix" HTML editorial decisions.
- Report inconsistencies.
- Use v4c only when a decomposition is completely absent from HTML.

Outputs
-------
  data/kanji/kml_component_database.json
  data/kanji/kml_component_database_report.md

Usage
-----
  python3 scripts/build_kml_component_database.py
  python3 scripts/build_kml_component_database.py --max-lesson 35
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from lib.html_component_parser import (  # noqa: E402
    parse_lesson_html,
)

LESSONS_DIR = BASE / "contents" / "books" / "book_01" / "lessons"
V4C = BASE / "data" / "kanji" / "kanji_master_with_components.v4c.csv"
OUT_JSON = BASE / "data" / "kanji" / "kml_component_database.json"
OUT_REPORT = BASE / "data" / "kanji" / "kml_component_database_report.md"


def discover_lessons(max_lesson: int | None) -> list[tuple[int, Path]]:
    found: list[tuple[int, Path]] = []
    for p in LESSONS_DIR.glob("lesson_*.html"):
        try:
            n = int(p.stem.split("_")[1])
        except (IndexError, ValueError):
            continue
        if max_lesson is not None and n > max_lesson:
            continue
        found.append((n, p))
    found.sort(key=lambda x: x[0])
    return found


def load_v4c() -> dict[str, dict]:
    if not V4C.exists():
        return {}
    by: dict[str, dict] = {}
    with V4C.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            k = row.get("kanji") or ""
            if not k:
                continue
            # Prefer earliest numbered lesson row when duplicates exist
            if k not in by:
                by[k] = row
            else:
                try:
                    n = int(row.get("lesson_number") or 9999)
                    old = int(by[k].get("lesson_number") or 9999)
                    if n < old:
                        by[k] = row
                except ValueError:
                    pass
    return by


def v4c_parts(row: dict) -> list[str]:
    raw = row.get("kml_primitives") or ""
    return [p for p in raw.split("|") if p]


def build(max_lesson: int | None = None) -> tuple[dict, str]:
    lessons = discover_lessons(max_lesson)
    v4c = load_v4c()

    kanji_records: dict[str, dict] = {}
    component_parents: dict[str, list[dict]] = defaultdict(list)
    inconsistencies: list[dict] = []
    stats = {
        "lessonsScanned": 0,
        "kanjiFromHtml": 0,
        "withBox": 0,
        "absentBox": 0,
        "filledFromV4c": 0,
        "stillAbsent": 0,
        "placeholderRemnants": 0,
    }

    for lesson_num, path in lessons:
        stats["lessonsScanned"] += 1
        decomps = parse_lesson_html(path, lesson_num)
        for d in decomps:
            stats["kanjiFromHtml"] += 1
            rec = d.to_dict()
            # Drop bulky raw box from DB; keep notes/tree
            rec.pop("raw_box", None)

            raw_parts = list(rec.get("partsFlat") or [])
            # Usable parts for downstream builds: drop parent self-refs
            # (placeholder remnants, not editorial intent).
            usable = [p for p in raw_parts if p and p != d.kanji]
            rec["partsFlatRaw"] = raw_parts
            rec["partsFlat"] = usable if usable else (
                raw_parts if raw_parts == [d.kanji] else []
            )
            if "placeholder_self_reference" in (d.notes or []) or (
                d.kanji in raw_parts and len(raw_parts) > 1
            ):
                rec["hasPlaceholderRemnant"] = True
                stats["placeholderRemnants"] += 1

            if d.has_box:
                stats["withBox"] += 1
            else:
                stats["absentBox"] += 1

            # v4c fallback only when HTML has no box / no parts at all
            is_anchor = raw_parts == [d.kanji]
            if (not d.has_box or not raw_parts) and not is_anchor:
                row = v4c.get(d.kanji)
                parts = v4c_parts(row) if row else []
                if parts:
                    rec["source"] = "v4c_fallback"
                    rec["partsFlat"] = parts
                    rec["layoutType"] = rec.get("layoutType") or (
                        row.get("layout_type") or ""
                    )
                    rec["notes"] = list(rec.get("notes") or []) + [
                        "filled_from_v4c_absent_html"
                    ]
                    stats["filledFromV4c"] += 1
                    inconsistencies.append(
                        {
                            "type": "absent_html_used_v4c",
                            "kanji": d.kanji,
                            "lesson": lesson_num,
                            "v4cParts": parts,
                        }
                    )
                else:
                    stats["stillAbsent"] += 1
                    inconsistencies.append(
                        {
                            "type": "absent_decomposition",
                            "kanji": d.kanji,
                            "lesson": lesson_num,
                            "keyword": d.keyword,
                        }
                    )

            # Compare reviewed HTML raw parts vs v4c (report only)
            if d.has_box and raw_parts and d.kanji in v4c:
                vparts = v4c_parts(v4c[d.kanji])
                if vparts and vparts != raw_parts:
                    inconsistencies.append(
                        {
                            "type": "html_v4c_mismatch",
                            "kanji": d.kanji,
                            "lesson": lesson_num,
                            "htmlParts": raw_parts,
                            "v4cParts": vparts,
                            "note": "HTML is canonical; v4c is legacy placeholder reference",
                        }
                    )

            for note in d.notes:
                inconsistencies.append(
                    {
                        "type": note,
                        "kanji": d.kanji,
                        "lesson": lesson_num,
                        "partsRaw": raw_parts,
                        "partsUsable": rec.get("partsFlat"),
                        "layoutType": d.layout_type,
                        "editorial": (
                            False
                            if note.startswith("placeholder_")
                            else None
                        ),
                    }
                )

            # Keep first lesson occurrence as canonical record; later
            # duplicates are reported.
            if d.kanji in kanji_records:
                prev = kanji_records[d.kanji]
                inconsistencies.append(
                    {
                        "type": "duplicate_kanji_entry",
                        "kanji": d.kanji,
                        "lesson": lesson_num,
                        "earlierLesson": prev.get("lesson"),
                        "parts": d.parts_flat,
                        "earlierParts": prev.get("partsFlat"),
                    }
                )
            else:
                kanji_records[d.kanji] = rec

            for part in rec.get("partsFlat") or []:
                if not part:
                    continue
                component_parents[part].append(
                    {
                        "kanji": d.kanji,
                        "lesson": lesson_num,
                        "keyword": d.keyword,
                    }
                )

    # Component index
    components: dict[str, dict] = {}
    for glyph, parents in sorted(component_parents.items(), key=lambda x: x[0]):
        # unique parents preserving order
        seen = set()
        uniq_parents = []
        for p in parents:
            if p["kanji"] in seen:
                continue
            seen.add(p["kanji"])
            uniq_parents.append(p)

        first = uniq_parents[0]
        child_parts: list[str] = []
        if glyph in kanji_records:
            child_parts = list(kanji_records[glyph].get("partsFlat") or [])
            # If the glyph's own decomposition is only itself (anchor), no children
            if child_parts == [glyph]:
                child_parts = []

        components[glyph] = {
            "glyph": glyph,
            "firstLesson": first["lesson"],
            "firstParent": first["kanji"],
            "reuseCount": len(uniq_parents),
            "parentKanji": [p["kanji"] for p in uniq_parents],
            "parentDetails": uniq_parents,
            "childComponents": child_parts,
            "isLessonKanji": glyph in kanji_records,
        }

    db = {
        "meta": {
            "title": "KML Component Database",
            "policy": (
                "Reviewed lesson HTML is the canonical source for approved KML "
                "decompositions. Original component data (including v4c) was "
                "placeholder content for scaffolding lessons and is not editorial "
                "intent. Self-reference parts are placeholder remnants. "
                "v4c is legacy: comparison/recovery only when HTML is missing. "
                "See data/kanji/KML_COMPONENT_SOURCE_POLICY.md."
            ),
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "lessonsDir": str(LESSONS_DIR.relative_to(BASE)),
            "maxLesson": max_lesson,
            "stats": stats,
            "kanjiCount": len(kanji_records),
            "componentCount": len(components),
            "inconsistencyCount": len(inconsistencies),
        },
        "kanji": kanji_records,
        "components": components,
        "inconsistencies": inconsistencies,
    }

    report = render_report(db)
    return db, report


def render_report(db: dict) -> str:
    meta = db["meta"]
    stats = meta["stats"]
    lines: list[str] = []
    lines.append("# KML Component Database Report")
    lines.append("")
    lines.append(f"Generated: `{meta['generatedAt']}`")
    lines.append("")
    lines.append("## Policy")
    lines.append("")
    lines.append(meta["policy"])
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Lessons scanned: **{stats['lessonsScanned']}**")
    lines.append(f"- Kanji entries: **{meta['kanjiCount']}**")
    lines.append(f"- Distinct component glyphs: **{meta['componentCount']}**")
    lines.append(f"- With component-box: **{stats['withBox']}**")
    lines.append(f"- Absent component-box: **{stats['absentBox']}**")
    lines.append(f"- Filled from v4c fallback: **{stats['filledFromV4c']}**")
    lines.append(f"- Still absent: **{stats['stillAbsent']}**")
    lines.append(
        f"- Placeholder remnants (self-ref, not editorial): "
        f"**{stats.get('placeholderRemnants', 0)}**"
    )
    lines.append(f"- Inconsistency records: **{meta['inconsistencyCount']}**")
    lines.append("")
    lines.append(
        "Placeholder self-references are **not** approved decompositions — "
        "they are leftover scaffolding from the original placeholder dataset."
    )
    lines.append("")

    by_type: dict[str, list] = defaultdict(list)
    for item in db["inconsistencies"]:
        by_type[item["type"]].append(item)

    lines.append("## Inconsistencies (report only — HTML not changed)")
    lines.append("")
    for t in sorted(by_type.keys()):
        items = by_type[t]
        lines.append(f"### `{t}` ({len(items)})")
        lines.append("")
        for item in items[:80]:
            k = item.get("kanji", "?")
            lesson = item.get("lesson", "?")
            extra = ""
            if "htmlParts" in item:
                extra = f" html={item['htmlParts']} v4c={item['v4cParts']}"
            elif "parts" in item:
                extra = f" parts={item['parts']}"
            elif "v4cParts" in item:
                extra = f" v4c={item['v4cParts']}"
            lines.append(f"- L{lesson} {k}{extra}")
        if len(items) > 80:
            lines.append(f"- … {len(items) - 80} more")
        lines.append("")

    # Top reused components
    comps = sorted(
        db["components"].values(),
        key=lambda c: (-c["reuseCount"], c["firstLesson"], c["glyph"]),
    )
    lines.append("## Top reused components")
    lines.append("")
    lines.append("| Glyph | First lesson | Reuse | First parent | Children |")
    lines.append("|-------|-------------:|------:|--------------|----------|")
    for c in comps[:40]:
        children = " ".join(c["childComponents"]) if c["childComponents"] else "—"
        lines.append(
            f"| {c['glyph']} | {c['firstLesson']} | {c['reuseCount']} | "
            f"{c['firstParent']} | {children} |"
        )
    lines.append("")

    # Single-use components (possible intro noise)
    singles = [c for c in comps if c["reuseCount"] == 1 and not c["isLessonKanji"]]
    lines.append(f"## Single-use non-kanji components ({len(singles)})")
    lines.append("")
    for c in singles[:60]:
        lines.append(
            f"- {c['glyph']} — L{c['firstLesson']} in {c['firstParent']}"
        )
    if len(singles) > 60:
        lines.append(f"- … {len(singles) - 60} more")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--max-lesson",
        type=int,
        default=None,
        help="Only scan lessons 1..N (default: all lesson_XX.html)",
    )
    args = ap.parse_args()

    db, report = build(args.max_lesson)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(db, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    OUT_REPORT.write_text(report, encoding="utf-8")

    print(f"wrote {OUT_JSON.relative_to(BASE)}")
    print(f"wrote {OUT_REPORT.relative_to(BASE)}")
    meta = db["meta"]
    stats = meta["stats"]
    print(
        f"kanji={meta['kanjiCount']} components={meta['componentCount']} "
        f"withBox={stats['withBox']} absent={stats['absentBox']} "
        f"v4cFallback={stats['filledFromV4c']} "
        f"inconsistencies={meta['inconsistencyCount']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
