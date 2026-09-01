#!/usr/bin/env python3
"""Convert guided-song Start Here rooms to Watch & Listen | Read dual panels."""

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1]
START_HERE = ROOT / "start-here"

DUAL_MODE_ROOMS = [1, 3, 5, 17, 18, 24, 25, 40]

TOGGLE_HTML = """
        <div
          class="pathway-mode reveal"
          data-watch-mode
          role="group"
          aria-label="Watch &amp; Listen or Read"
        >
          <button type="button" data-watch-select="watch" aria-pressed="true">
            Watch &amp; Listen
          </button>
          <button type="button" data-watch-select="read" aria-pressed="false">Read</button>
        </div>
"""


def _clone(tag: Tag | None) -> str:
    if tag is None:
        return ""
    return str(tag)


def _children_html(parent: Tag) -> str:
    parts: list[str] = []
    for child in parent.children:
        if isinstance(child, (Comment, NavigableString)):
            text = str(child)
            if text.strip():
                parts.append(text)
        elif isinstance(child, Tag):
            parts.append(str(child))
    return "".join(parts)


def _strip_leading_nav(container: Tag) -> None:
    nav = container.find("nav", class_=lambda c: c and "pathway-nav" in c)
    if nav:
        nav.decompose()


def _extract_trailing_blocks(container: Tag) -> tuple[list[Tag], Tag | None]:
    """Pull standalone Sensei mounts and room-forward out of the read panel."""
    sensei_blocks: list[Tag] = []
    room_forward: Tag | None = None

    for el in list(container.find_all("div", attrs={"data-chat-sensei": True})):
        if el.find_parent("aside", class_=lambda c: c and "pathway-source" in (c or "")):
            continue
        sensei_blocks.append(el.extract())

    forward = container.find("div", class_=lambda c: c and "room-forward" in (c or ""))
    if forward:
        room_forward = forward.extract()

    return sensei_blocks, room_forward


def _fix_boolean_attrs(html: str) -> str:
    html = html.replace(' defer="True"', " defer")
    html = html.replace(' hidden="True"', " hidden")
    html = re.sub(r' data-watch-read="True"', " data-watch-read", html)
    html = re.sub(r' data-watch-watch="True"', " data-watch-watch", html)
    html = re.sub(r' data-watch-mode=""', " data-watch-mode", html)
    return html


def convert_room(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "data-watch-mode" in text:
        return False
    if 'id="listen-youtube"' not in text or 'id="after"' not in text:
        return False

    soup = BeautifulSoup(text, "html.parser")
    main = soup.find("main")
    if not main:
        return False

    film_section = main.find("section", id="listen-youtube")
    after_section = main.find("section", id="after")
    if not film_section or not after_section:
        return False

    film_container = film_section.find("div", class_="room-container")
    after_container = after_section.find("div", class_="room-container")
    if not film_container or not after_container:
        return False

    nav_html = _clone(film_container.find("nav"))
    header_html = _clone(film_container.find("header"))
    film_html = _clone(
        film_container.find(
            "article",
            class_=lambda c: c and "pathway-film-exhibit" in (c or ""),
        )
    )

    _strip_leading_nav(after_container)
    sensei_blocks, room_forward = _extract_trailing_blocks(after_container)
    read_html = _children_html(after_container).strip()

    lesson = soup.new_tag("section", attrs={"class": "room-section", "id": "lesson"})
    container = soup.new_tag("div", attrs={"class": "room-container"})
    lesson.append(container)

    for block_html in (nav_html, header_html):
        if block_html.strip():
            container.append(BeautifulSoup(block_html, "html.parser"))

    container.append(BeautifulSoup(TOGGLE_HTML, "html.parser"))

    read_panel = soup.new_tag("div")
    read_panel["data-watch-read"] = ""
    read_panel["hidden"] = ""
    read_panel.append(BeautifulSoup(read_html, "html.parser"))
    container.append(read_panel)

    watch_panel = soup.new_tag("div")
    watch_panel["data-watch-watch"] = ""
    watch_panel.append(BeautifulSoup(film_html, "html.parser"))
    container.append(watch_panel)

    for block in sensei_blocks:
        container.append(block)
    if room_forward is not None:
        container.append(room_forward)

    main.clear()
    main.append(NavigableString("\n\n    "))
    main.append(lesson)
    main.append(NavigableString("\n  "))

    body = soup.find("body")
    if body:
        classes = body.get("class", [])
        if "is-watch-mode" not in classes:
            body["class"] = classes + ["is-watch-mode"]

    skip = soup.find("a", class_="skip-link")
    if skip:
        skip.clear()
        skip["href"] = "#lesson"
        skip.append("Skip to lesson")

    head = soup.find("head")
    if head and not head.find("script", src=re.compile(r"beginner-watch\.js")):
        watch_script = soup.new_tag("script", src="../js/beginner-watch.js")
        watch_script["defer"] = ""
        lesson_script = head.find("script", src=re.compile(r"beginner-lesson\.js"))
        if lesson_script:
            lesson_script.insert_after(watch_script)
        else:
            head.append(watch_script)

    output = _fix_boolean_attrs(str(soup))
    path.write_text(output, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for room_id in DUAL_MODE_ROOMS:
        html_path = START_HERE / f"lesson-{room_id}" / "index.html"
        if not html_path.exists():
            print(f"Missing {html_path}")
            continue
        if convert_room(html_path):
            changed += 1
            print(html_path.relative_to(ROOT))
    print(f"Converted {changed} guided-song rooms.")


if __name__ == "__main__":
    main()
