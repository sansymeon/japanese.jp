#!/usr/bin/env python3
"""Build the 137-minute Ambient Gallery Film collection (Ambient Move V2).

Mixes Heart Exhibition + Lessons 1–10 gallery artwork into one textless
Ken Burns journey timed to audio/137_minute_ambient.mp3.

V2: scenic quality filter, longer holds (35–45s), stronger museum camera.
"""

from __future__ import annotations

import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ASSETS = REPO / "assets"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import collection_json_path, write_collection_path  # noqa: E402

COLLECTION_ID = "ambient_gallery_film"
OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)
SCENIC_EXCLUDE_PATH = ROOT / "collections" / "ambient_gallery_film" / "scenic_exclude.json"
SOUNDTRACK = "audio/137_minute_ambient.mp3"
SEED = 20260725

MOTIONS = (
    "push-in",
    "pull-out",
    "drift-x",
    "drift-y",
    "drift-diagonal",
    "rise",
)

# Ambient Move V2 — longer museum pacing (ms).
HOLD_MIN_MS = 35_000
HOLD_MAX_MS = 45_000
HOLD_EXCEPTIONAL_MS = 60_000
TRANSITION_MS = 2_500
ARRIVAL_FADE_MS = 2_500
# Long-film closing crest: soft arrival → linger → long fade to black.
CLOSING_REVEAL_MS = 5_000
CLOSING_HOLD_MS = 7_000
CLOSING_FADE_MS = 12_000
CLOSING_BLACK_AFTER_MS = 2_000

SILENT_CREST_BOOKENDS = {
    "mode": "silentCrest",
    "closing": {
        "image": "images/gold_closing.png",
        "bookendSize": "small",
        "silentAfterSoundtrack": True,
        "holdUntilSoundtrackEnds": False,
    },
}

# Noticeable yet elegant Ken Burns (~2.5× prior gallery drift).
CAMERA_MOTION_SCALE = 2.5
PEOPLE_MOTION_SCALE = 1.15

# Intelligent camera: preferred motion by keyword / slug.
SCENIC_MOTION_BY_SLUG: dict[str, str] = {
    # Landscapes — slowly reveal the wider scene
    "field": "pull-out",
    "meadow": "pull-out",
    "farm": "drift-x",
    "open_sea": "pull-out",
    "horizon": "pull-out",
    "cape": "drift-x",
    "state": "pull-out",
    "plane": "pull-out",
    "outside": "pull-out",
    "many": "pull-out",
    # Streets / villages — drift gently along
    "street": "drift-x",
    "town": "drift-x",
    "home_village": "drift-x",
    "straightaway": "drift-x",
    "gland": "drift-x",
    # Temples / architecture — move toward the entrance
    "temple": "push-in",
    "old": "push-in",
    "olden_times": "push-in",
    "guard": "push-in",
    "complete": "push-in",
    # Rivers / water — follow the water
    "river": "drift-x",
    "large_river": "drift-diagonal",
    "creek": "drift-diagonal",
    "water": "drift-x",
    "tide": "drift-x",
    "fishing": "drift-x",
    "spring": "push-in",
    "source": "push-in",
    "lake": "pull-out",
    "swim": "drift-x",
    "ice": "drift-diagonal",
    "cleanse": "drift-x",
    "eventide": "drift-y",
    "evening": "drift-y",
    # Mountains / sky — climb toward the peak / light
    "rise": "rise",
    "rising_sun": "rise",
    "dawn": "rise",
    "morning": "rise",
    "sun": "rise",
    "moon": "rise",
    "top": "rise",
    "up": "rise",
    "ray": "rise",
    "sparkle": "rise",
    "illuminate": "rise",
    "shining": "rise",
    "bright": "rise",
    # Interiors / focal points
    "lamp": "push-in",
    "stomach": "push-in",
    "overnight": "push-in",
    "den": "push-in",
    # People / portraits — very subtle (also lower motionScale)
    "eye": "drift-x",
    "elbow": "push-in",
    "love": "push-in",
    "mother": "push-in",
    "child": "push-in",
    "woman": "push-in",
    "companion": "drift-x",
    "tongue": "push-in",
    "newborn": "push-in",
    "older_brother": "push-in",
    "I": "push-in",
    "oneself": "push-in",
}

