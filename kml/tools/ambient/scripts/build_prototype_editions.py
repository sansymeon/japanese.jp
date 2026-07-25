#!/usr/bin/env python3
"""Build the prototype-edition collections (Gallery 16:9 / Mobile 9:16 typography lab).

Experimental. These collections exist only to compare presentation layouts —
they are not part of any published series and are not added to manifest.json.

  python3 scripts/build_prototype_editions.py

Writes:
  collections/prototypes/proto_typography_lab.json
  collections/prototypes/proto_party_kanji_lab.json
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "collections" / "prototypes"

SOUNDTRACK = "audio/12_minutes_minus3db.mp3"

# Per-step budget, identical to Beyond Jōyō. Pacing is deliberately not changed.
STEP_MS = 19_400
OPEN_MS = 800 + 1200 + 3200
REVIEW_MS = 22_000
FINAL_FADE_MS = 4_000


# Eighteen high stroke-count kanji, each carried by a real two-kanji compound.
# Two dense glyphs side by side is the worst case for the "mass of white"
# problem, and it is what the Beyond Jōyō corpus actually contains.
DENSE = [
    ("憂鬱", "ゆううつ", "melancholy", [("憂", "ゆう"), ("鬱", "うつ")]),
    ("驚愕", "きょうがく", "astonishment", [("驚", "きょう"), ("愕", "がく")]),
    ("籠城", "ろうじょう", "holing up / standing siege", [("籠", "ろう"), ("城", "じょう")]),
    ("擁護", "ようご", "protection / advocacy", [("擁", "よう"), ("護", "ご")]),
    ("議論", "ぎろん", "discussion / debate", [("議", "ぎ"), ("論", "ろん")]),
    ("試験", "しけん", "examination", [("試", "し"), ("験", "けん")]),
    ("鑑賞", "かんしょう", "appreciation of art", [("鑑", "かん"), ("賞", "しょう")]),
    ("折鶴", "おりづる", "folded paper crane", [("折", "おり"), ("鶴", "づる")]),
    ("華麗", "かれい", "splendour", [("華", "か"), ("麗", "れい")]),
    ("競技", "きょうぎ", "athletic contest", [("競", "きょう"), ("技", "ぎ")]),
    ("心臓", "しんぞう", "the heart", [("心", "しん"), ("臓", "ぞう")]),
    ("懸念", "けねん", "concern / misgiving", [("懸", "け"), ("念", "ねん")]),
    ("顧客", "こきゃく", "customer / client", [("顧", "こ"), ("客", "きゃく")]),
    ("警鐘", "けいしょう", "alarm bell / warning", [("警", "けい"), ("鐘", "しょう")]),
    ("謙譲", "けんじょう", "modesty / deference", [("謙", "けん"), ("譲", "じょう")]),
    ("沸騰", "ふっとう", "boiling / seething", [("沸", "ふっ"), ("騰", "とう")]),
    ("魔法", "まほう", "magic", [("魔", "ま"), ("法", "ほう")]),
    ("書籍", "しょせき", "books / publications", [("書", "しょ"), ("籍", "せき")]),
]

# Optical-weight control group — the same type at a fraction of the stroke count.
SIMPLE = [
    ("山", "やま", "mountain", [("山", "やま")]),
    ("川", "かわ", "river", [("川", "かわ")]),
    ("人", "ひと", "person", [("人", "ひと")]),
    ("空", "そら", "sky", [("空", "そら")]),
    ("木", "き", "tree", [("木", "き")]),
]


def ruby_html(pairs: list[tuple[str, str]]) -> str:
    return "".join(f"<ruby>{base}<rt>{rt}</rt></ruby>" for base, rt in pairs)


def steps() -> list[dict]:
    out = []
    for order, (jp, reading, en, pairs) in enumerate(DENSE + SIMPLE, start=1):
        group = "dense" if order <= len(DENSE) else "simple"
        out.append(
            {
                "jp": jp,
                "reading": reading,
                "en": en,
                "jpHtml": ruby_html(pairs),
                "meta": {
                    "kanji": jp[0],
                    "strokeGroup": group,
                    "displayOrder": order,
                },
            }
        )
    return out


def exhibition() -> dict:
    """Beyond Jōyō timing, unchanged. The lab tests layout, not pacing."""
    return {
        "artworkArrivalMs": 0,
        "artworkArrivalFadeMs": 1200,
        "artworkAloneMs": 0,
        "exhibitionBlackBeforeMs": 800,
        "compoundsPauseBeforeMs": 3200,
        "compoundsStepRevealMs": 1400,
        "compoundsFuriganaEnterDelayMs": 900,
        "compoundsFuriganaEnterMs": 2200,
        "compoundsFuriganaHoldMs": 3000,
        "compoundsFuriganaFadeMs": 2200,
        "compoundsNativeHoldMs": 2200,
        "compoundsReadingRevealMs": 1200,
        "compoundsReadingHoldMs": 1800,
        "compoundsEnRevealMs": 1200,
        "compoundsEnHoldMs": 3500,
        "compoundsEnFadeMs": 1400,
        "compoundsStepFadeMs": 1400,
        "compoundsFinalReviewHoldMs": REVIEW_MS,
        "compoundsFinalFadeToBlackMs": FINAL_FADE_MS,
        "vocabArtworkExhaleMs": 2800,
        "exhibitTransitionMs": 0,
        "kenBurnsDurationMs": 1200000,
        "closingBlackAfterMs": 600,
    }


def typography_lab() -> dict:
    body = steps()
    runtime_ms = (
        OPEN_MS
        + STEP_MS * len(body)
        - 1400  # final step is left visible instead of fading out
        + REVIEW_MS
        + FINAL_FADE_MS
        + 600
    )
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": "proto_typography_lab",
        "title": "Prototype — Typography Lab (Gallery 16:9 / Mobile 9:16)",
        "titleJa": "試作 — 文字組み検証",
        "notes": (
            "EXPERIMENT ONLY. 18 high stroke-count compounds + 5 simple kanji for "
            "optical-weight comparison. Same engine, timing, soundtrack and transitions "
            "as Beyond Jōyō; only the presentation layout varies. Drive with "
            "?edition=mobile and ?typeLab=a|b|c."
        ),
        "soundtrack": {"main": SOUNDTRACK},
        "exhibition": exhibition(),
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
            "stage": "compounds",
            "sceneCount": 1,
            "compoundCount": len(body),
            "denseCount": len(DENSE),
            "simpleCount": len(SIMPLE),
            "soundtrackDurationMs": 771288,
            "estimatedContentRuntimeMs": runtime_ms,
            "ending": "finalCompoundReview",
        },
        "scenes": [
            {
                "id": "PROTO_typography_lab",
                "image": "images/black.png",
                "galleryCamera": {"motion": "still", "focus": "50% 50%", "motionScale": 1.0},
                "compounds": {"steps": body},
            }
        ],
    }


def party_kanji_lab() -> dict:
    """Two worst-case compositions for the merging-white-mass problem."""
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": "proto_party_kanji_lab",
        "title": "Prototype — Party Kanji spacing lab (龘 / 麤)",
        "notes": (
            "EXPERIMENT ONLY. Same six-phase Party Kanji flow, used to compare component "
            "spacing and optical weight at a large overall composition. "
            "Drive with ?typeLab=a|b|c and optionally &edition=mobile."
        ),
        "exhibition": {
            "partyShockKanjiRevealMs": 250,
            "partyShockChallengeDelayMs": 3000,
            "partyShockChallengeRevealMs": 350,
            "partyShockHoldAfterChallengeMs": 1650,
            "partyShockFadeMs": 400,
            "partyRevealFadeInMs": 350,
            "partyRevealBurstMs": 400,
            "partyComponentStaggerMs": 2000,
            "partyComponentArriveMs": 450,
            "partyEquationDelayMs": 3000,
            "partyEquationRevealMs": 400,
            "partyEquationHoldMs": 4000,
            "partyRevealFadeMs": 400,
            "partyProofFadeInMs": 400,
            "partyProofHoldMs": 8000,
            "partyProofFadeMs": 400,
            "partyFinalFadeInMs": 1200,
            "partyFinalHoldMs": 1500,
            "partyComponentPulseFadeInMs": 500,
            "partyComponentPulseHoldMs": 2000,
            "partyFinalFadeOutMs": 600,
            "partyClosingFadeInMs": 350,
            "partyClosingHoldMs": 2500,
            "partyClosingFadeMs": 350,
            "partyEndCardFadeInMs": 350,
            "partyEndCardHoldMs": 1500,
            "partyEndCardFadeMs": 350,
            "exhibitTransitionMs": 0,
            "exhibitBlackHoldMs": 0,
            "blackHoldMs": 0,
        },
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "partyKanji",
            "exhibitProfile": "partyKanji",
            "showKeyword": False,
            "typography": "party-kanji",
        },
        "meta": {
            "theme": "partyKanji",
            "series": "PARTY KANJI",
            "prototype": True,
            "tagline": "Learn this before your next party.",
            "closingMessage": "Big kanji are just little kanji having a party.",
            "partyVisual": {
                "componentReveal": "burst",
                "componentGlow": False,
                "componentBounce": True,
                "finalGlow": False,
                "componentPulseOpacity": 0.18,
                "showReadingInReveal": False,
                "showTrivia": False,
                "showPlaylistSubtitle": True,
            },
            "sceneCount": 2,
            "playlists": ["Party Kanji"],
        },
        "scenes": [
            {
                "id": "PROTO_PK_three_dragons",
                "kanji": "龘",
                "keyword": "three dragons",
                "party": {
                    "challenge": "Can you write this?",
                    "playlist": "Party Kanji",
                    "components": [{"kanji": "龍", "label": "dragon"}] * 3,
                    "componentLayout": "gathering",
                    "operator": "+",
                    "reading": "トウ",
                    "disclaimer": "No dragons were harmed in the production of this video.",
                    "trivia": "",
                    "closingMessage": "",
                },
            },
            {
                "id": "PROTO_PK_three_deer",
                "kanji": "麤",
                "keyword": "three deer",
                "party": {
                    "challenge": "Three deer. One kanji.",
                    "playlist": "Party Kanji",
                    "components": [{"kanji": "鹿", "label": "deer"}] * 3,
                    "componentLayout": "gathering",
                    "operator": "+",
                    "reading": "ソ",
                    "disclaimer": "No deer were harmed in the production of this video.",
                    "trivia": "",
                    "closingMessage": "",
                },
            },
        ],
    }


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  → {path.relative_to(ROOT)}")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lab = typography_lab()
    write(OUT_DIR / "proto_typography_lab.json", lab)
    write(OUT_DIR / "proto_party_kanji_lab.json", party_kanji_lab())

    runtime_s = lab["meta"]["estimatedContentRuntimeMs"] // 1000
    print(
        f"\n  {lab['meta']['compoundCount']} slides "
        f"({lab['meta']['denseCount']} dense + {lab['meta']['simpleCount']} simple) "
        f"≈ {runtime_s // 60}:{runtime_s % 60:02d}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
