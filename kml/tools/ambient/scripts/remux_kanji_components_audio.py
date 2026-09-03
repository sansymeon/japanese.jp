#!/usr/bin/env python3
"""Replace Kanji Components MP4 audio with the current soundtrack master.

Keeps the existing H.264 video stream (-c:v copy). Does not recapture visuals.
Trims the soundtrack to the video duration and applies the standard 8s end fade.

Originals are copied to components_lesson_NN.pre_audio_remux.mp4 and kept.

Usage:
  python3 scripts/remux_kanji_components_audio.py --lesson 52
  python3 scripts/remux_kanji_components_audio.py --all --workers 4
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED = list(range(1, 154))
SOUNDTRACK = ROOT / "audio" / "kanji_components.mp3"
BACKUP_SUFFIX = ".pre_audio_remux.mp4"
SILENCE_DB = -45.0
DURATION_TOLERANCE_S = 0.05

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    exhibition_soundtrack_filter,
    probe_duration_seconds,
    soundtrack_end_fade_plan,
)


def mp4_path(lesson: int) -> Path:
    return (
        ROOT
        / "collections"
        / f"lesson_{lesson:02d}"
        / f"components_lesson_{lesson:02d}.mp4"
    )


def backup_path(lesson: int) -> Path:
    src = mp4_path(lesson)
    return src.with_name(src.stem + BACKUP_SUFFIX)


def ffprobe_info(path: Path) -> dict:
    return json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration,size,bit_rate:stream=index,codec_type,codec_name,"
                "duration,bit_rate,nb_frames,width,height,avg_frame_rate,sample_rate,channels",
                "-of",
                "json",
                str(path),
            ],
            text=True,
        )
    )


def stream(info: dict, kind: str) -> dict:
    return next(s for s in info["streams"] if s.get("codec_type") == kind)


def volume_mean(path: Path, start: float, length: float) -> float | None:
    if start < 0:
        return None
    r = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-ss",
            f"{start:.3f}",
            "-t",
            f"{length:.3f}",
            "-i",
            str(path),
            "-af",
            "volumedetect",
            "-vn",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    for line in r.stderr.splitlines():
        if "mean_volume" in line:
            return float(line.split(":")[-1].replace("dB", "").strip())
    return None


def video_packet_md5(path: Path) -> str:
    r = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(path),
            "-map",
            "0:v:0",
            "-c",
            "copy",
            "-f",
            "md5",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    for line in (r.stdout + r.stderr).splitlines():
        if line.startswith("MD5="):
            return line.strip()
    raise RuntimeError(f"Could not hash video packets: {path}\n{r.stderr}")


def already_repaired(lesson: int) -> bool:
    src = mp4_path(lesson)
    bak = backup_path(lesson)
    if not src.is_file() or not bak.is_file():
        return False
    mean = volume_mean(src, 270.0, 6.0)
    return mean is not None and mean > SILENCE_DB


def remux_to_tmp(backup: Path, tmp: Path, video_dur: float) -> None:
    filter_complex = exhibition_soundtrack_filter(
        soundtrack_start_ms=0,
        video_duration_s=video_dur,
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(backup),
        "-i",
        str(SOUNDTRACK),
        "-filter_complex",
        filter_complex,
        "-map",
        "0:v:0",
        "-map",
        "[a]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(tmp),
    ]
    subprocess.run(cmd, check=True)


def validate_repaired(path: Path, original: Path) -> list[str]:
    """Return a list of problem strings; empty means OK."""
    problems: list[str] = []
    if not path.is_file():
        return ["repaired MP4 missing"]
    if not original.is_file():
        return ["original backup missing"]

    try:
        new = ffprobe_info(path)
        old = ffprobe_info(original)
    except Exception as exc:
        return [f"ffprobe failed: {exc}"]

    nv, na = stream(new, "video"), stream(new, "audio")
    ov, oa = stream(old, "video"), stream(old, "audio")
    new_dur = float(new["format"]["duration"])
    old_dur = float(old["format"]["duration"])
    video_dur = float(nv.get("duration") or new_dur)
    audio_dur = float(na.get("duration") or new_dur)

    if abs(new_dur - old_dur) > DURATION_TOLERANCE_S:
        problems.append(
            f"format duration changed {old_dur:.6f} → {new_dur:.6f}s"
        )
    if abs(video_dur - float(ov.get("duration") or old_dur)) > DURATION_TOLERANCE_S:
        problems.append("video stream duration changed")
    if abs(video_dur - audio_dur) > 0.25:
        problems.append(
            f"video/audio duration mismatch v={video_dur:.3f} a={audio_dur:.3f}"
        )
    if nv.get("codec_name") != "h264" or nv.get("nb_frames") != ov.get("nb_frames"):
        problems.append(
            f"video stream changed codec={nv.get('codec_name')} "
            f"frames={nv.get('nb_frames')} (was {ov.get('nb_frames')})"
        )
    try:
        if video_packet_md5(path) != video_packet_md5(original):
            problems.append("video packet MD5 differs from original (re-encoded?)")
    except Exception as exc:
        problems.append(f"video MD5 check failed: {exc}")

    checks = [
        ("4:30", 270.0, 6.0, "music"),
        ("6:00", 360.0, 6.0, "music"),
        ("final minute", max(0.0, new_dur - 50.0), 8.0, "music"),
        ("pre-fade", max(0.0, new_dur - 16.0), 4.0, "music"),
        ("final 2s", max(0.0, new_dur - 2.0), 1.8, "fade"),
    ]
    levels: dict[str, float | None] = {}
    for label, start, length, kind in checks:
        if start + length > new_dur + 0.2:
            continue
        mean = volume_mean(path, start, length)
        levels[label] = mean
        if mean is None:
            problems.append(f"{label}: no volume reading")
            continue
        if kind == "music" and mean < SILENCE_DB:
            problems.append(f"{label}: silence/too quiet ({mean:.1f} dB)")
        if kind == "fade" and mean > -25.0:
            problems.append(f"{label}: fade too loud ({mean:.1f} dB)")

    pre = levels.get("pre-fade")
    fade = levels.get("final 2s")
    if pre is not None and fade is not None and fade > pre - 6.0:
        problems.append(
            f"end fade not quieter than pre-fade ({fade:.1f} vs {pre:.1f} dB)"
        )
    return problems


def remux_lesson(lesson: int, *, skip_repaired: bool = True) -> dict:
    src = mp4_path(lesson)
    bak = backup_path(lesson)
    result = {
        "lesson": lesson,
        "status": "ok",
        "skipped": False,
        "problems": [],
        "path": str(src),
    }
    if not src.is_file():
        result["status"] = "fail"
        result["problems"] = ["source MP4 missing"]
        return result
    if not SOUNDTRACK.is_file():
        result["status"] = "fail"
        result["problems"] = [f"missing soundtrack {SOUNDTRACK}"]
        return result

    if skip_repaired and already_repaired(lesson):
        result["skipped"] = True
        result["status"] = "skipped"
        return result

    if not bak.is_file():
        shutil.copy2(src, bak)

    tmp = src.with_name(f"{src.stem}.remux.tmp.mp4")
    if tmp.exists():
        tmp.unlink()

    try:
        video_dur = probe_duration_seconds(bak)
        fade_start, fade_s = soundtrack_end_fade_plan(video_dur)
        remux_to_tmp(bak, tmp, video_dur)
        problems = validate_repaired(tmp, bak)
        if problems:
            result["status"] = "fail"
            result["problems"] = problems
            if tmp.exists():
                tmp.unlink()
            return result
        shutil.move(str(tmp), str(src))
        result["fade"] = f"{fade_s:.1f}s from {fade_start:.1f}s"
        return result
    except Exception as exc:
        result["status"] = "fail"
        result["problems"] = [str(exc)]
        if tmp.exists():
            tmp.unlink()
        return result


def _validate_one_row(lesson: int) -> dict:
    src = mp4_path(lesson)
    bak = backup_path(lesson)
    row = {
        "lesson": lesson,
        "present": src.is_file(),
        "backup": bak.is_file(),
        "problems": [],
    }
    if not src.is_file():
        row["problems"] = ["MP4 missing"]
        return row
    original = bak if bak.is_file() else src
    row["problems"] = validate_repaired(src, original)
    try:
        info = ffprobe_info(src)
        v, a = stream(info, "video"), stream(info, "audio")
        row["format_dur"] = float(info["format"]["duration"])
        row["video_dur"] = float(v.get("duration") or row["format_dur"])
        row["audio_dur"] = float(a.get("duration") or row["format_dur"])
        row["size"] = int(info["format"]["size"])
        row["frames"] = v.get("nb_frames")
        if bak.is_file():
            old = ffprobe_info(bak)
            row["orig_dur"] = float(old["format"]["duration"])
        row["vol_430"] = volume_mean(src, 270.0, 6.0)
        row["vol_600"] = volume_mean(src, 360.0, 6.0)
        row["vol_final_min"] = volume_mean(
            src, max(0.0, row["format_dur"] - 50.0), 8.0
        )
        row["vol_final_10"] = volume_mean(
            src, max(0.0, row["format_dur"] - 10.0), 8.0
        )
        row["vol_final_2"] = volume_mean(
            src, max(0.0, row["format_dur"] - 2.0), 1.8
        )
    except Exception as exc:
        row["problems"].append(f"probe/volume failed: {exc}")
    return row


def validate_all(lessons: list[int], *, workers: int = 6) -> list[dict]:
    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futs = {pool.submit(_validate_one_row, n): n for n in lessons}
        by_lesson = {}
        for fut in as_completed(futs):
            row = fut.result()
            by_lesson[row["lesson"]] = row
    return [by_lesson[n] for n in lessons]


def print_validation_report(rows: list[dict], elapsed_s: float) -> int:
    present = sum(1 for r in rows if r.get("present"))
    failed = [r for r in rows if r.get("problems")]
    print("\n======== Kanji Components audio remux validation ========")
    print(f"1. Files present: {present}/153")

    mismatches = []
    for r in rows:
        if not r.get("present"):
            continue
        vd, ad = r.get("video_dur"), r.get("audio_dur")
        if vd is None or ad is None:
            mismatches.append(r["lesson"])
        elif abs(vd - ad) > 0.25:
            mismatches.append(r["lesson"])
    print(
        "2. Video vs audio-stream duration: "
        + ("all within 0.25s" if not mismatches else f"MISMATCH lessons {mismatches}")
    )

    silence_before_fade = [
        r["lesson"]
        for r in rows
        if r.get("present")
        and (
            (r.get("vol_430") is not None and r["vol_430"] < SILENCE_DB)
            or (r.get("vol_600") is not None and r["vol_600"] < SILENCE_DB)
            or (r.get("vol_final_min") is not None and r["vol_final_min"] < SILENCE_DB)
        )
    ]
    print(
        "3. Unintended long silence before fade: "
        + ("none" if not silence_before_fade else f"YES lessons {silence_before_fade}")
    )

    copy_fails = [
        r["lesson"]
        for r in rows
        if any("MD5" in p or "video stream changed" in p for p in r.get("problems", []))
    ]
    print(
        "4. Video streams copied (not re-encoded): "
        + ("yes" if not copy_fails else f"NO lessons {copy_fails}")
    )

    dur_fails = [
        r["lesson"]
        for r in rows
        if r.get("orig_dur") is not None
        and abs(r["format_dur"] - r["orig_dur"]) > DURATION_TOLERANCE_S
    ]
    print(
        "5. Duration vs originals: "
        + ("no significant changes" if not dur_fails else f"CHANGED lessons {dur_fails}")
    )

    print(
        "6. Failed or anomalous files: "
        + ("none" if not failed else f"{len(failed)} (see below)")
    )
    for r in failed:
        print(f"   L{r['lesson']:03d}: {'; '.join(r['problems'])}")

    mins, secs = divmod(int(round(elapsed_s)), 60)
    print(f"7. Total processing time: {mins}m {secs:02d}s ({elapsed_s:.1f}s)")

    def avg(key):
        vals = [r[key] for r in rows if r.get(key) is not None]
        return sum(vals) / len(vals) if vals else None

    print("\nSpot-check mean volume (all 153, averages):")
    for key, label in (
        ("vol_430", "4:30"),
        ("vol_600", "6:00"),
        ("vol_final_min", "final minute (t-50s)"),
        ("vol_final_10", "final 10 seconds"),
        ("vol_final_2", "final 2 seconds (fade)"),
    ):
        a = avg(key)
        lo = min((r[key] for r in rows if r.get(key) is not None), default=None)
        hi = max((r[key] for r in rows if r.get(key) is not None), default=None)
        if a is None:
            print(f"   {label}: n/a")
        else:
            print(f"   {label}: avg {a:.1f} dB  range {lo:.1f} … {hi:.1f} dB")

    # Explicit spread matching the original investigation set.
    print("\nPer-lesson spot sample:")
    print(
        f"{'L':>3} {'dur':>8} {'v-a':>7} {'4:30':>8} {'6:00':>8} "
        f"{'t-50s':>8} {'last10':>8} {'last2':>8}  status"
    )
    for n in (1, 10, 25, 40, 50, 51, 52, 86, 153):
        r = next((x for x in rows if x["lesson"] == n), None)
        if not r or not r.get("present"):
            print(f"{n:3d}  MISSING")
            continue
        gap = (r.get("video_dur") or 0) - (r.get("audio_dur") or 0)
        st = "OK" if not r["problems"] else "; ".join(r["problems"])
        def f(v):
            return f"{v:7.1f}" if isinstance(v, float) else "    n/a"
        print(
            f"{n:3d} {r.get('format_dur', 0):8.2f} {gap:7.3f} "
            f"{f(r.get('vol_430'))} {f(r.get('vol_600'))} "
            f"{f(r.get('vol_final_min'))} {f(r.get('vol_final_10'))} "
            f"{f(r.get('vol_final_2'))}  {st}"
        )

    print("========================================================")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--lesson", type=int, choices=SUPPORTED)
    group.add_argument("--all", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remux even if a repaired file already has music.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Skip remux; only validate existing MP4s against backups.",
    )
    args = parser.parse_args()

    started = time.monotonic()
    lessons = SUPPORTED if args.all else [args.lesson]

    if not args.validate_only:
        skip_repaired = not args.force
        if args.all:
            print(
                f"Remuxing Components L1–153  workers={args.workers}  "
                f"skip_already_repaired={skip_repaired}"
            )
            failures = []
            skipped = []
            ok = []
            with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
                futs = {
                    pool.submit(remux_lesson, n, skip_repaired=skip_repaired): n
                    for n in lessons
                }
                done = 0
                for fut in as_completed(futs):
                    done += 1
                    r = fut.result()
                    tag = r["status"]
                    extra = ""
                    if r["skipped"]:
                        skipped.append(r["lesson"])
                        extra = " (already repaired)"
                    elif r["status"] == "fail":
                        failures.append(r)
                        extra = " " + "; ".join(r["problems"])
                    else:
                        ok.append(r["lesson"])
                    print(
                        f"  [{done:3d}/153] L{r['lesson']:03d} {tag}{extra}",
                        flush=True,
                    )
            print(
                f"Remux finished: ok={len(ok)} skipped={len(skipped)} "
                f"failed={len(failures)}"
            )
            if failures:
                print("Per-file remux failures (originals left in place):")
                for r in failures:
                    print(f"  L{r['lesson']:03d}: {'; '.join(r['problems'])}")
        else:
            r = remux_lesson(args.lesson, skip_repaired=skip_repaired)
            print(r)
            if r["status"] == "fail":
                return 1

    rows = validate_all(lessons, workers=max(2, args.workers))
    elapsed = time.monotonic() - started
    return print_validation_report(rows, elapsed)


if __name__ == "__main__":
    raise SystemExit(main())
