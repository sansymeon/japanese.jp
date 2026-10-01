#!/usr/bin/env python3
"""Build Lessons 96–100 Compounds. Do not touch 1–95. Stop after 100."""

from __future__ import annotations

import argparse
import json
import unicodedata
from collections import Counter
from pathlib import Path

from _build_lessons_01_10 import HTML, load_keywords, make_id, nav_html, ruby_segments

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMP_HTML = ROOT / "contents/books/book_01/compounds"
SELECTION = HERE / "selection"

IMAGES = {
    96: ("assets/studies/shore.jpg", "A shore in Japan"),
    97: ("assets/studies/wind.jpg", "Wind in Japan"),
    98: ("assets/studies/winding.jpg", "A winding path in Japan"),
    99: ("assets/studies/bamboo_hat.jpg", "A bamboo hat in Japan"),
    100: ("assets/studies/canopy.jpg", "A canopy in Japan"),
}

REMOVE = {
    (97, "共産~", "きょうさん"),
    (97, "隻翼", "せきよく"),
    (98, "再~", "さい"),
    (99, "低~", "てい"),
    (100, "盾にする", "たてに"),
}
REMOVE_META = {
    (97, "共産~", "きょうさん"): ("MALFORMED", "Combining-form stub, not a lexical word."),
    (97, "隻翼", "せきよく"): ("NON_LEXICAL", "Chinese-order pad; Japanese uses 片翼."),
    (98, "再~", "さい"): ("MALFORMED", "Combining-form stub, not a lexical word."),
    (99, "低~", "てい"): ("MALFORMED", "Combining-form stub, not a lexical word."),
    (100, "盾にする", "たてに"): ("NON_LEXICAL", "Collocation stored as vocabulary; 盾 remains."),
}
CORRECT_SURFACE: dict = {}
MEANING_FIX = {
    (96, "遺憾"): "regret",
    (96, "叔父貴"): "uncle (familiar)",
    (96, "遺失物拾得"): "lost-and-found (legal)",
    (97, "短編"): "short story, short work",
    (98, "殿"): "Mr., Ms. (honorific after a name)",
    (99, "短編"): "short story, short work",
    (99, "長編"): "full-length work, novel",
    (99, "辞典"): "dictionary",
    (99, "百科事典"): "encyclopedia",
    (100, "部長"): "department head, section chief",
    (100, "郡"): "district, county",
}
NAMES = {
    "那覇",
    "浦島",
    "桃太郎",
    "那智の滝",
    "呂氏",
    "源氏",
}
LITERARY = {
    "遺憾",
    "恭敬",
    "人倫",
    "浦辺",
    "循序",
    "甚だ",
    "租借",
    "津々浦々",
    "遍歴",
}
SPECIALIZED = {
    "遺失物拾得",
    "顕微鏡",
    "繊維",
    "化繊",
    "洪積世",
    "亜種",
    "亜熱帯",
    "亜鉛",
    "沈殿",
    "抵当",
    "抵触",
    "哺乳",
    "哺乳類",
    "主翼",
    "租税",
    "仮名遣い",
    "詰将棋",
}
REVIEW_KEEP = {
    "循序",
}


def clean_reading(raw: str) -> str:
    text = unicodedata.normalize("NFKC", raw).strip()
    text = text.split("／")[0].split("/")[0].split(";")[0].split("；")[0].strip()
    if "する" in text and "(" in text:
        text = text.split("(")[0].strip()
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
            }
        )
    return chars


def load_examples() -> dict:
    out = {}
    for path in sorted(HERE.glob("_examples_l96_100_*.py")):
        ns: dict = {}
        exec(path.read_text(encoding="utf-8"), ns)
        out.update(ns.get("EXAMPLES") or {})
    return out


