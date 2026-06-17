#!/usr/bin/env python3
"""Record Lesson 1 study exhibition — mobile readability refine (mobile-refine)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "study_exhibitions" / "lesson_01_study_mobile_refine.mp4"
COLLECTION = ROOT / "exhibition" / "lesson_1_study.json"
PORT = 8775
VIEWPORT = {"width": 1920, "height": 1080}


def intro_audio_delay_ms(collection: dict) -> int:
    intro = collection.get("intro") or {}
    timing = collection.get("timing") or {}
    hold = intro.get("holdBeforeMs", 0)
    duration = intro.get("durationMs", 0)
    fade = intro.get("exitFadeMs") or timing.get("introExitFadeMs") or timing.get("fadeMs", 0)
    return int(hold + duration + fade)


def ensure_deps() -> None:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg is required on PATH.", file=sys.stderr)
        sys.exit(1)
    try:
        import playwright  # noqa: F401
    except ImportError:
        print("Run: .venv/bin/pip install playwright && .venv/bin/playwright install chromium", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    ensure_deps()
    if not COLLECTION.is_file():
        print(f"Missing {COLLECTION}. Run: python3 scripts/build_lesson_01_exhibition.py", file=sys.stderr)
        return 1
    if not (ROOT / "assets" / "studies").exists():
        print("Missing assets symlink.", file=sys.stderr)
        return 1

    collection = json.loads(COLLECTION.read_text(encoding="utf-8"))
    audio_delay_ms = intro_audio_delay_ms(collection)
    soundtrack = ROOT / (collection.get("soundtrack") or {}).get("main", "audio/study_version_3_minus3db.mp3")
    if not soundtrack.is_file():
        print(f"Missing soundtrack: {soundtrack}", file=sys.stderr)
        return 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = OUTPUT.parent / ".tmp_lesson_01_mobile_refine"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    url = (
        f"http://127.0.0.1:{PORT}/index.html"
        f"?collection=lesson_1_study&capture=1&typography=mobile-refine"
    )
    print("Recording Lesson 1 mobile refine …")
    print(f"  URL: {url}")

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--autoplay-policy=no-user-gesture-required", "--disable-dev-shm-usage"],
            )
            context = browser.new_context(
                viewport=VIEWPORT,
                record_video_dir=str(tmp_dir),
                record_video_size=VIEWPORT,
                color_scheme="dark",
            )
            page = context.new_page()
            page.goto(url, wait_until="load", timeout=120_000)
            page.wait_for_function("() => window.kmlAmbient", timeout=120_000)

            gate = page.locator("[data-ambient-autoplay-gate]")
            try:
                if gate.is_visible():
                    gate.click()
                else:
                    page.wait_for_timeout(300)
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
            raise RuntimeError("No video captured")

        tmp_mp4 = tmp_dir / "muxed.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(webm),
                "-itsoffset",
                f"{audio_delay_ms / 1000:.3f}",
                "-i",
                str(soundtrack),
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
        shutil.move(str(tmp_mp4), str(OUTPUT))
        for f in tmp_dir.iterdir():
            f.unlink()
        tmp_dir.rmdir()

        print(f"  → {OUTPUT}")
        return 0
    finally:
        try:
            server.terminate()
            server.wait(timeout=5)
        except PermissionError:
            pass
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
