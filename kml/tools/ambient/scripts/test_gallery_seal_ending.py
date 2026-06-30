#!/usr/bin/env python3
"""Browser test: gallery seal ending for a study exhibition collection."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8765
VIEWPORT = {"width": 1920, "height": 1080}


def start_server(port: int) -> subprocess.Popen:
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    return proc


def run_test(*, lesson: int, port: int, out_dir: Path) -> int:
    from playwright.sync_api import sync_playwright

    collection = f"lesson_{lesson}_foundations"
    url = f"http://127.0.0.1:{port}/index.html?collection={collection}&capture=1"
    out_dir.mkdir(parents=True, exist_ok=True)

    console_lines: list[str] = []
    milestones: list[dict] = []
    errors: list[str] = []

    def log_milestone(name: str, page) -> None:
        state = page.evaluate(
            """() => {
              const root = document.querySelector('[data-ambient-root]');
              const audio = window.kmlAmbient?.mainAudio;
              return {
                classes: root ? Array.from(root.classList) : [],
                presentationEnded: Boolean(window.kmlAmbient?.presentationEnded),
                audioTime: audio ? audio.currentTime : null,
                audioDuration: audio?.duration ?? null,
              };
            }"""
        )
        entry = {"t": round(time.time() - started_at, 2), "phase": name, **state}
        milestones.append(entry)
        print(f"  [{entry['t']:7.1f}s] {name}")
        if state.get("audioTime") is not None:
            print(
                f"           audio {state['audioTime']:.2f}s"
                f" / {state['audioDuration']:.2f}s"
            )
        page.screenshot(path=str(out_dir / f"{len(milestones):02d}_{name}.png"))

    started_at = time.time()
    print(f"Testing {collection} gallery seal ending")
    print(f"  URL: {url}")
    print(f"  Screenshots → {out_dir}/")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--autoplay-policy=no-user-gesture-required",
                "--disable-dev-shm-usage",
            ],
        )
        context = browser.new_context(
            viewport=VIEWPORT,
            color_scheme="dark",
        )
        page = context.new_page()

        page.on(
            "console",
            lambda msg: console_lines.append(f"[{msg.type}] {msg.text}"),
        )
        page.on("pageerror", lambda err: errors.append(str(err)))

        page.goto(url, wait_until="load", timeout=60_000)
        page.wait_for_function(
            "() => window.kmlAmbient",
            timeout=120_000,
        )

        gate = page.locator("[data-ambient-autoplay-gate]")
        try:
            if gate.is_visible():
                gate.click()
            else:
                # Headless Chromium often unlocks audio without showing the gate.
                page.wait_for_timeout(300)
        except Exception:
            page.mouse.click(VIEWPORT["width"] // 2, VIEWPORT["height"] // 2)

        log_milestone("started", page)

        seen = set()

        def poll() -> None:
            classes = page.evaluate(
                """() => {
                  const root = document.querySelector('[data-ambient-root]');
                  return root ? Array.from(root.classList) : [];
                }"""
            )
            mapping = {
                "is-gallery-seal-holding": "image_hold",
                "is-gallery-seal-fading": "fade_to_black",
                "is-gallery-seal-active": "crest_visible",
                "is-gallery-seal-exiting": "crest_fade_out",
                "is-presentation-ended": "presentation_ended",
            }
            for cls, name in mapping.items():
                if cls in classes and name not in seen:
                    seen.add(name)
                    log_milestone(name, page)

        deadline = time.time() + 900
        while time.time() < deadline:
            poll()
            ended = page.evaluate(
                "() => Boolean(window.kmlAmbient && window.kmlAmbient.presentationEnded)"
            )
            if ended:
                if "presentation_ended" not in seen:
                    log_milestone("presentation_ended", page)
                break
            page.wait_for_timeout(500)
        else:
            print("TIMEOUT waiting for presentation end", file=sys.stderr)
            page.screenshot(path=str(out_dir / "timeout.png"))
            context.close()
            browser.close()
            return 1

        page.wait_for_timeout(800)
        engine = page.evaluate(
            """() => ({
              version: window.kmlAmbient?.constructor?.name,
              presentationEnded: window.kmlAmbient?.presentationEnded,
              collection: window.kmlAmbient?.collection?.id,
            })"""
        )
        context.close()
        browser.close()

    elapsed = time.time() - started_at
    gallery_logs = [
        line for line in console_lines if "GALLERY" in line or "gallery" in line.lower()
    ]

    report = {
        "collection": collection,
        "elapsed_s": round(elapsed, 2),
        "presentationEnded": engine.get("presentationEnded"),
        "milestones": milestones,
        "gallery_console": gallery_logs[-10:],
        "errors": errors,
    }
    report_path = out_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\nFinished in {elapsed:.1f}s")
    print(f"  presentationEnded: {engine.get('presentationEnded')}")
    print(f"  milestones: {[m['phase'] for m in milestones]}")
    if gallery_logs:
        print("  gallery logs:")
        for line in gallery_logs[-5:]:
            print(f"    {line}")
    if errors:
        print("  ERRORS:", file=sys.stderr)
        for err in errors:
            print(f"    {err}", file=sys.stderr)
        return 1

    required = {
        "image_hold",
        "fade_to_black",
        "crest_visible",
        "crest_fade_out",
        "presentation_ended",
    }
    missing = required - seen
    if missing:
        print(f"  MISSING phases: {sorted(missing)}", file=sys.stderr)
        return 1

    print(f"  report → {report_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, default=39)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "foundations_exhibitions" / ".ending_test",
    )
    parser.add_argument(
        "--no-server",
        action="store_true",
        help="Assume http.server already running on --port",
    )
    args = parser.parse_args()

    try:
        import playwright  # noqa: F401
    except ImportError:
        print("Playwright required: pip install playwright && playwright install chromium")
        return 1

    server = None
    if not args.no_server:
        server = start_server(args.port)

    try:
        out = args.output_dir / f"lesson_{args.lesson}_foundations"
        return run_test(lesson=args.lesson, port=args.port, out_dir=out)
    finally:
        if server:
            server.terminate()
            server.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
