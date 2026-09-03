#!/usr/bin/env python3
"""Apply / refresh Lesson bottom YouTube media-card CTAs from lesson_media_urls.json.

Does not embed players or link local ambient/compounds media. Empty slots use
the matching placeholder until real YouTube URLs are filled in.

After editing kml/data/lesson_media_urls.json, run this script to bake URLs
and labels into all classic lesson pages.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS = ROOT / "contents/books/book_01/lessons"
MEDIA_PATH = ROOT / "data/lesson_media_urls.json"

CTA_RE = re.compile(
    r"<!-- CTA(?: — YouTube media cards \(no local video/audio\))? -->\s*"
    r'<div class="cta">.*?</div>\s*(?=<!-- STAMPS -->|<!--STAMPS-->|<div class="stamps">)',
    re.S,
)

# Canonical JSON keys, with aliases kept so older files still apply.
SLOT_KEYS = {
    "compounds": ("compounds",),
    "playlist": ("playlist", "ambient"),
    "gallery": ("gallery", "exhibition"),
}


def load_media():
    raw = json.loads(MEDIA_PATH.read_text(encoding="utf-8"))
    placeholder = str(
        raw.get("_placeholder") or "https://www.youtube.com/@ambientkanji"
    ).strip()
    gallery_placeholder = str(
        raw.get("_gallery_placeholder") or placeholder
    ).strip() or placeholder
    media = {
        str(k): {
            slot: str(url).strip()
            for slot, url in v.items()
            if isinstance(url, str)
        }
        for k, v in raw.items()
        if not str(k).startswith("_") and isinstance(v, dict)
    }
    return placeholder, gallery_placeholder, media


def url_for(media, placeholder, gallery_placeholder, lesson_num: int, slot: str) -> str:
    entry = media.get(str(lesson_num), {})
    for key in SLOT_KEYS[slot]:
        url = (entry.get(key) or "").strip()
        if url:
            return url
    if slot == "gallery":
        return gallery_placeholder
    return placeholder


def build_cta(lesson_num: int, media, placeholder: str, gallery_placeholder: str) -> str:
    return f"""<!-- CTA — YouTube media cards (no local video/audio) -->
<div class="cta">
  <a class="btn-compounds"
     href="{url_for(media, placeholder, gallery_placeholder, lesson_num, "compounds")}"
     target="_blank"
     rel="noopener noreferrer">
    ▶️ View Common Compounds for Lesson {lesson_num}
  </a>
  <a class="btn-compounds"
     href="{url_for(media, placeholder, gallery_placeholder, lesson_num, "playlist")}"
     target="_blank"
     rel="noopener noreferrer">
    🎬 Lesson {lesson_num} Playlist
  </a>
  <a class="btn-compounds"
     href="{url_for(media, placeholder, gallery_placeholder, lesson_num, "gallery")}"
     target="_blank"
     rel="noopener noreferrer">
    🖼️ Digital Art Gallery
  </a>
</div>

"""


def main() -> None:
    placeholder, gallery_placeholder, media = load_media()
    updated = 0
    skipped = 0
    for path in sorted(LESSONS.glob("lesson_*.html")):
        match = re.search(r"lesson_(\d+)\.html$", path.name)
        if not match:
            continue
        n = int(match.group(1))
        text = path.read_text(encoding="utf-8")
        if not CTA_RE.search(text):
            if "btn-compounds" in text:
                raise SystemExit(f"CTA block not found/replaced in {path.name}")
            skipped += 1
            continue
        new_text, count = CTA_RE.subn(
            build_cta(n, media, placeholder, gallery_placeholder), text, count=1
        )
        if count != 1:
            raise SystemExit(f"CTA block not found/replaced in {path.name}")
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            updated += 1
    print(
        f"Refreshed media-card CTAs ({updated} files changed"
        + (f", {skipped} skipped" if skipped else "")
        + ")."
    )


if __name__ == "__main__":
    main()
