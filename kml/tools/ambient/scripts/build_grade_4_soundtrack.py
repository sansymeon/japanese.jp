#!/usr/bin/env python3
"""Build Grade 4 Kanji Soundtrack collections (gojūon order, mature linear edition)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS))
from collection_paths import write_collection_path  # noqa: E402
from grade4_gojuon import sections_for_part  # noqa: E402
from grade4_kanji_common import (  # noqa: E402
    DEFAULT_EXHIBITION,
    MILESTONE_EVERY,
    OPENING_BOOKEND_EXHIBITION,
    PART_COUNT,
    SERIES_ID,
    SERIES_SCOPE,
    SERIES_TITLE,
    bookend_image_for_part,
    collection_id,
    content_budget_ms,
    format_duration,
    probe_duration_ms,
    scene_for_entry,
    soundtrack_path_for_part,
)
from grade4_musical_timing import (  # noqa: E402
    MS_PER_KANJI,
    fit_musical_entries,
    musical_collection_runtime_ms,
)


def entries_for_part(part: int) -> list:
    entries = []
    for _kana, items in sections_for_part(part):
        entries.extend(items)
    return entries


def build_collection(
    part: int,
    entries: list,
    scenes: list[dict],
    *,
    soundtrack_rel: str,
    soundtrack_ms: int,
) -> dict:
    content_ms = musical_collection_runtime_ms(scenes)
    cid = collection_id(part)
    bookend_image = bookend_image_for_part(part)
    exhibition = dict(DEFAULT_EXHIBITION)
    if bookend_image:
        exhibition.update(OPENING_BOOKEND_EXHIBITION)

    config: dict = {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": cid,
        "title": f"{SERIES_TITLE} — Part {part}",
        "notes": (
            f"{SERIES_TITLE}: mature washi edition. "
            f"Part {part} ({len(scenes)} kanji, gojūon order) @ ~{MS_PER_KANJI / 1000:.1f}s each. "
            f"Soundtrack ~{format_duration(soundtrack_ms)}."
        ),
        "soundtrack": {"main": soundtrack_rel},
        "exhibition": exhibition,
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "grade4KanjiSoundtrack",
            "showKeyword": False,
            "showKanji": False,
            "showEnglish": False,
            "exhibitProfile": "grade4KanjiSoundtrack",
            "musicalTiming": True,
            "continuousFlow": True,
        },
        "meta": {
            "series": SERIES_ID,
            "scope": SERIES_SCOPE,
            "part": part,
            "stage": "grade4KanjiSoundtrack",
            "sceneCount": len(scenes),
            "kanjiRange": [entries[0].kanji, entries[-1].kanji],
            "joyoIndexRange": [entries[0].joyo_index, entries[-1].joyo_index],
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
            "contentBudgetMs": content_budget_ms(soundtrack_ms),
            "msPerKanji": MS_PER_KANJI,
            "milestoneEvery": MILESTONE_EVERY,
            "order": "gojuon",
        },
        "scenes": scenes,
    }
    if bookend_image:
        config["bookends"] = {
            "opening": {
                "image": bookend_image,
                "bookendSize": "large",
                "startSoundtrackWithImage": True,
                "startSoundtrackAfterImageMs": int(
                    exhibition.get("openingSoundtrackDelayMs", 2500)
                ),
            },
            "closing": {
                "image": bookend_image,
                "holdUntilSoundtrackEnds": True,
                "fadeWithSoundtrackEnd": True,
                "bookendSize": "large",
            },
        }
    return config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", type=int, required=True, help=f"Part number (1–{PART_COUNT})")
    args = parser.parse_args()

    if args.part < 1 or args.part > PART_COUNT:
        print(f"Part must be 1–{PART_COUNT}.", file=sys.stderr)
        return 1

    entries = entries_for_part(args.part)
    if not entries:
        print(f"Part {args.part} has no kanji.", file=sys.stderr)
        return 1

    soundtrack_rel = soundtrack_path_for_part(args.part)
    soundtrack_path = ROOT / soundtrack_rel
    soundtrack_ms = probe_duration_ms(soundtrack_path)
    if soundtrack_ms is None:
        print(f"Missing soundtrack: {soundtrack_path}", file=sys.stderr)
        return 1

    budget = content_budget_ms(soundtrack_ms)
    chunk, scenes = fit_musical_entries(
        entries,
        budget,
        scene_for_entry=lambda e, index: scene_for_entry(e, part=args.part, index=index),
    )
    if not chunk:
        print(f"Part {args.part} has no kanji that fit the soundtrack budget.", file=sys.stderr)
        return 1

    last = dict(scenes[-1])
    meta = dict(last.get("meta") or {})
    meta["finale"] = True
    last["meta"] = meta
    scenes[-1] = last

    config = build_collection(
        args.part,
        chunk,
        scenes,
        soundtrack_rel=soundtrack_rel,
        soundtrack_ms=soundtrack_ms,
    )
    out_path = write_collection_path(ROOT, config["id"])
    out_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    content_ms = config["meta"]["estimatedContentRuntimeMs"]
    sections = sections_for_part(args.part)
    print(f"Wrote {len(chunk)} kanji → {out_path}")
    print(f"  range: {chunk[0].kanji} → {chunk[-1].kanji} (gojūon)")
    print(f"  sections: {sections[0][0]} → {sections[-1][0]}")
    print(f"  soundtrack: {soundtrack_rel} ({format_duration(soundtrack_ms)})")
    print(f"  exhibit runtime: {format_duration(content_ms)}")
    print(f"  exhibition.html?collection={config['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
