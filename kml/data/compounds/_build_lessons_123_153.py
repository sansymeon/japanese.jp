#!/usr/bin/env python3
"""Build Lessons 123–153 Compounds. Do not touch 1–122. Stop after 153."""

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
    123: ("assets/studies/dew.jpg", "Dew in Japan"),
    124: ("assets/studies/evening.jpg", "Evening in Japan"),
    125: ("assets/studies/farm.jpg", "A farm in Japan"),
    126: ("assets/studies/field.jpg", "A field in Japan"),
    127: ("assets/studies/lake.jpg", "A lake in Japan"),
    128: ("assets/studies/woods.jpg", "Woods in Japan"),
    129: ("assets/studies/quiet.jpg", "A quiet scene in Japan"),
    130: ("assets/studies/still.jpg", "A still scene in Japan"),
    131: ("assets/studies/shadow.jpg", "Shadow in Japan"),
    132: ("assets/studies/pear_tree.jpg", "A pear tree in Japan"),
    133: ("assets/studies/catalpa_tree.jpg", "A catalpa tree in Japan"),
    134: ("assets/studies/chestnut.jpg", "A chestnut tree in Japan"),
    135: ("assets/studies/climate.jpg", "Climate in Japan"),
    136: ("assets/studies/delight.jpg", "A delightful scene in Japan"),
    137: ("assets/studies/rejoice.jpg", "A scene of rejoicing in Japan"),
    138: ("assets/studies/soft.jpg", "A soft scene in Japan"),
    139: ("assets/studies/moon.jpg", "The moon over Japan"),
    140: ("assets/studies/temple.jpg", "A temple in Japan"),
    141: ("assets/studies/lightning_bug.jpg", "Fireflies in Japan"),
    142: ("assets/studies/hot_water.jpg", "Hot water in Japan"),
    143: ("assets/studies/tree_trunk.jpg", "A tree trunk in Japan"),
    144: ("assets/studies/dawn.jpg", "Dawn in Japan"),
    145: ("assets/studies/gokayama_winter.jpg", "Gokayama in winter"),
    146: ("assets/studies/tea_fields.jpg", "Tea fields in Japan"),
    147: ("assets/studies/thatched_roof.jpg", "A thatched roof in Japan"),
    148: ("assets/studies/ume.jpg", "Ume blossoms in Japan"),
    149: ("assets/studies/raizan.jpg", "Mount Raizan"),
    150: ("assets/studies/takayama.jpg", "Takayama"),
    151: ("assets/studies/tsumago.jpg", "Tsumago"),
    152: ("assets/studies/senso_ji_temple.jpg", "Sensō-ji"),
    153: ("assets/studies/saga_koinobori.jpg", "Koinobori in Saga"),
}

REMOVE: set[tuple[int, str, str]] = set()
REMOVE_META: dict[tuple[int, str, str], tuple[str, str]] = {}
CORRECT_SURFACE: dict = {}
MEANING_FIX: dict = {}
NAMES: set[str] = set()
LITERARY: set[str] = set()
SPECIALIZED: set[str] = set()
REVIEW_KEEP: set[str] = set()


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
    for path in sorted(HERE.glob("_examples_l123_153_*.py")):
        ns: dict = {}
        exec(path.read_text(encoding="utf-8"), ns)
        out.update(ns.get("EXAMPLES") or {})
    return out


def load_flags() -> None:
    path = HERE / "_flags_l123_153.py"
    if not path.is_file():
        return
    ns: dict = {}
    exec(path.read_text(encoding="utf-8"), ns)
    REMOVE.update(ns.get("REMOVE") or set())
    REMOVE_META.update(ns.get("REMOVE_META") or {})
    CORRECT_SURFACE.update(ns.get("CORRECT_SURFACE") or {})
    MEANING_FIX.update(ns.get("MEANING_FIX") or {})
    NAMES.update(ns.get("NAMES") or set())
    LITERARY.update(ns.get("LITERARY") or set())
    SPECIALIZED.update(ns.get("SPECIALIZED") or set())
    REVIEW_KEEP.update(ns.get("REVIEW_KEEP") or set())


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
        elif t0 == "夜更" and rest.startswith("け"):
            segs[i] = {"text": "夜更け", "reading": "よふけ"}
            leftover = rest[1:]
            if leftover:
                segs[i + 1] = {k: v for k, v in nxt.items() if k != "text"}
                segs[i + 1]["text"] = leftover
                if leftover[0:1] in "がをにはとでもの":
                    segs[i + 1].pop("reading", None)
            else:
                del segs[i + 1]
        elif t0 == "凍" and rest.startswith("て"):
            segs[i] = {"text": "凍て", "reading": "いて"}
            leftover = rest[1:]
            if leftover:
                segs[i + 1] = {k: v for k, v in nxt.items() if k != "text"}
                segs[i + 1]["text"] = leftover
            else:
                del segs[i + 1]
        elif t0 == "真っ直" and rest.startswith("ぐ"):
            segs[i] = {"text": "真っ直ぐ", "reading": "まっすぐ"}
            leftover = rest[1:]
            if leftover:
                segs[i + 1] = {k: v for k, v in nxt.items() if k != "text"}
                segs[i + 1]["text"] = leftover
                segs[i + 1].pop("reading", None)
            else:
                del segs[i + 1]
        elif t0 == "朝焼" and rest.startswith("け"):
            segs[i] = {"text": "朝焼け", "reading": "あさやけ"}
            leftover = rest[1:]
            if leftover:
                segs[i + 1] = {k: v for k, v in nxt.items() if k != "text"}
                segs[i + 1]["text"] = leftover
                segs[i + 1].pop("reading", None)
            else:
                del segs[i + 1]
        elif t0 == "茶請" and rest.startswith("け"):
            segs[i] = {"text": "茶請け", "reading": "ちゃうけ"}
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
        if seg.get("text") == "刃" and seg.get("reading") == "じん" and "刃を" in ja:
            seg["reading"] = "は"
        if (
            seg.get("text") == "仏"
            and seg.get("reading") == "ふつ"
            and "仏像" not in ja
            and "仏教" not in ja
            and "仏壇" not in ja
        ):
            seg["reading"] = "ほとけ"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-lesson", type=int, default=123)
    ap.add_argument("--to-lesson", type=int, default=153)
    args = ap.parse_args()
    if args.from_lesson < 123 or args.to_lesson > 153:
        raise SystemExit("This builder only writes lessons 123–153.")
    load_flags()
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
        for ch in chars:
            comps = []
            seen_id = set()
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
                    qa["reviewNote"] = "Retained pending human lexical judgment."
                    review.append(
                        {
                            "lesson": n,
                            "surface": surface,
                            "reading": reading,
                            "reason": "REVIEW_KEEP",
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
                "band": "later",
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

    report_path = HERE / "_review_queue_123_153.json"
    prev_report = {}
    if report_path.is_file() and args.from_lesson > 123:
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
    return 0 if not stats["ruby_err"] and not stats["missing"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
