#!/usr/bin/env python3
"""Trim Heart v5 exhibition MP4 — remove recorder lead-in and trailing black."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = "heart_v5"


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
    parser.add_argument("--input", type=Path, help="Source MP4 (default: heart_exhibitions/heart_v5.mp4)")
    parser.add_argument("--output", type=Path, help="Trimmed output (default: replace input)")
    parser.add_argument(
        "--head",
        type=float,
        default=3.0,
        help="Seconds to cut from head (recorder lead-in before opening black)",
    )
    parser.add_argument(
        "--tail",
        type=float,
        default=3.5,
        help="Seconds to cut from tail (closingBlackAfter + record pad)",
    )
    args = parser.parse_args()

    src = args.input or ROOT / "heart_exhibitions" / f"{COLLECTION}.mp4"
    out = args.output or src
    backup = src.parent / f"{COLLECTION}_original.mp4"
    tmp = src.parent / f".{COLLECTION}_trim.mp4"

    if not src.is_file():
        print(f"Missing source: {src}", file=sys.stderr)
        return 1

    duration = probe_duration(src)
    end_at = duration - args.tail
    if end_at <= args.head:
        print("Trim values exceed duration.", file=sys.stderr)
        return 1

    if not backup.is_file() and src.resolve() == out.resolve():
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
            str(tmp),
        ],
        check=True,
    )

    trimmed = probe_duration(tmp)
    if out.resolve() == src.resolve():
        tmp.replace(out)
    else:
        tmp.replace(out)

    collection_path = ROOT / "collections" / f"{COLLECTION}.json"
    opening_ms = 2000
    if collection_path.is_file():
        collection = json.loads(collection_path.read_text(encoding="utf-8"))
        opening_ms = int((collection.get("exhibition") or {}).get("openingBlackBeforeMs", 2000))

    print(f"Trimmed Heart v5: {duration:.1f}s → {trimmed:.1f}s")
    print(f"  head {args.head}s, tail {args.tail}s (opening black ~{opening_ms / 1000:.1f}s retained)")
    print(f"  → {out}")
    if backup.is_file():
        print(f"  backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
