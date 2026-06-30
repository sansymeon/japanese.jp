#!/usr/bin/env python3
"""Trim a study exhibition MP4 and print YouTube chapter timestamps."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def yt(ms: int) -> str:
    ms = max(0, int(round(ms / 1000)))
    h, rem = divmod(ms, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def chapter_timestamps(collection: dict, *, head_trim_s: float) -> list[str]:
    intro = collection["intro"]
    t = collection["timing"]
    scenes = collection["scenes"]

    intro_ms = (
        intro.get("holdBeforeMs", 0)
        + intro.get("durationMs", 0)
        + (intro.get("exitFadeMs") or t.get("introExitFadeMs") or t.get("fadeMs", 0))
    )
    prep_first = t.get("foundationsKanjiGapMs", 350)
    prep_between = t.get("foundationsKanjiGapMs", 350)
    scene_dur = t.get("sceneDurationMs", 22000)

    last_start = intro_ms + prep_first + (len(scenes) - 1) * (scene_dur + prep_between)
    last_end = last_start + scene_dur

    lines = [f"0:00 Lesson {collection['id'].split('_')[1]} — Intro"]
    for i, sc in enumerate(scenes):
        start = intro_ms + prep_first + i * (scene_dur + prep_between)
        lines.append(f"{yt(start)} {sc['kanji']} — {sc['keyword']}")
    lines.append(f"{yt(last_end)} Gallery Seal — 漢")
    return ["LESSON TIMESTAMPS", *lines]


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, required=True)
    parser.add_argument("--input", type=Path, help="Source MP4 (default: foundations_exhibitions/)")
    parser.add_argument("--output", type=Path, help="Trimmed output (default: exhibition/)")
    parser.add_argument("--head", type=float, default=2.0, help="Seconds to cut from head")
    parser.add_argument("--tail", type=float, default=3.0, help="Seconds to cut from tail")
    args = parser.parse_args()

    src = args.input or ROOT / "foundations_exhibitions" / f"lesson_{args.lesson}_foundations.mp4"
    out = args.output or ROOT / "exhibition" / f"lesson_{args.lesson}_foundations.mp4"
    backup = src.parent / f"lesson_{args.lesson}_foundations_original.mp4"
    collection_path = ROOT / "exhibition" / f"lesson_{args.lesson}_foundations.json"

    if not src.is_file():
        print(f"Missing source: {src}", file=sys.stderr)
        return 1
    if not collection_path.is_file():
        print(f"Missing collection: {collection_path}", file=sys.stderr)
        return 1

    duration = probe_duration(src)
    end_at = duration - args.tail
    if end_at <= args.head:
        print("Trim values exceed duration.", file=sys.stderr)
        return 1

    if not backup.is_file():
        subprocess.run(["cp", str(src), str(backup)], check=True)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{args.head:.3f}",
            "-to",
            f"{end_at:.3f}",
            "-i",
            str(src),
            "-c",
            "copy",
            str(out),
        ],
        check=True,
    )

    trimmed = probe_duration(out)
    collection = json.loads(collection_path.read_text(encoding="utf-8"))
    print(f"Trimmed lesson {args.lesson}: {duration:.1f}s → {trimmed:.1f}s")
    print(f"  head {args.head}s, tail {args.tail}s")
    print(f"  → {out}")
    print()
    print("\n".join(chapter_timestamps(collection, head_trim_s=args.head)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
