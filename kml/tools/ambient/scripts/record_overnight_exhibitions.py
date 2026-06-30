#!/usr/bin/env python3
"""
Overnight batch: record extended exhibitions via Playwright.

  1. lessons_1_5_prototype   (~51 min)
  2. lesson_01-05_verses     (~51 min)
  3. lessons_6_10_prototype  (~51 min)
  4. heart_v5                (~98 min) — skipped by default; record manually

Total ~3 hours (Playwright). Heart: OBS + serve.sh. Log: record_overnight.log

Requires: .venv with playwright + chromium, ffmpeg on PATH
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "extended_exhibitions" / "record_overnight.log"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    ensure_deps,
    heart_opening_timeline_ms,
    load_collection,
    mux_video_with_audio,
    presentation_timeout_ms,
    reflections_audio_timeline_ms,
    start_server,
)

DEFAULT_PORT = 8768
HEART_OUT = ROOT / "heart_exhibitions"
REFLECTIONS_OUT = ROOT / "extended_exhibitions"


def log(msg: str, log_file) -> None:
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    log_file.write(line + "\n")
    log_file.flush()


def rebuild_all() -> None:
    scripts = [
        "build_lessons_1_5_prototype.py",
        "build_lesson_01_05_verses_exhibition.py",
        "build_lessons_6_10_prototype.py",
        "build_heart_v5_exhibition.py",
    ]
    for script in scripts:
        subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True, cwd=ROOT)


def record_reflections(collection_id: str, port: int, log_file) -> Path:
    import shutil

    collection = load_collection(ROOT, collection_id)
    intro_delay_ms, main_start_ms, outro_start_ms = reflections_audio_timeline_ms(collection, ROOT)
    timeout_ms = presentation_timeout_ms(collection, ROOT)

    bookends = collection.get("bookends") or {}
    soundtrack = collection.get("soundtrack") or {}
    intro = ROOT / (bookends.get("opening", {}).get("audio") or "audio/fifty_minute_intro.mp3")
    main = ROOT / (soundtrack.get("main") or "audio/-3db_fifty_minutes.mp3")
    outro = ROOT / (bookends.get("closing", {}).get("audio") or "audio/fifty_minute_outro.mp3")

    url = f"http://127.0.0.1:{port}/exhibition.html?collection={collection_id}"
    out_path = REFLECTIONS_OUT / f"{collection_id}.mp4"
    tmp_dir = REFLECTIONS_OUT / f".tmp_{collection_id}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    log(f"START {collection_id} — intro@{intro_delay_ms}ms main@{main_start_ms}ms outro@{outro_start_ms}ms", log_file)
    webm = capture_exhibition_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    filter_complex = (
        f"[1:a]adelay={intro_delay_ms}|{intro_delay_ms}[i];"
        f"[2:a]adelay={main_start_ms}|{main_start_ms}[m];"
        f"[3:a]adelay={outro_start_ms}|{outro_start_ms}[o];"
        f"[i][m][o]amix=inputs=3:duration=longest:dropout_transition=0[a]"
    )
    tmp_mux = tmp_dir / "muxed.mp4"
    mux_video_with_audio(
        webm=webm,
        output_mp4=tmp_mux,
        filter_complex=filter_complex,
        audio_inputs=[intro, main, outro],
    )
    shutil.move(str(tmp_mux), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()
    log(f"DONE {collection_id} → {out_path}", log_file)
    return out_path


def record_heart(port: int, log_file) -> Path:
    import shutil

    collection_id = "heart_v5"
    collection = load_collection(ROOT, collection_id)
    flute_delay_ms, ambient_start_ms = heart_opening_timeline_ms(collection, ROOT)
    timeout_ms = presentation_timeout_ms(collection, ROOT)

    bookends = collection.get("bookends") or {}
    flute = ROOT / (bookends.get("opening", {}).get("audio") or "audio/exhibition_flute_intro.mp3")
    ambient = ROOT / (collection.get("soundtrack") or {}).get("main", "audio/ambient_kanji_exhibition.mp3")
    if isinstance(ambient, str):
        ambient = ROOT / ambient

    url = f"http://127.0.0.1:{port}/exhibition.html?collection={collection_id}&camera=guardian"
    out_path = HEART_OUT / f"{collection_id}.mp4"
    tmp_dir = HEART_OUT / f".tmp_{collection_id}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    log(f"START heart_v5 — flute@{flute_delay_ms}ms ambient@{ambient_start_ms}ms", log_file)
    webm = capture_exhibition_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    filter_complex = (
        f"[1:a]adelay={flute_delay_ms}|{flute_delay_ms}[fl];"
        f"[2:a]adelay={ambient_start_ms}|{ambient_start_ms}[amb];"
        f"[fl][amb]amix=inputs=2:duration=longest:dropout_transition=0[a]"
    )
    tmp_mux = tmp_dir / "muxed.mp4"
    mux_video_with_audio(
        webm=webm,
        output_mp4=tmp_mux,
        filter_complex=filter_complex,
        audio_inputs=[flute, ambient],
    )
    shutil.move(str(tmp_mux), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()
    log(f"DONE heart_v5 → {out_path}", log_file)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--rebuild", action="store_true", help="Rebuild all collection JSON first")
    parser.add_argument("--skip-heart", action="store_true")
    parser.add_argument("--skip-lessons-1-5", action="store_true")
    parser.add_argument("--skip-lesson-01-05-verses", action="store_true")
    parser.add_argument("--skip-lessons-6-10", action="store_true")
    args = parser.parse_args()

    ensure_deps()
    REFLECTIONS_OUT.mkdir(parents=True, exist_ok=True)
    HEART_OUT.mkdir(parents=True, exist_ok=True)

    if args.rebuild:
        rebuild_all()

    jobs: list[tuple[str, callable]] = []
    if not args.skip_lessons_1_5:
        jobs.append(("lessons_1_5", lambda: record_reflections("lessons_1_5_prototype", args.port, log_file)))
    if not args.skip_lesson_01_05_verses:
        jobs.append(("lesson_01_05_verses", lambda: record_reflections("lesson_01-05_verses", args.port, log_file)))
    if not args.skip_lessons_6_10:
        jobs.append(("lessons_6_10", lambda: record_reflections("lessons_6_10_prototype", args.port, log_file)))
    if not args.skip_heart:
        jobs.append(("heart_v5", lambda: record_heart(args.port, log_file)))

    if not jobs:
        print("No jobs selected.", file=sys.stderr)
        return 1

    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log("=== Overnight exhibition batch ===", log_file)
        server = start_server(ROOT, args.port)
        t0 = time.time()
        failed = False
        try:
            for name, fn in jobs:
                try:
                    fn()
                except Exception as exc:
                    failed = True
                    log(f"FAILED {name}: {exc}", log_file)
                    log_file.write(traceback.format_exc() + "\n")
                    log_file.flush()
        finally:
            server.terminate()
            server.wait(timeout=5)
        elapsed = time.time() - t0
        log(f"=== Batch finished in {elapsed / 3600:.2f}h (failed={failed}) ===", log_file)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
