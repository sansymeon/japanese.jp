#!/usr/bin/env python3
"""Record lesson gallery exhibition MP4 via Playwright.

Output: collections/lesson_NN/gallery_lesson_NN.mp4
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8780

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    compounds_exhibition_soundtrack_start_ms,
    ensure_deps,
    exhibition_record_url,
    load_collection,
    mux_exhibition_soundtrack,
    presentation_timeout_ms,
    start_server,
    stop_server,
)

BUILDERS = {
    1: "build_lesson_01_gallery.py",
    2: "build_lesson_02_gallery.py",
    3: "build_lesson_03_gallery.py",
    4: "build_lesson_04_gallery.py",
    5: "build_lesson_05_gallery.py",
    6: "build_lesson_06_gallery.py",
    7: "build_lesson_07_gallery.py",
    8: "build_lesson_08_gallery.py",
    9: "build_lesson_09_gallery.py",
    10: "build_lesson_10_gallery.py",
    # Lessons 11–20, 33–38, 41 use the shared gallery builder (same profile as 1–10).
    11: "build_lesson_gallery.py",
    12: "build_lesson_gallery.py",
    13: "build_lesson_gallery.py",
    14: "build_lesson_gallery.py",
    15: "build_lesson_gallery.py",
    16: "build_lesson_gallery.py",
    17: "build_lesson_gallery.py",
    18: "build_lesson_gallery.py",
    19: "build_lesson_gallery.py",
    20: "build_lesson_gallery.py",
    33: "build_lesson_gallery.py",
    34: "build_lesson_gallery.py",
    35: "build_lesson_gallery.py",
    36: "build_lesson_gallery.py",
    37: "build_lesson_gallery.py",
    38: "build_lesson_gallery.py",
    41: "build_lesson_gallery.py",
}

SHARED_GALLERY_BUILDER = "build_lesson_gallery.py"


def collection_id(lesson: int) -> str:
    return f"lesson_{lesson:02d}_gallery"


def record(*, lesson: int, port: int) -> Path:
    cid = collection_id(lesson)
    collection = load_collection(ROOT, cid)
    soundtrack_start_ms = compounds_exhibition_soundtrack_start_ms(collection)
    timeout_ms = presentation_timeout_ms(collection, ROOT)

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    display = dict(collection.get("display") or {})
    display.setdefault("typography", "mobile-refine")
    display.setdefault("verseMode", "sequential")
    url = exhibition_record_url(port=port, collection_id=cid, display=display)

    out_dir = ROOT / "collections" / f"lesson_{lesson:02d}"
    out_path = out_dir / f"gallery_lesson_{lesson:02d}.mp4"
    tmp_dir = out_dir / f".tmp_gallery_lesson_{lesson:02d}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {cid} → {out_path.name}")
    print(f"  URL: {url}")
    print(f"  Soundtrack @ {soundtrack_start_ms} ms")
    print(f"  Max wait: {timeout_ms // 1000}s")

    webm = capture_exhibition_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    tmp_mux = tmp_dir / "muxed.mp4"
    mux_exhibition_soundtrack(
        webm=webm,
        output_mp4=tmp_mux,
        soundtrack=soundtrack,
        soundtrack_start_ms=soundtrack_start_ms,
    )
    shutil.move(str(tmp_mux), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()

    print(f"  → {out_path}")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, required=True, choices=sorted(BUILDERS))
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()

    ensure_deps()

    if args.rebuild:
        script = BUILDERS[args.lesson]
        cmd = [sys.executable, str(ROOT / "scripts" / script)]
        if script == SHARED_GALLERY_BUILDER:
            cmd.extend(["--lesson", str(args.lesson)])
        subprocess.run(cmd, check=True, cwd=ROOT)

    server = start_server(ROOT, args.port)
    try:
        record(lesson=args.lesson, port=args.port)
    finally:
        stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
