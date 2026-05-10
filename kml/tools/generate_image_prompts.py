#!/usr/bin/env python3
"""
Generate per-kanji image prompts from kanji_image_production.csv + lesson_styles.json.

Run from repo root (or any cwd): paths resolve from this file location.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

# =====================================================
# CONFIG
# =====================================================

SCRIPT_DIR = Path(__file__).resolve().parent
KML_DIR = SCRIPT_DIR.parent
BASE_DIR = KML_DIR / "data" / "kanji"

CSV_PATH = BASE_DIR / "kanji_image_production.csv"
STYLES_PATH = KML_DIR / "config" / "lesson_styles.json"

MASK_DIR = BASE_DIR / "masks"
PROMPT_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = BASE_DIR / "outputs"
META_DIR = BASE_DIR / "metadata"

PROMPT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_VERSION = "v3.0"

VARIANTS = 3

# Inclusive bounds on CSV `kanji_index` (1-based). Process full sheet by default.
ROW_START = 1
ROW_END = 10**9

# =====================================================
# LESSON STYLES
# =====================================================


def load_lesson_styles(path: Path) -> dict[int, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    lookup: dict[int, dict] = {}
    for entry in data["lessons"]:
        n = int(entry["lesson"])
        lookup[n] = entry
    return lookup


def validate_style_lookup(lookup: dict[int, dict]) -> None:
    required = ("palette", "flow", "mode", "surface", "paint_density", "energy")
    missing_lessons: list[int] = []
    bad_keys: list[tuple[int, str]] = []
    for n in range(1, 154):
        if n not in lookup:
            missing_lessons.append(n)
            continue
        style = lookup[n]
        for key in required:
            if key not in style or not str(style.get(key, "")).strip():
                bad_keys.append((n, key))
    if missing_lessons:
        raise SystemExit(f"lesson_styles.json missing lessons: {missing_lessons[:20]}…")
    if bad_keys:
        raise SystemExit(f"lesson_styles.json incomplete styles: {bad_keys[:10]}…")


def lesson_dir_name(lesson_number: int) -> str:
    return f"lesson_{lesson_number:03d}"


# =====================================================
# PROMPT FILE HELPERS
# =====================================================


def get_lesson_dir(base_dir: Path, lesson_name: str) -> Path:
    lesson_dir = base_dir / lesson_name
    lesson_dir.mkdir(parents=True, exist_ok=True)
    return lesson_dir


def write_prompt_file(
    prompt_text: str,
    lesson_name: str,
    slug: str,
    variant_num: str,
) -> Path:
    lesson_prompt_dir = get_lesson_dir(PROMPT_DIR, lesson_name)
    filename = f"{slug}_v{variant_num}.txt"
    output_path = lesson_prompt_dir / filename
    output_path.write_text(prompt_text, encoding="utf-8")
    return output_path


# =====================================================
# STYLE PROFILES (mode / surface expansion text)
# =====================================================

STYLE_PROFILES = {
    "standard": """
Balanced painterly treatment.
Respect the original structure.
Moderate texture depth.
""",
    "motion": """
Allow directional energy and visible brush movement.
Paint flow may imply motion,
but must never distort the kanji geometry.
""",
    "contained": """
Controlled energy.
Quiet composition.
Internal tension rather than outward explosion.
""",
    "hero": """
Museum-quality presentation.
Rich material interaction.
Elegant paint behavior.
Strong visual presence while preserving simplicity.
""",
    "fast": """
Slightly looser paint handling.
Faster expressive strokes.
Still preserve exact kanji structure.
""",
}

SURFACE_PROFILES = {
    "clean": """
Cleaner paint handling.
More stable edges.
Controlled surface transitions.
Lower paint chaos.
""",
    "painterly": """
Visible brush breakup.
Minor irregular paint ridges.
Organic paint accumulation.
Subtle edge instability.
""",
    "raw": """
Heavy material interaction.
Visible scraping and drag.
Broken paint edges.
Uneven paint density.
Canvas interaction remains visible.
""",
    "museum": """
