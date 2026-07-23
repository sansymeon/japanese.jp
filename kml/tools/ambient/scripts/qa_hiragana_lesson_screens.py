#!/usr/bin/env python3
"""QA screenshots for the hiragana lesson prototype (no video render)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = 8792
SCALE = 0.2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import start_server, stop_server  # noqa: E402

PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
if PLAYWRIGHT_BROWSERS.is_dir():
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

# (label, unscaled ms into the timeline)
SHOTS = [
    ("title", 3000 + 2800 + 4000 + 1600 + 1800),
    ("kana_alone", 18800 + 800 + 600),
    ("kana_romaji", 18800 + 800 + 1200 + 800 + 700),
    ("review", 18800 + 5 * 7300 + 500 + 1000 + 1700),
]

FULL_SHOTS = [
    ("chart", "full", 0),
]


def main() -> int:
    from playwright.sync_api import sync_playwright

    out = ROOT / "analysis_frames" / "hiragana_lesson_qa"
    out.mkdir(parents=True, exist_ok=True)
    server = start_server(ROOT, PORT)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(
                f"http://127.0.0.1:{PORT}/hiragana_lesson.html?scope=test&timingScale={SCALE}",
                wait_until="load",
            )
            page.wait_for_function("() => document.fonts.status === 'loaded'")
            start = page.evaluate("performance.now()")
            for label, ms in SHOTS:
                target = start + ms * SCALE
                page.wait_for_function(
                    f"() => performance.now() >= {target}", timeout=120_000
                )
                page.screenshot(path=str(out / f"{label}.png"))
                print(f"shot: {label}")

            # Chart from the full scope — jump straight there with tiny scale
            page.goto(
                f"http://127.0.0.1:{PORT}/hiragana_lesson.html?scope=full&timingScale=0.012",
                wait_until="load",
            )
            page.wait_for_function("() => document.fonts.status === 'loaded'")
            page.wait_for_function(
                "() => document.querySelector('[data-hl-chart]')?.classList.contains('is-visible')",
                timeout=120_000,
            )
            page.wait_for_timeout(400)
            page.screenshot(path=str(out / "chart.png"))
            print("shot: chart")
            try:
                # At tiny timing scales the highlight pass may already be over.
                page.wait_for_function(
                    "() => document.querySelector('[data-hl-chart]')?.classList.contains('is-highlighting')",
                    timeout=10_000,
                )
                page.wait_for_timeout(150)
                page.screenshot(path=str(out / "chart_highlight.png"))
                print("shot: chart_highlight")
            except Exception:
                print("skip: chart_highlight (pass already finished)")
            page.wait_for_function(
                "() => window.kmlExhibition.presentationEnded === true", timeout=120_000
            )
            print("presentation ended cleanly")
            browser.close()
    finally:
        stop_server(server)
    print(f"→ {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
