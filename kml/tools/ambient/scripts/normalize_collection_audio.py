#!/usr/bin/env python3
"""Two-pass loudnorm for OBS-recorded collection videos (video stream copied)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Match Playwright-recorded ambient study levels (ambient_study_lesson_4 ≈ −17.3 LUFS).
TARGET_I = -17.0
TARGET_TP = -2.0
TARGET_LRA = 11.0


def require_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg is required on PATH.", file=sys.stderr)
        raise SystemExit(1)


def measure_loudness(path: Path) -> dict[str, float]:
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            "loudnorm=print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    match = re.search(r"\{[\s\S]*\}", result.stderr)
    if not match:
        raise RuntimeError(f"loudnorm measurement failed for {path}")
    raw = json.loads(match.group())
    return {
        "measured_i": float(raw["input_i"]),
        "measured_tp": float(raw["input_tp"]),
        "measured_lra": float(raw["input_lra"]),
        "measured_thresh": float(raw["input_thresh"]),
    }


def normalize_file(
    path: Path,
    *,
    backup: bool,
    dry_run: bool,
) -> dict[str, float]:
    before = measure_loudness(path)
    print(
        f"  before: I={before['measured_i']:.1f} LUFS  TP={before['measured_tp']:.1f} dBFS",
        flush=True,
    )

    if dry_run:
        gain = TARGET_I - before["measured_i"]
        print(f"  would apply ~{gain:+.1f} dB to reach {TARGET_I} LUFS", flush=True)
        return before

    backup_path = path.with_name(f"{path.stem}_original{path.suffix}")
    if backup and not backup_path.exists():
        print(f"  backup → {backup_path.name}", flush=True)
        shutil.copy2(path, backup_path)
    elif backup:
        print(f"  backup exists: {backup_path.name}", flush=True)

    tmp_out = path.with_name(f"{path.stem}.normalized.tmp{path.suffix}")
    if tmp_out.exists():
        tmp_out.unlink()

    af = (
        f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}"
        f":measured_I={before['measured_i']}"
        f":measured_TP={before['measured_tp']}"
        f":measured_LRA={before['measured_lra']}"
        f":measured_thresh={before['measured_thresh']}"
        ":linear=true:print_format=summary"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-c:v",
            "copy",
            "-af",
            af,
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(tmp_out),
        ],
        check=True,
    )

    after = measure_loudness(tmp_out)
    print(
        f"  after:  I={after['measured_i']:.1f} LUFS  TP={after['measured_tp']:.1f} dBFS",
        flush=True,
    )
    tmp_out.replace(path)
    return after


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="MP4 files or directories containing *.mp4 (skips *_original.mp4)",
    )
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    require_ffmpeg()

    files: list[Path] = []
    for item in args.paths:
        if item.is_dir():
            files.extend(
                sorted(
                    p
                    for p in item.glob("*.mp4")
                    if not p.stem.endswith("_original")
                    and not p.name.endswith(".normalized.tmp.mp4")
                )
            )
        elif item.suffix == ".mp4" and not item.stem.endswith("_original"):
            files.append(item)

    if not files:
        print("No MP4 files found.", file=sys.stderr)
        raise SystemExit(1)

    print(
        f"Target: {TARGET_I} LUFS integrated, {TARGET_TP} dBFS true peak\n",
        flush=True,
    )
    for path in files:
        print(path.name, flush=True)
        normalize_file(path, backup=not args.no_backup, dry_run=args.dry_run)
        print(flush=True)


if __name__ == "__main__":
    main()
