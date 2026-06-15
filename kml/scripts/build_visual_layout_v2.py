#!/usr/bin/env python3
"""
Build lesson_visual_layout_v2.json / .csv — exhibition-oriented visual planning (L1–34).

Does not generate images. Curator notebook output for Visual Layout v2.
"""

from __future__ import annotations

import csv
import json
import re
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KANJI_CSV = REPO / "kml" / "data" / "kanji" / "kanji_production.csv"
V1_STYLES = REPO / "lesson_visual_styles_v1.json"
V1_PROMPTS = REPO / "kml" / "assets" / "prompts" / "kml_prompts.json"
AUDIT = REPO / "kml" / "data" / "kanji" / "palettes" / "lesson_visual_audit.txt"
OUT_JSON = REPO / "lesson_visual_layout_v2.json"
OUT_CSV = REPO / "lesson_visual_layout_v2.csv"

# Lesson 1 v1 cinematic briefs (from v1 test pass)
L1_V1_SCENES: dict[str, str] = {
    "one": "Single reed/brushstroke in pale dawn mist — abstract oneness.",
    "two": "Two parallel stones or matched lanterns on a quiet path.",
    "three": "Three cranes or torii posts in grey-blue dawn.",
    "four": "Square courtyard or garden frame from above.",
    "five": "Cross of paths in misty field with faint ochre grass.",
    "six": "Honeycomb light on water or six petals in a bowl.",
    "seven": "Bent branch or turning mountain path.",
    "eight": "Forking paths diverging in damp earth.",
    "nine": "Nearly complete stone circle, one segment open.",
    "ten": "Crossroads with worn stone under dawn sky.",
    "mouth": "Cave mouth in ivory cliff, breath-like mist.",
    "sun": "Low sun through cloud bands over wide field.",
    "moon": "Crescent reflected in still rice paddy at twilight.",
    "field": "Wide terraced fields in pale dawn wash.",
    "eye": "Reflective pool mirroring sky; distant figure at shore.",
    "old": "Gnarled cedar or weathered gate post with moss.",
    "I": "Solitary traveler turning at edge of misty field.",
    "risk": "Foot hovering over stone step above dark water.",
    "companion": "Two travelers side by side on forest path.",
    "bright": "Sun and moon light meeting across a river gorge.",
}

