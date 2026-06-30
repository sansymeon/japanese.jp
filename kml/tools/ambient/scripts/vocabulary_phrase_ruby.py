"""Build ruby HTML for vocabulary phrase steps from lesson verse markup."""

from __future__ import annotations

import re

from verse_reading_stages import KANJI_RE, _coalesce_text, iter_segments

RUBY_OUT_RE = re.compile(r"<ruby>")


def _normalize(s: str) -> str:
    return re.sub(r"[\s　]+", "", s)


def _token_surface(tok: dict) -> str:
    if tok["type"] == "ruby":
        return tok["kanji"]
    if tok["type"] == "text":
        return tok["text"]
    return ""


def tokenize_verse(jp_html: str) -> list[dict]:
    tokens: list[dict] = []
    for seg in _coalesce_text(iter_segments(jp_html)):
        if seg["type"] == "br":
            continue
        tokens.append(seg)
    return tokens


def reading_map_from_verse(jp_html: str) -> dict[str, str]:
    m: dict[str, str] = {}
    for seg in iter_segments(jp_html):
        if seg["type"] == "ruby":
            m[seg["kanji"]] = seg["reading"]
    return m


def _render_token_slice(tokens: list[dict]) -> str:
    parts: list[str] = []
    for tok in tokens:
        if tok["type"] == "ruby":
            parts.append(f'<ruby>{tok["kanji"]}<rt>{tok["reading"]}</rt></ruby>')
        elif tok["type"] == "text":
            parts.append(tok["text"])
    return "".join(parts)


def _match_phrase_tokens(tokens: list[dict], phrase: str) -> list[dict] | None:
    if not phrase:
        return None
    surfaces = [_token_surface(t) for t in tokens]
    full = _normalize("".join(surfaces))
    pn = _normalize(phrase)
    if not pn or pn not in full:
        return None
    start = full.index(pn)
    end = start + len(pn)

    pos = 0
    out: list[dict] = []
    for tok in tokens:
        surf = _token_surface(tok)
        if not surf:
            continue
        tok_start = pos
        tok_end = pos + len(_normalize(surf))
        if tok_end <= start:
            pos = tok_end
            continue
        if tok_start >= end:
            break
        if tok["type"] == "ruby":
            out.append(dict(tok))
        else:
            kept: list[str] = []
            norm_i = tok_start
            for ch in tok["text"]:
                if ch in " \t\n\r　":
                    if start <= norm_i < end:
                        kept.append(ch)
                    continue
                if start <= norm_i < end:
                    kept.append(ch)
                norm_i += 1
            if kept:
                out.append({"type": "text", "text": "".join(kept)})
        pos = tok_end
    return out or None


KANA_RE = re.compile(r"[ぁ-んァ-ンー]")


def _ruby_from_map(phrase: str, readings: dict[str, str]) -> str:
    parts: list[str] = []
    i = 0
    while i < len(phrase):
        ch = phrase[i]
        if not KANJI_RE.search(ch):
            parts.append(ch)
            i += 1
            continue
        matched = None
        for size in range(min(8, len(phrase) - i), 0, -1):
            chunk = phrase[i : i + size]
            if chunk in readings:
                matched = chunk
                break
        if matched:
            rt = readings[matched]
            if KANA_RE.search(matched):
                parts.append(matched)
            else:
                parts.append(f"<ruby>{matched}<rt>{rt}</rt></ruby>")
            i += len(matched)
        else:
            parts.append(ch)
            i += 1
    return "".join(parts)


def enrich_readings(readings: dict[str, str], steps: list[dict]) -> dict[str, str]:
    out = dict(readings)
    for step in steps:
        jp = step.get("jp") or ""
        reading = step.get("reading") or ""
        if reading and jp and KANJI_RE.search(jp) and not step.get("phrase"):
            if not KANA_RE.search(jp):
                out[jp] = reading
    return out


def phrase_ruby_html(
    verse_html: str,
    phrase: str,
    *,
    extra_readings: dict[str, str] | None = None,
) -> tuple[str, bool]:
    """Return (display html, uses_furigana)."""
    if not phrase or not KANJI_RE.search(phrase):
        return phrase, False

    tokens = tokenize_verse(verse_html)
    matched = _match_phrase_tokens(tokens, phrase)
    if matched:
        html = _render_token_slice(matched)
        if RUBY_OUT_RE.search(html):
            return html, True

    readings = reading_map_from_verse(verse_html)
    if extra_readings:
        readings.update(extra_readings)
    html = _ruby_from_map(phrase, readings)
    if RUBY_OUT_RE.search(html):
        return html, True
    return phrase, False


def enrich_vocabulary_steps(steps: list[dict], verse_html: str) -> list[dict]:
    readings = reading_map_from_verse(verse_html)
    enriched: list[dict] = []
    for step in steps:
        s = dict(step)
        jp = s.get("jp") or ""
        reading = s.get("reading") or ""
        if reading and jp and KANJI_RE.search(jp) and not s.get("phrase"):
            if not KANA_RE.search(jp):
                readings[jp] = reading

        if s.get("phrase") and KANJI_RE.search(jp):
            tokens = tokenize_verse(verse_html)
            matched = _match_phrase_tokens(tokens, jp)
            if matched:
                html = _render_token_slice(matched)
            else:
                html = _ruby_from_map(jp, readings)
            if RUBY_OUT_RE.search(html):
                s["jpHtml"] = html
                s["furigana"] = True

        enriched.append(s)
    return enriched
