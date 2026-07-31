#!/usr/bin/env python3
"""KML Curriculum Analytics.

Reads the published KML Vocabulary lesson files (and, read-only, the KML
Master Vocabulary database) and generates curriculum statistics:

    output/kml_curriculum_analysis.json   - full analysis (the superset)
    output/kml_jlpt_statistics.json       - JLPT coverage + cumulative
    output/kml_frequency_statistics.json  - spoken-frequency coverage
    output/kml_channel_statistics.json    - publication/channel summary
    output/CURRICULUM_REPORT.md           - human-readable report

Design rules
------------
* Every input is READ ONLY. This script never writes outside
  kml/analytics/output/.
* Everything is regenerated from scratch on every run. Adding lesson 13
  requires nothing but rerunning this script (lessons are discovered via
  a glob defined in analytics_config.json).

Run:
    .venv/bin/python kml/analytics/scripts/analyze_curriculum.py
"""

from __future__ import annotations

import csv
import glob
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import fugashi

# --------------------------------------------------------------------------
# Paths / config
# --------------------------------------------------------------------------

ANALYTICS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = ANALYTICS_DIR.parent.parent  # kml/analytics -> repo root

CONFIG = json.loads((ANALYTICS_DIR / "analytics_config.json").read_text(encoding="utf-8"))

OUTPUT_DIR = REPO_ROOT / CONFIG["output_dir"]
FREQ_BANDS = CONFIG["frequency_bands"]
REVIEW_GAP = CONFIG["reinforcement"]["review_gap_lessons"]

KANJI_RE = re.compile(r"[一-龯々〆〤]")
KATAKANA_RE = re.compile(r"^[ァ-ヶーヽヾ・]+$")
KANA_ONLY_RE = re.compile(r"^[ぁ-んァ-ヶーヽヾゝゞ・]+$")

TAGGER = fugashi.Tagger()

# --------------------------------------------------------------------------
# Theme classification (keyword match against English glosses)
# --------------------------------------------------------------------------

THEME_KEYWORDS = {
    "shopping": ["shop", "store", "price", "buy", "purchase", "money", "pay", "cash",
                 "receipt", "discount", "bargain", "market", "customer", "wallet"],
    "food": ["food", "eat", "meal", "cook", "drink", "tea", "rice", "bread", "fish ",
             "meat", "vegetable", "fruit", "delicious", "taste", "restaurant", "lunch",
             "dinner", "breakfast", "hungry", "sweet", "cuisine", "dish"],
    "travel": ["travel", "trip", "journey", "hotel", "sightseeing", "tourist",
               "passport", "luggage", "abroad", "vacation", "destination"],
    "transportation": ["train", "bus", "car", "station", "airport", "airplane", "plane",
                       "bicycle", "subway", "taxi", "ride", "ticket", "traffic", "road",
                       "railway", "boat", "ship"],
    "school": ["school", "study", "student", "teacher", "class", "lesson", "homework",
               "exam", "test", "university", "college", "learn", "education", "textbook",
               "grade", "kindergarten"],
    "family": ["family", "mother", "father", "parent", "child", "brother", "sister",
               "grandmother", "grandfather", "son", "daughter", "wife", "husband",
               "relative", "baby"],
    "home": ["house", "home", "room", "kitchen", "door", "window", "bath", "toilet",
             "garden", "roof", "wall", "floor", "furniture", "bed", "apartment"],
    "work": ["work", "job", "company", "office", "business", "meeting", "boss",
             "employee", "salary", "career", "colleague", "occupation"],
    "nature": ["nature", "mountain", "river", "sea", "ocean", "forest", "tree", "flower",
               "sky", "wind", "rain", "snow", "sun", "moon", "star", "weather", "season",
               "spring", "summer", "autumn", "winter", "cloud", "bird", "animal",
               "leaves", "leaf", "cherry blossom", "sunlight", "sunset", "sunrise",
               "haze", "twilight", "petal", "breeze", "insect", "cicada"],
    "daily_life": ["today", "tomorrow", "yesterday", "time", "morning", "afternoon",
                   "evening", "night", "daily", "life", "everyday", "week", "month",
                   "year", "hour", "minute", "clock", "wake", "sleep", "walk", "clean",
                   "laundry", "habit", "schedule"],
    "greetings": ["hello", "good morning", "good evening", "goodbye", "thank",
                  "excuse me", "please", "welcome", "greeting", "congratulat",
                  "nice to meet"],
}


