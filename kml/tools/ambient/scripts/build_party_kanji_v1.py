#!/usr/bin/env python3
"""Build PARTY KANJI v1 exhibition collection from episode source data."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "collections" / "party_kanji_v1.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from party_kanji_config import PARTY_TIMING, PARTY_VISUAL  # noqa: E402
from party_kanji_episodes import (  # noqa: E402
    DISCLAIMERS,
    EPISODES,
    PRODUCTION_ORDER,
    SERIES,
)


def scene_from_episode(ep: dict) -> dict:
    playlist = ep.get("playlist") or ep.get("collection") or ""
    party = {
        "challenge": ep["challenge"],
        "playlist": playlist,
        "components": ep.get("components", []),
        "componentLayout": ep.get("component_layout", "vertical"),
        "operator": ep.get("operator", "+"),
        "reading": ep.get("reading", ""),
        "disclaimer": ep.get("disclaimer", ""),
        "trivia": ep.get("trivia", ""),
        "strokePage": ep.get("stroke_page", ""),
        "strokeNote": ep.get("stroke_note", ""),
        "closingMessage": ep.get("closing_message", ""),
    }
    if ep.get("visual"):
        party["visual"] = ep["visual"]
    scene = {
        "id": ep["id"],
        "kanji": ep["kanji"],
        "keyword": ep.get("keyword") or ep.get("meaning", ""),
        "party": party,
    }
    return scene


def build() -> dict:
    scenes = [scene_from_episode(ep) for ep in EPISODES]
    playlists = sorted({s["party"]["playlist"] for s in scenes if s["party"]["playlist"]})
    return {
        "presentation": "exhibition",
        "assetsBase": "../../assets",
        "id": "party_kanji_v1",
        "title": f"{SERIES['title']} — Episode 1 (龘)",
        "notes": (
            "PARTY KANJI: fast visual discovery — Shock → Reveal → Proof → Final → Closing → End Card. "
            "Timing and visuals are JSON-configured for reuse across collections."
        ),
        "exhibition": dict(PARTY_TIMING),
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
            "series": SERIES["title"],
            "tagline": SERIES["tagline"],
            "closingMessage": SERIES["closingMessage"],
            "partyVisual": dict(PARTY_VISUAL),
            "disclaimers": DISCLAIMERS,
            "productionOrder": PRODUCTION_ORDER,
            "sceneCount": len(scenes),
            "prototype": True,
            "playlists": playlists,
        },
        "scenes": scenes,
    }


def main() -> None:
    data = build()
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(data['scenes'])} scene(s))")


if __name__ == "__main__":
    main()
