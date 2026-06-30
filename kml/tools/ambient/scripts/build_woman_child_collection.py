#!/usr/bin/env python3
"""Build woman_child_v1 — primitive exhibition source.

女 / 子 / 母 radical families, every_family (毎侮悔晦梅海), and kin (海・苺).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from primitive_collection import collect_scenes, list_gaps  # noqa: E402

COLLECTION_ID = "woman_child_v1"
PRIMITIVE_PARTS = frozenset({"女", "子", "母", "海", "苺", "毎"})
PRIMITIVE_FAMILIES = frozenset({"every_family"})

# glossary_family.csv — phonetic/visual cluster around 毎 (母-family)
EVERY_FAMILY_KANJI = frozenset({"毎", "侮", "悔", "晦", "梅", "海"})

# Radical-family anchor kanji (self-primitive entries; may not show 女/母/子 in kanji-part)
WOMAN_RADICAL_KANJI = frozenset(
    "姦奻嫐嬲婪孌妁妣妲姆妓婀娉嫋媼嫗嬶嬾嬉妥妙妖姑妊妬"
)
MOTHER_RADICAL_KANJI = frozenset("毒毓繁")
CHILD_RADICAL_KANJI = frozenset("孕孚孵孜孟季孤")

FAMILY_KANJI = EVERY_FAMILY_KANJI | WOMAN_RADICAL_KANJI | MOTHER_RADICAL_KANJI | CHILD_RADICAL_KANJI

DEFAULT_LESSON_MAX = None  # all lessons on disk

OUT_PATH = ROOT / "collections" / f"{COLLECTION_ID}.json"


def build_config(scenes: list[dict], *, lesson_max: int | None) -> dict:
    lessons = sorted({s["lesson"] for s in scenes})
    hi = lesson_max if lesson_max is not None else (max(lessons) if lessons else 0)
    return {
        "id": COLLECTION_ID,
        "title": "KML Ambient – Woman, Child & Mother Radicals 女・子・母",
        "notes": (
            "Primitive exhibition: 女/子/母 parts, every_family (毎侮悔晦梅海), "
            "and radical-family anchor kanji (woman / mother / child clusters). "
            f"{len(scenes)} scenes with artwork + verses in current book."
        ),
        "assetsBase": "../../assets",
        "timing": {
            "fadeMs": 4000,
            "kanjiLeadMs": 2000,
            "imageLeadMs": 6000,
            "verseLeadMs": 12000,
            "holdMs": 35000,
            "crossfadeMs": 5000,
            "kenBurnsDurationMs": 180000,
        },
        "background": {
            "mode": "auto",
            "kenBurns": True,
            "overlayOpacity": 0.55,
            "blurPx": 0,
        },
        "display": {
            "showKeyword": True,
            "showFurigana": False,
            "loop": True,
            "autoAdvance": True,
        },
        "meta": {
            "theme": "womanChildMotherRadicals",
            "primitive": "womanChildMotherRadicals",
            "primitiveParts": sorted(PRIMITIVE_PARTS),
            "everyFamilyMembers": sorted(EVERY_FAMILY_KANJI),
            "radicalFamilies": {
                "woman": sorted(WOMAN_RADICAL_KANJI),
                "mother": sorted(MOTHER_RADICAL_KANJI),
                "child": sorted(CHILD_RADICAL_KANJI),
            },
            "primitiveFamilies": sorted(PRIMITIVE_FAMILIES),
            "lessonRange": [1, hi],
            "sceneCount": len(scenes),
            "lessonsRepresented": lessons,
            "targetSceneCount": 40,
        },
        "scenes": scenes,
    }


def main() -> int:
    lesson_max = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LESSON_MAX
    kwargs = {
        "primitive_parts": PRIMITIVE_PARTS,
        "family_kanji": FAMILY_KANJI,
        "family_ids": PRIMITIVE_FAMILIES,
        "lesson_max": lesson_max,
    }
    scenes = collect_scenes(**kwargs)
    config = build_config(scenes, lesson_max=lesson_max)
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(scenes)} scenes → {OUT_PATH}")
    print(f"  lessons: {config['meta']['lessonsRepresented'][:8]}{'…' if len(config['meta']['lessonsRepresented']) > 8 else ''}")
    gaps = list_gaps(**kwargs)
    if gaps:
        print(f"  needs prep ({len(gaps)}):")
        for g in gaps:
            print(f"    L{g['lesson']:03d} {g['kanji']} ({g['primitivePart']}) — {', '.join(g['missing'])}")
    print(f"  index.html?collection={COLLECTION_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
