#!/usr/bin/env python3
"""Record Katakana Cookie Song MP4 via Playwright.

Output: collections/katakana_cookie/katakana_cookie.mp4

Uses exhibition.html?collection=katakana_cookie
Soundtrack starts with the picture (no adelay).
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8795
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
COLLECTION_ID = "katakana_cookie"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exhibition_record_common import (  # noqa: E402
    capture_exhibition_webm,
    ensure_deps,
    exhibition_record_url,
    load_collection,
    mux_video_with_audio,
    presentation_timeout_ms,
    probe_duration_seconds,
    start_server,
    stop_server,
)


def record(*, port: int) -> Path:
    collection = load_collection(ROOT, COLLECTION_ID)
    timeout_ms = presentation_timeout_ms(collection, ROOT, extra_ms=60_000)

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    url = exhibition_record_url(port=port, collection_id=COLLECTION_ID)

    out_dir = ROOT / "collections" / COLLECTION_ID
    out_path = out_dir / f"{COLLECTION_ID}.mp4"
    tmp_dir = out_dir / f".tmp_{COLLECTION_ID}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {COLLECTION_ID} → {out_path.name}")
    print(f"  Max wait: {timeout_ms // 1000}s")

    webm = capture_exhibition_webm(
        url=url,
        tmp_dir=tmp_dir,
        timeout_ms=timeout_ms,
        require_yuji_syuku=False,
        preload_fonts=['400 146px "Shippori Mincho"', '500 146px "Shippori Mincho"'],
    )

    webm_s = probe_duration_seconds(webm)
    mp3_s = probe_duration_seconds(soundtrack)
    pad_s = max(1.0, webm_s - mp3_s + 1.0)
    # Music is gone by 3:36.3; fade covers leftover click/encoder junk at the tail.
    fade_end_s = 216.3
    fade_dur_s = 2.0
    fade_start_s = fade_end_s - fade_dur_s
    print(f"  Video: {webm_s:.1f}s, soundtrack {mp3_s:.1f}s, pad {pad_s:.1f}s")
    print(f"  Audio fade-out {fade_start_s:.1f}s → {fade_end_s:.1f}s")

    filter_complex = (
        f"[1:a]afade=t=out:st={fade_start_s:.3f}:d={fade_dur_s:.3f},"
        f"apad=pad_dur={pad_s:.3f}[m];"
        f"[m]asetpts=PTS-STARTPTS[a]"
    )
    tmp_mux = tmp_dir / "muxed.mp4"
    mux_video_with_audio(
        webm=webm,
        output_mp4=tmp_mux,
        filter_complex=filter_complex,
        audio_inputs=[soundtrack],
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
    args = parser.parse_args()

    ensure_deps()

    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    server = start_server(ROOT, args.port)
    try:
        record(port=args.port)
    finally:
        stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