# Hand-curated v2 concepts — Lesson 1 (full) + high-value primitives
CURATED_V2: dict[str, dict] = {
    # —— Lesson 1: exhibition opening suite ——
    "one": {
        "v2Concept": "A single ripe persimmon on worn cedar, afternoon amber slicing through paper shoji — solitude before abundance.",
        "subjectType": "still_life",
        "humanPresence": "none",
        "narrativeStrength": "static",
        "emotionalTone": "hushed anticipation",
        "colorWeight": "moderate",
        "atmosphere": "late autumn interior, single shaft of gold",
        "galleryPriority": "transition",
    },
    "two": {
        "v2Concept": "Two stone lanterns at a shrine stair, moss at their bases, crimson torii bleeding into indigo shadow — companionship without speech.",
        "subjectType": "architecture",
        "humanPresence": "implied",
        "narrativeStrength": "implied",
        "emotionalTone": "quiet pairing",
        "colorWeight": "rich",
        "atmosphere": "dusk approach, incense implied",
        "galleryPriority": "supporting",
    },
    "three": {
        "v2Concept": "Three persimmons on a lacquer tray beside a folded fan — the third completes the triangle of attention.",
        "subjectType": "still_life",
        "humanPresence": "none",
        "narrativeStrength": "static",
        "emotionalTone": "composed arrival",
        "colorWeight": "moderate",
        "atmosphere": "tea-room stillness, warm ochre against charcoal wood",
        "galleryPriority": "supporting",
    },
    "four": {
        "v2Concept": "Four tatami mats in a room opened to a square courtyard garden, rain on the eaves — enclosure that breathes.",
        "subjectType": "architecture",
        "humanPresence": "implied",
        "narrativeStrength": "implied",
        "emotionalTone": "sheltered calm",
        "colorWeight": "restrained",
        "atmosphere": "grey rain, green stone, pale interior",
        "galleryPriority": "supporting",
    },
    "five": {
        "v2Concept": "Five carp flags catching wind above a village river, their reflections broken by current — celebration held in air.",
        "subjectType": "mixed",
        "humanPresence": "implied",
        "narrativeStrength": "active",
        "emotionalTone": "lifted festivity",
        "colorWeight": "rich",
        "atmosphere": "spring breeze, indigo water, vermilion cloth",
        "galleryPriority": "feature",
    },
    "six": {
        "v2Concept": "Six tea bowls cooling on a long wooden counter after a gathering — steam ghosts still rising.",
        "subjectType": "still_life",
        "humanPresence": "implied",
        "narrativeStrength": "implied",
        "emotionalTone": "aftermath warmth",
        "colorWeight": "moderate",
        "atmosphere": "post-ceremony hush, celadon and umber",
        "galleryPriority": "supporting",
    },
    "seven": {
        "v2Concept": "Seven koi in a temple pond, one turning against the flow — a single decisive curve in silver and orange.",
        "subjectType": "animal",
        "humanPresence": "none",
        "narrativeStrength": "active",
        "emotionalTone": "restless grace",
        "colorWeight": "rich",
        "atmosphere": "moonlit water, black pine silhouette",
        "galleryPriority": "feature",
    },
    "eight": {
        "v2Concept": "Two mountain paths splitting at a cedar fork, a traveler pausing mid-step — the moment before choosing.",
        "subjectType": "landscape",
        "humanPresence": "secondary",
        "narrativeStrength": "active",
        "emotionalTone": "threshold uncertainty",
        "colorWeight": "moderate",
        "atmosphere": "mist in valley, wet bark gleaming",
        "galleryPriority": "feature",
    },
    "nine": {
        "v2Concept": "Nine paper lanterns lining a festival bridge, one unlit at the far end — almost complete, deliberately open.",
        "subjectType": "architecture",
        "humanPresence": "implied",
        "narrativeStrength": "implied",
        "emotionalTone": "tender incompleteness",
        "colorWeight": "rich",
        "atmosphere": "blue hour, warm points against cool river",
        "galleryPriority": "supporting",
    },
    "ten": {
        "v2Concept": "A crossroads market at closing: ten wooden stalls, the last vendor folding indigo cloth — the day completes itself.",
        "subjectType": "mixed",
        "humanPresence": "secondary",
        "narrativeStrength": "implied",
        "emotionalTone": "earned closure",
        "colorWeight": "moderate",
        "atmosphere": "dust in sunset, long shadows",
        "galleryPriority": "supporting",
    },
    "mouth": {
        "v2Concept": "An old woman laughing mid-sentence at a kitchen table, steam from miso between her hands — speech as warmth.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "active",
        "emotionalTone": "generous vitality",
        "colorWeight": "moderate",
        "atmosphere": "domestic amber, copper kettle gleam",
        "galleryPriority": "feature",
    },
    "sun": {
        "v2Concept": "Harvest field at low sun, a farmer straightening their back, light flooding the grain — labor crowned in gold.",
        "subjectType": "landscape",
        "humanPresence": "secondary",
        "narrativeStrength": "active",
        "emotionalTone": "exhausted radiance",
        "colorWeight": "rich",
        "atmosphere": "horizontal blaze, dust like pollen",
        "galleryPriority": "hero",
    },
    "moon": {
        "v2Concept": "A fisherman mending net on a boat, crescent moon on tidal mudflat silver — night work, patient tide.",
        "subjectType": "mixed",
        "humanPresence": "secondary",
        "narrativeStrength": "implied",
        "emotionalTone": "solitary devotion",
        "colorWeight": "restrained",
        "atmosphere": "moonlit silver, indigo mud, one lantern",
        "galleryPriority": "hero",
    },
    "field": {
        "v2Concept": "Terraced rice fields after planting, a heron standing in mirrored water — geometry alive with reflection.",
        "subjectType": "landscape",
        "humanPresence": "none",
        "narrativeStrength": "static",
        "emotionalTone": "fertile patience",
        "colorWeight": "moderate",
        "atmosphere": "early summer green, pearl sky",
        "galleryPriority": "feature",
    },
    "eye": {
        "v2Concept": "Close portrait: a child's face watching fireworks reflected in their eyes — wonder held still.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "static",
        "emotionalTone": "astonished attention",
        "colorWeight": "rich",
        "atmosphere": "festival night, crimson bursts in dark irises",
        "galleryPriority": "feature",
    },
    "old": {
        "v2Concept": "Ancient camphor tree, roots gripping stone steps; an elderly couple resting on the trunk — time shared.",
        "subjectType": "landscape",
        "humanPresence": "secondary",
        "narrativeStrength": "implied",
        "emotionalTone": "enduring tenderness",
        "colorWeight": "moderate",
        "atmosphere": "deep green canopy, weathered grey bark",
        "galleryPriority": "feature",
    },
    "I": {
        "v2Concept": "A woman alone on a coastal promenade at first light, coat pulled tight, facing the horizon — self as witness.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "implied",
        "emotionalTone": "self-possessed solitude",
        "colorWeight": "restrained",
        "atmosphere": "cold dawn, pale rose sky, dark sea",
        "galleryPriority": "feature",
    },
    "risk": {
        "v2Concept": "Mountain guide reaching for a hand across a crevasse bridge, wind lifting snow — one step, mutual trust.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "active",
        "emotionalTone": "charged courage",
        "colorWeight": "rich",
        "atmosphere": "alpine white, bruised violet shadow",
        "galleryPriority": "hero",
    },
    "companion": {
        "v2Concept": "Two friends on a bench in falling snow, shoulders touching, thermos between them — warmth without words.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "static",
        "emotionalTone": "steady belonging",
        "colorWeight": "moderate",
        "atmosphere": "soft snowfall, charcoal coats, amber thermos",
        "galleryPriority": "feature",
    },
    "bright": {
        "v2Concept": "Riverside at equinox twilight: last sun on water while moon rises behind cedar — dual light, one breath.",
        "subjectType": "landscape",
        "humanPresence": "implied",
        "narrativeStrength": "implied",
        "emotionalTone": "ceremonial clarity",
        "colorWeight": "rich",
        "atmosphere": "gold water, silver sky, lesson climax",
        "galleryPriority": "hero",
    },
    # —— Lesson 34 emotion coda suite ——
    "fear": {
        "v2Concept": "Child on a dark stairwell landing, hand on railing, listening to rain — fear as listening, not screaming.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "static",
        "emotionalTone": "hushed dread",
        "colorWeight": "rich",
        "atmosphere": "indigo stairwell, single floor light",
        "galleryPriority": "feature",
    },
    "beguile": {
        "v2Concept": "Street magician fanning cards, observer leaning too close — charm as dangerous proximity.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "active",
        "emotionalTone": "seductive misdirection",
        "colorWeight": "moderate",
        "atmosphere": "festival dusk, lantern bokeh",
        "galleryPriority": "feature",
    },
    "feeling": {
        "v2Concept": "Hands overlapping on a shared umbrella handle in sudden rain — feeling before speech.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "implied",
        "emotionalTone": "tender recognition",
        "colorWeight": "moderate",
        "atmosphere": "silver rain, blurred crossing",
        "galleryPriority": "hero",
    },
    "melancholy": {
        "v2Concept": "Empty swing moving in wind at an abandoned playground, long shadow — absence as motion.",
        "subjectType": "landscape",
        "humanPresence": "implied",
        "narrativeStrength": "implied",
        "emotionalTone": "sweet ache",
        "colorWeight": "restrained",
        "atmosphere": "late afternoon violet, dust in light",
        "galleryPriority": "feature",
    },
    "widow": {
        "v2Concept": "Black obi folded on a chair beside an untouched tea cup — room still arranged for two.",
        "subjectType": "still_life",
        "humanPresence": "implied",
        "narrativeStrength": "static",
        "emotionalTone": "reverent absence",
        "colorWeight": "restrained",
        "atmosphere": "muted interior, grey daylight",
        "galleryPriority": "feature",
    },
    "busy": {
        "v2Concept": "Kitchen before service: three cooks crossing in steam, knives and flame — beautiful hurry.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "active",
        "emotionalTone": "controlled frenzy",
        "colorWeight": "rich",
        "atmosphere": "copper flame, white steam",
        "galleryPriority": "supporting",
    },
    "ecstasy": {
        "v2Concept": "Dancer mid-spin, skirt blooming, face lifted to spotlit dust — joy as physical law.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "active",
        "emotionalTone": "radiant release",
        "colorWeight": "rich",
        "atmosphere": "amber stage, dark void",
        "galleryPriority": "hero",
    },
    "constancy": {
        "v2Concept": "Same bench through four seasons in four-panel composition — one tree, changing light.",
        "subjectType": "landscape",
        "humanPresence": "implied",
        "narrativeStrength": "implied",
        "emotionalTone": "faithful return",
        "colorWeight": "moderate",
        "atmosphere": "seasonal cycle, restrained palette each panel",
        "galleryPriority": "feature",
    },
    "lament": {
        "v2Concept": "Funeral procession from above, umbrellas like dark petals on wet street — collective grief.",
        "subjectType": "mixed",
        "humanPresence": "secondary",
        "narrativeStrength": "implied",
        "emotionalTone": "solemn weight",
        "colorWeight": "restrained",
        "atmosphere": "rain gloss, black fabric",
        "galleryPriority": "feature",
    },
    "enlightenment": {
        "v2Concept": "Monk extinguishing a candle at dawn, smile barely there — light released, not seized.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "static",
        "emotionalTone": "quiet clarity",
        "colorWeight": "moderate",
        "atmosphere": "first blue hour, smoke thread",
        "galleryPriority": "hero",
    },
    "dreadful": {
        "v2Concept": "Hospital corridor perspective, fluorescent hum, figure waiting outside closed door.",
        "subjectType": "architecture",
        "humanPresence": "secondary",
        "narrativeStrength": "implied",
        "emotionalTone": "clinical dread",
        "colorWeight": "restrained",
        "atmosphere": "green-white fluorescent, linoleum gleam",
        "galleryPriority": "supporting",
    },
    "disconcerted": {
        "v2Concept": "Woman holding two ringing phones, city blur behind glass — nowhere to look.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "active",
        "emotionalTone": "frayed attention",
        "colorWeight": "moderate",
        "atmosphere": "urban night, reflected neon",
        "galleryPriority": "supporting",
    },
    "repent": {
        "v2Concept": "Kneeling figure rinsing hands in stone basin, sleeves dark with soil — repentance as labor.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "active",
        "emotionalTone": "humble reckoning",
        "colorWeight": "restrained",
        "atmosphere": "courtyard night, water sound implied",
        "galleryPriority": "feature",
    },
    "hate": {
        "v2Concept": "Two men back to back in snow, fists unclenched but shoulders rigid — hatred as cold distance.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "static",
        "emotionalTone": "frozen hostility",
        "colorWeight": "restrained",
        "atmosphere": "whiteout edge, black coats",
        "galleryPriority": "feature",
    },
    "accustomed": {
        "v2Concept": "Barista making the same pour for a regular at the window seat — habit as tenderness.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "implied",
        "emotionalTone": "easy familiarity",
        "colorWeight": "moderate",
        "atmosphere": "morning coffee gold, steam",
        "galleryPriority": "supporting",
    },
    "pleasure": {
        "v2Concept": "Bare feet in summer river, head thrown back, fruit in hand — pleasure without performance.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "active",
        "emotionalTone": "unselfconscious delight",
        "colorWeight": "rich",
        "atmosphere": "green water, dappled sun",
        "galleryPriority": "feature",
    },
    "lazy": {
        "v2Concept": "Cat and human both napping on tatami, book open on chest — afternoon surrendered.",
        "subjectType": "mixed",
        "humanPresence": "primary",
        "narrativeStrength": "static",
        "emotionalTone": "guilty peace",
        "colorWeight": "restrained",
        "atmosphere": "slatted shade, dust motes",
        "galleryPriority": "supporting",
    },
    "humility": {
        "v2Concept": "Craftsman bowing to customer while presenting a bowl, both hands visible — humility as offering.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "static",
        "emotionalTone": "respectful lowering",
        "colorWeight": "moderate",
        "atmosphere": "shop interior, clay and linen",
        "galleryPriority": "feature",
    },
    "remorse": {
        "v2Concept": "Letter half-written, crumpled drafts in basket, rain on glass — words failed.",
        "subjectType": "still_life",
        "humanPresence": "implied",
        "narrativeStrength": "implied",
        "emotionalTone": "aching regret",
        "colorWeight": "restrained",
        "atmosphere": "desk lamp, grey window",
        "galleryPriority": "feature",
    },
    "recollection": {
        "v2Concept": "Elderly man finding a child's marble in a coat pocket, garden out of focus — memory in palm.",
        "subjectType": "human",
        "humanPresence": "primary",
        "narrativeStrength": "static",
        "emotionalTone": "tender surprise",
        "colorWeight": "moderate",
        "atmosphere": "autumn garden bokeh, amber leaf",
        "galleryPriority": "hero",
    },
}

