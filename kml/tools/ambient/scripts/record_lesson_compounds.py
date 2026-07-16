#!/usr/bin/env python3
"""Record lesson compounds exhibition MP4 via Playwright.

Output: collections/lesson_NN/compounds_lesson_NN.mp4
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8780

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    apply_mp4_end_fade,
    capture_exhibition_webm,
    compounds_exhibition_soundtrack_start_ms,
    ensure_deps,
    exhibition_record_url,
    format_mmss,
    load_collection,
    mux_video_with_audio,
    presentation_timeout_ms,
    start_server,
    stop_server,
)

BUILDERS = {
    1: "build_lesson_01_compounds_exhibition.py",
    2: "build_lesson_02_compounds_exhibition.py",
    3: "build_lesson_03_compounds_exhibition.py",
    4: "build_lesson_04_compounds_exhibition.py",
    5: "build_lesson_05_compounds_exhibition.py",
    6: "build_lesson_06_compounds_exhibition.py",
    7: "build_lesson_07_compounds_exhibition.py",
    8: "build_lesson_08_compounds_exhibition.py",
    9: "build_lesson_09_compounds_exhibition.py",
    10: "build_lesson_10_compounds_exhibition.py",
}

# Lesson 8: fade out from 20:10, then cut (10s fade).
COMPOUNDS_OUTPUT_FADES: dict[int, tuple[int, int]] = {
    8: (20 * 60 + 10, 10),
}


def collection_id(lesson: int) -> str:
    return f"lesson_{lesson:02d}_compounds"


def record(*, lesson: int, port: int) -> Path:
    cid = collection_id(lesson)
    collection = load_collection(ROOT, cid)
    soundtrack_start_ms = compounds_exhibition_soundtrack_start_ms(collection)
    timeout_ms = presentation_timeout_ms(collection, ROOT)

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    display = dict(collection.get("display") or {})
    display.setdefault("typography", "mobile-refine")
    display.setdefault("verseMode", "sequential")
    url = exhibition_record_url(port=port, collection_id=cid, display=display)

    out_dir = ROOT / "collections" / f"lesson_{lesson:02d}"
    out_path = out_dir / f"compounds_lesson_{lesson:02d}.mp4"
    tmp_dir = out_dir / f".tmp_compounds_lesson_{lesson:02d}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {cid} → {out_path.name}")
    print(f"  URL: {url}")
    print(f"  Soundtrack @ {soundtrack_start_ms} ms")
    print(f"  Max wait: {timeout_ms // 1000}s")

    webm = capture_exhibition_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    filter_complex = (
        f"[1:a]adelay={soundtrack_start_ms}|{soundtrack_start_ms}[m];"
        f"[m]asetpts=PTS-STARTPTS[a]"
    )
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

    fade = COMPOUNDS_OUTPUT_FADES.get(lesson)
    if fade:
        fade_start_s, fade_duration_s = fade
        apply_mp4_end_fade(
            out_path, fade_start_s=fade_start_s, fade_duration_s=fade_duration_s
        )
        cut_s = fade_start_s + fade_duration_s
        print(
            f"  → {out_path} "
            f"(fade @ {format_mmss(fade_start_s)}, cut @ {format_mmss(cut_s)})"
        )
    else:
        print(f"  → {out_path}")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, required=True, choices=sorted(BUILDERS))
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument(
        "--fade-only",
        action="store_true",
        help="Apply configured end fade-out trim to existing MP4 (no remux)",
    )
    args = parser.parse_args()

    ensure_deps()

    if args.fade_only:
        fade = COMPOUNDS_OUTPUT_FADES.get(args.lesson)
        if not fade:
            print(f"No compounds fade configured for lesson {args.lesson}", file=sys.stderr)
            return 1
        out_path = (
            ROOT
            / "collections"
            / f"lesson_{args.lesson:02d}"
            / f"compounds_lesson_{args.lesson:02d}.mp4"
        )
        if not out_path.is_file():
            raise FileNotFoundError(out_path)
        fade_start_s, fade_duration_s = fade
        apply_mp4_end_fade(
            out_path, fade_start_s=fade_start_s, fade_duration_s=fade_duration_s
        )
        cut_s = fade_start_s + fade_duration_s
        print(
            f"Faded {out_path.name} "
            f"@ {format_mmss(fade_start_s)}, cut @ {format_mmss(cut_s)}"
        )
        return 0

    if args.rebuild:
        script = BUILDERS[args.lesson]
        subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True, cwd=ROOT)

    server = start_server(ROOT, args.port)
    try:
        record(lesson=args.lesson, port=args.port)
    finally:
        stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
