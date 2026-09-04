#!/usr/bin/env python3
"""Build Ambient Movie — Lessons 1–20 (Ambient Revised).

Authoritative playlist: collections/ambient_gallery_film/ambient_movie_revised.txt

Quiet Japanese Photographic Realism journey timed to audio/137_minute_ambient.mp3.
Category-aware interleaving (not filename order). Silent gold crest after soundtrack.
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
from collection_paths import collection_json_path, write_collection_path  # noqa: E402

COLLECTION_ID = "ambient_gallery_film"
OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)
PLAYLIST_PATH = (
    ROOT / "collections" / "ambient_gallery_film" / "ambient_movie_revised.txt"
)
SOUNDTRACK = "audio/137_minute_ambient.mp3"
SEED = 20260727

MOTIONS = (
    "push-in",
    "pull-out",
    "drift-x",
    "drift-y",
    "drift-diagonal",
    "rise",
)

# Ambient pacing (ms) — same museum holds as Ambient Move V2.
HOLD_MIN_MS = 35_000
HOLD_MAX_MS = 45_000
HOLD_EXCEPTIONAL_MS = 60_000
HOLD_FINAL_MS = 55_000  # last image held slightly longer when budget allows
TRANSITION_MS = 2_500
ARRIVAL_FADE_MS = 2_500
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

CAMERA_MOTION_SCALE = 2.5
PEOPLE_MOTION_SCALE = 1.15

# Filename aliases when playlist typos / bare stems appear.
PLAYLIST_ALIASES: dict[str, str] = {
    "fold_of.png": "fond_of.jpg",
    "fold_of.jpg": "fond_of.jpg",
    "fold_of": "fond_of.jpg",
    "specialty": "specialty.jpg",
}

# Visual categories for interleaving.
CATEGORY_BY_SLUG: dict[str, str] = {
    # Mountains / wide landscapes
    "mt_fuji_2": "mountains",
    "rise": "mountains",
    "rising_sun": "mountains",
    "horizon": "mountains",
    "cape": "mountains",
    "plane": "mountains",
    "state": "mountains",
    "outside": "mountains",
    "scenery": "mountains",
    "top": "mountains",
    "up": "mountains",
    "span": "mountains",
    "many": "mountains",
    "eminent": "mountains",
    "tall": "mountains",
    "open_sea": "mountains",
    # Forests / trees
    "forest": "forests",
    "woods": "forests",
    "tree": "forests",
    "oak": "forests",
    "judas_tree": "forests",
    "paulownia_tree": "forests",
    "apricot": "forests",
    "peach_tree": "forests",
    "leaf": "forests",
    "reed": "forests",
    "wither": "forests",
    "crude": "forests",
    "obscure": "forests",
    "vague": "forests",
    # Rivers / lakes / water
    "river": "water",
    "large_river": "water",
    "creek": "water",
    "water": "water",
    "lake": "water",
    "tide": "water",
    "spring": "water",
    "source": "water",
    "ice": "water",
    "splash": "water",
    "cleanse": "water",
    "wash": "water",
    "fishing": "water",
    "fish": "water",
    "carp": "water",
    "whale": "water",
    "shellfish": "water",
    "grains_of_sand": "water",
    "sand": "water",
    "nitrate": "water",
    "eternity": "water",
    "gland": "water",
    "condition": "water",
    "lively": "water",
    # Shrines & temples
    "temple": "temples",
    "senso_ji_temple": "temples",
    "pagoda": "temples",
    "kyoto_pagoda": "temples",
    "chant": "temples",
    "old": "temples",
    "olden_times": "temples",
    "good_luck": "temples",
    "virtue": "temples",
    "pavilion": "temples",
    "haven": "temples",
    "study": "temples",
    "beginning": "temples",
    # Castles
    "castle_2": "castles",
    # Historic villages / rural
    "home_village": "villages",
    "village": "villages",
    "thatched_roof": "villages",
    "thatched_roof_winter": "villages",
    "farm": "villages",
    "meadow": "villages",
    "field": "villages",
    "den": "villages",
    # Kyoto / streets / towns
    "kyoto": "streets",
    "street": "streets",
    "town": "streets",
    "capital": "streets",
    "sapporo_clock": "streets",
    "car": "streets",
    "take_along": "streets",
    "in_front": "streets",
    "right": "streets",
    "below": "streets",
    "finish": "streets",
    "possible": "streets",
    "general": "streets",
    "previous": "streets",
    "dispose": "streets",
    # Tea houses / still life / intimate detail
    "tea": "still_life",
    "lamp": "still_life",
    "utensil": "still_life",
    "measuring_box": "still_life",
    "ladle": "still_life",
    "shelf": "still_life",
    "chair": "still_life",
    "ball": "still_life",
    "pearl": "still_life",
    "specialty": "still_life",
    "tool": "still_life",
    "hook": "still_life",
    "sword": "still_life",
    "bulls_eye": "still_life",
    "texture": "still_life",
    "inlay": "still_life",
    "letter": "still_life",
    "present": "still_life",
    "crown": "still_life",
    "exquisite": "still_life",
    "plump": "still_life",
    "thick": "still_life",
    "strange": "still_life",
    "flavor": "still_life",
    "imitation": "still_life",
    "metaphor": "still_life",
    "name": "still_life",
    "stone": "still_life",
    "cavity": "still_life",
    "small": "still_life",
    "round": "still_life",
    "white": "still_life",
    "fire": "still_life",
    "pop_song": "still_life",
    "fortune_telling": "still_life",
    "mediocre": "still_life",
    "stubborn": "still_life",
    "overcome": "still_life",
    "special": "still_life",
    "mutual": "still_life",
    "not_yet": "still_life",
    "extremity": "still_life",
    "follow": "still_life",
    "petition": "still_life",
    # Cherry blossoms / spring flourish
    "flourishing": "blossoms",
    "radiance": "blossoms",
    "sparkle": "blossoms",
    "shining": "blossoms",
    "illuminate": "blossoms",
    "ray": "blossoms",
    "ripe": "blossoms",
    "refreshing": "blossoms",
    "dream": "blossoms",
    "vermilion": "blossoms",
    # Autumn
    "nikko_fall_colors": "autumn",
    # Evening / night / tranquil light
    "evening": "evening",
    "eventide": "evening",
    "early_evening": "evening",
    "moon": "evening",
    "sun": "evening",
    "morning": "evening",
    "overnight": "evening",
    "emperor": "evening",
    # People (landscape remains subject — quiet supporting figures)
    "eye": "people",
    "woman": "people",
    "child": "people",
    "mother": "people",
    "older_brother": "people",
    "newborn": "people",
    "younger_sister": "people",
    "tongue": "people",
    "elbow": "people",
    "see": "people",
    "stare": "people",
    "likeness": "people",
    "resemblance": "people",
    "fond_of": "people",
    "vice": "people",
    "seduce": "people",
    "derision": "people",
    "dog": "people",
    "cat": "people",
    # Numbers / abstract opening accents → treat as still_life intimacy
    "one": "still_life",
    "four": "still_life",
    "five": "still_life",
    "six": "still_life",
    "seven": "still_life",
    "eight": "still_life",
    "nine": "still_life",
    "hundred": "still_life",
    "thousand": "still_life",
    "ten_thousand": "still_life",
    "ten_days": "still_life",
}

# Wide vs intimate — for alternating camera distance feel.
WIDE_CATEGORIES = frozenset(
    {
        "mountains",
        "forests",
        "water",
        "temples",
        "castles",
        "villages",
        "streets",
        "autumn",
        "blossoms",
        "evening",
    }
)
INTIMATE_CATEGORIES = frozenset({"still_life", "people"})

SIGNATURE_SLUGS = frozenset(
    {
        "mt_fuji_2",
        "castle_2",
        "senso_ji_temple",
        "kyoto",
        "kyoto_pagoda",
        "thatched_roof",
        "thatched_roof_winter",
        "sapporo_clock",
        "nikko_fall_colors",
        "temple",
        "pagoda",
        "home_village",
    }
)

# Closing arc: increasingly tranquil, categories alternating (no temple run).
# Prefer non-signature scenes so landmarks stay scattered through the body.
ENDING_PRIORITY = (
    "early_evening",
    "lake",
    "temple",
    "horizon",
    "evening",
    "water",
    "pagoda",
    "scenery",
    "eventide",
    "moon",  # final: night sky, held slightly longer
)

SCENIC_MOTION_BY_SLUG: dict[str, str] = {
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
    "scenery": "pull-out",
    "mt_fuji_2": "rise",
    "street": "drift-x",
    "town": "drift-x",
    "home_village": "drift-x",
    "village": "drift-x",
    "kyoto": "drift-x",
    "capital": "drift-x",
    "thatched_roof": "push-in",
    "thatched_roof_winter": "push-in",
    "sapporo_clock": "push-in",
    "temple": "push-in",
    "senso_ji_temple": "push-in",
    "pagoda": "rise",
    "kyoto_pagoda": "rise",
    "castle_2": "rise",
    "pavilion": "push-in",
    "old": "push-in",
    "olden_times": "push-in",
    "haven": "push-in",
    "river": "drift-x",
    "large_river": "drift-diagonal",
    "creek": "drift-diagonal",
    "water": "drift-x",
    "tide": "drift-x",
    "fishing": "drift-x",
    "spring": "push-in",
    "source": "push-in",
    "lake": "pull-out",
    "ice": "drift-diagonal",
    "cleanse": "drift-x",
    "eventide": "drift-y",
    "evening": "drift-y",
    "early_evening": "drift-y",
    "forest": "drift-diagonal",
    "woods": "drift-diagonal",
    "tree": "rise",
    "nikko_fall_colors": "drift-x",
    "rise": "rise",
    "rising_sun": "rise",
    "morning": "rise",
    "sun": "rise",
    "moon": "rise",
    "top": "rise",
    "up": "rise",
    "ray": "rise",
    "sparkle": "rise",
    "illuminate": "rise",
    "shining": "rise",
    "radiance": "rise",
    "lamp": "push-in",
    "overnight": "push-in",
    "den": "push-in",
    "tea": "push-in",
    "eye": "drift-x",
    "elbow": "push-in",
    "mother": "push-in",
    "child": "push-in",
    "woman": "push-in",
    "tongue": "push-in",
    "newborn": "push-in",
    "older_brother": "push-in",
    "fond_of": "push-in",
    "see": "push-in",
    "stare": "push-in",
    "likeness": "push-in",
    "resemblance": "push-in",
}

PEOPLE_SLUGS = frozenset(
    {
        "eye",
        "elbow",
        "mother",
        "child",
        "woman",
        "tongue",
        "newborn",
        "older_brother",
        "younger_sister",
        "fond_of",
        "see",
        "stare",
        "likeness",
        "resemblance",
        "vice",
        "seduce",
        "derision",
        "petition",
    }
)

EXCEPTIONAL_SLUGS = frozenset(
    {
        "river",
        "temple",
        "senso_ji_temple",
        "field",
        "lake",
        "morning",
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
        "eventide",
        "early_evening",
        "moon",
        "sun",
        "water",
        "spring",
        "fishing",
        "town",
        "street",
        "kyoto",
        "kyoto_pagoda",
        "mt_fuji_2",
        "castle_2",
        "nikko_fall_colors",
        "thatched_roof",
        "thatched_roof_winter",
        "forest",
        "scenery",
        "pagoda",
        "lamp",
        "plane",
        "sapporo_clock",
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


def scene_slug(scene: dict) -> str:
    return Path(scene["image"]).stem


def category_of(scene: dict) -> str:
    return scene.get("category") or CATEGORY_BY_SLUG.get(scene_slug(scene), "still_life")


def scale_of(scene: dict) -> str:
    cat = category_of(scene)
    if cat in INTIMATE_CATEGORIES:
        return "intimate"
    if cat in WIDE_CATEGORIES:
        return "wide"
    return "wide"


def normalize_playlist_line(line: str) -> str:
    raw = line.strip()
    if not raw:
        return ""
    if raw in PLAYLIST_ALIASES:
        return PLAYLIST_ALIASES[raw]
    if raw.endswith(".png"):
        raw = f"{raw[:-4]}.jpg"
    if raw.endswith((".jpg", ".jpeg", ".webp")):
        return raw
    return f"{raw}.jpg"


def load_playlist_filenames() -> list[str]:
    if not PLAYLIST_PATH.is_file():
        raise SystemExit(f"Missing playlist: {PLAYLIST_PATH}")
    names: list[str] = []
    seen: set[str] = set()
    for line in PLAYLIST_PATH.read_text(encoding="utf-8").splitlines():
        name = normalize_playlist_line(line)
        if not name:
            continue
        if name in seen:
            print(f"warn: duplicate playlist entry skipped: {name}", file=sys.stderr)
            continue
        seen.add(name)
        names.append(name)
    return names


def index_gallery_metadata() -> dict[str, dict]:
    """Index Heart + Lessons 1–20 gallery scenes by image stem."""
    by_stem: dict[str, dict] = {}

    heart_path = ROOT / "collections" / "heart_v5.json"
    if heart_path.is_file():
        heart = load_json(heart_path)
        for scene in heart.get("scenes") or []:
            image = scene.get("image")
            if not image:
                continue
            by_stem[Path(image).stem] = {
                "kanji": scene.get("kanji") or "",
                "keyword": scene.get("keyword") or "",
                "galleryCamera": dict(scene.get("galleryCamera") or {}),
                "imageScale": scene.get("imageScale"),
                "imageFocus": scene.get("imageFocus"),
                "source": "heart",
            }

    for lesson in range(1, 21):
        path = collection_json_path(ROOT, f"lesson_{lesson:02d}_gallery")
        if not path.is_file():
            continue
        doc = load_json(path)
        for scene in doc.get("scenes") or []:
            image = scene.get("image")
            if not image:
                continue
            stem = Path(image).stem
            if stem in by_stem:
                continue
            by_stem[stem] = {
                "kanji": scene.get("kanji") or "",
                "keyword": scene.get("keyword") or "",
                "galleryCamera": dict(scene.get("galleryCamera") or {}),
                "imageScale": scene.get("imageScale"),
                "imageFocus": scene.get("imageFocus"),
                "source": f"lesson_{lesson:02d}",
            }
    return by_stem


def collect_playlist_scenes() -> list[dict]:
    """Build scene dicts strictly from the revised playlist."""
    meta = index_gallery_metadata()
    scenes: list[dict] = []
    missing: list[str] = []

    for filename in load_playlist_filenames():
        relative = f"studies/{filename}"
        path = ASSETS / relative
        if not path.is_file():
            missing.append(filename)
            continue
        stem = Path(filename).stem
        info = meta.get(stem) or {}
        keyword = info.get("keyword") or stem.replace("_", " ")
        cat = CATEGORY_BY_SLUG.get(stem, "still_life")
        if stem not in CATEGORY_BY_SLUG:
            print(f"warn: uncategorized slug → still_life: {stem}", file=sys.stderr)
        scenes.append(
            {
                "id": f"ambient_{stem}",
                "kanji": info.get("kanji") or "",
                "keyword": keyword,
                "image": relative,
                "source": info.get("source") or "playlist",
                "category": cat,
                "galleryCamera": dict(info.get("galleryCamera") or {}),
                "imageScale": info.get("imageScale"),
                "imageFocus": info.get("imageFocus"),
                "signature": stem in SIGNATURE_SLUGS,
            }
        )

    if missing:
        raise SystemExit(
            "Playlist images missing from assets/studies:\n  "
            + "\n  ".join(missing)
        )
    return scenes


def pick_ending_scenes(scenes: list[dict], count: int = 10) -> list[dict]:
    """Select tranquil closing scenes in a calming progression."""
    by_slug = {scene_slug(s): s for s in scenes}
    chosen: list[dict] = []
    used: set[str] = set()
    for slug in ENDING_PRIORITY:
        if len(chosen) >= count:
            break
        scene = by_slug.get(slug)
        if scene is None or slug in used:
            continue
        chosen.append(scene)
        used.add(slug)
    # Prefer evening / water / mountains if still short.
    if len(chosen) < count:
        for scene in scenes:
            if len(chosen) >= count:
                break
            slug = scene_slug(scene)
            if slug in used:
                continue
            if category_of(scene) in {"evening", "water", "temples", "mountains"}:
                chosen.append(scene)
                used.add(slug)
    return chosen


def score_candidate(
    scene: dict,
    *,
    prev_cats: list[str],
    prev_scale: str | None,
    recent_signatures: int,
    want_signature_gap: bool,
    remaining_by_cat: dict[str, int],
) -> float:
    """Higher is better. Penalize category / scale / signature clustering."""
    cat = category_of(scene)
    scale = scale_of(scene)
    score = 10.0

    if prev_cats and cat == prev_cats[-1]:
        score -= 100.0
    if len(prev_cats) >= 2 and cat == prev_cats[-2]:
        score -= 40.0
    if cat in prev_cats[-3:]:
        score -= 12.0
    # Extra pressure against still_life runs (largest bucket).
    if cat == "still_life" and prev_cats and prev_cats[-1] == "still_life":
        score -= 40.0

    if prev_scale and scale == prev_scale:
        score -= 8.0
    else:
        score += 6.0

    if scene.get("signature"):
        if recent_signatures > 0 or want_signature_gap:
            score -= 50.0
        else:
            score += 4.0

    # Prefer drawing from categories that still have more remaining (spread load).
    # But never prefer same-as-previous.
    rem = remaining_by_cat.get(cat, 0)
    total_rem = max(1, sum(remaining_by_cat.values()))
    # Invert: rarer categories get a small boost so they don't pile at the end.
    rarity = 1.0 - (rem / total_rem)
    score += rarity * 8.0
    # Pressure valve: if still_life dominates the remaining pool, draw it now
    # (unless it would repeat the previous category).
    still_rem = remaining_by_cat.get("still_life", 0)
    if (
        cat == "still_life"
        and still_rem / total_rem > 0.42
        and (not prev_cats or prev_cats[-1] != "still_life")
    ):
        score += 35.0
    if (
        cat != "still_life"
        and still_rem / total_rem > 0.42
        and prev_cats
        and prev_cats[-1] != "still_life"
    ):
        score -= 15.0

    # Soft preference: after wide landscape, intimate detail; after temple, forest/water.
    if prev_cats:
        last = prev_cats[-1]
        prefer = {
            "mountains": {"still_life", "villages", "temples", "water"},
            "forests": {"water", "villages", "still_life", "temples"},
            "water": {"temples", "forests", "villages", "mountains"},
            "temples": {"forests", "water", "streets", "still_life"},
            "castles": {"mountains", "water", "forests", "streets"},
            "villages": {"temples", "forests", "streets", "still_life"},
            "streets": {"mountains", "temples", "water", "still_life"},
            "still_life": {"mountains", "forests", "water", "villages", "streets"},
            "people": {"mountains", "forests", "water", "temples"},
            "blossoms": {"villages", "temples", "still_life"},
            "autumn": {"water", "temples", "mountains"},
            "evening": {"water", "temples", "mountains", "still_life"},
        }.get(last, set())
        if cat in prefer:
            score += 5.0

    return score


def interleave_by_category(
    scenes: list[dict],
    rng: random.Random,
    *,
    ending_count: int = 10,
) -> list[dict]:
    """Interleave categories; scatter signatures; finish with tranquil arc."""
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
    prev_scale: str | None = None
    since_signature = 99
    # Aim to space signatures ~every 14–22 scenes.
    signature_gap_target = rng.randint(14, 22)

    while any(buckets.values()):
        candidates = [b[0] for b in buckets.values() if b]
        if not candidates:
            break
        want_gap = since_signature < signature_gap_target
        remaining_by_cat = {k: len(v) for k, v in buckets.items()}
        scored = [
            (
                score_candidate(
                    c,
                    prev_cats=prev_cats,
                    prev_scale=prev_scale,
                    recent_signatures=max(0, signature_gap_target - since_signature),
                    want_signature_gap=want_gap,
                    remaining_by_cat=remaining_by_cat,
                )
                + rng.random() * 1.5,
                c,
            )
            for c in candidates
        ]
        scored.sort(key=lambda t: t[0], reverse=True)
        # Hard rule: never pick same category as previous if any alternative exists.
        chosen = None
        last_cat = prev_cats[-1] if prev_cats else None
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
        prev_scale = scale_of(chosen)
        if chosen.get("signature"):
            since_signature = 0
            signature_gap_target = rng.randint(14, 22)
        else:
            since_signature += 1

    # Append tranquil ending (preserve calming priority order).
    ordered.extend(ending)
    return ordered


def preferred_motion(scene: dict) -> str | None:
    slug = scene_slug(scene)
    if slug in SCENIC_MOTION_BY_SLUG:
        return SCENIC_MOTION_BY_SLUG[slug]
    cam = scene.get("galleryCamera") or {}
    preferred = cam.get("motion")
    return preferred if preferred in MOTIONS else None


def assign_motions(scenes: list[dict], rng: random.Random) -> None:
    prev = None
    for scene in scenes:
        slug = scene_slug(scene)
        preferred = preferred_motion(scene)
        choices = [m for m in MOTIONS if m != prev]
        if preferred in choices and rng.random() < 0.78:
            motion = preferred
        elif preferred == prev and preferred is not None:
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
    n = len(scenes)
    if n <= 0:
        return []
    avg = budget_ms / n
    if avg < HOLD_MIN_MS:
        return [max(HOLD_MIN_MS, int(avg))] * n
    if avg > HOLD_MAX_MS:
        return [min(HOLD_EXCEPTIONAL_MS, int(avg))] * n

    holds: list[int] = []
    for i, scene in enumerate(scenes):
        slug = scene_slug(scene)
        roll = rng.random()
        if i == n - 1:
            holds.append(HOLD_FINAL_MS)
        elif slug in EXCEPTIONAL_SLUGS and roll < 0.55:
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
    # Keep final image slightly longer when possible.
    if scaled[-1] < HOLD_FINAL_MS and HOLD_FINAL_MS <= HOLD_EXCEPTIONAL_MS:
        need = HOLD_FINAL_MS - scaled[-1]
        for i in range(n - 2, -1, -1):
            if need <= 0:
                break
            give = min(need, scaled[i] - HOLD_MIN_MS)
            if give > 0:
                scaled[i] -= give
                scaled[-1] += give
                need -= give

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
            "category": raw.get("category"),
            "signature": bool(raw.get("signature")),
            "ambientGalleryFilm": True,
            "ambientMove": "revised",
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
    sources = collect_playlist_scenes()
    if not sources:
        raise SystemExit("Playlist produced no scenes")

    mixed = interleave_by_category(sources, rng, ending_count=10)
    assign_motions(mixed, rng)

    n = len(mixed)
    transitions = max(0, n - 1) * TRANSITION_MS
    hold_budget = soundtrack_ms - transitions
    if hold_budget < n * HOLD_MIN_MS:
        max_scenes = max(1, hold_budget // HOLD_MIN_MS)
        # Prefer dropping from middle of body, keep ending intact.
        ending = mixed[-10:] if n > 10 else []
        body = mixed[:-10] if n > 10 else mixed
        keep_body = max(0, max_scenes - len(ending))
        mixed = body[:keep_body] + ending
        n = len(mixed)
        transitions = max(0, n - 1) * TRANSITION_MS
        hold_budget = soundtrack_ms - transitions

    holds = distribute_holds(mixed, hold_budget, rng)
    scenes = [build_scene_payload(raw, hold) for raw, hold in zip(mixed, holds)]
    avg_hold = sum(holds) / n
    max_run, max_run_cat = max_same_category_run(mixed)
    cat_counts: dict[str, int] = defaultdict(int)
    for s in mixed:
        cat_counts[category_of(s)] += 1

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
        "title": "Ambient Movie — Lessons 1–20 (Ambient Revised)",
        "notes": (
            "Ambient Revised: playlist-curated textless journey through timeless Japan "
            "(Lessons 1–20 gallery art + signature landmarks). Category-interleaved "
            "Ken Burns, 35–45s holds (exceptional up to 60s), tranquil closing arc, "
            f"silent gold crest after soundtrack "
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
            "ambientMove": "revised",
        },
        "meta": {
            "family": "ambientGalleryFilm",
            "ambientMove": "revised",
            "edition": "Lessons 1–20 (Ambient Revised)",
            "sceneCount": n,
            "soundtrackDurationMs": soundtrack_ms,
            "playlist": "collections/ambient_gallery_film/ambient_movie_revised.txt",
            "seed": SEED,
            "avgHoldMs": int(avg_hold),
            "holdMinMs": min(holds),
            "holdMaxMs": max(holds),
            "cameraMotionScale": CAMERA_MOTION_SCALE,
            "maxSameCategoryRun": max_run,
            "maxSameCategory": max_run_cat,
            "categoryCounts": dict(sorted(cat_counts.items())),
            "endingSlugs": [scene_slug(s) for s in mixed[-10:]],
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    meta = config["meta"]
    print(
        f"Wrote {meta['sceneCount']} exhibits → {OUT_PATH}\n"
        f"  edition: {meta['edition']}\n"
        f"  soundtrack {meta['soundtrackDurationMs'] / 60000:.1f} min\n"
        f"  holds {meta['holdMinMs'] / 1000:.1f}–{meta['holdMaxMs'] / 1000:.1f}s "
        f"(avg {meta['avgHoldMs'] / 1000:.1f}s)\n"
        f"  max same-category run: {meta['maxSameCategoryRun']} "
        f"({meta['maxSameCategory']})\n"
        f"  ending: {' → '.join(meta['endingSlugs'])}\n"
        f"  categories: {meta['categoryCounts']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
