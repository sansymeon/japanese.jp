#!/usr/bin/env python3
"""Build a reference-only candidate index for the 4-hour Ambient Japan scenery film.

Does not copy or modify existing image assets. Writes candidates.json + index.html.
"""

from pathlib import Path
import json
import sys
from collections import OrderedDict

ROOT = Path(__file__).resolve().parents[5]
STUDIES = ROOT / "kml/assets/studies"
ADD = STUDIES / "add_to_ambient_japan_4_seasons"
FOUR = ROOT / "kml/tools/ambient/collections/ambient_gallery_japan_4_seasons/images"
OUT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "kml/tools/ambient/scripts"
sys.path.insert(0, str(SCRIPTS))
from ambient_gallery_exclusions import load_exclude_slugs  # noqa: E402

# --- curated groups (stems). An image may appear in several groups. ---

FOUR_SEASONS = [
    "apple_blossoms", "apple_tree", "bamboo_forest", "beginning", "blue_pond",
    "cape", "capital", "castle", "castle_01", "castle_2", "chant", "cleanse",
    "coastal_view", "condition", "country_station", "country_train_summer",
    "country_train_winter", "creek", "dagashiya", "dawn", "dazaifu_shopping",
    "den", "dream", "early_evening", "eminent", "evening", "eventide", "farm",
    "field", "fishing", "fishing_village", "fishing_village_2", "flourishing",
    "ford", "forest", "futamigaura", "garden", "gokayama_winter", "good_luck",
    "guidance", "hida_furukawa", "home_village", "horizon", "ice", "illuminate",
    "imperial_gardens", "inland_sea", "japan_alps_summer", "japan_alps_summer_2",
    "japan_alps_winter", "judas_tree", "kumamoto", "kyoto", "kyoto_autumn",
    "kyoto_pagoda", "lake", "lake_toya", "large_river", "lavendar", "lively",
    "magome", "marsh", "meadow", "miyajima", "monkey_hotspring", "moon",
    "morning", "mt_fuji_2", "nara_deer", "nikko_2", "nikko_3", "nikko_fall_colors",
    "oak", "obscure", "ocean", "okinawa_temple", "olden_times", "outside",
    "overgrown", "overnight", "pagoda", "patchwork_hills", "paulownia_tree",
    "pavilion", "peach_tree", "plane", "plantation", "radiance", "raizan",
    "range", "ray", "reed", "refreshing", "rice", "rice_post_harvest", "right",
    "rise", "rising_sun", "river", "road", "saga_koinobori", "sakurajima",
    "sapporo_clock", "scenery", "senso_ji_temple", "shallow", "shining",
    "shirakawa_spring", "shirakawa_winter", "shiretoko_ice", "shopping_street",
    "shoutengai_new_store", "source", "span", "spring", "state", "sun",
    "takayama", "take_along", "tanuki", "tea_fields", "tea_shop", "temple",
    "ten_thousand", "thatched_roof", "thatched_roof_winter", "tide", "top",
    "town", "train_cherry_blossoms", "train_hydrangea", "tree", "treetops",
    "tsumago", "vague", "vermilion", "villa", "village", "virtue", "wagashi_shop",
    "walk", "water", "winter_cranes", "winter_evening", "winter_honshu", "woods",
]

# Four Seasons interiors to use only as rare exceptions (or skip).
RARE_INTERIOR = {
    "beginning", "early_evening", "eminent", "olden_times", "outside", "shining",
}

# Four Seasons images that are busy / indoor-commercial / less scenery-like.
SOFT_EXCLUDE_FROM_4S = {
    "eminent",  # closed tatami still life
    "shoutengai_new_store",  # indoor commercial
    "ten_thousand",  # busy charm close-up
}

