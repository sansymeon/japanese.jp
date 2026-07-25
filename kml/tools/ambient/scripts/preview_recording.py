#!/usr/bin/env python3
"""Open an exhibition in the exact Chromium pipeline used for MP4 recording.

Interactive Chrome (resized window, often DPR=2) is not the approval surface.
This launches the same Playwright Chromium, viewport, deviceScaleFactor, color
scheme, and URL params as capture_exhibition_webm() — headed, so you can watch
and approve what the recorder will actually rasterize.

Examples:
  .venv/bin/python scripts/preview_recording.py --collection beyond_joyo_biang_qa
  .venv/bin/python scripts/preview_recording.py --collection party_kanji_v1 \\
      --extra skipBookends=1 --extra singleExhibit=1
  .venv/bin/python scripts/preview_recording.py --collection beyond_joyo_reward_qa \\
      --timing-scale 0.05

Press Enter in the terminal when finished (closes the browser).
Optional: --screenshot-ms 25500,44000 writes PNGs from this same pipeline.
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
    DEVICE_SCALE_FACTOR,
    VIEWPORT,
    ensure_deps,
    exhibition_record_url,
    launch_recording_browser,
    load_collection,
    new_recording_context,
    start_server,
    stop_server,
)


def parse_extra(pairs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in pairs:
        if "=" not in raw:
            raise SystemExit(f"--extra expects key=value, got: {raw}")
        key, value = raw.split("=", 1)
        out[key] = value
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", required=True, help="Collection id")
    parser.add_argument("--port", type=int, default=9088)
    parser.add_argument(
        "--timing-scale",
        type=float,
        default=None,
        help="Optional timingScale (e.g. 0.05 for fast QA)",
    )
    parser.add_argument(
        "--extra",
        action="append",
        default=[],
        help="Extra query param key=value (repeatable)",
    )
    parser.add_argument(
        "--screenshot-ms",
        default="",
        help="Comma-separated elapsed ms to screenshot (same pipeline as capture)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Directory for --screenshot-ms PNGs (default: collections/<id>/.record_preview)",
    )
    args = parser.parse_args()

    ensure_deps()
    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    collection = load_collection(ROOT, args.collection)
    display = dict(collection.get("display") or {})
    extra = parse_extra(args.extra)
    if args.timing_scale is not None:
        extra["timingScale"] = str(args.timing_scale)
    extra.setdefault("recordPipeline", "1")

    url = exhibition_record_url(
        port=args.port,
        collection_id=args.collection,
        display=display,
        extra_params=extra,
    )

    shot_times = [
        int(x.strip())
        for x in args.screenshot_ms.split(",")
        if x.strip()
    ]
    out_dir = args.out_dir
    if shot_times and out_dir is None:
        from collection_paths import collection_json_path  # noqa: E402

        coll_path = collection_json_path(ROOT, args.collection)
        out_dir = coll_path.parent / f".record_preview_{args.collection}"
    if shot_times:
        assert out_dir is not None
        out_dir.mkdir(parents=True, exist_ok=True)

    server = start_server(ROOT, args.port)
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = launch_recording_browser(p, headless=False)
            context = new_recording_context(browser, viewport=VIEWPORT)
            page = context.new_page()
            print("Recording pipeline preview")
            print(f"  URL:      {url}")
            print(f"  Viewport: {VIEWPORT['width']}×{VIEWPORT['height']}")
            print(f"  DPR:      {DEVICE_SCALE_FACTOR} (same as MP4 capture)")
            print(f"  Browser:  Playwright Chromium (headed)")
            print("  Approve what you see here — this is the export rasterizer.")
            page.goto(url, wait_until="load", timeout=120_000)
            page.wait_for_function("() => window.kmlExhibition", timeout=120_000)
            page.wait_for_function(
                "() => document.fonts && document.fonts.status === 'loaded'",
                timeout=120_000,
            )

            if shot_times:
                gate = page.locator("[data-exhibition-autoplay-gate]")
                try:
                    if gate.is_visible():
                        gate.click()
                except Exception:
                    page.mouse.click(VIEWPORT["width"] // 2, VIEWPORT["height"] // 2)
                elapsed = 0
                for at in shot_times:
                    page.wait_for_timeout(max(0, at - elapsed))
                    elapsed = at
                    path = out_dir / f"at_{at:06d}.png"
                    page.screenshot(path=str(path))
                    print(f"  screenshot {path}")

            input("\nPress Enter to close the recording-preview browser…\n")
            context.close()
            browser.close()
    finally:
        stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
