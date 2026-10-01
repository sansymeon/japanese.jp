#!/usr/bin/env python3
"""Build Lessons 66–95 Compounds. Do not touch 1–65. Stop after 95."""

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
    66: ("assets/studies/hollow.jpg", "A hollow in Japan"),
    67: ("assets/studies/cavern.jpg", "A cavern in Japan"),
    68: ("assets/studies/cliff.jpg", "A cliff in Japan"),
    69: ("assets/studies/bay.jpg", "A bay in Japan"),
    70: ("assets/studies/cloud.jpg", "Clouds in Japan"),
    71: ("assets/studies/cloudy_weather.jpg", "Cloudy weather in Japan"),
    72: ("assets/studies/grass.jpg", "Grass in Japan"),
    73: ("assets/studies/harvest.jpg", "Harvest in Japan"),
    74: ("assets/studies/rice_plant.jpg", "Rice plants in Japan"),
    75: ("assets/studies/springtime.jpg", "Springtime in Japan"),
    76: ("assets/studies/star.jpg", "Stars over Japan"),
    77: ("assets/studies/night.jpg", "Night in Japan"),
    78: ("assets/studies/crane.jpg", "A crane in Japan"),
    79: ("assets/studies/frozen.jpg", "Frozen landscape in Japan"),
    80: ("assets/studies/steam.jpg", "Steam in Japan"),
    81: ("assets/studies/seasons.jpg", "The seasons in Japan"),
    82: ("assets/studies/seaweed.jpg", "Seaweed on a Japanese shore"),
    83: ("assets/studies/home_country.jpg", "The home country"),
    84: ("assets/studies/visit_shrine.jpg", "A shrine visit in Japan"),
    85: ("assets/studies/monkey.jpg", "A monkey in Japan"),
    86: ("assets/studies/grains.jpg", "Grains in Japan"),
    87: ("assets/studies/go_upstream.jpg", "Going upstream in Japan"),
    88: ("assets/studies/pass_through.jpg", "A pass in Japan"),
    89: ("assets/studies/cornerstone.jpg", "A cornerstone in Japan"),
    90: ("assets/studies/encompassing.jpg", "An encompassing view in Japan"),
    91: ("assets/studies/imperial_seal.jpg", "An imperial seal"),
    92: ("assets/studies/navigate.jpg", "Navigating in Japan"),
    93: ("assets/studies/open.jpg", "An open landscape in Japan"),
    94: ("assets/studies/voice.jpg", "A voice in Japan"),
    95: ("assets/studies/stealth.jpg", "A quiet scene in Japan"),
}

REMOVE = {
    (66, "不", "ふ"),
    (66, "不", "ぶ"),
    (66, "会釈挨拶", "えしゃくあいさつ"),
    (66, "朝の挨拶", "あさのあいさつ"),
    (66, "戚族", "せきぞく"),
    (67, "第~", "だい"),
    (67, "弱", "じゃく"),
    (68, "諸~", "しょ"),
    (68, "匕箸", "ひちょ"),
    (70, "防~", "ぼう"),
    (70, "行踪", "ぎょうしょう"),
    (74, "総~", "そう"),
    (75, "幾~", "いく"),
    (78, "短~", "たん"),
    (89, "干し~", "ほし"),
    (75, "頁脚", "けっきゃく"),
    (77, "脱臼肘", "だっきゅうひじ"),
    (86, "過剰汰", "かじょうた"),
    (89, "賂罪", "ろざい"),
    (91, "危険を冒す", "きけんをおかす"),
}
REMOVE_META = {
    (66, "不", "ふ"): ("NON_LEXICAL", "Combining prefix 不- presented as a standalone word."),
    (66, "不", "ぶ"): ("NON_LEXICAL", "Combining prefix 不- (ぶ) presented as a standalone word."),
    (66, "会釈挨拶", "えしゃくあいさつ"): ("NON_LEXICAL", "Concatenated 会釈+挨拶; same artifact removed in Lesson 36."),
    (66, "朝の挨拶", "あさのあいさつ"): ("NON_LEXICAL", "Phrase stored as vocabulary; 挨拶 remains."),
    (66, "戚族", "せきぞく"): ("NON_LEXICAL", "Chinese-order 戚+族 pad; Japanese uses 親族/姻戚."),
    (67, "第~", "だい"): ("MALFORMED", "Combining-form stub, not a lexical word."),
    (67, "弱", "じゃく"): ("NON_LEXICAL", "Onyomi combining form presented as a standalone word; 弱い remains."),
    (68, "諸~", "しょ"): ("MALFORMED", "Combining-form stub; 諸国/諸君 remain."),
    (68, "匕箸", "ひちょ"): ("NON_LEXICAL", "Chinese 匕+箸 concatenation, not a Japanese lexical unit."),
    (70, "防~", "ぼう"): ("MALFORMED", "Combining-form stub; 予防/防ぐ remain."),
    (70, "行踪", "ぎょうしょう"): ("NON_LEXICAL", "Chinese 行踪; Japanese is 行方."),
    (74, "総~", "そう"): ("MALFORMED", "Combining-form stub."),
    (75, "幾~", "いく"): ("MALFORMED", "Combining-form stub."),
    (78, "短~", "たん"): ("MALFORMED", "Combining-form stub."),
    (89, "干し~", "ほし"): ("MALFORMED", "Combining-form stub."),
    (75, "頁脚", "けっきゃく"): ("NON_LEXICAL", "Invented on'yomi pad for page footer; not a Japanese lexical unit."),
    (77, "脱臼肘", "だっきゅうひじ"): ("NON_LEXICAL", "Concatenated 脱臼+肘; not a single lexical unit."),
    (86, "過剰汰", "かじょうた"): ("NON_LEXICAL", "Invented concatenation 過剰+汰; not a Japanese word."),
    (89, "賂罪", "ろざい"): ("NON_LEXICAL", "Chinese-order pad related to bribery; Japanese uses 収賄/贈賄."),
    (91, "危険を冒す", "きけんをおかす"): ("NON_LEXICAL", "Complete clause stored as vocabulary; 危険 remains."),
}
CORRECT_SURFACE = {
    (67, "陽射"): ("陽射し", "ひざし", "sunlight, rays of the sun"),
    (70, "陽射"): ("陽射し", "ひざし", "sunlight, rays of the sun"),
    (73, "終る"): ("終わる", "おわる", "to finish, to close"),
    (74, "引っ繰り返す"): ("ひっくり返す", "ひっくりかえす", "to turn over, to overturn"),
    (74, "引っ繰り返る"): ("ひっくり返る", "ひっくりかえる", "to be overturned, to topple"),
    (79, "即する"): ("即する", "そくする", "to conform to, to be adapted to"),
    (86, "口吟む"): ("口ずさむ", "くちずさむ", "to hum, to sing under one's breath"),
    (66, "霧中"): ("霧中", "きりちゅう", "in the fog"),
    (91, "錮疾"): ("痼疾", "こしつ", "chronic illness"),
    (94, "楽む"): ("楽しむ", "たのしむ", "to enjoy"),
}
MEANING_FIX = {
    (68, "中学校"): "junior high school",
    (73, "統計"): "statistics",
    (77, "酉"): "the Bird of the Chinese zodiac",
    (81, "離れる"): "to leave, to be separated",
    (82, "亥"): "the Boar of the Chinese zodiac",
    (86, "漢和"): "Sino-Japanese; a Chinese-Japanese dictionary",
}
NAMES = {
    "那智の滝",
    "弥勒",
    "弥生",
    "岐阜",
    "大阪",
    "阿部",
    "京阪",
    "沖縄",
    "滋賀",
    "近畿",
    "畿内",
    "静岡",
    "睦月",
    "鎌倉",
    "韓国",
    "関西",
    "台湾",
}
LITERARY = {
    "窮乏",
    "諾否",
    "矛先",
    "弔問",
    "弔意",
    "不朽",
    "老朽",
    "渚",
    "恣縦",
    "繁昌",
    "幽冥",
    "隠居",
}
SPECIALIZED = {
    "矯正歯科",
    "顎関節",
    "沸点",
    "脊髄",
    "骨髄",
    "脊髄炎",
    "窒素",
    "網膜",
    "紫外線",
    "陣痛",
    "搾乳",
    "窯業",
    "紡績",
}
REVIEW_KEEP = set()  # 之/廿/庸俗/看護婦/剥す are 62–65 only unless they recur


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
    for path in sorted(HERE.glob("_examples_l66_95_*.py")):
        ns: dict = {}
        exec(path.read_text(encoding="utf-8"), ns)
        out.update(ns.get("EXAMPLES") or {})
    return out


