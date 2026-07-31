#!/usr/bin/env python3
"""Build Ambient Gallery Japan — Four Seasons exhibition JSON.

Curation source: collections/ambient_gallery_japan_4_seasons/manifest.json
Soundtrack: audio/ambient_japan_4_seasons.mp3 (~120 min)
Ending: silent gold crest (images/gold_closing.png), Ambient Film style.
"""

from __future__ import annotations

import json
import random
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import write_collection_path  # noqa: E402

COLLECTION_ID = "ambient_gallery_japan_4_seasons"
CURATION_DIR = ROOT / "collections" / "ambient_gallery_japan_4_seasons"
CURATION_MANIFEST = CURATION_DIR / "manifest.json"
OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)
SOUNDTRACK = "audio/ambient_japan_4_seasons.mp3"
IMAGE_PREFIX = "ambient_japan_4_seasons"
SEED = 20260729

MOTIONS = (
    "push-in",
    "pull-out",
    "drift-x",
    "drift-y",
    "drift-diagonal",
    "rise",
)

# Soft museum pacing around the ~46s average for 147 scenes / 120 min.
HOLD_MIN_MS = 38_000
HOLD_MAX_MS = 55_000
HOLD_EXCEPTIONAL_MS = 62_000
HOLD_FINAL_MS = 55_000
TRANSITION_MS = 2_500
ARRIVAL_FADE_MS = 2_500
CLOSING_REVEAL_MS = 5_000
CLOSING_HOLD_MS = 7_000
CLOSING_FADE_MS = 12_000
CLOSING_BLACK_AFTER_MS = 2_000
CAMERA_MOTION_SCALE = 2.5

SILENT_CREST_BOOKENDS = {
    "mode": "silentCrest",
    "closing": {
        "image": "images/gold_closing.png",
        "bookendSize": "small",
        "silentAfterSoundtrack": True,
        "holdUntilSoundtrackEnds": False,
    },
}

# Map curation folder → film category used for interleaving.
FOLDER_TO_CAT = {
    "01_spring": "spring",
    "02_summer": "summer",
    "03_autumn": "autumn",
    "04_winter": "winter",
    "05_mountains": "mountains",
    "06_forests": "forests",
    "07_rivers": "water",
    "08_coast": "coast",
    "09_temples_shrines": "temples",
    "10_villages": "villages",
    "11_gardens": "gardens",
    "12_mist_rain": "mist",
    "13_evening_night": "evening",
}

# Prefer season / place as primary exhibit category.
PRIMARY_PRIORITY = [
    "01_spring",
    "02_summer",
    "03_autumn",
    "04_winter",
    "13_evening_night",
    "09_temples_shrines",
    "08_coast",
    "07_rivers",
    "05_mountains",
    "06_forests",
    "10_villages",
    "11_gardens",
    "12_mist_rain",
]

ENDING_CANDIDATES = [
    "early_evening",
    "eventide",
    "evening",
    "moon",
    "inland_sea",
    "horizon",
    "water",
    "lake",
    "pagoda",
    "temple",
    "scenery",
    "garden",
    "imperial_gardens",
    "dawn",
    "overnight",
    "winter_evening",
    "rising_sun",
    "ray",
    "shining",
]

SIGNATURE_SLUGS = {
    "mt_fuji_2",
    "miyajima",
    "senso_ji_temple",
    "kyoto",
    "kyoto_pagoda",
    "bamboo_forest",
    "imperial_gardens",
    "nikko_fall_colors",
    "thatched_roof",
    "thatched_roof_winter",
    "inland_sea",
    "castle",
    "castle_2",
    "train_cherry_blossoms",
}


def soundtrack_duration_ms(relative_path: str) -> int:
    audio_path = ROOT / relative_path
    if not audio_path.is_file():
        raise FileNotFoundError(f"Missing soundtrack: {audio_path}")
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(audio_path),
        ],
        text=True,
    ).strip()
    return int(float(out) * 1000)


def image_rev(relative: str) -> int | None:
    path = ASSETS / relative
    if path.is_file():
        return int(path.stat().st_mtime)
    return None


def primary_category(folders: list[str]) -> str:
    for folder in PRIMARY_PRIORITY:
        if folder in folders:
            return FOLDER_TO_CAT[folder]
    return "mountains"


