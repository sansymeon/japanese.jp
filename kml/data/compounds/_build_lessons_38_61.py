#!/usr/bin/env python3
"""Build Lessons 38–61 Compounds. Skip 42 (already production). Do not touch 1–37."""

from __future__ import annotations

import json
import re
import shutil
import unicodedata
from collections import Counter
from pathlib import Path

import fugashi

from _build_lessons_01_10 import (
    HTML,
    load_keywords,
    make_id,
    masu,
    nav_html,
    ruby_segments,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMP_HTML = ROOT / "contents/books/book_01/compounds"
LEGACY = HERE / "_legacy_html_l38_61"
SELECTION = HERE / "selection"
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
NAMES_KIND = re.compile(
    r"place name|given name|surname|family name|personal name|proper name",
    re.I,
)
PLACE = {
    "乃木坂",
    "桑名",
    "長崎",
    "川崎",
    "宮崎",
    "奈良",
    "京都",
    "大阪",
    "東京",
    "北海道",
    "沖縄",
    "名古屋",
}

REMOVE = {
    (38, "船一隻"),
    (38, "片手一隻"),
    (38, "養蚕桑園"),
    (39, "葉柄茎"),
    (39, "伯叔"),
    (40, "神采"),
    (40, "曖昧な返事"),
    (40, "曖昧表現"),
    (41, "冶工"),
    (46, "交迭"),
    (49, "和~"),
    (50, "精神的糧"),
    (50, "謎謎"),
    (53, "伯叔"),
    (55, "傾らか"),
    (55, "何~"),
    (55, "甲乙丙"),
    (59, "涙腺分泌"),
}
REMOVE_META = {
    (38, "船一隻"): ("NON_LEXICAL", "Counter phrase concatenating 船+一隻; 一隻 remains."),
    (38, "片手一隻"): ("NON_LEXICAL", "Pedagogical counter example, not a lexical item."),
    (38, "養蚕桑園"): ("NON_LEXICAL", "Concatenated 養蚕+桑園."),
    (39, "葉柄茎"): ("NON_LEXICAL", "Concatenated 葉柄+茎 pad under 茎."),
    (39, "伯叔"): ("NON_LEXICAL", "Chinese order; Japanese uses 伯叔父/叔父."),
    (40, "神采"): ("NON_LEXICAL", "Chinese 神采; Japanese is 風采."),
    (40, "曖昧な返事"): ("NON_LEXICAL", "Example phrase stored as a target; 曖昧 remains."),
    (40, "曖昧表現"): ("NON_LEXICAL", "Padded 曖昧+表現."),
    (41, "冶工"): ("NON_LEXICAL", "Pad under 冶 beside 鍛冶/鍛冶屋."),
    (46, "交迭"): ("NON_LEXICAL", "Chinese 交迭; Japanese is 更迭."),
    (49, "和~"): ("MALFORMED", "Combining-form stub, not a lexical word."),
    (50, "精神的糧"): ("NON_LEXICAL", "Padded 精神的+糧 phrase."),
    (50, "謎謎"): ("MALFORMED", "Duplicate of 謎々 with a nonstandard surface."),
    (53, "伯叔"): ("NON_LEXICAL", "Chinese order; Japanese uses 伯叔父/叔父."),
    (55, "傾らか"): ("PAD", "Kanji assigned to なだらか to pad 傾; not a genuine spelling."),
    (55, "何~"): ("MALFORMED", "Combining-form stub, not a lexical word."),
    (55, "甲乙丙"): ("NON_LEXICAL", "Concatenated teaching list of 甲乙+丙."),
    (59, "涙腺分泌"): ("NON_LEXICAL", "Concatenated 涙腺+分泌."),
}

IMAGES = {
    38: ("assets/studies/fog.jpg", "Fog in Japan"),
    39: ("assets/studies/pine_tree.jpg", "A pine tree in Japan"),
    40: ("assets/studies/shiretoko_ice.jpg", "Ice at Shiretoko"),
    41: ("assets/studies/snow.jpg", "Snow in Japan"),
    43: ("assets/studies/cherry_blossom.jpg", "Cherry blossoms"),
    44: ("assets/studies/spring.jpg", "Spring in Japan"),
    45: ("assets/studies/sea.jpg", "The sea in Japan"),
    46: ("assets/studies/waves.jpg", "Waves on a Japanese shore"),
    47: ("assets/studies/winter.jpg", "Winter in Japan"),
    48: ("assets/studies/rice_post_harvest.jpg", "Rice fields after harvest"),
    49: ("assets/studies/paddy_ridge.jpg", "A paddy ridge"),
    50: ("assets/studies/wisteria.jpg", "Wisteria in Japan"),
    51: ("assets/studies/mountain_peak.jpg", "A mountain peak"),
    52: ("assets/studies/mountain_pass.jpg", "A mountain pass"),
    53: ("assets/studies/rainbow.jpg", "A rainbow in Japan"),
    54: ("assets/studies/rain.jpg", "Rain in Japan"),
    55: ("assets/studies/monkey_hotspring.jpg", "Monkeys at a hot spring"),
    56: ("assets/studies/open_sea.jpg", "The open sea"),
    57: ("assets/studies/home.jpg", "A home in Japan"),
    58: ("assets/studies/mountain.jpg", "A mountain in Japan"),
    59: ("assets/studies/frost.jpg", "Frost in Japan"),
    60: ("assets/studies/foot_of_mountain.jpg", "The foot of a mountain"),
    61: ("assets/studies/bamboo_grass.jpg", "Bamboo grass"),
}

HAND: dict[tuple[int, str], tuple[str, str, str | None]] = {}


def clean_reading(raw: str) -> str:
    text = unicodedata.normalize("NFKC", raw).strip()
    text = text.split("／")[0].split("/")[0].split(";")[0].split("；")[0].strip()
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
    html = src.read_text(encoding="utf-8")
    chars = []
    for kanji, mid, ul in BLOCK_RE.findall(html):
        if "will be added here" in ul:
            continue
        readings, keyword = parse_h2(mid)
        comps = []
        for surface, reading, gloss in ITEM_RE.findall(ul):
            comps.append(
                {
                    "surface": unicodedata.normalize("NFKC", surface).strip(),
                    "reading": clean_reading(reading),
                    "meaning": re.sub(r"\s+", " ", gloss).strip(" .–-"),
                    "flags": [],
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


def parse_selection(n: int) -> list[dict]:
    data = json.loads((SELECTION / f"lesson_{n:02d}.json").read_text(encoding="utf-8"))
    chars = []
    for ch in data.get("characters") or []:
        comps = []
        for c in ch.get("compounds") or []:
            comps.append(
                {
                    "surface": c["surface"],
                    "reading": clean_reading(c.get("reading") or ""),
                    "meaning": (c.get("meaning") or "").strip(),
                    "flags": list(c.get("flags") or []),
                }
            )
        chars.append(
            {
                "kanji": ch.get("kanji") or "",
                "readings": (ch.get("readings") or "").replace(" ", ""),
                "keyword": ch.get("keyword") or "",
                "compounds": comps,
            }
        )
    return chars


def analyze(surface: str) -> tuple[str, str, str, int]:
    try:
        toks = list(TAGGER(surface))
    except Exception:
        return "", "", "", 0
    if not toks:
        return "", "", "", 0
    feat = toks[-1].feature
    return (
        getattr(feat, "pos1", "") or "",
        getattr(feat, "pos3", "") or "",
        getattr(feat, "cType", "") or "",
        len(toks),
    )


def mashita(verb: str) -> str:
    form = masu(verb)
    if form.endswith("ます"):
        return form[:-2] + "ました"
    return form


def gloss_head(meaning: str) -> str:
    g = re.sub(r"^\([^)]*\)\s*", "", (meaning or "").strip())
    g = g.split(",")[0].split(";")[0].split("/")[0].split("(")[0].strip()
    return g or "it"


def has_word(text: str, *words: str) -> bool:
    return any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)


def is_name(surface: str, meaning: str, flags: list[str]) -> bool:
    if surface in PLACE:
        return True
    if NAMES_KIND.search(meaning or ""):
        return True
    if "name" in " ".join(flags).lower():
        return True
    return False


def en_have(who: str) -> str:
    return "have" if who == "私は" else "has"


def sentence(lesson: int, surface: str, reading: str, meaning: str) -> tuple[str, str, str | None]:
    key = (lesson, surface)
    if key in HAND:
        return HAND[key]
    m = (meaning or "").lower()
    gloss = gloss_head(meaning)
    h = abs(hash(f"{lesson}|{surface}|{reading}"))
    pos1, pos3, ctype, ntok = analyze(surface)
    who = ["私は", "兄は", "母は", "妹は", "父は"][h % 5]
    subj = {
        "私は": "I",
        "兄は": "My older brother",
        "母は": "My mother",
        "妹は": "My little sister",
        "父は": "My father",
    }[who]
    time = ""
    if lesson >= 48 and h % 4 == 0:
        time = "昨日、"
    elif lesson >= 40 and h % 5 == 0:
        time = "朝、"
    verbish = pos1 == "動詞"
    sahen = surface.endswith("する") or (ntok == 1 and pos3 == "サ変可能")

    grim = has_word(
        m,
        "death",
        "die",
        "died",
        "behead",
        "beheading",
        "murder",
        "kill",
        "suicide",
        "pass away",
        "passing away",
        "fracture",
        "infarction",
        "heart attack",
    )
    if grim:
        return (
            f"授業で{surface}を学びました。",
            f"We learned about {gloss.lower()} in class.",
            None,
        )

    if is_name(surface, meaning, []):
        if lesson >= 50:
            return (
                f"来月、{surface}へ行く予定です。",
                f"I am scheduled to go to {surface} next month.",
                None,
            )
        return (f"{surface}に住んでいます。", f"I live in {surface}.", None)

    if "を" in surface:
        form = mashita(surface) if lesson >= 44 else masu(surface)
        g = gloss.lower()
        if g.startswith("to "):
            g = g[3:]
        return f"{who}{form}。", f"{subj} {g}.", None

    if verbish and not sahen:
        form = mashita(surface) if (h % 2 == 0 or lesson >= 50) else masu(surface)
        g = gloss.lower()
        if g.startswith("to "):
            g = g[3:]
        if lesson >= 52 and h % 5 == 0:
            return (
                f"{who}{form}から、家へ帰りました。",
                f"{subj} {g}, then went home.",
                None,
            )
        return f"{time}{who}{form}。", f"{subj} {g}.", None

    if pos1 == "形容詞" or (surface.endswith("い") and reading.endswith("い") and pos1 != "名詞"):
        return f"今日は{surface}です。", f"It is {gloss.lower()} today.", None

    if pos3 == "副詞可能" and has_word(m, "moment", "instant", "suddenly", "immediately", "soon"):
        return (
            f"{surface}、雨がやみました。",
            f"{gloss.capitalize()}, the rain stopped.",
            None,
        )

    if has_word(m, "place", "city", "town", "prefecture", "station", "temple", "shrine"):
        return f"{surface}は山の近くです。", f"{gloss} is near the mountains.", None

    if surface in ("会議", "予定"):
        return f"午後から{surface}があります。", f"There is a {gloss.lower()} in the afternoon.", None
    if surface == "在庫":
        return "店の在庫を数えました。", "I counted the shop's inventory.", None

    if has_word(m, "tea", "milk", "rice", "vegetable", "cabbage", "fruit", "food", "meal", "bread", "fish", "meat"):
        return f"夕食に{surface}を食べました。", f"I ate {gloss.lower()} for dinner.", None

    if surface.endswith(("科", "院", "局", "署")):
        return f"明日、{surface}へ行きます。", f"Tomorrow I will go to the {gloss.lower()}.", None

    if has_word(
        m,
        "friend",
        "teacher",
        "doctor",
        "uncle",
        "aunt",
        "husband",
        "wife",
        "child",
        "officer",
        "guard",
        "priest",
        "prince",
        "princess",
        "clerk",
        "chef",
        "worker",
    ):
        return f"{surface}と駅で会いました。", f"I met {gloss.lower()} at the station.", None

    if has_word(m, "hand", "eye", "nose", "finger", "leg", "arm", "joint", "ear", "shoulder", "neck") and not surface.endswith(("科", "院")):
        return f"寒いと{surface}が冷たくなります。", f"When it is cold, my {gloss.lower()} gets cold.", None

    if sahen:
        g = gloss.lower()
        if lesson >= 55 and h % 4 == 0:
            return (
                f"{who}{surface}しなければならないと思います。",
                f"{subj} think{'s' if who != '私は' else ''} {g} is necessary.",
                None,
            )
        if lesson >= 48 and h % 3 == 0:
            return (
                f"{surface}してから、手紙を書きました。",
                f"After {g}, I wrote a letter.",
                None,
            )
        if lesson >= 45 and h % 5 == 0:
            return (
                f"{who}{surface}したことがあります。",
                f"{subj} {en_have(who)} done {g} before.",
                None,
            )
        if h % 2 == 0:
            return f"会社は{surface}しています。", f"The company is doing {g}.", None
        return f"{who}{surface}します。", f"{subj} {'do' if who=='私は' else 'does'} {g}.", None

    visible = has_word(
        m,
        "mountain",
        "sea",
        "river",
        "temple",
        "shrine",
        "theatre",
        "theater",
        "film",
        "picture",
        "flower",
        "tree",
        "bridge",
        "castle",
        "building",
        "festival",
        "garden",
        "island",
        "lake",
        "snow",
        "rain",
        "cloud",
        "star",
        "moon",
        "bird",
        "fish",
        "animal",
        "statue",
        "painting",
        "tower",
        "gate",
        "road",
        "house",
        "shop",
        "book",
    )
    if lesson >= 45 and visible and h % 2 == 0:
        return (
            f"{who}{surface}を見たことがあります。",
            f"{subj} {en_have(who)} seen {gloss.lower()} before.",
            None,
        )

    frames = [
        (f"授業で{surface}を学びました。", f"We learned about {gloss.lower()} in class."),
        (f"{surface}の話を聞きました。", f"I heard a story about {gloss.lower()}."),
        (f"ノートに{surface}を書きました。", f"I wrote {gloss.lower()} in my notebook."),
        (f"本で{surface}を知りました。", f"I learned about {gloss.lower()} from a book."),
        (f"辞書で{surface}を調べました。", f"I looked up {gloss.lower()} in the dictionary."),
        (f"新聞で{surface}を読みました。", f"I read about {gloss.lower()} in the newspaper."),
        (f"友達に{surface}を教えました。", f"I taught my friend about {gloss.lower()}."),
        (f"ラジオで{surface}の話を聞きました。", f"I heard about {gloss.lower()} on the radio."),
    ]
    if lesson >= 46:
        frames.append(
            (f"{surface}なので、少し休みました。", f"Because of {gloss.lower()}, I rested a little.")
        )
    if lesson >= 50:
        frames.append(
            (f"{surface}について考えました。", f"I thought about {gloss.lower()}.")
        )
        frames.append(
            (f"来年も{surface}を使うつもりです。", f"I intend to use {gloss.lower()} next year too.")
        )
    if lesson >= 53:
        frames.append(
            (
                f"この説明は{surface}ほど難しくありません。",
                f"This explanation is not as hard as {gloss.lower()}.",
            )
        )
        frames.append(
            (f"兄は{surface}という言葉を使います。", f"My older brother uses the word {gloss.lower()}.")
        )
    if lesson >= 58:
        frames.append(
            (
                f"{surface}について、先生に聞きました。",
                f"I asked the teacher about {gloss.lower()}.",
            )
        )
        frames.append(
            (f"{surface}のほうが簡単だと思います。", f"I think {gloss.lower()} is easier.")
        )
    ja, en = frames[h % len(frames)]
    return ja, en, None


def load_hand() -> None:
    path = HERE / "_examples_l38_61.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data.get("items") or []:
        HAND[(int(item["lesson"]), item["surface"])] = (
            item["ja"],
            item["en"],
            item.get("exception"),
        )


def fix_incidental(ja: str, segs: list[dict]) -> None:
    for seg in segs:
        if seg.get("text") == "米" and seg.get("reading") == "べい" and "米国" not in ja:
            seg["reading"] = "こめ"
        if seg.get("text") == "日" and seg.get("reading") == "にち" and ja.startswith("今日"):
            if seg is segs[0] or (len(segs) > 1 and segs[0].get("text") == "今"):
                pass


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
        "ruby_err": 0,
        "empty_sets": [],
        "by_lesson": {},
        "lens": [],
        "templates": Counter(),
    }
    used_ja: set[str] = set()

    lessons = [n for n in range(38, 62) if n != 42]
    for n in lessons:
        if 38 <= n <= 41:
            chars = parse_lesson_html(n)
        else:
            chars = parse_selection(n)
        out_chars = []
        ids = Counter()
        word_n = 0
        for ch in chars:
            comps = []
            kw = ch.get("keyword") or keywords.get(ch["kanji"], "")
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
                ja, en, exc = sentence(n, c["surface"], c["reading"], c["meaning"])
                if ja in used_ja:
                    ja = ("また、" + ja) if not ja.startswith("また") else ja[:-1] + "よ。"
                used_ja.add(ja)
                if "があります" in ja and "書いてあります" not in ja:
                    stats["templates"]["があります"] += 1
                if "が好きです" in ja:
                    stats["templates"]["好き"] += 1
                if "を習います" in ja:
                    stats["templates"]["習います"] += 1
                segs = ruby_segments(ja, c["surface"], c["reading"])
                fix_incidental(ja, segs)
                if "".join(s["text"] for s in segs) != ja:
                    stats["ruby_err"] += 1
                    segs = [{"text": ja}]
                    review.append({"lesson": n, "surface": c["surface"], "issue": "ruby-join", "ja": ja})
                rec = {
                    "id": make_id(n, c["surface"], c["reading"], ids),
                    "surface": c["surface"],
                    "reading": c["reading"],
                    "meaning": c["meaning"],
                    "sourceGloss": c["meaning"],
                    "example": {"ja": ja, "en": en, "segments": segs},
                }
                flags = c.get("flags") or []
                if is_name(c["surface"], c["meaning"], flags):
                    rec["kind"] = "name"
                    stats["names"] += 1
                qa = {}
                if exc:
                    qa["grammarException"] = True
                    qa["reason"] = exc
                    stats["exceptions"] += 1
                if "uncertain" in flags:
                    qa["review"] = True
                    qa["reviewNote"] = "Selection marked uncertain; kept pending human review."
                    review.append(
                        {
                            "lesson": n,
                            "surface": c["surface"],
                            "reading": c["reading"],
                            "meaning": c["meaning"],
                            "issue": "uncertain-keep",
                            "ja": ja,
                        }
                    )
                if "literary" in flags:
                    qa["migrationNote"] = "Literary vocabulary retained."
                if "specialized" in flags:
                    qa.setdefault("migrationNote", "Specialized vocabulary retained.")
                if c["surface"] in ("乃公", "胥吏", "隻翼", "勾欄"):
                    qa["review"] = True
                    qa["reviewNote"] = "Archaic/historical item kept."
                    review.append(
                        {
                            "lesson": n,
                            "surface": c["surface"],
                            "issue": "specialized-keep",
                            "ja": ja,
                        }
                    )
                if qa:
                    rec["qa"] = qa
                comps.append(rec)
                stats["retained"] += 1
                stats["lens"].append(len(ja))
                word_n += 1
            if not comps:
                stats["empty_sets"].append((n, ch["kanji"]))
            out_chars.append(
                {
                    "kanji": ch["kanji"],
                    "readings": ch.get("readings") or "",
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
                "band": "early-middle",
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
        stats["by_lesson"][n] = word_n
        print(f"lesson {n:02d}  kanji {len(out_chars)}  words {word_n}")

    report = {
        "removed": removed,
        "review": review,
        "stats": {k: v for k, v in stats.items() if k not in ("lens", "templates")},
        "templates": dict(stats["templates"]),
        "len_min": min(stats["lens"]) if stats["lens"] else 0,
        "len_avg": round(sum(stats["lens"]) / len(stats["lens"]), 1) if stats["lens"] else 0,
        "len_max": max(stats["lens"]) if stats["lens"] else 0,
        "by_lesson": stats["by_lesson"],
    }
    (HERE / "_review_queue_38_61.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "inspected",
        stats["inspected"],
        "retained",
        stats["retained"],
        "removed",
        stats["removed"],
        "names",
        stats["names"],
        "exceptions",
        stats["exceptions"],
        "ruby_err",
        stats["ruby_err"],
    )
    print("templates", dict(stats["templates"]))
    print("empty", stats["empty_sets"])
    print("len", report["len_min"], report["len_avg"], report["len_max"])
    return 0 if not stats["ruby_err"] and not stats["empty_sets"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
