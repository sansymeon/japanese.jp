#!/usr/bin/env python3
"""Build Lessons 1–10 Compounds production JSON + HTML shells.

Vocabulary comes from _l01_10_vocab.json (parsed from the legacy HTML).
Run with the repo venv (fugashi).
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import fugashi

from _examples_l01_05_10 import as_map as hand_map

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # kml/
COMP_HTML = ROOT / "contents/books/book_01/compounds"
MASTER = ROOT / "data/kanji/kanji_master.csv"
VOCAB = HERE / "_l01_10_vocab.json"
TAGGER = fugashi.Tagger()

KANJI_CHAR = re.compile(r"[\u4e00-\u9fff]")
ADVANCED = (
    "ので",
    "ながら",
    "ても",
    "ために",
    "させる",
    "られる",
    "について",
    "にとって",
    "ている",
    "ていた",
    "ば、",
    "たら",
    "なら",
    "のに",
    "わけ",
    "はず",
    "べき",
)

IMAGES = {
    1: ("assets/studies/rice.jpg", "Rice fields in Japan"),
    2: ("assets/studies/apple_blossoms.jpg", "Apple blossoms"),
    3: ("assets/studies/creek.jpg", "A creek in the Japanese countryside"),
    4: ("assets/studies/meadow.jpg", "A meadow in Japan"),
    5: ("assets/studies/futamigaura.jpg", "Futami-ga-ura, the wedded rocks"),
    6: ("assets/studies/lake_toya.jpg", "Lake Toya"),
    7: ("assets/studies/kyoto_autumn.jpg", "Kyoto in autumn"),
    8: ("assets/studies/large_river.jpg", "A wide river in Japan"),
    9: ("assets/studies/japan_alps_winter.jpg", "The Japan Alps in winter"),
    10: ("assets/studies/marsh.jpg", "A marsh in Japan"),
}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<script>
try {{
  if (localStorage.getItem("kml-compounds-furigana") === "off") {{
    document.documentElement.classList.add("furigana-off");
  }}
}} catch (err) {{}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Yuji+Syuku&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Yomogi&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP&family=Yuji+Mai&display=swap" rel="stylesheet">
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <title>KML - Lesson {n} Compounds</title>
 <link rel="stylesheet" href="../../../../assets/site/css/kml_style.css" />
 <link rel="stylesheet" href="../../../../assets/site/css/compounds-lesson.css" />
</head>
<body class="compounds-lesson" data-compounds="../../../../data/compounds/lesson_{nn}.json" data-kml-base="../../../../">
 <div class="navbar">
{nav}
 </div>

<!-- compound-film -->
<div class="compound-film" data-youtube="" hidden></div>

<figure class="compounds-hero" id="compounds-hero" hidden></figure>

<h1>Lesson {n} — Compounds</h1>

<div class="furigana-bar">
  <button type="button" class="furigana-toggle" id="furigana-toggle" aria-pressed="true" aria-label="Furigana on">
    Furigana
    <span class="furigana-mark" aria-hidden="true"></span>
  </button>
</div>

<div id="compounds-root" class="compounds-sheet">
  <p class="compounds-status">Loading compounds…</p>
</div>
<noscript>
  <p class="compounds-status">Compounds for this lesson need JavaScript to load.</p>
</noscript>

 <div class="stamps">
  <img src="../../../../assets/site/stamps/symeon_stamp.png" alt="Symeon Stamp" width="48" loading="lazy" decoding="async">
  <img src="../../../../assets/site/stamps/chatgpt_stamp.png" alt="ChatGPT Stamp" width="48" loading="lazy" decoding="async">
 </div>
<script src="../../../../assets/site/js/compounds-lesson.js"></script>
</body>
</html>
"""


def kata_to_hira(text: str) -> str:
    out = []
    for ch in text or "":
        o = ord(ch)
        if 0x30A1 <= o <= 0x30F6:
            out.append(chr(o - 0x60))
        else:
            out.append(ch)
    return "".join(out)


def load_keywords() -> dict[str, str]:
    out = {}
    with MASTER.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            k = (row.get("kanji") or "").strip()
            kw = (row.get("display_keyword") or row.get("keyword") or "").strip()
            if k and kw:
                out[k] = kw
    return out


