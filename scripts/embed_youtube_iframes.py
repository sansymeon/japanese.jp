#!/usr/bin/env python3
"""Embed static YouTube iframes in Start Here rooms (Room 39 pattern)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START_HERE = ROOT / "start-here"
COURSE_JS = START_HERE / "js" / "beginner-course.js"

IFRAME_BLOCK = """            <div class="pathway-film">
              <iframe
                src="https://www.youtube.com/embed/{youtube_id}?rel=0&modestbranding=1"
                title="{title}"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                referrerpolicy="strict-origin-when-cross-origin"
                allowfullscreen
              ></iframe>
            </div>"""

PENDING_BLOCK = re.compile(
    r"\n\s*<p class=\"pathway-watch-pending\" data-watch-pending hidden>[\s\S]*?</p>",
    re.MULTILINE,
)

WATCH_FILM_EMPTY = re.compile(
    r"<div data-watch-film></div>",
    re.MULTILINE,
)

GUIDED_IFRAME = re.compile(
    r"<article class=\"beginner-exhibit pathway-film-exhibit reveal\">\s*"
    r"<div class=\"pathway-film\">\s*"
    r"<iframe[\s\S]*?</iframe>\s*"
    r"</div>\s*"
    r"</article>",
    re.MULTILINE,
)


def parse_youtube_ids() -> dict[str, str]:
    text = COURSE_JS.read_text(encoding="utf-8")
    ids: dict[str, str] = {}
    for match in re.finditer(
        r'"(\d+)":\s*\{[^}]*?watchYoutubeId:\s*"([^"]+)"',
        text,
        re.DOTALL,
    ):
        ids[match.group(1)] = match.group(2)
    return ids


def page_title(html: str) -> str:
    match = re.search(r"<title>([^<]+)</title>", html)
    return match.group(1).strip() if match else "Start Here"


def embed_study_room(path: Path, youtube_id: str) -> bool:
    html = path.read_text(encoding="utf-8")
    if not WATCH_FILM_EMPTY.search(html):
        return False
    title = page_title(html).replace('"', "&quot;")
    block = IFRAME_BLOCK.format(youtube_id=youtube_id, title=title)
    html = WATCH_FILM_EMPTY.sub(block, html, count=1)
    html = PENDING_BLOCK.sub("", html)
    path.write_text(html, encoding="utf-8")
    return True


def normalize_guided_iframe(path: Path, youtube_id: str) -> bool:
    html = path.read_text(encoding="utf-8")
    if WATCH_FILM_EMPTY.search(html):
        return False
    title = page_title(html).replace('"', "&quot;")
    block = (
        '<article class="beginner-exhibit pathway-film-exhibit reveal">\n'
        + IFRAME_BLOCK.format(youtube_id=youtube_id, title=title)
        + "\n        </article>"
    )

    def repl(_: re.Match[str]) -> str:
        return block

    new_html, count = GUIDED_IFRAME.subn(repl, html, count=1)
    if count:
        path.write_text(new_html, encoding="utf-8")
    return count > 0


def main() -> None:
    youtube_ids = parse_youtube_ids()
    study = 0
    guided = 0
    for room_id, yt_id in sorted(youtube_ids.items(), key=lambda x: int(x[0])):
        path = START_HERE / f"lesson-{room_id}" / "index.html"
        if not path.exists():
            continue
        if embed_study_room(path, yt_id):
            study += 1
        elif normalize_guided_iframe(path, yt_id):
            guided += 1
    print(f"Embedded static iframes in {study} study rooms; normalized {guided} guided rooms.")


if __name__ == "__main__":
    main()