# Keyword-pattern engines for exhibition concepts (not mnemonic)
ANIMAL_KEYWORDS = {
    "dog", "cat", "cow", "fish", "fishing", "whale", "monkey", "shellfish",
    "carp", "bird", "crane", "horse", "sheep", "pig", "deer", "bear",
}
BODY_KEYWORDS = {
    "mouth", "eye", "spine", "stomach", "gallbladder", "neck", "elbow",
    "tongue", "back", "fat", "liver", "heart", "bone", "flesh",
}
WATER_KEYWORDS = {
    "water", "ice", "river", "lake", "spring", "swim", "marsh", "tide",
    "creek", "soup", "rain", "flood", "ford", "open_sea", "large_river",
}
FIRE_KEYWORDS = {
    "fire", "inflammation", "lamp", "burn", "roast", "ash", "charcoal",
    "storm", "lightning", "embers", "candle",
}
TREE_KEYWORDS = {
    "tree", "woods", "forest", "oak", "pine", "peach_tree", "paulownia_tree",
    "apricot", "reed", "leaf", "seedling", "plant", "grass", "wither",
    "ume", "plum", "cherry", "cedar",
}
ARCH_KEYWORDS = {
    "temple", "castle", "town", "street", "shrine", "gate", "bridge",
    "pagoda", "palace", "tower", "grave", "cottage", "villa", "pavilion",
}
EMOTION_KEYWORDS = {
    "fear", "feeling", "melancholy", "ecstasy", "dreadful", "hate", "love",
    "joy", "sorrow", "anxiety", "grief", "pleasure", "remorse", "recollection",
    "enlightenment", "repent", "beguile", "disconcerted", "accustomed",
    "humility", "lazy", "busy", "widow", "lament", "constancy",
}