def fix_incidental(ja: str, segs: list[dict], surface: str = "", reading: str = "") -> None:
    i = 0
    while i < len(segs):
        t0 = segs[i].get("text") or ""
        nxt = segs[i + 1] if i + 1 < len(segs) else None
        rest = (nxt or {}).get("text") or ""
        if t0 == "日差" and rest.startswith("し"):
            segs[i] = {"text": "日差し", "reading": "ひざし"}
            leftover = rest[1:]
            if leftover:
                segs[i + 1] = {k: v for k, v in nxt.items() if k != "text"}
                segs[i + 1]["text"] = leftover
                if leftover[0:1] in "がをにはとでもの":
                    segs[i + 1].pop("reading", None)
            else:
                del segs[i + 1]
        elif t0 in ("押入", "押し入") and rest.startswith("れ"):
            merged = "押入れ" if t0 == "押入" else "押し入れ"
            segs[i] = {"text": merged, "reading": "おしいれ"}
            leftover = rest[1:]
            if leftover:
                segs[i + 1] = {k: v for k, v in nxt.items() if k != "text"}
                segs[i + 1]["text"] = leftover
                segs[i + 1].pop("reading", None)
            else:
                del segs[i + 1]
        elif t0 == "日照" and rest.startswith("り"):
            segs[i] = {"text": "日照り", "reading": "ひでり"}
            leftover = rest[1:]
            if leftover:
                segs[i + 1] = {k: v for k, v in nxt.items() if k != "text"}
                segs[i + 1]["text"] = leftover
                segs[i + 1].pop("reading", None)
            else:
                del segs[i + 1]
        i += 1
    for i, seg in enumerate(segs):
        if (
            seg.get("text") == "米"
            and seg.get("reading") == "べい"
            and "米国" not in ja
            and "南米" not in ja
            and "米軍" not in ja
            and "米ドル" not in ja
            and "欧米" not in ja
        ):
            seg["reading"] = "こめ"
        if seg.get("text") == "霧中" and seg.get("reading") == "むちゅう":
            seg["reading"] = "きりちゅう"
        if (
            seg.get("text") == "日"
            and "日曜日" in ja
            and i
            and segs[i - 1].get("text") == "日曜"
        ):
            seg["reading"] = "び"
        if "無に帰" in ja and seg.get("text") == "帰" and seg.get("reading") == "かえ":
            seg["reading"] = "き"
        if "那覇" in ja and seg.get("text") == "市場" and seg.get("reading") == "しじょう":
            seg["reading"] = "いちば"
        if (
            seg.get("text") == "風"
            and seg.get("reading") == "ふう"
            and ("風に" in ja or "風で" in ja or "風が" in ja)
            and "風景" not in ja
            and "風力" not in ja
            and "台風" not in ja
        ):
            seg["reading"] = "かぜ"
        if surface == "堪える" and seg.get("text") == "堪":
            seg["reading"] = "た" if reading == "たえる" else "こら"
        if seg.get("text") == "実" and seg.get("reading") == "じつ" and "実が" in ja:
            seg["reading"] = "み"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-lesson", type=int, default=96)
    ap.add_argument("--to-lesson", type=int, default=100)
    args = ap.parse_args()
    examples = load_examples()
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
        "missing": [],
        "dup_ja": [],
        "by_lesson": {},
        "lens": [],
    }
    used_ja: set[str] = set()
    example_cursor: Counter = Counter()
    for n_prev in range(1, args.from_lesson):
        p = HERE / f"lesson_{n_prev:02d}.json"
        if not p.is_file():
            continue
        prev = json.loads(p.read_text(encoding="utf-8"))
        for ch in prev.get("characters") or []:
            for c in ch.get("compounds") or []:
                ja = (c.get("example") or {}).get("ja")
                if ja:
                    used_ja.add(ja)

    for n in range(args.from_lesson, args.to_lesson + 1):
        chars = parse_selection(n)
        out_chars = []
        ids = Counter()
        word_n = 0
        seen_id = set()
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
                ident = (n, surface, reading)
                if ident in seen_id:
                    removed.append(
                        {
                            "lesson": n,
                            "kanji": ch["kanji"],
                            "original": surface,
                            "reading": raw_reading,
                            "meaning": meaning,
                            "classification": "VALID_BUT_METADATA_PROBLEM",
                            "decision": "Removed duplicate identity already retained in this lesson.",
                            "cause": "Same written form + reading already retained in this lesson.",
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
                            "decision": f"Corrected {surface} → {new_s}.",
                        }
                    )
                    surface, reading, meaning = new_s, new_r, new_m
                    stats["corrected"] += 1
                if (n, surface) in MEANING_FIX:
                    meaning = MEANING_FIX[(n, surface)]
                    stats["corrected"] += 1
                if "(する)" in raw_reading:
                    corrections.append(
                        {
                            "lesson": n,
                            "kanji": ch["kanji"],
                            "original": surface,
                            "reading": raw_reading,
                            "newReading": reading,
                            "classification": "VALID_BUT_METADATA_PROBLEM",
                            "decision": "Stripped (する) from the reading; identity is the noun.",
                        }
                    )
                    stats["corrected"] += 1
                key = (n, surface, reading)
                if key not in examples:
                    stats["missing"].append(
                        {"lesson": n, "surface": surface, "reading": reading, "kanji": ch["kanji"]}
                    )
                    continue
                batch = examples[key]
                if batch and isinstance(batch[0], str):
                    batch = [batch]
                idx = example_cursor[key]
                if idx >= len(batch):
                    stats["missing"].append(
                        {
                            "lesson": n,
                            "surface": surface,
                            "reading": reading,
                            "kanji": ch["kanji"],
                            "issue": "need-another-sentence",
                        }
                    )
                    continue
                row = batch[idx]
                example_cursor[key] += 1
                ja, en, *rest = row
                exc = rest[0] if rest else None
                if ja in used_ja:
                    stats["dup_ja"].append({"lesson": n, "surface": surface, "ja": ja})
                used_ja.add(ja)
                segs = ruby_segments(ja, surface, reading)
                fix_incidental(ja, segs, surface, reading)
                if "".join(s["text"] for s in segs) != ja:
                    stats["ruby_err"] += 1
                    segs = [{"text": ja}]
                    review.append({"lesson": n, "surface": surface, "issue": "ruby-join", "ja": ja})
                rec = {
                    "id": make_id(n, surface, reading, ids),
                    "surface": surface,
                    "reading": reading,
                    "meaning": meaning,
                    "sourceGloss": c["meaning"],
                    "example": {"ja": ja, "en": en, "segments": segs},
                }
                qa = {}
                if surface in NAMES:
                    rec["kind"] = "name"
                    stats["names"] += 1
                if surface in LITERARY:
                    qa["migrationNote"] = "Literary vocabulary retained."
                if surface in SPECIALIZED:
                    qa.setdefault("migrationNote", "Specialized vocabulary retained.")
                if exc:
                    qa["grammarException"] = True
                    qa["reason"] = exc
                    stats["exceptions"] += 1
                if surface in REVIEW_KEEP:
                    qa["review"] = True
                    qa["reviewNote"] = "Rare Sino-Japanese; Japanese more often uses 順序."
                    review.append(
                        {
                            "lesson": n,
                            "surface": surface,
                            "reading": reading,
                            "reason": "Rare; possible confusion with 順序. Retained as literary 循序.",
                        }
                    )
                if qa:
                    rec["qa"] = qa
                comps.append(rec)
                seen_id.add(ident)
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
                "band": "late-middle",
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

    report_path = HERE / "_review_queue_96_100.json"
    prev_report = {}
    if report_path.is_file() and args.from_lesson > 96:
        prev_report = json.loads(report_path.read_text(encoding="utf-8"))
    report = {
        "removed": (prev_report.get("removed") or []) + removed,
        "corrections": (prev_report.get("corrections") or []) + corrections,
        "review": (prev_report.get("review") or []) + review,
        "missing": stats["missing"],
        "dup_ja": stats["dup_ja"],
        "stats": {k: v for k, v in stats.items() if k not in ("lens",)},
        "len_min": min(stats["lens"]) if stats["lens"] else prev_report.get("len_min", 0),
        "len_avg": round(sum(stats["lens"]) / len(stats["lens"]), 1) if stats["lens"] else 0,
        "len_max": max(stats["lens"]) if stats["lens"] else 0,
        "by_lesson": {**(prev_report.get("by_lesson") or {}), **{str(k): v for k, v in stats["by_lesson"].items()}},
    }
    seen = set()
    uniq = []
    for row in report["removed"]:
        k = (row.get("lesson"), row.get("original"), row.get("reading"))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(row)
    report["removed"] = uniq
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "inspected",
        stats["inspected"],
        "retained",
        stats["retained"],
        "removed",
        stats["removed"],
        "missing",
        len(stats["missing"]),
        "dup_ja",
        len(stats["dup_ja"]),
        "ruby_err",
        stats["ruby_err"],
        "empty",
        stats["empty_sets"],
    )
    if stats["missing"]:
        print("MISSING SAMPLE", stats["missing"][:30])
    return 0 if not stats["ruby_err"] and not stats["missing"] and not stats["empty_sets"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
