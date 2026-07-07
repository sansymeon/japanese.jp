#!/usr/bin/env python3
"""Measure audio levels in lesson MP4s and flag quiet OBS captures.

Compares each file against a reference lesson (default: lesson 5 foundations).
Uses ffmpeg volumedetect + ebur128 integrated loudness.

Typical layout (gitignored locally):
  foundations_exhibitions/lesson_01_foundations_mobile_refine.mp4
  foundations_exhibitions/ambient_study_lesson_5.mp4
  foundations_exhibitions/lesson_1_foundations.mp4
  exhibition/lesson_1_foundations.mp4
  collections/lesson_01/*.mp4

Examples:
  python3 scripts/analyze_lesson_video_audio.py --lesson 1
  python3 scripts/analyze_lesson_video_audio.py --lesson 1 --reference-lesson 5
  python3 scripts/analyze_lesson_video_audio.py path/to/video.mp4 --reference path/to/ref.mp4
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Candidate paths relative to kml/tools/ambient (first match wins per slot).
LESSON_PATTERNS: dict[int, list[str]] = {
    1: [
        "foundations_exhibitions/lesson_01_foundations_mobile_refine.mp4",
        "foundations_exhibitions/lesson_1_foundations.mp4",
        "exhibition/lesson_1_foundations.mp4",
        "collections/lesson_01/lesson_01_foundations.mp4",
        "collections/lesson_01/lesson_1_foundations.mp4",
        "collections/lesson_01/foundations.mp4",
        "collections/lesson_01/lesson_01_reading.mp4",
        "collections/lesson_01/lesson_01_vocabulary.mp4",
        "collections/lesson_01/lesson_01_strokes.mp4",
        "collections/lesson_01/lesson_01_compounds.mp4",
        "collections/lesson_01/lesson_01_gallery.mp4",
    ],
    3: [
        "foundations_exhibitions/ambient_study_lesson_3.mp4",
        "foundations_exhibitions/lesson_3_foundations.mp4",
        "exhibition/lesson_3_foundations.mp4",
        "collections/lesson_03/lesson_03_reading.mp4",
        "collections/lesson_03/lesson_03_vocabulary.mp4",
        "collections/lesson_03/lesson_03_strokes.mp4",
        "collections/lesson_03/lesson_03_gallery.mp4",
    ],
    5: [
        "foundations_exhibitions/ambient_study_lesson_5.mp4",
        "foundations_exhibitions/lesson_5_foundations.mp4",
        "exhibition/lesson_5_foundations.mp4",
        "collections/lesson_05/lesson_05_reading.mp4",
        "collections/lesson_05/lesson_5_foundations.mp4",
    ],
}

# Flag when integrated loudness is this many LU below reference (or below floor).
DEFAULT_DELTA_LU = 3.0
DEFAULT_MIN_LUFS = -24.0


@dataclass
class AudioMetrics:
    path: Path
    duration_s: float | None
    mean_volume_db: float | None
    max_volume_db: float | None
    integrated_lufs: float | None
    true_peak_dbfs: float | None
    has_audio: bool
    error: str | None = None


def ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        print("ffmpeg and ffprobe are required on PATH.", file=sys.stderr)
        sys.exit(1)


def probe_duration(path: Path) -> float | None:
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
        return float(out) if out else None
    except (subprocess.CalledProcessError, ValueError):
        return None


def analyze_audio(path: Path) -> AudioMetrics:
    if not path.is_file():
        return AudioMetrics(
            path=path,
            duration_s=None,
            mean_volume_db=None,
            max_volume_db=None,
            integrated_lufs=None,
            true_peak_dbfs=None,
            has_audio=False,
            error="file not found",
        )

    duration_s = probe_duration(path)

    # volumedetect
    mean_db: float | None = None
    max_db: float | None = None
    has_audio = False
    try:
        vol_out = subprocess.check_output(
            [
                "ffmpeg",
                "-hide_banner",
                "-i",
                str(path),
                "-af",
                "volumedetect",
                "-f",
                "null",
                "-",
            ],
            text=True,
            stderr=subprocess.STDOUT,
        )
        if "n_samples: 0" not in vol_out and "Audio:" in vol_out:
            has_audio = True
        m_mean = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", vol_out)
        m_max = re.search(r"max_volume:\s*([-\d.]+)\s*dB", vol_out)
        if m_mean:
            mean_db = float(m_mean.group(1))
        if m_max:
            max_db = float(m_max.group(1))
    except subprocess.CalledProcessError as exc:
        return AudioMetrics(
            path=path,
            duration_s=duration_s,
            mean_volume_db=None,
            max_volume_db=None,
            integrated_lufs=None,
            true_peak_dbfs=None,
            has_audio=False,
            error=str(exc),
        )

    if not has_audio:
        return AudioMetrics(
            path=path,
            duration_s=duration_s,
            mean_volume_db=mean_db,
            max_volume_db=max_db,
            integrated_lufs=None,
            true_peak_dbfs=None,
            has_audio=False,
            error="no audio stream",
        )

    # ebur128 integrated loudness (slower but standard)
    integrated: float | None = None
    true_peak: float | None = None
    try:
        ebur_out = subprocess.check_output(
            [
                "ffmpeg",
                "-hide_banner",
                "-i",
                str(path),
                "-filter_complex",
                "ebur128=peak=true",
                "-f",
                "null",
                "-",
            ],
            text=True,
            stderr=subprocess.STDOUT,
        )
        m_i = re.search(r"I:\s*([-\d.]+)\s*LUFS", ebur_out)
        m_tp = re.search(r"Peak:\s*([-\d.]+)\s*dBFS", ebur_out)
        if m_i:
            integrated = float(m_i.group(1))
        if m_tp:
            true_peak = float(m_tp.group(1))
    except subprocess.CalledProcessError:
        pass

    return AudioMetrics(
        path=path,
        duration_s=duration_s,
        mean_volume_db=mean_db,
        max_volume_db=max_db,
        integrated_lufs=integrated,
        true_peak_dbfs=true_peak,
        has_audio=True,
    )


def discover_lesson_files(lesson: int, root: Path) -> list[Path]:
    patterns = LESSON_PATTERNS.get(lesson, [])
    found: list[Path] = []
    seen: set[Path] = set()

    for rel in patterns:
        p = (root / rel).resolve()
        if p.is_file() and p not in seen:
            found.append(p)
            seen.add(p)

    # Any MP4 under collections/lesson_XX/
    lesson_dir = root / "collections" / f"lesson_{lesson:02d}"
    if lesson_dir.is_dir():
        for p in sorted(lesson_dir.glob("*.mp4")):
            rp = p.resolve()
            if rp not in seen:
                found.append(rp)
                seen.add(rp)

    # foundations_exhibitions wildcards
    fe = root / "foundations_exhibitions"
    if fe.is_dir():
        for pat in (
            f"*lesson*{lesson}*.mp4",
            f"*lesson_{lesson:02d}*.mp4",
            f"*lesson_{lesson}_*.mp4",
        ):
            for p in sorted(fe.glob(pat)):
                rp = p.resolve()
                if rp not in seen:
                    found.append(rp)
                    seen.add(rp)

    return found


def fmt_db(value: float | None, suffix: str = " dB") -> str:
    if value is None:
        return "—"
    return f"{value:+.1f}{suffix}"


def print_row(label: str, m: AudioMetrics, ref: AudioMetrics | None, delta_lu: float) -> str:
    dur = f"{m.duration_s / 60:.1f} min" if m.duration_s else "—"
    lufs = fmt_db(m.integrated_lufs, " LUFS")
    mean = fmt_db(m.mean_volume_db)
    peak = fmt_db(m.max_volume_db)
    tp = fmt_db(m.true_peak_dbfs)

    flag = ""
    if m.error:
        flag = f"  ⚠ {m.error}"
    elif m.integrated_lufs is not None:
        if m.integrated_lufs < DEFAULT_MIN_LUFS:
            flag = f"  ⚠ below floor ({DEFAULT_MIN_LUFS} LUFS)"
        elif ref and ref.integrated_lufs is not None:
            diff = m.integrated_lufs - ref.integrated_lufs
            if diff < -delta_lu:
                flag = f"  ⚠ {diff:+.1f} LU vs reference (redo suggested)"

    rel = m.path
    try:
        rel = m.path.relative_to(ROOT)
    except ValueError:
        pass

    return (
        f"{label:<28} {dur:>10}  {lufs:>12}  {mean:>10}  {peak:>10}  {tp:>10}"
        f"\n  {rel}{flag}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Explicit MP4 paths (optional; else scan --lesson)",
    )
    parser.add_argument("--lesson", type=int, help="Lesson number to scan (e.g. 1)")
    parser.add_argument(
        "--reference-lesson",
        type=int,
        default=5,
        help="Reference lesson for comparison (default: 5)",
    )
    parser.add_argument("--reference", type=Path, help="Explicit reference MP4")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Ambient root (default: kml/tools/ambient)",
    )
    parser.add_argument(
        "--delta-lu",
        type=float,
        default=DEFAULT_DELTA_LU,
        help=f"Flag if this many LU quieter than reference (default: {DEFAULT_DELTA_LU})",
    )
    args = parser.parse_args()

    ensure_ffmpeg()
    root = args.root.resolve()

    # Resolve files to analyze
    files: list[Path] = [p.resolve() for p in args.paths]
    if args.lesson is not None:
        files.extend(discover_lesson_files(args.lesson, root))
    files = sorted({p for p in files})

    if not files:
        print("No MP4 files found.", file=sys.stderr)
        print(f"  Searched under: {root}", file=sys.stderr)
        if args.lesson:
            print(
                f"  Tip: place lesson {args.lesson} OBS exports in "
                f"{root / 'foundations_exhibitions'} or "
                f"{root / 'collections' / f'lesson_{args.lesson:02d}'}",
                file=sys.stderr,
            )
        return 1

    # Reference
    ref_path = args.reference.resolve() if args.reference else None
    if ref_path is None:
        ref_candidates = discover_lesson_files(args.reference_lesson, root)
        ref_path = ref_candidates[0] if ref_candidates else None

    ref_metrics: AudioMetrics | None = None
    if ref_path:
        print(f"Reference: {ref_path}")
        ref_metrics = analyze_audio(ref_path)
        if ref_metrics.integrated_lufs is not None:
            print(
                f"  → {ref_metrics.integrated_lufs:+.1f} LUFS"
                f"  mean {fmt_db(ref_metrics.mean_volume_db)}"
                f"  peak {fmt_db(ref_metrics.max_volume_db)}"
            )
        print()

    print(
        f"{'File':<28} {'Duration':>10}  {'Integrated':>12}  {'Mean':>10}  "
        f"{'Max':>10}  {'TruePk':>10}"
    )
    print("-" * 88)

    redo: list[Path] = []
    for i, path in enumerate(files):
        label = path.stem[:28]
        m = analyze_audio(path)
        print(print_row(label, m, ref_metrics, args.delta_lu))
        if m.error:
            continue
        if m.integrated_lufs is not None:
            if m.integrated_lufs < DEFAULT_MIN_LUFS:
                redo.append(path)
            elif ref_metrics and ref_metrics.integrated_lufs is not None:
                if m.integrated_lufs - ref_metrics.integrated_lufs < -args.delta_lu:
                    redo.append(path)
        print()

    if redo:
        print("REDO SUGGESTED:")
        for p in redo:
            try:
                print(f"  - {p.relative_to(ROOT)}")
            except ValueError:
                print(f"  - {p}")
        return 2

    print("All analyzed files are within tolerance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