ANCHORS = [
    # landmarks / unmistakable Japan
    "castle", "castle_01", "castle_2", "kumamoto", "king",
    "miyajima", "vermilion", "futamigaura",
    "kyoto", "kyoto_pagoda", "kyoto_autumn", "capital", "town", "weekday",
    "senso_ji_temple", "nara_deer",
    "nikko_2", "nikko_3", "nikko_fall_colors",
    "mt_fuji_2", "apple_blossoms", "acknowledge", "dream",
    "pagoda", "temple", "okinawa_temple", "chant", "good_luck",
    "bamboo_forest", "imperial_gardens", "garden", "pavilion", "water",
    "shirakawa_spring", "shirakawa_winter", "gokayama_winter", "thatched_roof",
    "thatched_roof_winter", "morning", "winter", "melt", "mulberry",
    "magome", "tsumago", "takayama", "hida_furukawa",
    "dazaifu_shopping", "right", "shopping_street", "busy", "beguile",
    "tea_fields", "rice", "field", "plane", "raizan", "sun", "fertile", "in_front",
    "saga_koinobori", "five",
    "woods", "walk", "virtue", "ice", "monkey_hotspring",
    "inland_sea", "sakurajima", "sapporo_clock",
    "about_that_time", "assurance", "ecstasy", "endure_silently",
    "visit_shrine", "righteousness", "sweet_oak", "loyalty", "location",
    "neglect", "old", "permit", "public_hall", "safeguard", "shouldering",
    "sovereign", "year_end", "weld", "intimidate", "hedge", "few", "fish",
    "curse", "conform", "constancy", "bell", "noon", "pond", "hot_water",
    "many", "remainder", "remorse", "frozen", "courtyard",
]

COUNTRYSIDE = [
    "cape", "coastal_view", "creek", "dawn", "den", "eventide", "farm",
    "forest", "flourishing", "ford", "horizon", "japan_alps_summer",
    "japan_alps_summer_2", "japan_alps_winter", "lake", "lake_toya",
    "large_river", "lavendar", "lively", "marsh", "meadow", "oak", "ocean",
    "overgrown", "patchwork_hills", "radiance", "range", "reed", "refreshing",
    "river", "scenery", "shallow", "source", "span", "spring", "state", "tide",
    "vague", "winter_cranes", "shiretoko_ice", "cleanse", "condition",
    "blue_pond", "apple_tree", "judas_tree", "peach_tree", "paulownia_tree",
    "treetops", "tree", "rice_post_harvest", "plantation", "home_village",
    "road", "village", "guidance", "evening", "overnight", "rising_sun",
    "accustomed", "annexed", "augment", "bathe", "breath", "boulder", "cliff",
    "cloud", "cloudy_weather", "current", "dike", "dilute", "distinction",
    "early", "exist", "failure", "fall", "frost", "length", "load", "method",
    "milk", "mountain", "mountain_pass", "open_sea", "prefecture", "rain",
    "rainbow", "sea", "waves", "waterfall", "stone", "storm", "sunset",
    "valve", "thick", "invariably", "lazy", "leaf", "lumber", "each",
    "environs", "run_alongside", "rut", "see", "splash", "split", "stiff",
    "sulfur", "violent", "wink", "wither", "vast", "wide", "sheep", "signal",
    "ardent", "clear_land", "country", "crossing", "grains_of_sand",
    "horse_chestnut", "kudzu", "plank", "promontory", "prosperous", "pursue",
    "revolve", "robust", "selfish", "valley",
]

SPRING = [
    "castle", "apple_blossoms", "peach_tree", "judas_tree", "spring",
    "shirakawa_spring", "train_cherry_blossoms", "saga_koinobori", "five",
    "walk", "woods", "radiance", "ray", "flourishing", "plantation",
    "paulownia_tree", "ume", "woman", "remorse", "orderliness", "hedge",
    "incur", "metaphor", "core", "plump",
]

