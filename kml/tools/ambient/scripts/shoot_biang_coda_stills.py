#!/usr/bin/env python3
"""Shoot stills of the party-kanji gold flakes and the biáng finale coda.

Usage:
  .venv/bin/python scripts/shoot_biang_coda_stills.py --case finale
  .venv/bin/python scripts/shoot_biang_coda_stills.py --case reward

Output: collections/beyond_joyo/.qa_<case>/at_<ms>.png
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    VIEWPORT,
    ensure_deps,
    exhibition_record_url,
    start_server,
    stop_server,
)

# Single-step QA fixtures. Reward: meaning lands ~24.7s (5s reward hold), then a
# 22s review hold. Finale: meaning lands ~24.7s with an 8s hold, review ends 48.5s,
# crest reveal 53.3s onward.
CASES = {
    "reward": {
        "collection": "beyond_joyo_reward_qa",
        "shots": [25_500, 27_500, 31_000, 36_000, 44_000, 52_000],
    },
    "finale": {
        "collection": "beyond_joyo_biang_qa",
        "shots": [25_500, 29_500, 33_000, 44_000, 50_500, 55_500, 58_600, 61_000],
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(CASES), default="finale")
    parser.add_argument("--port", type=int, default=9077)
    args = parser.parse_args()
    case = CASES[args.case]

    ensure_deps()
    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    out_dir = ROOT / "collections" / "beyond_joyo" / f".qa_{args.case}"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.png"):
        old.unlink()

    url = exhibition_record_url(
        port=args.port,
        collection_id=case["collection"],
        display={"typography": "mobile-refine", "verseMode": "sequential"},
    )
    server = start_server(ROOT, args.port)
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--autoplay-policy=no-user-gesture-required", "--disable-dev-shm-usage"],
            )
            page = browser.new_context(viewport=VIEWPORT, color_scheme="dark").new_page()
            print(f"  URL: {url}")
            page.goto(url, wait_until="load", timeout=120_000)
            page.wait_for_function("() => window.kmlExhibition", timeout=120_000)
            page.wait_for_function(
                "() => document.fonts && document.fonts.status === 'loaded'",
                timeout=120_000,
            )
            elapsed = 0
            for at in case["shots"]:
                page.wait_for_timeout(at - elapsed)
                elapsed = at
                page.screenshot(path=str(out_dir / f"at_{at:06d}.png"))
                stats = page.evaluate(
                    """() => {
                      const flakes = [...document.querySelectorAll('.kml-gold-flake')];
                      const lit = flakes.filter((f) => Number(getComputedStyle(f).opacity) > 0.02);
                      const crest = document.querySelector('.exhibition-bookend');
                      return {
                        flakes: flakes.length,
                        lit: lit.length,
                        crest: crest ? Number(getComputedStyle(crest).opacity).toFixed(2) : 'none',
                      };
                    }"""
                )
                print(
                    f"  {at:6d}ms  flakes={stats['flakes']:3d} lit={stats['lit']:3d} "
                    f"crest={stats['crest']}"
                )
            browser.close()
    finally:
        stop_server(server)

    print(f"stills → {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