LESSON_EXHIBITION_ARCS: dict[int, str] = {
    1: "Opening gallery: from solitary object to shared light — the dawn of seeing.",
    2: "Morning ritual suite: voice, body, measure, and the first stacked suns.",
    3: "Workshop of speech: tongue, measure, rank — wit in daylight.",
    4: "Scholar's table: seeing, birth, tools, truth — ink and patience.",
    5: "Street of blades and towns: craft, cut, rule, possibility.",
    6: "Family room: kinship, scale, evening naming — domestic depth.",
    7: "Mineral and river room: earth pressure, seal, fire on the farm.",
    8: "Ash and ink village: fish, burial, letters, completion.",
    9: "Forest proclamation: trees, wealth, frames, withering beauty.",
    10: "Village scholarship wall: books, calendar, grass, suffering.",
    11: "Garden and creature corridor: plants, dogs, cats, silence.",
    12: "Court of tea and treasure: world, king, pearl, emperor.",
    13: "Earth organic opening: bullying/tolerance through plant and animal life.",
    14: "Metal and road workshop: gold, copper, guidance, creation.",
    15: "Motion gallery: cars, summer, transport, metaphor of passage.",
    16: "Fall and crown room: army, dream, capital, refreshing scenery.",
    17: "Study and speech hall: gentleman, memorize, plot, admonish.",
    18: "Language archive: poem, read, tune, formal closure.",
    19: "Castle and coin corridor: relatives, sincerity, ford, repeatedly.",
    20: "Power and passage: agreement, politics, build, prolong.",
    21: "Garment and far room: bride, judge, monkey, brocade.",
    22: "Cool contemplative threshold: north, back, compare — inward turn.",
    23: "Shrine visit suite: delicious, fat, shrine, ume blossom.",
    24: "Mix and thirst gallery: audience, brown, kudzu, cleverness.",
    25: "Interior comparison room: descendants, everyone, orderliness.",
    26: "Continued inward suite: restraint, civic calm, soft horizons.",
    27: "Reflective depth chamber: mirrors, emotion, fine gesture.",
    28: "Spacious quiet gallery: administrative calm, distance.",
    29: "Luminous depth interval: jewel teal, harvest gold accents.",
    30: "Charged dialogue wall: sharp cuts, workshop energy.",
    31: "Impressionist interior: intellectual and emotional space.",
    32: "Museum poise room: craft encyclopedia, cultural closure approaching.",
    33: "Late contemplative suite: synthesis before emotion coda.",
    34: "Emotion coda gallery: twilight interiors of feeling — exhibition climax of Book 1.",
}


