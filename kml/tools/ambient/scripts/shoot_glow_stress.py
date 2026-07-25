#!/usr/bin/env python3
"""Shoot full-resolution 2×2 glow-stress boards for the densest kanji.

  .venv/bin/python scripts/shoot_glow_stress.py
  .venv/bin/python scripts/shoot_glow_stress.py --kanji 鬱,龘,靈,麤

Output: collections/prototypes/stills/glow_<kanji>_<edition>.png
        collections/prototypes/stills/glow_detail_<kanji>_<edition>.png  (glyph crop)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
OUT_DIR = ROOT / "collections" / "prototypes" / "stills"
DATA = ROOT / "collections" / "prototypes" / "glow_stress_kanji.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import ensure_deps, start_server, stop_server  # noqa: E402

VIEWPORTS = {
    "gallery": {"width": 1920, "height": 1080},
    "mobile": {"width": 1080, "height": 1920},
}


def slug(text: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in text).strip("_") or "glyph"


def shoot(*, editions: list[str], kanji_filter: list[str] | None, port: int) -> list[Path]:
    from playwright.sync_api import sync_playwright

    data = json.loads(DATA.read_text(encoding="utf-8"))
    items = data["kanji"]
    if kanji_filter:
        wanted = set(kanji_filter)
        items = [k for k in items if k["kanji"] in wanted]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--autoplay-policy=no-user-gesture-required", "--disable-dev-shm-usage"],
        )
        for edition in editions:
            context = browser.new_context(
                viewport=VIEWPORTS[edition], color_scheme="dark"
            )
            page = context.new_page()
            page.goto(
                f"http://127.0.0.1:{port}/glow-stress.html",
                wait_until="networkidle",
                timeout=120_000,
            )
            page.wait_for_function(
                "() => document.documentElement.classList.contains('is-ready')",
                timeout=120_000,
            )
            page.wait_for_function(
                "() => document.fonts && document.fonts.status === 'loaded'",
                timeout=120_000,
            )

            for item in items:
                page.evaluate(
                    """(kanji) => {
                      const buttons = [...document.querySelectorAll('#kanji-nav button')];
                      const hit = buttons.find(b => b.textContent === kanji);
                      if (hit) hit.click();
                    }""",
                    item["kanji"],
                )
                page.wait_for_timeout(120)
                path = OUT_DIR / f"glow_{slug(item['kanji'])}_{edition}.png"
                page.screenshot(path=str(path))
                written.append(path)

                # Crop the top-left "current glow" panel for close reading.
                panel = page.locator('.panel[data-glow="current"]').bounding_box()
                if panel:
                    detail = OUT_DIR / f"glow_detail_{slug(item['kanji'])}_{edition}.png"
                    page.screenshot(path=str(detail), clip=panel)
                    written.append(detail)

            context.close()
            print(f"  {edition}: {len(items)} boards")
        browser.close()

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editions", default="gallery,mobile")
    parser.add_argument("--kanji", default="", help="Comma-separated subset, e.g. 鬱,龘,靈")
    parser.add_argument("--port", type=int, default=9403)
    args = parser.parse_args()

    if not DATA.is_file():
        raise SystemExit(f"Missing {DATA} — run build_prototype_glow_stress.py first")

    ensure_deps()
    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    editions = [e.strip() for e in args.editions.split(",") if e.strip()]
    kanji_filter = [k.strip() for k in args.kanji.split(",") if k.strip()] or None

    server = start_server(ROOT, args.port)
    try:
        written = shoot(editions=editions, kanji_filter=kanji_filter, port=args.port)
    finally:
        stop_server(server)

    print(f"\n  {len(written)} files → {OUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
