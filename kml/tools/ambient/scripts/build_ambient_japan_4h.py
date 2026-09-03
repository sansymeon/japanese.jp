#!/usr/bin/env python3
"""Build Ambient Japan 4h exhibition JSON — full approved 142-image sequence.

Same holds, crossfades, and Ken Burns seed as the playback prototype.
Soundtrack: audio/ambient_four_hour.mp3 (~4:00:00). No image add/remove/reorder.
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

COLLECTION_ID = "ambient_japan_4h"
OUT_PATH = write_collection_path(ROOT, COLLECTION_ID)

SOUNDTRACK = "audio/ambient_four_hour.mp3"
SEED = 20260827

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
        # Pictures fill ~4:00:00; the master is ~4:00:00. Crest after last image.
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

    scenes = []
    for it, cam in zip(items, cameras):
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
    picture_ms = picture_runtime_ms(n, hold_ms)
    soundtrack_ms = soundtrack_duration_ms(SOUNDTRACK)

    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": COLLECTION_ID,
        "title": "Ambient Japan 4h",
        "notes": (
            f"Approved 142-image sequence at {hold_ms / 1000:.3f}s holds. "
            f"Soundtrack {SOUNDTRACK}."
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
            "edition": "Ambient Japan 4h",
            "sequenceSource": "collections/ambient_japan_4h_scenery/playback_sequence.json",
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
                "ambient_four_hour.mp3 covers the picture journey (~4:00:00). "
                "No loop; mux trims/pads to video and fades 8s at the end."
            ),
            "pictureRuntimeMs": picture_ms,
            "closingMs": closing_ms(),
            "estimatedContentRuntimeMs": picture_ms + closing_ms(),
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
    print(f"  scenes: {meta['sceneCount']}")
    print(f"  hold: {meta['holdMs']} ms ({meta['holdMs'] / 1000:.3f}s)")
    print(f"  soundtrack: {SOUNDTRACK} ({meta['soundtrackDurationMs'] / 1000:.3f}s)")
    print(
        f"  pictures: {meta['pictureRuntimeMs'] / 1000 / 60:.2f} min · "
        f"with crest {meta['estimatedContentRuntimeMs'] / 1000 / 60:.2f} min"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