def load_v1_styles() -> dict[int, dict]:
    data = json.loads(V1_STYLES.read_text(encoding="utf-8"))
    return {e["lesson"]: e for e in data["lessons"] if 1 <= e["lesson"] <= 34}


def load_v1_prompts() -> dict[str, str]:
    if not V1_PROMPTS.exists():
        return {}
    items = json.loads(V1_PROMPTS.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for item in items:
        prompt = item.get("prompt", "")
        m = re.search(r"Visual composition:\s*\n(.*?)\n\nStyle:", prompt, re.S)
        comp = (m.group(1).strip() if m else "").replace("\n", " ")
        if comp:
            out[item["slug"]] = comp
        else:
            out[item["slug"]] = "Flat vector mnemonic icon from primitive components."
    return out


def load_audit() -> dict[int, dict]:
    out: dict[int, dict] = {}
    if not AUDIT.exists():
        return out
    for line in AUDIT.read_text(encoding="utf-8").splitlines():
        m = re.match(r"(\d{3})\s+(\S+)\s*\npalette:\s*(.+)\nflow:\s*(.+)\nenergy:\s*(.+)", line + "\n")
        if not m:
            continue
        lesson = int(m.group(1))
        if 1 <= lesson <= 34:
            out[lesson] = {
                "family": m.group(2),
                "palette": m.group(3).strip(),
                "flow": m.group(4).strip(),
                "energy": m.group(5).strip(),
            }
    # line-by-line parse (audit is multiline blocks)
    text = AUDIT.read_text(encoding="utf-8")
    blocks = re.split(r"\n(?=\d{3} )", text.strip())
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        head = re.match(r"(\d{3})\s+(\S+)", lines[0])
        if not head:
            continue
        lesson = int(head.group(1))
        if not (1 <= lesson <= 34):
            continue
        palette = flow = energy = ""
        for ln in lines[1:]:
            if ln.startswith("palette:"):
                palette = ln.split(":", 1)[1].strip()
            elif ln.startswith("flow:"):
                flow = ln.split(":", 1)[1].strip()
            elif ln.startswith("energy:"):
                energy = ln.split(":", 1)[1].strip()
        out[lesson] = {
            "family": head.group(2),
            "palette": palette,
            "flow": flow,
            "energy": energy,
        }
    return out


def verse_theme(en_verse: str) -> str:
    line = (en_verse or "").replace("\\n", " ").strip()
    if not line:
        return ""
    first = line.split()[0:8]
    return " ".join(first) + ("…" if len(line.split()) > 8 else "")


def v1_summary(slug: str, lesson: int, style_cfg: dict, prompts: dict[str, str], en_verse: str) -> str:
    parts: list[str] = []
    if slug in L1_V1_SCENES:
        parts.append(f"V1 cinematic wash: {L1_V1_SCENES[slug]}")
    elif slug in prompts:
        parts.append(f"V1 mnemonic icon: {prompts[slug]}")
    else:
        dom = style_cfg.get("dominant_style", "KML-WASH")
        parts.append(f"V1 {dom}: study illustration tied to lesson palette and verse mood.")
    weak = ""
    if slug in {"one", "six", "seven", "nine", "eye"}:
        weak = " Weak v1 test: overly symbolic / floating kanji / misread risk."
    elif slug in {"two", "three", "four", "five", "eight", "ten"}:
        weak = " Weak v1 test: number symbolism without compelling subject."
    theme = verse_theme(en_verse)
    if theme:
        parts.append(f"Verse: «{theme}»")
    return " ".join(parts) + weak


def pick_variant(slug: str, options: list[str]) -> str:
    return options[hash(slug) % len(options)]


def infer_gallery_priority(lesson: int, order: int, slug: str, style_cfg: dict) -> str:
    accents = {a["slug"] for a in style_cfg.get("accent_kanji") or []}
    if slug in accents or order == 20:
        return "hero"
    if order == 1:
        return "transition"
    if order in {10, 19} or lesson in {1, 12, 20, 34} and order >= 18:
        return "feature"
    if order <= 3:
        return "transition"
    return "supporting"


def color_weight_for(lesson: int, slug: str, audit: dict) -> str:
    if lesson == 1 and slug in {"sun", "bright", "risk", "five", "seven", "nine"}:
        return "rich"
    if lesson >= 34:
        return "rich"
    if lesson >= 25:
        return "moderate"
    pal = audit.get(lesson, {}).get("palette", "")
    if any(x in pal for x in ("indigo", "crimson", "red", "copper")):
        return "moderate"
    return "restrained" if lesson <= 12 else "moderate"


def generate_v2(
    slug: str,
    keyword: str,
    kanji: str,
    lesson: int,
    order: int,
    en_verse: str,
    style_cfg: dict,
    audit: dict,
) -> dict:
    if slug in CURATED_V2:
        return dict(CURATED_V2[slug])

    kw = keyword.lower().replace("_", " ")
    pal = audit.get(lesson, {}).get("palette", "weathered earth and muted gold")
    tone = style_cfg.get("emotional_tone", "contemplative")
    gp = infer_gallery_priority(lesson, order, slug, style_cfg)
    cw = color_weight_for(lesson, slug, audit)

    # —— pattern routing ——
    if kw in ANIMAL_KEYWORDS or any(kw.endswith(x) for x in ("_tree",)):
        concept = pick_variant(
            slug,
            [
                f"A {kw.replace('_', ' ')} caught mid-movement in {pal.split(',')[0]} light — fur, scale, or feather rendered with tactile realism; the animal owns the frame.",
                f"Early morning: a {kw.replace('_', ' ')} at the forest margin, breath visible, dew on grass — impressionistic realism, story implied beyond the edge of trees.",
                f"Portrait of a {kw.replace('_', ' ')} in shallow depth of field, background dissolved into indigo shadow — a gallery animal study, not an emblem.",
            ],
        )
        return _pack(concept, "animal", "none", "active", tone, cw, "living air, tactile detail", gp)

    if kw in BODY_KEYWORDS:
        concept = pick_variant(
            slug,
            [
                f"Intimate still life: objects associated with the body — cloth, bowl, mirror — arranged as if after bathing; {pal}; human implied, not diagrammed.",
                f"A hands-close study: working, healing, or holding — veins and knuckle light in amber; the body as lived subject, not anatomy chart.",
            ],
        )
        return _pack(concept, "still_life", "implied", "implied", "embodied quiet", cw, "warm interior, shallow focus", gp)

    if kw in WATER_KEYWORDS:
        concept = pick_variant(
            slug,
            [
                f"River or shore at blue hour, current carrying reflected sky — a figure optional at the margin; {pal}; water as moving light.",
                f"Rain on stone basin overflowing — weather as protagonist; silver streaks, deep green moss, one wooden ladle.",
            ],
        )
        return _pack(concept, "landscape", "secondary", "implied", "flowing calm", cw, "wet stone, atmospheric depth", gp)

    if kw in FIRE_KEYWORDS:
        concept = pick_variant(
            slug,
            [
                f"Hearth or forge corner: ember core, face lit from below if a figure tends flame — crimson accent in indigo room.",
                f"Storm light on hillside, distant lightning dividing sky — fire as weather, not symbol.",
            ],
        )
        return _pack(concept, "weather", "secondary", "active", "compressed heat", "rich", "ember and shadow", gp)

    if kw in TREE_KEYWORDS or "tree" in kw or "wood" in kw:
        concept = pick_variant(
            slug,
            [
                f"A single {kw.replace('_', ' ')} holding wind in its branches — roots gripping stone; {pal}; landscape as portrait.",
                f"Planting or harvest moment: hands near soil, seedling or leaf backlit — growth as narrative, not botany slide.",
            ],
        )
        return _pack(concept, "landscape", "secondary", "implied", "grounded life", cw, "green depth, gold rim light", gp)

    if kw in ARCH_KEYWORDS or any(x in kw for x in ("town", "street", "gate", "castle", "temple")):
        concept = pick_variant(
            slug,
            [
                f"Architectural passage — corridor, gate, or alley — figure crossing threshold; weathered stone, {pal}.",
                f"Twilight on rooftops and tiles, smoke from one chimney — town as breathing organism.",
            ],
        )
        return _pack(concept, "architecture", "secondary", "implied", "institutional calm", cw, "stone grey, lantern amber", gp)

    if lesson == 34 or kw in EMOTION_KEYWORDS:
        concept = pick_variant(
            slug,
            [
                f"Interior twilight: a face turned from window light, emotion held in jaw and hand — {kw} as atmosphere, not caption.",
                f"Two figures in separate frames of the same room, distance speaking louder than gesture — {pal}, emotional coda.",
            ],
        )
        return _pack(concept, "human", "primary", "static", "emotional twilight", "rich", "violet dusk, smoky rose", "feature")

    if any(x in kw for x in ("walk", "run", "cross", "ford", "hunt", "cut", "strike", "carry")):
        concept = pick_variant(
            slug,
            [
                f"Mid-action freeze: a figure {kw.replace('_', ' ')}ing through weather — coat or cloth caught by wind; diagonal energy, cinematic still.",
                f"Footprints in wet sand leading toward horizon — journey implied, figure small but decisive.",
            ],
        )
        return _pack(concept, "human", "primary", "active", "kinetic resolve", cw, "motion blur on rain", gp)

    if any(x in kw for x in ("sun", "moon", "dawn", "evening", "day", "night", "early", "morning")):
        concept = pick_variant(
            slug,
            [
                f"Horizon ceremony: {kw.replace('_', ' ')} light breaking through cloud vault — land or sea below, no floating symbols.",
                f"Window scene: interior dark, exterior lit — the hour itself is the subject.",
            ],
        )
        return _pack(concept, "weather", "implied", "implied", "temporal hush", "rich", "amber and silver split", gp)

    if any(x in kw for x in ("gold", "silver", "copper", "iron", "pearl", "treasure", "coin", "jade")):
        concept = pick_variant(
            slug,
            [
                f"Still life on cloth: metal or stone object catching slit light — patina, scratch, weight; museum case without the case.",
                f"Artisan hands polishing or weighing — material honesty, {pal}.",
            ],
        )
        return _pack(concept, "still_life", "secondary", "static", "material reverence", "moderate", "specular highlight, dark ground", gp)

    if any(x in kw for x in ("book", "read", "write", "study", "poem", "letter", "word", "language")):
        concept = pick_variant(
            slug,
            [
                f"Desk at night: paper, ink, one lamp — reader leaning close; scholarly intimacy, not instruction.",
                f"Open book on windowsill, breeze lifting a corner — words implied, world outside in soft focus.",
            ],
        )
        return _pack(concept, "still_life", "secondary", "implied", "scholarly calm", "restrained", "lamp pool, parchment cream", gp)

    # —— default exhibition still ——
    concept = (
        f"Gallery still for «{keyword}»: a compelling real-world subject — figure, object, or weather — "
        f"in {pal}; impressionistic realism; moment from a larger story; kanji {kanji} only if carved, cast, or woven into the scene."
    )
    subj = pick_variant(slug, ["mixed", "landscape", "still_life", "human"])
    hp = "secondary" if subj == "human" else "implied" if subj == "mixed" else "none"
    return _pack(concept, subj, hp, "implied", tone, cw, f"{tone}; exhibition depth", gp)


def _pack(concept, subject, human, narrative, emotion, color, atmosphere, gallery):
    return {
        "v2Concept": concept,
        "subjectType": subject,
        "humanPresence": human,
        "narrativeStrength": narrative,
        "emotionalTone": emotion,
        "colorWeight": color,
        "atmosphere": atmosphere,
        "galleryPriority": gallery,
    }


def build() -> dict:
    styles = load_v1_styles()
    prompts = load_v1_prompts()
    audit = load_audit()

    lessons_out: list[dict] = []
    flat_rows: list[dict] = []

    for lesson in range(1, 35):
        cfg = styles.get(lesson, {})
        entries: list[dict] = []
        with KANJI_CSV.open(encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if int(r["lesson_number"]) == lesson]
        def _order_key(r: dict) -> int:
            for key in ("heisig_number", "kanji_index"):
                val = r.get(key) or ""
                if str(val).isdigit():
                    return int(val)
            return 0

        rows.sort(key=_order_key)

        for order, row in enumerate(rows, 1):
            slug = row["slug"]
            entry = {
                "order_in_lesson": order,
                "kanji": row["kanji"],
                "slug": slug,
                "keyword": row.get("display_keyword") or row["keyword"],
                "v1_concept_summary": v1_summary(
                    slug, lesson, cfg, prompts, row.get("en_verse", "")
                ),
            }
            entry.update(
                generate_v2(
                    slug,
                    entry["keyword"],
                    entry["kanji"],
                    lesson,
                    order,
                    row.get("en_verse", ""),
                    cfg,
                    audit,
                )
            )
            entries.append(entry)
            flat_rows.append({"lesson": lesson, **entry})

        lessons_out.append(
            {
                "lesson": lesson,
                "lesson_family": cfg.get("lesson_family", ""),
                "dominant_v1_style": cfg.get("dominant_style", ""),
                "v1_palette": cfg.get("palette", ""),
                "v1_emotional_tone": cfg.get("emotional_tone", ""),
                "exhibition_audit_palette": audit.get(lesson, {}).get("palette", ""),
                "exhibition_arc": LESSON_EXHIBITION_ARCS.get(lesson, ""),
                "entries": entries,
            }
        )

    return {
        "schema_version": "2.0",
        "system_name": "lesson_visual_layout_v2",
        "description": (
            "Exhibition-oriented visual planning for KML Lessons 1–34. "
            "Impressionistic realism with atmospheric storytelling. "
            "Planning pass only — no generated images."
        ),
        "style_direction": "Impressionistic realism with atmospheric storytelling.",
        "optimizes_for": [
            "exhibition viewing",
            "large-screen display",
            "ambient video",
            "coffee table book",
            "emotional resonance",
            "memorability",
        ],
        "deprioritizes": [
            "clip-art symbolism",
            "instructional diagrams",
            "obvious mnemonic illustration",
            "floating kanji overlays",
            "pale wash monoculture",
        ],
        "curator_notes": textwrap.dedent(
            """
            Visual Layout v2 shifts from mobile mnemonic clarity to gallery pause.
            Lesson 1 numbers become still life and festival counts — not stroke diagrams.
            Human presence appears when narrative demands it; animals and architecture carry equal weight.
            Color moves toward amber, indigo, crimson, and silver while staying restrained.
            Kanji integration should be environmental (carved, woven, reflected) — never pasted.
            Use galleryPriority to sequence exhibition loops: transition → supporting → feature → hero.
            """
        ).strip(),
        "field_definitions": {
            "subjectType": ["human", "animal", "still_life", "architecture", "landscape", "weather", "mixed"],
            "humanPresence": ["none", "implied", "secondary", "primary"],
            "narrativeStrength": ["static", "implied", "active"],
            "colorWeight": ["restrained", "moderate", "rich"],
            "galleryPriority": ["transition", "supporting", "feature", "hero"],
        },
        "sources": {
            "v1_styles": str(V1_STYLES.relative_to(REPO)),
            "kanji_production": str(KANJI_CSV.relative_to(REPO)),
            "v1_prompts": str(V1_PROMPTS.relative_to(REPO)),
            "lesson_audit": str(AUDIT.relative_to(REPO)),
        },
        "lesson_count": 34,
        "entry_count": len(flat_rows),
        "lessons": lessons_out,
        "flat_index": flat_rows,
    }


def write_csv(flat_rows: list[dict], path: Path) -> None:
    fields = [
        "lesson",
        "order_in_lesson",
        "kanji",
        "keyword",
        "slug",
        "v1_concept_summary",
        "v2Concept",
        "subjectType",
        "humanPresence",
        "narrativeStrength",
        "emotionalTone",
        "colorWeight",
        "atmosphere",
        "galleryPriority",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in flat_rows:
            w.writerow(row)


def main() -> int:
    doc = build()
    OUT_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(doc["flat_index"], OUT_CSV)
    print(f"Wrote {OUT_JSON} ({doc['entry_count']} entries)")
    print(f"Wrote {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
