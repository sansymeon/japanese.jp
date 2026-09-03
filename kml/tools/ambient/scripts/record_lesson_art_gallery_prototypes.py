#!/usr/bin/env python3
"""Record Lesson Art Gallery prototypes via Playwright.

Output: collections/prototypes/lesson_art_gallery_*.mp4

Captures at 2× resolution (3840×2160) then Lanczos-downsamples to 1080p so
slow panorama walks stay fluid after encode.

Usage:
  python scripts/record_lesson_art_gallery_prototypes.py
  python scripts/record_lesson_art_gallery_prototypes.py --rebuild
  python scripts/record_lesson_art_gallery_prototypes.py --only proto_lesson_art_gallery_34
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "collections" / "prototypes"
DEFAULT_PORT = 8791
BUILDER = "build_lesson_art_gallery_prototypes.py"

# Keep mux end-fade short and aligned with crest exhale — do not stretch music.
END_FADE_S = 4.0

# Capture high-res for smoother panorama / dissolve encoding, then downsample.
CAPTURE_VIEWPORT = {"width": 3840, "height": 2160}
OUTPUT_SIZE = (1920, 1080)

COLLECTION_IDS = [
    "proto_lesson_art_gallery_34",
    "proto_lesson_art_gallery_32",
    "proto_lesson_art_gallery_31_panorama",
]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    ensure_deps,
    exhibition_record_url,
    load_collection,
    mux_exhibition_soundtrack,
    presentation_timeout_ms,
    start_server,
    stop_server,
    vocabulary_exhibition_soundtrack_start_ms,
)


def rebuild() -> None:
    script = ROOT / "scripts" / BUILDER
    subprocess.check_call([sys.executable, str(script)], cwd=str(ROOT))


def downsample_to_1080(webm: Path, out_mp4: Path) -> Path:
    """Lanczos scale 2× capture → final 1080p before soundtrack mux."""
    w, h = OUTPUT_SIZE
    print(f"  Downsample → {w}×{h} (lanczos)")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(webm),
            "-vf",
            f"scale={w}:{h}:flags=lanczos",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out_mp4),
        ],
        check=True,
    )
    return out_mp4


def record_one(*, collection_id: str, port: int, output_dir: Path) -> Path:
    collection = load_collection(ROOT, collection_id)
    soundtrack_start_ms = vocabulary_exhibition_soundtrack_start_ms(collection)
    timeout_ms = presentation_timeout_ms(collection, ROOT, extra_ms=90_000)

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    display = dict(collection.get("display") or {})
    display.setdefault("typography", "mobile-refine")
    display.setdefault("verseMode", "sequential")
    url = exhibition_record_url(port=port, collection_id=collection_id, display=display)

    out_path = output_dir / f"{collection_id}.mp4"
    tmp_dir = output_dir / f".tmp_{collection_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    meta = collection.get("meta") or {}
    print(f"Recording {collection_id} → {out_path.name}")
    print(f"  Soundtrack: {soundtrack_rel}")
    print(f"  Soundtrack @ {soundtrack_start_ms} ms")
    print(f"  Scenes: {len(collection.get('scenes') or [])}")
    print(f"  Avg hold: {meta.get('avgHoldMs', '?')} ms")
    print(f"  Transition: {meta.get('transitionMs', '?')} ms")
    print(f"  Capture: {CAPTURE_VIEWPORT['width']}×{CAPTURE_VIEWPORT['height']} → 1080p")
    print(f"  Max wait: {timeout_ms // 1000}s")
    print(f"  URL: {url}")

    webm = capture_exhibition_webm(
        url=url,
        tmp_dir=tmp_dir,
        timeout_ms=timeout_ms,
        viewport=CAPTURE_VIEWPORT,
    )
    scaled = downsample_to_1080(webm, tmp_dir / "scaled_1080.mp4")

    tmp_mux = tmp_dir / "muxed.mp4"
    mux_exhibition_soundtrack(
        webm=scaled,
        output_mp4=tmp_mux,
        soundtrack=soundtrack,
        soundtrack_start_ms=soundtrack_start_ms,
        end_fade_s=END_FADE_S,
        video_from_mp4=True,
    )
    shutil.move(str(tmp_mux), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()

    print(f"  → {out_path}")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--only", choices=COLLECTION_IDS, default=None)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    ensure_deps()
    if args.rebuild:
        rebuild()

    ids = [args.only] if args.only else list(COLLECTION_IDS)
    server = start_server(ROOT, args.port)
    try:
        for cid in ids:
            record_one(collection_id=cid, port=args.port, output_dir=args.output_dir)
    finally:
        stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
