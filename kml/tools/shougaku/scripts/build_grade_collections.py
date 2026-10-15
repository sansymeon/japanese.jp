#!/usr/bin/env python3
"""Build shougaku (elementary school grade) kanji exhibition collections."""

from __future__ import annotations

import csv
import json
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KANJI_MASTER = ROOT.parents[1] / "data" / "kanji" / "kanji_master.csv"
COLLECTIONS_DIR = ROOT / "collections"

GRADE_META = {
    "1": {
        "id": "grade_1",
        "title": "小学校一年で学ぶ漢字",
        "titleEn": "Grade 1 Elementary Kanji",
        "expectedCount": 80,
        "soundtrack": "audio/grade_1_soundtrack.mp3",
    },
    "2": {
        "id": "grade_2",
        "title": "小学校二年で学ぶ漢字",
        "titleEn": "Grade 2 Elementary Kanji",
        "expectedCount": 160,
        "soundtrack": "audio/grade_2_soundtrack.mp3",
    },
}


def load_grade_kanji(grade: str) -> list[dict]:
    seen: OrderedDict[str, dict] = OrderedDict()
    with KANJI_MASTER.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("grade") != grade:
                continue
            kanji = row["kanji"]
            if kanji in seen:
                continue
            seen[kanji] = {
                "kanji": kanji,
                "slug": row["slug"],
                "keyword": row.get("keyword") or row["slug"],
            }
    return list(seen.values())


def chunk(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def build_collection(grade: str) -> dict:
    meta = GRADE_META[grade]
    kanji = load_grade_kanji(grade)
    expected = meta["expectedCount"]
    if len(kanji) > expected:
        print(
            f"Note: grade {grade} has {len(kanji)} unique kanji; "
            f"using first {expected} for {expected // 40}×40 groups."
        )
        kanji = kanji[:expected]
    group_size = 40
    groups = chunk(kanji, group_size)
    return {
        "id": meta["id"],
        "title": meta["title"],
        "titleEn": meta["titleEn"],
        "grade": int(grade),
        "kanjiCount": len(kanji),
        "groupCount": len(groups),
        "groupSize": group_size,
        "grid": {"cols": 4, "rows": 10},
        "soundtrack": {"main": meta["soundtrack"]},
        "timing": {
            "titleFadeInMs": 1200,
            "titleHoldMs": 3500,
            "titleFadeOutMs": 1000,
            "groupFadeInMs": 2800,
            "groupHoldMs": 9000,
            "groupFadeOutMs": 2200,
            "staggerMs": 70,
            "groupGapMs": 600,
            "endFadeMs": 3000,
        },
        "display": {
            "loop": True,
            "randomizeGroups": True,
            "randomizeWithinGroup": True,
            "showTitle": True,
        },
        "palette": [
            "#e85d4c",
            "#f4a261",
            "#e9c46a",
            "#2a9d8f",
            "#4cc9f0",
            "#4895ef",
            "#7b61ff",
            "#f72585",
            "#ff6b6b",
            "#06d6a0",
            "#ffd166",
            "#118ab2",
        ],
        "kanji": kanji,
        "groups": [
            {
                "id": f"group_{index + 1}",
                "index": index,
                "kanji": [entry["kanji"] for entry in group],
            }
            for index, group in enumerate(groups)
        ],
    }


def main() -> None:
    COLLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {"collections": []}

    for grade in ("1", "2"):
        collection = build_collection(grade)
        count = collection["kanjiCount"]
        expected = GRADE_META[grade]["expectedCount"]
        if count != expected:
            print(
                f"Warning: grade {grade} has {count} kanji "
                f"(expected {expected})"
            )

        out_path = COLLECTIONS_DIR / f"{collection['id']}.json"
        out_path.write_text(
            json.dumps(collection, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {out_path} ({count} kanji, {collection['groupCount']} groups)")

        manifest["collections"].append(
            {
                "id": collection["id"],
                "title": collection["title"],
                "url": f"./index.html?collection={collection['id']}",
                "kanjiCount": count,
                "groupCount": collection["groupCount"],
                "groupSize": collection["groupSize"],
            }
        )

    manifest_path = COLLECTIONS_DIR / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {manifest_path}")


if __name__ == "__main__":
    main()
