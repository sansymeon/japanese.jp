#!/usr/bin/env python3
"""Record Grade 5 Stroke Order exhibition MP4s via Playwright.

Output: collections/grade_5/grade_5_strokes_{part:02d}.mp4
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8775
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    ensure_deps,
    grade_stroke_order_soundtrack_start_ms,
    load_collection,
    mux_video_with_audio,
    presentation_timeout_ms,
    start_server,
    stop_server,
)
from grade5_stroke_order_common import (  # noqa: E402
    PART_COUNT,
    STROKE_OUTPUT_DURATION_S,
    STROKE_OUTPUT_FADE_DURATION_S,
    STROKE_OUTPUT_FADE_START_S,
    STROKE_SOUNDTRACK_GAIN_DB,
    collection_id,
)


def apply_stroke_output_fade(path: Path) -> None:
    """Fade video/audio out near soundtrack end and trim the file."""
    tmp = path.with_name(f"{path.stem}.fade.tmp{path.suffix}")
    if tmp.exists():
        tmp.unlink()
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-vf",
            f"fade=t=out:st={STROKE_OUTPUT_FADE_START_S}:d={STROKE_OUTPUT_FADE_DURATION_S}",
            "-af",
            f"afade=t=out:st={STROKE_OUTPUT_FADE_START_S}:d={STROKE_OUTPUT_FADE_DURATION_S}",
            "-t",
            str(STROKE_OUTPUT_DURATION_S),
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(tmp),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    tmp.replace(path)


def soundtrack_filter_complex(start_ms: int) -> str:
    gain = STROKE_SOUNDTRACK_GAIN_DB
    gain_filter = f"volume={gain}dB," if gain else ""
    return (
        f"[1:a]{gain_filter}adelay={start_ms}|{start_ms}[m];"
        f"[m]asetpts=PTS-STARTPTS[a]"
    )


def remux(*, part: int) -> Path:
    """Re-apply soundtrack timing to an existing Playwright capture."""
    cid = collection_id(part)
    collection = load_collection(ROOT, cid)
    soundtrack_start_ms = grade_stroke_order_soundtrack_start_ms(collection)

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    out_path = ROOT / "collections" / "grade_5" / f"grade_5_strokes_{part:02d}.mp4"
    if not out_path.is_file():
        raise FileNotFoundError(f"Missing video: {out_path}")

    tmp_dir = out_path.parent / f".tmp_grade_5_strokes_{part:02d}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_mux = tmp_dir / "muxed.mp4"

    print(f"Remuxing {out_path.name} (soundtrack @ {soundtrack_start_ms} ms, {STROKE_SOUNDTRACK_GAIN_DB:+.1f} dB)")
    filter_complex = soundtrack_filter_complex(soundtrack_start_ms)
    mux_video_with_audio(
        webm=out_path,
        output_mp4=tmp_mux,
        filter_complex=filter_complex,
        audio_inputs=[soundtrack],
        video_from_mp4=True,
    )
    shutil.move(str(tmp_mux), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()
    apply_stroke_output_fade(out_path)

    print(
        f"  → {out_path} (fade @ {STROKE_OUTPUT_FADE_START_S // 60}:"
        f"{STROKE_OUTPUT_FADE_START_S % 60:02d}, cut @ "
        f"{STROKE_OUTPUT_DURATION_S // 60}:{STROKE_OUTPUT_DURATION_S % 60:02d})"
    )
    return out_path


def record(*, part: int, port: int) -> Path:
    cid = collection_id(part)
    collection = load_collection(ROOT, cid)
    soundtrack_start_ms = grade_stroke_order_soundtrack_start_ms(collection)
    meta_runtime = int((collection.get("meta") or {}).get("estimatedContentRuntimeMs") or 0)
    timeout_ms = max(
        presentation_timeout_ms(collection, ROOT),
        meta_runtime + soundtrack_start_ms + 180_000,
    )

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    url = f"http://127.0.0.1:{port}/exhibition.html?collection={cid}"
    out_path = ROOT / "collections" / "grade_5" / f"grade_5_strokes_{part:02d}.mp4"
    tmp_dir = out_path.parent / f".tmp_grade_5_strokes_{part:02d}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {cid} → {out_path.name}")
    print(f"  URL: {url}")
    print(f"  Soundtrack @ {soundtrack_start_ms} ms ({STROKE_SOUNDTRACK_GAIN_DB:+.1f} dB)")
    print(f"  Max wait: {timeout_ms // 1000}s")

    webm = capture_exhibition_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    filter_complex = soundtrack_filter_complex(soundtrack_start_ms)
    tmp_mux = tmp_dir / "muxed.mp4"
    mux_video_with_audio(
        webm=webm,
        output_mp4=tmp_mux,
        filter_complex=filter_complex,
        audio_inputs=[soundtrack],
    )
    shutil.move(str(tmp_mux), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()
    apply_stroke_output_fade(out_path)

    print(
        f"  → {out_path} (fade @ {STROKE_OUTPUT_FADE_START_S // 60}:"
        f"{STROKE_OUTPUT_FADE_START_S % 60:02d}, cut @ "
        f"{STROKE_OUTPUT_DURATION_S // 60}:{STROKE_OUTPUT_DURATION_S % 60:02d})"
    )
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", type=int, choices=range(1, PART_COUNT + 1))
    parser.add_argument("--all", action="store_true", help=f"Record parts 1–{PART_COUNT}")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument(
        "--remux",
        action="store_true",
        help="Re-apply soundtrack to existing MP4 (fix audio sync only)",
    )
    parser.add_argument(
        "--fade",
        action="store_true",
        help="Apply end fade-out trim to existing MP4 (no remux)",
    )
    args = parser.parse_args()

    if not args.part and not args.all:
        parser.error("Specify --part N or --all")

    if shutil.which("ffmpeg") is None:
        print("ffmpeg is required on PATH.", file=sys.stderr)
        sys.exit(1)

    if not args.remux and not args.fade:
        ensure_deps()

    if PLAYWRIGHT_BROWSERS.is_dir():
        import os

        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    parts = list(range(1, PART_COUNT + 1)) if args.all else [args.part]

    if args.rebuild:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_grade_5_stroke_order_exhibition.py"),
                "--all",
            ],
            check=True,
            cwd=ROOT,
        )

    if args.fade:
        for part in parts:
            out_path = ROOT / "collections" / "grade_5" / f"grade_5_strokes_{part:02d}.mp4"
            if not out_path.is_file():
                raise FileNotFoundError(f"Missing video: {out_path}")
            print(f"Fading {out_path.name} …")
            apply_stroke_output_fade(out_path)
            print(f"  → {out_path}")
        return 0

    if args.remux:
        for part in parts:
            remux(part=part)
        return 0

    server = start_server(ROOT, args.port)
    try:
        for part in parts:
            record(part=part, port=args.port)
    finally:
        stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
