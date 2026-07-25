#!/usr/bin/env python3
"""Record Jr High Compounds Part N MP4 via Playwright.

Usage:
  python scripts/record_post_elementary_compounds.py --part 2
  python scripts/record_post_elementary_compounds.py --part 2 --port 8812

Output: collections/post_elementary/post_elementary_compounds_{NN}.mp4
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"

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


def collection_id_for_part(part: int) -> str:
    return f"post_elementary_compounds_{part:02d}"


def record(*, part: int, port: int) -> Path:
    collection_id = collection_id_for_part(part)
    collection = load_collection(ROOT, collection_id)
    soundtrack_start_ms = vocabulary_exhibition_soundtrack_start_ms(collection)
    timeout_ms = presentation_timeout_ms(collection, ROOT, extra_ms=180_000)

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    soundtrack = ROOT / soundtrack_rel
    if not soundtrack.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")

    display = dict(collection.get("display") or {})
    display.setdefault("typography", "mobile-refine")
    display.setdefault("verseMode", "sequential")
    url = exhibition_record_url(port=port, collection_id=collection_id, display=display)

    out_dir = ROOT / "collections" / "post_elementary"
    out_path = out_dir / f"{collection_id}.mp4"
    tmp_dir = out_dir / f".tmp_{collection_id}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {collection_id} → {out_path.name}")
    print(f"  Soundtrack: {soundtrack_rel}")
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
    parser.add_argument("--part", type=int, required=True, help="Part number (1–22)")
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()
    if args.part < 1:
        raise SystemExit("--part must be >= 1")
    port = args.port if args.port is not None else 8810 + args.part

    ensure_deps()

    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    server = start_server(ROOT, port)
    try:
        record(part=args.part, port=port)
    finally:
        stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
