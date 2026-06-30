#!/usr/bin/env python3
"""
Record PARTY KANJI exhibition MP4 (silent — no soundtrack in v1).

Uses exhibition.html?collection=party_kanji_v1&skipBookends=1&singleExhibit=1

Output: party_exhibitions/party_kanji_v1.mp4 (gitignored)

Requires: playwright, chromium, ffmpeg
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
OUTPUT_DIR = ROOT / "party_exhibitions"
DEFAULT_PORT = 8767
VIEWPORT = {"width": 1920, "height": 1080}
COLLECTION = "party_kanji_v1"


def ensure_deps() -> None:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg is required on PATH.", file=sys.stderr)
        sys.exit(1)
    try:
        import playwright  # noqa: F401
    except ImportError:
        print(
            "Playwright required:\n"
            "  python3 -m venv .venv && .venv/bin/pip install playwright\n"
            "  .venv/bin/playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)


def episode_duration_ms(collection: dict) -> int:
    t = collection.get("exhibition") or {}
    return sum(
        int(t.get(key, default))
        for key, default in [
            ("partyShockRevealMs", 800),
            ("partyShockHoldMs", 3500),
            ("partyShockFadeMs", 600),
            ("partyRevealFadeInMs", 800),
            ("partyRevealHoldMs", 12000),
            ("partyRevealFadeMs", 800),
            ("partyProofFadeInMs", 800),
            ("partyProofHoldMs", 12000),
            ("partyProofFadeMs", 800),
            ("partyFinalFadeMs", 600),
            ("partyFinalHoldMs", 4500),
            ("partyEndCardFadeInMs", 800),
            ("partyEndCardHoldMs", 4500),
            ("partyEndCardFadeMs", 800),
        ]
    )


def start_server(port: int) -> subprocess.Popen:
    if not (ROOT / "assets" / "studies").exists():
        print("Missing assets symlink. From kml/tools/ambient: ln -s ../../assets assets", file=sys.stderr)
        sys.exit(1)
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    return proc


def record(*, port: int, output_dir: Path, timing_scale: float) -> Path:
    from playwright.sync_api import sync_playwright

    collection_path = ROOT / "collections" / f"{COLLECTION}.json"
    collection = json.loads(collection_path.read_text(encoding="utf-8"))
    duration_ms = int(episode_duration_ms(collection) * timing_scale) + 3000

    url = (
        f"http://127.0.0.1:{port}/exhibition.html"
        f"?collection={COLLECTION}&skipBookends=1&singleExhibit=1&timingScale={timing_scale}"
    )
    out_path = output_dir / f"{COLLECTION}.mp4"
    tmp_dir = output_dir / f".tmp_{COLLECTION}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print("Recording PARTY KANJI prototype …")
    print(f"  URL: {url}")
    print(f"  Expected duration: ~{duration_ms / 1000:.0f}s")

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
            record_video_dir=str(tmp_dir),
            record_video_size=VIEWPORT,
            color_scheme="dark",
        )
        page = context.new_page()
        page.goto(url, wait_until="load", timeout=120_000)
        page.wait_for_function("() => window.kmlExhibition", timeout=120_000)

        gate = page.locator("[data-exhibition-autoplay-gate]")
        try:
            if gate.is_visible():
                gate.click()
            else:
                page.wait_for_timeout(300)
        except Exception:
            page.mouse.click(VIEWPORT["width"] // 2, VIEWPORT["height"] // 2)

        page.wait_for_function(
            "() => window.kmlExhibition && window.kmlExhibition.presentationEnded === true",
            timeout=max(duration_ms * 2, 120_000),
        )
        page.wait_for_timeout(1000)

        video = page.video
        page.close()
        video_path = video.path() if video else None
        context.close()
        browser.close()

    webm_files = list(tmp_dir.glob("*.webm"))
    webm = Path(video_path) if video_path else (webm_files[0] if webm_files else None)
    if not webm or not webm.is_file():
        raise RuntimeError("No video captured for PARTY KANJI")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(webm),
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out_path),
        ],
        check=True,
    )

    for f in tmp_dir.glob("*"):
        f.unlink(missing_ok=True)
    tmp_dir.rmdir()

    print(f"Wrote {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Record PARTY KANJI v1 MP4")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument(
        "--timing-scale",
        type=float,
        default=1.0,
        help="Scale episode timing (1.0 = full; 0.05 = fast QA)",
    )
    args = parser.parse_args()

    ensure_deps()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    server = start_server(args.port)
    try:
        record(port=args.port, output_dir=args.output_dir, timing_scale=args.timing_scale)
    finally:
        server.terminate()
        server.wait(timeout=5)


if __name__ == "__main__":
    main()
