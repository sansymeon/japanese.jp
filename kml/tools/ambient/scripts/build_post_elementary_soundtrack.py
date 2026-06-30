#!/usr/bin/env python3
"""Build Jōyō Kanji Soundtrack collections (post-elementary → end of Jōyō).

Grade-S Jōyō only. Post-Jōyō / high-school kanji will be a separate series.
"""

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
from loop_soundtrack import loop_soundtrack  # noqa: E402
from post_elementary_kanji import (  # noqa: E402
    load_post_elementary_kanji,
    part_count,
    part_slice,
)
from musical_timing import (  # noqa: E402
    DEFAULT_BPM,
    estimate_kanji_per_part,
    fit_musical_part_entries,
    musical_collection_runtime_ms,
)
from soundtrack_kanji_common import (  # noqa: E402
    CLOSING_IMAGE,
    CLOSING_OVERHEAD_MS,
    COLLECTION_PREFIX,
    CONTENT_TAIL_PAD_MS,
    DEFAULT_EXHIBITION,
    OPENING_IMAGE,
    OPENING_OVERHEAD_MS,
    SERIES_ID,
    SERIES_SCOPE,
    SERIES_TITLE,
    estimate_looped_soundtrack_ms,
    format_duration,
    probe_duration_ms,
    scene_for_entry,
    soundtrack_paths_for_part,
)


def collection_id(part: int) -> str:
    return f"{COLLECTION_PREFIX}_{part:02d}"


def resolve_track_ms(path: Path, fallback_ms: int) -> int:
    probed = probe_duration_ms(path)
    return probed if probed is not None else fallback_ms


def content_budget_ms(soundtrack_ms: int) -> int:
    return max(
        0,
        soundtrack_ms - OPENING_OVERHEAD_MS - CLOSING_OVERHEAD_MS - CONTENT_TAIL_PAD_MS,
    )


def build_soundtrack_file(
    track_a: Path,
    track_b: Path,
    output: Path,
    *,
    cycles: int,
    crossfade: float,
    end_fade: float,
) -> int:
    loop_soundtrack(
        track_a,
        track_b,
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
    opening_image: str,
    closing_image: str,
    bpm: float,
) -> dict:
    if not scenes:
        raise ValueError(f"Part {part} has no kanji scenes")

    content_ms = musical_collection_runtime_ms(scenes)
    timing = dict(DEFAULT_EXHIBITION)

    first_k = entries[0].kanji
    last_k = entries[-1].kanji
    cid = collection_id(part)

    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": cid,
        "title": f"{SERIES_TITLE} — Part {part}",
        "notes": (
            f"{SERIES_TITLE}: post-elementary through end of Jōyō (grade S). "
            "Calligraphy soundtrack — kanji typography with continuous crossfades. "
            f"Part {part} ({len(scenes)} kanji). Soundtrack ~{format_duration(soundtrack_ms)}."
        ),
        "soundtrack": {"main": soundtrack_rel},
        "bookends": {
            "opening": {
                "image": opening_image,
                "bookendSize": "large",
                "startSoundtrackWithImage": True,
                "startSoundtrackAfterImageMs": int(
                    DEFAULT_EXHIBITION.get("openingSoundtrackDelayMs", 1400)
                ),
            },
            "closing": {
                "image": closing_image,
                "holdUntilSoundtrackEnds": True,
                "fadeWithSoundtrackEnd": True,
                "bookendSize": "large",
            },
        },
        "exhibition": timing,
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "kanjiSoundtrack",
            "showKeyword": False,
            "showKanji": False,
            "showEnglish": False,
            "exhibitProfile": "kanjiSoundtrack",
            "musicalTiming": True,
            "continuousFlow": True,
        },
        "meta": {
            "series": SERIES_ID,
            "scope": SERIES_SCOPE,
            "part": part,
            "stage": "kanjiSoundtrackCalligraphy",
            "musicalBpm": bpm,
            "sceneCount": len(scenes),
            "kanjiRange": [first_k, last_k],
            "heisigRange": [entries[0].heisig_number, entries[-1].heisig_number],
            "soundtrackDurationMs": soundtrack_ms,
            "estimatedContentRuntimeMs": content_ms,
            "contentBudgetMs": content_budget_ms(soundtrack_ms),
            "strokeDataRoot": "kml/tools/strokes",
        },
        "scenes": scenes,
    }


