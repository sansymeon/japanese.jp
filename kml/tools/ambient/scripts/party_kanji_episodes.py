"""PARTY KANJI — episode source data.

Reusable JSON-driven template for short-form kanji episodes.
Not JLPT prep — surprise, curiosity, pattern recognition, confidence.

Episode structure:
  Shock → Reveal (staggered) → Proof → Final (+ pulse) → Closing → End Card
"""

from __future__ import annotations

from typing import Any, TypedDict

from party_kanji_config import (  # noqa: E402
    DEFAULT_CLOSING_MESSAGE,
    SERIES_TAGLINE,
)

STROKES_BASE = "strokes/pages"


class PartyComponent(TypedDict):
    kanji: str
    label: str


class PartyEpisode(TypedDict, total=False):
    id: str
    kanji: str
    keyword: str
    meaning: str
    challenge: str
    playlist: str
    collection: str  # legacy alias for playlist
    components: list[PartyComponent]
    component_layout: str  # vertical | horizontal
    operator: str
    reading: str
    disclaimer: str
    trivia: str
    stroke_page: str
    stroke_note: str
    closing_message: str
    visual: dict[str, Any]


DISCLAIMERS: list[str] = [
    "No dragons were harmed in the production of this video.",
    "No roses were harmed in the production of this video.",
    "No trees were harmed in the production of this video.",
    "Party Kanji is not FDA approved.",
    "Results may vary.",
    "Use responsibly.",
    "Side effects may include spontaneous kanji recognition.",
]

SERIES = {
    "title": "PARTY KANJI",
    "tagline": SERIES_TAGLINE,
    "closingMessage": DEFAULT_CLOSING_MESSAGE,
    "tone": "playful, intelligent, slightly absurd — not childish, not academic",
}

# Suggested production order — familiarity → spectacle (finale: biáng).
PRODUCTION_ORDER: list[str] = [
    "龘",
    "森",
    "晶",
    "品",
    "轟",
    "鑫",
    "焱",
    "淼",
    "犇",
    "鱻",
    "靐",
    "麤",
    "毳",
    "垚",
    "猋",
    "𰻞",
]

EPISODES: list[PartyEpisode] = [
    {
        "id": "PK01_three_dragons",
        "kanji": "龘",
        "keyword": "three dragons",
        "meaning": "three dragons",
        "challenge": "Can you write this?",
        "playlist": "Monster Kanji",
        "components": [
            {"kanji": "龍", "label": "dragon"},
            {"kanji": "龍", "label": "dragon"},
            {"kanji": "龍", "label": "dragon"},
        ],
        "component_layout": "vertical",
        "operator": "+",
        "reading": "トウ",
        "disclaimer": "No dragons were harmed in the production of this video.",
        "stroke_page": f"{STROKES_BASE}/dragon_old.html",
        "stroke_note": "",
    },
]

# Stubs for upcoming episodes — wire into EPISODES as content is ready.
FUTURE_EPISODES: list[dict[str, Any]] = [
    {
        "order": 2,
        "kanji": "森",
        "challenge": "Can you write FOREST?",
        "playlist": "Three of Something",
        "components": [
            {"kanji": "木", "label": "tree"},
            {"kanji": "木", "label": "tree"},
            {"kanji": "木", "label": "tree"},
        ],
        "stroke_page": f"{STROKES_BASE}/forest.html",
    },
    {
        "order": 3,
        "kanji": "晶",
        "challenge": "Can you write SPARKLE?",
        "playlist": "Three of Something",
        "components": [
            {"kanji": "日", "label": "sun"},
            {"kanji": "日", "label": "sun"},
            {"kanji": "日", "label": "sun"},
        ],
        "stroke_page": f"{STROKES_BASE}/sparkle.html",
    },
    {
        "order": 4,
        "kanji": "品",
        "challenge": "Can you write GOODS?",
        "playlist": "Three of Something",
        "components": [
            {"kanji": "口", "label": "mouth"},
            {"kanji": "口", "label": "mouth"},
            {"kanji": "口", "label": "mouth"},
        ],
        "stroke_page": f"{STROKES_BASE}/goods.html",
    },
    {
        "order": 5,
        "kanji": "轟",
        "challenge": "Can you write RUMBLE?",
        "playlist": "Three of Something",
        "components": [
            {"kanji": "車", "label": "car"},
            {"kanji": "車", "label": "car"},
            {"kanji": "車", "label": "car"},
        ],
        "stroke_page": f"{STROKES_BASE}/rumble.html",
    },
    {
        "order": 6,
        "kanji": "鑫",
        "challenge": "Can you write GOLD?",
        "playlist": "Three of Something",
        "components": [
            {"kanji": "金", "label": "gold"},
            {"kanji": "金", "label": "gold"},
            {"kanji": "金", "label": "gold"},
        ],
    },
    {
        "order": 7,
        "kanji": "焱",
        "challenge": "Can you write FIRE?",
        "playlist": "Three of Something",
        "components": [
            {"kanji": "火", "label": "fire"},
            {"kanji": "火", "label": "fire"},
            {"kanji": "火", "label": "fire"},
        ],
    },
    {
        "order": 8,
        "kanji": "淼",
        "challenge": "Can you write WATER?",
        "playlist": "Three of Something",
    },
    {
        "order": 9,
        "kanji": "犇",
        "challenge": "Can you write OXEN?",
        "playlist": "Three of Something",
    },
    {
        "order": 10,
        "kanji": "鱻",
        "challenge": "Can you write FISH?",
        "playlist": "Three of Something",
    },
    {
        "order": 11,
        "kanji": "靐",
        "challenge": "Can you write THUNDER?",
        "playlist": "Three of Something",
    },
    {
        "order": 12,
        "kanji": "麤",
        "challenge": "Can you write DEER?",
        "playlist": "Three of Something",
    },
    {
        "order": 13,
        "kanji": "毳",
        "challenge": "Can you write FUR?",
        "playlist": "Three of Something",
    },
    {
        "order": 14,
        "kanji": "垚",
        "challenge": "Can you write EARTH?",
        "playlist": "Three of Something",
    },
    {
        "order": 15,
        "kanji": "猋",
        "challenge": "Can you write DOGS?",
        "playlist": "Three of Something",
    },
    {
        "order": 16,
        "kanji": "𰻞",
        "challenge": "Can you write BIÁNG?",
        "playlist": "Legendary",
        "closing_message": "Some parties need extra noodles.",
    },
]
