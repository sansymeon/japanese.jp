#!/usr/bin/env python3
"""Build Grade 1 Kanji Soundtrack collections (40 kanji per part, cheerful edition)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS))
from collection_paths import write_collection_path  # noqa: E402
from grade_1_kanji import load_grade_1_kanji  # noqa: E402
from grade1_kanji_common import (  # noqa: E402
    CONTENT_TAIL_PAD_MS,
    DEFAULT_EXHIBITION,
    SERIES_ID,
    SERIES_SCOPE,
    SERIES_TITLE,
    SOUNDTRACK_RENDERED_PART1,
    SOUNDTRACK_RENDERED_PART2,
    bookend_image_for_part,
    collection_id,
    content_budget_ms,
    format_duration,
    probe_duration_ms,
    scene_for_entry,
    soundtrack_paths_for_part,
)
from grade1_musical_timing import (  # noqa: E402
    MS_PER_KANJI,
    fit_musical_entries,
    musical_collection_runtime_ms,
)
from loop_soundtrack import loop_single_track  # noqa: E402


def cycles_for_budget(track_ms: int, target_ms: int, *, crossfade_s: float) -> int:
    if track_ms <= 0:
        return 1
    crossfade_ms = int(crossfade_s * 1000)
    cycles = 1
    while True:
        total = track_ms + (cycles - 1) * max(0, track_ms - crossfade_ms)
        if total >= target_ms or cycles >= 12:
            return cycles
        cycles += 1


def build_soundtrack(track: Path, output: Path, *, cycles: int, crossfade: float, end_fade: float) -> int:
    loop_single_track(
        track,
        output,
        cycles=cycles,
        crossfade=crossfade,
        end_fade=end_fade,
    )
    probed = probe_duration_ms(output)
    if probed is None:
        raise RuntimeError(f"Could not probe rendered soundtrack: {output}")
    return probed


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
            f"Part {part} ({len(scenes)} kanji) @ ~{MS_PER_KANJI / 1000:.1f}s each. "
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
            "family": "grade1KanjiSoundtrack",
            "showKeyword": False,
            "showKanji": False,
            "showEnglish": False,
            "exhibitProfile": "grade1KanjiSoundtrack",
            "musicalTiming": True,
            "continuousFlow": True,
        },
        "meta": {
            "series": SERIES_ID,
            "scope": SERIES_SCOPE,
            "part": part,
            "stage": "grade1KanjiSoundtrack",
            "sceneCount": len(scenes),
            "kanjiRange": [entries[0].kanji, entries[-1].kanji],
            "joyoIndexRange": [entries[0].joyo_index, entries[-1].joyo_index],
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
            "contentBudgetMs": content_budget_ms(soundtrack_ms),
            "msPerKanji": MS_PER_KANJI,
            "milestoneEvery": 10,
        },
        "scenes": scenes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", type=int, default=1, help="Part number (default: 1)")
    parser.add_argument("--offset", type=int, help="Skip first N kanji before this part")
    parser.add_argument("--kanji-per-part", type=int, default=40, help="Kanji in this part")
    parser.add_argument("--track", type=Path, help="Source MP3 override")
    parser.add_argument("--render-soundtrack", action="store_true")
    parser.add_argument("--cycles", type=int, help="Loop count override")
    parser.add_argument("--crossfade", type=float, default=3.0)
    parser.add_argument("--end-fade", type=float, default=4.0)
    args = parser.parse_args()

    entries = load_grade_1_kanji()
    if not entries:
        print("No grade-1 kanji found.", file=sys.stderr)
        return 1

    offset = args.offset if args.offset is not None else 0
    size = args.kanji_per_part
    slice_entries = entries[offset : offset + size]
    if not slice_entries:
        print(f"Part {args.part} has no kanji at offset {offset}.", file=sys.stderr)
        return 1

    track_rel, soundtrack_rel = soundtrack_paths_for_part(args.part)
    track_path = args.track or (ROOT / track_rel)
    soundtrack_path = ROOT / soundtrack_rel
    track_ms = probe_duration_ms(track_path) or int(2.2 * 60_000)

    est_content = len(slice_entries) * MS_PER_KANJI
    est_target = est_content + CONTENT_TAIL_PAD_MS
    cycles = args.cycles or cycles_for_budget(track_ms, est_target, crossfade_s=args.crossfade)

    if args.render_soundtrack:
        render_out = ROOT / (SOUNDTRACK_RENDERED_PART1 if args.part == 1 else SOUNDTRACK_RENDERED_PART2)
        if not track_path.is_file():
            print(f"Missing track: {track_path}", file=sys.stderr)
            return 1
        try:
            soundtrack_ms = build_soundtrack(
                track_path,
                render_out,
                cycles=cycles,
                crossfade=args.crossfade,
                end_fade=args.end_fade,
            )
            soundtrack_rel = render_out.relative_to(ROOT).as_posix()
        except (RuntimeError, subprocess.CalledProcessError, ValueError) as err:
            print(err, file=sys.stderr)
            return 1
    else:
        probed = probe_duration_ms(soundtrack_path)
        if probed is not None:
            soundtrack_ms = probed
        else:
            crossfade_ms = int(args.crossfade * 1000)
            soundtrack_ms = track_ms + (cycles - 1) * max(0, track_ms - crossfade_ms)

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
    print(f"  range: {chunk[0].kanji} → {chunk[-1].kanji}")
    print(f"  soundtrack: {soundtrack_rel} ({format_duration(soundtrack_ms)})")
    print(f"  exhibit runtime: {format_duration(content_ms)}")
    print(f"  exhibition.html?collection={config['id']}")
    if not soundtrack_path.is_file() and not args.render_soundtrack:
        print()
        print("  Re-run with --render-soundtrack when ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