Rich layered surface behavior.
Complex paint breakup.
Subtle historical oil painting feel.
Controlled imperfection.
""",
}

# =====================================================
# PROMPT SECTIONS
# =====================================================

STRUCTURE_RULES = """
Use the provided kanji mask image as the exact shape reference.

Do not alter, reinterpret, stylize, correct, or improve the kanji structure.

Preserve the original mask shape exactly.

No added strokes.
No removed strokes.
No merged strokes.
No disconnected fragments.
"""

STYLE_RULES = """
Apply painterly impasto oil paint texture to the existing kanji form.

The paint must feel integrated into the canvas surface,
not sculpted on top.

Natural brush variation is encouraged.
Material richness is encouraged.
"""

COMPOSITION_RULES = """
Square composition.
Centered composition.
Balanced margins.

The kanji and background must feel like one unified painting.

The background should support the kanji,
not compete with it.
"""

NEGATIVE_RULES = """
Avoid:
- logo rendering
- vector appearance
- glossy typography
- metallic effects
- embossed edges
- floating symbols
- isolated object rendering
- 3D extrusion
- beveled carving
- cast shadows
"""

# =====================================================
# HELPERS
# =====================================================


def clean(value: str | None) -> str:
    return (value or "").strip()


def field(row: dict[str, str], key: str, default: str = "") -> str:
    return clean(row.get(key, default))


def file_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# =====================================================
# BUILD PROMPT
# =====================================================


def build_prompt(
    kanji: str,
    mask_path: str,
    lesson_palette: str,
    flow: str,
    mode: str,
    surface: str,
    paint_density: str,
    energy: str,
    special_state: str | None = None,
) -> str:
    style_profile = STYLE_PROFILES.get(mode, "")
    surface_profile = SURFACE_PROFILES.get(surface, "")

    special_block = ""
    if special_state:
        special_block = f"""
=====================================================
SPECIAL ATMOSPHERE
==================

{special_state}
"""

    return f"""
Japanese kanji: {kanji}

=====================================================
MASK REFERENCE
=====================================================

Use this mask image as the exact structural reference:

{mask_path}

=====================================================
STRUCTURE RULES
=====================================================

{STRUCTURE_RULES}

=====================================================
STYLE RULES
=====================================================

{STYLE_RULES}

=====================================================
STYLE PROFILE
=====================================================

{style_profile}

=====================================================
SURFACE QUALITY
=====================================================

{surface_profile}

=====================================================
PALETTE
=====================================================

{lesson_palette}

=====================================================
BACKGROUND FLOW
=====================================================

{flow}

=====================================================
PAINT DENSITY
=====================================================

{paint_density}

=====================================================
ENERGY
=====================================================

{energy}
{special_block}
=====================================================
COMPOSITION
=====================================================

{COMPOSITION_RULES}

=====================================================
NEGATIVE RULES
=====================================================

{NEGATIVE_RULES}

=====================================================
PAINTERLY IMPERFECTION
=====================================================

Avoid overly perfect digital smoothness.

Minor painterly imperfections are desirable.