def fix_incidental(ja: str, segs: list[dict]) -> None:
    i = 0
    while i < len(segs):
        if segs[i].get("text") == "日差":
            nxt = segs[i + 1] if i + 1 < len(segs) else None
            rest = (nxt or {}).get("text") or ""
            if rest.startswith("し"):
                segs[i] = {"text": "日差し", "reading": "ひざし"}
                leftover = rest[1:]
                if leftover:
                    segs[i + 1] = {k: v for k, v in nxt.items() if k != "text"}
                    segs[i + 1]["text"] = leftover
                    if leftover in "がをにはとでもの":
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-lesson", type=int, default=66)
    ap.add_argument("--to-lesson", type=int, default=95)
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
    # keep uniqueness across the whole 66–95 band when those files exist
    for n_prev in range(66, args.from_lesson):
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
                # drop (する) duplicate if a clean copy of the same identity remains
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
                    stats["missing"].append({"lesson": n, "surface": surface, "reading": reading, "kanji": ch["kanji"]})
                    continue
                batch = examples[key]
                if batch and isinstance(batch[0], str):
                    batch = [batch]
                idx = example_cursor[key]
                if idx >= len(batch):
                    stats["missing"].append(
                        {"lesson": n, "surface": surface, "reading": reading, "kanji": ch["kanji"], "issue": "need-another-sentence"}
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
                fix_incidental(ja, segs)
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
                    qa["reviewNote"] = "Flag reused from earlier lexical decision."
                    review.append({"lesson": n, "surface": surface, "issue": "lexical-review", "ja": ja})
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

    report_path = HERE / "_review_queue_66_95.json"
    prev_report = {}
    if report_path.is_file():
        prev_report = json.loads(report_path.read_text(encoding="utf-8"))
    report = {
        "removed": (prev_report.get("removed") or []) + removed,
        "corrections": (prev_report.get("corrections") or []) + corrections,
        "review": (prev_report.get("review") or []) + review,
        "missing": stats["missing"],
        "dup_ja": stats["dup_ja"],
        "stats": {k: v for k, v in stats.items() if k not in ("lens",)},
        "len_min": min(stats["lens"]) if stats["lens"] else 0,
        "len_avg": round(sum(stats["lens"]) / len(stats["lens"]), 1) if stats["lens"] else 0,
        "len_max": max(stats["lens"]) if stats["lens"] else 0,
        "by_lesson": {**(prev_report.get("by_lesson") or {}), **stats["by_lesson"]},
    }
    # de-dupe removed by lesson+surface+reading
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
        print("MISSING SAMPLE", stats["missing"][:20])
    return 0 if not stats["ruby_err"] and not stats["missing"] and not stats["empty_sets"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
