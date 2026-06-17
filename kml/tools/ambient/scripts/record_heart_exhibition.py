#!/usr/bin/env python3
"""
Record Heart v5 Digital Art Exhibition MP4 (Gallery Guardian + immersive cover).

Uses exhibition.html?collection=heart_v5 (Guardian camera is automatic for heart_*).

Output: heart_exhibitions/heart_v5.mp4 (gitignored)

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
OUTPUT_DIR = ROOT / "heart_exhibitions"
DEFAULT_PORT = 8766
VIEWPORT = {"width": 1920, "height": 1080}
COLLECTION = "heart_v5"


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


def probe_duration_seconds(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def opening_timeline_ms(collection: dict) -> tuple[int, int]:
    """Return (flute_delay_ms, ambient_start_ms) aligned to exhibition engine."""
    t = collection.get("exhibition") or {}
    bookends = collection.get("bookends") or {}
    before = int(t.get("openingBlackBeforeMs", 2000))
    exhale = int(t.get("openingExhaleMs", 6000))
    after = int(t.get("openingBlackAfterMs", 0))
    flute_path = ROOT / (bookends.get("opening", {}).get("audio") or "audio/flute_intro.mp3")
    flute_ms = int(probe_duration_seconds(flute_path) * 1000) if flute_path.is_file() else 0
    flute_delay = before
    ambient_start = before + flute_ms + exhale + after
    return flute_delay, ambient_start


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


def record(*, port: int, output_dir: Path, log_path: Path | None) -> Path:
    from playwright.sync_api import sync_playwright

    collection_path = ROOT / "collections" / f"{COLLECTION}.json"
    collection = json.loads(collection_path.read_text(encoding="utf-8"))
    flute_delay_ms, ambient_start_ms = opening_timeline_ms(collection)

    url = f"http://127.0.0.1:{port}/exhibition.html?collection={COLLECTION}&camera=guardian"
    out_path = output_dir / f"{COLLECTION}.mp4"
    tmp_dir = output_dir / f".tmp_{COLLECTION}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording Heart exhibition (Gallery Guardian) …")
    print(f"  URL: {url}")
    print(f"  Audio: flute @ {flute_delay_ms}ms, ambient @ {ambient_start_ms}ms")

    log_file = None
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = log_path.open("w", encoding="utf-8")
        log_file.write(f"URL: {url}\n")
        log_file.flush()

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
            timeout=7_200_000,
        )
        page.wait_for_timeout(1500)

        video = page.video
        page.close()
        video_path = video.path() if video else None
        context.close()
        browser.close()

    webm_files = list(tmp_dir.glob("*.webm"))
    webm = Path(video_path) if video_path else (webm_files[0] if webm_files else None)
    if not webm or not webm.is_file():
        raise RuntimeError("No video captured for Heart exhibition")

    flute = ROOT / "audio" / "flute_intro.mp3"
    ambient = ROOT / "audio" / "ambient_kanji_exhibition.mp3"
    if not flute.is_file() or not ambient.is_file():
        raise FileNotFoundError("Missing flute_intro.mp3 or ambient_kanji_exhibition.mp3")

    tmp_mux = tmp_dir / "muxed.mp4"
    flute_delay_s = flute_delay_ms / 1000.0
    ambient_start_s = ambient_start_ms / 1000.0

    filter_complex = (
        f"[1:a]adelay={flute_delay_ms}|{flute_delay_ms}[fl];"
        f"[2:a]adelay={ambient_start_ms}|{ambient_start_ms}[amb];"
        f"[fl][amb]amix=inputs=2:duration=longest:dropout_transition=0[a]"
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(webm),
            "-i",
            str(flute),
            "-i",
            str(ambient),
            "-filter_complex",
            filter_complex,
            "-map",
            "0:v:0",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(tmp_mux),
        ],
        check=True,
    )

    shutil.move(str(tmp_mux), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()

    if log_file:
        log_file.write(f"Done: {out_path}\n")
        log_file.write(f"flute_delay_s={flute_delay_s:.3f} ambient_start_s={ambient_start_s:.3f}\n")
        log_file.close()

    print(f"  → {out_path}")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument(
        "--log",
        type=Path,
        default=OUTPUT_DIR / "record_heart_v5.log",
        help="Progress log path",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild heart_v5.json before recording",
    )
    args = parser.parse_args()

    ensure_deps()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.rebuild:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_heart_v5_exhibition.py")],
            check=True,
            cwd=ROOT,
        )

    server = start_server(args.port)
    try:
        record(port=args.port, output_dir=args.output_dir, log_path=args.log)
    finally:
        server.terminate()
        server.wait(timeout=5)

    print(f"\nDone. MP4 in {args.output_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
