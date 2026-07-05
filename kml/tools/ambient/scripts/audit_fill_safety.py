#!/usr/bin/env python3
"""Audit and auto-fix imageScale for long-hold Gallery Guardian collections.

KML framing policy: preserve full composition by default; apply only the minimum
per-scene imageScale required for full-frame coverage across the entire motion path.

Usage (from kml/tools/ambient):
  python3 scripts/audit_fill_safety.py lesson_02_vocabulary
  python3 scripts/audit_fill_safety.py lesson_02_vocabulary --dry-run
  node tools/audit-fill-safety.js lesson_02_vocabulary
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from collection_paths import collection_json_path  # noqa: E402
from fill_safety_geometry import ViewportSpec, motion_path_is_safe  # noqa: E402
from gallery_guardian_core import (  # noqa: E402
    measure_cover_boost_from_rgba,
    plan_scene,
)

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("audit_fill_safety.py requires Pillow (pip install Pillow)") from exc

GUARDIAN_PROFILES = frozenset(
    {
        "gallery",
        "vocabularyExhibition",
        "compoundsExhibition",
    }
)

BLEED_BY_PROFILE: dict[str, float] = {
    "vocabularyExhibition": 0.14,
    "gallery": 0.10,
    "compoundsExhibition": 0.10,
}

DEFAULT_BLEED = 0.10
NATURAL_FRAMING_SCALE = 1.0
MAX_IMAGE_SCALE = 2.5
SCALE_STEP = 0.005


@dataclass
class SceneReport:
    index: int
    scene_id: str
    kanji: str
    keyword: str
    original_scale: float
    final_scale: float
    adjusted: bool
    cover_boost: float


def scene_framing_scale(scene: dict) -> float:
    return float(scene.get("imageScale", NATURAL_FRAMING_SCALE))


def resolve_image_path(collection: dict, scene: dict) -> Path:
    assets_base = collection.get("assetsBase", "../../assets")
    base = (ROOT / assets_base).resolve()
    return base / scene.get("image", "")


def load_image_metrics(path: Path) -> tuple[int, int, float]:
    with Image.open(path) as im:
        im = im.convert("RGBA")
        w, h = im.size
        sample = im.resize((48, 32), Image.Resampling.BILINEAR)
        boost = measure_cover_boost_from_rgba(48, 32, sample.tobytes())
    return w, h, boost


def exhibit_motion_duration_ms(collection: dict, scene: dict, exhibition: dict) -> int:
    profile = (collection.get("display") or {}).get("exhibitProfile", "")
    t = exhibition

    if profile == "vocabularyExhibition":
        steps = scene.get("vocabulary", {}).get("steps") or []
        step_count = max(len(steps), 1)
        step_ms = (
            t.get("vocabularyStepRevealMs", 1400)
            + t.get("vocabularyStepHoldMs", 3500)
            + t.get("vocabularyStepFadeMs", 1400)
        )
        ms = (
            t.get("artworkAloneMs", 0)
            + t.get("vocabularyPauseBeforeMs", 4000)
            + step_count * step_ms
            + t.get("vocabularyVerseJpRevealMs", 1600)
            + t.get("vocabularyVerseKanjiHoldMs", 3500)
            + t.get("vocabularyVerseFuriganaEnterDelayMs", 900)
            + t.get("vocabularyVerseFuriganaEnterMs", 2500)
            + t.get("vocabularyVerseFuriganaHoldMs", 4500)
            + t.get("vocabularyVerseFuriganaFadeMs", 2500)
            + t.get("vocabularyVerseNativeHoldMs", 3000)
            + t.get("vocabularyVerseJpFadeMs", 1400)
        )
        if (collection.get("display") or {}).get("showEnglish", True):
            ms += (
                t.get("vocabularyVerseEnRevealMs", 1400)
                + t.get("vocabularyVerseEnHoldMs", 6000)
                + t.get("vocabularyVerseEnFadeMs", 1400)
            )
        return int(ms)

    if profile == "compoundsExhibition":
        compounds = scene.get("compounds") or {}
        rows = compounds.get("steps") or compounds.get("items") or []
        row_count = max(len(rows), 1)
        step_ms = t.get("compoundsStepRevealMs", 1400) + t.get("compoundsStepFadeMs", 1400)
        ms = (
            t.get("artworkAloneMs", 0)
            + t.get("compoundsPauseBeforeMs", 4000)
            + row_count * step_ms
            + t.get("compoundsTargetKanjiRevealMs", 1600)
            + t.get("compoundsTargetKanjiHoldMs", 2400)
            + t.get("compoundsTargetKanjiFadeMs", 1400)
        )
        return int(ms)

    if profile == "gallery":
        return int(
            t.get("artworkAloneMs", 0)
            + t.get("kanjiRevealMs", 0)
            + t.get("imageVerseKanjiHoldMs", t.get("artworkAloneMs", 8000))
            + t.get("imageExhaleFadeMs", 0)
        )

    return int(t.get("kenBurnsDurationMs", 90000))


def uses_guardian(collection: dict, scene: dict) -> bool:
    profile = (collection.get("display") or {}).get("exhibitProfile", "")
    if profile in GUARDIAN_PROFILES:
        return True
    return bool(scene.get("galleryCamera"))


def minimum_safe_scale(
    *,
    is_safe,
    base_scale: float,
) -> float:
    """Smallest framingScale >= base_scale that passes the motion-path check."""
    scale = base_scale
    if is_safe(scale):
        return round(scale, 3)

    while scale <= MAX_IMAGE_SCALE:
        scale += SCALE_STEP
        if is_safe(scale):
            return round(scale, 3)

    raise RuntimeError(f"could not achieve full coverage below imageScale {MAX_IMAGE_SCALE}")


def audit_scene(
    collection: dict,
    scene: dict,
    *,
    index: int,
    viewport: ViewportSpec,
    sample_count: int,
    scene_index: int,
) -> SceneReport:
    scene_id = scene.get("id", f"scene_{index}")
    kanji = scene.get("kanji", "")
    keyword = scene.get("keyword", "")
    original = scene_framing_scale(scene)

    image_path = resolve_image_path(collection, scene)
    if not image_path.is_file():
        raise FileNotFoundError(f"Missing image for {scene_id}: {image_path}")

    img_w, img_h, cover_boost = load_image_metrics(image_path)
    exhibition = collection.get("exhibition") or {}
    duration_ms = exhibit_motion_duration_ms(collection, scene, exhibition)
    focus = scene.get("imageFocus") or (scene.get("galleryCamera") or {}).get("focus")

    is_heart = (collection.get("id") or "").startswith("heart_") or (
        (collection.get("meta") or {}).get("theme") == "heart"
    )
    base_scale = NATURAL_FRAMING_SCALE
    plan_opts_base: dict = {
        "durationMs": duration_ms,
        "coverBoost": cover_boost,
        "sceneIndex": scene_index,
    }
    if is_heart:
        plan_opts_base["scaleMin"] = 0.82
        base_scale = scene_framing_scale(scene) if "imageScale" in scene else 0.86

    def is_safe(scale: float) -> bool:
        plan = plan_scene(scene, options={**plan_opts_base, "framingScale": scale})
        return motion_path_is_safe(
            img_w=img_w,
            img_h=img_h,
            plan=plan,
            focus=focus,
            viewport=viewport,
            sample_count=sample_count,
        )

    final = minimum_safe_scale(is_safe=is_safe, base_scale=base_scale)
    return SceneReport(
        index=index,
        scene_id=scene_id,
        kanji=kanji,
        keyword=keyword,
        original_scale=round(original, 3),
        final_scale=final,
        adjusted=abs(final - original) > 0.0005,
        cover_boost=cover_boost,
    )


def apply_scene_scale(scene: dict, final_scale: float) -> None:
    if final_scale <= NATURAL_FRAMING_SCALE + 0.0005:
        scene.pop("imageScale", None)
    else:
        scene["imageScale"] = final_scale


def audit_collection(
    collection_id: str,
    *,
    dry_run: bool = False,
    sample_count: int = 32,
    viewport: ViewportSpec | None = None,
) -> tuple[list[SceneReport], Path, dict, set[int]]:
    json_path = collection_json_path(ROOT, collection_id)
    if not json_path.is_file():
        raise FileNotFoundError(f"Collection not found: {json_path}")

    collection = json.loads(json_path.read_text(encoding="utf-8"))
    scenes = collection.get("scenes") or []
    if not scenes:
        raise ValueError(f"{collection_id}: no scenes")

    profile = (collection.get("display") or {}).get("exhibitProfile", "")
    bleed = BLEED_BY_PROFILE.get(profile, DEFAULT_BLEED)
    vp = viewport or ViewportSpec(bleed=bleed)

    reports: list[SceneReport] = []
    guardian_indices: set[int] = set()
    for index, scene in enumerate(scenes):
        if not uses_guardian(collection, scene):
            reports.append(
                SceneReport(
                    index=index,
                    scene_id=scene.get("id", f"scene_{index}"),
                    kanji=scene.get("kanji", ""),
                    keyword=scene.get("keyword", ""),
                    original_scale=scene_framing_scale(scene),
                    final_scale=scene_framing_scale(scene),
                    adjusted=False,
                    cover_boost=1.0,
                )
            )
            continue

        guardian_indices.add(index)
        report = audit_scene(
            collection,
            scene,
            index=index,
            viewport=vp,
            sample_count=sample_count,
            scene_index=index,
        )
        reports.append(report)
        if not dry_run:
            apply_scene_scale(scene, report.final_scale)

    if not dry_run:
        json_path.write_text(
            json.dumps(collection, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return reports, json_path, collection, guardian_indices


def _format_scale(value: float) -> str:
    return f"{value:.2f}"


def print_report(
    collection: dict,
    collection_id: str,
    reports: list[SceneReport],
    json_path: Path,
    *,
    dry_run: bool,
    guardian_indices: set[int],
) -> None:
    adjusted = [r for r in reports if r.index in guardian_indices and r.adjusted]
    already_safe = [r for r in reports if r.index in guardian_indices and not r.adjusted]

    print(f"Fill-safety audit: {collection_id}")
    print(f"  path: {json_path}")
    print(f"  profile: {(collection.get('display') or {}).get('exhibitProfile', '?')}")
    print(f"  mode: {'dry-run' if dry_run else 'apply'}")
    print()

    for r in reports:
        if r.index not in guardian_indices:
            continue
        label_parts = [p for p in (r.kanji, r.keyword) if p]
        label = " ".join(label_parts) if label_parts else r.scene_id
        if r.adjusted:
            status = "adjusted"
            detail = f"{_format_scale(r.original_scale)} → {_format_scale(r.final_scale)} {status}"
        else:
            status = "unchanged safe"
            detail = f"{_format_scale(r.final_scale)} {status}"
        boost_note = f"  (coverBoost {r.cover_boost:.3f})" if r.cover_boost > 1.001 else ""
        print(f"  {r.index:2d} {label} — {detail}{boost_note}")

    print()
    print(
        f"{len(guardian_indices)} exhibits checked, "
        f"{len(adjusted)} adjusted, {len(already_safe)} already safe."
    )
    if dry_run and adjusted:
        print("Re-run without --dry-run to write imageScale fixes.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Minimum per-scene fill-safety audit (KML long-hold framing policy)"
    )
    parser.add_argument("collection_id", help="e.g. lesson_02_vocabulary")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report without modifying JSON",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=32,
        help="Motion-path sample count per exhibit (default: 32)",
    )
    parser.add_argument(
        "--safety-px",
        type=float,
        default=2.0,
        help="Extra viewport inset safety margin in px (default: 2)",
    )
    parser.add_argument(
        "--viewport",
        default="1920x1080",
        help="Viewport WxH for audit (default: 1920x1080)",
    )
    args = parser.parse_args()

    try:
        vw, vh = args.viewport.lower().split("x", 1)
        viewport = ViewportSpec(width=float(vw), height=float(vh), safety_px=args.safety_px)
    except ValueError:
        print("Invalid --viewport; use WIDTHxHEIGHT e.g. 1920x1080", file=sys.stderr)
        return 2

    try:
        reports, json_path, collection, guardian_indices = audit_collection(
            args.collection_id,
            dry_run=args.dry_run,
            sample_count=max(8, args.samples),
            viewport=viewport,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print_report(
        collection,
        args.collection_id,
        reports,
        json_path,
        dry_run=args.dry_run,
        guardian_indices=guardian_indices,
    )
    over_max = [
        r
        for r in reports
        if r.index in guardian_indices and r.final_scale >= MAX_IMAGE_SCALE - 0.001
    ]
    return 1 if over_max else 0


if __name__ == "__main__":
    raise SystemExit(main())