SUMMER = [
    "bamboo_forest", "tea_fields", "rice", "field", "miyajima", "pagoda",
    "temple", "thatched_roof", "train_hydrangea", "country_train_summer",
    "country_station", "japan_alps_summer", "japan_alps_summer_2",
    "lavendar", "patchwork_hills", "okinawa_temple", "lively", "refreshing",
    "source", "waterfall", "forest", "overgrown", "creek", "ford",
    "lightning_bug", "hot_water", "noon", "fertile", "each", "milk",
]

AUTUMN = [
    "kyoto_autumn", "nikko_fall_colors", "nikko_2", "nikko_3", "lake_toya",
    "rice", "rice_post_harvest", "reed", "scenery", "tree", "oak", "meadow",
    "farm", "radiance", "water", "persimmon", "pond", "fall", "eternity",
    "recess", "wither", "younger_sister", "widow", "apple_tree",
]

WINTER = [
    "mt_fuji_2", "gokayama_winter", "shirakawa_winter", "thatched_roof_winter",
    "country_train_winter", "japan_alps_winter", "shiretoko_ice", "ice",
    "monkey_hotspring", "winter_cranes", "winter_evening", "winter_honshu",
    "virtue", "marsh", "ocean", "apple_tree", "winter", "melt", "frost",
    "frozen", "endure_silently", "officer", "stiff", "year_end", "drought",
    "pine_tree",
]

CASTLES_TEMPLES = [
    "castle", "castle_01", "castle_2", "kumamoto", "king",
    "pagoda", "kyoto_pagoda", "kyoto_autumn", "capital", "town",
    "temple", "senso_ji_temple", "okinawa_temple", "nara_deer",
    "chant", "good_luck", "miyajima", "vermilion", "futamigaura",
    "nikko_2", "nikko_3", "nikko_fall_colors", "imperial_gardens", "garden",
    "pavilion", "water", "walk", "woods", "virtue", "ice", "ray",
    "visit_shrine", "righteousness", "assurance", "ecstasy", "endure_silently",
    "sweet_oak", "loyalty", "location", "neglect", "old", "permit",
    "public_hall", "safeguard", "shouldering", "sovereign", "year_end",
    "weld", "intimidate", "few", "fish", "curse", "conform", "constancy",
    "bell", "noon", "pond", "courtyard", "frozen", "respond", "sacrifice",
    "ridgepole", "about_that_time", "awe",
]

RURAL_CULTURAL = [
    "thatched_roof", "thatched_roof_winter", "shirakawa_spring", "shirakawa_winter",
    "gokayama_winter", "magome", "tsumago", "takayama", "hida_furukawa",
    "dazaifu_shopping", "dagashiya", "tea_shop", "wagashi_shop", "tanuki",
    "shopping_street", "right", "kyoto", "home_village", "village", "road",
    "plantation", "farm", "field", "rice", "tea_fields", "fishing_village",
    "fishing_village_2", "evening", "winter_evening", "winter_honshu",
    "morning", "villa", "country", "cloudy_weather", "beguile", "busy",
    "store", "slope", "weekday", "remainder", "environs", "run_alongside",
    "rut", "see", "load", "each", "robust", "soil", "cottage", "mulberry",
    "melt", "winter",
]

PEOPLE = [
    "boy", "child", "woman", "breed", "visit_shrine", "craft", "portable",
    "valley", "voiced", "accept", "awe", "back", "descendants", "particularly",
    "younger_sister", "yank", "special", "soil", "load", "officer",
    "take_along", "fishing", "dream", "moon", "obscure", "matrimony",
    "shouldering", "surpass", "renunciation", "see", "in_front",
    "light_weight", "leave", "juvenile",
]

MODERN_RAIL = [
    "country_station", "country_train_summer", "country_train_winter",
    "train_cherry_blossoms", "train_hydrangea", "sapporo_clock",
    "stop", "transport", "dog", "mediocre", "next", "car", "patrol",
]

