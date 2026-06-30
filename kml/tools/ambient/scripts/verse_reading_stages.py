"""Generate hiragana, mixed, and natural reading-stage text from lesson jp-verse HTML."""

from __future__ import annotations

import re

from verse_mixed_curation import MIXED_REVEAL

RUBY_RE = re.compile(r"<ruby>([^<]+)<rt>([^<]*)</rt></ruby>")
BR_RE = re.compile(r"<br\s*/?>", re.I)
TAG_RE = re.compile(r"<[^>]+>")
KANJI_RE = re.compile(
    r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3005\u3006]"
)


def _is_kanji(ch: str) -> bool:
    return bool(KANJI_RE.fullmatch(ch))


def iter_segments(inner_html: str) -> list[dict]:
    """Walk jp-verse inner HTML; yield ruby, br, and plain text segments in order."""
    segments: list[dict] = []
    i = 0
    while i < len(inner_html):
        ruby = RUBY_RE.match(inner_html, i)
        if ruby:
            segments.append(
                {
                    "type": "ruby",
                    "kanji": ruby.group(1),
                    "reading": ruby.group(2),
                }
            )
            i = ruby.end()
            continue
        br = BR_RE.match(inner_html, i)
        if br:
            segments.append({"type": "br"})
            i = br.end()
            continue
        tag = TAG_RE.match(inner_html, i)
        if tag:
            i = tag.end()
            continue
        ch = inner_html[i]
        if ch not in " \t\n\r":
            segments.append({"type": "text", "text": ch})
        i += 1
    return segments


def _coalesce_text(segments: list[dict]) -> list[dict]:
    """Merge adjacent plain-text segments."""
    out: list[dict] = []
    buf = ""
    for seg in segments:
        if seg["type"] == "text":
            buf += seg["text"]
            continue
        if buf:
            out.append({"type": "text", "text": buf})
            buf = ""
        out.append(seg)
    if buf:
        out.append({"type": "text", "text": buf})
    return out


def normalize_two_lines(html: str) -> str:
    """Collapse multi-line verses to two lines at a natural thought break."""
    lines = [line.strip() for line in BR_RE.split(html) if line.strip()]
    if len(lines) <= 2:
        return "<br>".join(lines)
    if len(lines) == 4:
        return f"{lines[0]}　{lines[1]}<br>{lines[2]}　{lines[3]}"
    if len(lines) == 3:
        return f"{lines[0]}　{lines[1]}<br>{lines[2]}"
    mid = len(lines) // 2
    top = "　".join(lines[:mid])
    bottom = "　".join(lines[mid:])
    return f"{top}<br>{bottom}"


def _reveal_items(scene_id: str) -> set[str]:
    return set(MIXED_REVEAL.get(scene_id, []))


def _render_mixed(segments: list[dict], scene_id: str) -> str:
    reveal = _reveal_items(scene_id)
    coalesced = _coalesce_text(segments)
    parts: list[str] = []
    i = 0
    while i < len(coalesced):
        seg = coalesced[i]
        if seg["type"] == "br":
            parts.append("<br>")
            i += 1
            continue
        if seg["type"] == "text":
            parts.append(seg["text"])
            i += 1
            continue
        if seg["type"] == "ruby":
            rubies: list[dict] = []
            j = i
            while j < len(coalesced) and coalesced[j]["type"] == "ruby":
                rubies.append(coalesced[j])
                j += 1
            combined = "".join(r["kanji"] for r in rubies)
            if combined in reveal:
                for r in rubies:
                    parts.append(r["kanji"])
            else:
                for r in rubies:
                    if r["kanji"] in reveal:
                        parts.append(r["kanji"])
                    else:
                        parts.append(r["reading"])
            i = j
            continue
        i += 1
    return normalize_two_lines("".join(parts))


def _render(segments: list[dict], *, mode: str) -> str:
    parts: list[str] = []
    for seg in segments:
        if seg["type"] == "br":
            parts.append("<br>")
            continue
        if seg["type"] == "text":
            parts.append(seg["text"])
            continue
        kanji = seg["kanji"]
        reading = seg["reading"]
        if mode == "hiragana":
            parts.append(reading)
        elif mode == "natural":
            parts.append(kanji)
        elif mode == "mixed":
            raise ValueError("use _render_mixed for mixed mode")
    return normalize_two_lines("".join(parts))


def kanji_density(html: str) -> float:
    """Rough kanji ratio in visible text (for QA)."""
    plain = (
        html.replace("<br>", "")
        .replace("<br/>", "")
        .replace("<br />", "")
    )
    if not plain:
        return 0.0
    ks = sum(1 for c in plain if _is_kanji(c))
    return ks / len(plain)


def reading_stages(jp_html: str, scene_id: str) -> dict[str, str]:
    """Return hiragana, mixed, and natural HTML for one jp-verse block."""
    segments = _coalesce_text(iter_segments(jp_html))
    return {
        "hiragana": _render(segments, mode="hiragana"),
        "mixed": _render_mixed(segments, scene_id),
        "natural": _render(segments, mode="natural"),
    }


def plain_preview(html: str) -> str:
    return (
        html.replace("<br>", "\n")
        .replace("<br/>", "\n")
        .replace("<br />", "\n")
    )
