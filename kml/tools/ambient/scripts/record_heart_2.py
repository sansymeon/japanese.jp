#!/usr/bin/env python3
"""
Record Heart 2 — Ambient Gallery (no kanji).

Uses exhibition.html?collection=heart_2 with intro + main + outro mux.
Outro (exhibition_flute_outro_+3) plays under the closing crest.

Output: heart_exhibitions/heart_2.mp4 (gitignored)

Requires: playwright, chromium, ffmpeg
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "heart_exhibitions"
DEFAULT_PORT = 8768
COLLECTION = "heart_2"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    ensure_deps,
    load_collection,
    mux_video_with_audio,
    presentation_timeout_ms,
    reflections_audio_timeline_ms,
    start_server,
)


def record(*, port: int, output_dir: Path) -> Path:
    collection = load_collection(ROOT, COLLECTION)
    intro_delay_ms, main_start_ms, outro_start_ms = reflections_audio_timeline_ms(
        collection, ROOT
    )
    timeout_ms = presentation_timeout_ms(collection, ROOT, extra_ms=300_000)

    bookends = collection.get("bookends") or {}
    soundtrack = collection.get("soundtrack") or {}
    intro = ROOT / (
        bookends.get("opening", {}).get("audio") or "audio/exhibition_flute_intro.mp3"
    )
    main = ROOT / (
        soundtrack.get("main") or "audio/ambient_kanji_exhibition.mp3"
    )
    outro = ROOT / (
        bookends.get("closing", {}).get("audio")
        or "audio/exhibition_flute_outro_+3.mp3"
    )
    for path in (intro, main, outro):
        if not path.is_file():
            raise FileNotFoundError(f"Missing audio: {path}")

    url = (
        f"http://127.0.0.1:{port}/exhibition.html"
        f"?collection={COLLECTION}&camera=guardian&typography=mobile-refine"
    )
    out_path = output_dir / f"{COLLECTION}.mp4"
    tmp_dir = output_dir / f".tmp_{COLLECTION}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording Heart 2 (textless ambient gallery) …")
    print(f"  URL: {url}")
    print(
        f"  Audio: intro @ {intro_delay_ms}ms, main @ {main_start_ms}ms, "
        f"outro @ {outro_start_ms}ms"
    )
    print(f"  Max wait: {timeout_ms // 1000}s")

    webm = capture_exhibition_webm(
        url=url,
        tmp_dir=tmp_dir,
        timeout_ms=timeout_ms,
    )

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
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    ensure_deps()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Refresh imageRev for replaced studies before capture
    subprocess.run(
        [
            sys.executable,
            "-c",
            """
import json
from pathlib import Path
root = Path('collections/heart_2.json')
studies = Path('../../assets/studies')
doc = json.loads(root.read_text(encoding='utf-8'))
for s in doc['scenes']:
    stem = Path(s['image']).name
    p = studies / stem
    if p.is_file():
        s['imageRev'] = int(p.stat().st_mtime)
doc['meta']['status'] = 'recording'
root.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')
print('Refreshed heart_2 imageRev')
""",
        ],
        check=True,
        cwd=ROOT,
    )

    server = start_server(ROOT, args.port)
    try:
        record(port=args.port, output_dir=args.output_dir)
    finally:
        from exhibition_record_common import stop_server

        stop_server(server)

    print(f"\nDone. MP4 in {args.output_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