FANTASY_OK = [
    "pine_tree", "challenge", "lightning_bug", "rise", "dream",
    "obscure", "bewitched",
]

# Use sparingly / probably skip among fantasy_ok
FANTASY_CAUTION = {"bewitched", "challenge"}

# Recommended unique pool for a 4-hour film (quality-first; not every tagged image).
CORE_POOL = [
    # existing 4-seasons keepers (drop only the soft-excludes)
    *[s for s in FOUR_SEASONS if s not in SOFT_EXCLUDE_FROM_4S],
    # additional unused scenery
    "acknowledge", "about_that_time", "accustomed", "allot", "annexed",
    "assurance", "ardent", "augment", "awe", "back",
    "bathe", "beckon", "beguile", "bell", "boulder", "boy", "branch",
    "breath", "breed", "bridge", "busy",
    "car", "capture", "child", "clear_land", "cliff", "cloud", "cloudy_weather",
    "conform", "constancy", "country", "courtyard", "crossing", "current",
    "curse",
    "dike", "dilute", "distinction", "dog", "drought",
    "each", "early", "east", "ecstasy", "endure_silently", "enlightenment",
    "environs", "eternity", "exist", "extremity",
    "failure", "fall", "fertile", "few", "fish", "five", "floating",
    "following_day", "frost", "frozen",
    "hedge", "hot_water",
    "in_front", "incur", "intimidate", "invariably",
    "king", "kudzu",
    "lazy", "length", "lightning_bug", "load", "location", "loyalty",
    "many", "mediocre", "melt", "method", "milk", "mountain", "mountain_pass",
    "mulberry",
    "neglect", "next", "nine", "noon",
    "officer", "old", "open_sea", "orderliness",
    "permit", "persimmon", "pine_tree", "plank", "pond", "portable",
    "prefecture", "promontory", "public_hall",
    "rainbow", "rain", "remainder", "remorse", "respond", "revolve",
    "righteousness", "robust", "run_alongside", "rut",
    "sacrifice", "safeguard", "sail", "sea", "see", "shouldering",
    "slope", "snake", "sovereign", "special", "splash", "split", "stiff",
    "stop", "store", "storm", "street", "sulfur", "sunset", "sweet_oak",
    "tea", "thick", "transport",
    "ume",
    "valley", "valve", "vast", "violent", "visit_shrine",
    "waterfall", "waves", "weekday", "weld", "wide", "wink", "winter",
    "wither", "woman",
    "yank", "year_end", "younger_sister",
]