def classify_themes(en_gloss: str, master_themes: list[str]) -> list[str]:
    """Themes from the master DB win; otherwise keyword-match the English gloss."""
    if master_themes:
        return sorted(set(master_themes))
    text = en_gloss.lower()
    hits = [theme for theme, keys in THEME_KEYWORDS.items()
            if any(k in text for k in keys)]
    return hits or ["general"]


# --------------------------------------------------------------------------
# Part-of-speech classification
# --------------------------------------------------------------------------

POS1_MAP = {
    "動詞": "verb",
    "形容詞": "i_adjective",
    "形状詞": "na_adjective",
    "副詞": "adverb",
    "代名詞": "pronoun",
    "接続詞": "conjunction",
    "助詞": "particle",
    "感動詞": "expression",
    "連体詞": "other",
    "接頭辞": "other",
    "接尾辞": "other",
    "助動詞": "other",
}

MASTER_POS_MAP = {
    "noun": "noun", "verb": "verb", "i_adjective": "i_adjective",
    "na_adjective": "na_adjective", "adverb": "adverb", "particle": "particle",
    "conjunction": "conjunction", "interjection": "expression",
    "pronoun": "pronoun", "counter": "counter", "phrase": "expression",
    "clause": "expression", "pattern": "expression", "auxiliary": "other",
    "prefix": "other", "suffix": "other", "other": "other", "unknown": "other",
}


def classify_pos(jp: str, master_pos: list[str]) -> str:
    if master_pos:
        return MASTER_POS_MAP.get(master_pos[0], "other")
    tokens = list(TAGGER(jp))
    if not tokens:
        return "other"
    if len(tokens) == 1:
        tok = tokens[0].feature
        if tok.pos1 == "名詞":
            return "counter" if tok.pos2 == "助数詞" else "noun"
        return POS1_MAP.get(tok.pos1, "other")
    pos1s = [t.feature.pos1 for t in tokens]
    if all(p in ("名詞", "接頭辞", "接尾辞") for p in pos1s):
        return "noun"
    if pos1s[-1] in ("動詞", "助動詞") and "動詞" in pos1s:
        return "verb"
    if pos1s[-1] == "形容詞":
        return "i_adjective"
    if pos1s[-1] == "接尾辞" and all(p in ("名詞", "接頭辞", "接尾辞", "動詞") for p in pos1s):
        return "noun"
    return "expression"


# --------------------------------------------------------------------------
# Word records
# --------------------------------------------------------------------------

@dataclass
class Word:
    jp: str
    reading: str
    en: str
    lessons: list[int] = field(default_factory=list)
    roles: set = field(default_factory=set)  # "compound" | "beautiful_word"
    # enriched
    pos: str = "other"
    themes: list[str] = field(default_factory=list)
    jlpt: str | None = None
    freq_rank: int | None = None
    kanji: list[str] = field(default_factory=list)
    kana_only: bool = False
    katakana: bool = False
    goshu: str | None = None  # 和 / 漢 / 外 / 固 / 混
    lemma: str | None = None
    in_master_db: bool = False


