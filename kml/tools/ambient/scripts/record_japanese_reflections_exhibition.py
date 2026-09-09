#!/usr/bin/env python3
"""
Record Japanese Reflections five-lesson prototype exhibitions.

Uses exhibition.html?collection=lessons_*_prototype with intro + main + outro mux.

Output: ambient-study-japanese-reflections/five-lesson-reflections/lessons_*_exhibition.mp4
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8767

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_video_paths import FIVE_LESSON_REFLECTIONS  # noqa: E402
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    ensure_deps,
    load_collection,
    mux_video_with_audio,
    presentation_timeout_ms,
    reflections_audio_timeline_ms,
    start_server,
    stop_server,
)

OUTPUT_DIR = FIVE_LESSON_REFLECTIONS

BUILDERS = {
    f"lessons_{a}_{b}_prototype": f"build_lessons_{a}_{b}_prototype.py"
    for a, b in (
        (1, 5),
        (6, 10),
        (11, 15),
        (16, 20),
        (21, 25),
        (26, 30),
        (31, 35),
        (36, 40),
        (41, 45),
        (46, 50),
    )
}


def exhibition_mp4_name(collection_id: str) -> str:
    return f"{collection_id.replace('_prototype', '_exhibition')}.mp4"


def record(*, collection_id: str, port: int, output_dir: Path) -> Path:
    collection = load_collection(ROOT, collection_id)
    intro_delay_ms, main_start_ms, outro_start_ms = reflections_audio_timeline_ms(collection, ROOT)
    timeout_ms = presentation_timeout_ms(collection, ROOT)

    bookends = collection.get("bookends") or {}
    soundtrack = collection.get("soundtrack") or {}
    intro = ROOT / (bookends.get("opening", {}).get("audio") or "audio/fifty_minute_intro.mp3")
    main = ROOT / (soundtrack.get("main") or "audio/-3db_fifty_minutes.mp3")
    outro = ROOT / (bookends.get("closing", {}).get("audio") or "audio/fifty_minute_outro.mp3")
    for path in (intro, main, outro):
        if not path.is_file():
            raise FileNotFoundError(f"Missing audio: {path}")

    display = collection.get("display") or {}
    typo = display.get("typography") or "mobile-refine"
    verse_mode = display.get("verseMode") or "sequential"
    url = (
        f"http://127.0.0.1:{port}/exhibition.html"
        f"?collection={collection_id}&typography={typo}&verseMode={verse_mode}"
    )
    out_path = output_dir / exhibition_mp4_name(collection_id)
    tmp_dir = output_dir / f".tmp_{collection_id}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {collection_id} …")
    print(
        f"  Audio: intro @ {intro_delay_ms}ms, main @ {main_start_ms}ms, outro @ {outro_start_ms}ms"
    )

    webm = capture_exhibition_webm(url=url, tmp_dir=tmp_dir, timeout_ms=timeout_ms)

    filter_complex = (
        f"[1:a]adelay={intro_delay_ms}|{intro_delay_ms}[i];"
        f"[2:a]adelay={main_start_ms}|{main_start_ms}[m];"
        f"[3:a]adelay={outro_start_ms}|{outro_start_ms}[o];"
        f"[i][m][o]amix=inputs=3:duration=longest:dropout_transition=0[a]"
    )
    tmp_mux = tmp_dir / "muxed.mp4"
    mux_video_with_audio(
        webm=webm,
        output_mp4=tmp_mux,
        filter_complex=filter_complex,
        audio_inputs=[intro, main, outro],
    )

    shutil.move(str(tmp_mux), str(out_path))
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()

    print(f"  → {out_path}")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "collection",
        choices=sorted(BUILDERS),
        help="Collection id to record",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()

    ensure_deps()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.rebuild:
        script = BUILDERS[args.collection]
        subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True, cwd=ROOT)

    server = start_server(ROOT, args.port)
    try:
        record(collection_id=args.collection, port=args.port, output_dir=args.output_dir)
    finally:
        stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