MISSING_JAPAN = [
    {
        "id": "shinkansen_rice",
        "need": "Shinkansen passing through countryside / rice fields — train small in the landscape",
        "priority": "high",
        "notes": "Filled by shinkansen.png (viaduct through a misty rice-and-village valley). Fuji pairing still open.",
    },
    {
        "id": "shinkansen_fuji",
        "need": "Shinkansen with Mount Fuji (classic railway-landscape composition)",
        "priority": "high",
        "notes": "We have Fuji (mt_fuji_2, apple_blossoms, acknowledge) but never with a train.",
    },
    {
        "id": "shinkansen_sakura_or_tea",
        "need": "One more Shinkansen in seasonal landscape (sakura or tea country)",
        "priority": "medium",
        "notes": "Optional if the two high-priority Shinkansen images are strong. train_cherry_blossoms already covers local rail + sakura.",
    },
    {
        "id": "kiyomizu",
        "need": "Kiyomizu-dera hillside / wooden stage overlooking Kyoto",
        "priority": "medium",
        "notes": "Kyoto pagoda / Higashiyama street is strong; the Kiyomizu veranda view is absent.",
    },
    {
        "id": "byodoin",
        "need": "Byōdō-in Phoenix Hall across the pond (Uji)",
        "priority": "medium",
        "notes": "No phoenix-hall silhouette identified.",
    },
    {
        "id": "fushimi_senbon",
        "need": "Fushimi Inari senbon torii as a landscape tunnel (quiet, not tourist crush)",
        "priority": "medium",
        "notes": "Filled by fushimi.png.",
    },
    {
        "id": "todaiji_hall",
        "need": "Tōdai-ji Great Buddha Hall as a wide architectural landscape",
        "priority": "low",
        "notes": "nara_deer already shows the hall behind deer — may be enough.",
    },
    {
        "id": "nachi",
        "need": "Nachi waterfall with the red pagoda (one of Japan’s unique stacked landscapes)",
        "priority": "medium",
        "notes": "Filled by nachi_falls.png.",
    },
    {
        "id": "sakura_tunnel",
        "need": "2–3 wide sakura-row / river-tunnel landscapes (not close-up blossoms)",
        "priority": "medium",
        "notes": "Filled by sakura_river.png (one wide riverside row). Additional tunnels optional.",
    },
    {
        "id": "seto_islands",
        "need": "One more Seto Inland Sea / island-sea panorama (optional Matsushima-class)",
        "priority": "low",
        "notes": "wink already suggests this; only fill if we want a clearer iconic view.",
    },
    {
        "id": "matsuri_distance",
        "need": "A distant summer festival or fireworks over a river — people small, landscape first",
        "priority": "low",
        "notes": "Filled in spirit by matsuri.png (quiet shrine-path stalls) and yatai.png (night riverside stalls). Not a distant fireworks landscape.",
    },
    {
        "id": "showa_rural_modern",
        "need": "One quiet Showa/modern-rural cue (vending machine at dusk, rural bus, concrete coast with tetrapods) beautifully integrated",
        "priority": "low",
        "notes": "kei truck (car, transport) and wet modern street (patrol) already cover some modern-rural ground.",
    },
    {
        "id": "hoshi_rice_night",
        "need": "Starry night over flooded rice paddies — Milky Way reflected in tanada",
        "priority": "medium",
        "notes": "Filled by starlight.png (village and flooded paddies under the Milky Way). Replaces Start Here room_9/hoshi.",
    },
]


def resolve(stem: str) -> Path | None:
    for folder, exts in (
        (STUDIES, [".jpg", ".jpeg", ".png", ".webp"]),
        (ADD, [".jpg", ".jpeg", ".png", ".webp"]),
        (FOUR, [".png", ".jpg", ".jpeg", ".webp"]),
    ):
        for ext in exts:
            p = folder / f"{stem}{ext}"
            if p.is_file():
                return p
    return None


def rel_from_out(path: Path) -> str:
    return os_rel(path, OUT)


def os_rel(path: Path, start: Path) -> str:
    try:
        return str(path.relative_to(start))
    except ValueError:
        return os_relpath(path, start)


def os_relpath(path: Path, start: Path) -> str:
    import os
    return os.path.relpath(path, start)


def keep(stem: str, excluded: set[str]) -> bool:
    return stem not in excluded


