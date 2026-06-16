#!/usr/bin/env python3
"""Capture before/after typography screenshots for representative Heart exhibits."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "typography_samples"
PORT = 8768
VIEWPORT = {"width": 1920, "height": 1080}

# (exhibit index, slug, background type)
SAMPLES = [
    (0, "love", "warm_portrait"),
    (13, "concept", "water_reflection"),
    (17, "fear", "mist_bridge"),
    (20, "melancholy", "rain_interior"),
    (31, "lazy", "water_mist"),
    (35, "desire", "moonlight_water"),
    (39, "angry", "bright_clouds"),
    (43, "heart", "quiet_lake"),
]

FREEZE_JS = """
() => {
  const veil = document.querySelector('[data-exhibition-veil]');
  const art = document.querySelector('[data-exhibition-artwork]');
  const kanji = document.querySelector('[data-exhibition-kanji]');
  const kw = document.querySelector('[data-exhibition-keyword]');
  const vjp = document.querySelector('[data-exhibition-verse-jp]');
  const ven = document.querySelector('[data-exhibition-verse-en]');
  veil?.classList.add('is-clear');
  art?.classList.add('is-visible');
  kanji?.classList.add('is-visible');
  kw?.classList.add('is-visible');
  vjp?.classList.add('is-visible');
  ven?.classList.add('is-visible');
}
"""


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Run: python3 -m venv .venv && .venv/bin/pip install playwright", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for exhibit, slug, kind in SAMPLES:
                for mode in ("legacy", "gallery"):
                    typo = "legacy" if mode == "legacy" else ""
                    qs = f"collection=heart_v5&skipBookends=1&exhibit={exhibit}&singleExhibit=1&timingScale=0.01"
                    if typo:
                        qs += f"&typography={typo}"
                    url = f"http://127.0.0.1:{PORT}/exhibition.html?{qs}"
                    page = browser.new_page(viewport=VIEWPORT)
                    page.goto(url, wait_until="load", timeout=60_000)
                    page.wait_for_function("() => window.kmlExhibition", timeout=30_000)
                    page.wait_for_timeout(1200)
                    page.evaluate(FREEZE_JS)
                    page.wait_for_timeout(400)
                    out = OUT / f"{slug}_{kind}_{mode}.png"
                    page.screenshot(path=str(out), full_page=False)
                    page.close()
                    print(f"  {out.name}")
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=5)

    print(f"\nScreenshots saved to {OUT}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
