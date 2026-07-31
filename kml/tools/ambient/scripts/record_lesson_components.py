#!/usr/bin/env python3
"""Record Lesson N Kanji Components MP4 via Playwright.

Output: collections/lesson_NN/components_lesson_NN.mp4

Usage:
  python3 scripts/record_lesson_components.py --lesson 1 --rebuild
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
DEFAULT_PORT = 9780
VIEWPORT = {"width": 1920, "height": 1080}
SUPPORTED = list(range(1, 31))
BUILD_SCRIPT = "build_kanji_components.py"

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


def collection_id(lesson: int) -> str:
    return f"lesson_{lesson:02d}_components"


def collection_json(lesson: int) -> Path:
    return ROOT / "collections" / f"lesson_{lesson:02d}" / f"{collection_id(lesson)}.json"


def estimate_timeout_ms(collection: dict) -> int:
    timing = collection.get("timing") or {}
    intro = collection.get("introTiming") or {}

    def g(d: dict, key: str, default: int) -> int:
        return int(d.get(key, default))

    hero = g(timing, "heroFadeInMs", 1800)
    after_hero = g(timing, "afterHeroPauseMs", 900)
    arrive = g(timing, "componentArriveMs", 1400)
    stagger = g(timing, "componentStaggerMs", 1700)
    after_comp = g(timing, "afterComponentsPauseMs", 1400)
    kw_in = g(timing, "keywordFadeInMs", 1400)
    kw_hold = g(timing, "keywordHoldMs", 3200)
    kw_out = g(timing, "keywordFadeOutMs", 1100)
    after_kw = g(timing, "afterKeywordsPauseMs", 900)
    leave = g(timing, "componentsFadeOutMs", 1600)
    alone = g(timing, "heroAloneMs", 2400)
    cross = g(timing, "crossfadeMs", 1600)
    black = g(timing, "blackBetweenMs", 700)

    intro_ms = (
        g(intro, "headingFadeInMs", 1400)
        + g(intro, "glyphFadeInMs", 2000)
        + g(intro, "glyphAloneHoldMs", 2800)
        + g(intro, "labelFadeInMs", 1600)
        + g(intro, "completeHoldMs", 4500)
        + g(intro, "fadeOutMs", 1800)
        + g(intro, "blackAfterMs", 900)
        + cross
        + black
    )

    crest_ms = (
        g(timing, "crestBlackBeforeMs", 900)
        + g(timing, "crestRevealMs", 2800)
        + g(timing, "crestHoldMs", 1400)
        + g(timing, "soundtrackFadeMs", 8000)
        + g(timing, "crestFadeOutMs", 3500)
        + g(timing, "crestBlackAfterMs", 800)
    )

    total = crest_ms
    for scene in collection.get("scenes") or []:
        stype = scene.get("type") or "kanji"
        if stype in ("newComponent", "newFamily"):
            total += intro_ms
            continue
        n = len(scene.get("components") or [])
        if n <= 0:
            comps = 0
        elif n == 1:
            comps = arrive
        else:
            comps = arrive + (n - 1) * stagger
        total += (
            hero
            + after_hero
            + comps
            + after_comp
            + kw_in
            + kw_hold
            + kw_out
            + after_kw
            + leave
            + alone
            + cross
            + black
        )
    # Gate + font settle + buffer
    return int(total + 120_000)


def record(*, lesson: int, port: int) -> Path:
    path = collection_json(lesson)
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}. Run with --rebuild.")
    collection = json.loads(path.read_text(encoding="utf-8"))
    timeout_ms = estimate_timeout_ms(collection)
    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    out_dir = ROOT / "collections" / f"lesson_{lesson:02d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"components_lesson_{lesson:02d}.mp4"
    tmp_dir = out_dir / f".tmp_components_lesson_{lesson:02d}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)

    cid = collection_id(lesson)
    url = (
        f"http://127.0.0.1:{port}/kanji-components.html"
        f"?collection={cid}&capture=1"
    )
    print(f"Recording {cid} → {out_path.name}")
    print(f"  URL: {url}")
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
        page.wait_for_function(
            "() => window.KmlKanjiComponentsPlayer",
            timeout=120_000,
        )
        page.wait_for_function(
            "() => document.fonts && document.fonts.status === 'loaded'",
            timeout=120_000,
        )
        ensure_noto_serif_jp_ready(page)
        ensure_yuji_syuku_ready(page)

        gate = page.locator("[data-kc-autoplay-gate]")
        try:
            if gate.is_visible():
                gate.click()
            else:
                page.wait_for_timeout(800)
        except Exception:
            page.mouse.click(VIEWPORT["width"] // 2, VIEWPORT["height"] // 2)

        try:
            page.wait_for_function(
                "() => window.KmlKanjiComponentsPlayer"
                " && window.KmlKanjiComponentsPlayer.presentationEnded === true",
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
        soundtrack_start_ms=0,
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
            [sys.executable, str(ROOT / "scripts" / BUILD_SCRIPT)],
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
