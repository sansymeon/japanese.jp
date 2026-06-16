#!/usr/bin/env python3
"""
Render Heart exhibition camera samples: legacy Ken Burns vs Gallery Guardian.

Output: gallery_guardian_samples/{legacy,guardian}/exhibit_XX_{id}.mp4

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
OUTPUT_DIR = ROOT / "gallery_guardian_samples"
DEFAULT_PORT = 8767
VIEWPORT = {"width": 1920, "height": 1080}
TIMING_SCALE = 0.3

# Representative Heart v5 exhibits (index, scene id, label)
SAMPLES = [
    (0, "L40_love", "love"),
    (4, "L33_think", "think"),
    (7, "L33_concept", "concept"),
    (12, "L34_fear", "fear"),
    (19, "L34_melancholy", "melancholy"),
    (27, "L34_lazy", "lazy"),
    (35, "L35_desire", "desire"),
    (43, "L32_heart", "heart"),
]


def ensure_deps() -> None:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg is required.", file=sys.stderr)
        sys.exit(1)
    try:
        import playwright  # noqa: F401
    except ImportError:
        print("pip install playwright && playwright install chromium", file=sys.stderr)
        sys.exit(1)


def start_server(port: int) -> subprocess.Popen:
    if not (ROOT / "assets" / "studies").exists():
        print("Missing assets symlink in kml/tools/ambient", file=sys.stderr)
        sys.exit(1)
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    return proc


def exhibit_duration_ms(collection: dict, timing_scale: float) -> int:
    t = {**collection.get("exhibition", {})}
    defaults = {
        "artworkArrivalMs": 8000,
        "artworkAloneMs": 6000,
        "kanjiRevealMs": 5500,
        "keywordDelayMs": 4500,
        "keywordFadeMs": 5000,
        "titleHoldMs": 8000,
        "titleFadeMs": 5500,
        "verseJpRevealMs": 6500,
        "verseEnDelayMs": 9000,
        "verseEnFadeMs": 5500,
        "reflectionHoldMs": 12000,
        "versesFadeMs": 5500,
        "essenceKanjiRevealMs": 2500,
        "essenceHoldMs": 0,
        "imageExhaleFadeMs": 16000,
        "kanjiAloneHoldMs": 9000,
        "kanjiExhaleFadeMs": 20000,
        "blackHoldMs": 3500,
    }
    for k, v in defaults.items():
        t.setdefault(k, v)
    total = sum(
        t[k]
        for k in [
            "artworkArrivalMs",
            "artworkAloneMs",
            "kanjiRevealMs",
            "keywordDelayMs",
            "keywordFadeMs",
            "titleHoldMs",
            "titleFadeMs",
            "verseJpRevealMs",
            "verseEnDelayMs",
            "verseEnFadeMs",
            "reflectionHoldMs",
            "versesFadeMs",
            "essenceKanjiRevealMs",
            "essenceHoldMs",
            "imageExhaleFadeMs",
            "kanjiAloneHoldMs",
            "kanjiExhaleFadeMs",
            "blackHoldMs",
        ]
    )
    return int(total * timing_scale) + 2000


def record_sample(
    *,
    port: int,
    exhibit_index: int,
    scene_id: str,
    label: str,
    camera: str,
    output_dir: Path,
    timing_scale: float,
) -> Path:
    from playwright.sync_api import sync_playwright

    camera_param = "legacy" if camera == "legacy" else "guardian"
    url = (
        f"http://127.0.0.1:{port}/exhibition.html"
        f"?collection=heart_v5"
        f"&skipBookends=1"
        f"&singleExhibit=1"
        f"&exhibit={exhibit_index}"
        f"&timingScale={timing_scale}"
        f"&camera={camera_param}"
    )
    out_path = output_dir / camera / f"exhibit_{exhibit_index:02d}_{label}.mp4"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = output_dir / ".tmp" / f"{camera}_{exhibit_index}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    collection = json.loads((ROOT / "collections" / "heart_v5.json").read_text())
    wait_ms = exhibit_duration_ms(collection, timing_scale)

    print(f"  [{camera}] #{exhibit_index} {label} ({scene_id}) …")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--autoplay-policy=no-user-gesture-required", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport=VIEWPORT,
            record_video_dir=str(tmp_dir),
            record_video_size=VIEWPORT,
            color_scheme="dark",
        )
        page = context.new_page()
        page.add_init_script(
            """
            window.__kmlExhibitEnded = false;
            document.addEventListener('kml-exhibition-exhibit-end', () => {
              window.__kmlExhibitEnded = true;
            });
            """
        )
        page.goto(url, wait_until="load", timeout=60_000)
        page.wait_for_function("() => window.kmlExhibition", timeout=60_000)
        page.wait_for_function(
            "() => window.__kmlExhibitEnded === true",
            timeout=max(wait_ms + 30_000, 120_000),
        )
        page.wait_for_timeout(800)

        video = page.video
        page.close()
        video_path = video.path() if video else None
        context.close()
        browser.close()

    webm_files = list(tmp_dir.glob("*.webm"))
    webm = Path(video_path) if video_path else (webm_files[0] if webm_files else None)
    if not webm or not webm.is_file():
        raise RuntimeError(f"No video for exhibit {exhibit_index} ({camera})")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(webm),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--timing-scale", type=float, default=TIMING_SCALE)
    parser.add_argument(
        "--exhibits",
        type=int,
        nargs="*",
        default=None,
        help="Exhibit indices to render (default: all samples)",
    )
    args = parser.parse_args()

    ensure_deps()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    samples = SAMPLES
    if args.exhibits:
        idx_set = set(args.exhibits)
        samples = [s for s in SAMPLES if s[0] in idx_set]

    server = start_server(args.port)
    try:
        for exhibit_index, scene_id, label in samples:
            for camera in ("legacy", "guardian"):
                record_sample(
                    port=args.port,
                    exhibit_index=exhibit_index,
                    scene_id=scene_id,
                    label=label,
                    camera=camera,
                    output_dir=args.output_dir,
                    timing_scale=args.timing_scale,
                )
    finally:
        server.terminate()
        server.wait(timeout=5)

    print(f"\nDone. Samples in {args.output_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
