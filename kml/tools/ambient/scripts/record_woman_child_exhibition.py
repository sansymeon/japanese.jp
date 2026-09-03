#!/usr/bin/env python3
"""Record the 女・子 exhibition MP4 once the soundtrack MP3 exists.

Preview: exhibition.html?collection=woman_child_exhibition
Output:  woman_child_exhibitions/woman_child_exhibition.mp4 (gitignored)

Requires: soundtrack at audio/mother_child_exhibition.mp3, playwright, chromium, ffmpeg
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "woman_child_exhibitions"
DEFAULT_PORT = 8767
VIEWPORT = {"width": 1920, "height": 1080}
COLLECTION = "woman_child_exhibition"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    LONG_CAPTURE_CHROMIUM_ARGS,
    assert_local_noto_serif_files,
    assert_local_yuji_syuku_files,
    ensure_deps,
    ensure_noto_serif_jp_ready,
    ensure_yuji_syuku_ready,
    launch_recording_browser,
    new_recording_context,
)
from record_heart_exhibition import opening_timeline_ms, start_server  # noqa: E402


def record(*, port: int, output_dir: Path, log_path: Path | None) -> Path:
    from playwright.sync_api import sync_playwright

    collection_path = ROOT / "collections" / f"{COLLECTION}.json"
    collection = json.loads(collection_path.read_text(encoding="utf-8"))
    flute_delay_ms, ambient_start_ms = opening_timeline_ms(collection)

    url = (
        f"http://127.0.0.1:{port}/exhibition.html"
        f"?collection={COLLECTION}&camera=guardian&typography=mobile-refine"
    )
    out_path = output_dir / f"{COLLECTION}.mp4"
    tmp_dir = output_dir / f".tmp_{COLLECTION}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print("Recording 女・子 exhibition (Gallery Guardian) …")
    print(f"  URL: {url}")
    print(f"  Audio: flute @ {flute_delay_ms}ms, ambient @ {ambient_start_ms}ms")

    log_file = None
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = log_path.open("w", encoding="utf-8")
        log_file.write(f"URL: {url}\n")
        log_file.flush()

    assert_local_noto_serif_files()
    assert_local_yuji_syuku_files()

    with sync_playwright() as p:
        browser = launch_recording_browser(
            p, headless=True, extra_args=LONG_CAPTURE_CHROMIUM_ARGS
        )
        context = new_recording_context(
            browser,
            viewport=VIEWPORT,
            record_video_dir=tmp_dir,
        )
        page = context.new_page()
        page.goto(url, wait_until="load", timeout=120_000)
        page.wait_for_function("() => window.kmlExhibition", timeout=120_000)
        page.wait_for_function(
            "() => document.fonts && document.fonts.status === 'loaded'",
            timeout=120_000,
        )
        ensure_noto_serif_jp_ready(page)
        ensure_yuji_syuku_ready(page)

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
            timeout=3_600_000,
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
        raise RuntimeError("No video captured for 女・子 exhibition")

    bookends = collection.get("bookends") or {}
    flute = ROOT / (bookends.get("opening", {}).get("audio") or "audio/exhibition_flute_intro.mp3")
    ambient = ROOT / (collection.get("soundtrack") or {}).get(
        "main", "audio/mother_child_exhibition.mp3"
    )
    if not flute.is_file() or not ambient.is_file():
        raise FileNotFoundError(f"Missing flute ({flute}) or ambient ({ambient})")

    tmp_mux = tmp_dir / "muxed.mp4"
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
        default=OUTPUT_DIR / "record_woman_child_exhibition.log",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild woman_child_exhibition.json before recording",
    )
    args = parser.parse_args()

    ensure_deps()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.rebuild:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_woman_child_exhibition.py")],
            check=True,
            cwd=ROOT,
        )

    soundtrack = ROOT / "audio" / "mother_child_exhibition.mp3"
    if not soundtrack.is_file():
        print(f"Missing soundtrack: {soundtrack}", file=sys.stderr)
        print("Compose the MP3 to the runtime printed by the build script, then re-run.", file=sys.stderr)
        return 1

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