PEOPLE_SLUGS = frozenset(
    {
        "eye",
        "elbow",
        "love",
        "mother",
        "child",
        "woman",
        "companion",
        "tongue",
        "newborn",
        "older_brother",
        "I",
        "oneself",
        "fond_of",
        "see",
        "likeness",
        "resemblance",
        "employee",
        "vice",
        "petitioner",
        "petition",
    }
)

# Especially beautiful scenes — prefer exceptional hold lengths.
EXCEPTIONAL_SLUGS = frozenset(
    {
        "river",
        "temple",
        "field",
        "lake",
        "love",
        "morning",
        "dawn",
        "rising_sun",
        "open_sea",
        "meadow",
        "farm",
        "home_village",
        "large_river",
        "horizon",
        "cape",
        "eye",
        "evening",
        "moon",
        "sun",
        "water",
        "spring",
        "fishing",
        "town",
        "street",
        "black",
        "lamp",
        "plane",
        "gallbladder",
        "stomach",
    }
)


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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_scenic_exclude() -> frozenset[str]:
    if not SCENIC_EXCLUDE_PATH.is_file():
        print(f"warn: missing scenic exclude {SCENIC_EXCLUDE_PATH}", file=sys.stderr)
        return frozenset()
    doc = load_json(SCENIC_EXCLUDE_PATH)
    return frozenset(str(s) for s in (doc.get("excludeSlugs") or []))


def scene_slug(scene: dict) -> str:
    return Path(scene["image"]).stem


def apply_scenic_filter(scenes: list[dict], exclude: frozenset[str]) -> list[dict]:
    """Curate wall-worthy scenic artwork only (Ambient Move V2)."""
    kept: list[dict] = []
    dropped: list[str] = []
    for scene in scenes:
        slug = scene_slug(scene)
        if slug in exclude:
            dropped.append(slug)
            continue
        kept.append(scene)
    print(
        f"Scenic filter: kept {len(kept)} / {len(scenes)} "
        f"(excluded {len(dropped)})",
        file=sys.stderr,
    )
    return kept


def collect_source_scenes() -> list[dict]:
    """Heart + Lessons 1–10 gallery images, deduped by image path."""
    by_image: dict[str, dict] = {}

    heart = load_json(ROOT / "collections" / "heart_v5.json")
    for scene in heart.get("scenes") or []:
        image = scene.get("image")
        if not image:
            continue
        by_image[image] = {
            "id": scene.get("id") or f"heart_{Path(image).stem}",
            "kanji": scene.get("kanji") or "",
            "keyword": scene.get("keyword") or "",
            "image": image,
            "source": "heart",
            "galleryCamera": dict(scene.get("galleryCamera") or {}),
            "imageScale": scene.get("imageScale"),
            "imageFocus": scene.get("imageFocus"),
            "verse": scene.get("verse") or {"jpHtml": "", "en": ""},
        }

    for lesson in range(1, 11):
        path = collection_json_path(ROOT, f"lesson_{lesson:02d}_gallery")
        if not path.is_file():
            print(f"warn: missing {path}", file=sys.stderr)
            continue
        doc = load_json(path)
        for scene in doc.get("scenes") or []:
            image = scene.get("image")
            if not image or image in by_image:
                continue
            by_image[image] = {
                "id": scene.get("id") or f"L{lesson:02d}_{Path(image).stem}",
                "kanji": scene.get("kanji") or "",
                "keyword": scene.get("keyword") or "",
                "image": image,
                "source": f"lesson_{lesson:02d}",
                "galleryCamera": dict(scene.get("galleryCamera") or {}),
                "imageScale": scene.get("imageScale"),
                "imageFocus": scene.get("imageFocus"),
                "verse": scene.get("verse") or {"jpHtml": "", "en": ""},
            }

    return list(by_image.values())


def interleave_mix(scenes: list[dict], rng: random.Random) -> list[dict]:
    """Mix sources naturally — not strict lesson order."""
    buckets: dict[str, list[dict]] = {}
    for scene in scenes:
        buckets.setdefault(scene["source"], []).append(scene)
    for bucket in buckets.values():
        rng.shuffle(bucket)

    order = list(buckets.keys())
    rng.shuffle(order)
    mixed: list[dict] = []
    while any(buckets.values()):
        progressed = False
        for key in order:
            if buckets.get(key):
                mixed.append(buckets[key].pop())
                progressed = True
        if not progressed:
            break
        # Occasional double-draw from a random non-empty bucket softens the pattern.
        if rng.random() < 0.18:
            nonempty = [k for k, v in buckets.items() if v]
            if nonempty:
                k = rng.choice(nonempty)
                mixed.append(buckets[k].pop())
    return mixed