def main() -> None:
    excluded = load_exclude_slugs()
    groups = OrderedDict([
        ("strong_japan_anchors", ANCHORS),
        ("countryside_nature", COUNTRYSIDE),
        ("spring", SPRING),
        ("summer", SUMMER),
        ("autumn", AUTUMN),
        ("winter", WINTER),
        ("castles_temples_shrines", CASTLES_TEMPLES),
        ("rural_cultural_japan", RURAL_CULTURAL),
        ("people", PEOPLE),
        ("modern_japan_rail", MODERN_RAIL),
        ("possible_fantasy_exceptions", FANTASY_OK),
    ])

    missing = []
    resolved = {}
    for stem in sorted(set(sum(groups.values(), []) + CORE_POOL + FOUR_SEASONS)):
        p = resolve(stem)
        if p is None:
            missing.append(stem)
        else:
            resolved[stem] = p

    group_payload = {}
    for name, stems in groups.items():
        items = []
        for stem in stems:
            if not keep(stem, excluded):
                continue
            p = resolved.get(stem)
            if not p:
                continue
            items.append({
                "stem": stem,
                "rel": os_relpath(p, OUT),
                "inFourSeasons": stem in FOUR_SEASONS,
                "rareInterior": stem in RARE_INTERIOR,
                "softExclude": stem in SOFT_EXCLUDE_FROM_4S,
                "fantasyCaution": stem in FANTASY_CAUTION,
            })
        group_payload[name] = items

    core_items = []
    seen_core = set()
    for stem in CORE_POOL:
        if not keep(stem, excluded) or stem in seen_core:
            continue
        p = resolved.get(stem)
        if not p:
            continue
        seen_core.add(stem)
        core_items.append({
            "stem": stem,
            "rel": os_relpath(p, OUT),
            "inFourSeasons": stem in FOUR_SEASONS,
            "rareInterior": stem in RARE_INTERIOR,
        })

    start_here = []
    start_here_accepted = []
    sh_path = OUT / "start_here_candidates.json"
    sh_raw = {}
    if sh_path.is_file():
        sh_raw = json.loads(sh_path.read_text())
        for rec in sh_raw.get("accepted") or []:
            item = {
                "stem": rec["id"],
                "rel": rec["rel"],
                "fromStartHere": True,
                "inFourSeasons": False,
                "rareInterior": False,
            }
            if rec["id"] not in seen_core:
                seen_core.add(rec["id"])
                core_items.append(item)
            start_here_accepted.append(item)
        for rec in sh_raw.get("recommended") or []:
            start_here.append({
                "stem": rec["id"],
                "rel": rec["rel"],
                "recommendation": rec.get("priority"),
                "reason": rec.get("fills"),
            })

    new_additions = []
    new_path = OUT / "new_additions.json"
    if new_path.is_file():
        new_raw = json.loads(new_path.read_text())
        for rec in new_raw.get("items") or []:
            item = {
                "stem": rec["id"],
                "rel": rec["rel"],
                "fromNewAddition": True,
                "inFourSeasons": False,
                "rareInterior": False,
                "reason": rec.get("fills"),
            }
            if rec["id"] not in seen_core:
                seen_core.add(rec["id"])
                core_items.append(item)
            new_additions.append(item)

    payload = {
        "id": "ambient_japan_4h_scenery",
        "title": "Ambient Japan — 4-hour scenery (candidate index)",
        "notes": "Reference-only index after curatorial exclusions. No image copies. Source assets unchanged.",
        "library": {
            "uniqueStemsAudited": 1019,
            "landscape": 972,
            "portrait": 15,
            "squareish": 32,
            "fourSeasonsSelected": 147,
            "fourSeasonsKeepers": len(FOUR_SEASONS) - len(SOFT_EXCLUDE_FROM_4S),
        },
        "exclusions": {
            "path": "kml/tools/ambient/collections/ambient_gallery_japan/exclusions.json",
            "pass": 6,
            "count": len(excluded),
            "appliedToCore": len(set(CORE_POOL) & excluded),
        },
        "counts": {
            "corePoolBeforeExclusions": len(set(CORE_POOL)),
            "corePool": len(core_items),
            "groups": {k: len(v) for k, v in group_payload.items()},
        },
        "pacing": {
            "targetDurationMin": 240,
            "holdSeconds": "50–60 (signature images 65–75)",
            "transitionSeconds": 2.5,
            "recommendedImageCount": "230–250",
            "fourSeasonsReference": "147 images / 120 min / ~46s hold",
        },
        "audio": {
            "primary": "kml/tools/ambient/audio/ambient_japan_4_seasons.mp3",
            "primaryMinutes": 119.8,
            "plan": "Loop once with a long crossfade to reach ~4 hours. Do not create or modify audio yet.",
            "alternates": [
                {"file": "137_minute_ambient.mp3", "minutes": 137.3},
                {"file": "ambient_kanji_full.mp3", "minutes": 98.1},
                {"file": "ambient_kanji_exhibition.mp3", "minutes": 98.1},
            ],
        },
        "missingJapan": MISSING_JAPAN,
        "corePool": core_items,
        "groups": group_payload,
        "unresolvedStems": missing,
    }

    second_look = []
    second_path = OUT / "second_look.json"
    if second_path.is_file():
        raw = json.loads(second_path.read_text())
        by_stem = {it["stem"]: it for it in core_items}
        for flag in raw.get("flagged") or []:
            item = by_stem.get(flag["stem"])
            if not item:
                continue
            second_look.append({**item, **flag})
    payload["counts"]["secondLook"] = len(second_look)
    payload["counts"]["startHereAccepted"] = len(start_here_accepted)
    payload["counts"]["startHereRecommended"] = len(start_here)
    payload["counts"]["newAdditions"] = len(new_additions)
    payload["startHereAccepted"] = start_here_accepted
    payload["newAdditions"] = new_additions
    (OUT / "candidates.json").write_text(json.dumps(payload, indent=2) + "\n")
    write_html(payload, group_payload, core_items, second_look, start_here, new_additions)
    print(f"core pool: {len(core_items)}")
    print(f"second look: {len(second_look)}")
    print(f"start here accepted: {len(start_here_accepted)}")
    print(f"start here pending: {len(start_here)}")
    print(f"new additions: {len(new_additions)}")
    print(f"group counts: {payload['counts']['groups']}")
    print(f"unresolved: {missing}")
    print(f"wrote {OUT / 'candidates.json'}")
    print(f"wrote {OUT / 'index.html'}")


