#!/usr/bin/env python3
"""Record Lesson N foundations exhibition MP4 (Lesson 5 mobile-refine standard).

Output: collections/lesson_NN/foundations_lesson_NN.mp4

Usage:
  python3 scripts/record_lesson_foundations.py --lesson 33 --rebuild
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
DEFAULT_PORT = 8790
VIEWPORT = {"width": 1920, "height": 1080}
SUPPORTED = [11, 12, 13, 14] + list(range(33, 38))
BUILD_SCRIPT = "build_lesson_foundations_exhibition.py"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    assert_local_noto_serif_files,
    assert_local_yuji_syuku_files,
    ensure_deps,
    ensure_noto_serif_jp_ready,
    ensure_yuji_syuku_ready,
    launch_recording_browser,
    mux_exhibition_soundtrack,
    new_recording_context,
)


def collection_name(lesson: int) -> str:
    return f"lesson_{lesson}_foundations"


def exhibition_json(lesson: int) -> Path:
    return ROOT / "exhibition" / f"{collection_name(lesson)}.json"


def intro_audio_delay_ms(collection: dict) -> int:
    intro = collection.get("intro") or {}
    timing = collection.get("timing") or {}
    hold = intro.get("holdBeforeMs", 0)
    duration = intro.get("durationMs", 0)
    fade = intro.get("exitFadeMs") or timing.get("introExitFadeMs") or timing.get("fadeMs", 0)
    return int(hold + duration + fade)


def presentation_timeout_ms(collection: dict) -> int:
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
    return int(intro_ms + len(scenes) * scene_ms + ending_ms + 45000)


def record(*, lesson: int, port: int) -> Path:
    path = exhibition_json(lesson)
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}. Run with --rebuild.")
    collection = json.loads(path.read_text(encoding="utf-8"))
    audio_delay_ms = intro_audio_delay_ms(collection)
    timeout_ms = presentation_timeout_ms(collection)
    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    out_dir = ROOT / "collections" / f"lesson_{lesson:02d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"foundations_lesson_{lesson:02d}.mp4"
    tmp_dir = out_dir / f".tmp_foundations_lesson_{lesson:02d}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)

    cid = collection_name(lesson)
    url = (
        f"http://127.0.0.1:{port}/index.html"
        f"?collection={cid}&capture=1&typography=mobile-refine"
    )
    print(f"Recording {cid} → {out_path.name}")
    print(f"  URL: {url}")
    print(f"  Audio delay: {audio_delay_ms} ms")
    print(f"  Max wait: {timeout_ms // 1000}s")

    assert_local_noto_serif_files()
    assert_local_yuji_syuku_files()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = launch_recording_browser(p)
        context = new_recording_context(
            browser,
            viewport=VIEWPORT,
            record_video_dir=tmp_dir,
        )
        page = context.new_page()
        page.goto(url, wait_until="load", timeout=120_000)
        page.wait_for_function("() => window.kmlAmbient", timeout=120_000)
        page.wait_for_function(
            "() => document.fonts && document.fonts.status === 'loaded'",
            timeout=120_000,
        )
        ensure_noto_serif_jp_ready(page)
        ensure_yuji_syuku_ready(page)

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
        raise RuntimeError(f"No video captured for lesson {lesson}")

    tmp_mp4 = tmp_dir / "muxed.mp4"
    mux_exhibition_soundtrack(
        webm=webm,
        output_mp4=tmp_mp4,
        soundtrack=soundtrack,
        soundtrack_start_ms=audio_delay_ms,
    )
    shutil.move(str(tmp_mp4), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()
    print(f"  → {out_path}")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, required=True, choices=SUPPORTED)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()

    ensure_deps()

    if args.rebuild:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / BUILD_SCRIPT),
                "--lesson",
                str(args.lesson),
            ],
            check=True,
            cwd=ROOT,
        )

    if not (ROOT / "assets" / "studies").exists():
        print("Missing assets symlink.", file=sys.stderr)
        return 1

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(args.port), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    try:
        record(lesson=args.lesson, port=args.port)
    finally:
        try:
            server.terminate()
            server.wait(timeout=5)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
