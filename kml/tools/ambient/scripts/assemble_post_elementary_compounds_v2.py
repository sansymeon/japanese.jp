#!/usr/bin/env python3
"""Assemble Volume 2 jukugo list + CSV from curated batch JSON files.

Usage:
  python scripts/assemble_post_elementary_compounds_v2.py \\
    --batches /tmp/vol2_batches/vol2_batch_*.json

Validates against Volume 1, writes:
  collections/post_elementary/post_elementary_jukugo_list_v2.json
  collections/post_elementary/post_elementary_jukugo_list_v2.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = ROOT / "collections" / "post_elementary"
VOL1 = COLLECTIONS / "post_elementary_jukugo_list.json"
OUT_JSON = COLLECTIONS / "post_elementary_jukugo_list_v2.json"
OUT_CSV = COLLECTIONS / "post_elementary_jukugo_list_v2.csv"

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from compounds_ruby import ruby_compound, ruby_word  # noqa: E402


def jp_html_from_entry(e: dict) -> str:
    if e.get("jpHtml"):
        return e["jpHtml"]
    ruby = e.get("ruby")
    if ruby:
        parts = [(a, b) for a, b in ruby]
        return ruby_compound(parts)
    return ruby_word(e["anchor"], e["reading"])


def load_batches(paths: list[Path]) -> list[dict]:
    entries: list[dict] = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise SystemExit(f"{path}: expected JSON array")
        entries.extend(data)
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--batches",
        nargs="+",
        type=Path,
        required=True,
        help="Curated vol2 batch JSON files (in order)",
    )
    args = parser.parse_args()

    vol1 = json.loads(VOL1.read_text(encoding="utf-8"))
    vol1_entries = vol1["entries"]
    vol1_by_kanji = {e["kanji"]: e for e in vol1_entries}
    vol1_anchors = {e["anchor"] for e in vol1_entries}

    raw = load_batches(args.batches)
    errors: list[str] = []

    if len(raw) != len(vol1_entries):
        errors.append(f"count mismatch: vol2={len(raw)} vol1={len(vol1_entries)}")

    seen_kanji: set[str] = set()
    seen_anchors: Counter[str] = Counter()
    entries: list[dict] = []

    for i, (v1, e) in enumerate(zip(vol1_entries, raw), start=1):
        kanji = e.get("kanji")
        anchor = e.get("anchor")
        reading = e.get("reading")
        en = e.get("en")
        if kanji != v1["kanji"]:
            errors.append(
                f"order {i}: kanji mismatch vol2={kanji!r} expected={v1['kanji']!r}"
            )
        if not anchor or not reading or not en:
            errors.append(f"order {i} ({kanji}): missing anchor/reading/en")
        if kanji in seen_kanji:
            errors.append(f"duplicate kanji: {kanji}")
        seen_kanji.add(kanji)
        if kanji in vol1_by_kanji and anchor == vol1_by_kanji[kanji]["anchor"]:
            errors.append(f"{kanji}: reused Volume 1 anchor {anchor}")
        elif anchor in vol1_anchors:
            errors.append(f"{kanji}: reuses a Volume 1 compound {anchor}")
        if anchor and kanji and kanji not in str(anchor):
            errors.append(f"{kanji}: anchor {anchor!r} does not contain target kanji")
        seen_anchors[anchor] += 1

        out = {
            "kanji": kanji,
            "anchor": anchor,
            "reading": reading,
            "en": en,
            "jpHtml": jp_html_from_entry(e),
            "heisigNumber": e.get("heisigNumber", v1["heisigNumber"]),
            "slug": e.get("slug", v1.get("slug")),
            "displayOrder": e.get("displayOrder", v1["displayOrder"]),
            "volume1Anchor": v1["anchor"],
        }
        entries.append(out)

    missing = [e["kanji"] for e in vol1_entries if e["kanji"] not in seen_kanji]
    if missing:
        errors.append(f"missing {len(missing)} kanji (first: {missing[:10]})")

    dups = sorted((a, n) for a, n in seen_anchors.items() if a and n > 1)
    soft_vol1_overlap = sorted(
        a for a in seen_anchors if a in vol1_anchors and seen_anchors[a]
    )
    # Shared Vol1 unavoidable pairs may appear; warn only.
    hard_same_kanji_reuse = [
        e["kanji"]
        for e in entries
        if e["kanji"] in vol1_by_kanji
        and e["anchor"] == vol1_by_kanji[e["kanji"]]["anchor"]
    ]

    if errors:
        print("VALIDATION FAILED:")
        for err in errors[:50]:
            print(f"  - {err}")
        if len(errors) > 50:
            print(f"  … +{len(errors) - 50} more")
        return 1

    part_sizes: list[int] = []
    n = len(entries)
    part_count = (n + 49) // 50
    for p in range(part_count):
        start = p * 50
        part_sizes.append(len(entries[start : start + 50]))

    doc = {
        "type": "jukugo",
        "scope": "post_elementary_through_joyo",
        "volume": 2,
        "companionTo": "post_elementary_jukugo_list.json",
        "totalKanji": n,
        "kanjiPerPart": 50,
        "partCount": part_count,
        "partSizes": part_sizes,
        "anchorRule": "bestAdditionalCompoundAfterVolume1",
        "notes": [
            "Same kanji order as Volume 1 (post_elementary_01..11 → parts of 50).",
            "Volume 2 selects the best additional compound after the Volume 1 anchor.",
            "Priorities: modern frequency, everyday usefulness, JLPT N1, newspaper/book frequency, "
            "different meaning/nuance from Volume 1, different reading when appropriate.",
            "No Volume 1 per-kanji anchors reused. Prefer unique anchors within Volume 2.",
            "Avoid obscure, literary, historical, or specialist vocabulary unless clearly common today.",
        ],
        "entries": [
            {k: v for k, v in e.items() if k != "volume1Anchor"} for e in entries
        ],
    }
    OUT_JSON.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "displayOrder",
                "kanji",
                "volume1Anchor",
                "anchor",
                "reading",
                "en",
                "heisigNumber",
                "slug",
                "jpHtml",
                "part",
            ],
        )
        writer.writeheader()
        for e in entries:
            part = (int(e["displayOrder"]) - 1) // 50 + 1
            writer.writerow(
                {
                    "displayOrder": e["displayOrder"],
                    "kanji": e["kanji"],
                    "volume1Anchor": e["volume1Anchor"],
                    "anchor": e["anchor"],
                    "reading": e["reading"],
                    "en": e["en"],
                    "heisigNumber": e["heisigNumber"],
                    "slug": e.get("slug") or "",
                    "jpHtml": e["jpHtml"],
                    "part": part,
                }
            )

    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_CSV}")
    print(f"entries: {n}  parts: {part_count}")
    if dups:
        print(f"WARNING: duplicate anchors within Vol2 ({len(dups)}): {dups[:20]}")
    if soft_vol1_overlap:
        print(
            f"WARNING: {len(soft_vol1_overlap)} anchors also appear somewhere in Vol1 "
            f"(first 20): {soft_vol1_overlap[:20]}"
        )
    if hard_same_kanji_reuse:
        print(f"ERROR leftover same-kanji reuse: {hard_same_kanji_reuse}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
