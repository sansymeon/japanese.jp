#!/usr/bin/env python3
"""Build Grade 2 Kanji Soundtrack collections (joyo order, cheerful edition)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS))
from collection_paths import write_collection_path  # noqa: E402
from grade_2_kanji import load_grade_2_kanji  # noqa: E402
from grade2_kanji_common import (  # noqa: E402
    CONTENT_TAIL_PAD_MS,
    DEFAULT_EXHIBITION,
    PART_KANJI_COUNT,
    PART_KANJI_OFFSET,
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
from grade2_musical_timing import (  # noqa: E402
    MS_PER_KANJI,
    fit_musical_entries,
    musical_collection_runtime_ms,
)


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
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": cid,
        "title": f"{SERIES_TITLE} — Part {part}",
        "notes": (
            f"{SERIES_TITLE}: cheerful review for young learners. "
            f"Part {part} ({len(scenes)} kanji, joyo order) @ ~{MS_PER_KANJI / 1000:.1f}s each. "
            f"Soundtrack ~{format_duration(soundtrack_ms)}."
        ),
        "soundtrack": {"main": soundtrack_rel},
        "bookends": {
            "opening": {
                "image": bookend_image,
                "bookendSize": "large",
                "startSoundtrackWithImage": True,
                "startSoundtrackAfterImageMs": int(
                    DEFAULT_EXHIBITION.get("openingSoundtrackDelayMs", 2500)
                ),
            },
            "closing": {
                "image": bookend_image,
                "holdUntilSoundtrackEnds": True,
                "fadeWithSoundtrackEnd": True,
                "bookendSize": "large",
            },
        },
        "exhibition": dict(DEFAULT_EXHIBITION),
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "grade2KanjiSoundtrack",
            "showKeyword": False,
            "showKanji": False,
            "showEnglish": False,
            "exhibitProfile": "grade2KanjiSoundtrack",
            "musicalTiming": True,
            "continuousFlow": True,
        },
        "meta": {
            "series": SERIES_ID,
            "scope": SERIES_SCOPE,
            "part": part,
            "stage": "grade2KanjiSoundtrack",
            "sceneCount": len(scenes),
            "kanjiRange": [entries[0].kanji, entries[-1].kanji],
            "joyoIndexRange": [entries[0].joyo_index, entries[-1].joyo_index],
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
            "contentBudgetMs": content_budget_ms(soundtrack_ms),
            "msPerKanji": MS_PER_KANJI,
            "milestoneEvery": 10,
            "order": "joyo_index",
        },
        "scenes": scenes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", type=int, required=True, help="Part number (1–4)")
    parser.add_argument("--offset", type=int, help="Skip first N kanji before this part")
    parser.add_argument("--kanji-per-part", type=int, help="Kanji in this part")
    args = parser.parse_args()

    entries = load_grade_2_kanji()
    if not entries:
        print("No grade-2 kanji found.", file=sys.stderr)
        return 1

    offset = args.offset if args.offset is not None else PART_KANJI_OFFSET.get(args.part, 0)
    size = args.kanji_per_part if args.kanji_per_part is not None else PART_KANJI_COUNT.get(args.part, 40)
    slice_entries = entries[offset : offset + size]
    if not slice_entries:
        print(f"Part {args.part} has no kanji at offset {offset}.", file=sys.stderr)
        return 1

    soundtrack_rel = soundtrack_path_for_part(args.part)
    soundtrack_path = ROOT / soundtrack_rel
    soundtrack_ms = probe_duration_ms(soundtrack_path)
    if soundtrack_ms is None:
        print(f"Missing soundtrack: {soundtrack_path}", file=sys.stderr)
        return 1

    budget = content_budget_ms(soundtrack_ms)
    chunk, scenes = fit_musical_entries(
        slice_entries,
        budget,
        scene_for_entry=lambda e, index: scene_for_entry(e, part=args.part, index=index),
    )
    if not chunk:
        print(f"Part {args.part} has no kanji that fit the soundtrack budget.", file=sys.stderr)
        return 1

    last = dict(scenes[-1])
    meta = dict(last.get("meta") or {})
    meta["milestone"] = True
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
    print(f"Wrote {len(chunk)} kanji → {out_path}")
    print(f"  range: {chunk[0].kanji} → {chunk[-1].kanji} (joyo order)")
    print(f"  soundtrack: {soundtrack_rel} ({format_duration(soundtrack_ms)})")
    print(f"  exhibit runtime: {format_duration(content_ms)}")
    print(f"  exhibition.html?collection={config['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
