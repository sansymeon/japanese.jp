#!/usr/bin/env python3
"""Build Kanji Components collections from lesson HTML (canonical).

Source policy
-------------
- Lesson HTML is the canonical source of all KML decompositions.
- v4c is legacy: comparison / recovery only when HTML data is missing.
- If HTML and v4c disagree, HTML wins unless explicitly reported otherwise.
- Catalog labels + New Component intros remain in kanji_components_catalog.json.
- Catalog componentOverrides apply only when HTML has no parts (legacy escape hatch).

Rebuild the HTML database first when needed:
  python3 ../../scripts/build_kml_component_database.py

Then:
  python3 scripts/build_kanji_components.py
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KML_ROOT = ROOT.parents[1]
CATALOG_PATH = ROOT / "data" / "kanji_components_catalog.json"
HTML_DB_PATH = KML_ROOT / "data" / "kanji" / "kml_component_database.json"
HTML_DB_BUILD = KML_ROOT / "scripts" / "build_kml_component_database.py"
V4C_PATH = KML_ROOT / "data" / "kanji" / "kanji_master_with_components.v4c.csv"
LESSONS_HTML = KML_ROOT / "contents" / "books" / "book_01" / "lessons"
OUT_PROTO = ROOT / "collections" / "prototypes"
LESSON_DIRS = ROOT / "collections"

TIMING = {
    "heroFadeInMs": 1800,
    "afterHeroPauseMs": 900,
    "componentArriveMs": 1400,
    "componentStaggerMs": 1700,
    "afterComponentsPauseMs": 1400,
    "keywordFadeInMs": 1400,
    "keywordHoldMs": 3200,
    "keywordFadeOutMs": 1100,
    "afterKeywordsPauseMs": 900,
    "componentsFadeOutMs": 1600,
    "heroAloneMs": 2400,
    "crossfadeMs": 1600,
    "blackBetweenMs": 700,
    "crestBlackBeforeMs": 900,
    "crestRevealMs": 2800,
    "crestHoldMs": 1400,
    "soundtrackFadeMs": 8000,
    "crestFadeOutMs": 3500,
    "crestBlackAfterMs": 800,
}

DEFAULT_INTRO_TIMING = {
    "headingFadeInMs": 1400,
    "glyphFadeInMs": 2000,
    "glyphAloneHoldMs": 2800,
    "labelFadeInMs": 1600,
    "completeHoldMs": 4500,
    "fadeOutMs": 1800,
    "blackAfterMs": 900,
}


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def ensure_html_db(rebuild: bool = False) -> dict:
    if rebuild or not HTML_DB_PATH.exists():
        subprocess.run(
            [sys.executable, str(HTML_DB_BUILD)],
            check=True,
            cwd=KML_ROOT,
        )
    return json.loads(HTML_DB_PATH.read_text(encoding="utf-8"))


def load_v4c_legacy() -> dict[str, dict]:
    """Legacy reference only — used when HTML has no parts."""
    by_kanji: dict[str, dict] = {}
    if not V4C_PATH.exists():
        return by_kanji
    with V4C_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            k = row["kanji"]
            if k not in by_kanji:
                by_kanji[k] = row
    return by_kanji


def foundations_path(lesson: int) -> Path:
    p = ROOT / "exhibition" / f"lesson_{lesson}_foundations.json"
    if p.exists():
        return p
    alt = ROOT / "ambient_exhibitions" / f"lesson_{lesson}_foundations.json"
    if alt.exists():
        return alt
    raise FileNotFoundError(f"No foundations JSON for lesson {lesson}")


def scenes_from_html_lesson(lesson: int, html_db: dict) -> list[dict]:
    """Lesson order + keywords from HTML DB (and live HTML if needed)."""
    # Prefer live HTML order so we never miss a kanji whose first-seen
    # lesson in the DB differs from this lesson file.
    sys.path.insert(0, str(KML_ROOT))
    from lib.html_component_parser import parse_lesson_html

    path = LESSONS_HTML / f"lesson_{lesson:02d}.html"
    if not path.exists():
        raise FileNotFoundError(path)
    return [
        {"kanji": d.kanji, "keyword": d.keyword, "slug": d.slug}
        for d in parse_lesson_html(path, lesson)
    ]


def load_lesson_scenes(lesson: int, html_db: dict) -> list[dict]:
    """Foundations if present; otherwise HTML lesson order."""
    try:
        found = json.loads(foundations_path(lesson).read_text(encoding="utf-8"))
        scenes = found.get("scenes") or []
        if scenes:
            return [
                {"kanji": s["kanji"], "keyword": s["keyword"], "slug": s.get("id", "")}
                for s in scenes
            ]
    except FileNotFoundError:
        pass
    return scenes_from_html_lesson(lesson, html_db)


def slugify(keyword: str) -> str:
    s = keyword.strip().lower().replace("'", "").replace("-", " ")
    return "_".join(s.split())


def normalize_glyph(glyph: str, catalog: dict) -> str:
    return catalog.get("glyphNormalize", {}).get(glyph, glyph)


def label_for(glyph: str, keyword_by_kanji: dict[str, str], catalog: dict) -> str:
    g = normalize_glyph(glyph, catalog)
    labels = catalog.get("componentLabels", {})
    # Approved component labels win over incidental DB keywords.
    if g in labels:
        return labels[g]
    if glyph in labels:
        return labels[glyph]
    if g in keyword_by_kanji:
        return keyword_by_kanji[g]
    return keyword_by_kanji.get(glyph, g)


def parts_for_kanji(
    kanji: str,
    html_db: dict,
    v4c: dict[str, dict],
    catalog: dict,
) -> tuple[list[str], str]:
    """Return (parts, source_tag).

    Reviewed HTML is canonical. Self-reference parts are placeholder remnants
    (not editorial) and are stripped. v4c / catalog overrides only if no usable
    HTML parts remain.
    """
    html_rec = (html_db.get("kanji") or {}).get(kanji) or {}
    raw = [p for p in (html_rec.get("partsFlatRaw") or html_rec.get("partsFlat") or []) if p]
    # Prefer DB's cleaned partsFlat when present
    cleaned = [p for p in (html_rec.get("partsFlat") or []) if p]
    if not cleaned and raw:
        cleaned = [p for p in raw if p != kanji]

    if cleaned:
        return cleaned, "html"
    if raw == [kanji]:
        return raw, "html_anchor"

    overrides = catalog.get("componentOverrides") or {}
    if kanji in overrides:
        parts = [p for p in overrides[kanji] if p]
        if parts:
            return parts, "catalog_override"

    row = v4c.get(kanji)
    if row:
        parts = [p for p in (row.get("kml_primitives") or "").split("|") if p]
        if parts:
            return parts, "v4c_fallback"

    return [], "absent"


def components_for(
    kanji: str,
    html_db: dict,
    v4c: dict[str, dict],
    keyword_by_kanji: dict[str, str],
    catalog: dict,
) -> list[dict]:
    family_on = catalog.get("familyOnGlyph") or {}
    parts, source = parts_for_kanji(kanji, html_db, v4c, catalog)

    if not parts:
        return [{"glyph": kanji, "label": keyword_by_kanji.get(kanji, kanji)}]

    # Anchor: single part equal to the kanji itself
    if parts == [kanji]:
        return [{"glyph": kanji, "label": keyword_by_kanji.get(kanji, kanji)}]

    out: list[dict] = []
    for raw in parts:
        # Phase 1: keep approved HTML glyphs as-is. Normalize only for
        # label / family lookup.
        g_lookup = normalize_glyph(raw, catalog)
        glyph = raw if source in ("html", "html_anchor") else g_lookup
        item: dict = {
            "glyph": glyph,
            "label": label_for(raw, keyword_by_kanji, catalog),
        }
        fam = family_on.get(g_lookup) or family_on.get(glyph)
        if fam:
            item["familyId"] = fam
        out.append(item)
    return out


def intro_map(catalog: dict) -> dict[tuple[int, str], tuple[str, str]]:
    out: dict[tuple[int, str], tuple[str, str]] = {}
    for item in catalog.get("introductions") or []:
        key = (int(item["lesson"]), item["beforeKanji"])
        out[key] = (item["glyph"], item["label"])
    return out


def family_intro_map(catalog: dict) -> dict[tuple[int, str], tuple[str, str, str]]:
    out: dict[tuple[int, str], tuple[str, str, str]] = {}
    for item in catalog.get("familyIntros") or []:
        key = (int(item["lesson"]), item["beforeKanji"])
        out[key] = (item["familyId"], item["glyph"], item["label"])
    return out


def build_keyword_index(lesson: int, html_db: dict) -> dict[str, str]:
    """Keywords for lesson kanji taught so far (foundations), else HTML lesson files."""
    keyword_by_kanji: dict[str, str] = {}
    for n in range(1, lesson + 1):
        try:
            earlier = json.loads(foundations_path(n).read_text(encoding="utf-8"))
            for s in earlier.get("scenes") or []:
                keyword_by_kanji[s["kanji"]] = s["keyword"]
            continue
        except FileNotFoundError:
            pass
        # No foundations yet — pull keywords from this lesson's HTML only
        try:
            for s in scenes_from_html_lesson(n, html_db):
                keyword_by_kanji[s["kanji"]] = s["keyword"]
        except FileNotFoundError:
            pass
    return keyword_by_kanji


def build_lesson(lesson: int, html_db: dict, v4c: dict[str, dict], catalog: dict) -> dict:
    scenes_in = load_lesson_scenes(lesson, html_db)
    keyword_by_kanji = build_keyword_index(lesson, html_db)

    new_components = intro_map(catalog)
    new_families = family_intro_map(catalog)
    scenes: list[dict] = []
    sources_used: set[str] = set()

    for s in scenes_in:
        kanji = s["kanji"]
        keyword = s["keyword"]

        intro = new_components.get((lesson, kanji))
        if intro:
            glyph, label = intro
            scenes.append(
                {
                    "type": "newComponent",
                    "id": f"L{lesson:02d}_intro_{slugify(label)}",
                    "glyph": glyph,
                    "label": label,
                }
            )

        fam = new_families.get((lesson, kanji))
        if fam:
            family_id, glyph, label = fam
            scenes.append(
                {
                    "type": "newFamily",
                    "id": f"L{lesson:02d}_family_{family_id}",
                    "familyId": family_id,
                    "glyph": glyph,
                    "label": label,
                }
            )

        _parts, src = parts_for_kanji(kanji, html_db, v4c, catalog)
        sources_used.add(src)

        scenes.append(
            {
                "type": "kanji",
                "id": f"L{lesson:02d}_{slugify(keyword)}",
                "kanji": kanji,
                "keyword": keyword,
                "components": components_for(
                    kanji, html_db, v4c, keyword_by_kanji, catalog
                ),
            }
        )

    pad = f"{lesson:02d}"
    used_family_ids = set()
    for sc in scenes:
        if sc.get("type") == "newFamily":
            used_family_ids.add(sc["familyId"])
        for c in sc.get("components") or []:
            if c.get("familyId"):
                used_family_ids.add(c["familyId"])
    all_families = catalog.get("families") or {}
    families = {fid: all_families[fid] for fid in used_family_ids if fid in all_families}

    intro_timing = {
        **DEFAULT_INTRO_TIMING,
        **(catalog.get("introTiming") or {}),
    }

    return {
        "presentation": "kanjiComponents",
        "id": f"lesson_{pad}_components",
        "title": f"Lesson {lesson} — Kanji Components",
        "notes": (
            "Kanji + Component visual literacy (Family support ready, deferred). "
            "Decompositions from lesson HTML (canonical). "
            "Catalog: data/kanji_components_catalog.json. "
            "Rebuild: python3 scripts/build_kanji_components.py"
        ),
        "soundtrack": {
            "main": "audio/kanji_components.mp3",
            "loop": True,
        },
        "bookends": {
            "mode": "silentCrest",
            "closing": {
                "image": "assets/images/gold_closing.png",
                "bookendSize": "small",
            },
        },
        "families": families,
        "timing": TIMING,
        "introTiming": intro_timing,
        "display": {
            "loop": False,
            "hideChrome": True,
            "family": "kanjiComponents",
            "typography": "kanji-components",
        },
        "meta": {
            "prototype": True,
            "theme": "kanjiComponents",
            "stage": "components",
            "lesson": lesson,
            "sceneCount": len(scenes),
            "source": "lesson_html",
            "sourcePolicy": (
                "Reviewed lesson HTML is canonical. Original component/v4c data was "
                "placeholder scaffolding, not editorial intent. Self-reference parts "
                "are stripped as placeholder remnants. v4c only if HTML has no usable parts."
            ),
            "htmlDatabase": "data/kanji/kml_component_database.json",
            "catalog": "data/kanji_components_catalog.json",
            "partSourcesUsed": sorted(sources_used),
            "schema": "kanji|newComponent|newFamily",
        },
        "scenes": scenes,
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n_intro = sum(1 for s in data["scenes"] if s.get("type") == "newComponent")
    n_fam = sum(1 for s in data["scenes"] if s.get("type") == "newFamily")
    print(
        f"wrote {path.relative_to(ROOT)} "
        f"({data['meta']['sceneCount']} scenes, {n_intro} intros, {n_fam} families)"
    )


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rebuild-html-db", action="store_true")
    ap.add_argument("--max-lesson", type=int, default=30)
    args = ap.parse_args()

    catalog = load_catalog()
    html_db = ensure_html_db(rebuild=args.rebuild_html_db)
    v4c = load_v4c_legacy()
    OUT_PROTO.mkdir(parents=True, exist_ok=True)

    for lesson in range(1, args.max_lesson + 1):
        data = build_lesson(lesson, html_db, v4c, catalog)
        pad = f"{lesson:02d}"
        write_json(LESSON_DIRS / f"lesson_{pad}" / f"lesson_{pad}_components.json", data)

        proto = dict(data)
        proto["id"] = f"proto_lesson_{pad}_components"
        proto["meta"] = dict(data["meta"])
        proto["meta"]["prototype"] = True
        write_json(OUT_PROTO / f"proto_lesson_{pad}_components.json", proto)


if __name__ == "__main__":
    main()