def write_html(payload, groups, core_items, second_look, start_here=None, new_additions=None) -> None:
    start_here = start_here or []
    new_additions = new_additions or []
    tabs = [("core", f"Core pool ({len(core_items)})")]
    if new_additions:
        tabs.append(("new_additions", f"New ({len(new_additions)})"))
    if second_look:
        tabs.append(("second_look", f"Second look ({len(second_look)})"))
    if start_here:
        tabs.append(("start_here", f"Start Here ({len(start_here)})"))
    tabs += [
        (k, f"{k.replace('_', ' ')} ({len(v)})") for k, v in groups.items()
    ]

    def cards(items):
        parts = []
        for it in items:
            flags = []
            if it.get("inFourSeasons"):
                flags.append("4S")
            if it.get("rareInterior"):
                flags.append("interior")
            if it.get("softExclude"):
                flags.append("skip?")
            if it.get("fantasyCaution"):
                flags.append("caution")
            if it.get("fromStartHere"):
                flags.append("start-here")
            if it.get("fromNewAddition"):
                flags.append("new")
            if it.get("recommendation"):
                flags.append(it["recommendation"].replace(" ", "-"))
            flag_html = "".join(f'<span class="flag">{f}</span>' for f in flags)
            reason = it.get("reason") or ""
            reason_html = f'<div class="reason">{reason}</div>' if reason else ""
            parts.append(
                f'<figure class="card">'
                f'<img loading="lazy" src="{it["rel"]}" alt="{it["stem"]}">'
                f'<figcaption>{it["stem"]}{flag_html}{reason_html}</figcaption>'
                f'</figure>'
            )
        return "\n".join(parts)

    panels = [f'<section class="panel active" data-tab="core">{cards(core_items)}</section>']
    if new_additions:
        panels.append(f'<section class="panel" data-tab="new_additions">{cards(new_additions)}</section>')
    if second_look:
        panels.append(f'<section class="panel" data-tab="second_look">{cards(second_look)}</section>')
    if start_here:
        panels.append(f'<section class="panel" data-tab="start_here">{cards(start_here)}</section>')
    for k, items in groups.items():
        panels.append(f'<section class="panel" data-tab="{k}">{cards(items)}</section>')

    tab_html = "\n".join(
        f'<button type="button" class="tab{" active" if i==0 else ""}" data-tab="{tid}">{label}</button>'
        for i, (tid, label) in enumerate(tabs)
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Ambient Japan 4h — candidate index</title>
<style>
  :root {{
    --bg: #141414;
    --fg: #ececec;
    --muted: #9a9a9a;
    --line: #2a2a2a;
    --accent: #c4a574;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font: 14px/1.45 system-ui, sans-serif;
    background: var(--bg);
    color: var(--fg);
  }}
  header {{
    padding: 28px 28px 12px;
    border-bottom: 1px solid var(--line);
  }}
  h1 {{ font-size: 22px; font-weight: 600; margin: 0 0 8px; }}
  .lede {{ color: var(--muted); max-width: 72ch; }}
  .lede a {{ color: var(--accent); }}
  .stats {{
    display: flex;
    flex-wrap: wrap;
    gap: 18px;
    margin: 16px 0 0;
  }}
  .stat span {{ display: block; color: var(--muted); font-size: 12px; }}
  .stat b {{ font-size: 20px; font-weight: 600; }}
  nav {{
    position: sticky;
    top: 0;
    background: var(--bg);
    border-bottom: 1px solid var(--line);
    padding: 10px 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    z-index: 2;
  }}
  .tab {{
    background: transparent;
    color: var(--muted);
    border: 1px solid var(--line);
    padding: 6px 10px;
    cursor: pointer;
  }}
  .tab.active {{ color: var(--fg); border-color: var(--accent); }}
  .panel {{ display: none; padding: 20px 24px 48px; }}
  .panel.active {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 14px;
  }}
  .card {{ margin: 0; }}
  .card img {{
    width: 100%;
    height: 150px;
    object-fit: cover;
    background: #000;
    display: block;
  }}
  figcaption {{
    margin-top: 6px;
    font-size: 12px;
    color: var(--muted);
  }}
  .reason {{
    margin-top: 4px;
    font-size: 11px;
    color: #b8b8b8;
    line-height: 1.35;
  }}
  .flag {{
    display: inline-block;
    margin-left: 6px;
    padding: 0 5px;
    border: 1px solid var(--line);
    color: var(--accent);
    font-size: 10px;
    letter-spacing: .04em;
    text-transform: uppercase;
  }}
