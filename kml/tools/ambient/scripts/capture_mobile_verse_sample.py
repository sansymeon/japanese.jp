#!/usr/bin/env python3
"""Capture mobile sequential-verse test frames for a single Heart exhibit."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mobile_verse_samples"
PORT = 8774
EXHIBIT = 0  # 愛 love

STATES = {
    "image_only": """
() => {
  const veil = document.querySelector('[data-exhibition-veil]');
  const art = document.querySelector('[data-exhibition-artwork]');
  const kanji = document.querySelector('[data-exhibition-kanji]');
  const kw = document.querySelector('[data-exhibition-keyword]');
  const vjp = document.querySelector('[data-exhibition-verse-jp]');
  const ven = document.querySelector('[data-exhibition-verse-en]');
  veil?.classList.add('is-clear');
  art?.classList.add('is-visible');
  [kanji, kw, vjp, ven].forEach((el) => el?.classList.remove('is-visible'));
}
""",
    "verse_jp": """
() => {
  const veil = document.querySelector('[data-exhibition-veil]');
  const art = document.querySelector('[data-exhibition-artwork]');
  const vjp = document.querySelector('[data-exhibition-verse-jp]');
  const ven = document.querySelector('[data-exhibition-verse-en]');
  veil?.classList.add('is-clear');
  art?.classList.add('is-visible');
  vjp?.classList.add('is-visible');
  ven?.classList.remove('is-visible');
}
""",
    "verse_en": """
() => {
  const veil = document.querySelector('[data-exhibition-veil]');
  const art = document.querySelector('[data-exhibition-artwork]');
  const vjp = document.querySelector('[data-exhibition-verse-jp]');
  const ven = document.querySelector('[data-exhibition-verse-en]');
  veil?.classList.add('is-clear');
  art?.classList.add('is-visible');
  vjp?.classList.remove('is-visible');
  ven?.classList.add('is-visible');
}
""",
}

VIEWPORTS = {
    "mobile": {"width": 390, "height": 844},
    "desktop": {"width": 1920, "height": 1080},
}


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Run: .venv/bin/pip install playwright", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    if not (ROOT / "assets" / "studies").exists():
        print("Missing assets symlink. From kml/tools/ambient: ln -s ../../assets assets", file=sys.stderr)
        return 1

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2.5)

    base_qs = (
        f"collection=heart_v5&skipBookends=1&exhibit={EXHIBIT}"
        "&singleExhibit=1&verseMode=sequential&typography=mobile&timingScale=0.01"
    )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for vp_name, viewport in VIEWPORTS.items():
                for state, js in STATES.items():
                    url = f"http://127.0.0.1:{PORT}/exhibition.html?{base_qs}"
                    page = browser.new_page(viewport=viewport)
                    page.goto(url, wait_until="load", timeout=60_000)
                    page.wait_for_function("() => window.kmlExhibition", timeout=30_000)
                    page.wait_for_timeout(800)
                    page.evaluate(js)
                    page.wait_for_timeout(400)
                    out = OUT / f"love_{state}_{vp_name}.png"
                    page.screenshot(path=str(out), full_page=False)
                    page.close()
                    print(out)
    finally:
        server.terminate()
        server.wait(timeout=5)

    print(f"\nSamples in {OUT}/")
    print(
        "Live test: http://127.0.0.1:8765/exhibition.html?"
        "collection=heart_v5&skipBookends=1&exhibit=0&singleExhibit=1"
        "&verseMode=sequential&typography=mobile"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
