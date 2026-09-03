#!/usr/bin/env python3
"""Build the curated 女・子 exhibition (Video #500).

Ten existing paintings. Heart v5 choreography with more time on the artwork.
Gold-foil Lesson 6 好 cover as gallery crest. Soundtrack:
audio/mother_child_exhibition.mp3.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT.parents[1] / "contents" / "books" / "book_01" / "lessons"
REPO_ASSETS = ROOT.parents[1] / "assets" / "studies"
COVERS = ROOT.parents[1] / "assets" / "covers"
OUT_PATH = ROOT / "collections" / "woman_child_exhibition.json"
HEART_V5 = ROOT / "collections" / "heart_v5.json"
BOOKEND_IMAGE = "bookends/lesson_06.jpg"
FLUTE_AUDIO = "audio/exhibition_flute_intro.mp3"
SOUNDTRACK = "audio/mother_child_exhibition.mp3"

# Visual / emotional hang — not lesson order, not a primitive dump.
EXHIBITS = [
    (6, "woman", "element"),
    (5, "child", "element"),
    (6, "fond_of", "hinge"),
    (12, "younger_sister", "kinship"),
    (23, "older_sister", "kinship"),
    (11, "relax", "sanctuary"),
    (28, "pregnancy", "becoming"),
    (40, "milk", "nourishment"),
    (44, "old_woman", "generations"),
    (6, "mother", "resolution"),
]


def load_scene(lesson_num: int, slug: str) -> dict:
    path = LESSONS_DIR / f"lesson_{lesson_num:02d}.html"
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    for section in re.split(r'<section class="kanji-entry"', text)[1:]:
        slug_m = re.search(r'data-slug="([^"]+)"', section)
        if not slug_m or slug_m.group(1) != slug:
            continue
        kanji_m = re.search(r'data-kanji="([^"]+)"', section)
        keyword_m = re.search(r'<span class="kanji-keyword">([^<]+)</span>', section)
        img_m = re.search(r"assets/studies/([^\"?]+\.jpg)", section)
        jp_m = re.search(r'<p class="jp-verse[^"]*">(.*?)</p>', section, re.DOTALL)
        en_m = re.search(r'<p class="en-verse">(.*?)</p>', section, re.DOTALL)
        if not (kanji_m and keyword_m and img_m and jp_m and en_m):
            raise ValueError(f"Incomplete lesson HTML for L{lesson_num:02d} {slug}")
        image_file = img_m.group(1).split("/")[-1]
        image_path = REPO_ASSETS / image_file
        if not image_path.is_file():
            raise FileNotFoundError(image_path)
        en_text = re.sub(r"<br\s*/?>", "\n", en_m.group(1)).strip()
        en_text = re.sub(r"<[^>]+>", "", en_text)
        scene = {
            "id": f"L{lesson_num:02d}_{slug}",
            "lesson": lesson_num,
            "kanji": kanji_m.group(1),
            "keyword": keyword_m.group(1),
            "image": f"studies/{image_file}",
            "video": None,
            "verse": {"jpHtml": jp_m.group(1).strip(), "en": en_text},
            "imageRev": int(image_path.stat().st_mtime),
        }
        return scene
    raise KeyError(f"No section slug={slug!r} in {path.name}")


def exhibition_timing(heart_timing: dict) -> dict:
    """Heart v5 dissolves and handoffs; longer holds so 10 works can breathe."""
    return {
        **heart_timing,
        "artworkAloneMs": 20000,
        "titleHoldMs": 10000,
        "essenceHoldMs": 18000,
        "reflectionHoldMs": 14000,
        "verseEnDelayMs": 10000,
    }


def print_runtime(collection: dict) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from calc_heart_sequential_timing import (  # noqa: E402
        engine_exhibits_ms,
        exhibit_body_ms,
        gallery_bridge_ms,
    )

    t = collection["exhibition"]
    sequential = (collection.get("display") or {}).get("verseMode") == "sequential"
    n = len(collection["scenes"])
    body = exhibit_body_ms(t, sequential=sequential)
    bridge = gallery_bridge_ms(t)
    exhibits = engine_exhibits_ms(t, n, sequential=sequential)

    import subprocess

    flute_path = ROOT / FLUTE_AUDIO
    flute_ms = 34700
    try:
        if flute_path.is_file():
            out = subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "csv=p=0",
                    str(flute_path),
                ],
                text=True,
            )
            flute_ms = int(float(out.strip()) * 1000)
    except (OSError, subprocess.CalledProcessError, ValueError):
        pass

    opening = (
        t["openingBlackBeforeMs"]
        + flute_ms
        + t["openingExhaleMs"]
        + t.get("openingBlackAfterMs", 0)
    )
    closing_before = t.get("closingBlackBeforeMs", 0) + t["closingRevealMs"]
    soundtrack_ms = exhibits + closing_before
    film_ms = (
        opening
        + exhibits
        + closing_before
        + t.get("closingExhaleMs", 0)
        + t.get("closingFadeToBlackMs", 0)
        + t.get("closingBlackAfterMs", 0)
    )

    later = t["artworkAloneMs"] + body + bridge
    soundtrack_path = ROOT / SOUNDTRACK
    soundtrack_s = None
    try:
        if soundtrack_path.is_file():
            out = subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "csv=p=0",
                    str(soundtrack_path),
                ],
                text=True,
            )
            soundtrack_s = float(out.strip())
    except (OSError, subprocess.CalledProcessError, ValueError):
        soundtrack_s = None

    print()
    print("Runtime (engine-accurate)")
    print(f"  Exhibit body: {body / 1000:.1f}s  (Heart v5 was 89.0s)")
    print(f"  Artwork alone before kanji: {t['artworkAloneMs'] / 1000:.0f}s  (Heart v5 was 6s)")
    print(f"  Later exhibit: {later / 1000:.1f}s  (Heart v5 was 133s)")
    print(f"  Opening (flute crest, pre-soundtrack): {opening / 1000:.1f}s")
    print(f"  {n} exhibits: {exhibits / 60000:.2f} min")
    print(f"  Visuals to closing-crest wait: {soundtrack_ms / 60000:.2f} min")
    if soundtrack_s is not None:
        gap_s = soundtrack_ms / 1000 - soundtrack_s
        m, sec = divmod(soundtrack_s, 60)
        print(f"  Soundtrack {SOUNDTRACK}: {int(m)}:{sec:05.2f} ({soundtrack_s / 60:.2f} min)")
        if gap_s > 1:
            print(f"  Visuals reach closing ~{gap_s:.0f}s before music ends.")
        elif gap_s < -5:
            print(f"  Closing 好 crest holds ~{-gap_s:.0f}s on remaining music, then fades.")
        else:
            print("  Sync OK (music and closing crest align within a few seconds).")
        film_with_hold_ms = (
            opening
            + max(soundtrack_ms, int(soundtrack_s * 1000))
            + t.get("closingBlackAfterMs", 0)
        )
        print(f"  Total film: {film_with_hold_ms / 60000:.2f} min")
    else:
        print(f"  Total film (incl. crest fade): {film_ms / 60000:.2f} min")
        print(f"  Missing soundtrack: {soundtrack_path}")


def ensure_bookend() -> None:
    bookends = ROOT / "bookends"
    bookends.mkdir(exist_ok=True)
    dest = bookends / "lesson_06.jpg"
    src = COVERS / "lesson_06.jpg"
    if not src.is_file():
        raise FileNotFoundError(src)
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    dest.symlink_to(Path("../../../assets/covers/lesson_06.jpg"))


def build() -> dict:
    heart_v5 = json.loads(HEART_V5.read_text(encoding="utf-8"))
    scenes = []
    roles = {}
    for lesson_num, slug, role in EXHIBITS:
        scene = load_scene(lesson_num, slug)
        scene["role"] = role
        scenes.append(scene)
        roles[scene["id"]] = role

    ensure_bookend()

    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": "woman_child_exhibition",
        "title": "女・子 — Woman & Child | A Quiet Japanese Art Exhibition",
        "notes": (
            "Curated 10-work gallery. Gold-foil Lesson 6 好 crest opens and closes. "
            "好 is the hinge (exhibit 3); 母 resolves last. Heart v5 choreography with "
            "longer artwork/verse holds. Soundtrack: audio/mother_child_exhibition.mp3."
        ),
        "soundtrack": {"main": SOUNDTRACK},
        "bookends": {
            "opening": {
                "image": BOOKEND_IMAGE,
                "audio": FLUTE_AUDIO,
                "holdUntilAudioEnds": True,
            },
            "closing": {
                "image": BOOKEND_IMAGE,
                "holdUntilSoundtrackEnds": True,
            },
        },
        "exhibition": exhibition_timing(heart_v5["exhibition"]),
        "display": {
            "loop": False,
            "hideChrome": True,
            "fixedKanji": True,
            "showKeyword": True,
            "verseMode": "sequential",
            "typography": "mobile-refine",
            "typographyStyle": "foundations",
            "camera": "guardian",
        },
        "meta": {
            "theme": "womanChild",
            "family": "ambientKanjiGallery",
            "presentation": "exhibition",
            "fixedKanji": True,
            "bookendArtwork": BOOKEND_IMAGE,
            "sourcePaintings": "existing studies only; no new generation",
            "sceneCount": len(scenes),
            "sceneOrder": (
                "女 → 子 → 好 (hinge) → 妹 → 姉 → 安 → 妊 → 乳 → 婆 → 母 (resolution)"
            ),
            "sceneRoles": roles,
            "publicTitle": "女・子 — Woman & Child | A Quiet Japanese Art Exhibition",
        },
        "scenes": scenes,
    }


def main() -> int:
    config = build()
    OUT_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(config['scenes'])} scenes → {OUT_PATH}")
    print(f"  Crest: {BOOKEND_IMAGE}")
    print(f"  Preview: exhibition.html?collection=woman_child_exhibition")
    for i, scene in enumerate(config["scenes"], 1):
        print(
            f"  {i:2d}. {scene['kanji']}  {scene['keyword']:<16} "
            f"{scene['image']}  ({scene['role']})"
        )
    print_runtime(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
