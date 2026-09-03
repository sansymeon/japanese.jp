#!/usr/bin/env python3
"""Build proposed playback sequence + numbered contact sheets.

Sequencing review only. Does not modify, delete, regenerate, or retime images.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCENERY = Path(__file__).resolve().parents[1] / ".." / "ambient_japan_4h_scenery"
SCENERY = SCENERY.resolve()
CANDIDATES = SCENERY / "candidates.json"
SEQ_JSON = SCENERY / "playback_sequence.json"
SEQ_TXT = SCENERY / "playback_sequence.txt"
OUT = Path(__file__).resolve().parent

SHEET_W, SHEET_H = 5120, 2880
COLS, ROWS = 6, 5
PER_SHEET = COLS * ROWS  # 30
MARGIN = 28
HEADER_H = 90
GAP = 18
CAPTION_H = 96
BG = (22, 22, 22)
CELL_BG = (12, 12, 12)
FG = (236, 236, 236)
MUTED = (168, 168, 168)
ACCENT = (210, 176, 118)
FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

# Proposed unhurried journey order. Mix seasons/places/subjects; keep
# rare textures (people, modern Japan, trains, yatai, matsuri, Fushimi,
# Nachi, Tokyo/Fuji) as occasional changes rather than a tour itinerary.
SEQUENCE = [
    "morning",
    "road",
    "room_7/mountain",
    "car",
    "home_village",
    "creek",
    "village",
    "country_station",
    "magome",
    "tea_shop",
    "dagashiya",
    "younger_sister",
    "bamboo_forest",
    "woods",
    "visit_shrine",
    "garden",
    "peach_tree",
    "ume",
    "hedge",
    "winter",
    "castle",
    "bell",
    "imperial_gardens",
    "kyoto",
    "train_cherry_blossoms",
    "rain",
    "lesson_24/bamboo_2",
    "raizan",
    "tea_fields",
    "plantation",
    "ice",
    "field",
    "fishing_village",
    "japan_alps_summer_2",
    "lavendar",
    "winter_honshu",
    "shinkansen",
    "villa",
    "thatched_roof",
    "lake_toya",
    "rice",
    "enlightenment",
    "mt_fuji_2",
    "sulfur",
    "transport",
    "monkey_hotspring",
    "starlight",
    "evening",
    "tsumago",
    "room-9",
    "wagashi_shop",
    "takayama",
    "kyoto_autumn",
    "persimmon",
    "winter_cranes",
    "rice_post_harvest",
    "nikko_fall_colors",
    "sun",
    "train_hydrangea",
    "lesson_40/kazega_yowai",
    "fushimi",
    "sakura_river",
    "weekday",
    "dike",
    "matsuri",
    "run_alongside",
    "gokayama_winter",
    "shopping_street",
    "castle_2",
    "tanuki",
    "nara_deer",
    "store",
    "location",
    "apple_blossoms",
    "futamigaura",
    "pavilion",
    "shiretoko_ice",
    "nikko_3",
    "tea",
    "nachi_falls",
    "japan_alps_winter",
    "courtyard",
    "room-15",
    "public_hall",
    "hida_furukawa",
    "pond",
    "slope",
    "room_9/kasa",
    "year_end",
    "busy",
    "yatai",
    "beguile",
    "skytree_view_fuji",
    "room-10",
    "eventide",
    "kyoto_pagoda",
    "shirakawa_spring",
    "country_train_summer",
    "senso_ji_temple",
    "next",
    "orderliness",
    "lesson_40/genki_desuka",
    "endure_silently",
    "saga_koinobori",
    "town",
    "remainder",
    "dazaifu_shopping",
    "mulberry",
    "pagoda",
    "fishing_village_2",
    "chant",
    "sakurajima",
    "miyajima",
    "permit",
    "good_luck",
    "east",
    "acknowledge",
    "rut",
    "okinawa_temple",
    "assurance",
    "hot_water",
    "righteousness",
    "kumamoto",
    "capital",
    "respond",
    "mediocre",
    "thatched_roof_winter",
    "stop",
    "apple_tree",
    "dog",
    "safeguard",
    "country_train_winter",
    "nikko_2",
    "melt",
    "temple",
    "incur",
    "kudzu",
    "shirakawa_winter",
    "few",
    "lesson_40/kotobaga_saku_2",
    "noon",
    "winter_evening",
]

# Soft grouping for cluster checks. An image may carry several tags.
TAGS: dict[str, set[str]] = {
    "mt_fuji_2": {"fuji"},
    "apple_blossoms": {"fuji", "spring"},
    "acknowledge": {"fuji"},
    "apple_tree": {"fuji", "winter"},
    "lesson_40/kotobaga_saku_2": {"fuji", "winter"},
    "skytree_view_fuji": {"fuji", "modern", "sunset"},
    "shinkansen": {"train", "rice", "modern"},
    "train_cherry_blossoms": {"train", "spring"},
    "train_hydrangea": {"train"},
    "country_train_summer": {"train"},
    "country_train_winter": {"train", "winter"},
    "country_station": {"train_adj"},
    "stop": {"train_adj"},
    "dog": {"train_adj", "people"},
    "next": {"train_adj"},
    "mediocre": {"train_adj"},
    "transport": {"train_adj"},
    "car": {"road"},
    "winter": {"winter"},
    "ice": {"winter"},
    "winter_honshu": {"winter"},
    "winter_cranes": {"winter"},
    "melt": {"winter"},
    "gokayama_winter": {"winter", "thatched"},
    "japan_alps_winter": {"winter"},
    "monkey_hotspring": {"winter"},
    "shiretoko_ice": {"winter"},
    "thatched_roof_winter": {"winter", "thatched"},
    "year_end": {"winter"},
    "endure_silently": {"winter"},
    "shirakawa_winter": {"winter", "thatched"},
    "winter_evening": {"winter", "sunset"},
    "visit_shrine": {"temple", "people"},
    "nachi_falls": {"temple", "falls"},
    "fushimi": {"temple"},
    "okinawa_temple": {"temple"},
    "senso_ji_temple": {"temple"},
    "kyoto_pagoda": {"temple"},
    "pagoda": {"temple"},
    "chant": {"temple"},
    "temple": {"temple"},
    "nikko_2": {"temple", "nikko"},
    "nikko_3": {"temple", "nikko"},
    "nikko_fall_colors": {"temple", "nikko", "autumn"},
    "nara_deer": {"temple", "people"},
    "miyajima": {"temple"},
    "good_luck": {"temple"},
    "bell": {"temple"},
    "enlightenment": {"temple"},
    "courtyard": {"temple"},
    "raizan": {"temple"},
    "castle": {"castle"},
    "castle_2": {"castle"},
    "kumamoto": {"castle"},
    "rice": {"rice"},
    "field": {"rice"},
    "room_7/mountain": {"rice"},
    "starlight": {"rice", "night"},
    "rice_post_harvest": {"rice", "autumn"},
    "magome": {"street"},
    "tsumago": {"street"},
    "takayama": {"street"},
    "hida_furukawa": {"street"},
    "kyoto": {"street"},
    "town": {"street"},
    "dazaifu_shopping": {"street"},
    "shopping_street": {"street"},
    "busy": {"street"},
    "lesson_40/genki_desuka": {"street", "people"},
    "room_9/kasa": {"street"},
    "morning": {"sunset"},
    "sun": {"sunset"},
    "east": {"sunset"},
    "evening": {"sunset"},
    "eventide": {"sunset"},
    "room-9": {"sunset"},
    "creek": {"stream"},
    "dike": {"stream"},
    "run_alongside": {"stream"},
    "thatched_roof": {"thatched"},
    "shirakawa_spring": {"thatched"},
    "bamboo_forest": {"bamboo"},
    "lesson_24/bamboo_2": {"bamboo"},
    "younger_sister": {"people"},
    "lesson_40/kazega_yowai": {"people"},
    "yatai": {"modern", "night", "people"},
    "matsuri": {"people"},
    "sakura_river": {"stream", "spring", "people"},
}


NO_CONSECUTIVE = {
    "fuji",
    "train",
    "temple",
    "rice",
    "sunset",
    "street",
    "falls",
    "stream",
    "thatched",
    "castle",
    "bamboo",
    "nikko",
    "winter",
    "people",
    "night",
}

MIN_GAP = {
    "fuji": 8,
    "train": 8,
    "falls": 12,
    "night": 10,
}


def load_pool() -> dict[str, Path]:
    data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    pool: dict[str, Path] = {}
    for rec in data["corePool"]:
        stem = rec["stem"]
        pool[stem] = (SCENERY / rec["rel"]).resolve()
    return pool


def validate_membership(pool: dict[str, Path]) -> None:
    seq = SEQUENCE
    if len(seq) != len(pool):
        raise SystemExit(f"sequence length {len(seq)} != pool {len(pool)}")
    if len(set(seq)) != len(seq):
        dupes = sorted({s for s in seq if seq.count(s) > 1})
        raise SystemExit(f"duplicate stems: {dupes}")
    missing = sorted(set(pool) - set(seq))
    extra = sorted(set(seq) - set(pool))
    if missing or extra:
        raise SystemExit(f"missing from sequence: {missing}\nextra: {extra}")
    absent = [s for s, p in pool.items() if not p.is_file()]
    if absent:
        raise SystemExit(f"missing source files: {absent}")


def cluster_report() -> list[str]:
    warnings: list[str] = []
    last_pos: dict[str, int] = {}
    prev_tags: set[str] = set()
    for i, stem in enumerate(SEQUENCE):
        tags = TAGS.get(stem, set())
        overlap = tags & prev_tags & NO_CONSECUTIVE
        if overlap:
            warnings.append(
                f"{i:03d}/{i + 1:03d} consecutive {sorted(overlap)}: "
                f"{SEQUENCE[i - 1]} → {stem}"
            )
        if "train" in tags and "train_adj" in prev_tags:
            warnings.append(f"{i:03d} train after train-adjacent: {SEQUENCE[i - 1]} → {stem}")
        if "train_adj" in tags and "train" in prev_tags:
            warnings.append(f"{i:03d} train-adjacent after train: {SEQUENCE[i - 1]} → {stem}")
        for tag in tags:
            if tag in last_pos and tag in MIN_GAP:
                gap = i - last_pos[tag]
                if gap < MIN_GAP[tag]:
                    warnings.append(
                        f"{i:03d} {tag} gap {gap} < {MIN_GAP[tag]}: "
                        f"{SEQUENCE[last_pos[tag]]} … {stem}"
                    )
            last_pos[tag] = i
        prev_tags = tags
    return warnings


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold and FONT_BOLD.is_file() else FONT_PATH
    return ImageFont.truetype(str(path), size)


def contain(src: Image.Image, box_w: int, box_h: int) -> Image.Image:
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


def paint_cell(
    sheet: Image.Image,
    draw: ImageDraw.ImageDraw,
    *,
    index: int,
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
    overlay = ImageDraw.Draw(thumb_box)
    number = f"{index:03d}"
    num_font = font(42, bold=True)
    bbox = overlay.textbbox((0, 0), number, font=num_font)
    nw, nh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 12, 8
    badge = (8, 8, 8 + nw + 2 * pad_x, 8 + nh + 2 * pad_y)
    overlay.rectangle(badge, fill=(0, 0, 0))
    overlay.text((8 + pad_x, 8 + pad_y - 2), number, font=num_font, fill=ACCENT)
    sheet.paste(thumb_box, (x0, y0))
    draw.text((x0, y0 + thumb_h + 6), number, font=font(36, bold=True), fill=ACCENT)
    draw.text((x0, y0 + thumb_h + 48), stem, font=font(22, bold=True), fill=FG)


def write_sheet(
    items: list[tuple[int, str, Path]],
    *,
    out_path: Path,
    title: str,
    subtitle: str,
) -> None:
    cell_w, cell_h, thumb_w, thumb_h = cell_geometry()
    sheet = Image.new("RGB", (SHEET_W, SHEET_H), BG)
    draw = ImageDraw.Draw(sheet)
    draw.text((MARGIN, 18), title, font=font(32, bold=True), fill=FG)
    draw.text((MARGIN, 54), subtitle, font=font(22), fill=MUTED)
    for i, (index, stem, path) in enumerate(items):
        col = i % COLS
        row = i // COLS
        if row >= ROWS:
            break
        paint_cell(
            sheet,
            draw,
            index=index,
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


def write_manifest(items: list[tuple[int, str, Path]], sheets_meta: list[dict]) -> None:
    numbered = [
        {
            "n": n,
            "id": f"{n:03d}",
            "stem": stem,
            "rel": str(path.relative_to(SCENERY.parent))
            if str(path).startswith(str(SCENERY.parent))
            else str(path),
        }
        for n, stem, path in items
    ]
    payload = {
        "id": "ambient_japan_4h_playback_sequence",
        "title": "Ambient Japan 4h — proposed playback sequence",
        "status": "proposed",
        "notes": (
            "Sequencing review only. Exact proposed playback order for the "
            "current approved 142-image pool. Source images, exclusions, and "
            "timings are unchanged. Once approved, this order is the source of "
            "truth for the prototype/render."
        ),
        "pool": "ambient_japan_4h_scenery/candidates.json corePool",
        "totalImages": len(items),
        "numbering": "001-based, matching contact-sheet labels",
        "sheets": sheets_meta,
        "sequence": numbered,
    }
    SEQ_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "Ambient Japan 4h — proposed playback sequence",
        "Status: proposed (sequencing review only)",
        f"Total images: {len(items)}",
        "Numbering matches contact-sheet labels 001…",
        "",
        "Contact sheets:",
    ]
    for m in sheets_meta:
        lines.append(
            f"  {m['file']}: {m['idFirst']}–{m['idLast']}  {m['first']} – {m['last']}"
        )
    lines.append("")
    lines.append("Sequence:")
    for n, stem, _path in items:
        lines.append(f"{n:03d}  {stem}")
    SEQ_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    (OUT / "manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (OUT / "manifest.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {SEQ_JSON}")
    print(f"wrote {SEQ_TXT}")
    print(f"wrote {OUT / 'manifest.txt'}")


def main() -> None:
    pool = load_pool()
    validate_membership(pool)
    warnings = cluster_report()
    if warnings:
        print("cluster warnings:")
        for w in warnings:
            print(f"  {w}")
        print()

    items = [(i + 1, stem, pool[stem]) for i, stem in enumerate(SEQUENCE)]

    for stale in OUT.glob("ambient_japan_playback_*.jpg"):
        stale.unlink()

    sheets_meta = []
    n_sheets = (len(items) + PER_SHEET - 1) // PER_SHEET
    for i in range(n_sheets):
        chunk = items[i * PER_SHEET : (i + 1) * PER_SHEET]
        name = f"ambient_japan_playback_{i + 1:02d}.jpg"
        first_n, first_stem, _ = chunk[0]
        last_n, last_stem, _ = chunk[-1]
        write_sheet(
            chunk,
            out_path=OUT / name,
            title=f"Ambient Japan 4h  ·  proposed playback  {i + 1:02d} of {n_sheets}",
            subtitle=(
                f"{first_n:03d} {first_stem}  –  {last_n:03d} {last_stem}"
                f"    ·    {len(chunk)} images    ·    playback order    ·    review only"
            ),
        )
        sheets_meta.append(
            {
                "file": name,
                "count": len(chunk),
                "idFirst": f"{first_n:03d}",
                "idLast": f"{last_n:03d}",
                "first": first_stem,
                "last": last_stem,
            }
        )

    write_manifest(items, sheets_meta)
    print()
    print(f"total images: {len(items)}")
    print(f"contact sheets: {len(sheets_meta)}")
    for m in sheets_meta:
        print(f"  {m['file']}: {m['idFirst']}–{m['idLast']}  {m['first']} – {m['last']}")


if __name__ == "__main__":
    main()