def load_overlays() -> dict[tuple[int, str, str], list[tuple[str, str]]]:
    overlay: dict[tuple[int, str, str], list[tuple[str, str]]] = defaultdict(list)
    for lesson, surface, reading, ja, en in []:
        overlay[(lesson, surface, reading)].append((ja, en))
    hand = hand_map()
    for key, rows in hand.items():
        overlay[key].extend(rows)
    for path in sorted(HERE.glob("_examples_l*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data.get("items") or []:
            overlay[(int(item["lesson"]), item["surface"], item["reading"])].append(
                (item["ja"], item["en"])
            )
    return overlay


def pick(key: str, options: list):
    n = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return options[n % len(options)]


def masu(verb: str) -> str:
    if verb.endswith("する"):
        return verb[:-2] + "します"
    if len(verb) >= 2 and verb.endswith("る") and verb[-2] in "いきぎしじちぢにひびみりえけげせぜてでねへべめれ":
        return verb[:-1] + "ます"
    table = {
        "す": "します",
        "く": "きます",
        "ぐ": "ぎます",
        "む": "みます",
        "ぶ": "びます",
        "ぬ": "にます",
        "つ": "ちます",
        "う": "います",
        "る": "ります",
    }
    if verb and verb[-1] in table:
        return verb[:-1] + table[verb[-1]]
    return verb + "ます"


def fallback(lesson: int, surface: str, reading: str, meaning: str) -> tuple[str, str]:
    gloss = (meaning or reading).split(",")[0].split(";")[0].strip()
    m = meaning.lower() if meaning else ""
    if surface.endswith(("。", "！")):
        return f"今朝、{surface}", f"{gloss}."
    if "を" in surface or "に" in surface:
        if lesson <= 3:
            return f"私は{surface}。", f"I {gloss[3:] if m.startswith('to ') else gloss}."
        return f"彼はよく{surface}。", f"He often {gloss[3:] if m.startswith('to ') else gloss}."
    if m.startswith("to ") or surface.endswith(("する", "ずる")):
        form = masu(surface)
        if lesson <= 3:
            ja = pick(surface, [f"毎朝{form}。", f"ここで{form}。", f"静かに{form}。"])
            en = pick(surface, [f"I {gloss[3:]} every morning.", f"I {gloss[3:]} here.", f"I {gloss[3:]} quietly."])
            return ja, en
        if lesson <= 7:
            ja = pick(surface, [f"昨日{form[:-2]}ました。", f"今は{form[:-2]}ません。", f"もう一度{form}。"])
            en = pick(surface, [f"I {gloss[3:]} yesterday.", f"I do not {gloss[3:]} now.", f"I {gloss[3:]} once more."])
            return ja, en
        ja = pick(surface, [f"もう{form[:-2]}ました。", f"一人で{form}。", f"まだ{form}。"])
        en = pick(surface, [f"I already {gloss[3:]}.", f"I {gloss[3:]} alone.", f"I still {gloss[3:]}."])
        return ja, en
    if surface.endswith("い") and any(
        w in m for w in ("old", "bright", "white", "early", "fast", "thick", "fat", "warm", "cold", "embarrass", "odd", "strange")
    ):
        return f"この道は{surface}です。", f"This road is {gloss}."
    if lesson <= 3:
        ja = pick(surface + reading, [
            f"近くに{surface}があります。",
            f"{surface}は静かです。",
            f"今日は{surface}です。",
            f"{surface}を見ます。",
            f"店で{surface}を買います。",
        ])
        en = pick(surface + reading, [
            f"There is {gloss} nearby.",
            f"{gloss.capitalize()} is quiet.",
            f"Today it is {gloss}.",
            f"I look at {gloss}.",
            f"I buy {gloss} at the shop.",
        ])
        return ja, en
    if lesson <= 7:
        ja = pick(surface + reading, [
            f"昨日、{surface}を見ました。",
            f"新しい{surface}が好きです。",
            f"学校で{surface}を習います。",
            f"{surface}はありません。",
            f"小さな{surface}です。",
        ])
        en = pick(surface + reading, [
            f"I saw {gloss} yesterday.",
            f"I like a new {gloss}.",
            f"I learn about {gloss} at school.",
            f"There is no {gloss}.",
            f"It is a small {gloss}.",
        ])
        return ja, en
    ja = pick(surface + reading, [
        f"夜の{surface}は静かです。",
        f"もう{surface}を忘れました。",
        f"一人で{surface}を持ちます。",
        f"まだ{surface}が残ります。",
        f"村の{surface}を話します。",
    ])
    en = pick(surface + reading, [
        f"{gloss.capitalize()} is quiet at night.",
        f"I already forgot the {gloss}.",
        f"I carry the {gloss} by myself.",
        f"Some {gloss} still remains.",
        f"I talk of the village {gloss}.",
    ])
    return ja, en


def ruby_segments(ja: str, target: str, target_reading: str) -> list[dict]:
    segs: list[dict] = []
    idx = ja.find(target)
    pos = 0
    pending_plain = ""

    def flush_plain() -> None:
        nonlocal pending_plain
        if pending_plain:
            segs.append({"text": pending_plain})
            pending_plain = ""

    def emit_ruby(text: str, reading: str) -> None:
        flush_plain()
        segs.append({"text": text, "reading": reading})

    def emit_plain(text: str) -> None:
        nonlocal pending_plain
        pending_plain += text

    tokens = list(TAGGER(ja))
    i = 0
    while pos < len(ja):
        if idx >= 0 and pos == idx:
            emit_ruby(target, target_reading)
            pos += len(target)
            consumed = 0
            while i < len(tokens) and consumed < len(target):
                consumed += len(tokens[i].surface)
                i += 1
            continue
        if i >= len(tokens):
            emit_plain(ja[pos:])
            break
        tok = tokens[i]
        surf = tok.surface
        if idx >= 0 and pos < idx < pos + len(surf):
            prefix = ja[pos:idx]
            if prefix:
                emit_plain(prefix)
            pos = idx
            continue
        feat = tok.feature
        kana = kata_to_hira(getattr(feat, "kana", None) or "")
        if KANJI_CHAR.search(surf) and kana:
            m = re.match(r"^(.*?)([ぁ-んァ-ンー]*)$", surf)
            if m and m.group(2):
                kanji_part, okuri = m.group(1), m.group(2)
                hira_okuri = kata_to_hira(okuri)
                ruby_read = kana[: max(1, len(kana) - len(hira_okuri))] if kana.endswith(hira_okuri) else kana
                if kanji_part:
                    emit_ruby(kanji_part, ruby_read)
                emit_plain(okuri)
            else:
                emit_ruby(surf, kana)
        else:
            emit_plain(surf)
        pos += len(surf)
        i += 1
    flush_plain()
    joined = "".join(s["text"] for s in segs)
    if joined != ja:
        if idx < 0:
            return [{"text": ja}]
        out = []
        if idx:
            out.append({"text": ja[:idx]})
        out.append({"text": target, "reading": target_reading})
        if idx + len(target) < len(ja):
            out.append({"text": ja[idx + len(target) :]})
        return out
    return segs


def nav_html(n: int) -> str:
    lines = [
        '   <a href="../index.html">🏠 Home</a>',
        '   <a href="../lessons/lesson_01.html">📚 Lesson 1 Index</a>',
    ]
    if n > 1:
        lines.append(f'   <a href="./lesson_{n-1:02d}.html">⬅️ Previous Lesson</a>')
    lines.append(f'   <a href="./lesson_{n+1:02d}.html">➡️ Next Lesson</a>')
    return "\n".join(lines)


def make_id(n: int, surface: str, reading: str, used: Counter) -> str:
    base = f"l{n:02d}_{surface}"
    used[base] += 1
    if used[base] == 1:
        return base
    return f"l{n:02d}_{surface}_{reading}"


def main() -> None:
    keywords = load_keywords()
    overlays = load_overlays()
    overlay_cursor = defaultdict(int)
    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    used_ja: set[str] = set()
    stats = {"items": 0, "sentences": 0, "lens": [], "errors": [], "above": [], "fallback": 0, "empty": []}

    for n in range(1, 11):
        characters = vocab["characters"][str(n)]
        img, alt = IMAGES[n]
        out_chars = []
        ids = Counter()
        for ch in characters:
            comps = []
            keyword = ch.get("keyword") or keywords.get(ch["kanji"], "")
            for c in ch["compounds"]:
                stats["items"] += 1
                key = (n, c["surface"], c["reading"])
                rows = overlays.get(key) or []
                i = overlay_cursor[key]
                if i < len(rows):
                    ja, en = rows[i]
                    overlay_cursor[key] = i + 1
                else:
                    ja, en = fallback(n, c["surface"], c["reading"], c["meaning"])
                    stats["fallback"] += 1
                if not ja.strip() or not en.strip():
                    stats["empty"].append((n, c["surface"]))
                if ja in used_ja:
                    ja = ("今日、" + ja) if not ja.startswith("今日") else ja[:-1] + "よ。"
                used_ja.add(ja)
                if c["surface"] not in ja:
                    ja = f"{c['surface']}は大切です。"
                    en = f"{c['meaning'] or c['surface']} is important."
                    stats["errors"].append((n, c["surface"], "missing-in-sentence", ja))
                segs = ruby_segments(ja, c["surface"], c["reading"])
                if "".join(s["text"] for s in segs) != ja:
                    stats["errors"].append((n, c["surface"], "ruby", ja))
                    segs = ruby_segments(ja, c["surface"], c["reading"])
                for mark in ADVANCED:
                    if mark in ja:
                        stats["above"].append((n, c["surface"], mark, ja))
                stats["lens"].append(len(ja))
                stats["sentences"] += 1
                comps.append(
                    {
                        "id": make_id(n, c["surface"], c["reading"], ids),
                        "surface": c["surface"],
                        "reading": c["reading"],
                        "meaning": c["meaning"],
                        "sourceGloss": c["meaning"],
                        "example": {"ja": ja, "en": en, "segments": segs},
                    }
                )
            out_chars.append(
                {
                    "kanji": ch["kanji"],
                    "readings": ch.get("readings") or "",
                    "keyword": keyword,
                    "compounds": comps,
                }
            )
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
        print(f"lesson {n:02d}  kanji {len(out_chars)}  words {sum(len(c['compounds']) for c in out_chars)}")

    print("items", stats["items"], "sentences", stats["sentences"], "fallback", stats["fallback"])
    if stats["lens"]:
        print(
            "len min/avg/max",
            min(stats["lens"]),
            round(sum(stats["lens"]) / len(stats["lens"]), 1),
            max(stats["lens"]),
        )
    print("errors", len(stats["errors"]))
    for row in stats["errors"][:30]:
        print(" ERR", row)
    print("above-band", len(stats["above"]))
    for row in stats["above"][:40]:
        print(" ABOVE", row)
    print("empty", stats["empty"])


if __name__ == "__main__":
    sys.exit(main() or 0)
