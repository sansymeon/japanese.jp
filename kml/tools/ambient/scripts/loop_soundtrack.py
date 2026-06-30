#!/usr/bin/env python3
"""Crossfade two MP3 tracks into a looping exhibition soundtrack.

Alternates track A and track B with triangular crossfades (pop-style handoffs),
then fades out at the end. Requires ffmpeg on PATH.

Example (one A→B pass, 5 s crossfade, 4 s ending fade):

  python3 loop_soundtrack.py part_a.mp3 part_b.mp3 -o soundtrack.mp3

Longer loop for a ~13 minute exhibit (four A→B cycles):

  python3 loop_soundtrack.py part_a.mp3 part_b.mp3 -o soundtrack.mp3 --cycles 4
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    )
    return float(out.strip())


def chain_duration(durations: tuple[float, float], segments: int, crossfade: float) -> float:
    """Total length when alternating A/B for `segments` track plays."""
    if segments < 1:
        raise ValueError("segments must be >= 1")
    total = durations[0]
    for i in range(1, segments):
        total += durations[i % 2] - crossfade
    return total


def acrossfade_pair(
    left: Path,
    right: Path,
    output: Path,
    crossfade: float,
) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(left),
            "-i",
            str(right),
            "-filter_complex",
            f"[0:a][1:a]acrossfade=d={crossfade}:c1=tri:c2=tri[out]",
            "-map",
            "[out]",
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",
            str(output),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def attenuate_track(input_path: Path, output: Path, gain_db: float) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-af",
            f"volume={gain_db}dB",
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",
            str(output),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def prepare_segment(
    source: Path,
    work: Path,
    *,
    gain_db: float | None = None,
) -> Path:
    if gain_db is None:
        return source
    out = work / f"gain_{source.stem}_{abs(gain_db):.1f}db.mp3"
    attenuate_track(source, out, gain_db)
    return out


def chain_duration(durations: list[float], crossfade: float) -> float:
    if not durations:
        return 0.0
    total = durations[0]
    for duration in durations[1:]:
        total += duration - crossfade
    return total


def chain_soundtrack(
    segments: list[Path],
    output: Path,
    *,
    crossfade: float = 5.0,
    end_fade: float = 4.0,
    gains_db: list[float | None] | None = None,
) -> float:
    """Crossfade an ordered list of MP3s; optional per-segment gain in dB."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required on PATH")
    if len(segments) < 1:
        raise ValueError("segments must not be empty")
    if crossfade <= 0:
        raise ValueError("crossfade must be positive")

    gains_db = list(gains_db or [None] * len(segments))
    if len(gains_db) != len(segments):
        raise ValueError("gains_db must match segments length")

    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="chain_soundtrack_") as tmp:
        work = Path(tmp)
        prepared = [
            prepare_segment(seg, work, gain_db=gain)
            for seg, gain in zip(segments, gains_db)
        ]
        durations = [probe_duration(path) for path in prepared]
        min_track = min(durations)
        if crossfade >= min_track:
            raise ValueError(
                f"crossfade ({crossfade}s) must be shorter than the shortest segment ({min_track:.2f}s)"
            )

        current = prepared[0]
        for i, nxt in enumerate(prepared[1:], 1):
            step_out = work / f"step_{i:02d}.mp3"
            acrossfade_pair(current, nxt, step_out, crossfade)
            current = step_out

        if end_fade > 0:
            apply_end_fade(current, output, end_fade)
        else:
            shutil.copy2(current, output)

    return probe_duration(output)


def build_extended_soundtrack(
    track_a: Path,
    track_b: Path,
    extra_tracks: list[Path],
    output: Path,
    *,
    ab_cycles: int = 1,
    crossfade: float = 5.0,
    end_fade: float = 4.0,
    ab_gains_db: tuple[float | None, float | None] = (None, None),
    extra_gains_db: list[float | None] | None = None,
) -> float:
    """Loop A↔B, then crossfade in additional tracks at the end."""
    extra_gains_db = extra_gains_db or [None] * len(extra_tracks)
    if len(extra_gains_db) != len(extra_tracks):
        raise ValueError("extra_gains_db must match extra_tracks length")

    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="extended_soundtrack_") as tmp:
        work = Path(tmp)
        ab_out = work / "ab_loop.mp3"
        loop_soundtrack(
            track_a,
            track_b,
            ab_out,
            cycles=ab_cycles,
            crossfade=crossfade,
            end_fade=0,
        )

        segments = [ab_out, *extra_tracks]
        gains: list[float | None] = [None, *extra_gains_db]
        chain_out = work / "chained.mp3"
        chain_soundtrack(
            segments,
            chain_out,
            crossfade=crossfade,
            end_fade=0,
            gains_db=gains,
        )
        if end_fade > 0:
            apply_end_fade(chain_out, output, end_fade)
        else:
            shutil.copy2(chain_out, output)

    return probe_duration(output)


