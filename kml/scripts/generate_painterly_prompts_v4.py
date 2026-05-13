#!/usr/bin/env python3
"""
KML painterly prompt generation v4 (optical refinement of v3.1).

Preserves the entire v3.1 prompt architecture: core principle, lesson atmosphere,
variant material philosophy (impasto prompts unchanged), artist aspects, hero
block, mask reference, structure, composition, painterly surface, master
integrity/philosophy.

v4 adds only a pigment-scale optical refinement layer and v4-specific negative
discipline. Output is separate from v3.

Reads:
  - kml/data/kanji/palettes/kml_master_visual_system.json
  - lesson_assignments_v2.json (repo root, or kml/lesson_assignments_v2.json)
  - kml/data/kanji/kanji_production.csv

Writes (default: kml/data/kanji/painterly_prompts_v4/):
  - prompts/lesson_XX/{slug}_{variant}_{lesson:02d}.txt
  - combined/all_prompts_combined.txt
  - metadata/painterly_prompts_v4_catalog.json
  - metadata/missing_masks_v4.txt
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
KML_DIR = SCRIPT_DIR.parent
REPO_ROOT = KML_DIR.parent

DEFAULT_MASTER_PATH = KML_DIR / "data" / "kanji" / "palettes" / "kml_master_visual_system.json"
DEFAULT_CSV_PATH = KML_DIR / "data" / "kanji" / "kanji_production.csv"
DEFAULT_OUTPUT_ROOT = KML_DIR / "data" / "kanji" / "painterly_prompts_v4"

PROMPT_VERSION = "v4.0"
BASELINE_VERSION = "v3.1"

STRUCTURE_RULES = """
Use the provided kanji mask image as the exact structural reference.

Even if the mask file is missing from disk, treat the mask as authoritative:
preserve mask fidelity and exact kanji geometry.

Do not alter, reinterpret, stylize, correct, or improve the kanji structure.

Preserve the original mask shape exactly.

No added strokes.
No removed strokes.
No merged strokes.
No disconnected fragments.
""".strip()

COMPOSITION_RULES = """
Square composition.
Centered composition.
Balanced margins.

The kanji and background must feel like one unified painting.

The background should support the kanji,
not compete with it.
""".strip()

PAINTERLY_SURFACE_RULES = """
Visible canvas weave / tooth should read subtly in both background and paint.

Subtle surface grain is desirable (not noise, not digital speckle).

Organic brush behavior: natural bristle breakup, controlled edge variation,
and believable paint-body physics.

Avoid sterile airbrushed blending; keep transitions painterly and tactile.
""".strip()

OPTICAL_REFINEMENT_V4 = """
## V4 OPTICAL REFINEMENT (pigment-scale; matte museum dominant)

This v4 layer is an optical refinement of the v3.1 prompt system, not a new aesthetic system.
Preserve the entire v3.1 structure, composition logic, palette behavior, mask fidelity,
and variant material philosophy (including all impasto / variant language above).

Add only these subtle optical/material cues (restrained, never spectacle):
- micro-reflective pigment variation (tiny grain-level events inside matte paint films)
- subtle semi-burnished ridge highlights along impasto ridges (dry, soft, not glossy)
- slight warm/cool internal pigment temperature variation within passages (not rainbow shifting)
- localized optical depth within darker paint regions (breathing depth, not crushed voids)
- uneven pigment absorption behavior (credible dry-ground tooth variation; canvas interaction)

Overall finish target:
- maintain an overall matte museum-quality finish at normal viewing distance.

These cues must not change kanji structure or edge discipline: they are film-level
and pigment-body behaviors only.
""".strip()

NEGATIVE_RULES_V3 = """
Avoid:
- logo rendering or brand-like lockups
- vector-flat fills or perfectly uniform edges
- 3D extrusion, bevels, embossing, or carved relief typography
- synthetic UI gloss / plastic sheen (unless the VARIANT explicitly calls for controlled reflective behavior)
- floating symbol feeling: the glyph must remain integrated into the painted field
- imitation of specific named artists or recognizable signature styles
""".strip()

NEGATIVE_RULES_V4_APPEND = """
Additional v4 optical discipline (matte museum dominant read):
- glossy varnish appearance, thick resin gloss, or piano-grade topcoat sheen
- wet high-gloss acrylic plastic skin or “wet look” cosmetic sheen
- exaggerated mirror-like reflections, lens-flare sparkle, or specular spectacle unrelated to the VARIANT definition
- broad metallic chrome / foil / CG-metal sheet treatments used as a global filter

