#!/usr/bin/env python3
"""Record prototype-edition MP4s — Gallery 16:9 and Mobile 9:16.

Experimental. Shares the engine, JSON, timing and soundtrack with the shipping
landscape system; only the presentation layout differs.

  # Gallery Edition, kanji +50%, current weight
  python scripts/record_prototype_editions.py --edition gallery --type-lab a

  # Mobile Edition, one weight lighter, +50%
  python scripts/record_prototype_editions.py --edition mobile --type-lab b

  # All three typography versions of one edition, back to back
  python scripts/record_prototype_editions.py --edition mobile --type-lab all

  # Party Kanji spacing test (short)
  python scripts/record_prototype_editions.py --collection proto_party_kanji_lab \
      --edition mobile --type-lab b

Output: collections/prototypes/<collection>__<edition>_<lab>.mp4
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYWRIGHT_BROWSERS = ROOT / ".playwright-browsers"
OUT_DIR = ROOT / "collections" / "prototypes"

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

VIEWPORTS = {
    "gallery": {"width": 1920, "height": 1080},
    "mobile": {"width": 1080, "height": 1920},
}

# Weight 500 is only reachable through the lab, so the engine never preloads it.
PRELOAD_FONTS = [
    '500 5rem "Noto Serif JP"',
    '600 5rem "Noto Serif JP"',
    '400 5rem "Noto Serif JP"',
    'italic 500 3rem "Cormorant Garamond"',
    '400 5rem "Yuji Syuku"',
]


def record(*, collection_id: str, edition: str, type_lab: str, port: int) -> Path:
    collection = load_collection(ROOT, collection_id)
    timeout_ms = presentation_timeout_ms(collection, ROOT, extra_ms=180_000)

    display = dict(collection.get("display") or {})
    display.setdefault("typography", "mobile-refine")
    extra = {"typeLab": type_lab}
    if edition == "mobile":
        extra["edition"] = "mobile"
    if display.get("exhibitProfile") == "partyKanji":
        extra["skipBookends"] = "1"
    url = exhibition_record_url(
        port=port, collection_id=collection_id, display=display, extra_params=extra
    )

    suffix = f"{edition}_{type_lab}"
    out_path = OUT_DIR / f"{collection_id}__{suffix}.mp4"
    tmp_dir = OUT_DIR / f".tmp_{collection_id}_{suffix}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording {collection_id} [{edition} / version {type_lab.upper()}] → {out_path.name}")

    webm = capture_exhibition_webm(
        url=url,
        tmp_dir=tmp_dir,
        timeout_ms=timeout_ms,
        viewport=VIEWPORTS[edition],
        preload_fonts=PRELOAD_FONTS,
    )

    soundtrack_rel = (collection.get("soundtrack") or {}).get("main") or ""
    if soundtrack_rel:
        soundtrack = ROOT / soundtrack_rel
        if not soundtrack.is_file():
            raise FileNotFoundError(f"Missing soundtrack: {soundtrack}")
        start_ms = vocabulary_exhibition_soundtrack_start_ms(collection)
        print(f"  Soundtrack: {soundtrack_rel} @ {start_ms} ms")
        tmp_mux = tmp_dir / "muxed.mp4"
        mux_exhibition_soundtrack(
            webm=webm,
            output_mp4=tmp_mux,
            soundtrack=soundtrack,
            soundtrack_start_ms=start_ms,
        )
        shutil.move(str(tmp_mux), str(out_path))
    else:
        # Party Kanji has no soundtrack — transcode the silent capture as-is.
        import subprocess

        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(webm),
                "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                "-pix_fmt", "yuv420p", str(out_path),
            ],
            check=True,
        )

    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()

    print(f"  → {out_path}")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", default="proto_typography_lab")
    parser.add_argument("--edition", choices=("gallery", "mobile"), default="mobile")
    parser.add_argument("--type-lab", choices=("a", "b", "c", "all"), default="b")
    parser.add_argument("--port", type=int, default=9401)
    args = parser.parse_args()

    labs = ["a", "b", "c"] if args.type_lab == "all" else [args.type_lab]

    ensure_deps()
    if PLAYWRIGHT_BROWSERS.is_dir():
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    server = start_server(ROOT, args.port)
    try:
        for lab in labs:
            record(
                collection_id=args.collection,
                edition=args.edition,
                type_lab=lab,
                port=args.port,
            )
    finally:
        stop_server(server)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