def load_curated_scenes() -> list[dict]:
    manifest = json.loads(CURATION_MANIFEST.read_text(encoding="utf-8"))
    membership = manifest.get("membership") or {}
    related_groups = [
        set(g) for g in (manifest.get("relatedGroups") or []) if isinstance(g, list)
    ]
    scenes: list[dict] = []
    for stem in manifest.get("images") or []:
        rel = f"{IMAGE_PREFIX}/{stem}.png"
        if not (ASSETS / rel).is_file():
            raise FileNotFoundError(f"Missing curated image asset: {rel}")
        folders = membership.get(stem) or []
        cat = primary_category(folders)
        group_ids = [
            i for i, g in enumerate(related_groups) if stem in g
        ]
        scenes.append(
            {
                "id": f"japan_{stem}",
                "kanji": "",
                "keyword": stem.replace("_", " "),
                "image": rel,
                "category": cat,
                "folders": folders,
                "relatedGroups": group_ids,
                "signature": stem in SIGNATURE_SLUGS,
                "galleryCamera": {},
                "slug": stem,
            }
        )
    return scenes


def category_of(scene: dict) -> str:
    return scene.get("category") or "mountains"


def scene_slug(scene: dict) -> str:
    return scene.get("slug") or Path(scene["image"]).stem


def pick_ending_scenes(scenes: list[dict], count: int = 10) -> list[dict]:
    by_slug = {scene_slug(s): s for s in scenes}
    chosen: list[dict] = []
    used: set[str] = set()
    for slug in ENDING_CANDIDATES:
        if slug in by_slug and slug not in used:
            chosen.append(by_slug[slug])
            used.add(slug)
        if len(chosen) >= count:
            break
    # Prefer evening/mist leftovers if still short.
    if len(chosen) < count:
        for s in scenes:
            slug = scene_slug(s)
            if slug in used:
                continue
            if category_of(s) in {"evening", "mist", "coast", "water", "temples"}:
                chosen.append(s)
                used.add(slug)
            if len(chosen) >= count:
                break
    return chosen[:count]


def related_conflict(candidate: dict, recent: list[dict], window: int = 4) -> bool:
    cand_groups = set(candidate.get("relatedGroups") or [])
    if not cand_groups:
        return False
    for prev in recent[-window:]:
        if cand_groups & set(prev.get("relatedGroups") or []):
            return True
    return False


def score_candidate(
    cand: dict,
    *,
    prev_cats: list[str],
    remaining_by_cat: dict[str, int],
    since_signature: int,
    signature_gap_target: int,
) -> float:
    cat = category_of(cand)
    score = 0.0
    total_rem = max(1, sum(remaining_by_cat.values()))
    # Prefer underrepresented remaining categories.
    score += (1.0 - remaining_by_cat.get(cat, 0) / total_rem) * 12.0

    if prev_cats:
        last = prev_cats[-1]
        if cat == last:
            score -= 80.0
        prefer = {
            "spring": {"temples", "villages", "gardens", "water", "mountains"},
            "summer": {"forests", "coast", "water", "villages", "mountains"},
            "autumn": {"temples", "forests", "mountains", "water", "villages"},
            "winter": {"mountains", "villages", "water", "evening", "mist"},
            "mountains": {"water", "forests", "villages", "temples", "coast"},
            "forests": {"water", "mist", "temples", "mountains"},
            "water": {"mountains", "temples", "forests", "coast", "evening"},
            "coast": {"villages", "temples", "mountains", "evening"},
            "temples": {"gardens", "forests", "water", "villages", "mist"},
            "villages": {"temples", "spring", "forests", "water", "summer"},
            "gardens": {"temples", "spring", "water", "evening"},
            "mist": {"forests", "water", "temples", "evening"},
            "evening": {"water", "temples", "mountains", "coast", "mist"},
        }.get(last, set())
        if cat in prefer:
            score += 6.0

    if cand.get("signature"):
        if since_signature < signature_gap_target:
            score -= 25.0
        else:
            score += 8.0
    return score


def interleave(scenes: list[dict], rng: random.Random, *, ending_count: int = 10) -> list[dict]:
    ending = pick_ending_scenes(scenes, count=ending_count)
    ending_ids = {s["id"] for s in ending}
    pool = [s for s in scenes if s["id"] not in ending_ids]
    rng.shuffle(pool)

    buckets: dict[str, list[dict]] = defaultdict(list)
    for scene in pool:
        buckets[category_of(scene)].append(scene)
    for bucket in buckets.values():
        rng.shuffle(bucket)

    ordered: list[dict] = []
    prev_cats: list[str] = []
    since_signature = 99
    signature_gap_target = rng.randint(12, 18)

    while any(buckets.values()):
        candidates = [b[0] for b in buckets.values() if b]
        remaining_by_cat = {k: len(v) for k, v in buckets.items()}
        scored = [
            (
                score_candidate(
                    c,
                    prev_cats=prev_cats,
                    remaining_by_cat=remaining_by_cat,
                    since_signature=since_signature,
                    signature_gap_target=signature_gap_target,
                )
                + rng.random() * 1.5,
                c,
            )
            for c in candidates
        ]
        scored.sort(key=lambda t: t[0], reverse=True)

        last_cat = prev_cats[-1] if prev_cats else None
        chosen = None
        for _score, cand in scored:
            if related_conflict(cand, ordered):
                continue
            if last_cat is None or category_of(cand) != last_cat:
                chosen = cand
                break
        if chosen is None:
            # Relax related-group rule if stuck.
            for _score, cand in scored:
                if last_cat is None or category_of(cand) != last_cat:
                    chosen = cand
                    break
        if chosen is None:
            chosen = scored[0][1]

        cat = category_of(chosen)
        buckets[cat].pop(0)
        if not buckets[cat]:
            del buckets[cat]

        ordered.append(chosen)
        prev_cats.append(cat)
        if len(prev_cats) > 6:
            prev_cats = prev_cats[-6:]
        if chosen.get("signature"):
            since_signature = 0
            signature_gap_target = rng.randint(12, 18)
        else:
            since_signature += 1

    ordered.extend(ending)
    return ordered


