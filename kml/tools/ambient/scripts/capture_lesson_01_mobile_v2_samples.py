#!/usr/bin/env python3
"""Capture Lesson 1 mobile V2 layout frames (image / kanji / verse)."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mobile_verse_samples" / "lesson_01_v2"
PORT = 8776

STATES = {
    "image_only": """
() => {
  document.querySelector('.ambient-kanji-block')?.classList.remove('is-visible');
  document.querySelector('.ambient-keyword')?.classList.remove('is-visible');
  document.querySelector('.ambient-verse-jp')?.classList.remove('is-visible');
}
""",
    "kanji_keyword": """
() => {
  document.querySelector('.ambient-kanji-block')?.classList.add('is-visible');
  document.querySelector('.ambient-keyword')?.classList.add('is-visible');
  document.querySelector('.ambient-verse-jp')?.classList.remove('is-visible');
}
""",
    "verse_jp": """
() => {
  document.querySelector('.ambient-kanji-block')?.classList.add('is-visible');
  document.querySelector('.ambient-keyword')?.classList.remove('is-visible');
  document.querySelector('.ambient-verse-jp')?.classList.add('is-visible');
}
""",
}


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Run: .venv/bin/pip install playwright", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2.5)

    qs = "collection=lesson_1_foundations&capture=1&typography=mobile-v2"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for vp_name, viewport in {
                "mobile": {"width": 390, "height": 844},
                "desktop": {"width": 1920, "height": 1080},
            }.items():
                for state, js in STATES.items():
                    page = browser.new_page(viewport=viewport)
                    page.goto(f"http://127.0.0.1:{PORT}/index.html?{qs}", wait_until="load", timeout=60_000)
                    page.wait_for_function("() => window.kmlAmbient", timeout=60_000)
                    page.wait_for_timeout(2500)
                    page.evaluate(js)
                    page.wait_for_timeout(500)
                    out = OUT / f"L01_{state}_{vp_name}.png"
                    page.screenshot(path=str(out))
                    page.close()
                    print(out)
    finally:
        server.terminate()
        server.wait(timeout=5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