def preferred_motion(scene: dict) -> str | None:
    slug = scene_slug(scene)
    if slug in SCENIC_MOTION_BY_SLUG:
        return SCENIC_MOTION_BY_SLUG[slug]
    cam = scene.get("galleryCamera") or {}
    preferred = cam.get("motion")
    return preferred if preferred in MOTIONS else None


def assign_motions(scenes: list[dict], rng: random.Random) -> None:
    """Intelligent camera: composition-aware motion, no consecutive repeats."""
    prev = None
    for scene in scenes:
        slug = scene_slug(scene)
        preferred = preferred_motion(scene)
        choices = [m for m in MOTIONS if m != prev]
        if preferred in choices and rng.random() < 0.78:
            motion = preferred
        elif preferred == prev and preferred is not None:
            # Soft alternate when preferred would repeat.
            alt = {
                "push-in": "drift-diagonal",
                "pull-out": "drift-x",
                "drift-x": "push-in",
                "drift-y": "drift-diagonal",
                "drift-diagonal": "rise",
                "rise": "pull-out",
            }.get(preferred, rng.choice(choices))
            motion = alt if alt != prev else rng.choice(choices)
        else:
            motion = rng.choice(choices)

        cam = dict(scene.get("galleryCamera") or {})
        cam["motion"] = motion
        if slug in PEOPLE_SLUGS:
            cam["motionScale"] = PEOPLE_MOTION_SCALE
        scene["galleryCamera"] = cam
        prev = motion


def distribute_holds(scenes: list[dict], budget_ms: int, rng: random.Random) -> list[int]:
    """Vary 35–45s (exceptional up to 60s) so holds sum to budget."""
    n = len(scenes)
    if n <= 0:
        return []
    avg = budget_ms / n
    if avg < HOLD_MIN_MS:
        return [max(HOLD_MIN_MS, int(avg))] * n
    if avg > HOLD_MAX_MS:
        # Stretch toward exceptional band rather than clamping everything flat.
        return [min(HOLD_EXCEPTIONAL_MS, int(avg))] * n

    holds = []
    for scene in scenes:
        slug = scene_slug(scene)
        roll = rng.random()
        if slug in EXCEPTIONAL_SLUGS and roll < 0.55:
            holds.append(rng.randint(48_000, HOLD_EXCEPTIONAL_MS))
        elif roll < 0.10:
            holds.append(rng.randint(HOLD_MAX_MS, HOLD_EXCEPTIONAL_MS))
        elif roll < 0.28:
            holds.append(rng.randint(HOLD_MIN_MS, HOLD_MIN_MS + 4_000))
        else:
            holds.append(rng.randint(HOLD_MIN_MS + 4_000, HOLD_MAX_MS))

    total = sum(holds)
    scaled = [
        max(HOLD_MIN_MS, min(HOLD_EXCEPTIONAL_MS, int(h * budget_ms / total)))
        for h in holds
    ]
    drift = budget_ms - sum(scaled)
    i = 0
    while drift != 0 and i < n * 8:
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


def expand_pool_if_needed(scenes: list[dict], soundtrack_ms: int, rng: random.Random) -> list[dict]:
    """If average hold would exceed exceptional max, soft-loop with reshuffled pass."""
    n = len(scenes)
    transitions = max(0, n - 1) * TRANSITION_MS
    budget = soundtrack_ms - transitions
    if n == 0:
        raise SystemExit("No source images found")
    avg = budget / n
    if avg <= HOLD_EXCEPTIONAL_MS:
        return scenes

    target_avg = (HOLD_MIN_MS + HOLD_MAX_MS) // 2
    needed = max(n, int(budget / target_avg) + 1)
    extras = needed - n
    pool = list(scenes)
    second = list(scenes)
    rng.shuffle(second)
    added = 0
    last_image = pool[-1]["image"] if pool else None
    for scene in second:
        if added >= extras:
            break
        if scene["image"] == last_image:
            continue
        clone = dict(scene)
        clone["id"] = f"{scene['id']}__reprise"
        pool.append(clone)
        last_image = clone["image"]
        added += 1
    while len(pool) < needed:
        for scene in second:
            if len(pool) >= needed:
                break
            if scene["image"] == last_image:
                continue
            clone = dict(scene)
            clone["id"] = f"{scene['id']}__reprise{len(pool)}"
            pool.append(clone)
            last_image = clone["image"]
    return pool


