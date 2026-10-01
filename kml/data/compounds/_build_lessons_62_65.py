#!/usr/bin/env python3
"""Build Lessons 62–65 Compounds. Do not touch 1–61. Stop after 65."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from _build_lessons_01_10 import HTML, load_keywords, make_id, nav_html, ruby_segments
from _examples_l62_65 import EXAMPLES

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMP_HTML = ROOT / "contents/books/book_01/compounds"
SELECTION = HERE / "selection"

IMAGES = {
    62: ("assets/studies/pond.jpg", "A pond in Japan"),
    63: ("assets/studies/path.jpg", "A path in Japan"),
    64: ("assets/studies/gates.jpg", "Gates in Japan"),
    65: ("assets/studies/nightfall.jpg", "Nightfall in Japan"),
}

REMOVE = {
    (62, "昨", "さく"),
    (62, "掃除", "そうじ (する)"),
    (63, "両~", "りょう"),
}
REMOVE_META = {
    (62, "昨", "さく"): (
        "NON_LEXICAL",
        "Combining prefix (昨年, 昨夜) presented as a standalone word.",
    ),
    (62, "掃除", "そうじ (する)"): (
        "VALID_BUT_METADATA_PROBLEM",
        "Duplicate of 掃除 そうじ; parenthetical する is not a reading.",
    ),
    (63, "両~", "りょう"): (
        "MALFORMED",
        "Combining-form stub, not a lexical word; 両手/両方 remain.",
    ),
}
CORRECT_SURFACE = {
    (63, "曲る"): ("曲がる", "まがる", "to turn, to bend"),
}
MEANING_FIX = {
    (63, "群衆"): "crowd",
    (63, "群集"): "crowd, gathering",
    (63, "漕ぐ"): "to row",
    (64, "橋渡し"): "bridge-building, mediation",
    (65, "片付ける"): "to tidy up",
    (65, "判"): "print size",
}
NAMES = {"群馬", "伊達"}
LITERARY = {"沫雪", "暁光", "池畔", "之", "廿", "措辞", "婉曲", "庸俗", "憤然", "木乃伊"}
SPECIALIZED = {"民事訴訟", "曹洞宗", "儒学", "儒教", "謄本", "燃焼", "法曹"}
REVIEW_KEEP = {"之", "廿", "庸俗", "看護婦", "剥す"}


def clean_reading(raw: str) -> str:
    text = unicodedata.normalize("NFKC", raw).strip()
    text = text.split("／")[0].split("/")[0].split(";")[0].split("；")[0].strip()
    return "".join(chr(ord(c) - 96) if "ァ" <= c <= "ヶ" else c for c in text)


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
                    "raw_reading": (c.get("reading") or "").strip(),
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
                "fewerThanFive": ch.get("fewerThanFive") or "",
            }
        )
    return chars


def fix_incidental(ja: str, segs: list[dict]) -> None:
    for i, seg in enumerate(segs):
        if seg.get("text") == "米" and seg.get("reading") == "べい" and "米国" not in ja:
            seg["reading"] = "こめ"
        if seg.get("text") == "中" and "部屋中" in ja:
            seg["reading"] = "じゅう"
        if (
            seg.get("text") == "日"
            and "日曜日" in ja
            and i
            and segs[i - 1].get("text") == "日曜"
        ):
            seg["reading"] = "び"


def main() -> int:
    keywords = load_keywords()
    removed = []
    review = []
    corrections = []
    stats = {
        "inspected": 0,
        "retained": 0,
        "removed": 0,
        "corrected": 0,
        "names": 0,
        "exceptions": 0,
        "ruby_err": 0,
        "empty_sets": [],
        "short_sets": [],
        "literary": 0,
        "specialized": 0,
        "by_lesson": {},
        "lens": [],
        "missing": [],
    }
    used_ja: set[str] = set()

    for n in range(62, 66):
        chars = parse_selection(n)
        out_chars = []
        ids = Counter()
        word_n = 0
        for ch in chars:
            comps = []
            kw = ch.get("keyword") or keywords.get(ch["kanji"], "")
            for c in ch["compounds"]:
                stats["inspected"] += 1
                surface = c["surface"]
                reading = c["reading"]
                meaning = c["meaning"]
                raw_reading = c.get("raw_reading") or reading
                rm_key = (n, surface, raw_reading)
                rm_key2 = (n, surface, reading)
                if rm_key in REMOVE or rm_key2 in REMOVE:
                    meta_key = rm_key if rm_key in REMOVE_META else rm_key2
                    cls, cause = REMOVE_META[meta_key]
                    removed.append(
                        {
                            "lesson": n,
                            "kanji": ch["kanji"],
                            "original": surface,
                            "reading": raw_reading,
                            "meaning": meaning,
                            "classification": cls,
                            "decision": "Removed; no automatic replacement.",
                            "cause": cause,
                        }
                    )
                    stats["removed"] += 1
                    continue
                if (n, surface) in CORRECT_SURFACE:
                    new_s, new_r, new_m = CORRECT_SURFACE[(n, surface)]
                    corrections.append(
                        {
                            "lesson": n,
                            "kanji": ch["kanji"],
                            "original": surface,
                            "reading": reading,
                            "new": new_s,
                            "newReading": new_r,
                            "classification": "VALID_BUT_METADATA_PROBLEM",
                            "decision": f"Corrected okurigana {surface} → {new_s}.",
                            "cause": "Standard modern spelling is 曲がる.",
                        }
                    )
                    surface, reading, meaning = new_s, new_r, new_m
                    stats["corrected"] += 1
                if (n, surface) in MEANING_FIX:
                    meaning = MEANING_FIX[(n, surface)]
                    stats["corrected"] += 1
                key = (n, surface, reading)
                if key not in EXAMPLES:
                    stats["missing"].append({"lesson": n, "surface": surface, "reading": reading})
                    continue
                ja, en, exc = EXAMPLES[key]
                if ja in used_ja:
                    stats["missing"].append(
                        {"lesson": n, "surface": surface, "issue": "duplicate-ja", "ja": ja}
                    )
                used_ja.add(ja)
                segs = ruby_segments(ja, surface, reading)
                fix_incidental(ja, segs)
                if "".join(s["text"] for s in segs) != ja:
                    stats["ruby_err"] += 1
                    segs = [{"text": ja}]
                    review.append(
                        {"lesson": n, "surface": surface, "issue": "ruby-join", "ja": ja}
                    )
                rec = {
                    "id": make_id(n, surface, reading, ids),
                    "surface": surface,
                    "reading": reading,
                    "meaning": meaning,
                    "sourceGloss": c["meaning"],
                    "example": {"ja": ja, "en": en, "segments": segs},
                }
                qa = {}
                if surface in NAMES or "name" in meaning.lower():
                    rec["kind"] = "name"
                    stats["names"] += 1
                if surface in LITERARY:
                    qa["migrationNote"] = "Literary vocabulary retained."
                    stats["literary"] += 1
                if surface in SPECIALIZED:
                    qa.setdefault("migrationNote", "Specialized vocabulary retained.")
                    stats["specialized"] += 1
                if exc:
                    qa["grammarException"] = True
                    qa["reason"] = exc
                    stats["exceptions"] += 1
                if surface in REVIEW_KEEP:
                    qa["review"] = True
                    notes = {
                        "之": "Classical written 之 kept as a genuine character-word.",
                        "廿": "Rare numeral form kept; one-word set.",
                        "庸俗": "Uncommon Sino-Japanese; kept beside 凡庸.",
                        "看護婦": "Dated female-nurse term; 看護師 is now usual.",
                        "剥す": "Okurigana 剥す for はがす; 剥がす is now more common.",
                    }
                    qa["reviewNote"] = notes[surface]
                    review.append(
                        {
                            "lesson": n,
                            "surface": surface,
                            "reading": reading,
                            "meaning": meaning,
                            "issue": "lexical-review",
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
            elif len(comps) < 5:
                stats["short_sets"].append((n, ch["kanji"], len(comps)))
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
                "band": "middle",
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
        "corrections": corrections,
        "review": review,
        "missing": stats["missing"],
        "stats": {k: v for k, v in stats.items() if k not in ("lens",)},
        "len_min": min(stats["lens"]) if stats["lens"] else 0,
        "len_avg": round(sum(stats["lens"]) / len(stats["lens"]), 1) if stats["lens"] else 0,
        "len_max": max(stats["lens"]) if stats["lens"] else 0,
        "by_lesson": stats["by_lesson"],
    }
    (HERE / "_review_queue_62_65.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "inspected",
        stats["inspected"],
        "retained",
        stats["retained"],
        "removed",
        stats["removed"],
        "corrected",
        stats["corrected"],
        "names",
        stats["names"],
        "exceptions",
        stats["exceptions"],
        "ruby_err",
        stats["ruby_err"],
    )
    print("empty", stats["empty_sets"])
    print("short", stats["short_sets"])
    print("missing", stats["missing"])
    print("len", report["len_min"], report["len_avg"], report["len_max"])
    return 0 if not stats["ruby_err"] and not stats["missing"] and not stats["empty_sets"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
