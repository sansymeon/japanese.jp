#!/usr/bin/env python3
"""
Build kanji_master_layouts.csv from kanji_master.csv by adding layout_type.

layout_type is derived from the outermost Ideographic Description Character (IDS)
in the CJKVI CHISE-based ids.txt database (dominant composition only).

Does not read or write kanji_master.csv except as read-only input.
"""

from __future__ import annotations

import csv
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

IDS_URL = "https://raw.githubusercontent.com/cjkvi/cjkvi-ids/master/ids.txt"

# Ideographic Description Characters (Unicode 16.x)
IDC_HORIZONTAL = frozenset({"\u2ff0", "\u2ff2"})  # ⿰ ⿲
IDC_VERTICAL = frozenset({"\u2ff1", "\u2ff3"})  # ⿱ ⿳
IDC_BOX = frozenset(
    {
        "\u2ff4",  # ⿴
        "\u2ff5",  # ⿵
        "\u2ff6",  # ⿶
        "\u2ff7",  # ⿷
        "\u2ff8",  # ⿸
        "\u2ff9",  # ⿹
        "\u2ffa",  # ⿺
    }
)
IDC_OVERLAID = "\u2ffb"  # ⿻


def _strip_ids_suffix(token: str) -> str:
    return re.sub(r"\[.*]$", "", token)


def classify_outer_ids(ids: str) -> str:
    """
    Map the leading IDS of a character to layout_type.
    Allowed return values: horizontal | vertical | box | unknown
    """
    ids = ids.strip()
    if not ids:
        return "unknown"
    first = ids[0]
    if first in IDC_HORIZONTAL:
        return "horizontal"
    if first in IDC_VERTICAL:
        return "vertical"
    if first in IDC_BOX:
        return "box"
    if first == IDC_OVERLAID:
        return "unknown"
    return "unknown"


def load_ids_map(text: str) -> dict[str, str]:
    """char -> layout_type (first IDS variant wins)."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        char = parts[1]
        # Remaining tokens are IDS variants (e.g. ⿱天日[G] ⿱夭日[TK])
        for token in parts[2:]:
            cleaned = _strip_ids_suffix(token)
            if not cleaned:
                continue
            layout = classify_outer_ids(cleaned)
            if char not in out:
                out[char] = layout
            break
    return out


def fetch_ids_text(url: str = IDS_URL) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "kml-generate-kanji-master-layouts/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8")


def main() -> int:
    kml_root = Path(__file__).resolve().parents[1]
    master_path = kml_root / "data" / "kanji" / "kanji_master.csv"
    out_path = kml_root / "data" / "kanji" / "kanji_master_layouts.csv"

    if not master_path.is_file():
        print(f"Missing input: {master_path}", file=sys.stderr)
        return 1

    try:
        ids_text = fetch_ids_text()
    except OSError as e:
        print(f"Failed to fetch IDS data: {e}", file=sys.stderr)
        return 1

    char_layout = load_ids_map(ids_text)

    with master_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("Empty CSV header", file=sys.stderr)
            return 1
        fieldnames = list(reader.fieldnames)
        if "layout_type" in fieldnames:
            print("Input already has layout_type; aborting to avoid confusion.", file=sys.stderr)
            return 1
        out_fieldnames = fieldnames + ["layout_type"]
        rows = list(reader)

    # Normalize rows: some lines have trailing commas → DictReader puts overflow under key None.
    rows = [{k: (row.get(k) or "") for k in fieldnames} for row in rows]

    counts: Counter[str] = Counter()
    by_layout: dict[str, list[dict[str, str]]] = {
        "horizontal": [],
        "vertical": [],
        "box": [],
        "unknown": [],
    }

    for row in rows:
        kanji = row.get("kanji", "") or ""
        ch = kanji[:1] if kanji else ""
        layout = char_layout.get(ch, "unknown")
        if layout not in ("horizontal", "vertical", "box", "unknown"):
            layout = "unknown"
        row["layout_type"] = layout
        counts[layout] += 1
        bucket = by_layout.setdefault(layout, [])
        if len(bucket) < 8:
            bucket.append(row)

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    # --- Report (stdout) ---
    print(f"Wrote {out_path}")
    print()
    print("Counts by layout_type:")
    for k in ("horizontal", "vertical", "box", "unknown"):
        print(f"  {k}: {counts[k]}")
    print(f"  total: {sum(counts.values())}")
    print()

    def _sample_lines(label: str, sample_rows: list[dict[str, str]]) -> None:
        print(f"Sample ({label}):")
        for r in sample_rows:
            print(f"  {r.get('kanji','')}\t{r.get('slug','')}\t{r.get('layout_type','')}")
        print()

    _sample_lines("horizontal", by_layout["horizontal"])
    _sample_lines("vertical", by_layout["vertical"])
    _sample_lines("box", by_layout["box"])
    _sample_lines("unknown", by_layout["unknown"][:8])

    unknown_rows = [r for r in rows if r.get("layout_type") == "unknown"]
    print(f"All rows classified as unknown ({len(unknown_rows)} rows):")
    for r in unknown_rows:
        u = r.get("unicode", "")
        slug = r.get("slug", "")
        k = r.get("kanji", "")
        print(f"  {k}\t{u}\t{slug}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
