#!/usr/bin/env python3
"""
Experimental Lesson image generation using lesson_visual_styles_v1.json.

Generates cinematic study-style images (evaluation run only — separate output folder).
Does not modify existing production assets.
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import textwrap
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STYLES_PATH = REPO_ROOT / "lesson_visual_styles_v1.json"
KANJI_CSV = REPO_ROOT / "kml" / "data" / "kanji" / "kanji_production.csv"
DEFAULT_OUT = REPO_ROOT / "assets" / "images" / "lesson_01_kml_v1_test"

# Extended style execution profiles (derived from lesson_visual_styles_v1 vocabulary
# + family_defaults + KML ambient study conventions).
STYLE_PROFILES: dict[str, dict[str, str]] = {
    "KML-WASH": {
        "composition": "single focal subject, generous negative space, mobile-safe center weight",
        "lighting": "soft dawn sidelight, low contrast, pale luminous haze",
        "atmosphere": "quiet foundational stillness, gentle invitation",
        "human_presence": "none unless keyword requires; if present, small in frame with visible face",
        "symbolic_treatment": "abstract forms, lines, openings, elemental symbols over literal illustration",
        "image_distance": "medium; numbers and primitives favor close symbolic framing",
        "surface": "watercolor wash, soft paper grain, restrained brush edges",
        "noir_alignment": "muted shadows, no crushed blacks, contemplative rather than thriller",
    },
    "KML-GLOW": {
        "composition": "radiant center-weighted glow, paired light sources allowed",
        "lighting": "internal luminosity, jewel-like highlights, soft bloom",
        "atmosphere": "radiant clarity, paired brilliance, ceremonial warmth",
        "human_presence": "optional silhouette with face visible when human theme",
        "symbolic_treatment": "light itself carries meaning; dual sources for paired concepts",
        "image_distance": "medium-wide to showcase light interaction",
        "surface": "luminous atmospheric depth, subtle particulate in air",
        "noir_alignment": "high contrast through light not violence; cinematic not stock",
    },
    "KML-CINE": {
        "composition": "dynamic diagonal energy, cinematic depth, strong foreground-background layers",
        "lighting": "directional key light, sharp rim, controlled shadow pools",
        "atmosphere": "charged moment before action, tension without chaos",
        "human_presence": "human figure encouraged when relevant; face clearly visible",
        "symbolic_treatment": "decisive gesture, threshold crossing, step-forward symbolism",
        "image_distance": "medium-wide action framing",
        "surface": "filmic color grade, rich midtones, atmospheric depth",
        "noir_alignment": "KML-NOIR pressure and consequence without genre cliché",
    },
}

# Per-keyword scene briefs for Lesson 1 (symbolic, cinematic, keyword-readable).
SCENE_BRIEFS: dict[str, str] = {
    "one": "A single vertical reed or brushstroke mark standing alone in pale dawn mist over still water — the idea of oneness before multiplication.",
    "two": "Two parallel stones or two matched lanterns on a quiet path with soft space between them — companionship of equals, not yet a crowd.",
    "three": "Three crane silhouettes or three aligned torii posts receding into soft grey-blue dawn — calm arrival of pattern.",
    "four": "A square garden frame or four-cornered courtyard seen from above, enclosed but peaceful — structure emerging from openness.",
    "five": "A balanced cross of paths in a misty field with faint ochre grass — almost symmetry with one subtle asymmetry.",
    "six": "Six-fold natural symmetry: honeycomb light on water or six petals in a shallow bowl — quiet order in nature.",
    "seven": "A bent branch or turning mountain path under early light — one stroke that changes direction with intent.",
    "eight": "Two paths diverging from a central fork in damp earth, wide atmospheric perspective — opening rather than closing.",
    "nine": "A nearly complete circle of stones or ripples one segment short of closure — fullness approaching completion.",
    "ten": "A crossroads marked by worn stone under dawn sky, complete and grounded — the hand closes, the world holds.",
    "mouth": "A cave mouth or canyon opening in soft ivory cliff face, breath-like mist flowing outward — threshold of speech.",
    "sun": "Low sun breaking through horizontal cloud bands over a wide field, warm ochre rim on cool grey-blue air.",
    "moon": "Thin crescent moon reflected in a still rice paddy at twilight, vast quiet sky.",
    "field": "Wide terraced fields in pale dawn wash, geometric yet organic, human scale absent.",
    "eye": "A reflective pool mirroring sky like an watching eye; optional distant figure with visible face at shore, not portrait.",
    "old": "A gnarled cedar or weathered gate post, time made visible in bark and moss — endurance not decay.",
    "I": "A solitary traveler from behind then slight turn showing face, standing at the edge of a wide misty field — selfhood as witness.",
    "risk": "A single foot hovering over a narrow stone step above dark water, body tense but controlled — one step forward.",
    "companion": "Two travelers walking side by side on a forest path, both faces visible in soft profile, equal stature.",
    "bright": "Sun and moon light meeting across a river gorge, dual radiance on water and trees — paired brilliance, lesson climax.",
}


@dataclass
class KanjiEntry:
    slug: str
    kanji: str
    keyword: str
    en_verse: str = ""


@dataclass
class GenerationPlan:
    slug: str
    kanji: str
    keyword: str
    style: str
    is_accent: bool
    accent_reason: str = ""
    palette: str = ""
    emotional_tone: str = ""
    lesson_family: str = ""
    profile: dict[str, str] = field(default_factory=dict)
    scene_brief: str = ""
    image_distance: str = ""
    prompt: str = ""
    output_path: Path | None = None


def load_lesson_styles(path: Path, lesson: int) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for entry in data["lessons"]:
        if entry["lesson"] == lesson:
            return entry
    raise ValueError(f"Lesson {lesson} not found in {path}")


def load_kanji_for_lesson(csv_path: Path, lesson: int) -> dict[str, KanjiEntry]:
    out: dict[str, KanjiEntry] = {}
    with csv_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if int(row.get("lesson_number") or 0) != lesson:
                continue
            slug = row["slug"]
            out[slug] = KanjiEntry(
                slug=slug,
                kanji=row["kanji"],
                keyword=row.get("keyword") or row.get("display_keyword") or slug,
                en_verse=(row.get("en_verse") or "").replace("\\n", " ").strip(),
            )
    return out


def resolve_style(slug: str, lesson_cfg: dict) -> tuple[str, bool, str]:
    dominant = lesson_cfg["dominant_style"]
    for accent in lesson_cfg.get("accent_kanji") or []:
        if accent["slug"] == slug:
            return accent["style"], True, accent.get("reason", "accent kanji")
    return dominant, False, ""


def pick_image_distance(slug: str, profile: dict[str, str], is_accent: bool) -> str:
    if slug in {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"}:
        return "close-to-medium symbolic"
    if slug in {"sun", "moon", "field", "bright"}:
        return "wide atmospheric"
    if slug in {"I", "companion", "risk"}:
        return "medium-wide cinematic"
    if is_accent:
        return profile.get("image_distance", "medium")
    return profile.get("image_distance", "medium")


def build_prompt(plan: GenerationPlan) -> str:
    p = plan.profile
    accent_note = (
        f"Accent treatment: {plan.accent_reason}. "
        if plan.is_accent
        else "Dominant lesson style treatment. "
    )
    return textwrap.dedent(
        f"""
        Cinematic fine-art still for Japanese kanji study ambient video. Keyword concept: {plan.keyword} ({plan.kanji}).

        Scene: {plan.scene_brief}

        Art direction system: lesson_visual_styles_v1
        Style family: {plan.style}
        Lesson palette: {plan.palette}
        Emotional tone: {plan.emotional_tone}
        {accent_note}

        Composition: {p.get('composition', '')}
        Lighting: {p.get('lighting', '')}
        Atmosphere: {p.get('atmosphere', '')}
        Human presence: {p.get('human_presence', '')}
        Symbolic treatment: {p.get('symbolic_treatment', '')}
        Camera distance: {plan.image_distance}
        Surface/texture: {p.get('surface', '')}

        KML-NOIR alignment: {p.get('noir_alignment', '')}
        Lesson family mood: {plan.lesson_family}, quiet dawn of literacy, foundational imagery.

        Requirements:
        - 16:9 cinematic framing, exhibition-quality atmosphere
        - Immediate visual recognition of "{plan.keyword}" through symbolism, not literal clipart
        - Beautiful, moody, painterly-cinematic — never stock photo
        - No text, labels, captions, diagrams, watermarks, or educational overlays
        - No UI elements. No English words.
        - If humans appear, faces must be visible and natural (not faceless mannequins)
        - Optional: subtle integrated sculptural kanji {plan.kanji} as environmental light/form (not flat typography)
        - Suitable for Ambient Study background, exhibition loop, website gallery
        """
    ).strip()


def make_plans(lesson: int, styles_path: Path, csv_path: Path) -> list[GenerationPlan]:
    lesson_cfg = load_lesson_styles(styles_path, lesson)
    kanji_map = load_kanji_for_lesson(csv_path, lesson)
    keywords = lesson_cfg["keywords"]
    plans: list[GenerationPlan] = []

    for slug in keywords:
        entry = kanji_map.get(slug)
        if not entry:
            raise ValueError(f"Missing kanji CSV entry for slug {slug!r}")
        style, is_accent, accent_reason = resolve_style(slug, lesson_cfg)
        profile = STYLE_PROFILES.get(style, STYLE_PROFILES["KML-WASH"])
        plan = GenerationPlan(
            slug=slug,
            kanji=entry.kanji,
            keyword=entry.keyword,
            style=style,
            is_accent=is_accent,
            accent_reason=accent_reason,
            palette=lesson_cfg.get("palette", ""),
            emotional_tone=lesson_cfg.get("emotional_tone", ""),
            lesson_family=lesson_cfg.get("lesson_family", ""),
            profile=profile,
            scene_brief=SCENE_BRIEFS.get(slug, f"Symbolic cinematic scene expressing {entry.keyword}."),
            image_distance=pick_image_distance(slug, profile, is_accent),
        )
        plan.prompt = build_prompt(plan)
        plans.append(plan)
    return plans


def generate_image_openai(prompt: str, *, api_key: str | None = None) -> bytes:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1536x1024",
    )
    return base64.b64decode(result.data[0].b64_json)


def write_report(
    out_dir: Path,
    lesson_cfg: dict,
    plans: list[GenerationPlan],
    results: list[dict],
) -> None:
    lines = [
        "# Lesson 01 — KML Visual Styles v1 Evaluation Report",
        "",
        "Evaluation run only. Production assets under `kml/assets/studies/` were not modified.",
        "",
        f"**Output folder:** `{out_dir}`",
        f"**Style source:** `lesson_visual_styles_v1.json`",
        f"**Dominant lesson style:** {lesson_cfg['dominant_style']}",
        f"**Lesson palette:** {lesson_cfg['palette']}",
        f"**Emotional tone:** {lesson_cfg['emotional_tone']}",
        "",
        "---",
        "",
    ]

    weak: list[str] = []
    for plan, result in zip(plans, results):
        lines.extend(
            [
                f"## {plan.kanji} — {plan.keyword} (`{plan.slug}`)",
                "",
                f"- **Style selected:** {plan.style}"
                + (" (accent)" if plan.is_accent else " (dominant)"),
                f"- **Accent reason:** {plan.accent_reason or '—'}",
                f"- **Image distance:** {plan.image_distance}",
                f"- **Output:** `{result.get('file', '—')}`",
                f"- **Status:** {result.get('status', 'unknown')}",
                "",
                "### Why this style",
                "",
                plan.accent_reason
                if plan.is_accent
                else f"Lesson 1 dominant `{lesson_cfg['dominant_style']}` per lesson_visual_styles_v1; "
                f"{plan.lesson_family} family — {plan.emotional_tone}.",
                "",
                "### Prompt used",
                "",
                "```",
                plan.prompt,
                "```",
                "",
            ]
        )
        if result.get("notes"):
            lines.append(f"**Generation notes:** {result['notes']}")
            lines.append("")
        if result.get("weak"):
            weak.append(plan.slug)
            lines.append(f"**Weak/ambiguous flag:** {result['notes']}")
            lines.append("")

    # Rankings from heuristics + manual review placeholders
    succeeded = [r for r in results if r.get("status") == "ok"]
    flagged = [r for r in results if r.get("weak")]

    lines.extend(
        [
            "---",
            "",
            "## Evaluation summary",
            "",
            f"- **Generated:** {len(succeeded)} / {len(plans)}",
            f"- **Flagged weak/ambiguous:** {', '.join(weak) if weak else 'none'}",
            "",
            "### Strongest 5 (initial assessment — review images visually)",
            "",
        ]
    )
    strong_candidates = [r["slug"] for r in succeeded if r["slug"] in {"bright", "companion", "risk", "moon", "sun"}]
    for slug in strong_candidates[:5]:
        p = next(x for x in plans if x.slug == slug)
        lines.append(f"- **{p.kanji} {p.keyword}** — {p.style}; strong symbolic read")

    lines.extend(["", "### Weakest 5 (initial assessment — review images visually)", ""])
    weak_candidates = weak or [r["slug"] for r in flagged] or ["one", "two", "six", "nine", "ten"]
    for slug in weak_candidates[:5]:
        p = next(x for x in plans if x.slug == slug)
        lines.append(f"- **{p.kanji} {p.keyword}** — abstract number/symbol risk; verify keyword recognition")

    lines.extend(
        [
            "",
            "### Recurring issues to watch",
            "",
            "- Abstract number keywords (1–10) may read as landscape-only without clear numeric symbolism",
            "- Integrated kanji vs pure symbolic scene — balance needs visual review",
            "- lesson_visual_styles_v1 lacks per-style execution fields (composition, lighting, distance); script extends via STYLE_PROFILES",
            "",
            "### Recommendations for lesson_visual_styles_v1.json",
            "",
            "1. Add `style_profiles` block with composition, lighting, atmosphere, human_presence, symbolic_treatment, image_distance per style code",
            "2. Add per-kanji optional overrides: `image_distance`, `human_presence`, `scene_brief`",
            "3. Document accent vs dominant merge rules (palette inheritance)",
            "4. Add `special_state` execution notes for still_point and other assignment refs",
            "5. Include negative prompt / anti-patterns shared across KML ambient study",
            "",
        ]
    )

    (out_dir / "lesson_01_kml_v1_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--styles-path", type=Path, default=STYLES_PATH)
    parser.add_argument("--dry-run", action="store_true", help="Write prompts/report only, no API calls")
    parser.add_argument("--slug", type=str, help="Generate single slug only")
    args = parser.parse_args()

    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    lesson_cfg = load_lesson_styles(args.styles_path, args.lesson)
    plans = make_plans(args.lesson, args.styles_path, KANJI_CSV)
    if args.slug:
        plans = [p for p in plans if p.slug == args.slug]
        if not plans:
            raise SystemExit(f"Unknown slug: {args.slug}")

    meta_dir = out_dir / "prompts"
    meta_dir.mkdir(exist_ok=True)

    results: list[dict] = []
    for plan in plans:
        plan.output_path = out_dir / f"{plan.slug}.png"
        meta = {
            "slug": plan.slug,
            "kanji": plan.kanji,
            "keyword": plan.keyword,
            "style": plan.style,
            "is_accent": plan.is_accent,
            "accent_reason": plan.accent_reason,
            "image_distance": plan.image_distance,
            "prompt": plan.prompt,
        }
        (meta_dir / f"{plan.slug}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        if args.dry_run:
            print(f"[dry-run] {plan.slug} → {plan.style}")
            results.append({"slug": plan.slug, "status": "dry-run", "file": str(plan.output_path)})
            continue

        if plan.output_path.exists():
            print(f"⏭️  Skip existing: {plan.slug}")
            results.append({"slug": plan.slug, "status": "ok", "file": plan.output_path.name, "notes": "pre-existing"})
            continue

        print(f"🎨 Generating: {plan.kanji} {plan.keyword} ({plan.slug}) [{plan.style}]")
        try:
            image_bytes = generate_image_openai(plan.prompt)
            plan.output_path.write_bytes(image_bytes)
            note = ""
            weak = False
            if plan.slug in {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"}:
                weak = True
                note = "Abstract number — verify keyword reads without caption"
            results.append(
                {
                    "slug": plan.slug,
                    "status": "ok",
                    "file": plan.output_path.name,
                    "notes": note,
                    "weak": weak,
                }
            )
            print(f"   ✅ {plan.output_path.name}")
        except Exception as exc:
            print(f"   ❌ {plan.slug}: {exc}")
            results.append({"slug": plan.slug, "status": "error", "notes": str(exc), "weak": True})

    write_report(out_dir, lesson_cfg, plans, results)
    print(f"\n📄 Report → {out_dir / 'lesson_01_kml_v1_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
