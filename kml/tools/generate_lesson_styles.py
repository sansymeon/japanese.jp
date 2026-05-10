#!/usr/bin/env python3
"""
Regenerate kml/config/lesson_styles.json (canonical path for prompt tooling).

Vocabulary:
  - palettes, flows, energy: kml/tools/palette.json
  - modes: keys of STYLE_PROFILES in generate_image_prompts.py
  - surfaces: keys of SURFACE_PROFILES in generate_image_prompts.py
  - paint_density: production default used in kanji metadata (single value)

Selection uses a fixed RNG seed for reproducible output, weighted picks
within each family (no strict modulo rotation), occasional repeated flows,
anti-clustering for dramatic palettes, and rare optional special_state ids.

Run from repo root:
  python3 kml/tools/generate_lesson_styles.py
  python3 kml/tools/generate_lesson_styles.py --write-audit
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from random import Random

TOOLS_DIR = Path(__file__).resolve().parent
PALETTE_JSON = TOOLS_DIR / "palette.json"
DEFAULT_OUTPUT = TOOLS_DIR.parent / "config" / "lesson_styles.json"
DEFAULT_AUDIT = TOOLS_DIR.parent / "data" / "kanji" / "palettes" / "lesson_visual_audit.txt"

LESSON_COUNT = 153

# Reproducible sequence; change only when intentionally reshuffling the book.
STYLE_SEED = 0x4B4D4C01  # KML + version nibble

# Must match STYLE_PROFILES in kml/tools/generate_image_prompts.py
MODES = ("standard", "motion", "contained", "hero", "fast")

# Must match SURFACE_PROFILES in kml/tools/generate_image_prompts.py
SURFACES = ("clean", "painterly", "raw", "museum")

PAINT_DENSITY = "medium impasto"

# Heavier palettes: space them apart so the book never feels “all charcoal.”
DRAMATIC_PALETTES = frozenset(
    {
        "charcoal black and ember red",
        "smoky violet and oxidized copper",
    }
)

CALM_PALETTES = frozenset(
    {
        "warm red and orange with ivory strokes",
        "earth umber and parchment cream",
        "cold blue-grey with pale ivory",
        "turquoise and weathered gold",
    }
)

# Sparse, human-facing markers (not prompt vocabulary). Omitted on most lessons.
SPECIAL_STATES: dict[int, str] = {
    23: "still_point",
    41: "threshold",
    56: "open_sky",
    71: "ember_surge",
    86: "threshold",
    101: "still_point",
    116: "brightening",
    133: "afterglow",
}

# Thirteen bands: twelve lessons each, except the last band (145–153) has nine.
FAMILIES: tuple[dict, ...] = (
    {
        "id": "warm_foundational",
        "lesson_start": 1,
        "lesson_end": 12,
        "title": "Warm foundational family",
        "notes": "Warm, simple, inviting impasto language; ivory-friendly light.",
        "palette_prefs": (
            "warm red and orange with ivory strokes",
            "earth umber and parchment cream",
            "turquoise and weathered gold",
            "moss green and aged bronze",
            "deep indigo and muted gold with cool ivory strokes",
            "cold blue-grey with pale ivory",
        ),
    },
    {
        "id": "earth_organic",
        "lesson_start": 13,
        "lesson_end": 24,
        "title": "Earth / organic family",
        "notes": "Grounded mineral greens and umber; tactile, slow growth.",
        "palette_prefs": (
            "earth umber and parchment cream",
            "moss green and aged bronze",
            "turquoise and weathered gold",
            "warm red and orange with ivory strokes",
            "smoky violet and oxidized copper",
            "deep indigo and muted gold with cool ivory strokes",
        ),
    },
    {
        "id": "cool_contemplative",
        "lesson_start": 25,
        "lesson_end": 36,
        "title": "Cool contemplative family",
        "notes": "Restrained cool greys and indigo; spacious, inward-looking.",
        "palette_prefs": (
            "cold blue-grey with pale ivory",
            "deep indigo and muted gold with cool ivory strokes",
            "smoky violet and oxidized copper",
            "turquoise and weathered gold",
            "moss green and aged bronze",
            "charcoal black and ember red",
        ),
    },
    {
        "id": "dramatic_high_contrast",
        "lesson_start": 37,
        "lesson_end": 48,
        "title": "Dramatic high-contrast family",
        "notes": "Deep value range; ember accents against charcoal and violet.",
        "palette_prefs": (
            "charcoal black and ember red",
            "smoky violet and oxidized copper",
            "deep indigo and muted gold with cool ivory strokes",
            "cold blue-grey with pale ivory",
            "warm red and orange with ivory strokes",
            "turquoise and weathered gold",
        ),
    },
    {
        "id": "luminous_depth",
        "lesson_start": 49,
        "lesson_end": 60,
        "title": "Luminous depth family",
        "notes": "Jewel-like turquoise and gold against cool depths.",
        "palette_prefs": (
            "turquoise and weathered gold",
            "deep indigo and muted gold with cool ivory strokes",
            "cold blue-grey with pale ivory",
            "moss green and aged bronze",
            "smoky violet and oxidized copper",
            "warm red and orange with ivory strokes",
        ),
    },
    {
        "id": "twilight_atmosphere",
        "lesson_start": 61,
        "lesson_end": 72,
        "title": "Twilight atmosphere family",
        "notes": "Violet–copper oxidation; turbulent but controlled skies.",
        "palette_prefs": (
            "smoky violet and oxidized copper",
            "cold blue-grey with pale ivory",
            "deep indigo and muted gold with cool ivory strokes",
            "charcoal black and ember red",
            "moss green and aged bronze",
            "earth umber and parchment cream",
        ),
    },
    {
        "id": "tempered_warmth",
        "lesson_start": 73,
        "lesson_end": 84,
        "title": "Tempered warmth family",
        "notes": "Return to warmth with matured contrast and earth anchors.",
        "palette_prefs": (
            "warm red and orange with ivory strokes",
            "earth umber and parchment cream",
            "deep indigo and muted gold with cool ivory strokes",
            "turquoise and weathered gold",
            "moss green and aged bronze",
            "charcoal black and ember red",
        ),
    },
    {
        "id": "shadow_earth",
        "lesson_start": 85,
        "lesson_end": 96,
        "title": "Shadow earth family",
        "notes": "Darker atmospheric middle; umber and charcoal as pressure.",
        "palette_prefs": (
            "charcoal black and ember red",
            "earth umber and parchment cream",
            "moss green and aged bronze",
            "smoky violet and oxidized copper",
            "cold blue-grey with pale ivory",
            "deep indigo and muted gold with cool ivory strokes",
        ),
    },
    {
        "id": "mist_cool",
        "lesson_start": 97,
        "lesson_end": 108,
        "title": "Mist cool family",
        "notes": "Pale cool ivory fog; subtle movement and reduced saturation feel.",
        "palette_prefs": (
            "cold blue-grey with pale ivory",
            "turquoise and weathered gold",
            "deep indigo and muted gold with cool ivory strokes",
            "moss green and aged bronze",
            "smoky violet and oxidized copper",
            "warm red and orange with ivory strokes",
        ),
    },
    {
        "id": "voltaic_contrast",
        "lesson_start": 109,
        "lesson_end": 120,
        "title": "Voltaic contrast family",
        "notes": "Advanced sparks: ember, turquoise, and violet in sharp dialogue.",
        "palette_prefs": (
            "turquoise and weathered gold",
            "charcoal black and ember red",
            "warm red and orange with ivory strokes",
            "smoky violet and oxidized copper",
            "deep indigo and muted gold with cool ivory strokes",
            "cold blue-grey with pale ivory",
        ),
    },
    {
        "id": "polychrome_synthesis",
        "lesson_start": 121,
        "lesson_end": 132,
        "title": "Polychrome synthesis family",
        "notes": "Long-form richness: rotate full vocabulary with disciplined cadence.",
        "palette_prefs": None,
    },
    {
        "id": "mastery_return",
        "lesson_start": 133,
        "lesson_end": 144,
        "title": "Mastery return family",
        "notes": "Cohesive KML identity: museum poise with painterly warmth echoes.",
        "palette_prefs": (
            "deep indigo and muted gold with cool ivory strokes",
            "warm red and orange with ivory strokes",
            "earth umber and parchment cream",
            "smoky violet and oxidized copper",
            "turquoise and weathered gold",
            "charcoal black and ember red",
            "cold blue-grey with pale ivory",
            "moss green and aged bronze",
        ),
    },
    {
        "id": "coda_coherent",
        "lesson_start": 145,
        "lesson_end": 153,
        "title": "Coda coherent family",
        "notes": "Closing arc: converge on signature warmth–indigo–ivory harmony.",
        "palette_prefs": (
            "warm red and orange with ivory strokes",
            "deep indigo and muted gold with cool ivory strokes",
            "earth umber and parchment cream",
            "cold blue-grey with pale ivory",
            "turquoise and weathered gold",
            "moss green and aged bronze",
        ),
    },
)


def load_palette_vocab(path: Path) -> tuple[list[str], list[str], list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    palettes = data["palettes"]
    flows = data["flows"]
    energy = data["energy"]
    for name, seq in (("palettes", palettes), ("flows", flows), ("energy", energy)):
        if len(set(seq)) != len(seq):
            raise ValueError(f"palette.json {name} contains duplicates")
    return palettes, flows, energy


def family_for_lesson(n: int) -> dict:
    for fam in FAMILIES:
        if fam["lesson_start"] <= n <= fam["lesson_end"]:
            return fam
    raise ValueError(f"no family for lesson {n}")


def lesson_rng(seed: int, lesson: int) -> Random:
    """Per-lesson RNG: distinct streams without simple modulo repetition."""
    mixed = (seed ^ (lesson * 0x9E3779B9)) & 0xFFFFFFFF
    return Random(mixed)


def weighted_choice(rng: Random, items: tuple[str, ...], weights: list[float]) -> str:
    return rng.choices(items, weights=weights, k=1)[0]


def irrational_phase(lesson: int, salt: float) -> float:
    """0..1 aperiodic bias (not lesson % k)."""
    return (lesson * math.sqrt(2) + salt * math.pi) % 1.0


def pick_palette(
    lesson: int,
    last_two: list[str],
    fam: dict,
    pal_t: tuple[str, ...],
    rng: Random,
) -> str:
    prefs = fam["palette_prefs"]
    ordered = prefs if prefs is not None else pal_t
    candidates = [p for p in ordered if p not in last_two]
    if not candidates:
        candidates = [p for p in pal_t if p not in last_two]
    if not candidates:
        raise RuntimeError("cannot satisfy palette window")

    dramatic_in_window = sum(1 for p in last_two if p in DRAMATIC_PALETTES)
    t = irrational_phase(lesson, 0.31)

    weights: list[float] = []
    for p in candidates:
        w = 0.55 + 0.9 * rng.random()

        if prefs is not None and p in prefs:
            try:
                rank = prefs.index(p)
            except ValueError:
                rank = len(prefs)
            w *= 1.22 - min(rank, 5) * 0.07

        if lesson <= 20:
            if p in CALM_PALETTES:
                w *= 1.65 + 0.35 * t
            if p in DRAMATIC_PALETTES:
                w *= 0.22
        elif lesson <= 48:
            if p in DRAMATIC_PALETTES:
                w *= 0.85 + 0.45 * t
            else:
                w *= 0.92 + 0.2 * rng.random()
        elif 133 <= lesson <= 153 and fam["id"] in ("mastery_return", "coda_coherent"):
            prefs_m = fam["palette_prefs"]
            if prefs_m is not None and p in prefs_m:
                r = prefs_m.index(p)
                w *= 1.16 - min(r, 6) * 0.048
            if p in DRAMATIC_PALETTES:
                w *= 0.55 + 0.25 * rng.random()

        if dramatic_in_window >= 2 and p in DRAMATIC_PALETTES:
            w *= 0.1
        elif dramatic_in_window == 1 and p in DRAMATIC_PALETTES:
            w *= 0.45 + 0.35 * rng.random()

        weights.append(max(w, 1e-6))

    return weighted_choice(rng, tuple(candidates), weights)


def pick_flow(
    lesson: int,
    flows: tuple[str, ...],
    rng: Random,
    last_flow: str | None,
) -> str:
    if last_flow is not None and rng.random() < 0.14:
        return last_flow

    phase = irrational_phase(lesson, 0.73)
    weights = []
    for f in flows:
        w = 0.5 + phase * 0.4 + 0.85 * rng.random()
        if last_flow is not None and f == last_flow:
            w *= 0.1
        weights.append(w)
    return weighted_choice(rng, flows, weights)


def pick_energy(lesson: int, energy_opts: tuple[str, ...], rng: Random) -> str:
    u = irrational_phase(lesson, 0.11)
    if lesson <= 24:
        base = {
            "quiet": 1.55,
            "meditative": 1.45,
            "balanced": 1.1,
            "subtle movement": 1.05,
            "controlled tension": 0.35 + 0.25 * u,
        }
    elif lesson <= 72:
        base = {
            "balanced": 1.2,
            "quiet": 1.05,
            "meditative": 1.1,
            "controlled tension": 0.75 + 0.5 * u,
            "subtle movement": 0.85,
        }
    elif lesson <= 120:
        base = {
            "controlled tension": 1.15 + 0.35 * u,
            "balanced": 1.0,
            "subtle movement": 1.0,
            "meditative": 0.85,
            "quiet": 0.65,
        }
    else:
        base = {
            "controlled tension": 1.05,
            "balanced": 1.0,
            "subtle movement": 1.0,
            "quiet": 0.9,
            "meditative": 0.95,
        }

    weights = [max(base.get(e, 0.4), 0.05) * (0.75 + 0.55 * rng.random()) for e in energy_opts]
    return weighted_choice(rng, energy_opts, weights)


def pick_mode(lesson: int, rng: Random) -> str:
    u = irrational_phase(lesson, 0.57)
    if lesson <= 24:
        base = {"standard": 1.5, "contained": 1.45, "hero": 0.55 + 0.25 * u, "motion": 0.35, "fast": 0.2}
    elif lesson <= 96:
        base = {
            "contained": 1.25,
            "standard": 1.15,
            "motion": 0.85 + 0.35 * u,
            "hero": 0.75,
            "fast": 0.45,
        }
    elif lesson <= 132:
        base = {
            "hero": 1.05,
            "motion": 1.0,
            "fast": 0.85,
            "contained": 0.95,
            "standard": 0.75,
        }
    else:
        base = {
            "contained": 1.35,
            "standard": 1.15,
            "hero": 0.95 + 0.2 * u,
            "motion": 0.55,
            "fast": 0.45,
        }

    weights = [max(base[m], 0.05) * (0.7 + 0.65 * rng.random()) for m in MODES]
    return weighted_choice(rng, MODES, weights)


def pick_surface(lesson: int, rng: Random) -> str:
    u = irrational_phase(lesson, 0.19)
    if lesson <= 24:
        base = {"clean": 1.55, "museum": 1.05, "painterly": 0.75 + 0.2 * u, "raw": 0.18}
    elif lesson <= 96:
        base = {
            "painterly": 1.15,
            "clean": 1.0,
            "museum": 1.05,
            "raw": 0.55 + 0.35 * u,
        }
    else:
        base = {
            "museum": 1.15,
            "painterly": 1.05,
            "clean": 0.95,
            "raw": 0.75 + 0.25 * u,
        }

    weights = [max(base[s], 0.05) * (0.72 + 0.6 * rng.random()) for s in SURFACES]
    return weighted_choice(rng, SURFACES, weights)


def apply_special_state_nudge(
    lesson: int,
    special: str | None,
    energy: str,
    mode: str,
    surface: str,
    rng: Random,
) -> tuple[str, str, str]:
    if special is None:
        return energy, mode, surface

    if special == "still_point":
        energy = weighted_choice(
            rng,
            ("quiet", "meditative", "balanced"),
            [1.4, 1.35, 0.75],
        )
        mode = weighted_choice(rng, ("contained", "standard"), [1.3, 1.0])
        surface = weighted_choice(rng, ("clean", "museum"), [1.1, 1.0])
    elif special == "threshold":
        energy = weighted_choice(
            rng,
            ("controlled tension", "balanced", "subtle movement"),
            [1.2, 1.0, 0.9],
        )
        mode = weighted_choice(rng, ("motion", "hero", "standard"), [1.0, 0.85, 0.8])
        surface = weighted_choice(rng, ("painterly", "museum", "raw"), [1.0, 0.95, 0.55])
    elif special == "open_sky":
        energy = weighted_choice(
            rng,
            ("subtle movement", "balanced", "quiet"),
            [1.15, 1.05, 0.95],
        )
        mode = weighted_choice(rng, ("standard", "motion", "contained"), [1.1, 0.95, 0.9])
        surface = weighted_choice(rng, ("clean", "museum", "painterly"), [1.2, 1.0, 0.85])
    elif special == "ember_surge":
        energy = weighted_choice(
            rng,
            ("controlled tension", "subtle movement", "balanced"),
            [1.35, 1.0, 0.75],
        )
        mode = weighted_choice(rng, ("hero", "motion", "fast"), [1.2, 1.0, 0.65])
        surface = weighted_choice(rng, ("raw", "painterly", "museum"), [1.05, 1.0, 0.85])
    elif special == "brightening":
        energy = weighted_choice(
            rng,
            ("balanced", "quiet", "meditative"),
            [1.2, 1.05, 1.0],
        )
        mode = weighted_choice(rng, ("standard", "hero", "contained"), [1.1, 0.95, 0.9])
        surface = weighted_choice(rng, ("museum", "clean", "painterly"), [1.15, 1.05, 0.9])
    elif special == "afterglow":
        energy = weighted_choice(
            rng,
            ("meditative", "quiet", "balanced"),
            [1.35, 1.2, 1.0],
        )
        mode = weighted_choice(rng, ("contained", "standard", "hero"), [1.25, 1.1, 0.75])
        surface = weighted_choice(rng, ("museum", "clean", "painterly"), [1.2, 1.0, 0.95])

    return energy, mode, surface


def build_document(palettes: list[str], flows: list[str], energy: list[str]) -> dict:
    pal_t = tuple(palettes)
    flow_t = tuple(flows)
    energy_t = tuple(energy)

    for label, seq in (
        ("palettes", pal_t),
        ("flows", flow_t),
        ("energy", energy_t),
    ):
        if len(set(seq)) != len(seq):
            raise ValueError(f"duplicate entries in palette.json {label}")

    for fam in FAMILIES:
        prefs = fam["palette_prefs"]
        if prefs is not None:
            for p in prefs:
                if p not in pal_t:
                    raise ValueError(
                        f"family {fam['id']} references unknown palette: {p!r}"
                    )

    lessons: list[dict] = []
    last_two: list[str] = []
    last_flow: str | None = None

    for n in range(1, LESSON_COUNT + 1):
        fam = family_for_lesson(n)
        rng = lesson_rng(STYLE_SEED, n)

        pal = pick_palette(n, last_two, fam, pal_t, rng)
        last_two.append(pal)
        if len(last_two) > 2:
            last_two.pop(0)

        fl = pick_flow(n, flow_t, rng, last_flow)
        last_flow = fl

        en = pick_energy(n, energy_t, rng)
        md = pick_mode(n, rng)
        sf = pick_surface(n, rng)

        special = SPECIAL_STATES.get(n)
        en, md, sf = apply_special_state_nudge(n, special, en, md, sf, rng)

        row: dict = {
            "lesson": n,
            "family": fam["id"],
            "family_title": fam["title"],
            "palette": pal,
            "flow": fl,
            "energy": en,
            "mode": md,
            "surface": sf,
            "paint_density": PAINT_DENSITY,
        }
        if special is not None:
            row["special_state"] = special
        lessons.append(row)

    for i, L in enumerate(lessons):
        pal = L["palette"]
        if i >= 1 and pal == lessons[i - 1]["palette"]:
            raise AssertionError(f"adjacent duplicate palette at lesson {L['lesson']}")
        if i >= 2 and pal == lessons[i - 2]["palette"]:
            raise AssertionError(
                f"palette repeats within 3 lessons at lesson {L['lesson']}"
            )

    return {
        "schema_version": "1.1",
        "description": (
            "Per-lesson visual style defaults for KML book generation. "
            "Palettes, flows, and energy use only kml/tools/palette.json. "
            "Modes use STYLE_PROFILES keys; surfaces use SURFACE_PROFILES keys "
            "from kml/tools/generate_image_prompts.py. paint_density matches "
            "production default. Lessons are assigned with weighted variation "
            "(fixed seed) plus rare optional special_state markers."
        ),
        "vocabulary": {
            "palettes": palettes,
            "flows": flows,
            "energy": energy,
            "modes": list(MODES),
            "surfaces": list(SURFACES),
            "paint_densities": [PAINT_DENSITY],
        },
        "families": [
            {
                "id": f["id"],
                "lesson_start": f["lesson_start"],
                "lesson_end": f["lesson_end"],
                "title": f["title"],
                "notes": f["notes"],
            }
            for f in FAMILIES
        ],
        "lessons": lessons,
    }


def validate_lessons(doc: dict) -> None:
    v = doc["vocabulary"]
    for L in doc["lessons"]:
        assert L["palette"] in v["palettes"]
        assert L["flow"] in v["flows"]
        assert L["energy"] in v["energy"]
        assert L["mode"] in v["modes"]
        assert L["surface"] in v["surfaces"]
        assert L["paint_density"] in v["paint_densities"]
        if "special_state" in L:
            assert isinstance(L["special_state"], str) and L["special_state"]


def write_audit(doc: dict, path: Path) -> None:
    lines: list[str] = []
    for L in doc["lessons"]:
        n = L["lesson"]
        lines.append(f"{n:03d} {L['family']}")
        if "special_state" in L:
            lines.append(f"special: {L['special_state']}")
        lines.append(f"palette: {L['palette']}")
        lines.append(f"flow: {L['flow']}")
        lines.append(f"energy: {L['energy']}")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"path to lesson_styles.json (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--palette-json",
        type=Path,
        default=PALETTE_JSON,
        help=f"path to palette.json (default: {PALETTE_JSON})",
    )
    parser.add_argument(
        "--write-audit",
        action="store_true",
        help=f"also write {DEFAULT_AUDIT.name} next to lesson_styles.json",
    )
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=DEFAULT_AUDIT,
        help="path for lesson visual audit txt",
    )
    args = parser.parse_args()

    palettes, flows, energy = load_palette_vocab(args.palette_json)
    doc = build_document(palettes, flows, energy)
    validate_lessons(doc)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output} ({len(doc['lessons'])} lessons)")

    if args.write_audit:
        write_audit(doc, args.audit_output)
        print(f"Wrote {args.audit_output}")


if __name__ == "__main__":
    main()
