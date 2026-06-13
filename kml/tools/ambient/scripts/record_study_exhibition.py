#!/usr/bin/env python3
"""
Record Study Exhibition MP4s via Presentation Mode (capture=1).

Uses exhibition/lesson_XX_study collections (Gallery Seal Ending, no loop).
Output: study_exhibitions/lesson_XX_study.mp4 (gitignored)

Requires:
  pip install playwright
  playwright install chromium
  ffmpeg on PATH

Example:
  python3 scripts/record_study_exhibition.py
  python3 scripts/record_study_exhibition.py --lessons 40
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "study_exhibitions"
AUDIO_PATH = ROOT / "audio" / "study_lesson.mp3"
DEFAULT_PORT = 8765
DEFAULT_LESSONS = (40, 41)
VIEWPORT = {"width": 1920, "height": 1080}


def intro_audio_delay_ms(collection: dict) -> int:
    intro = collection.get("intro") or {}
    timing = collection.get("timing") or {}
    hold = intro.get("holdBeforeMs", 0)
    duration = intro.get("durationMs", 0)
    fade = intro.get("exitFadeMs") or timing.get("introExitFadeMs") or timing.get("fadeMs", 0)
    return int(hold + duration + fade)


def load_exhibition_collection(lesson: int) -> dict:
    path = ROOT / "exhibition" / f"lesson_{lesson}_study.json"
    if not path.is_file():
        raise FileNotFoundError(f"Missing exhibition build: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_deps() -> None:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg is required on PATH.", file=sys.stderr)
        sys.exit(1)
    try:
        import playwright  # noqa: F401
    except ImportError:
        print(
            "Playwright is required:\n"
            "  pip install playwright\n"
            "  playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)


def start_server(port: int) -> subprocess.Popen:
    if not (ROOT / "assets" / "studies").exists():
        print(
            "Missing assets symlink. From kml/tools/ambient run:\n"
            "  ln -s ../../assets assets",
            file=sys.stderr,
        )
        sys.exit(1)
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    return proc


def record_lesson(*, lesson: int, port: int, output_dir: Path) -> Path:
    from playwright.sync_api import sync_playwright

    collection = load_exhibition_collection(lesson)
    audio_delay_ms = intro_audio_delay_ms(collection)
    collection_name = f"lesson_{lesson}_study"
    url = f"http://127.0.0.1:{port}/index.html?collection={collection_name}&capture=1"
    out_path = output_dir / f"lesson_{lesson}_study.mp4"
    tmp_dir = output_dir / f".tmp_lesson_{lesson}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording lesson {lesson} …")
    print(f"  URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--autoplay-policy=no-user-gesture-required",
                "--disable-dev-shm-usage",
            ],
        )
        context = browser.new_context(
            viewport=VIEWPORT,
            record_video_dir=str(tmp_dir),
            record_video_size=VIEWPORT,
            color_scheme="dark",
        )
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=180_000)

        try:
            gate = page.locator("[data-ambient-autoplay-gate]")
            gate.wait_for(state="visible", timeout=8000)
            gate.click()
        except Exception:
            page.mouse.click(VIEWPORT["width"] // 2, VIEWPORT["height"] // 2)

        page.wait_for_function(
            "() => window.kmlAmbient && window.kmlAmbient.presentationEnded === true",
            timeout=900_000,
        )
        page.wait_for_timeout(1200)

        video = page.video
        page.close()
        video_path = video.path() if video else None
        context.close()
        browser.close()

    webm_files = list(tmp_dir.glob("*.webm"))
    webm = Path(video_path) if video_path else (webm_files[0] if webm_files else None)
    if not webm or not webm.is_file():
        raise RuntimeError(f"No video captured for lesson {lesson}")

    if not AUDIO_PATH.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {AUDIO_PATH}")

    audio_delay_s = audio_delay_ms / 1000.0
    tmp_mp4 = tmp_dir / "muxed.mp4"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(webm),
            "-itsoffset",
            f"{audio_delay_s:.3f}",
            "-i",
            str(AUDIO_PATH),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
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
            "-shortest",
            str(tmp_mp4),
        ],
        check=True,
    )

    shutil.move(str(tmp_mp4), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()

    print(f"  → {out_path}")
    return out_path


def build_exhibition_configs(lessons: list[int]) -> None:
    builders = {
        37: "build_lesson_37_exhibition.py",
        38: "build_lesson_38_exhibition.py",
        39: "build_lesson_39_exhibition.py",
        40: "build_lesson_40_exhibition.py",
        41: "build_lesson_41_exhibition.py",
    }
    for lesson in lessons:
        script = builders.get(lesson)
        if not script:
            continue
        path = ROOT / "scripts" / script
        if path.is_file():
            subprocess.run([sys.executable, str(path)], check=True, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lessons",
        type=int,
        nargs="+",
        default=list(DEFAULT_LESSONS),
        help=f"Lesson numbers to record (default: {list(DEFAULT_LESSONS)})",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Output folder (gitignored)",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip rebuilding exhibition JSON before recording",
    )
    args = parser.parse_args()

    ensure_deps()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_build:
        build_exhibition_configs(args.lessons)

    server = start_server(args.port)
    try:
        for lesson in args.lessons:
            record_lesson(lesson=lesson, port=args.port, output_dir=args.output_dir)
    finally:
        server.terminate()
        server.wait(timeout=5)

    print(f"\nDone. MP4s in {args.output_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
