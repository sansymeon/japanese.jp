#!/usr/bin/env python3
"""Parse Start Here study-room HTML into film beat specs."""

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1]
LESSON_DIR = ROOT / "start-here"


def _text(el: Tag | None) -> str:
    if not el:
        return ""
    return re.sub(r"\s+", " ", el.get_text()).strip()


def _hiragana_from_verse(el: Tag) -> str:
    parts: list[str] = []

    def walk(node) -> None:
        if isinstance(node, NavigableString):
            parts.append(str(node))
            return
        if not isinstance(node, Tag):
            return
        if node.name == "rt":
            return
        if node.name == "ruby":
            rt = node.find("rt")
            if rt:
                parts.append(_text(rt))
            else:
                for child in node.children:
                    if getattr(child, "name", None) != "rt":
                        walk(child)
            return
        for child in node.children:
            walk(child)

    for child in el.children:
        walk(child)
    text = "".join(parts)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def resolve_image(src: str) -> Path:
    if src.startswith("../"):
        path = LESSON_DIR / src.removeprefix("../")
    elif src.startswith("../../"):
        path = ROOT / src.removeprefix("../../")
    else:
        path = ROOT / src
    return path


def slug_from_html(raw: str, room_id: int) -> str:
    m = re.search(r"<title>Room \d+ — ([^—<]+)", raw)
    if m:
        base = re.sub(r"[^\w\s-]", "", m.group(1).strip().lower())
        base = re.sub(r"\s+", "-", base).strip("-")
        if base:
            return base[:48]
    return f"room-{room_id}"


