"""Ruby HTML helpers for Compounds Exhibition steps."""

from __future__ import annotations


def ruby_word(kanji: str, reading: str) -> str:
    return f"<ruby>{kanji}<rt>{reading}</rt></ruby>"


def ruby_compound(parts: list[tuple[str, str]]) -> str:
    out: list[str] = []
    for kanji, reading in parts:
        if reading:
            out.append(ruby_word(kanji, reading))
        else:
            out.append(kanji)
    return "".join(out)


def enrich_compound_step(step: dict) -> dict:
    """Ensure jpHtml exists for furigana playback."""
    out = dict(step)
    if out.get("jpHtml"):
        return out
    jp = out.get("jp", "")
    reading = out.get("reading", "")
    parts = out.get("ruby")
    if parts:
        out["jpHtml"] = ruby_compound(parts)
    elif jp and reading and len(jp) <= 4:
        out["jpHtml"] = ruby_word(jp, reading)
    return out


def enrich_compound_steps(steps: list[dict]) -> list[dict]:
    return [enrich_compound_step(s) for s in steps]


def target_reading_for_hint(
    kanji: str, jp: str, parts: list[tuple[str, str]] | None
) -> str | None:
    """Reading of the target kanji within this compound (for hint generation)."""
    if not parts:
        return None
    for surface, reading in parts:
        if reading and surface == kanji:
            return reading
    for surface, reading in parts:
        if reading and surface == jp:
            return reading
    for surface, reading in parts:
        if reading and kanji in surface and surface.index(kanji) == 0:
            return reading
    return None


def apply_reading_hints_once(kanji: str, steps: list[dict]) -> list[dict]:
    """Add {compound}の{reading} hint only the first time each reading appears."""
    seen: set[str] = set()
    out: list[dict] = []
    for step in steps:
        row = dict(step)
        row.pop("hint", None)
        parts = row.get("ruby")
        reading = target_reading_for_hint(kanji, row.get("jp", ""), parts)
        if reading and reading not in seen:
            seen.add(reading)
            row["hint"] = f"{row['jp']}の{reading}"
        out.append(row)
    return out
