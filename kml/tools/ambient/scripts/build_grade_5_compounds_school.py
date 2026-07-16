#!/usr/bin/env python3
"""Build Grade 5 Compounds — school edition (10 parts from jukugo list).

Lane axes:
  contentType: compounds
  edition: school
  grade: 4
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from anchor_compounds_layout import anchor_word_scale  # noqa: E402
from collection_paths import write_collection_path  # noqa: E402
from grade_5_anchor_compounds_data import ordered_anchor_entries, part_batches  # noqa: E402
from grade5_compounds_school_common import (  # noqa: E402
    COLLECTION_PREFIX,
    CONTENT_TYPE,
    DEFAULT_EXHIBITION,
    EDITION,
    GRADE,
    PART_COUNT,
    SERIES_ID,
    SERIES_SCOPE,
    SERIES_TITLE,
    SOUNDTRACK,
    SOUNDTRACK_FULL,
    batching_meta,
    bookend_image_for_part,
    card_runtime_ms,
    collection_id,
    collection_runtime_ms,
    exhibition_timing_for_part,
    format_duration,
    kanji_color,
    probe_duration_ms,
)

FULL_COLLECTION_ID = COLLECTION_PREFIX
CONFIRMATION_MODES = ("stacked", "replace", "crossfade")


def scene_from_entry(entry: dict, *, part: int, index_in_part: int) -> dict:
    kanji = entry["kanji"]
    anchor_word = entry["anchor"]
    reading = entry["reading"]
    order = entry.get("displayOrder", index_in_part + 1)

    anchor: dict = {
        "word": anchor_word,
        "reading": reading,
        "wordScale": anchor_word_scale(anchor_word),
    }
    if entry.get("exception"):
        anchor["exception"] = True
        anchor["visualWeightTarget"] = (
            entry.get("visualWeightTarget")
            or entry.get("emphasize")
            or kanji
        )
        if entry.get("exceptionReason"):
            anchor["exceptionReason"] = entry["exceptionReason"]

    meta = {
        "grade": entry.get("grade", GRADE),
        "lesson": entry.get("lesson"),
        "part": part,
        "indexInPart": index_in_part,
        "displayOrder": order,
        "kanjiColor": kanji_color(order),
    }
    if entry.get("notes"):
        meta["notes"] = entry["notes"]

    return {
        "id": f"G5_compounds_{order:03d}_{kanji}",
        "kanji": kanji,
        "anchor": anchor,
        "meta": meta,
    }


def bookends_for_part(part: int, timing: dict | None = None) -> dict:
    image = bookend_image_for_part(part)
    t = timing or DEFAULT_EXHIBITION
    return {
        "opening": {
            "image": image,
            "bookendSize": "large",
            "startSoundtrackWithImage": True,
            "startSoundtrackAfterImageMs": int(
                t.get("openingSoundtrackDelayMs", 2500)
            ),
        },
        "closing": {
            "image": image,
            "holdUntilSoundtrackEnds": False,
            "fadeWithSoundtrackEnd": True,
            "bookendSize": "large",
        },
    }


def build_part_collection(
    part: int,
    entries: list[dict],
    *,
    confirmation_mode: str = "stacked",
) -> dict:
    timing = exhibition_timing_for_part(part)
    scenes = [
        scene_from_entry(entry, part=part, index_in_part=i)
        for i, entry in enumerate(entries)
    ]
    soundtrack_rel = SOUNDTRACK
    soundtrack_ms = probe_duration_ms(ROOT / soundtrack_rel)
    content_ms = collection_runtime_ms(len(scenes), timing)
    cid = collection_id(part)
    kanji_range = [entries[0]["kanji"], entries[-1]["kanji"]] if entries else []

    return {
        "presentation": "study",
        "contentType": CONTENT_TYPE,
        "edition": EDITION,
        "grade": GRADE,
        "id": cid,
        "title": f"{SERIES_TITLE} — Part {part}",
        "assetsBase": "../../assets",
        "soundtrack": {"main": soundtrack_rel},
        "bookends": bookends_for_part(part, timing),
        "display": {
            "exhibitProfile": "anchorCompoundsExhibition",
            "family": "schoolCompounds",
            "contentType": CONTENT_TYPE,
            "edition": EDITION,
            "typography": "mobile-refine",
            "verseMode": "sequential",
            "confirmationMode": confirmation_mode,
            "loop": False,
            "showKeyword": False,
        },
        "exhibition": timing,
        "meta": {
            "series": SERIES_ID,
            "scope": SERIES_SCOPE,
            "grade": GRADE,
            "contentType": CONTENT_TYPE,
            "edition": EDITION,
            "part": part,
            "stage": "compounds",
            "format": "anchorCompounds",
            "prototype": True,
            "sceneCount": len(scenes),
            "title": f"{SERIES_TITLE} — Part {part}",
            "kanjiRange": kanji_range,
            "confirmationModes": list(CONFIRMATION_MODES),
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
            "batching": batching_meta(),
        },
        "scenes": scenes,
    }


def build_full_collection(*, confirmation_mode: str = "stacked") -> dict:
    entries = ordered_anchor_entries()
    timing = dict(DEFAULT_EXHIBITION)
    scenes = [
        scene_from_entry(
            entry,
            part=int(entry.get("part") or 1),
            index_in_part=i,
        )
        for i, entry in enumerate(entries)
    ]
    # Fix indexInPart per part
    per_part_index: dict[int, int] = {}
    for scene in scenes:
        part = int(scene["meta"]["part"])
        idx = per_part_index.get(part, 0)
        scene["meta"]["indexInPart"] = idx
        per_part_index[part] = idx + 1

    soundtrack_rel = SOUNDTRACK_FULL
    soundtrack_ms = probe_duration_ms(ROOT / soundtrack_rel)
    content_ms = collection_runtime_ms(len(scenes), timing)
    bookend_image = bookend_image_for_part(1)

    return {
        "presentation": "study",
        "contentType": CONTENT_TYPE,
        "edition": EDITION,
        "grade": GRADE,
        "id": FULL_COLLECTION_ID,
        "title": SERIES_TITLE,
        "assetsBase": "../../assets",
        "soundtrack": {"main": soundtrack_rel},
        "bookends": {
            "opening": {
                "image": bookend_image,
                "bookendSize": "large",
                "startSoundtrackWithImage": True,
                "startSoundtrackAfterImageMs": int(
                    timing.get("openingSoundtrackDelayMs", 2500)
                ),
            },
            "closing": {
                "image": bookend_image,
                "holdUntilSoundtrackEnds": False,
                "fadeWithSoundtrackEnd": True,
                "bookendSize": "large",
            },
        },
        "display": {
            "exhibitProfile": "anchorCompoundsExhibition",
            "family": "schoolCompounds",
            "contentType": CONTENT_TYPE,
            "edition": EDITION,
            "typography": "mobile-refine",
            "verseMode": "sequential",
            "confirmationMode": confirmation_mode,
            "loop": False,
            "showKeyword": False,
        },
        "exhibition": timing,
        "meta": {
            "grade": GRADE,
            "contentType": CONTENT_TYPE,
            "edition": EDITION,
            "stage": "compounds",
            "format": "anchorCompounds",
            "prototype": True,
            "sceneCount": len(scenes),
            "title": SERIES_TITLE,
            "kanjiRange": [entries[0]["kanji"], entries[-1]["kanji"]] if entries else [],
            "confirmationModes": list(CONFIRMATION_MODES),
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
            "batching": batching_meta(),
        },
        "scenes": scenes,
    }


def write_collection(config: dict) -> Path:
    out_path = write_collection_path(ROOT, config["id"])
    out_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return out_path


def print_part_summary(config: dict, out_path: Path) -> None:
    content_ms = config["meta"]["estimatedContentRuntimeMs"]
    soundtrack_ms = config["meta"].get("soundtrackDurationMs") or 0
    soundtrack_rel = config["soundtrack"]["main"]
    bookend = config["bookends"]["opening"]["image"]
    kanji_range = config["meta"].get("kanjiRange", [])
    range_label = f"{kanji_range[0]} → {kanji_range[1]}" if kanji_range else "—"
    print(f"Wrote {out_path} ({config['meta']['sceneCount']} scenes)")
    print(f"  range: {range_label}")
    print(f"  bookend: {bookend}")
    print(f"  cards only: {format_duration(content_ms)}")
    if soundtrack_ms:
        print(f"  soundtrack: {soundtrack_rel} ({format_duration(soundtrack_ms)})")
    if soundtrack_ms and content_ms > soundtrack_ms:
        print(
            "  warning: card runtime exceeds soundtrack",
            file=sys.stderr,
        )
    print(f"  exhibition.html?collection={config['id']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", type=int, help=f"Build one part (1–{PART_COUNT})")
    parser.add_argument("--all", action="store_true", help="Build all parts")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Also build monolithic collection (grade_5_compounds_school)",
    )
    parser.add_argument("--plan", action="store_true", help="Print batch plan")
    parser.add_argument(
        "--mode",
        choices=CONFIRMATION_MODES,
        default="stacked",
        help="Default confirmation mode stored in collection display block",
    )
    args = parser.parse_args()

    if not any([args.plan, args.all, args.part, args.full]):
        args.all = True

    all_entries = ordered_anchor_entries()
    batches = part_batches(all_entries)
    timing = dict(DEFAULT_EXHIBITION)
    per_card = card_runtime_ms(timing)

    if args.plan:
        print(f"Grade 5 compounds school batch plan ({len(all_entries)} kanji)")
        print(f"  layout: {PART_COUNT} parts from jukugo list (~{per_card}ms/card)")
        for part, chunk in batches:
            ms = collection_runtime_ms(len(chunk), timing)
            print(
                f"  part {part:2d}: {len(chunk)} kanji "
                f"({chunk[0]['kanji']} → {chunk[-1]['kanji']}) "
                f"bookend={bookend_image_for_part(part)} "
                f"~{format_duration(ms)}"
            )
        return 0

    built_any = False

    if args.all or args.part:
        parts_to_build = (
            [args.part]
            if args.part
            else [part for part, _ in batches]
        )
        if args.part and (args.part < 1 or args.part > PART_COUNT):
            print(f"Part must be 1–{PART_COUNT}.", file=sys.stderr)
            return 1
        for part in parts_to_build:
            match = next((chunk for p, chunk in batches if p == part), None)
            if not match:
                print(f"No batch for part {part}.", file=sys.stderr)
                return 1
            config = build_part_collection(part, match, confirmation_mode=args.mode)
            out_path = write_collection(config)
            print_part_summary(config, out_path)
            print()
            built_any = True

    if args.full:
        config = build_full_collection(confirmation_mode=args.mode)
        out_path = write_collection(config)
        print_part_summary(config, out_path)
        built_any = True

    if not built_any:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
