#!/usr/bin/env python3
"""Fill <rt>?</rt> placeholders in lesson jp-verse blocks with hiragana readings."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import fugashi

BASE = Path(__file__).resolve().parent.parent
LESSONS_DIR = BASE / "contents/books/book_01/lessons"
MASTER_CSV = BASE / "data/kanji/kanji_master_with_stories.csv"

RUBY_RE = re.compile(r"<ruby>([^<]+)<rt>([^<]*)</rt></ruby>")
JP_VERSE_RE = re.compile(
    r'(<p class="jp-verse[^"]*">)(.*?)(</p>)',
    re.DOTALL,
)
KANJI_RE = re.compile(
    r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3005\u3006]"
)
TAG_RE = re.compile(r"<[^>]+>")
BR_RE = re.compile(r"<br\s*/?>", re.I)


def katakana_to_hiragana(text: str) -> str:
    out = []
    for ch in text:
        code = ord(ch)
        if 0x30A1 <= code <= 0x30F6:
            out.append(chr(code - 0x60))
        elif ch in ("ー", "ヴ"):
            out.append("ゔ" if ch == "ヴ" else "ー")
        else:
            out.append(ch)
    return "".join(out)


def normalize_reading(text: str) -> str:
    return katakana_to_hiragana(text).replace("ー", "")


def load_exact_lookup() -> dict[str, str]:
    counts: dict[str, dict[str, int]] = {}
    for n in range(1, 7):
        path = LESSONS_DIR / f"lesson_{n:02d}.html"
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        for kanji, rt in RUBY_RE.findall(html):
            if rt and rt != "?":
                counts.setdefault(kanji, {})
                counts[kanji][rt] = counts[kanji].get(rt, 0) + 1
    return {k: max(v, key=v.get) for k, v in counts.items()}


def load_kanji_readings() -> dict[str, list[str]]:
    readings: dict[str, list[str]] = {}
    if not MASTER_CSV.exists():
        return readings
    with MASTER_CSV.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            kanji = row["kanji"]
            opts: list[str] = []
            on = row.get("on_reading", "").strip()
            if on:
                for part in re.split(r"[・/]", on):
                    part = part.strip()
                    if part:
                        opts.append(normalize_reading(part))
            kun = row.get("kun_readings", "").strip()
            if kun:
                for part in re.split(r"[・/]", kun):
                    part = part.strip()
                    if part:
                        base = part.split("-")[0]
                        if base:
                            opts.append(normalize_reading(base))
            deduped: list[str] = []
            for opt in opts:
                if opt and opt not in deduped:
                    deduped.append(opt)
            if deduped:
                readings[kanji] = deduped
    return readings


def is_formatting_char(ch: str) -> bool:
    return ch in " \t\n\r"


def plain_text_from_verse(inner_html: str) -> str:
    chars: list[str] = []
    i = 0
    while i < len(inner_html):
        match = RUBY_RE.match(inner_html, i)
        if match:
            chars.append(match.group(1))
            i = match.end()
            continue
        if BR_RE.match(inner_html, i):
            i = BR_RE.match(inner_html, i).end()
            continue
        tag = TAG_RE.match(inner_html, i)
        if tag:
            i = tag.end()
            continue
        ch = inner_html[i]
        if not is_formatting_char(ch):
            chars.append(ch)
        i += 1
    return "".join(chars)


def tokenize(text: str, tagger: fugashi.Tagger) -> list[dict]:
    tokens = []
    pos = 0
    for node in tagger(text):
        surface = node.surface
        if not surface:
            continue
        reading = normalize_reading(node.feature.kana or node.feature.pron or surface)
        tokens.append(
            {
                "surface": surface,
                "reading": reading,
                "start": pos,
                "end": pos + len(surface),
            }
        )
        pos += len(surface)
    return tokens


def find_token(tokens: list[dict], start: int, end: int) -> dict | None:
    for tok in tokens:
        if tok["start"] <= start and tok["end"] >= end:
            return tok
    return None


def reading_for_surface(tagger: fugashi.Tagger, surface: str) -> str:
    if not surface:
        return ""
    return normalize_reading(
        "".join(n.feature.kana or n.surface for n in tagger(surface))
    )


def strip_okurigana(
    tagger: fugashi.Tagger, reading: str, okurigana: str
) -> str:
    if not okurigana:
        return reading
    oku = reading_for_surface(tagger, okurigana)
    if oku and reading.endswith(oku):
        return reading[: -len(oku)]
    if reading.endswith(okurigana):
        return reading[: -len(okurigana)]
    return reading


def split_reading(
    kanji_parts: list[str],
    full_reading: str,
    kanji_readings: dict[str, list[str]],
    exact_lookup: dict[str, str],
) -> list[str] | None:
    full = normalize_reading(full_reading)

    def options(part: str) -> list[str]:
        seen: list[str] = []
        for candidate in [*kanji_readings.get(part, []), exact_lookup.get(part, "")]:
            candidate = normalize_reading(candidate)
            if candidate and candidate not in seen:
                seen.append(candidate)
        return seen

    def search(i: int, remaining: str) -> list[str] | None:
        if i == len(kanji_parts):
            return [] if not remaining else None
        for opt in options(kanji_parts[i]):
            candidates = [opt]
            if opt.endswith("つ") and remaining.startswith(opt[:-1] + "っ"):
                candidates.insert(0, opt[:-1] + "っ")
            if len(remaining) > len(opt) and remaining[len(opt)] == "っ":
                candidates.append(opt + "っ")
            for cand in candidates:
                if remaining.startswith(cand):
                    rest = search(i + 1, remaining[len(cand) :])
                    if rest is not None:
                        return [cand] + rest
        return None

    result = search(0, full)
    if result is not None:
        return result

    if len(kanji_parts) > 1:
        last = kanji_parts[-1]
        for suffix in options(last):
            if full.endswith(suffix) and len(full) > len(suffix):
                prefix = full[: -len(suffix)]
                if len(kanji_parts) == 2:
                    return [prefix, suffix]
                inner = split_reading(
                    kanji_parts[:-1], prefix, kanji_readings, exact_lookup
                )
                if inner is not None:
                    return inner + [suffix]

    if len(kanji_parts) == 2 and len(full) >= 2:
        return [full[:-1], full[-1]]

    if len(kanji_parts) == 1:
        return [full]
    return None


def parse_rubies(inner_html: str) -> list[dict]:
    rubies: list[dict] = []
    pos = 0
    i = 0
    while i < len(inner_html):
        match = RUBY_RE.match(inner_html, i)
        if match:
            kanji = match.group(1)
            rubies.append(
                {
                    "kanji": kanji,
                    "rt": match.group(2),
                    "start": pos,
                    "end": pos + len(kanji),
                }
            )
            pos += len(kanji)
            i = match.end()
            continue
        if BR_RE.match(inner_html, i):
            i = BR_RE.match(inner_html, i).end()
            continue
        tag = TAG_RE.match(inner_html, i)
        if tag:
            i = tag.end()
            continue
        if not is_formatting_char(inner_html[i]):
            pos += 1
        i += 1
    return rubies


def group_rubies(rubies: list[dict], tokens: list[dict]) -> list[list[dict]]:
    groups: list[list[dict]] = []
    current: list[dict] = []
    current_token: dict | None = None
    for ruby in rubies:
        token = find_token(tokens, ruby["start"], ruby["end"])
        if current and token is current_token:
            current.append(ruby)
        else:
            if current:
                groups.append(current)
            current = [ruby]
            current_token = token
    if current:
        groups.append(current)
    return groups


def align_kanji_readings(
    surface: str,
    reading: str,
    kanji_spans: list[tuple[int, int]],
) -> list[str] | None:
    """Align a reading to kanji spans inside surface, skipping okurigana kana.

    Example: surface 受け取, reading うけと, spans for 受 and 取 → [う, と]
    """
    if not kanji_spans:
        return []

    # Require at least one intervening kana somewhere, or a single trailing/leading
    # kana run after a kanji — otherwise split_reading is more appropriate.
    has_kana = any(not KANJI_RE.match(ch) for ch in surface)
    if not has_kana and len(kanji_spans) > 1:
        return None

    ri = 0
    out: list[str] = []
    for idx, (start, end) in enumerate(kanji_spans):
        remaining_kanji = len(kanji_spans) - idx - 1
        oku_end = end
        while oku_end < len(surface) and not KANJI_RE.match(surface[oku_end]):
            oku_end += 1
        oku = surface[end:oku_end]
        max_take = len(reading) - ri - remaining_kanji
        if max_take < 1:
            return None

        assigned = None
        if oku:
            for n in range(1, max_take + 1):
                if reading[ri + n :].startswith(oku):
                    assigned = reading[ri : ri + n]
                    ri = ri + n + len(oku)
                    break
            if assigned is None:
                return None
        elif remaining_kanji == 0:
            assigned = reading[ri:]
            ri = len(reading)
        else:
            # Adjacent kanji with no kana between — let split_reading handle it.
            return None

        if not assigned:
            return None
        out.append(assigned)

    return out if len(out) == len(kanji_spans) else None


def readings_for_group(
    group: list[dict],
    tokens: list[dict],
    tagger: fugashi.Tagger,
    kanji_readings: dict[str, list[str]],
    exact_lookup: dict[str, str],
) -> dict[tuple[int, int], str]:
    token = find_token(tokens, group[0]["start"], group[-1]["end"])
    if not token:
        return {
            (ruby["start"], ruby["end"]): exact_lookup.get(ruby["kanji"], ruby["kanji"])
            for ruby in group
        }

    token_start = token["start"]
    token_surface = token["surface"]
    token_reading = token["reading"]
    rel_start = group[0]["start"] - token_start
    rel_end = group[-1]["end"] - token_start
    okurigana = token_surface[rel_end:]
    kanji_reading = strip_okurigana(tagger, token_reading, okurigana)
    surface_slice = token_surface[rel_start:rel_end]

    if len(group) == 1:
        ruby = group[0]
        if ruby["kanji"] == token_surface:
            return {(ruby["start"], ruby["end"]): token_reading}
        # Prefer aligning against the surface slice so mid-word okurigana is stripped
        # e.g. 繰 in 繰り返し → surface 繰り, reading くり → く
        spans = [(0, len(ruby["kanji"]))]
        if surface_slice.startswith(ruby["kanji"]):
            aligned = align_kanji_readings(surface_slice, kanji_reading, spans)
            if aligned and aligned[0]:
                return {(ruby["start"], ruby["end"]): aligned[0]}
        if rel_start == 0 and token_surface.startswith(ruby["kanji"]):
            return {(ruby["start"], ruby["end"]): kanji_reading}
        if ruby["kanji"] in exact_lookup and len(ruby["kanji"]) > 1:
            return {(ruby["start"], ruby["end"]): exact_lookup[ruby["kanji"]]}
        return {(ruby["start"], ruby["end"]): kanji_reading}

    # Build spans of each kanji inside surface_slice (accounting for inter-kanji kana)
    spans: list[tuple[int, int]] = []
    cursor = 0
    for ruby in group:
        idx = surface_slice.find(ruby["kanji"], cursor)
        if idx < 0:
            spans = []
            break
        spans.append((idx, idx + len(ruby["kanji"])))
        cursor = idx + len(ruby["kanji"])

    if spans:
        aligned = align_kanji_readings(surface_slice, kanji_reading, spans)
        if aligned and len(aligned) == len(group) and all(aligned):
            return {
                (group[i]["start"], group[i]["end"]): aligned[i]
                for i in range(len(group))
            }

    parts = [ruby["kanji"] for ruby in group]
    split = split_reading(parts, kanji_reading, kanji_readings, exact_lookup)
    if split is None:
        split = [
            kanji_reading if len(parts) == 1 else exact_lookup.get(part, part)
            for part in parts
        ]

    return {
        (group[i]["start"], group[i]["end"]): split[i] for i in range(len(group))
    }


def fill_inner_html(
    inner_html: str,
    tagger: fugashi.Tagger,
    kanji_readings: dict[str, list[str]],
    exact_lookup: dict[str, str],
) -> str:
    if "<rt>?</rt>" not in inner_html and not re.search(r"<rt></rt>", inner_html):
        return inner_html

    plain = plain_text_from_verse(inner_html)
    tokens = tokenize(plain, tagger)
    rubies = parse_rubies(inner_html)
    groups = group_rubies(rubies, tokens)

    reading_map: dict[tuple[int, int], str] = {}
    for group in groups:
        reading_map.update(
            readings_for_group(group, tokens, tagger, kanji_readings, exact_lookup)
        )

    pos = 0
    i = 0
    out: list[str] = []

    while i < len(inner_html):
        match = RUBY_RE.match(inner_html, i)
        if match:
            kanji, rt = match.group(1), match.group(2)
            start = pos
            end = pos + len(kanji)
            pos = end
            if rt in ("?", ""):
                reading = reading_map.get((start, end), exact_lookup.get(kanji, kanji))
                if not reading or reading == kanji or (
                    len(reading) == 1 and KANJI_RE.fullmatch(reading)
                ):
                    token = find_token(tokens, start, end)
                    if token:
                        reading = token["reading"]
                out.append(f"<ruby>{kanji}<rt>{reading}</rt></ruby>")
            else:
                out.append(match.group(0))
            i = match.end()
            continue
        if BR_RE.match(inner_html, i):
            out.append(BR_RE.match(inner_html, i).group(0))
            i = BR_RE.match(inner_html, i).end()
            continue
        tag = TAG_RE.match(inner_html, i)
        if tag:
            out.append(tag.group(0))
            i = tag.end()
            continue
        out.append(inner_html[i])
        if not is_formatting_char(inner_html[i]):
            pos += 1
        i += 1

    return "".join(out)


def reset_placeholders(inner_html: str) -> str:
    return RUBY_RE.sub(
        lambda m: f"<ruby>{m.group(1)}<rt>?</rt></ruby>",
        inner_html,
    )


def process_file(
    path: Path,
    tagger: fugashi.Tagger,
    kanji_readings: dict[str, list[str]],
    exact_lookup: dict[str, str],
    reset: bool = False,
) -> int:
    html = path.read_text(encoding="utf-8")
    filled = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal filled
        open_tag, inner, close_tag = match.group(1), match.group(2), match.group(3)
        if reset:
            inner = reset_placeholders(inner)
        if "<rt>?</rt>" not in inner and "<rt></rt>" not in inner:
            return f"{open_tag}{inner}{close_tag}"
        before = inner.count("<rt>?</rt>") + len(re.findall(r"<rt></rt>", inner))
        new_inner = fill_inner_html(inner, tagger, kanji_readings, exact_lookup)
        filled += before
        return f"{open_tag}{new_inner}{close_tag}"

    new_html = JP_VERSE_RE.sub(repl, html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
    return filled


def main() -> None:
    start = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 7
    end = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 27
    reset = "--reset" in sys.argv

    exact_lookup = load_exact_lookup()
    kanji_readings = load_kanji_readings()
    tagger = fugashi.Tagger()

    total = 0
    for n in range(start, end + 1):
        path = LESSONS_DIR / f"lesson_{n:02d}.html"
        if not path.exists():
            print(f"skip (missing): {path.name}")
            continue
        count = process_file(path, tagger, kanji_readings, exact_lookup, reset=reset)
        remaining = path.read_text(encoding="utf-8").count("<rt>?</rt>")
        print(f"{path.name}: filled {count}, remaining {remaining}")
        total += count
    print(f"done — {total} rt tags filled")


if __name__ == "__main__":
    main()