</style>
</head>
<body>
<header>
  <h1>Ambient Japan — 4-hour scenery candidates</h1>
  <p class="lede">
    Working visual index after curatorial exclusions.
    References only — source images were not deleted. Open locally.
    Core pool is the surviving working set ({len(core_items)} images),
    including {payload['counts'].get('startHereAccepted', 0)} accepted Start Here scenes.
    Start Here review: <a href="start_here_index.html">start_here_index.html</a>
  </p>
  <div class="stats">
    <div class="stat"><span>Exclusions</span><b>{payload['exclusions']['count']}</b></div>
    <div class="stat"><span>Core before cuts</span><b>{payload['counts']['corePoolBeforeExclusions']}</b></div>
    <div class="stat"><span>Surviving core pool</span><b>{len(core_items)}</b></div>
    <div class="stat"><span>Recommended for 4h</span><b>230–250</b></div>
  </div>
</header>
<nav>
{tab_html}
</nav>
{"".join(panels)}
<script>
  const tabs = document.querySelectorAll(".tab");
  const panels = document.querySelectorAll(".panel");
  tabs.forEach(tab => {{
    tab.addEventListener("click", () => {{
      tabs.forEach(t => t.classList.remove("active"));
      panels.forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      document.querySelector('.panel[data-tab="' + tab.dataset.tab + '"]').classList.add("active");
      window.scrollTo(0, 0);
    }});
  }});
</script>
</body>
</html>
"""
    (OUT / "index.html").write_text(html)


if __name__ == "__main__":
    main()
