import csv
import json
import hashlib
from pathlib import Path

# =====================================================
# CONFIG
# =====================================================

BASE_DIR = Path("kml/data/kanji")

CSV_PATH = BASE_DIR / "kanji_production.csv"

MASK_DIR = BASE_DIR / "masks"
PROMPT_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = BASE_DIR / "outputs"
META_DIR = BASE_DIR / "metadata"

PROMPT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
META_DIR.mkdir(exist_ok=True)

PROMPT_VERSION = "v2.0"
# =====================================================
# MASTER PROMPT EXPORT
# =====================================================

MASTER_PROMPT_FILE = BASE_DIR / "all_prompts.txt"

master_prompts = []
VARIANTS = 3


# =====================================================
# LESSON CONTROL
# =====================================================

# Example:
# LESSON_START = 1
# LESSON_END = 20

LESSON_START = 1
LESSON_END = 20

# =====================================================
# STYLE PROFILES
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
"""
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

def clean(value):
    return (value or "").strip()


def field(row, key, default=""):
    return clean(row.get(key, default))


def file_hash(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def build_prompt(
    kanji,
    mask_path,
    lesson_palette,
    flow,
    mode,
    paint_density,
    energy,
):
    style_profile = STYLE_PROFILES.get(mode, "")

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

=====================================================
COMPOSITION
=====================================================

{COMPOSITION_RULES}

=====================================================
NEGATIVE RULES
=====================================================

{NEGATIVE_RULES}
""".strip()


# =====================================================
# MAIN
# =====================================================

missing_masks = []
generated = 0
skipped = 0

with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:

    reader = csv.DictReader(f)

    for index, row in enumerate(reader, start=1):

        # =============================================
        # LESSON LIMITING
        # =============================================

        if index < LESSON_START:
            continue

        if index > LESSON_END:
            break

        # =============================================
        # FIELDS
        # =============================================

        kanji = field(row, "kanji")
        slug = field(row, "slug")

        flow = field(row, "flow")
        mode = field(row, "mode")

        lesson_palette = (
            field(row, "lesson_palette")
            or field(row, "palette")
        )

        paint_density = field(
            row,
            "paint_density",
            "medium impasto"
        )

        energy = field(
            row,
            "energy",
            "balanced"
        )

        if not slug:
            print(f"SKIP: missing slug for {kanji}")
            skipped += 1
            continue

        # =============================================
        # MASK CHECK
        # =============================================

        mask_path = MASK_DIR / f"{slug}.png"

        if not mask_path.exists():
            print(f"MISSING MASK: {kanji} → {mask_path}")
            missing_masks.append(slug)
            skipped += 1
            continue

        # =============================================
        # BUILD PROMPT
        # =============================================

        prompt = build_prompt(
            kanji=kanji,
            mask_path=mask_path.as_posix(),
            lesson_palette=lesson_palette,
            flow=flow,
            mode=mode,
            paint_density=paint_density,
            energy=energy,
        )

        # =============================================
        # HASH CHECK
        # =============================================

        prompt_hash = file_hash(prompt)

        meta_file = META_DIR / f"{slug}.json"

        if meta_file.exists():

            old_meta = json.loads(
                meta_file.read_text(encoding="utf-8")
            )

            if old_meta.get("prompt_hash") == prompt_hash:
                print(f"UNCHANGED: {kanji}")
                skipped += 1
                continue

                # =============================================
        # SAVE PROMPT
        # =============================================

        for i in range(1, VARIANTS + 1):

            variant_id = f"{i:02}"

            prompt_file = (
                PROMPT_DIR /
                f"{slug}_{variant_id}.txt"
            )

            prompt_file.write_text(
                prompt,
                encoding="utf-8"
            )

            # =========================================
            # MASTER PROMPT EXPORT
            # =========================================

            master_prompts.append(
                f"""
==================================================
KANJI: {kanji}
SLUG: {slug}
VARIANT: {variant_id}
==================================================

{prompt}

"""
            )

            print(
                f"OK: {kanji} variant {variant_id}"
            )

            generated += 1

        # =============================================
        # SAVE METADATA
        # =============================================

        metadata = {
            "prompt_version": PROMPT_VERSION,
            "kanji": kanji,
            "slug": slug,
            "mask_path": mask_path.as_posix(),
            "palette": lesson_palette,
            "flow": flow,
            "mode": mode,
            "paint_density": paint_density,
            "energy": energy,
            "prompt_hash": prompt_hash,
        }

        meta_file.write_text(
            json.dumps(
                metadata,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )
        # =============================================
        # SAVE PROMPT
        # =============================================

        for i in range(1, VARIANTS + 1):

            variant_id = f"{i:02}"

            prompt_file = (
                PROMPT_DIR /
                f"{slug}_{variant_id}.txt"
            )

            prompt_file.write_text(
                prompt,
                encoding="utf-8"
            )

            # =========================================
            # MASTER PROMPT EXPORT
            # =========================================

            master_prompts.append(
                f"""
==================================================
KANJI: {kanji}
SLUG: {slug}
VARIANT: {variant_id}
==================================================

{prompt}

"""
            )

            print(
                f"OK: {kanji} variant {variant_id}"
            )

            generated += 1
        print(f"OK: {kanji} → {prompt_file}")

        generated += 1

# =====================================================
# SAVE MISSING MASK REPORT
# =====================================================

if missing_masks:

    missing_file = BASE_DIR / "missing_masks.txt"

    missing_file.write_text(
        "\n".join(missing_masks),
        encoding="utf-8"
    )

# =====================================================
# SUMMARY
# =====================================================

print("\n====================================")
print("DONE")
print("====================================")
print(f"Generated: {generated}")
print(f"Skipped:   {skipped}")
print(f"Missing:   {len(missing_masks)}")
print("====================================")