Variant note (do not contradict v3.1 variant philosophy):
If the active VARIANT is reflective_black, oxidized_metal, or gold_leaf, interpret its cues
through dry oil-paint and mineral pigment physics with extremely restrained, localized optical
events—never decorative chrome, never global metallic photo textures, never exaggerated reflections.

Do not change kanji structure or edge discipline.
""".strip()


def _repo_paths_for_assignments() -> list[Path]:
    return [
        REPO_ROOT / "lesson_assignments_v2.json",
        KML_DIR / "lesson_assignments_v2.json",
    ]


def resolve_assignments_path(explicit: Path | None) -> Path:
    if explicit is not None:
        if not explicit.is_file():
            raise SystemExit(f"Missing assignments JSON: {explicit}")
        return explicit
    for p in _repo_paths_for_assignments():
        if p.is_file():
            return p
    raise SystemExit(
        "Could not find lesson_assignments_v2.json "
        f"(tried: {', '.join(str(p) for p in _repo_paths_for_assignments())})"
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_lesson_assignments(path: Path) -> dict[int, dict[str, Any]]:
    data = load_json(path)
    out: dict[int, dict[str, Any]] = {}
    for entry in data.get("lessons", []):
        out[int(entry["lesson"])] = entry
    return out


def build_aspect_lookup(master: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {a["id"]: a for a in master.get("artist_aspects", [])}


def build_variant_lookup(master: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {v["id"]: v for v in master.get("application_variants", [])}


def build_special_state_lookup(master: dict[str, Any]) -> dict[str, str]:
    return {s["id"]: s.get("meaning", "") for s in master.get("special_states", [])}


def resolve_mask_path(base_kanji_dir: Path, lesson: int, slug: str) -> tuple[Path | None, str]:
    candidates = [
        base_kanji_dir / "masks" / f"Lesson_{lesson:02d}" / f"{slug}.png",
        base_kanji_dir / "masks" / f"Lesson_{lesson:03d}" / f"{slug}.png",
        base_kanji_dir / "masks" / f"lesson_{lesson:02d}" / f"{slug}.png",
        base_kanji_dir / "masks" / f"{slug}.png",
    ]
    for p in candidates:
        if p.is_file():
            return p, str(p)
    preferred = base_kanji_dir / "masks" / f"Lesson_{lesson:02d}" / f"{slug}.png"
    return None, str(preferred)


def variant_section(variant_id: str, variant_lookup: dict[str, dict[str, Any]]) -> str:
    meta = variant_lookup.get(variant_id, {})
    rarity = meta.get("rarity", "")
    desc = meta.get("description", "")
    bullets = meta.get("surface_behavior", []) or []

    headers = {
        "full_impasto": "FULL IMPASTO",
        "substrate_overpaint": "SUBSTRATE OVERPAINT",
        "reflective_black": "REFLECTIVE BLACK",
        "oxidized_metal": "OXIDIZED METAL",
        "gold_leaf": "GOLD LEAF",
        "matte_mineral": "MATTE MINERAL",
        "ink_fragment": "INK FRAGMENT",
    }
    title = headers.get(variant_id, variant_id.upper().replace("_", " "))

    bullet_text = "\n".join(f"- {b}" for b in bullets) if bullets else "- (see master system description)"

    philosophy = {
        "full_impasto": """
Heavy integrated painterly material.
Dense paint interaction across the whole surface.
Stroke ridges and layered body should read as one continuous painting field.
""".strip(),
        "substrate_overpaint": """
Background is painted first as an impasto substrate field.
The kanji is painted afterward as a second intervention layer.
Keep visible substrate interaction: the glyph must feel embedded into prior paint,
not pasted as a separate graphic.
""".strip(),
        "reflective_black": """
Near-black reflective mineral paint system (not flat digital black).
Subtle warm/cool undertones and restrained highlight glints along ridges.
Maintain readability: reflectivity supports form, it does not replace structure.
""".strip(),
        "oxidized_metal": """
