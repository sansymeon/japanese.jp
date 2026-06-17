#!/usr/bin/env python3
"""Calculate runtime for lessons_1_5_prototype exhibition."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "collections" / "lessons_1_5_prototype.json"


def exhibit_ms(t: dict) -> int:
    return (
        t["artworkAloneMs"]
        + t["verseJpRevealMs"]
        + t["verseJpHoldMs"]
        + t["verseJpFadeMs"]
        + t["verseEnRevealMs"]
        + t["verseEnHoldMs"]
        + t["verseEnFadeMs"]
        + t.get("exhibitTransitionMs", 4000)
    )


def bookend_ms(t: dict, *, opening: bool) -> int:
    if opening:
        return (
            t.get("openingBlackBeforeMs", 0)
            + t.get("openingRevealMs", 0)
            + t.get("openingHoldMs", 0)
            + t.get("openingExhaleMs", 0)
            + t.get("openingBlackAfterMs", 0)
        )
    return (
        t.get("closingFadeToBlackMs", t.get("closingExhaleMs", 3000))
        + t.get("closingHoldMs", 0)
        + t.get("closingExhaleMs", 0)
        + t.get("closingBlackAfterMs", 0)
    )


def fmt(seconds: float) -> str:
    m, s = divmod(int(round(seconds)), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def main() -> int:
    if not COLLECTION.is_file():
        print(f"Missing {COLLECTION}. Run: python3 scripts/build_lessons_1_5_prototype.py", file=sys.stderr)
        return 1

    data = json.loads(COLLECTION.read_text(encoding="utf-8"))
    t = data["exhibition"]
    scenes = data["scenes"]
    per = exhibit_ms(t)
    body = per * len(scenes)
    opening = bookend_ms(t, opening=True)
    closing = bookend_ms(t, opening=False)
    total = body + opening + closing

    print("Lessons 1–5 prototype runtime")
    print(f"  Exhibit count:     {len(scenes)}")
    print(f"  Per exhibit:       {per / 1000:.1f}s ({fmt(per / 1000)})")
    print(f"  Exhibits only:     {body / 1000:.1f}s ({fmt(body / 1000)}) — excluding bookends")
    print(f"  Opening bookend:   {opening / 1000:.1f}s")
    print(f"  Closing bookend:   {closing / 1000:.1f}s")
    print(f"  Total w/ bookends: {total / 1000:.1f}s ({fmt(total / 1000)})")
    print()
    print(f"  Recommended soundtrack length: ≥ {fmt(total / 1000)} ({total / 1000 / 60:.1f} min)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
