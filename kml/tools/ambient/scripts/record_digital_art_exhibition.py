#!/usr/bin/env python3
"""Record a Digital Art Exhibition prototype (Moon first).

Separate from Ambient Kanji / Quiet Exhibition capture. Video is Playwright
Chromium; the MusicGPT master is muxed afterward so the room tone is clean.

  python3 scripts/record_digital_art_exhibition.py
  python3 scripts/record_digital_art_exhibition.py --id moon

Output: collections/digital_art/<id>.mp4  (gitignored)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "collections" / "digital_art"
DEFAULT_PORT = 8793
VIEWPORT = {"width": 1920, "height": 1080}
# Music already dies into silence; keep a short last-frame fade only.
END_FADE_S = 2.0

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    ensure_deps,
    launch_recording_browser,
    mux_exhibition_soundtrack,
    new_recording_context,
    probe_duration_seconds,
    start_server,
    stop_server,
)


def load_exhibition(exhibition_id: str) -> dict:
    path = OUTPUT_DIR / f"{exhibition_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Missing exhibition: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def capture_webm(*, url: str, tmp_dir: Path, timeout_ms: int) -> tuple[Path, int]:
    from playwright.sync_api import sync_playwright

    tmp_dir.mkdir(parents=True, exist_ok=True)
    print(f"  URL: {url}")
    print(f"  Viewport: {VIEWPORT['width']}×{VIEWPORT['height']}")
    print(f"  Max wait: {timeout_ms // 1000}s")

    with sync_playwright() as p:
        browser = launch_recording_browser(p, headless=True)
        context = new_recording_context(
            browser,
            viewport=VIEWPORT,
            record_video_dir=tmp_dir,
        )
        page = context.new_page()
        video_origin_ms = int(
            page.evaluate(
                "() => new Promise((resolve) => requestAnimationFrame(() => resolve(Date.now())))"
            )
        )
        page.goto(url, wait_until="load", timeout=120_000)
        page.wait_for_function(
            "() => window.KmlDigitalArtExhibition && window.KmlDigitalArtExhibition.ready",
            timeout=120_000,
        )
        page.wait_for_function(
            "() => window.KmlDigitalArtExhibition && window.KmlDigitalArtExhibition.started",
            timeout=120_000,
        )
        page.wait_for_function(
            "() => document.fonts && document.fonts.status === 'loaded'",
            timeout=60_000,
        )
        page.wait_for_function(
            "() => window.KmlDigitalArtExhibition && window.KmlDigitalArtExhibition.presentationEnded === true",
            timeout=timeout_ms,
        )
        started_at = int(
            page.evaluate(
                "() => window.KmlDigitalArtExhibition.soundtrackStartedAtEpochMs || 0"
            )
            or 0
        )
        page.wait_for_timeout(1200)

        video = page.video
        page.close()
        video_path = video.path() if video else None
        context.close()
        browser.close()

    webm_files = list(tmp_dir.glob("*.webm"))
    webm = Path(video_path) if video_path else (webm_files[0] if webm_files else None)
    if not webm or not webm.is_file():
        raise RuntimeError("No video captured for Digital Art Exhibition")

    delay_ms = max(0, started_at - video_origin_ms) if started_at else 0
    print(f"  Soundtrack delay: {delay_ms}ms")
    return webm, delay_ms


def record_one(*, exhibition_id: str, port: int, output_dir: Path) -> Path:
    collection = load_exhibition(exhibition_id)
    soundtrack_rel = (collection.get("soundtrack") or {}).get("src") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    duration_ms = int((collection.get("soundtrack") or {}).get("durationMs") or 169000)
    end_ms = duration_ms + int((collection.get("ending") or {}).get("blackAfterMs") or 1600)
    timeout_ms = end_ms + 90_000

    url = (
        f"http://127.0.0.1:{port}/digital-art-exhibition.html"
        f"?collection={exhibition_id}&recordPipeline=1"
    )
    out_path = output_dir / f"{exhibition_id}.mp4"
    tmp_dir = output_dir / f".tmp_{exhibition_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording Digital Art Exhibition “{collection.get('title') or exhibition_id}”")
    print(f"  Soundtrack: {soundtrack_rel} ({duration_ms / 1000:.1f}s)")
    print(f"  Works: {len(collection.get('artworks') or [])}")

    webm, delay_ms = capture_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    tmp_mux = tmp_dir / "muxed.mp4"
    mux_exhibition_soundtrack(
        webm=webm,
        output_mp4=tmp_mux,
        soundtrack=soundtrack,
        soundtrack_start_ms=delay_ms,
        end_fade_s=END_FADE_S,
    )
    shutil.move(str(tmp_mux), str(out_path))
    for f in tmp_dir.iterdir():
        if f.is_file():
            f.unlink()
    tmp_dir.rmdir()

    video_s = probe_duration_seconds(out_path)
    print(f"  → {out_path}  ({video_s:.1f}s)")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", default="moon", help="Exhibition id (default: moon)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild exhibition JSON before recording",
    )
    args = parser.parse_args()

    ensure_deps()
    if args.rebuild:
        subprocess.check_call(
            [sys.executable, str(ROOT / "scripts" / "build_digital_art_exhibition.py"), "--id", args.id],
            cwd=str(ROOT),
        )

    server = start_server(ROOT, args.port)
    try:
        record_one(exhibition_id=args.id, port=args.port, output_dir=args.output_dir)
    finally:
        stop_server(server)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