Aged metallic oxidation behavior with controlled corrosion patina.
Weathered mineral transitions and restrained color breakup in the metal skin.
Avoid sci-fi chrome; keep it grounded, tactile, and painterly.
""".strip(),
        "gold_leaf": """
Fragmented reflective leaf-like accents (selective, restrained).
Light-catching edges with sacred-object material feeling.
Never overly decorative; never full “bling” coverage; keep it integrated and rare.
""".strip(),
        "matte_mineral": """
Dry mineral paint surface with low specular response.
Quiet museum-wall tactility; powdery pigment feeling without chalky digital flattening.
""".strip(),
        "ink_fragment": """
Ink-like fragmentation at edges with painterly breakup.
Controlled dissolution and energy splatter that still respects the mask silhouette.
""".strip(),
    }.get(variant_id, "Material execution follows the master system variant definition.")

    return f"""
## {title}

Rarity class (for weighting / scheduling): {rarity or "unknown"}

Master description:
{desc or "(none)"}

Dedicated material philosophy:
{philosophy}

Surface behavior (from master system):
{bullet_text}
""".strip()


def artist_aspects_block(
    aspect_ids: list[str],
    aspect_lookup: dict[str, dict[str, Any]],
) -> str:
    lines: list[str] = []
    for aid in aspect_ids:
        a = aspect_lookup.get(aid, {})
        traits = a.get("traits", []) or []
        t = "\n".join(f"- {x}" for x in traits) if traits else "- (no traits listed)"
        lines.append(f"### {aid}\n{t}")
    return "\n\n".join(lines).strip()


def lesson_atmosphere_block(
    lesson_entry: dict[str, Any],
    special_lookup: dict[str, str],
) -> str:
    ss = str(lesson_entry.get("special_state") or "").strip()
    ss_line = ""
    if ss:
        meaning = special_lookup.get(ss, "")
        ss_line = f"special_state: {ss}\nmeaning: {meaning}".strip()

    return f"""
lesson_family: {lesson_entry.get("lesson_family", "")}

palette: {lesson_entry.get("palette", "")}
flow: {lesson_entry.get("flow", "")}
energy: {lesson_entry.get("energy", "")}

{ss_line}

assignment_notes:
{lesson_entry.get("notes", "")}
""".strip()


def hero_block(lesson_entry: dict[str, Any]) -> str:
    if not lesson_entry.get("hero_enabled"):
        return ""
    prob = lesson_entry.get("hero_probability", 0.0)
    hv = lesson_entry.get("hero_variants", [])
    return f"""
## HERO LESSON MODE (orchestration)

This lesson is hero-capable (scheduled rarity: hero_probability ≈ {prob}).

When hero treatment is selected for a kanji:
- increase material richness and surface complexity (still readable)
- allow stronger compositional drama in the field around the glyph
- deepen atmospheric sophistication (light behavior, depth, layering)
- do not distort kanji structure; do not break mask fidelity

Preferred hero material systems (if available for this lesson’s variant set):
{", ".join(str(x) for x in hv) if hv else "(none specified)"}
""".strip()


def build_prompt_text(
    *,
    kanji: str,
    slug: str,
    lesson: int,
    variant_id: str,
    mask_ref: str,
    mask_missing: bool,
    lesson_entry: dict[str, Any],
    master: dict[str, Any],
    variant_lookup: dict[str, dict[str, Any]],
    aspect_lookup: dict[str, dict[str, Any]],
    special_lookup: dict[str, str],
) -> str:
    aspects = [str(x) for x in (lesson_entry.get("artist_aspects") or [])]

    mask_status = "MISSING (still enforce geometry as if mask exists)" if mask_missing else "PRESENT"

    core_principle = master.get("core_principle", {})

    prompt = f"""
KML Painterly Prompt (schema {PROMPT_VERSION}; baseline {BASELINE_VERSION})

kanji: {kanji}
slug: {slug}
lesson: {lesson}
variant: {variant_id}

=====================================================
CORE PRINCIPLE (READ FIRST)
=====================================================

{json.dumps(core_principle, ensure_ascii=False, indent=2)}

=====================================================
LESSON ATMOSPHERE (NOT material execution)
=====================================================