The image should feel handmade rather than mechanically rendered.
""".strip()


# =====================================================
# MAIN
# =====================================================


def main() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing CSV: {CSV_PATH}")
    if not STYLES_PATH.exists():
        raise SystemExit(f"Missing styles JSON: {STYLES_PATH}")

    lesson_styles = load_lesson_styles(STYLES_PATH)
    validate_style_lookup(lesson_styles)

    missing_masks: list[str] = []
    generated = 0
    skipped = 0
    lesson_folders_created: set[str] = set()

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        expected_cols = {
            "kanji_index",
            "kanji",
            "slug",
            "keyword",
            "lesson_number",
            "kml_primitives",
            "cluster_components",
            "jp_verse",
            "en_verse",
        }
        if reader.fieldnames is None:
            raise SystemExit("CSV has no header")
        fn = set(reader.fieldnames)
        if not expected_cols.issubset(fn):
            raise SystemExit(f"CSV missing columns. Have {sorted(fn)}")

        for row in reader:
            try:
                ki = int(field(row, "kanji_index", "0") or "0")
            except ValueError:
                ki = 0
            if ki < ROW_START or ki > ROW_END:
                continue

            kanji = field(row, "kanji")
            slug = field(row, "slug")
            lesson_num_raw = field(row, "lesson_number")
            if not lesson_num_raw:
                print(f"SKIP: missing lesson_number for kanji_index={ki} {kanji!r}")
                skipped += 1
                continue
            lesson_number = int(lesson_num_raw)
            style = lesson_styles[lesson_number]

            palette = field(style, "palette")
            flow = field(style, "flow")
            mode = field(style, "mode")
            surface = field(style, "surface")
            paint_density = field(style, "paint_density")
            energy = field(style, "energy")
            special_raw = style.get("special_state")
            special_state = (
                str(special_raw).strip() if special_raw is not None else ""
            ) or None

            if not slug:
                print(f"SKIP: missing slug for {kanji}")
                skipped += 1
                continue

            mask_path = MASK_DIR / f"{slug}.png"
            if not mask_path.exists():
                print(f"MISSING MASK: {kanji} → {mask_path}")
                missing_masks.append(slug)
                skipped += 1
                continue

            prompt = build_prompt(
                kanji=kanji,
                mask_path=mask_path.as_posix(),
                lesson_palette=palette,
                flow=flow,
                mode=mode,
                surface=surface,
                paint_density=paint_density,
                energy=energy,
                special_state=special_state,
            )

            prompt_hash = file_hash(prompt)
            meta_file = META_DIR / f"{slug}.json"

            if meta_file.exists():
                old_meta = json.loads(meta_file.read_text(encoding="utf-8"))
                if old_meta.get("prompt_hash") == prompt_hash:
                    print(f"UNCHANGED: {kanji}")
                    skipped += 1
                    continue

            lesson_name = lesson_dir_name(lesson_number)
            lesson_folders_created.add(lesson_name)

            for i in range(1, VARIANTS + 1):
                variant_id = f"{i:02}"
                write_prompt_file(
                    prompt_text=prompt,
                    lesson_name=lesson_name,
                    slug=slug,
                    variant_num=variant_id,
                )
                print(f"OK: {kanji} {lesson_name} variant {variant_id}")
                generated += 1

    print()
    print("=== generate_image_prompts.py summary ===")
    print(f"PROMPT_VERSION: {PROMPT_VERSION}")
    print(f"Total prompt files written (this run): {generated}")
    print(f"Skipped (unchanged / missing data / missing mask): {skipped}")
    uniq_missing = sorted(set(missing_masks))
    print(
        f"Missing mask occurrences: {len(missing_masks)} "
        f"(unique slugs: {len(uniq_missing)}): "
        f"{uniq_missing[:30]}{'…' if len(uniq_missing) > 30 else ''}"
    )
    print(f"Distinct lesson folders touched: {len(lesson_folders_created)}")
    if lesson_folders_created:
        sample = sorted(lesson_folders_created)[:5]
        print(f"  sample: {sample} …")

    if generated and lesson_folders_created:
        first = sorted(lesson_folders_created)[0]
        pdir = PROMPT_DIR / first
        if not pdir.is_dir():
            raise SystemExit(f"Expected lesson folder missing: {pdir}")

    # Ensure style lookup covers all lesson numbers used in CSV
    # Full pass: re-read lesson numbers from CSV
    used_lessons: set[int] = set()
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f2:
        r2 = csv.DictReader(f2)
        for r in r2:
            ln = field(r, "lesson_number")
            if ln:
                used_lessons.add(int(ln))
    missing_in_styles = sorted(used_lessons - set(lesson_styles.keys()))
    if missing_in_styles:
        raise SystemExit(f"CSV uses lesson_numbers not in lesson_styles.json: {missing_in_styles[:30]}")

    print("Style lookup: all lesson_number values in CSV exist in lesson_styles.json.")
    print("Legacy CSV style columns: not referenced (image CSV + JSON only).")


if __name__ == "__main__":
    main()
