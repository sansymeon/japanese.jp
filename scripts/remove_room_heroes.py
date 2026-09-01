#!/usr/bin/env python3
"""Remove decorative room-hero sections from Start Here study rooms."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START_HERE = ROOT / "start-here"

HERO_SECTION = re.compile(
    r"\n[ \t]*<section class=\"room-hero\"[\s\S]*?</section>\n",
    re.MULTILINE,
)

HERO_INNER = re.compile(
    r"<div class=\"room-hero-inner\">([\s\S]*?)</div>\s*\n[ \t]*<a class=\"room-hero-scroll\"",
    re.MULTILINE,
)

BRAND = re.compile(r'<p class="room-hero-brand">([^<]+)</p>')
H1 = re.compile(r'<h1 id="lesson-heading">([\s\S]*?)</h1>')
LEAD = re.compile(r'<p class="room-hero-lead">([\s\S]*?)</p>')

NAV_END = re.compile(
    r'(<nav class="pathway-nav pathway-nav--top reveal"[\s\S]*?</nav>\n)',
    re.MULTILINE,
)


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def build_head(brand: str, title: str, lead: str) -> str:
    lines = [
        "",
        '        <header class="room-section-head reveal room-page-head">',
        f'          <p class="room-eyebrow">{brand}</p>',
        f'          <h1 id="lesson-heading">{title}</h1>',
    ]
    if lead:
        lines.append(f"          <p>{lead}</p>")
    lines.append("        </header>")
    lines.append("")
    return "\n".join(lines)


def lesson_has_page_head(html: str) -> bool:
    if "room-page-head" in html:
        return True
    return bool(
        re.search(
            r'id="lesson"[\s\S]*?<div class="room-container">\s*\n\s*<nav[\s\S]*?</nav>\s*\n\s*<header class="room-section-head',
            html,
        )
    )


def main() -> None:
    updated = 0
    for n in range(41):
        path = START_HERE / f"lesson-{n}" / "index.html"
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        if "room-hero" not in html:
            continue

        inner_match = HERO_INNER.search(html)
        brand = title = lead = ""
        if inner_match:
            inner = inner_match.group(1)
            brand_m = BRAND.search(inner)
            h1_m = H1.search(inner)
            lead_m = LEAD.search(inner)
            brand = brand_m.group(1).strip() if brand_m else "Beginner pathway"
            title = compact(h1_m.group(1)) if h1_m else ""
            lead = compact(lead_m.group(1)) if lead_m else ""

        new_html = HERO_SECTION.sub("\n", html, count=1)

        if n == 39:
            new_html = new_html.replace(
                "<h2>Room 39</h2>",
                '<h1 id="lesson-heading">Room 39</h1>',
                1,
            )
        elif title and not lesson_has_page_head(new_html):
            head = build_head(brand, title, lead)
            new_html, count = NAV_END.subn(r"\1" + head, new_html, count=1)
            if count == 0:
                new_html = new_html.replace(
                    '<div class="room-container">\n',
                    '<div class="room-container">\n' + head,
                    1,
                )

        new_html = re.sub(r"\n{4,}", "\n\n\n", new_html)
        if new_html != html:
            path.write_text(new_html, encoding="utf-8")
            updated += 1

    print(f"Removed decorative heroes from {updated} lesson pages.")


if __name__ == "__main__":
    main()
