#!/usr/bin/env python3
"""Build Lessons 11–34 Compounds JSON + HTML. Lexical sanitation first."""

from __future__ import annotations

import json
import re
import shutil
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import fugashi

from _build_lessons_01_10 import (
    HTML,
    MASTER,
    load_keywords,
    make_id,
    masu,
    nav_html,
    ruby_segments,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMP_HTML = ROOT / "contents/books/book_01/compounds"
LEGACY = HERE / "_legacy_html_l11_34"
TAGGER = fugashi.Tagger()

BLOCK_RE = re.compile(
    r'<span class="kanji-compound-font">([^<]+)</span>(.*?)<ul>(.*?)</ul>',
    re.DOTALL | re.IGNORECASE,
)
ITEM_RE = re.compile(
    r"<li>\s*(?:<strong>)?([^<【]+)(?:</strong>)?【([^】]+)】\s*(?:<br\s*/?>)?\s*[–-]\s*([^<]+)",
    re.IGNORECASE,
)
H2_RE = re.compile(r"<h2>(.*?)</h2>", re.DOTALL | re.IGNORECASE)

REMOVE = {
    (12, "昧昧"),
    (12, "昧心"),
    (12, "昧弱"),
    (12, "沫沫"),
    (12, "妹弟"),
    (13, "漠土"),
    (11, "梢雲"),
    (11, "梢鳴"),
    (12, "沫酒"),
    (12, "沫状"),
}

REMOVE_META = {
    (12, "昧昧"): ("NON_LEXICAL", "Rare literary reduplication; same padding pattern as 明晶."),
    (12, "昧心"): ("NON_LEXICAL", "Chinese-style pad under 昧; not ordinary Japanese."),
    (12, "昧弱"): ("NON_LEXICAL", "Labeled very rare; invented 昧 + 弱 pad."),
    (12, "沫沫"): ("NON_LEXICAL", "Reduplicated pad under 沫."),
    (12, "妹弟"): ("NON_LEXICAL", "Chinese order; Japanese is 弟妹. Rare-literary label is padding."),
    (13, "漠土"): ("NON_LEXICAL", "Labeled very rare classical; pad beside 砂漠/漠然."),
    (11, "梢雲"): ("NON_LEXICAL", "Poetic-term label; 梢 + 雲 on-yomi pad, not an established word."),
    (11, "梢鳴"): ("NON_LEXICAL", "Literary label; 梢 + 鳴 on-yomi pad, not an established word."),
    (12, "沫酒"): ("NON_LEXICAL", "Literary-usage label; 沫 + 酒 pad beside 沫沫, not established 発泡酒/泡."),
    (12, "沫状"): ("NON_LEXICAL", "Technical-term label; productive 状 glue, not a lexical unit."),
}

NAMES_KIND = re.compile(
    r"place name|given name|surname|family name|personal name|proper name",
    re.I,
)

IMAGES = {
    11: ("assets/studies/sakurajima.jpg", "Sakurajima"),
    12: ("assets/studies/nara.jpg", "Nara"),
    13: ("assets/studies/nikko_2.jpg", "Nikkō"),
    14: ("assets/studies/shirakawa_spring.jpg", "Shirakawa in spring"),
    15: ("assets/studies/zen.jpg", "A Zen garden"),
    16: ("assets/studies/okinawa_temple.jpg", "A temple in Okinawa"),
    17: ("assets/studies/sunrise.jpg", "Sunrise in Japan"),
    18: ("assets/studies/harbor.jpg", "A Japanese harbor"),
    19: ("assets/studies/bridge.jpg", "A bridge in Japan"),
    20: ("assets/studies/seacoast.jpg", "The Japanese seacoast"),
    21: ("assets/studies/bamboo.jpg", "Bamboo in Japan"),
    22: ("assets/studies/castle_01.jpg", "A Japanese castle"),
    23: ("assets/studies/winter_honshu.jpg", "Winter on Honshu"),
    24: ("assets/studies/shirakawa_winter.jpg", "Shirakawa in winter"),
    25: ("assets/studies/winter_evening.jpg", "A winter evening"),
    26: ("assets/studies/island.jpg", "A Japanese island"),
    27: ("assets/studies/beach.jpg", "A beach in Japan"),
    28: ("assets/studies/train_cherry_blossoms.jpg", "A train and cherry blossoms"),
    29: ("assets/studies/shinto_shrine.jpg", "A Shinto shrine"),
    30: ("assets/studies/buddhist_temple.jpg", "A Buddhist temple"),
    31: ("assets/studies/hometown.jpg", "A hometown in Japan"),
    32: ("assets/studies/valley.jpg", "A valley in Japan"),
    33: ("assets/studies/japan_alps_summer_2.jpg", "The Japan Alps in summer"),
    34: ("assets/studies/winter_cranes.jpg", "Cranes in winter"),
}

# Hand sentences: (lesson, surface) -> (ja, en, exception_reason|None)
HAND: dict[tuple[int, str], tuple[str, str, str | None]] = {}

ACTION = re.compile(
    r"\b(to |tion|sion|ment|ance|ence|al$|ing\b|publicity|oath|vow|proclamation|declaration|"
    r"imitation|copying|relief|stability|safety|gratitude|emotion|empathy|sensation|"
    r"fear|panic|bewilder|fascination|nuisance|depression|anxiety|lament|concern)\b",
    re.I,
)
PHYSICAL = re.compile(
    r"tree|river|city|town|island|mountain|temple|shrine|bridge|lake|sea|fish|bird|stone|"
    r"grave|tomb|cemetery|color|colour|food|rice|tea|sake|snow|rain|wind|house|room|road|"
    r"boat|ship|car|book|paper|stamp|pen|stock|share|stump|sister|brother|mother|father|"
    r"child|girl|boy|friend|teacher|doctor|spoon|model|replica|exam",
    re.I,
)

ADVANCED = (
    "ている",
    "ていた",
    "られる",
    "された",
    "させる",
    "ながら",
    "ても",
    "ために",
    "ので",
    "のに",
    "ば、",
    "なら",
    "たら",
    "である",
    "のごとく",
    "かもしれない",
)


def clean_reading(raw: str) -> str:
    text = unicodedata.normalize("NFKC", raw).strip()
    text = text.split("／")[0].split("/")[0].strip()
    return "".join(chr(ord(c) - 96) if "ァ" <= c <= "ヶ" else c for c in text)


def parse_h2(chunk: str) -> tuple[str, str]:
    m = H2_RE.search(chunk)
    if not m:
        return "", ""
    t = re.sub("<[^>]+>", "", m.group(1))
    rm = re.search(r"（([^）]+)）", t)
    readings = rm.group(1).replace("／", "・") if rm else ""
    km = re.search(r"[–-]\s*(.+)$", t)
    return readings, (km.group(1).strip() if km else "")


def parse_lesson_html(n: int) -> list[dict]:
    src = LEGACY / f"lesson_{n:02d}.html"
    if not src.exists():
        src = COMP_HTML / f"lesson_{n:02d}.html"
        LEGACY.mkdir(exist_ok=True)
        shutil.copy2(src, LEGACY / f"lesson_{n:02d}.html")
    html = src.read_text(encoding="utf-8")
    chars = []
    for kanji, mid, ul in BLOCK_RE.findall(html):
        readings, keyword = parse_h2(mid)
        comps = []
        for surface, reading, gloss in ITEM_RE.findall(ul):
            comps.append(
                {
                    "surface": unicodedata.normalize("NFKC", surface).strip(),
                    "reading": clean_reading(reading),
                    "meaning": re.sub(r"\s+", " ", gloss).strip(" .–-"),
                }
            )
        chars.append(
            {
                "kanji": kanji.strip(),
                "readings": readings,
                "keyword": keyword,
                "compounds": comps,
            }
        )
    return chars


def pos_of(surface: str) -> str:
    try:
        toks = list(TAGGER(surface))
    except Exception:
        return ""
    if not toks:
        return ""
    feat = toks[-1].feature
    return getattr(feat, "pos1", "") or ""


def mashita(verb: str) -> str:
    form = masu(verb)
    if form.endswith("ます"):
        return form[:-2] + "ました"
    return form


def inflect_for_sentence(surface: str, meaning: str, lesson: int) -> str | None:
    m = (meaning or "").lower()
    pos = pos_of(surface)
    if surface.endswith("する"):
        return masu(surface)
    if pos == "動詞" or m.startswith("to "):
        if lesson >= 27:
            return mashita(surface) if hash(surface) % 3 == 0 else masu(surface)
        return masu(surface)
    return None


def en_verb(gloss: str) -> str:
    g = gloss.lower()
    if g.startswith("to "):
        return g[3:]
    return g


def sentence(lesson: int, kanji: str, surface: str, reading: str, meaning: str) -> tuple[str, str, str | None]:
    key = (lesson, surface)
    if key in HAND:
        return HAND[key]
    m = (meaning or "").lower()
    gloss = (meaning or reading).split(",")[0].split(";")[0].split("(")[0].strip()
    pos = pos_of(surface)
    h = abs(hash(surface + "|" + reading))
    late = lesson >= 23
    time = "昨日、" if late else "朝、"

    if NAMES_KIND.search(meaning or ""):
        if any(x in m for x in ("place", "city", "river", "town")):
            return f"来月、{surface}へ行きます。", f"Next month I will go to {gloss}.", None
        return f"{surface}さんは隣に住みます。", f"{gloss} lives next door.", None

    if pos == "動詞" or m.startswith("to "):
        form = mashita(surface) if late and h % 2 == 0 else masu(surface)
        stem = en_verb(gloss)
        if "母" in (["私", "兄", "母"][h % 3]):
            pass
        who = ["私は", "兄は", "母は"][h % 3]
        ja = f"{time}{who}{form}。" if late else f"{who}{form}。"
        subj = {"私は": "I", "兄は": "My older brother", "母は": "My mother"}[who]
        return ja, f"{subj} {stem}.", None

    if pos == "形容詞":
        return f"今日は{surface}です。", f"It is {gloss.lower()} today.", None
    if surface == "安い":
        return "この店はりんごが安いです。", "Apples are cheap at this shop.", None

    # Phrase already containing grammar
    if "を" in surface or surface.endswith(("する", "なる")):
        if surface.endswith("する"):
            return f"{masu(surface)}。", f"I {en_verb(gloss)}.", None
        return f"春に{surface}。", f"In spring, {gloss.lower()}.", None

    people = ("missionary", "teacher", "doctor", "pirate", "thief", "bandit", "shareholder", "sister", "brother")
    if any(x in m for x in people):
        if "sister" in m:
            return f"{surface}はもう寝ます。", f"{gloss} is already going to bed.", None
        return f"{surface}が村に来ます。", f"A {gloss.lower()} comes to the village.", None

    places = (
        "city", "town", "river", "region", "territory", "district", "island", "mountain",
        "temple", "shrine", "desert", "sea", "basin", "area", "forest", "village", "harbor",
        "place name",
    )
    if any(x in m for x in places):
        return f"{surface}は広いです。", f"{gloss} is wide.", None

    times = ("evening", "dusk", "night", "weekend", "month", "year", "eve", "festival", "twilight", "tonight")
    if any(x in m for x in times):
        return f"{surface}に星が出ます。", f"Stars come out at {gloss.lower()}.", None

    jobs_acts = (
        "declaration", "advertisement", "publicity", "oath", "vow", "pronouncement",
        "imitation", "copying", "stability", "safety", "security", "relief",
        "gratitude", "emotion", "empathy", "sensation", "fear", "panic",
        "bewilder", "fascination", "nuisance", "depression", "anxiety", "lament",
        "concern", "proclamation", "inspection", "measurement",
    )
    if any(x in m for x in jobs_acts) and not re.search(r"[\u3040-\u30ff]", surface):
        if "relief" in m or surface == "安心":
            return "話を聞いて安心しました。", "I felt relieved after hearing the story.", None
        if "safety" in m or surface == "安全":
            return "この橋は安全です。", "This bridge is safe.", None
        if surface == "恐縮":
            return "遅れて、恐縮です。", "I am sorry for being late.", None
        return f"兄は{surface}します。", f"My older brother makes a {gloss.lower()}.", None

    colors = ("color", "colour", "vermilion", "red", "blue", "black", "white")
    if any(x in m for x in colors):
        return f"この紙は{surface}です。", f"This paper is {gloss.lower()}.", None

    food = ("tea", "sake", "rice", "fish", "food", "wine")
    if any(x in m for x in food):
        return f"夜は{surface}を飲みます。", f"At night I drink {gloss.lower()}.", None

    # Default noun: use as object or topic, never empty があります
    frames = [
        (f"父は{surface}が好きです。", f"My father likes {gloss.lower()}."),
        (f"店で{surface}を見ます。", f"I look at {gloss.lower()} in the shop."),
        (f"{surface}の話を聞きます。", f"I listen to a story about {gloss.lower()}."),
        (f"教室で{surface}を習います。", f"We learn about {gloss.lower()} in class."),
    ]
    if late:
        frames.append((f"昨日、{surface}を思いました。", f"Yesterday I thought about {gloss.lower()}."))
    ja, en = frames[h % len(frames)]
    return ja, en, None


def KANJI_ONLY(s: str) -> str:
    return "".join(ch for ch in s if "\u4e00" <= ch <= "\u9fff")


def _ingest_examples(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data.get("items") or []:
        les = int(item["lesson"])
        if les < 11 or les > 34:
            continue
        exc = item.get("exception")
        if item.get("grammarException") and not exc:
            exc = "Natural use of this word requires a slightly later construction."
        HAND[(les, item["surface"])] = (item["ja"], item["en"], exc)


def load_hand() -> None:
    overlays = sorted(
        p
        for p in HERE.glob("_examples_l*.json")
        if p.name != "_examples_l11_34_hand.json"
    )
    for path in overlays:
        _ingest_examples(path)
    hand = HERE / "_examples_l11_34_hand.json"
    if hand.is_file():
        _ingest_examples(hand)


def main() -> int:
    load_hand()
    keywords = load_keywords()
    removed = []
    review = []
    stats = {
        "inspected": 0,
        "retained": 0,
        "removed": 0,
        "names": 0,
        "exceptions": 0,
        "lens": [],
        "ruby_err": 0,
        "empty_sets": [],
    }
    used_ja: set[str] = set()

    for n in range(11, 35):
        chars = parse_lesson_html(n)
        out_chars = []
        ids = Counter()
        for ch in chars:
            comps = []
            kw = ch.get("keyword") or keywords.get(ch["kanji"], "")
            readings = ch.get("readings") or ""
            for c in ch["compounds"]:
                stats["inspected"] += 1
                key = (n, c["surface"])
                if key in REMOVE:
                    cls, cause = REMOVE_META[key]
                    removed.append(
                        {
                            "lesson": n,
                            "kanji": ch["kanji"],
                            "original": c["surface"],
                            "reading": c["reading"],
                            "meaning": c["meaning"],
                            "classification": cls,
                            "decision": "Removed; no automatic replacement.",
                            "cause": cause,
                        }
                    )
                    stats["removed"] += 1
                    continue
                ja, en, exc = sentence(n, ch["kanji"], c["surface"], c["reading"], c["meaning"])
                if ja in used_ja:
                    ja = ("また、" + ja) if not ja.startswith("また") else ja[:-1] + "よ。"
                used_ja.add(ja)
                segs = ruby_segments(ja, c["surface"], c["reading"])
                if "".join(s["text"] for s in segs) != ja:
                    stats["ruby_err"] += 1
                    segs = [{"text": ja}]
                    review.append(
                        {
                            "lesson": n,
                            "surface": c["surface"],
                            "issue": "ruby-join",
                            "ja": ja,
                        }
                    )
                rec = {
                    "id": make_id(n, c["surface"], c["reading"], ids),
                    "surface": c["surface"],
                    "reading": c["reading"],
                    "meaning": c["meaning"],
                    "sourceGloss": c["meaning"],
                    "example": {"ja": ja, "en": en, "segments": segs},
                }
                if c["surface"] != "苗字" and NAMES_KIND.search(c["meaning"] or ""):
                    rec["kind"] = "name"
                    stats["names"] += 1
                qa = {}
                if exc:
                    qa["grammarException"] = True
                    qa["reason"] = exc
                    stats["exceptions"] += 1
                if c["surface"] == "除夜の宵":
                    qa["migrationNote"] = (
                        "VALID_LITERARY seasonal expression; ordinary Japanese more often uses 除夜 or 大晦日."
                    )
                if c["surface"] == "匕":
                    qa["migrationNote"] = (
                        "VALID_SPECIALIZED isolated classical character-word (spoon / radical ひ), not a compound."
                    )
                if qa:
                    rec["qa"] = qa
                comps.append(rec)
                stats["retained"] += 1
                stats["lens"].append(len(ja))
            if not comps:
                stats["empty_sets"].append((n, ch["kanji"]))
            out_chars.append(
                {
                    "kanji": ch["kanji"],
                    "readings": readings,
                    "keyword": kw,
                    "compounds": comps,
                }
            )
        img, alt = IMAGES[n]
        payload = {
            "schema": "kml.compounds.lesson.v1",
            "lesson": n,
            "title": f"Lesson {n} — Compounds",
            "grammar": {
                "position": n,
                "lessonCount": 153,
                "progress": round(n / 153, 3),
                "band": "early",
                "progression": "grammar_progression.json",
            },
            "background": {
                "image": img,
                "alt": alt,
                "source": f"kml/{img}",
                "collection": "Ambient Gallery Japan — Four Seasons",
            },
            "characters": out_chars,
        }
        (HERE / f"lesson_{n:02d}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (COMP_HTML / f"lesson_{n:02d}.html").write_text(
            HTML.format(n=n, nn=f"{n:02d}", nav=nav_html(n)), encoding="utf-8"
        )
        print(
            f"lesson {n:02d}  kanji {len(out_chars)}  words {sum(len(c['compounds']) for c in out_chars)}"
        )

    report = {
        "removed": removed,
        "review": review,
        "stats": {
            k: v
            for k, v in stats.items()
            if k != "lens"
        },
        "len_min": min(stats["lens"]) if stats["lens"] else 0,
        "len_avg": round(sum(stats["lens"]) / len(stats["lens"]), 1) if stats["lens"] else 0,
        "len_max": max(stats["lens"]) if stats["lens"] else 0,
    }
    (HERE / "_review_queue_11_34.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("inspected", stats["inspected"], "retained", stats["retained"], "removed", stats["removed"])
    print("names", stats["names"], "exceptions", stats["exceptions"], "ruby_err", stats["ruby_err"])
    print("len", report["len_min"], report["len_avg"], report["len_max"])
    print("empty sets", stats["empty_sets"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