def dominant_goshu(jp: str) -> str | None:
    counts = Counter(
        t.feature.goshu for t in TAGGER(jp)
        if t.feature.goshu and t.feature.goshu != "*"
    )
    if not counts:
        return None
    if "外" in counts:
        return "外"
    return counts.most_common(1)[0][0]


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def sha256_short(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def load_lessons() -> tuple[list[dict], list[Path]]:
    pattern = str(REPO_ROOT / CONFIG["sources"]["lesson_glob"])
    paths = sorted(Path(p) for p in glob.glob(pattern))
    lessons = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        meta = data.get("meta", {})
        number = meta.get("lesson")
        if number is None:
            m = re.search(r"(\d+)", path.stem)
            number = int(m.group(1)) if m else 0
        entry = {
            "number": int(number),
            "id": data.get("id", path.stem),
            "title": data.get("title", path.stem),
            "file": str(path.relative_to(REPO_ROOT)),
            "meta": meta,
            "words": [],           # (jp, reading, en, role)
            "beautiful_words": [],
        }
        for scene in data.get("scenes", []):
            for step in scene.get("compounds", {}).get("steps", []):
                entry["words"].append((step["jp"], step.get("reading", ""),
                                       step.get("en", ""), "compound"))
            bw = scene.get("beautifulWord")
            if bw and bw.get("jp"):
                entry["words"].append((bw["jp"], bw.get("reading", ""),
                                       bw.get("en", ""), "beautiful_word"))
                entry["beautiful_words"].append(
                    {"jp": bw["jp"], "reading": bw.get("reading", ""),
                     "en": bw.get("en", "")})
        lessons.append(entry)
    lessons.sort(key=lambda x: x["number"])
    return lessons, paths


def load_master_vocabulary() -> dict[str, dict]:
    """Read-only lookup: jp -> {pos, themes, jlpt}. Never modified, never written.

    Missing file → empty index (JLPT CSVs / UniDic heuristics still apply).
    """
    path = REPO_ROOT / CONFIG["sources"]["master_vocabulary"]
    if not path.is_file():
        print(f"  note: master vocabulary not found ({path}); continuing without it")
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    index = {}
    for e in data.get("entries", []):
        index[e["jp"]] = {
            "pos": e.get("pos") or [],
            "themes": e.get("themes") or [],
            "jlpt": e.get("jlpt"),
        }
    return index


def load_jlpt() -> dict[str, str]:
    """word/reading -> easiest JLPT level (N5 checked first)."""
    table: dict[str, str] = {}
    reading_table: dict[str, str] = {}
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        path = REPO_ROOT / CONFIG["reference"]["jlpt_wordlists"][level]
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                expr = (row.get("expression") or "").strip()
                reading = (row.get("reading") or "").strip()
                if expr:
                    table.setdefault(expr, level)
                if reading:
                    reading_table.setdefault(reading, level)
    table["__readings__"] = reading_table  # type: ignore[assignment]
    return table


def jlpt_level(jp: str, reading: str, table: dict) -> str | None:
    if jp in table:
        return table[jp]
    # kana-only words are safe to match by reading (no homophone ambiguity in surface)
    if KANA_ONLY_RE.match(jp):
        norm = unicodedata.normalize("NFKC", jp)
        hira = "".join(chr(ord(c) - 96) if "ァ" <= c <= "ヶ" else c for c in norm)
        return table["__readings__"].get(hira)
    return None


def load_frequency() -> dict[str, int]:
    ranks: dict[str, int] = {}
    path = REPO_ROOT / CONFIG["reference"]["spoken_frequency"]
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            rank, lemma, _count = line.rstrip("\n").split("\t")
            ranks.setdefault(lemma, int(rank))
    return ranks


def freq_rank(jp: str, ranks: dict[str, int]) -> tuple[int | None, str | None]:
    if jp in ranks:
        return ranks[jp], jp
    tokens = list(TAGGER(jp))
    if len(tokens) == 1:
        lemma = tokens[0].feature.orthBase
        if lemma and lemma in ranks:
            return ranks[lemma], lemma
    return None, None


def load_joyo() -> set[str]:
    path = REPO_ROOT / CONFIG["reference"]["joyo_kanji"]
    with path.open(encoding="utf-8") as f:
        return {row["kanji"].strip() for row in csv.DictReader(f) if row.get("kanji")}


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------

def pct(part: float, whole: float) -> float:
    return round(100.0 * part / whole, 1) if whole else 0.0


def build_words(lessons, master, jlpt_table, freq_ranks) -> dict[str, Word]:
    words: dict[str, Word] = {}
    for lesson in lessons:
        for jp, reading, en, role in lesson["words"]:
            w = words.get(jp)
            if w is None:
                w = words[jp] = Word(jp=jp, reading=reading, en=en)
            if lesson["number"] not in w.lessons:
                w.lessons.append(lesson["number"])
            w.roles.add(role)

    for w in words.values():
        m = master.get(w.jp, {})
        w.in_master_db = w.jp in master
        w.pos = classify_pos(w.jp, m.get("pos", []))
        w.themes = classify_themes(w.en, m.get("themes", []))
        w.jlpt = m.get("jlpt") or jlpt_level(w.jp, w.reading, jlpt_table)
        w.freq_rank, w.lemma = freq_rank(w.jp, freq_ranks)
        w.kanji = sorted(set(KANJI_RE.findall(w.jp)))
        w.kana_only = bool(KANA_ONLY_RE.match(w.jp))
        w.katakana = bool(KATAKANA_RE.match(w.jp))
        w.goshu = dominant_goshu(w.jp)
    return words


def jlpt_distribution(word_list) -> dict:
    total = len(word_list)
    counts = Counter(w.jlpt or "outside_jlpt" for w in word_list)
    dist = {}
    for level in ["N5", "N4", "N3", "N2", "N1", "outside_jlpt"]:
        c = counts.get(level, 0)
        dist[level] = {"count": c, "percent": pct(c, total)}
    return dist


def frequency_bands(word_list, freq_ranks) -> dict:
    total = len(word_list)
    bands = {}
    for band in FREQ_BANDS:
        covered = sorted({w.lemma or w.jp for w in word_list
                          if w.freq_rank and w.freq_rank <= band})
        bands[f"top_{band}"] = {
            "curriculum_words_in_band": len(covered),
            "percent_of_curriculum": pct(len(covered), total),
            "percent_of_band_covered": pct(len(covered), band),
        }
    ranked = [w.freq_rank for w in word_list if w.freq_rank]
    bands["words_with_frequency_data"] = len(ranked)
    bands["median_rank"] = sorted(ranked)[len(ranked) // 2] if ranked else None
    return bands


def theme_distribution(word_list) -> dict:
    total = len(word_list)
    counts: Counter = Counter()
    for w in word_list:
        for t in w.themes:
            counts[t] += 1
    return {t: {"count": c, "percent": pct(c, total)}
            for t, c in counts.most_common()}


def kanji_stats(word_list, lessons, words, joyo) -> dict:
    all_kanji = sorted({k for w in word_list for k in w.kanji})
    joyo_hits = [k for k in all_kanji if k in joyo]
    per_lesson = []
    for lesson in lessons:
        ks = {k for jp, *_ in lesson["words"] for k in words[jp].kanji}
        per_lesson.append(len(ks))
    kana_only = [w.jp for w in word_list if w.kana_only]
    return {
        "unique_kanji": len(all_kanji),
        "joyo_kanji": len(joyo_hits),
        "non_joyo_kanji": len(all_kanji) - len(joyo_hits),
        "non_joyo_list": [k for k in all_kanji if k not in joyo],
        "kana_only_words": len(kana_only),
        "kana_only_percent": pct(len(kana_only), len(word_list)),
        "average_unique_kanji_per_lesson": round(sum(per_lesson) / len(per_lesson), 1) if per_lesson else 0,
        "kanji_inventory": all_kanji,
    }


def analyze(lessons, words: dict[str, Word], freq_ranks, joyo) -> dict:
    word_list = list(words.values())
    total_occurrences = sum(len(l["words"]) for l in lessons)
    lesson_numbers = [l["number"] for l in lessons]

    # ---- 1. overall -------------------------------------------------------
    repeated = [w for w in word_list if len(w.lessons) > 1]
    growth = []
    seen: set[str] = set()
    for lesson in lessons:
        new = {jp for jp, *_ in lesson["words"]} - seen
        seen |= new
        growth.append({
            "lesson": lesson["number"],
            "words_presented": len(lesson["words"]),
            "new_unique_words": len(new),
            "cumulative_unique_words": len(seen),
        })
    overall = {
        "lessons_analyzed": len(lessons),
        "lesson_numbers": lesson_numbers,
        "total_vocabulary_occurrences": total_occurrences,
        "unique_vocabulary": len(word_list),
        "repeated_vocabulary": len(repeated),
        "average_words_per_lesson": round(total_occurrences / len(lessons), 1) if lessons else 0,
        "vocabulary_growth_by_lesson": growth,
    }

    # ---- 4. parts of speech ----------------------------------------------
    pos_counts = Counter(w.pos for w in word_list)
    pos_order = ["noun", "verb", "i_adjective", "na_adjective", "expression",
                 "adverb", "counter", "pronoun", "conjunction", "particle", "other"]
    pos_stats = {p: {"count": pos_counts.get(p, 0),
                     "percent": pct(pos_counts.get(p, 0), len(word_list))}
                 for p in pos_order}

    # ---- 7. loanwords ------------------------------------------------------
    katakana_words = sorted(w.jp for w in word_list if w.katakana)
    gairaigo = sorted(w.jp for w in word_list if w.goshu == "外")
    goshu_counts = Counter(w.goshu or "unknown" for w in word_list)
    goshu_labels = {"和": "wago_native", "漢": "kango_sino_japanese",
                    "外": "gairaigo_loanword", "固": "proper_name",
                    "混": "mixed", "unknown": "unknown"}
    loanwords = {
        "katakana_words": len(katakana_words),
        "katakana_word_list": katakana_words,
        "loanword_count": len(gairaigo),
        "loanword_percent": pct(len(gairaigo), len(word_list)),
        "loanword_list": gairaigo,
        "origin_breakdown": {goshu_labels.get(g, g): {"count": c,
                                                      "percent": pct(c, len(word_list))}
                             for g, c in goshu_counts.most_common()},
        "source_languages_note": "Per-word source languages are not recorded in the "
                                 "current data sources; UniDic goshu origin classes "
                                 "are reported instead.",
    }

    # ---- 8. reading difficulty --------------------------------------------
    reading_lengths = [len(w.reading) for w in word_list if w.reading]
    kanji_counts = [len(KANJI_RE.findall(w.jp)) for w in word_list]
    reading_difficulty = {
        "average_reading_length_kana": round(sum(reading_lengths) / len(reading_lengths), 2) if reading_lengths else 0,
        "average_kanji_per_word": round(sum(kanji_counts) / len(kanji_counts), 2) if kanji_counts else 0,
        "kana_only_percent": pct(sum(1 for w in word_list if w.kana_only), len(word_list)),
        "per_lesson": [
            {
                "lesson": lesson["number"],
                "average_reading_length_kana": round(
                    sum(len(r) for _, r, *_ in lesson["words"]) / len(lesson["words"]), 2),
                "average_kanji_per_word": round(
                    sum(len(KANJI_RE.findall(jp)) for jp, *_ in lesson["words"]) / len(lesson["words"]), 2),
            }
            for lesson in lessons if lesson["words"]
        ],
    }

    # ---- 9. reinforcement ---------------------------------------------------
    latest = max(lesson_numbers) if lesson_numbers else 0
    introduced_once = [w for w in word_list if len(w.lessons) == 1]
    reviewed = [w for w in word_list if len(w.lessons) > 1]
    sr_opportunities = sorted(
        (w for w in introduced_once if w.lessons[0] <= latest - REVIEW_GAP),
        key=lambda w: w.lessons[0])
    reinforcement = {
        "words_introduced_once": len(introduced_once),
        "words_reviewed": len(reviewed),
        "words_in_multiple_lessons": [
            {"jp": w.jp, "reading": w.reading, "lessons": w.lessons}
            for w in sorted(reviewed, key=lambda w: (-len(w.lessons), w.lessons[0]))
        ],
        "review_rate_percent": pct(len(reviewed), len(word_list)),
        "spaced_repetition_opportunities": {
            "definition": f"Words introduced at least {REVIEW_GAP} lessons ago "
                          f"that have never reappeared.",
            "count": len(sr_opportunities),
            "words": [{"jp": w.jp, "reading": w.reading, "en": w.en,
                       "introduced_in_lesson": w.lessons[0]}
                      for w in sr_opportunities],
        },
    }

    # ---- 10. cumulative progress -------------------------------------------
    progress = []
    cum_words: list[Word] = []
    seen_jp: set[str] = set()
    for lesson in lessons:
        for jp, *_ in lesson["words"]:
            if jp not in seen_jp:
                seen_jp.add(jp)
                cum_words.append(words[jp])
        cum_kanji = {k for w in cum_words for k in w.kanji}
        progress.append({
            "after_lesson": lesson["number"],
            "unique_words": len(cum_words),
            "jlpt_coverage": jlpt_distribution(cum_words),
            "frequency_coverage": {
                f"top_{band}": {
                    "count": len({w.lemma or w.jp for w in cum_words
                                  if w.freq_rank and w.freq_rank <= band}),
                    "percent_of_band": pct(
                        len({w.lemma or w.jp for w in cum_words
                             if w.freq_rank and w.freq_rank <= band}), band),
                } for band in FREQ_BANDS
            },
            "unique_kanji": len(cum_kanji),
            "theme_balance": {t: v["percent"]
                              for t, v in theme_distribution(cum_words).items()},
        })

    return {
        "overall": overall,
        "jlpt": {
            "distribution": jlpt_distribution(word_list),
            "cumulative_by_lesson": [
                {"after_lesson": p["after_lesson"], **p["jlpt_coverage"]}
                for p in progress
            ],
        },
        "frequency": frequency_bands(word_list, freq_ranks),
        "parts_of_speech": pos_stats,
        "themes": theme_distribution(word_list),
        "kanji": kanji_stats(word_list, lessons, words, joyo),
        "loanwords": loanwords,
        "reading_difficulty": reading_difficulty,
        "reinforcement": reinforcement,
        "progress": progress,
    }


# --------------------------------------------------------------------------
# Output writers
# --------------------------------------------------------------------------

def provenance(lesson_paths: list[Path]) -> dict:
    master_path = REPO_ROOT / CONFIG["sources"]["master_vocabulary"]
    master_meta = {
        "file": str(master_path.relative_to(REPO_ROOT)),
        "access": "read_only",
    }
    if master_path.is_file():
        master_meta["sha256_12"] = sha256_short(master_path)
    else:
        master_meta["sha256_12"] = None
        master_meta["present"] = False
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "kml/analytics/scripts/analyze_curriculum.py",
        "note": "Generated analytics file. Never edit by hand; never treat as a "
                "canonical vocabulary source. Regenerate by rerunning the script.",
        "inputs": {
            "lessons": [{"file": str(p.relative_to(REPO_ROOT)),
                         "sha256_12": sha256_short(p)} for p in lesson_paths],
            "master_vocabulary": master_meta,
        },
    }


def bar(percent: float, width: int = 30) -> str:
    filled = round(percent / 100 * width)
    return "█" * filled + "░" * (width - filled)


def write_report(results: dict, lessons, path: Path) -> None:
    o = results["overall"]
    lines: list[str] = []
    a = lines.append

    a("# KML Vocabulary Curriculum Report")
    a("")
    a(f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} "
      f"by the KML Curriculum Analytics project. This file is regenerated "
      f"automatically — do not edit by hand._")
    a("")
    a("## 1. Overall Curriculum")
    a("")
    a("| Metric | Value |")
    a("|---|---|")
    a(f"| Lessons analyzed | {o['lessons_analyzed']} |")
    a(f"| Total vocabulary occurrences | {o['total_vocabulary_occurrences']} |")
    a(f"| Unique vocabulary | {o['unique_vocabulary']} |")
    a(f"| Repeated vocabulary | {o['repeated_vocabulary']} |")
    a(f"| Average words per lesson | {o['average_words_per_lesson']} |")
    a("")
    a("### Vocabulary growth by lesson")
    a("")
    a("| Lesson | Words presented | New unique words | Cumulative unique |")
    a("|---|---|---|---|")
    for g in o["vocabulary_growth_by_lesson"]:
        a(f"| {g['lesson']} | {g['words_presented']} | {g['new_unique_words']} "
          f"| {g['cumulative_unique_words']} |")
    a("")

    a("## 2. JLPT Coverage")
    a("")
    a("| Level | Words | % of curriculum | |")
    a("|---|---|---|---|")
    for level, v in results["jlpt"]["distribution"].items():
        label = "Outside JLPT" if level == "outside_jlpt" else level
        a(f"| {label} | {v['count']} | {v['percent']}% | `{bar(v['percent'])}` |")
    a("")
    a("### Cumulative JLPT coverage")
    a("")
    a("| After lesson | N5 | N4 | N3 | N2 | N1 | Outside |")
    a("|---|---|---|---|---|---|---|")
    for row in results["jlpt"]["cumulative_by_lesson"]:
        a(f"| {row['after_lesson']} | {row['N5']['count']} | {row['N4']['count']} "
          f"| {row['N3']['count']} | {row['N2']['count']} | {row['N1']['count']} "
          f"| {row['outside_jlpt']['count']} |")
    a("")

    a("## 3. Frequency Coverage (modern spoken Japanese)")
    a("")
    a("_Reference corpus: OpenSubtitles 2018 Japanese (film & TV dialogue), "
      "lemmatized with UniDic._")
    a("")
    a("| Band | Curriculum words in band | % of curriculum | % of band covered |")
    a("|---|---|---|---|")
    for band in FREQ_BANDS:
        v = results["frequency"][f"top_{band}"]
        a(f"| Top {band} | {v['curriculum_words_in_band']} "
          f"| {v['percent_of_curriculum']}% | {v['percent_of_band_covered']}% |")
    a("")
    a(f"Words with frequency data: {results['frequency']['words_with_frequency_data']} "
      f"of {o['unique_vocabulary']} (median rank "
      f"{results['frequency']['median_rank']}).")
    a("")

    a("## 4. Parts of Speech")
    a("")
    a("| Part of speech | Words | % | |")
    a("|---|---|---|---|")
    pos_labels = {"noun": "Nouns", "verb": "Verbs", "i_adjective": "i-adjectives",
                  "na_adjective": "na-adjectives", "expression": "Expressions",
                  "adverb": "Adverbs", "counter": "Counters", "pronoun": "Pronouns",
                  "conjunction": "Conjunctions", "particle": "Particles",
                  "other": "Other"}
    for p, v in results["parts_of_speech"].items():
        if v["count"] == 0:
            continue
        a(f"| {pos_labels[p]} | {v['count']} | {v['percent']}% | `{bar(v['percent'])}` |")
    a("")

    a("## 5. Theme Analysis")
    a("")
    a("_A word may belong to more than one theme; percentages are of unique words._")
    a("")
    a("| Theme | Words | % | |")
    a("|---|---|---|---|")
    for theme, v in results["themes"].items():
        a(f"| {theme.replace('_', ' ').title()} | {v['count']} | {v['percent']}% "
          f"| `{bar(v['percent'])}` |")
    a("")

    k = results["kanji"]
    a("## 6. Kanji Statistics")
    a("")
    a("| Metric | Value |")
    a("|---|---|")
    a(f"| Unique kanji | {k['unique_kanji']} |")
    a(f"| Joyo kanji | {k['joyo_kanji']} |")
    a(f"| Non-joyo kanji | {k['non_joyo_kanji']} ({''.join(k['non_joyo_list'])}) |")
    a(f"| Kana-only words | {k['kana_only_words']} ({k['kana_only_percent']}%) |")
    a(f"| Average unique kanji per lesson | {k['average_unique_kanji_per_lesson']} |")
    a("")

    lw = results["loanwords"]
    a("## 7. Loanword Analysis")
    a("")
    a("| Metric | Value |")
    a("|---|---|")
    a(f"| Katakana words | {lw['katakana_words']} |")
    a(f"| Loanwords (gairaigo) | {lw['loanword_count']} ({lw['loanword_percent']}%) |")
    a("")
    a("Word-origin breakdown (UniDic goshu):")
    a("")
    a("| Origin | Words | % |")
    a("|---|---|---|")
    for origin, v in lw["origin_breakdown"].items():
        a(f"| {origin.replace('_', ' ')} | {v['count']} | {v['percent']}% |")
    a("")

    rd = results["reading_difficulty"]
    a("## 8. Reading Difficulty")
    a("")
    a("| Metric | Value |")
    a("|---|---|")
    a(f"| Average reading length (kana) | {rd['average_reading_length_kana']} |")
    a(f"| Average kanji per word | {rd['average_kanji_per_word']} |")
    a(f"| Kana-only words | {rd['kana_only_percent']}% |")
    a("")

    r = results["reinforcement"]
    a("## 9. Reinforcement")
    a("")
    a("| Metric | Value |")
    a("|---|---|")
    a(f"| Words introduced once | {r['words_introduced_once']} |")
    a(f"| Words reviewed (2+ lessons) | {r['words_reviewed']} |")
    a(f"| Review rate | {r['review_rate_percent']}% |")
    a(f"| Spaced-repetition opportunities | {r['spaced_repetition_opportunities']['count']} |")
    a("")
    if r["words_in_multiple_lessons"]:
        a("Words appearing in multiple lessons:")
        a("")
        a("| Word | Reading | Lessons |")
        a("|---|---|---|")
        for w in r["words_in_multiple_lessons"]:
            a(f"| {w['jp']} | {w['reading']} | {', '.join(map(str, w['lessons']))} |")
        a("")
    else:
        a("No word has appeared in more than one lesson yet — every lesson so far "
          "introduces entirely new vocabulary. As the curriculum grows, the "
          "spaced-repetition list below is the natural pool for review lessons.")
        a("")

    a("## 10. Curriculum Progress (cumulative)")
    a("")
    a("| After lesson | Unique words | N5+N4 words | Top-1000 spoken coverage | Unique kanji |")
    a("|---|---|---|---|---|")
    for p in results["progress"]:
        n5n4 = p["jlpt_coverage"]["N5"]["count"] + p["jlpt_coverage"]["N4"]["count"]
        f1000 = p["frequency_coverage"]["top_1000"]
        a(f"| {p['after_lesson']} | {p['unique_words']} | {n5n4} "
          f"| {f1000['count']} ({f1000['percent_of_band']}%) | {p['unique_kanji']} |")
    a("")
    a("### Cumulative unique vocabulary")
    a("")
    a("```")
    max_cum = max(g["cumulative_unique_words"] for g in o["vocabulary_growth_by_lesson"])
    for g in o["vocabulary_growth_by_lesson"]:
        width = round(g["cumulative_unique_words"] / max_cum * 40)
        a(f"L{g['lesson']:>2} {'█' * width} {g['cumulative_unique_words']}")
    a("```")
    a("")
    a("---")
    a("")
    a("_Source data: published vocabulary lesson JSON files and the KML Master "
      "Vocabulary database (read-only). Reference data: JLPT word lists, "
      "OpenSubtitles-derived spoken frequency list, and the joyo kanji table. "
      "See `kml/analytics/README.md`._")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not OUTPUT_DIR.resolve().is_relative_to(ANALYTICS_DIR):
        sys.exit("Refusing to write outside kml/analytics/ — check output_dir.")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    lessons, lesson_paths = load_lessons()
    if not lessons:
        sys.exit("No lesson files matched the configured glob.")
    master = load_master_vocabulary()
    jlpt_table = load_jlpt()
    freq_ranks = load_frequency()
    joyo = load_joyo()

    words = build_words(lessons, master, jlpt_table, freq_ranks)
    results = analyze(lessons, words, freq_ranks, joyo)
    prov = provenance(lesson_paths)

    # -- kml_curriculum_analysis.json (superset) ----------------------------
    curriculum = {
        "schema": "kml.analytics.curriculum",
        "schema_version": 1,
        **prov,
        "analysis": results,
        "word_index": [
            {
                "jp": w.jp, "reading": w.reading, "en": w.en,
                "lessons": w.lessons, "roles": sorted(w.roles),
                "pos": w.pos, "themes": w.themes, "jlpt": w.jlpt,
                "spoken_frequency_rank": w.freq_rank, "kanji": w.kanji,
                "kana_only": w.kana_only, "katakana": w.katakana,
                "in_master_db": w.in_master_db,
            }
            for w in sorted(words.values(), key=lambda w: (w.lessons[0], w.jp))
        ],
    }
    (OUTPUT_DIR / CONFIG["outputs"]["curriculum"]).write_text(
        json.dumps(curriculum, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # -- kml_jlpt_statistics.json -------------------------------------------
    jlpt_out = {
        "schema": "kml.analytics.jlpt",
        "schema_version": 1,
        **prov,
        "unique_vocabulary": results["overall"]["unique_vocabulary"],
        "distribution": results["jlpt"]["distribution"],
        "cumulative_by_lesson": results["jlpt"]["cumulative_by_lesson"],
        "words_by_level": {
            level: sorted(w.jp for w in words.values()
                          if (w.jlpt or "outside_jlpt") == level)
            for level in ["N5", "N4", "N3", "N2", "N1", "outside_jlpt"]
        },
    }
    (OUTPUT_DIR / CONFIG["outputs"]["jlpt"]).write_text(
        json.dumps(jlpt_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # -- kml_frequency_statistics.json ---------------------------------------
    freq_out = {
        "schema": "kml.analytics.frequency",
        "schema_version": 1,
        **prov,
        "reference_corpus": "OpenSubtitles 2018 Japanese (hermitdave/FrequencyWords), "
                            "lemmatized with UniDic via fugashi",
        "unique_vocabulary": results["overall"]["unique_vocabulary"],
        "bands": {k: v for k, v in results["frequency"].items()
                  if k.startswith("top_")},
        "words_with_frequency_data": results["frequency"]["words_with_frequency_data"],
        "median_rank": results["frequency"]["median_rank"],
        "cumulative_by_lesson": [
            {"after_lesson": p["after_lesson"], **p["frequency_coverage"]}
            for p in results["progress"]
        ],
        "word_ranks": [
            {"jp": w.jp, "rank": w.freq_rank}
            for w in sorted(words.values(),
                            key=lambda w: (w.freq_rank is None, w.freq_rank or 0))
            if w.freq_rank
        ],
    }
    (OUTPUT_DIR / CONFIG["outputs"]["frequency"]).write_text(
        json.dumps(freq_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # -- kml_channel_statistics.json ------------------------------------------
    total_runtime = sum(l["meta"].get("soundtrackDurationMs") or 0 for l in lessons)
    channel = {
        "schema": "kml.analytics.channel",
        "schema_version": 1,
        **prov,
        "series": "japanese_vocabulary",
        "lessons_published": len(lessons),
        "total_vocabulary_presented": results["overall"]["total_vocabulary_occurrences"],
        "unique_vocabulary": results["overall"]["unique_vocabulary"],
        "total_soundtrack_runtime_ms": total_runtime,
        "total_soundtrack_runtime_hms": f"{total_runtime // 3600000}h "
                                        f"{total_runtime % 3600000 // 60000}m "
                                        f"{total_runtime % 60000 // 1000}s",
        "average_lesson_runtime_ms": round(total_runtime / len(lessons)) if lessons else 0,
        "beautiful_words": [
            {"lesson": l["number"], **bw}
            for l in lessons for bw in l["beautiful_words"]
        ],
        "lessons": [
            {
                "lesson": l["number"],
                "id": l["id"],
                "title": l["title"],
                "words_presented": len(l["words"]),
                "soundtrack_duration_ms": l["meta"].get("soundtrackDurationMs"),
                "estimated_content_runtime_ms": l["meta"].get("estimatedContentRuntimeMs"),
            }
            for l in lessons
        ],
    }
    (OUTPUT_DIR / CONFIG["outputs"]["channel"]).write_text(
        json.dumps(channel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # -- markdown report -------------------------------------------------------
    write_report(results, lessons, OUTPUT_DIR / CONFIG["outputs"]["report"])

    print(f"Analyzed {len(lessons)} lessons, "
          f"{results['overall']['unique_vocabulary']} unique words.")
    for key in ["curriculum", "jlpt", "frequency", "channel", "report"]:
        print("  wrote", OUTPUT_DIR / CONFIG["outputs"][key])


if __name__ == "__main__":
    main()