{lesson_atmosphere_block(lesson_entry, special_lookup)}

=====================================================
MATERIAL EXECUTION VARIANT (FUNDAMENTAL SYSTEM)
=====================================================

{variant_section(variant_id, variant_lookup)}

=====================================================
ARTIST ASPECTS (SUBTLE ORCHESTRATION)
=====================================================

These aspects influence motion, edge handling, light behavior, and atmosphere.
They must not imitate specific artists.

{artist_aspects_block(aspects, aspect_lookup)}

{hero_block(lesson_entry)}

=====================================================
MASK REFERENCE
=====================================================

mask_path: {mask_ref}
mask_status: {mask_status}

=====================================================
KANJI GEOMETRY / STRUCTURE
=====================================================

{STRUCTURE_RULES}

=====================================================
COMPOSITION RULES
=====================================================

{COMPOSITION_RULES}

=====================================================
PAINTERLY SURFACE RULES
=====================================================

{PAINTERLY_SURFACE_RULES}

=====================================================
V4 OPTICAL REFINEMENT (ADDITIVE ONLY)
=====================================================

{OPTICAL_REFINEMENT_V4}

=====================================================
GLOBAL KANJI INTEGRITY (FROM MASTER SYSTEM)
=====================================================

{chr(10).join('- ' + x for x in master.get('global_rules', {}).get('kanji_integrity', []))}

=====================================================
NEGATIVE RULES
=====================================================

{NEGATIVE_RULES_V3}

{NEGATIVE_RULES_V4_APPEND}

=====================================================
SURFACE PHILOSOPHY (FROM MASTER SYSTEM)
=====================================================

