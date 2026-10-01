#!/usr/bin/env python3
"""Build Lessons 35–37 Compounds JSON + HTML. Calibration batch only."""

from __future__ import annotations

import json
import re
import shutil
import unicodedata
from collections import Counter
from pathlib import Path

from _build_lessons_01_10 import (
    HTML,
    load_keywords,
    make_id,
    nav_html,
    ruby_segments,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMP_HTML = ROOT / "contents/books/book_01/compounds"
LEGACY = HERE / "_legacy_html_l35_37"

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

REMOVE = {
    (35, "惧心"),
    (35, "憧夢"),
    (35, "憧心"),
    (35, "憬然"),
    (35, "憬悟"),
    (35, "憬慕"),
    (35, "憬想"),
    (35, "半拉致"),
    (36, "批改"),
    (36, "会釈挨拶"),
    (36, "朝の挨拶"),
    (36, "難題に挑む"),
    (36, "拐誘"),
    (37, "作業が捗る"),
    (37, "弄花"),
}
REMOVE_META = {
    (35, "惧心"): ("NON_LEXICAL", "惧 + 心 on-yomi pad under 惧."),
    (35, "憧夢"): ("NON_LEXICAL", "憧 + 夢 pad under 憧."),
    (35, "憧心"): ("NON_LEXICAL", "憧 + 心 pad under 憧."),
    (35, "憬然"): ("NON_LEXICAL", "憬 is not productive; 然-pad beside 憧憬."),
    (35, "憬悟"): ("NON_LEXICAL", "Chinese-style 憬 glue; not ordinary Japanese."),
    (35, "憬慕"): ("NON_LEXICAL", "憬 + 慕 pad; 敬慕/恋慕 already teach 慕."),
    (35, "憬想"): ("NON_LEXICAL", "憬 + 想 pad under 憬."),
    (35, "半拉致"): ("NON_LEXICAL", "Invented ‘partial abduction’; not a lexical unit."),
    (36, "批改"): ("NON_LEXICAL", "Chinese 批改; Japanese uses 添削/訂正."),
    (36, "会釈挨拶"): ("NON_LEXICAL", "Concatenated 会釈+挨拶, not one word."),
    (36, "朝の挨拶"): ("NON_LEXICAL", "Phrase stored to pad 挨拶, already taught."),
    (36, "難題に挑む"): ("NON_LEXICAL", "Example collocation stored as a target; 挑む remains."),
    (36, "拐誘"): ("NON_LEXICAL", "Chinese-order blend beside 誘拐; not established."),
    (37, "作業が捗る"): ("NON_LEXICAL", "Full clause stored as vocabulary; 捗る remains."),
    (37, "弄花"): ("NON_LEXICAL", "Interpretive 弄+花 pad under 弄."),
}
CORRECT = {
    (35, "抜粋抄"): ("抜粋", "ばっすい", "Selection, excerpt", "Concatenated 抜粋+抄; recovered as 抜粋."),
}

IMAGES = {
    35: ("assets/studies/mountain_stream.jpg", "A mountain stream in Japan"),
    36: ("assets/studies/waterfall.jpg", "A waterfall in Japan"),
    37: ("assets/studies/autumn.jpg", "Autumn in Japan"),
}

HAND: dict[tuple[int, str], tuple[str, str, str | None]] = {}


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
        src_live = COMP_HTML / f"lesson_{n:02d}.html"
        LEGACY.mkdir(exist_ok=True)
        shutil.copy2(src_live, src)
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


def load_hand() -> None:
    path = HERE / "_examples_l35_37.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data.get("items") or []:
        les = int(item["lesson"])
        if les < 35 or les > 37:
            continue
        HAND[(les, item["surface"])] = (
            item["ja"],
            item["en"],
            item.get("exception"),
        )


def fix_incidental(ja: str, segs: list[dict]) -> None:
    for seg in segs:
        if seg.get("text") == "米" and seg.get("reading") == "べい" and "米国" not in ja:
            seg["reading"] = "こめ"


def main() -> int:
    load_hand()
    keywords = load_keywords()
    removed = []
    review = []
    stats = {
        "inspected": 0,
        "retained": 0,
        "removed": 0,
        "corrected": 0,
        "names": 0,
        "exceptions": 0,
        "ruby_err": 0,
        "empty_sets": [],
        "missing_hand": [],
        "lens": [],
        "by_lesson": {},
    }
    used_ja: set[str] = set()

    for n in range(35, 38):
        chars = parse_lesson_html(n)
        out_chars = []
        ids = Counter()
        word_n = 0
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
                if key in CORRECT:
                    ns, nr, nm, cause = CORRECT[key]
                    removed.append(
                        {
                            "lesson": n,
                            "kanji": ch["kanji"],
                            "original": c["surface"],
                            "reading": c["reading"],
                            "meaning": c["meaning"],
                            "classification": "MALFORMED",
                            "decision": f"Corrected to {ns} / {nr}.",
                            "cause": cause,
                        }
                    )
                    c = {
                        "surface": ns,
                        "reading": nr,
                        "meaning": nm,
                        "legacySurface": key[1],
                    }
                    stats["corrected"] += 1
                    key = (n, ns)
                if key not in HAND:
                    stats["missing_hand"].append(key)
                    continue
                ja, en, exc = HAND[key]
                if ja in used_ja:
                    ja = ja[:-1] + "よ。" if ja.endswith("。") else ja + "よ。"
                used_ja.add(ja)
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
                if c.get("legacySurface"):
                    rec.setdefault("qa", {})
                    rec["qa"]["legacySurface"] = c["legacySurface"]
                    rec["qa"]["migrationNote"] = CORRECT[(n, c["legacySurface"])][3]
                if NAMES_KIND.search(c["meaning"] or ""):
                    rec["kind"] = "name"
                    stats["names"] += 1
                qa = rec.get("qa") or {}
                if exc:
                    qa["grammarException"] = True
                    qa["reason"] = exc
                    stats["exceptions"] += 1
                if c["surface"] in ("拉する", "畏惧", "抱懐", "拐帯", "摘録", "捨象", "達摩"):
                    qa["review"] = True
                    qa["reviewNote"] = "Marked, legal, or literary item kept as genuine."
                    review.append(
                        {
                            "lesson": n,
                            "surface": c["surface"],
                            "reading": c["reading"],
                            "meaning": c["meaning"],
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
        "stats": {k: v for k, v in stats.items() if k != "lens"},
        "len_min": min(stats["lens"]) if stats["lens"] else 0,
        "len_avg": round(sum(stats["lens"]) / len(stats["lens"]), 1) if stats["lens"] else 0,
        "len_max": max(stats["lens"]) if stats["lens"] else 0,
    }
    (HERE / "_review_queue_35_37.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("inspected", stats["inspected"], "retained", stats["retained"], "removed", stats["removed"])
    print("corrected", stats["corrected"], "names", stats["names"], "exceptions", stats["exceptions"])
    print("ruby_err", stats["ruby_err"], "missing_hand", stats["missing_hand"])
    print("empty sets", stats["empty_sets"])
    print("len", report["len_min"], report["len_avg"], report["len_max"])
    return 1 if stats["missing_hand"] or stats["ruby_err"] or stats["empty_sets"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
