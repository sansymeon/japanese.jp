#!/usr/bin/env python3
"""Publish a Q90 JPEG web derivative from a PNG master.

Architecture: PNG = production master; JPEG Q90 = browser delivery.
Do not resize, crop, or recolor. Website references should use the JPEG.

Examples:
  python3 kml/scripts/publish_web_jpeg.py kml/assets/studies_png/river.png
  python3 kml/scripts/publish_web_jpeg.py kml/assets/covers_png/lesson_46.png
  python3 kml/scripts/publish_web_jpeg.py kml/assets/images_png/vocabulary_7.png
  python3 kml/scripts/publish_web_jpeg.py start-here/assets/images_png/intro.png

The web path is inferred by mapping:
  studies_png/ → studies/
  covers_png/  → covers/
  images_png/  → images/
and writing the same stem with a .jpg suffix.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

MAPPINGS = (
    ("/studies_png/", "/studies/"),
    ("/covers_png/", "/covers/"),
    ("/images_png/", "/images/"),
)


def infer_web_path(master: Path) -> Path:
    posix = master.resolve().as_posix()
    for src, dst in MAPPINGS:
        if src in posix:
            return Path(posix.replace(src, dst, 1)).with_suffix(".jpg")
    raise SystemExit(
        f"Cannot infer web path from {master}. "
        "Expected a path containing studies_png, covers_png, or images_png."
    )


def publish(master: Path, web: Path) -> None:
    if master.suffix.lower() != ".png":
        raise SystemExit(f"Master must be a PNG: {master}")
    if not master.is_file():
        raise SystemExit(f"Missing master: {master}")
    im = Image.open(master)
    size = im.size
    if im.mode == "RGBA":
        amin, amax = im.getchannel("A").getextrema()
        if amin < 255:
            raise SystemExit(
                f"True transparency in {master.name}; leave as PNG or flatten first."
            )
        im = im.convert("RGB")
    elif im.mode != "RGB":
        im = im.convert("RGB")
    web.parent.mkdir(parents=True, exist_ok=True)
    save_kwargs = dict(quality=90, optimize=True, subsampling=0)
    icc = Image.open(master).info.get("icc_profile")
    if icc:
        save_kwargs["icc_profile"] = icc
    im.save(web, "JPEG", **save_kwargs)
    out = Image.open(web)
    if out.size != size:
        web.unlink(missing_ok=True)
        raise SystemExit(f"Dimension mismatch writing {web}")
    print(f"{master} → {web}  {size[0]}x{size[1]}  {web.stat().st_size} bytes")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("master", type=Path, help="PNG master path")
    parser.add_argument("--web", type=Path, help="JPEG output path (inferred if omitted)")
    args = parser.parse_args(argv)
    master = args.master.resolve()
    web = args.web.resolve() if args.web else infer_web_path(master)
    publish(master, web)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
