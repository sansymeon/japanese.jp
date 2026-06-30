#!/usr/bin/env python3
"""Record Lesson 4 study exhibition — mobile-refine capture + external soundtrack mux."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "foundations_exhibitions" / "ambient_study_lesson_4.mp4"
COLLECTION = ROOT / "exhibition" / "lesson_4_foundations.json"
PORT = 8777
VIEWPORT = {"width": 1920, "height": 1080}


def intro_audio_delay_ms(collection: dict) -> int:
    intro = collection.get("intro") or {}
    timing = collection.get("timing") or {}
    hold = intro.get("holdBeforeMs", 0)
    duration = intro.get("durationMs", 0)
    fade = intro.get("exitFadeMs") or timing.get("introExitFadeMs") or timing.get("fadeMs", 0)
    return int(hold + duration + fade)


def presentation_timeout_ms(collection: dict) -> int:
    """Upper bound for capture playback (avoids hanging if soundtrack never ends)."""
    timing = collection.get("timing") or {}
    intro = collection.get("intro") or {}
    scenes = collection.get("scenes") or []
    scene_ms = timing.get("sceneDurationMs", 22000)
    intro_ms = (
        intro.get("holdBeforeMs", 0)
        + intro.get("durationMs", 0)
        + (intro.get("exitFadeMs") or timing.get("introExitFadeMs") or timing.get("fadeMs", 0))
    )
    ending_ms = (
        (timing.get("gallerySealImageHoldMs") or 9000)
        + (timing.get("gallerySealFadeToBlackMs") or 6500)
        + (timing.get("gallerySealFadeInMs") or 2500)
        + (timing.get("gallerySealCrestFadeLeadMs") or 3000)
        + (timing.get("gallerySealBlackHoldMs") or 1500)
        + 8000
    )
    total = intro_ms + len(scenes) * scene_ms + ending_ms
    return int(total + 45000)


def ensure_deps() -> None:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg is required on PATH.", file=sys.stderr)
        sys.exit(1)
    try:
        import playwright  # noqa: F401
    except ImportError:
        print(
            "Run: .venv/bin/pip install playwright && .venv/bin/playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> int:
    ensure_deps()

    build = ROOT / "scripts" / "build_lesson_04_exhibition.py"
    if build.is_file():
        subprocess.run([sys.executable, str(build)], check=True, cwd=ROOT)

    if not COLLECTION.is_file():
        print(f"Missing {COLLECTION}. Run build_lesson_04_exhibition.py", file=sys.stderr)
        return 1
    if not (ROOT / "assets" / "studies").exists():
        print("Missing assets symlink.", file=sys.stderr)
        return 1

    collection = json.loads(COLLECTION.read_text(encoding="utf-8"))
    audio_delay_ms = intro_audio_delay_ms(collection)
    timeout_ms = presentation_timeout_ms(collection)
    soundtrack = ROOT / (collection.get("soundtrack") or {}).get("main", "audio/study_version_3_minus3db.mp3")
    if not soundtrack.is_file():
        print(f"Missing soundtrack: {soundtrack}", file=sys.stderr)
        return 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = OUTPUT.parent / ".tmp_lesson_04_mobile_refine"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    url = (
        f"http://127.0.0.1:{PORT}/index.html"
        f"?collection=lesson_4_foundations&capture=1&typography=mobile-refine"
    )
    print("Recording Lesson 4 mobile-refine …")
    print(f"  URL: {url}")
    print(f"  Audio delay: {audio_delay_ms} ms")
    print(f"  Max wait: {timeout_ms // 1000}s")

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
                    page.wait_for_timeout(800)
            except Exception:
                page.mouse.click(VIEWPORT["width"] // 2, VIEWPORT["height"] // 2)

            page.evaluate(
                """async () => {
                  if (!window.kmlAmbient) return;
                  if (window.kmlAmbient.ensureAudioUnlocked) {
                    await window.kmlAmbient.ensureAudioUnlocked();
                  }
                  const audio = window.kmlAmbient.mainAudio;
                  if (audio && audio.paused) {
                    try { await audio.play(); } catch (_) {}
                  }
                }"""
            )

            try:
                page.wait_for_function(
                    "() => window.kmlAmbient && window.kmlAmbient.presentationEnded === true",
                    timeout=timeout_ms,
                )
            except Exception:
                print("  Warning: timed out before presentationEnded; closing capture anyway.")
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
                "medium",
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
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
