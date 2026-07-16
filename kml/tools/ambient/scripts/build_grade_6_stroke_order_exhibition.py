#!/usr/bin/env python3
"""Build Grade 6 Stroke Order exhibitions (8 parts; 25×7 + 16)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS))
from collection_paths import write_collection_path  # noqa: E402
from grade_6_kanji import load_grade_6_kanji  # noqa: E402
from grade6_stroke_order_common import (  # noqa: E402
    DEFAULT_EXHIBITION,
    KANJI_PER_PART,
    PART_COUNT,
    SERIES_ID,
    SERIES_SCOPE,
    SERIES_TITLE,
    bookend_image_for_part,
    collection_id,
    collection_runtime_ms,
    format_duration,
    plan_batches,
    probe_duration_ms,
    scene_for_entry,
    soundtrack_path_for_part,
)


def build_collection(part: int, entries: list) -> dict:
    timing = dict(DEFAULT_EXHIBITION)
    scenes = [scene_for_entry(e, part=part, index=i) for i, e in enumerate(entries)]
    content_ms = collection_runtime_ms(scenes, timing)
    soundtrack_rel = soundtrack_path_for_part(part)
    soundtrack_ms = probe_duration_ms(ROOT / soundtrack_rel)
    bookend_image = bookend_image_for_part(part)
    stroke_counts = [s["strokeOrder"]["strokeCount"] for s in scenes]
    cid = collection_id(part)

    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": cid,
        "title": f"{SERIES_TITLE} — Part {part}",
        "notes": (
            f"{SERIES_TITLE}: recognition → stroke writing → recognition. "
            f"Part {part} — {len(scenes)} kanji in school order; card length follows stroke count "
            f"(~{timing['strokeOrderDrawMs']}ms draw + {timing['strokeOrderStrokeGapMs']}ms gap). "
            f"Estimated runtime {format_duration(content_ms)}."
        ),
        "soundtrack": {"main": soundtrack_rel},
        "exhibition": timing,
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "grade6StrokeOrder",
            "showKeyword": False,
            "showKanji": False,
            "showEnglish": False,
            "exhibitProfile": "grade6StrokeOrder",
        },
        "meta": {
            "series": SERIES_ID,
            "scope": SERIES_SCOPE,
            "part": part,
            "stage": "grade6StrokeOrder",
            "sceneCount": len(scenes),
            "kanjiRange": [entries[0].kanji, entries[-1].kanji] if entries else [],
            "joyoIndexRange": [entries[0].joyo_index, entries[-1].joyo_index] if entries else [],
            "avgStrokeCount": round(sum(stroke_counts) / len(stroke_counts), 1) if stroke_counts else 0,
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
            "strokeDataRoot": "kml/tools/strokes",
            "batching": {
                "kanjiPerPart": KANJI_PER_PART,
                "partCount": PART_COUNT,
                "lastPartKanji": len(entries) if part == PART_COUNT else KANJI_PER_PART,
            },
        },
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
                "bookendSize": "large",
            },
        },
        "scenes": scenes,
    }


def write_collection(config: dict) -> Path:
    out_path = write_collection_path(ROOT, config["id"])
    out_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out_path


def print_summary(config: dict, out_path: Path) -> None:
    content_ms = config["meta"]["estimatedContentRuntimeMs"]
    soundtrack_ms = config["meta"].get("soundtrackDurationMs") or 0
    soundtrack_rel = config["soundtrack"]["main"]
    print(f"Wrote {len(config['scenes'])} kanji → {out_path}")
    print(f"  range: {config['meta']['kanjiRange'][0]} → {config['meta']['kanjiRange'][1]}")
    print(f"  avg strokes: {config['meta']['avgStrokeCount']}")
    print(f"  exhibit runtime: {format_duration(content_ms)}")
    if soundtrack_ms:
        print(f"  soundtrack: {soundtrack_rel} ({format_duration(soundtrack_ms)})")
        if content_ms > soundtrack_ms:
            over = content_ms - soundtrack_ms
            print(
                f"  warning: content exceeds soundtrack by {format_duration(over)} — extend MP3",
                file=sys.stderr,
            )
    print(f"  exhibition.html?collection={config['id']}")
    print("  QA: add &exhibit=0&singleExhibit=1&timingScale=0.05")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", type=int, help=f"Build one part (1–{PART_COUNT})")
    parser.add_argument("--all", action="store_true", help="Build all parts")
    parser.add_argument("--plan", action="store_true", help="Print batch plan for all 191 kanji")
    args = parser.parse_args()

    all_entries = load_grade_6_kanji()
    timing = dict(DEFAULT_EXHIBITION)
    batches = plan_batches(all_entries, timing)

    if args.plan:
        soundtrack_ms = probe_duration_ms(ROOT / soundtrack_path_for_part(1)) or 0
        print(f"Grade 6 stroke order batch plan ({len(all_entries)} kanji)")
        print(f"  layout: 25×7 + 16 → {PART_COUNT} parts")
        if soundtrack_ms:
            print(f"  soundtrack: {format_duration(soundtrack_ms)}")
        for part, start, end in batches:
            chunk = all_entries[start:end]
            scenes = [scene_for_entry(e, part=part, index=i) for i, e in enumerate(chunk)]
            ms = collection_runtime_ms(scenes, timing)
            flag = " ⚠ over" if soundtrack_ms and ms > soundtrack_ms else ""
            print(
                f"  part {part}: {len(chunk)} kanji "
                f"({chunk[0].kanji} → {chunk[-1].kanji}) "
                f"bookend={bookend_image_for_part(part)} "
                f"~{format_duration(ms)}{flag}"
            )
        return 0

    if args.all:
        for part, start, end in batches:
            chunk = all_entries[start:end]
            config = build_collection(part, chunk)
            out_path = write_collection(config)
            print_summary(config, out_path)
            print()
        return 0

    if args.part:
        if args.part < 1 or args.part > PART_COUNT:
            print(f"Part must be 1–{PART_COUNT}.", file=sys.stderr)
            return 1
        match = next((b for b in batches if b[0] == args.part), None)
        if not match:
            print(f"No batch for part {args.part}.", file=sys.stderr)
            return 1
        _, start, end = match
        chunk = all_entries[start:end]
        config = build_collection(args.part, chunk)
        out_path = write_collection(config)
        print_summary(config, out_path)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