def print_plan(
    entries: list,
    *,
    track_a_ms: int,
    track_b_ms: int,
    cycles: int,
    crossfade_ms: int,
    bpm: float,
) -> None:
    soundtrack_ms = estimate_looped_soundtrack_ms(
        track_a_ms, track_b_ms, cycles=cycles, crossfade_ms=crossfade_ms
    )
    budget = content_budget_ms(soundtrack_ms)
    per_part = estimate_kanji_per_part(
        entries, budget, bpm=bpm, scene_for_entry=scene_for_entry
    )
    parts = part_count(entries, size=per_part)
    print("Jōyō Kanji Soundtrack — partition plan (calligraphy edition)")
    print(f"  kanji in series: {len(entries)}")
    print(
        f"  track A: {format_duration(track_a_ms)}  "
        f"track B: {format_duration(track_b_ms)}  cycles: {cycles}"
    )
    print(f"  estimated soundtrack: {format_duration(soundtrack_ms)}")
    print(f"  content budget (exhibits): {format_duration(content_budget_ms(soundtrack_ms))}")
    print(f"  kanji per part (estimate): {per_part}")
    print(f"  parts (estimate): {parts}")
    print()
    for p in range(1, min(parts, 6) + 1):
        chunk = part_slice(entries, p, size=per_part)
        if not chunk:
            break
        print(
            f"  Part {p:02d}: {len(chunk):3d} kanji  "
            f"{chunk[0].kanji} ({chunk[0].heisig_number}) → "
            f"{chunk[-1].kanji} ({chunk[-1].heisig_number})"
        )
    if parts > 6:
        print(f"  … {parts - 6} more parts")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--part", type=int, default=1, help="Part number (default: 1)")
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Print partition plan and exit (no JSON written)",
    )
    parser.add_argument(
        "--track-a",
        type=Path,
        help="First soundtrack piece (MP3)",
    )
    parser.add_argument(
        "--track-b",
        type=Path,
        help="Second soundtrack piece (MP3)",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="A→B loop cycles in rendered soundtrack (default: 1)",
    )
    parser.add_argument(
        "--crossfade",
        type=float,
        default=5.0,
        help="Crossfade seconds between tracks (default: 5)",
    )
    parser.add_argument(
        "--end-fade",
        type=float,
        default=4.0,
        help="Final soundtrack fade seconds (default: 4)",
    )
    parser.add_argument(
        "--render-soundtrack",
        action="store_true",
        help="Render looped soundtrack MP3 with loop_soundtrack.py",
    )
    parser.add_argument(
        "--track-duration",
        type=float,
        metavar="MIN",
        help="Placeholder minutes per track when MP3s are missing (default: 3.5)",
    )
    parser.add_argument(
        "--kanji-per-part",
        type=int,
        help="Override automatic kanji count for this part",
    )
    parser.add_argument(
        "--offset",
        type=int,
        help="Skip first N kanji before this part (e.g. 100 after a 100-kanji part 1)",
    )
    parser.add_argument(
        "--soundtrack-out",
        type=Path,
        help="Rendered soundtrack path relative to ambient root (default: per-part)",
    )
    parser.add_argument(
        "--bpm",
        type=float,
        default=DEFAULT_BPM,
        help=f"Musical tempo for beat grid (default: {DEFAULT_BPM})",
    )
    parser.add_argument(
        "--opening-image",
        default=OPENING_IMAGE,
        help=f"Opening hero image path (default: {OPENING_IMAGE})",
    )
    parser.add_argument(
        "--closing-image",
        default=CLOSING_IMAGE,
        help=f"Closing hero image path (default: {CLOSING_IMAGE})",
    )
    args = parser.parse_args()

    entries = load_post_elementary_kanji(require_stroke_page=False)
    placeholder_ms = int((args.track_duration or 2.5) * 60_000)

    rel_a, rel_b, rel_soundtrack = soundtrack_paths_for_part(args.part)
    path_a = args.track_a or (ROOT / rel_a)
    path_b = args.track_b or (ROOT / rel_b)
    soundtrack_rel = (
        args.soundtrack_out.as_posix()
        if args.soundtrack_out
        else rel_soundtrack
    )
    path_soundtrack = ROOT / soundtrack_rel

    track_a_ms = resolve_track_ms(path_a, placeholder_ms)
    track_b_ms = resolve_track_ms(path_b, placeholder_ms)

    if args.plan:
        crossfade_ms = int(args.crossfade * 1000)
        print_plan(
            entries,
            track_a_ms=track_a_ms,
            track_b_ms=track_b_ms,
            cycles=args.cycles,
            crossfade_ms=crossfade_ms,
            bpm=args.bpm,
        )
        if not path_a.is_file() or not path_b.is_file():
            print()
            print("  (using placeholder track length — upload MP3s for exact counts)")
        return 0

    if args.render_soundtrack:
        if not path_a.is_file() or not path_b.is_file():
            print("Both --track-a and --track-b must exist to --render-soundtrack", file=sys.stderr)
            return 1
        try:
            soundtrack_ms = build_soundtrack_file(
                path_a,
                path_b,
                path_soundtrack,
                cycles=args.cycles,
                crossfade=args.crossfade,
                end_fade=args.end_fade,
            )
        except (RuntimeError, subprocess.CalledProcessError, ValueError) as err:
            print(err, file=sys.stderr)
            return 1
    else:
        soundtrack_ms = estimate_looped_soundtrack_ms(
            track_a_ms,
            track_b_ms,
            cycles=args.cycles,
            crossfade_ms=int(args.crossfade * 1000),
        )

    if args.kanji_per_part:
        size = args.kanji_per_part
    else:
        size = estimate_kanji_per_part(
            entries,
            content_budget_ms(soundtrack_ms),
            bpm=args.bpm,
            scene_for_entry=scene_for_entry,
        )

    if args.offset is not None:
        start = max(0, args.offset)
        slice_entries = entries[start : start + size]
    else:
        slice_entries = part_slice(entries, args.part, size=size)
    budget = content_budget_ms(soundtrack_ms)
    chunk, scenes = fit_musical_part_entries(
        slice_entries,
        args.part,
        budget,
        bpm=args.bpm,
        scene_for_entry=scene_for_entry,
    )
    if not chunk:
        print(f"Part {args.part} has no kanji that fit the soundtrack budget.", file=sys.stderr)
        return 1

    config = build_collection(
        args.part,
        chunk,
        scenes,
        soundtrack_rel=soundtrack_rel,
        soundtrack_ms=soundtrack_ms,
        opening_image=args.opening_image,
        closing_image=args.closing_image,
        bpm=args.bpm,
    )

    out_path = write_collection_path(ROOT, config["id"])
    out_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    content_ms = config["meta"]["estimatedContentRuntimeMs"]
    outro = max(0, soundtrack_ms - content_ms - OPENING_OVERHEAD_MS - CLOSING_OVERHEAD_MS)
    print(f"Wrote {len(chunk)} kanji → {out_path}")
    print(f"  range: {chunk[0].kanji} → {chunk[-1].kanji}")
    print(f"  soundtrack: {soundtrack_rel} ({format_duration(soundtrack_ms)})")
    print(f"  exhibit runtime: {format_duration(content_ms)}")
    print(f"  closing breathing room: ~{format_duration(outro)}")
    print(f"  exhibition.html?collection={config['id']}")
    print(f"  opening image: {args.opening_image}")
    print(f"  closing image: {args.closing_image}")
    if not path_soundtrack.is_file() and not args.render_soundtrack:
        print()
        print("  Upload MP3s and re-run with --render-soundtrack when ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
