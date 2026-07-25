#!/usr/bin/env python3
"""Build the dense-kanji glow stress-test data + exhibition collection.

Picks the densest glyphs from kanji_master.csv (plus 靈 / 驫, which the user
asked for but which are not in the master file) and writes:

  collections/prototypes/proto_glow_stress.json   — exhibition collection
  collections/prototypes/glow_stress_kanji.json   — board data for glow-stress.html

  python3 scripts/build_prototype_glow_stress.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT.parents[1] / "data" / "kanji" / "kanji_master.csv"
OUT_DIR = ROOT / "collections" / "prototypes"

SOUNDTRACK = "audio/12_minutes_minus3db.mp3"
STEP_MS = 12_000  # shorter than Beyond Jōyō — this is a visual stress test
OPEN_MS = 800 + 1200 + 2000
REVIEW_MS = 8_000
FINAL_FADE_MS = 3_000

# Requested by name even when absent from the master CSV.
EXTRAS = [
    {
        "kanji": "靈",
        "strokes": 24,
        "keyword": "spirit (kyūjitai)",
        "on_reading": "レイ",
        "slug": "spirit_kyu",
        "source": "requested",
    },
    {
        "kanji": "驫",
        "strokes": 30,
        "keyword": "three horses",
        "on_reading": "ヒョウ",
        "slug": "three_horses",
        "source": "requested",
    },
]

# Near-duplicate of 鬱 — skip so the board stays diverse.
SKIP = {"欝"}


def load_dense(limit: int = 18) -> list[dict]:
    rows = list(csv.DictReader(MASTER.open(encoding="utf-8")))

    def strokes(r: dict) -> int:
        try:
            return int(r["strokes"])
        except (TypeError, ValueError):
            return 0

    picked: list[dict] = []
    for r in sorted(rows, key=strokes, reverse=True):
        if r["kanji"] in SKIP:
            continue
        if strokes(r) < 22:
            continue
        keyword = (
            (r.get("display_keyword") or "").strip()
            or (r.get("keyword") or "").replace("_", " ").strip()
            or (r.get("slug") or "").replace("_", " ").strip()
        )
        picked.append(
            {
                "kanji": r["kanji"],
                "strokes": strokes(r),
                "keyword": keyword,
                "on_reading": r.get("on_reading") or "",
                "slug": r.get("slug") or r["kanji"],
                "source": "kanji_master",
                "category": r.get("category") or "",
            }
        )
        if len(picked) >= limit:
            break

    have = {p["kanji"] for p in picked}
    for extra in EXTRAS:
        if extra["kanji"] not in have:
            picked.append(dict(extra))
    return picked


def exhibition_for(kanji_list: list[dict]) -> dict:
    steps = []
    for i, k in enumerate(kanji_list, start=1):
        reading = k["on_reading"] or ""
        en = k["keyword"] or f"{k['strokes']} strokes"
        jp_html = (
            f"<ruby>{k['kanji']}<rt>{reading}</rt></ruby>" if reading else k["kanji"]
        )
        steps.append(
            {
                "jp": k["kanji"],
                "reading": reading.lower() if reading and reading.isascii() else reading,
                "en": f"{en} · {k['strokes']} strokes",
                "jpHtml": jp_html,
                "meta": {
                    "kanji": k["kanji"],
                    "strokes": k["strokes"],
                    "slug": k["slug"],
                    "displayOrder": i,
                },
            }
        )

    # Shorter timing — isolate the glyph, not the furigana choreography.
    exhibition = {
        "artworkArrivalMs": 0,
        "artworkArrivalFadeMs": 1200,
        "artworkAloneMs": 0,
        "exhibitionBlackBeforeMs": 800,
        "compoundsPauseBeforeMs": 2000,
        "compoundsStepRevealMs": 1000,
        "compoundsFuriganaEnterDelayMs": 400,
        "compoundsFuriganaEnterMs": 1200,
        "compoundsFuriganaHoldMs": 1600,
        "compoundsFuriganaFadeMs": 1000,
        "compoundsNativeHoldMs": 2200,
        "compoundsReadingRevealMs": 800,
        "compoundsReadingHoldMs": 1000,
        "compoundsEnRevealMs": 800,
        "compoundsEnHoldMs": 2000,
        "compoundsEnFadeMs": 800,
        "compoundsStepFadeMs": 1000,
        "compoundsFinalReviewHoldMs": REVIEW_MS,
        "compoundsFinalFadeToBlackMs": FINAL_FADE_MS,
        "vocabArtworkExhaleMs": 2000,
        "exhibitTransitionMs": 0,
        "kenBurnsDurationMs": 600000,
        "closingBlackAfterMs": 400,
    }

    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": "proto_glow_stress",
        "title": "Prototype — Dense Kanji Glow Stress Test",
        "titleJa": "試作 — 高画数漢字グロー検証",
        "notes": (
            "EXPERIMENT ONLY. The 18 densest master-CSV kanji plus 靈 / 驫. "
            "Drive with ?glowLab=current|reduced|none|tight and optionally "
            "&typeLab=a (150% size). Same engine; only the text-shadow and a "
            "4% size trim change."
        ),
        "soundtrack": {"main": SOUNDTRACK},
        "exhibition": exhibition,
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "japaneseVocabulary",
            "showKeyword": False,
            "showKanji": False,
            "showEnglish": True,
            "exhibitProfile": "japaneseVocabulary",
            "verseMode": "sequential",
            "typography": "mobile-refine",
            "typographyStyle": "foundations",
            "cameraMotionScale": 1.0,
        },
        "meta": {
            "series": "prototype_editions",
            "prototype": True,
            "stage": "glowStress",
            "sceneCount": 1,
            "compoundCount": len(steps),
            "ending": "finalCompoundReview",
        },
        "scenes": [
            {
                "id": "PROTO_glow_stress",
                "image": "images/black.png",
                "galleryCamera": {
                    "motion": "still",
                    "focus": "50% 50%",
                    "motionScale": 1.0,
                },
                "compounds": {"steps": steps},
            }
        ],
    }


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  → {path.relative_to(ROOT)}")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    kanji = load_dense(18)
    write(OUT_DIR / "glow_stress_kanji.json", {"kanji": kanji, "count": len(kanji)})
    write(OUT_DIR / "proto_glow_stress.json", exhibition_for(kanji))
    print(f"\n  {len(kanji)} dense glyphs:")
    for k in kanji:
        print(f"    {k['kanji']}  {k['strokes']:>2}  {k['keyword']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
