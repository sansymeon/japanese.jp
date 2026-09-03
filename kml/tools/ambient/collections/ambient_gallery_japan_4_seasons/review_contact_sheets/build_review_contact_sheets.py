#!/usr/bin/env python3
"""Build JPG contact sheets for a unified Ambient Japan 4h exhibition review.

Read-only: does not change exclusions, candidate lists, or source images.
Uses the current core pool (KML survivors + accepted Start Here + new additions).
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCENERY = Path(__file__).resolve().parents[1] / ".." / "ambient_japan_4h_scenery"
SCENERY = SCENERY.resolve()
CANDIDATES = SCENERY / "candidates.json"
EXCLUSIONS = Path(__file__).resolve().parents[1] / "exclusions.json"
OUT = Path(__file__).resolve().parent

SHEET_W, SHEET_H = 5120, 2880
COLS, ROWS = 8, 5
PER_SHEET = COLS * ROWS  # 40
MARGIN = 28
HEADER_H = 78
GAP = 14
CAPTION_H = 72
BG = (22, 22, 22)
CELL_BG = (12, 12, 12)
FG = (236, 236, 236)
MUTED = (168, 168, 168)
FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def load_exclude() -> set[str]:
    if not EXCLUSIONS.is_file():
        return set()
    data = json.loads(EXCLUSIONS.read_text(encoding="utf-8"))
    return {str(s) for s in (data.get("excludeSlugs") or [])}


def load_exhibition() -> list[tuple[str, Path]]:
    """Unified proposed exhibition: current core pool only, alphabetical."""
    excluded = load_exclude()
    data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    items = []
    seen = set()
    for rec in data["corePool"]:
        stem = rec["stem"]
        if stem in excluded or stem in seen:
            continue
        path = (SCENERY / rec["rel"]).resolve()
        items.append((stem, path))
        seen.add(stem)
    items.sort(key=lambda x: x[0].lower())
    return items


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold and FONT_BOLD.is_file() else FONT_PATH
    return ImageFont.truetype(str(path), size)


def contain(src: Image.Image, box_w: int, box_h: int) -> Image.Image:
    """Fit the whole image in the box. No crop."""
    img = src.convert("RGB")
    scale = min(box_w / img.width, box_h / img.height)
    new_w = max(1, int(img.width * scale))
    new_h = max(1, int(img.height * scale))
    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)


def cell_geometry() -> tuple[int, int, int, int]:
    usable_w = SHEET_W - 2 * MARGIN
    usable_h = SHEET_H - MARGIN - HEADER_H
    cell_w = usable_w // COLS
    cell_h = usable_h // ROWS
    thumb_w = cell_w - GAP
    thumb_h = cell_h - GAP - CAPTION_H
    return cell_w, cell_h, thumb_w, thumb_h


def draw_header(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> None:
    draw.text((MARGIN, 18), title, font=font(32, bold=True), fill=FG)
    draw.text((MARGIN, 52), subtitle, font=font(22), fill=MUTED)


def paint_cell(
    sheet: Image.Image,
    draw: ImageDraw.ImageDraw,
    *,
    col: int,
    row: int,
    stem: str,
    path: Path,
    cell_w: int,
    cell_h: int,
    thumb_w: int,
    thumb_h: int,
) -> None:
    x0 = MARGIN + col * cell_w
    y0 = HEADER_H + row * cell_h
    thumb_box = Image.new("RGB", (thumb_w, thumb_h), CELL_BG)
    with Image.open(path) as src:
        fitted = contain(src, thumb_w, thumb_h)
    px = (thumb_w - fitted.width) // 2
    py = (thumb_h - fitted.height) // 2
    thumb_box.paste(fitted, (px, py))
    sheet.paste(thumb_box, (x0, y0))
    draw.text((x0, y0 + thumb_h + 8), stem, font=font(22, bold=True), fill=FG)


def write_sheet(
    items: list[tuple[str, Path]],
    *,
    out_path: Path,
    title: str,
    subtitle: str,
) -> None:
    cell_w, cell_h, thumb_w, thumb_h = cell_geometry()
    sheet = Image.new("RGB", (SHEET_W, SHEET_H), BG)
    draw = ImageDraw.Draw(sheet)
    draw_header(draw, title, subtitle)
    for i, (stem, path) in enumerate(items):
        col = i % COLS
        row = i // COLS
        if row >= ROWS:
            break
        paint_cell(
            sheet,
            draw,
            col=col,
            row=row,
            stem=stem,
            path=path,
            cell_w=cell_w,
            cell_h=cell_h,
            thumb_w=thumb_w,
            thumb_h=thumb_h,
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, "JPEG", quality=88, optimize=True, subsampling=1)
    print(f"wrote {out_path.name}  ({out_path.stat().st_size / 1_000_000:.1f} MB)")


def write_manifest(items: list[tuple[str, Path]], sheets_meta: list[dict]) -> None:
    lines = [
        "Ambient Japan 4h — proposed exhibition (inspection only)",
        f"total images: {len(items)}",
        f"contact sheets: {len(sheets_meta)}",
        "order: alphabetical by slug",
        "",
        "sheets:",
    ]
    for m in sheets_meta:
        lines.append(f"  {m['file']}: {m['count']}  {m['first']} – {m['last']}")
    lines.append("")
    lines.append("filenames:")
    for stem, _path in items:
        lines.append(stem)
    (OUT / "manifest.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {
        "id": "ambient_japan_4h_exhibition_review",
        "notes": "Inspection only. Unified proposed exhibition, alphabetical.",
        "totalImages": len(items),
        "sheets": sheets_meta,
        "slugs": [stem for stem, _ in items],
    }
    (OUT / "manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT / 'manifest.txt'}")
    print(f"wrote {OUT / 'manifest.json'}")


def main() -> None:
    items = load_exhibition()
    missing = [stem for stem, path in items if not path.is_file()]
    if missing:
        raise SystemExit(f"missing source files: {missing}")

    for stale in OUT.glob("ambient_japan_*.jpg"):
        stale.unlink()

    sheets_meta = []
    n_sheets = (len(items) + PER_SHEET - 1) // PER_SHEET
    for i in range(n_sheets):
        chunk = items[i * PER_SHEET : (i + 1) * PER_SHEET]
        first = chunk[0][0]
        last = chunk[-1][0]
        name = f"ambient_japan_review_{i + 1:02d}.jpg"
        write_sheet(
            chunk,
            out_path=OUT / name,
            title=f"Ambient Japan 4h  ·  exhibition review {i + 1:02d} of {n_sheets}",
            subtitle=f"{first}  –  {last}    ·    {len(chunk)} images    ·    alphabetical    ·    unified pool",
        )
        sheets_meta.append(
            {
                "file": name,
                "count": len(chunk),
                "first": first,
                "last": last,
            }
        )

    write_manifest(items, sheets_meta)
    print()
    print(f"total images: {len(items)}")
    print(f"contact sheets: {len(sheets_meta)}")
    for m in sheets_meta:
        print(f"  {m['file']}: {m['count']}  {m['first']} – {m['last']}")


if __name__ == "__main__":
    main()