def assign_motions(scenes: list[dict], rng: random.Random) -> None:
    prev = None
    for scene in scenes:
        choices = [m for m in MOTIONS if m != prev] or list(MOTIONS)
        motion = rng.choice(choices)
        cam = dict(scene.get("galleryCamera") or {})
        cam["motion"] = motion
        scene["galleryCamera"] = cam
        prev = motion


def distribute_holds(n: int, budget_ms: int, rng: random.Random) -> list[int]:
    if n <= 0:
        return []
    avg = budget_ms / n
    holds: list[int] = []
    for i in range(n):
        if i == n - 1:
            holds.append(HOLD_FINAL_MS)
        elif rng.random() < 0.12:
            holds.append(rng.randint(int(avg), min(HOLD_EXCEPTIONAL_MS, int(avg) + 8_000)))
        elif rng.random() < 0.20:
            holds.append(rng.randint(HOLD_MIN_MS, max(HOLD_MIN_MS, int(avg) - 4_000)))
        else:
            lo = max(HOLD_MIN_MS, int(avg) - 5_000)
            hi = min(HOLD_MAX_MS, int(avg) + 5_000)
            if hi <= lo:
                hi = lo + 1
            holds.append(rng.randint(lo, hi))

    total = sum(holds)
    scaled = [
        max(HOLD_MIN_MS, min(HOLD_EXCEPTIONAL_MS, int(h * budget_ms / total)))
        for h in holds
    ]
    drift = budget_ms - sum(scaled)
    i = 0
    while drift != 0 and i < n * 12:
        idx = i % n
        if drift > 0 and scaled[idx] < HOLD_EXCEPTIONAL_MS:
            step = min(drift, HOLD_EXCEPTIONAL_MS - scaled[idx], 250)
            scaled[idx] += step
            drift -= step
        elif drift < 0 and scaled[idx] > HOLD_MIN_MS:
            step = min(-drift, scaled[idx] - HOLD_MIN_MS, 250)
            scaled[idx] -= step
            drift += step
        i += 1
    scaled[-1] += budget_ms - sum(scaled)
    return scaled


def max_same_category_run(scenes: list[dict]) -> tuple[int, str]:
    best = 1
    best_cat = category_of(scenes[0]) if scenes else ""
    run = 1
    for i in range(1, len(scenes)):
        if category_of(scenes[i]) == category_of(scenes[i - 1]):
            run += 1
            if run > best:
                best = run
                best_cat = category_of(scenes[i])
        else:
            run = 1
    return best, best_cat