{chr(10).join('- ' + x for x in master.get('global_rules', {}).get('surface_philosophy', []))}
""".strip()

    return prompt + "\n"


def md5_text(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def rel_to_repo(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(path.resolve())


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate KML painterly prompts v4 (v3.1 + optical refinement).")
    ap.add_argument("--master", type=Path, default=DEFAULT_MASTER_PATH)
    ap.add_argument("--assignments", type=Path, default=None, help="Path to lesson_assignments_v2.json")
    ap.add_argument("--csv", type=Path, dest="csv_path", default=DEFAULT_CSV_PATH)
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    ap.add_argument("--dry-run", action="store_true", help="Do not write files; print counts only")
    ap.add_argument("--limit-rows", type=int, default=0, help="Process only first N CSV rows (debug)")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    log = logging.getLogger("painterly_v4")

    master_path: Path = args.master
    csv_path: Path = args.csv_path
    output_root: Path = args.output_root

    if not master_path.is_file():
        log.error("Missing master visual system JSON: %s", master_path)
        return 2
    if not csv_path.is_file():
        log.error("Missing kanji_production.csv: %s", csv_path)
        return 2

    assign_path = resolve_assignments_path(args.assignments)
    master = load_json(master_path)
    lessons = load_lesson_assignments(assign_path)
    variant_lookup = build_variant_lookup(master)
    aspect_lookup = build_aspect_lookup(master)
    special_lookup = build_special_state_lookup(master)

    base_kanji_dir = csv_path.parent

    prompts_root = output_root / "prompts"
    combined_dir = output_root / "combined"
    meta_dir = output_root / "metadata"

    if not args.dry_run:
        prompts_root.mkdir(parents=True, exist_ok=True)
        combined_dir.mkdir(parents=True, exist_ok=True)
        meta_dir.mkdir(parents=True, exist_ok=True)

    combined_path = combined_dir / "all_prompts_combined.txt"
    catalog_path = meta_dir / "painterly_prompts_v4_catalog.json"

    missing_masks: list[str] = []
    catalog: list[dict[str, Any]] = []

    total_rows = 0
    total_prompts = 0

    combined_f = None
    if not args.dry_run:
        combined_f = combined_path.open("w", encoding="utf-8")

    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if args.limit_rows and total_rows >= args.limit_rows:
                    break
                total_rows += 1

                kanji = (row.get("kanji") or "").strip()
                slug = (row.get("slug") or "").strip()
                lesson = int(row.get("lesson_number") or 0)
                if not kanji or not slug or lesson <= 0:
                    log.warning("Skipping malformed row #%s: %r", total_rows, row)
                    continue

                if lesson not in lessons:
                    log.warning("Skipping row: unknown lesson %s (%s)", lesson, slug)
                    continue

                le = lessons[lesson]
                variants = [str(v) for v in (le.get("allowed_variants") or [])]
                if not variants:
                    log.warning("Lesson %s has no allowed_variants; skipping %s", lesson, slug)
                    continue

                mask_path, mask_ref = resolve_mask_path(base_kanji_dir, lesson, slug)
                mask_missing = mask_path is None
                if mask_missing:
                    missing_masks.append(mask_ref)

                for variant_id in variants:
                    total_prompts += 1
                    prompt_text = build_prompt_text(
                        kanji=kanji,
                        slug=slug,
                        lesson=lesson,
                        variant_id=variant_id,
                        mask_ref=mask_ref,
                        mask_missing=bool(mask_missing),
                        lesson_entry=le,
                        master=master,
                        variant_lookup=variant_lookup,
                        aspect_lookup=aspect_lookup,
                        special_lookup=special_lookup,
                    )

                    lesson_dir = prompts_root / f"lesson_{lesson:02d}"
                    filename = f"{slug}_{variant_id}_{lesson:02d}.txt"
                    rel_prompt = str(Path("prompts") / f"lesson_{lesson:02d}" / filename)

                    if not args.dry_run:
                        lesson_dir.mkdir(parents=True, exist_ok=True)
                        out_path = lesson_dir / filename
                        out_path.write_text(prompt_text, encoding="utf-8")

                        assert combined_f is not None
                        combined_f.write(
                            "\n".join(
                                [
                                    "==================================================",
                                    f"KANJI: {kanji}",
                                    f"SLUG: {slug}",
                                    f"LESSON: {lesson}",
                                    f"VARIANT: {variant_id}",
                                    f"PROMPT_VERSION: {PROMPT_VERSION}",
                                    "==================================================",
                                    "",
                                    prompt_text.strip(),
                                    "",
                                ]
                            )
                        )

                    catalog.append(
                        {
                            "kanji": kanji,
                            "slug": slug,
                            "lesson": lesson,
                            "variant": variant_id,
                            "palette": le.get("palette", ""),
                            "flow": le.get("flow", ""),
                            "energy": le.get("energy", ""),
                            "artist_aspects": le.get("artist_aspects", []),
                            "hero_enabled": bool(le.get("hero_enabled", False)),
                            "mask_missing": bool(mask_missing),
                            "mask_path_expected": mask_ref,
                            "prompt_relative": rel_prompt,
                            "prompt_version": PROMPT_VERSION,
                            "baseline_version": BASELINE_VERSION,
                            "prompt_md5": md5_text(prompt_text),
                        }
                    )
    finally:
        if combined_f is not None:
            combined_f.close()

    if not args.dry_run:
        catalog_doc = {
            "schema_version": "4.0",
            "prompt_version": PROMPT_VERSION,
            "baseline_version": BASELINE_VERSION,
            "sources": {
                "kml_master_visual_system": rel_to_repo(master_path),
                "lesson_assignments_v2": rel_to_repo(assign_path),
                "kanji_production_csv": rel_to_repo(csv_path),
            },
            "output_root": rel_to_repo(output_root),
            "counts": {
                "csv_rows_seen": total_rows,
                "prompts_written": total_prompts,
                "missing_masks_logged": len(missing_masks),
            },
            "entries": catalog,
        }
        catalog_path.write_text(json.dumps(catalog_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        missing_path = meta_dir / "missing_masks_v4.txt"
        uniq_missing = sorted(dict.fromkeys(missing_masks))
        missing_path.write_text("\n".join(uniq_missing) + ("\n" if uniq_missing else ""), encoding="utf-8")

    log.info("CSV rows processed: %s", total_rows)
    log.info("Prompts: %s", total_prompts)
    log.info("Missing mask paths (unique): %s", len(set(missing_masks)))
    if missing_masks:
        uniq = list(dict.fromkeys(missing_masks))
        for p in uniq[:30]:
            log.warning("Missing mask: %s", p)
        if len(uniq) > 30:
            log.warning("... %s more missing mask paths", len(uniq) - 30)

    if args.dry_run:
        log.info("Dry run: no files written")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