def apply_end_fade(input_path: Path, output: Path, end_fade: float) -> None:
    duration = probe_duration(input_path)
    fade_start = max(0.0, duration - end_fade)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-af",
            f"afade=t=out:st={fade_start:.3f}:d={end_fade}",
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",
            str(output),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def loop_single_track(
    track: Path,
    output: Path,
    *,
    cycles: int = 4,
    crossfade: float = 3.0,
    end_fade: float = 4.0,
) -> float:
    """Repeat one MP3 with crossfades until `cycles` plays, then fade out."""
    if cycles < 1:
        raise ValueError("cycles must be >= 1")
    segments = [track] * cycles
    return chain_soundtrack(
        segments,
        output,
        crossfade=crossfade,
        end_fade=end_fade,
    )


def loop_soundtrack(
    track_a: Path,
    track_b: Path,
    output: Path,
    *,
    cycles: int = 1,
    crossfade: float = 5.0,
    end_fade: float = 4.0,
) -> float:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required on PATH")
    if cycles < 1:
        raise ValueError("--cycles must be >= 1")
    if crossfade <= 0 or end_fade <= 0:
        raise ValueError("crossfade and end-fade must be positive")

    tracks = (track_a, track_b)
    durations = (probe_duration(track_a), probe_duration(track_b))
    min_track = min(durations)
    if crossfade >= min_track:
        raise ValueError(
            f"crossfade ({crossfade}s) must be shorter than the shorter track ({min_track:.2f}s)"
        )

    segments = 2 * cycles
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="loop_soundtrack_") as tmp:
        work = Path(tmp)
        current = tracks[0]
        for i in range(1, segments):
            nxt = tracks[i % 2]
            step_out = work / f"step_{i:02d}.mp3"
            acrossfade_pair(current, nxt, step_out, crossfade)
            current = step_out

        if end_fade > 0:
            apply_end_fade(current, output, end_fade)
        else:
            shutil.copy2(current, output)

    return probe_duration(output)


def fmt_duration(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("track_a", type=Path, help="First MP3 (starts the loop)")
    parser.add_argument("track_b", type=Path, help="Second MP3 (crossfades in after A)")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output MP3 path",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of A→B pairs (default: 1 = A crossfade B, then fade out)",
    )
    parser.add_argument(
        "--crossfade",
        type=float,
        default=5.0,
        metavar="SEC",
        help="Crossfade length between tracks (default: 5)",
    )
    parser.add_argument(
        "--end-fade",
        type=float,
        default=4.0,
        metavar="SEC",
        help="Final fade-out at the end (default: 4)",
    )
    args = parser.parse_args()

    for label, path in (("track_a", args.track_a), ("track_b", args.track_b)):
        if not path.is_file():
            print(f"Missing {label}: {path}", file=sys.stderr)
            return 1

    da, db = probe_duration(args.track_a), probe_duration(args.track_b)
    segments = 2 * args.cycles
    planned = chain_duration((da, db), segments, args.crossfade)

    try:
        out_duration = loop_soundtrack(
            args.track_a,
            args.track_b,
            args.output,
            cycles=args.cycles,
            crossfade=args.crossfade,
            end_fade=args.end_fade,
        )
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as err:
        print(err, file=sys.stderr)
        return 1

    print(f"Wrote {args.output}")
    print(f"  pattern: {' → '.join('AB'[i % 2] for i in range(segments))}")
    print(f"  crossfade: {args.crossfade:g}s   end fade: {args.end_fade:g}s")
    print(f"  duration: {fmt_duration(out_duration)}  (planned ~{fmt_duration(planned)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