def build() -> dict:
    rng = random.Random(SEED)
    soundtrack_ms = soundtrack_duration_ms(SOUNDTRACK)
    sources = load_curated_scenes()
    if not sources:
        raise SystemExit("No curated scenes found")

    mixed = interleave(sources, rng, ending_count=10)
    assign_motions(mixed, rng)

    n = len(mixed)
    transitions = max(0, n - 1) * TRANSITION_MS
    hold_budget = soundtrack_ms - transitions
    if hold_budget < n * HOLD_MIN_MS:
        raise SystemExit(
            f"Soundtrack too short for {n} scenes at min hold "
            f"({hold_budget}ms budget, need {n * HOLD_MIN_MS}ms)"
        )

    holds = distribute_holds(n, hold_budget, rng)
    scenes = []
    for raw, hold in zip(mixed, holds):
        scene = {
            "id": raw["id"],
            "kanji": "",
            "keyword": raw.get("keyword") or "",
            "image": raw["image"],
            "galleryCamera": raw["galleryCamera"],
            "artworkAloneMs": hold,
            "verse": {"jpHtml": "", "en": ""},
            "meta": {
                "source": "ambient_gallery_japan_4_seasons",
                "category": raw["category"],
                "folders": raw.get("folders") or [],
                "signature": bool(raw.get("signature")),
                "slug": scene_slug(raw),
            },
        }
        rev = image_rev(raw["image"])
        if rev is not None:
            scene["imageRev"] = rev
        scenes.append(scene)

    avg_hold = sum(holds) / n
    max_run, max_run_cat = max_same_category_run(mixed)
    cat_counts: dict[str, int] = defaultdict(int)
    for s in mixed:
        cat_counts[category_of(s)] += 1

    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": COLLECTION_ID,
        "title": "Ambient Gallery Japan — Four Seasons",
        "notes": (
            "Textless seasonal journey through curated Japanese landscapes. "
            "Category-interleaved Ken Burns, ~46s holds, tranquil evening close, "
            f"silent gold crest after soundtrack "
            f"(reveal {CLOSING_REVEAL_MS // 1000}s · hold {CLOSING_HOLD_MS // 1000}s · "
            f"fade {CLOSING_FADE_MS // 1000}s). {n} images · avg hold "
            f"{avg_hold / 1000:.1f}s · soundtrack {soundtrack_ms / 60000:.1f} min."
        ),
        "soundtrack": {"main": SOUNDTRACK},
        "bookends": dict(SILENT_CREST_BOOKENDS),
        "exhibition": {
            "artworkArrivalMs": 0,
            "artworkArrivalFadeMs": ARRIVAL_FADE_MS,
            "exhibitionBlackBeforeMs": 0,
            "artworkAloneMs": int(avg_hold),
            "kanjiRevealMs": 0,
            "imageVerseKanjiHoldMs": 0,
            "imageVerseKanjiFadeMs": 0,
            "titleFadeMs": 0,
            "verseJpRevealMs": 0,
            "verseJpHoldMs": 0,
            "verseJpFadeMs": 0,
            "verseEnRevealMs": 0,
            "verseEnHoldMs": 0,
            "verseEnFadeMs": 0,
            "exhibitTransitionMs": TRANSITION_MS,
            "exhibitBlackHoldMs": 0,
            "kenBurnsDurationMs": int(avg_hold + TRANSITION_MS),
            "closingBlackBeforeMs": 0,
            "closingRevealMs": CLOSING_REVEAL_MS,
            "closingHoldMs": CLOSING_HOLD_MS,
            "closingExhaleMs": CLOSING_FADE_MS,
            "closingFadeToBlackMs": CLOSING_FADE_MS,
            "closingBlackAfterMs": CLOSING_BLACK_AFTER_MS,
            "closingSilenceHoldMs": 0,
            "blackHoldMs": 0,
            "seamlessExhibitHandoff": True,
        },
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "ambientGalleryJapan",
            "showKeyword": False,
            "showKanji": False,
            "exhibitProfile": "gallery",
            "verseMode": "sequential",
            "typography": "mobile-refine",
            "bookendStyle": "galleryCrest",
            "cameraMotionScale": CAMERA_MOTION_SCALE,
        },
        "meta": {
            "family": "ambientGalleryJapan",
            "edition": "Four Seasons",
            "sceneCount": n,
            "soundtrackDurationMs": soundtrack_ms,
            "curationManifest": "collections/ambient_gallery_japan_4_seasons/manifest.json",
            "seed": SEED,
            "avgHoldMs": int(avg_hold),
            "holdMinMs": min(holds),
            "holdMaxMs": max(holds),
            "transitionMs": TRANSITION_MS,
            "cameraMotionScale": CAMERA_MOTION_SCALE,
            "maxSameCategoryRun": max_run,
            "maxSameCategory": max_run_cat,
            "categoryCounts": dict(sorted(cat_counts.items())),
            "endingSlugs": [scene_slug(s) for s in mixed[-10:]],
            "closing": "gold crest (silentCrest)",
        },
        "scenes": scenes,
    }


def main() -> int:
    # Ensure assets symlink exists for recording/preview.
    link = ASSETS / IMAGE_PREFIX
    target = CURATION_DIR / "images"
    if not link.exists():
        link.symlink_to(Path("../tools/ambient/collections/ambient_gallery_japan_4_seasons/images"))
    elif link.is_symlink() and link.resolve() != target.resolve():
        print(f"WARN: {link} points elsewhere ({link.resolve()})")

    config = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    meta = config["meta"]
    print(
        f"Wrote {meta['sceneCount']} exhibits → {OUT_PATH}\n"
        f"  edition: {meta['edition']}\n"
        f"  soundtrack {meta['soundtrackDurationMs'] / 60000:.1f} min\n"
        f"  holds {meta['holdMinMs'] / 1000:.1f}–{meta['holdMaxMs'] / 1000:.1f}s "
        f"(avg {meta['avgHoldMs'] / 1000:.1f}s)\n"
        f"  ending: {' → '.join(meta['endingSlugs'])}\n"
        f"  closing: {meta['closing']}\n"
        f"  categories: {meta['categoryCounts']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