def build_scene_payload(raw: dict, hold_ms: int) -> dict:
    scene = {
        "id": raw["id"],
        "kanji": raw.get("kanji") or "",
        "keyword": raw.get("keyword") or "",
        "image": raw["image"],
        "galleryCamera": raw["galleryCamera"],
        "artworkAloneMs": hold_ms,
        "verse": {"jpHtml": "", "en": ""},
        "meta": {
            "source": raw["source"],
            "ambientGalleryFilm": True,
            "ambientMove": "v2",
        },
    }
    if raw.get("imageScale") is not None:
        scene["imageScale"] = raw["imageScale"]
    if raw.get("imageFocus"):
        scene["imageFocus"] = raw["imageFocus"]
    rev = image_rev(raw["image"])
    if rev is not None:
        scene["imageRev"] = rev
    return scene


def build() -> dict:
    rng = random.Random(SEED)
    soundtrack_ms = soundtrack_duration_ms(SOUNDTRACK)
    exclude = load_scenic_exclude()
    sources = apply_scenic_filter(collect_source_scenes(), exclude)
    if not sources:
        raise SystemExit("Scenic filter removed every source image")

    mixed = interleave_mix(sources, rng)
    mixed = expand_pool_if_needed(mixed, soundtrack_ms, rng)
    assign_motions(mixed, rng)

    n = len(mixed)
    transitions = max(0, n - 1) * TRANSITION_MS
    hold_budget = soundtrack_ms - transitions
    if hold_budget < n * HOLD_MIN_MS:
        # Trim scenes so we never rush — soundtrack wins.
        max_scenes = max(1, hold_budget // HOLD_MIN_MS)
        mixed = mixed[:max_scenes]
        n = len(mixed)
        transitions = max(0, n - 1) * TRANSITION_MS
        hold_budget = soundtrack_ms - transitions

    holds = distribute_holds(mixed, hold_budget, rng)
    scenes = [build_scene_payload(raw, hold) for raw, hold in zip(mixed, holds)]
    avg_hold = sum(holds) / n

    exhibition = {
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
    }

    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": COLLECTION_ID,
        "title": "Ambient Gallery Film — KML Japan",
        "notes": (
            "Ambient Move V2: scenic-curated textless journey through Heart + "
            "Lessons 1–10 artwork. Stronger Ken Burns, 35–45s holds (exceptional "
            f"up to 60s). Silent gold crest after soundtrack "
            f"(reveal {CLOSING_REVEAL_MS // 1000}s · hold {CLOSING_HOLD_MS // 1000}s · "
            f"fade {CLOSING_FADE_MS // 1000}s). {n} images · avg hold "
            f"{avg_hold / 1000:.1f}s · soundtrack {soundtrack_ms / 60000:.1f} min."
        ),
        "soundtrack": {"main": SOUNDTRACK},
        "bookends": dict(SILENT_CREST_BOOKENDS),
        "exhibition": exhibition,
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "ambientGalleryFilm",
            "showKeyword": False,
            "showKanji": False,
            "exhibitProfile": "gallery",
            "verseMode": "sequential",
            "typography": "mobile-refine",
            "bookendStyle": "galleryCrest",
            "cameraMotionScale": CAMERA_MOTION_SCALE,
            "ambientMove": "v2",
        },
        "meta": {
            "family": "ambientGalleryFilm",
            "ambientMove": "v2",
            "sceneCount": n,
            "soundtrackDurationMs": soundtrack_ms,
            "sources": ["heart_v5", "lesson_01_gallery…lesson_10_gallery"],
            "scenicExcludePath": "collections/ambient_gallery_film/scenic_exclude.json",
            "scenicExcludedCount": len(exclude),
            "seed": SEED,
            "avgHoldMs": int(avg_hold),
            "holdMinMs": min(holds),
            "holdMaxMs": max(holds),
            "cameraMotionScale": CAMERA_MOTION_SCALE,
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    meta = config["meta"]
    print(
        f"Wrote {meta['sceneCount']} exhibits → {OUT_PATH}\n"
        f"  soundtrack {meta['soundtrackDurationMs'] / 60000:.1f} min\n"
        f"  holds {meta['holdMinMs'] / 1000:.1f}–{meta['holdMaxMs'] / 1000:.1f}s "
        f"(avg {meta['avgHoldMs'] / 1000:.1f}s)\n"
        f"  scenic excluded {meta['scenicExcludedCount']} · "
        f"cameraMotionScale {meta['cameraMotionScale']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