def parse_lesson(room_id: int) -> dict:
    html_path = LESSON_DIR / f"lesson-{room_id}" / "index.html"
    raw = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")
    lesson = soup.find("section", id="lesson")
    if not lesson:
        raise ValueError(f"Room {room_id}: no #lesson section")

    beats: list[dict] = []
    review_flags: list[str] = []
    exhibit_images: list[str] = []

    hero = soup.select_one(".room-hero-media img")
    hero_src = hero["src"] if hero and hero.get("src") else None
    default_image = resolve_image(hero_src) if hero_src else ROOT / "kml/assets/studies/room.png"

    def add_beat(beat: dict) -> None:
        if beat.get("image"):
            src = beat["image"]
            beat["image"] = str(resolve_image(src))
            exhibit_images.append(src)
        beats.append(beat)

    # Walk direct pedagogical children of .room-container
    container = lesson.find(class_="room-container")
    if not container:
        container = lesson

    for el in container.children:
        if not isinstance(el, Tag):
            continue
        cls = " ".join(el.get("class") or [])
        if el.name in {"nav", "aside"} or "pathway-nav" in cls or "pathway-source" in cls:
            continue
        if "room-forward" in cls or "beginner-assist" in cls:
            continue
        if el.name == "header" and "room-section-head" in cls:
            continue
        if el.name == "div" and el.get("data-chat-sensei") is not None:
            continue

        if el.name == "article" and "beginner-exhibit" in cls:
            img = el.find("img")
            img_src = img["src"] if img and img.get("src") else None
            if "pathway-kml-verse" in cls:
                verse_el = el.select_one(".jp-verse")
                if verse_el:
                    add_beat(
                        {
                            "kind": "verse",
                            "text": _hiragana_from_verse(verse_el),
                            "image": img_src,
                        }
                    )
                continue
            block = el.select_one(".jp-block")
            if block:
                add_beat(
                    {
                        "kind": "exhibit",
                        "kana": _text(block.select_one(".jp-kana")),
                        "romaji": _text(block.select_one(".jp-romaji")),
                        "en": _text(block.select_one(".jp-en")),
                        "image": img_src,
                    }
                )
            elif img_src:
                add_beat({"kind": "pause", "image": img_src})
            continue

        if el.name == "figure" and "jp-unpack" in cls:
            en = _text(el.select_one(".jp-en"))
            # Prefer the gloss after an em dash: "これ — this" → "this"
            if "—" in en:
                en = en.split("—", 1)[-1].strip()
            elif "-" in en and any("\u3040" <= ch <= "\u309f" for ch in en):
                en = en.split("-", 1)[-1].strip()
            add_beat(
                {
                    "kind": "unpack",
                    "kana": _text(el.select_one(".jp-kana")),
                    "romaji": _text(el.select_one(".jp-romaji")),
                    "en": en,
                }
            )
            continue

        if el.name == "figure" and "jp-block" in cls:
            kana = _text(el.select_one(".jp-kana"))
            if kana:
                add_beat(
                    {
                        "kind": "kana_return",
                        "kana": kana,
                        "romaji": _text(el.select_one(".jp-romaji")),
                        "en": _text(el.select_one(".jp-en")),
                    }
                )
            continue

        if el.name == "div" and "room-prose" in cls:
            if "pathway-door" in cls:
                paragraphs = [_text(p) for p in el.find_all("p")]
                text = " ".join(p for p in paragraphs if p)
                if text:
                    add_beat({"kind": "prose", "text": text})
                continue
            chunks: list[str] = []
            for child in el.children:
                if isinstance(child, Tag) and child.name == "h2":
                    t = _text(child)
                    if t:
                        chunks.append(t)
                elif isinstance(child, Tag) and child.name == "p":
                    t = _text(child)
                    if t:
                        chunks.append(t)
            text = " ".join(chunks)
            if text and "Where this came from" not in text:
                add_beat({"kind": "prose", "text": text})
            continue

        if el.name == "div" and "room-motto" in cls:
            text = _text(el)
            if text:
                add_beat({"kind": "prose", "text": text})
            continue

        if el.name == "section" and "kana-puzzle-section" in cls:
            note = _text(el.select_one(".kana-puzzle-note"))
            add_beat({"kind": "puzzle_heading", "text": "Your Hiragana"})
            if note:
                add_beat({"kind": "puzzle_note", "text": note})
            # Count line omitted in films — the chart itself is the progress update.
            add_beat({"kind": "grid"})
            continue

    # Pathway-source prose inside lesson (Room 37) — pedagogical, not the link
    source = container.find("aside", class_="pathway-source")
    if source and room_id == 37:
        prose = source.select_one(".room-prose p")
        if prose:
            text = _text(prose)
            if text:
                add_beat({"kind": "prose", "text": text})

    # Dedupe return word matching last exhibit
    cleaned: list[dict] = []
    for b in beats:
        if (
            cleaned
            and b.get("kind") == "kana_return"
            and cleaned[-1].get("kind") == "exhibit"
            and b.get("kana") == cleaned[-1].get("kana")
        ):
            continue
        cleaned.append(b)

    # Quiet beat before verses
    final: list[dict] = []
    for i, b in enumerate(cleaned):
        if b.get("kind") == "verse" and i and cleaned[i - 1].get("kind") == "prose":
            final.append(
                {
                    "kind": "pause",
                    "image": b.get("image") or str(default_image),
                }
            )
        final.append(b)

    if room_id == 37:
        prose_beat = None
        reordered: list[dict] = []
        for b in final:
            if b.get("kind") == "prose" and "You can read this now" in (b.get("text") or ""):
                prose_beat = b
                continue
            reordered.append(b)
        if prose_beat:
            idx = next(
                (i for i, b in enumerate(reordered) if b.get("kind") == "puzzle_heading"),
                len(reordered),
            )
            reordered.insert(idx, prose_beat)
        final = reordered

    if exhibit_images:
        default_image = resolve_image(exhibit_images[0])
    elif hero_src:
        default_image = resolve_image(hero_src)

    if len(exhibit_images) > 1:
        review_flags.append(f"multi_image ({len(exhibit_images)} exhibits)")
    if any(b.get("kind") == "verse" for b in final):
        review_flags.append("kml_verse")
    if room_id in {2, 4}:
        review_flags.append("text_only_layout")
    if room_id == 7:
        review_flags.append("four_picture_drill")
    if room_id == 37:
        review_flags.append("verse_only_room")
    if not any(b.get("kind") == "exhibit" for b in final):
        review_flags.append("no_standard_exhibit")

    return {
        "room_id": room_id,
        "slug": slug_from_html(raw, room_id),
        "default_image": default_image,
        "beats": final,
        "review_flags": review_flags,
    }
