#!/usr/bin/env python3
"""Build Ambient Japan 4h playback-prototype exhibition JSON.

Uses the approved 142-image playback_sequence.json order without changes.
This prototype is a consecutive slice (001–012) at the final 4-hour hold
so the viewing rhythm and render pipeline can be approved before the full film.

Do not render the full four-hour movie from this script.
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
SCENERY = ROOT / "collections" / "ambient_japan_4h_scenery"
SEQ_PATH = SCENERY / "playback_sequence.json"
CANDIDATES_PATH = SCENERY / "candidates.json"
START_HERE_LINK = ASSETS / "start_here"
START_HERE_TARGET = REPO.parents[0] / "start-here" / "assets" / "images"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collection_paths import write_collection_path  # noqa: E402

COLLECTION_ID = "ambient_japan_4h_prototype"
OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)

SOUNDTRACK = "audio/ambient_japan_4_seasons.mp3"
SEED = 20260827

# Consecutive approved-sequence slice. Opening stretch mixes landscape,
# village architecture, a station, old streets/shops, and a person.
# Not chosen for easy transitions.
PROTO_START = 1  # 001-based
PROTO_COUNT = 12

FULL_IMAGE_COUNT = 142
TARGET_CONTENT_MS = 4 * 60 * 60 * 1000  # 4:00:00 picture journey
TRANSITION_MS = 2_500
ARRIVAL_FADE_MS = 2_500
CLOSING_REVEAL_MS = 5_000
CLOSING_HOLD_MS = 7_000
CLOSING_FADE_MS = 12_000
CLOSING_BLACK_AFTER_MS = 2_000
CAMERA_MOTION_SCALE = 2.5
PEOPLE_MOTION_SCALE = 1.15

MOTIONS = (
    "push-in",
    "pull-out",
    "drift-x",
    "drift-y",
    "drift-diagonal",
    "rise",
)

PEOPLE_SLUGS = frozenset(
    {
        "younger_sister",
        "visit_shrine",
        "lesson_40/kazega_yowai",
        "lesson_40/genki_desuka",
        "dog",
        "nara_deer",
    }
)

SILENT_CREST_BOOKENDS = {
    "mode": "silentCrest",
    "closing": {
        "image": "images/gold_closing.png",
        "bookendSize": "small",
        # Prototype pictures are ~20 min; the master bed is ~120 min.
        # Do not hold the last image until the unused remainder of the bed
        # ends. The full 4h film will set this true once audio is looped
        # to cover the picture journey.
        "silentAfterSoundtrack": False,
        "holdUntilSoundtrackEnds": False,
    },
}


def soundtrack_duration_ms(rel: str) -> int:
    path = ROOT / rel
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        text=True,
    ).strip()
    return int(float(out) * 1000)


def ensure_start_here_link() -> None:
    if not START_HERE_TARGET.is_dir():
        raise SystemExit(f"Missing Start Here images: {START_HERE_TARGET}")
    if START_HERE_LINK.is_symlink():
        if START_HERE_LINK.resolve() == START_HERE_TARGET.resolve():
            return
        START_HERE_LINK.unlink()
    elif START_HERE_LINK.exists():
        return
    START_HERE_LINK.symlink_to(START_HERE_TARGET)


def exhibition_image(src: Path) -> str:
    """Map a source file to an assetsBase-relative exhibition path."""
    src = src.resolve()
    studies = (ASSETS / "studies").resolve()
    four = (ASSETS / "ambient_japan_4_seasons").resolve()
    start = START_HERE_TARGET.resolve()
    try:
        return (Path("studies") / src.relative_to(studies)).as_posix()
    except ValueError:
        pass
    try:
        return (Path("ambient_japan_4_seasons") / src.relative_to(four)).as_posix()
    except ValueError:
        pass
    try:
        return (Path("start_here") / src.relative_to(start)).as_posix()
    except ValueError:
        pass
    raise SystemExit(f"Cannot map exhibition image path: {src}")


def image_rev(relative: str) -> int | None:
    path = ASSETS / relative
    if path.is_file():
        return int(path.stat().st_mtime)
    return None


def hold_ms_for_count(n: int) -> int:
    """Per-image hold so arrival + holds + (n-1) crossfades = 4:00:00 for 142 images."""
    transitions = max(0, FULL_IMAGE_COUNT - 1) * TRANSITION_MS
    hold_budget = TARGET_CONTENT_MS - ARRIVAL_FADE_MS - transitions
    return hold_budget // FULL_IMAGE_COUNT


def assign_motions(stems: list[str], rng: random.Random) -> list[dict]:
    prev = None
    cameras = []
    for stem in stems:
        choices = [m for m in MOTIONS if m != prev] or list(MOTIONS)
        motion = rng.choice(choices)
        cam = {"motion": motion}
        if stem in PEOPLE_SLUGS:
            cam["motionScale"] = PEOPLE_MOTION_SCALE
        cameras.append(cam)
        prev = motion
    return cameras


def load_sequence() -> list[dict]:
    seq = json.loads(SEQ_PATH.read_text(encoding="utf-8"))
    cand = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
    rel_by_stem = {rec["stem"]: rec["rel"] for rec in cand["corePool"]}
    items = []
    for rec in seq["sequence"]:
        stem = rec["stem"]
        src = (SCENERY / rel_by_stem[stem]).resolve()
        if not src.is_file():
            raise SystemExit(f"Missing source image for {stem}: {src}")
        items.append({"n": rec["n"], "id": rec["id"], "stem": stem, "src": src})
    if len(items) != FULL_IMAGE_COUNT:
        raise SystemExit(f"Expected {FULL_IMAGE_COUNT} sequence items, got {len(items)}")
    return items


def picture_runtime_ms(n: int, hold_ms: int) -> int:
    return ARRIVAL_FADE_MS + n * hold_ms + max(0, n - 1) * TRANSITION_MS


def closing_ms() -> int:
    return CLOSING_REVEAL_MS + CLOSING_HOLD_MS + CLOSING_FADE_MS + CLOSING_BLACK_AFTER_MS


def build() -> dict:
    ensure_start_here_link()
    items = load_sequence()
    rng = random.Random(SEED)
    cameras = assign_motions([it["stem"] for it in items], rng)
    hold_ms = hold_ms_for_count(FULL_IMAGE_COUNT)

    start = PROTO_START - 1
    slice_items = items[start : start + PROTO_COUNT]
    if len(slice_items) != PROTO_COUNT:
        raise SystemExit("Prototype slice is short")

    scenes = []
    for it, cam in zip(slice_items, cameras[start : start + PROTO_COUNT]):
        image = exhibition_image(it["src"])
        if not (ASSETS / image).is_file():
            raise SystemExit(f"Exhibition asset missing: {image}")
        keyword = it["stem"].replace("_", " ").replace("/", " / ")
        scene = {
            "id": f"ambient_japan_4h_{it['id']}",
            "kanji": "",
            "keyword": keyword,
            "image": image,
            "galleryCamera": cam,
            "artworkAloneMs": hold_ms,
            "verse": {"jpHtml": "", "en": ""},
            "meta": {
                "source": "ambient_japan_4h",
                "sequenceIndex": it["n"],
                "sequenceId": it["id"],
                "slug": it["stem"],
            },
        }
        rev = image_rev(image)
        if rev is not None:
            scene["imageRev"] = rev
        scenes.append(scene)

    n = len(scenes)
    proto_picture_ms = picture_runtime_ms(n, hold_ms)
    full_picture_ms = picture_runtime_ms(FULL_IMAGE_COUNT, hold_ms)
    soundtrack_ms = soundtrack_duration_ms(SOUNDTRACK)

    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": COLLECTION_ID,
        "title": "Ambient Japan 4h — playback prototype",
        "notes": (
            f"Approved sequence {slice_items[0]['id']}–{slice_items[-1]['id']} "
            f"at final 4-hour holds ({hold_ms / 1000:.3f}s). Same exhibition "
            f"pipeline as Four Seasons / Ambient Movies. Prototype only — "
            f"do not use this JSON to render the full film."
        ),
        "soundtrack": {"main": SOUNDTRACK},
        "bookends": dict(SILENT_CREST_BOOKENDS),
        "exhibition": {
            "artworkArrivalMs": 0,
            "artworkArrivalFadeMs": ARRIVAL_FADE_MS,
            "exhibitionBlackBeforeMs": 0,
            "artworkAloneMs": hold_ms,
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
            "kenBurnsDurationMs": hold_ms + TRANSITION_MS,
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
            "ambientMove": "v2",
            "cameraMotionScale": CAMERA_MOTION_SCALE,
        },
        "meta": {
            "family": "ambientGalleryJapan",
            "edition": "Ambient Japan 4h prototype",
            "sequenceSource": "collections/ambient_japan_4h_scenery/playback_sequence.json",
            "prototypeSlice": {
                "start": slice_items[0]["id"],
                "end": slice_items[-1]["id"],
                "stems": [it["stem"] for it in slice_items],
            },
            "sceneCount": n,
            "fullImageCount": FULL_IMAGE_COUNT,
            "holdMs": hold_ms,
            "transitionMs": TRANSITION_MS,
            "arrivalFadeMs": ARRIVAL_FADE_MS,
            "cameraMotionScale": CAMERA_MOTION_SCALE,
            "peopleMotionScale": PEOPLE_MOTION_SCALE,
            "seed": SEED,
            "soundtrackDurationMs": soundtrack_ms,
            "soundtrackPlan": (
                "Loop ambient_japan_4_seasons.mp3 once with a long crossfade "
                "to cover the 4-hour picture journey. Prototype uses the "
                "opening of the same bed; no new audio file."
            ),
            "prototypePictureRuntimeMs": proto_picture_ms,
            "prototypeClosingMs": closing_ms(),
            "estimatedContentRuntimeMs": proto_picture_ms + closing_ms(),
            "fullPictureRuntimeMs": full_picture_ms,
            "fullEstimatedRuntimeMs": full_picture_ms + closing_ms(),
            "viewport": {"width": 1920, "height": 1080, "frameRate": 25},
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    meta = config["meta"]
    print(f"wrote {OUT_PATH}")
    print(f"  slice: {meta['prototypeSlice']['start']}–{meta['prototypeSlice']['end']}")
    print(f"  hold: {meta['holdMs']} ms ({meta['holdMs'] / 1000:.3f}s)")
    print(f"  transition: {meta['transitionMs']} ms")
    print(
        f"  prototype pictures: {meta['prototypePictureRuntimeMs'] / 1000:.1f}s · "
        f"with crest {meta['estimatedContentRuntimeMs'] / 1000:.1f}s"
    )
    print(
        f"  full 142 pictures: {meta['fullPictureRuntimeMs'] / 1000 / 60:.2f} min · "
        f"with crest {meta['fullEstimatedRuntimeMs'] / 1000 / 60:.2f} min"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
