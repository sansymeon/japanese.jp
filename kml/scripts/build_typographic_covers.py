#!/usr/bin/env python3
"""Build temporary lesson covers: Yuji Syuku on a plain framed plate.

Reads kml/data/cover_kanji.json. Writes a PNG master to kml/assets/covers_png/
(gitignored) and a Q90 JPEG to kml/assets/covers/lesson_XX.jpg.

The live site keeps those JPEG paths. To install a finished artistic cover
later, replace that lesson's PNG master and JPEG with a native 1672×941 image
(use kml/scripts/publish_web_jpeg.py for the JPEG). Do not re-run this script
for a lesson once its artistic file is in place; it will overwrite it.

Lesson 154's character is not in Yuji Syuku. That one glyph is set in
Noto Serif CJK JP. The plate, ink, and frame stay the same.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "kml/data/cover_kanji.json"
YUJI = ROOT / "kml/tools/ambient/fonts/yuji-syuku/YujiSyuku-Regular.ttf"
NOTO = Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc")
PNG_DIR = ROOT / "kml/assets/covers_png"
JPG_DIR = ROOT / "kml/assets/covers"

PAPER = (239, 233, 220)  # lesson card paper, #efe9dc
INK = (31, 30, 27)  # same ink as .kanji-main-font
FRAME = (74, 68, 58)
INSET = 46
FRAME_WIDTH = 2
INNER_PAD = 64


def load_map() -> dict:
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    lessons = {int(k): v for k, v in data["lessons"].items()}
    fallback = set(data.get("fallback_lessons", []))
    size = tuple(data["size"])
    return {"lessons": lessons, "fallback": fallback, "size": size}


def measure(font: ImageFont.FreeTypeFont, ch: str) -> tuple[Image.Image, tuple[int, int, int, int]]:
    probe = max(font.size * 3, 64)
    canvas = Image.new("L", (probe, probe), 0)
    ImageDraw.Draw(canvas).text((probe // 2, probe // 2), ch, font=font, fill=255, anchor="mm")
    box = canvas.getbbox()
    if box is None:
        raise SystemExit(f"Font produced no ink for {ch!r}")
    return canvas, box


def fit_font(path: Path, index: int, ch: str, max_w: int, max_h: int) -> ImageFont.FreeTypeFont:
    # One shared em size, reduced only when the glyph would leave the mat.
    size = max_h
    for _ in range(12):
        font = ImageFont.truetype(str(path), size, index=index)
        _canvas, box = measure(font, ch)
        bw, bh = box[2] - box[0], box[3] - box[1]
        if bw <= max_w and bh <= max_h:
            return font
        scale = min(max_w / bw, max_h / bh)
        size = max(8, int(size * scale * 0.98))
    return ImageFont.truetype(str(path), size, index=index)


def render(ch: str, lesson: int, size: tuple[int, int], fallback: bool) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle(
        [INSET, INSET, width - 1 - INSET, height - 1 - INSET],
        outline=FRAME,
        width=FRAME_WIDTH,
    )
    max_w = width - 2 * (INSET + INNER_PAD)
    max_h = height - 2 * (INSET + INNER_PAD)
    if fallback:
        font = fit_font(NOTO, 0, ch, max_w, max_h)
    else:
        font = fit_font(YUJI, 0, ch, max_w, max_h)
    canvas, box = measure(font, ch)
    glyph = canvas.crop(box)
    gw, gh = glyph.size
    x = (width - gw) // 2
    y = (height - gh) // 2
    ink = Image.new("RGB", (gw, gh), INK)
    image.paste(ink, (x, y), glyph)
    return image


def publish(master: Path, web: Path) -> None:
    image = Image.open(master).convert("RGB")
    web.parent.mkdir(parents=True, exist_ok=True)
    image.save(web, "JPEG", quality=90, optimize=True, subsampling=0)
    out = Image.open(web)
    if out.size != image.size:
        web.unlink(missing_ok=True)
        raise SystemExit(f"Dimension mismatch writing {web}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "lessons",
        nargs="*",
        type=int,
        help="Lesson numbers to build. Default: every lesson in the map.",
    )
    args = parser.parse_args(argv)
    spec = load_map()
    chosen = args.lessons or sorted(spec["lessons"])
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    for n in chosen:
        if n not in spec["lessons"]:
            raise SystemExit(f"No cover kanji for lesson {n}")
        ch = spec["lessons"][n]
        image = render(ch, n, spec["size"], n in spec["fallback"])
        master = PNG_DIR / f"lesson_{n:02d}.png"
        web = JPG_DIR / f"lesson_{n:02d}.jpg"
        image.save(master, "PNG")
        publish(master, web)
        face = "Noto Serif CJK JP" if n in spec["fallback"] else "Yuji Syuku"
        print(f"lesson {n:03d}  {ch}  {face}  {image.size[0]}x{image.size[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
