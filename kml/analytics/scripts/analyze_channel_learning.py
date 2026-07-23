#!/usr/bin/env python3
"""KML Channel Learning Analytics.

Treats every playlist as an independent learning path and the full channel
as one global learning path. After every video, computes cumulative:

  • unique vocabulary introduced
  • unique kanji introduced
  • JLPT word-list coverage (N5–N1)
  • Joyo kanji coverage
  • spoken-frequency band coverage (top 500 / 1k / 2k / 5k)
  • exposure depth (how many times each item was seen)
  • review opportunities

Then reports the exact lesson at which each coverage threshold is crossed:

  10%  25%  50%  75%  90%  95%  100%

Exposure bands (per distinct video an item appears in):

  1      Introduced
  2      Reinforced
  3–5    Becoming familiar
  6–9    Strong recognition
  10+    Core knowledge

Outputs (under kml/analytics/output/):
  kml_channel_learning.json
  CHANNEL_LEARNING_REPORT.md

Design rules match analyze_curriculum.py: read-only inputs; write only under
kml/analytics/output/; fully regeneratable.
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
REPO_ROOT = ANALYTICS_DIR.parent.parent
CONFIG = json.loads((ANALYTICS_DIR / "analytics_config.json").read_text(encoding="utf-8"))
CHANNEL_CFG = CONFIG.get("channel_learning", {})

OUTPUT_DIR = REPO_ROOT / CONFIG["output_dir"]
FREQ_BANDS = list(CHANNEL_CFG.get("frequency_bands") or CONFIG["frequency_bands"])
THRESHOLDS = list(CHANNEL_CFG.get("coverage_thresholds") or [10, 25, 50, 75, 90, 95, 100])
REVIEW_GAP = int(CHANNEL_CFG.get("review_gap_lessons")
                 or CONFIG.get("reinforcement", {}).get("review_gap_lessons", 3))
EXPOSURE_BANDS = list(CHANNEL_CFG.get("exposure_bands") or [
    {"id": "introduced", "min": 1, "max": 1, "label": "Introduced", "meaning": "Seen once"},
    {"id": "reinforced", "min": 2, "max": 2, "label": "Reinforced", "meaning": "Seen twice"},
    {"id": "familiar", "min": 3, "max": 5, "label": "Becoming familiar", "meaning": "Seen 3–5 times"},
    {"id": "strong", "min": 6, "max": 9, "label": "Strong recognition", "meaning": "Seen 6–9 times"},
    {"id": "core", "min": 10, "max": None, "label": "Core knowledge", "meaning": "Seen 10+ times"},
])
EXPOSURE_DEPTHS = list(CHANNEL_CFG.get("exposure_depth_thresholds") or [1, 2, 3, 6, 10])
LV_CFG = dict(CHANNEL_CFG.get("learning_value") or {})
LV_STAR_THRESHOLDS = {
    int(k): int(v)
    for k, v in (LV_CFG.get("star_thresholds") or {
        "5": 80, "4": 50, "3": 25, "2": 12, "1": 0,
    }).items()
}
LV_INTRO_MAX_REINFORCE = float(LV_CFG.get("introduction_max_reinforce_share", 0.25))
LV_CONSOL_MAX_NEW = float(LV_CFG.get("consolidation_max_new_share", 0.25))
LV_LIGHT_MAX_TOTAL = int(LV_CFG.get("light_max_total", 15))

KANJI_RE = re.compile(r"[一-龯々〆〤]")
KANA_ONLY_RE = re.compile(r"^[ぁ-んァ-ヶーヽヾゝゞ・]+$")
TAGGER = fugashi.Tagger()

COLLECTIONS = REPO_ROOT / "kml/tools/ambient/collections"


# --------------------------------------------------------------------------
# Learning-path definitions (playlist = independent path)
# --------------------------------------------------------------------------

def _num_from_stem(stem: str, pattern: str) -> int:
    m = re.search(pattern, stem)
    return int(m.group(1)) if m else 0


def discover_vocabulary() -> list[dict]:
    paths = sorted(Path(p) for p in glob.glob(str(COLLECTIONS / "vocabulary/vocabulary_*.json")))
    lessons = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        n = int(data.get("meta", {}).get("lesson") or _num_from_stem(path.stem, r"(\d+)"))
        words = []
        for scene in data.get("scenes", []):
            for step in scene.get("compounds", {}).get("steps", []):
                words.append((step["jp"], step.get("reading", ""), step.get("en", ""), "compound"))
            bw = scene.get("beautifulWord")
            if bw and bw.get("jp"):
                words.append((bw["jp"], bw.get("reading", ""), bw.get("en", ""), "beautiful_word"))
        kanji = sorted({k for jp, *_ in words for k in KANJI_RE.findall(jp)})
        lessons.append({
            "order": n,
            "id": data.get("id", path.stem),
            "title": data.get("title", path.stem),
            "label": f"Spoken Vocabulary Lesson {n}",
            "file": str(path.relative_to(REPO_ROOT)),
            "words": words,
            "kanji": kanji,
            "kind": "vocabulary",
        })
    lessons.sort(key=lambda x: x["order"])
    return lessons


def discover_grade_kanji(grade: int) -> list[dict]:
    paths = sorted(
        p for p in (COLLECTIONS / f"grade_{grade}").glob(f"grade_{grade}_*.json")
        if re.fullmatch(rf"grade_{grade}_\d+", p.stem)
    )
    lessons = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        part = _num_from_stem(path.stem, rf"grade_{grade}_(\d+)")
        kanji = [s["kanji"] for s in data.get("scenes", []) if s.get("kanji")]
        lessons.append({
            "order": part,
            "id": data.get("id", path.stem),
            "title": data.get("title", path.stem),
            "label": f"Grade {grade} Lesson {part}",
            "file": str(path.relative_to(REPO_ROOT)),
            "words": [],
            "kanji": kanji,
            "kind": "kanji",
        })
    lessons.sort(key=lambda x: x["order"])
    return lessons


def discover_grade_compounds(grade: int) -> list[dict]:
    paths = sorted(
        p for p in (COLLECTIONS / f"grade_{grade}").glob(f"grade_{grade}_compounds_school_*.json")
        if re.search(r"_(\d+)$", p.stem)
    )
    lessons = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        part = _num_from_stem(path.stem, r"_(\d+)$")
        words = []
        kanji = []
        for scene in data.get("scenes", []):
            if scene.get("kanji"):
                kanji.append(scene["kanji"])
            anchor = scene.get("anchor") or {}
            if anchor.get("word"):
                words.append((anchor["word"], anchor.get("reading", ""), "", "anchor"))
            for step in scene.get("compounds", {}).get("steps", []):
                words.append((step["jp"], step.get("reading", ""), step.get("en", ""), "compound"))
        lessons.append({
            "order": part,
            "id": data.get("id", path.stem),
            "title": data.get("title", path.stem),
            "label": f"Grade {grade} Compounds Lesson {part}",
            "file": str(path.relative_to(REPO_ROOT)),
            "words": words,
            "kanji": sorted(set(kanji)),
            "kind": "compounds",
        })
    lessons.sort(key=lambda x: x["order"])
    return lessons


def discover_post_elementary_kanji() -> list[dict]:
    paths = sorted(
        p for p in (COLLECTIONS / "post_elementary").glob("post_elementary_*.json")
        if re.fullmatch(r"post_elementary_\d+", p.stem)
    )
    lessons = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        n = _num_from_stem(path.stem, r"(\d+)")
        kanji = [s["kanji"] for s in data.get("scenes", []) if s.get("kanji")]
        lessons.append({
            "order": n,
            "id": data.get("id", path.stem),
            "title": data.get("title", path.stem),
            "label": f"Post-Elementary Lesson {n}",
            "file": str(path.relative_to(REPO_ROOT)),
            "words": [],
            "kanji": kanji,
            "kind": "kanji",
        })
    lessons.sort(key=lambda x: x["order"])
    return lessons


def discover_post_elementary_compounds() -> list[dict]:
    paths = sorted(
        p for p in (COLLECTIONS / "post_elementary").glob("post_elementary_compounds_*.json")
        if re.fullmatch(r"post_elementary_compounds_\d+", p.stem)
    )
    lessons = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        n = _num_from_stem(path.stem, r"(\d+)")
        words = []
        for scene in data.get("scenes", []):
            for step in scene.get("compounds", {}).get("steps", []):
                words.append((step["jp"], step.get("reading", ""), step.get("en", ""), "compound"))
        kanji = sorted({k for jp, *_ in words for k in KANJI_RE.findall(jp)})
        lessons.append({
            "order": n,
            "id": data.get("id", path.stem),
            "title": data.get("title", path.stem),
            "label": f"Post-Elementary Compounds Lesson {n}",
            "file": str(path.relative_to(REPO_ROOT)),
            "words": words,
            "kanji": kanji,
            "kind": "compounds",
        })
    lessons.sort(key=lambda x: x["order"])
    return lessons


def discover_foundations() -> list[dict]:
    """Foundations lessons from collections/ and exhibition/ (deduped by lesson #)."""
    candidates: list[Path] = []
    candidates.extend(COLLECTIONS.glob("lesson_*_foundations.json"))
    candidates.extend(COLLECTIONS.glob("lesson_*/lesson_*_foundations.json"))
    exhibition = REPO_ROOT / "kml/tools/ambient/exhibition"
    if exhibition.is_dir():
        candidates.extend(exhibition.glob("lesson_*_foundations.json"))

    by_num: dict[int, Path] = {}
    for path in candidates:
        n = _num_from_stem(path.stem, r"lesson_(\d+)")
        if n <= 0:
            continue
        # Prefer collections/ over exhibition/ when both exist
        prev = by_num.get(n)
        if prev is None or "collections" in str(path) and "exhibition" in str(prev):
            by_num[n] = path

    lessons = []
    for n, path in sorted(by_num.items()):
        data = json.loads(path.read_text(encoding="utf-8"))
        kanji = [s["kanji"] for s in data.get("scenes", []) if s.get("kanji")]
        lessons.append({
            "order": n,
            "id": data.get("id", path.stem),
            "title": data.get("title", path.stem),
            "label": f"Foundations Lesson {n}",
            "file": str(path.relative_to(REPO_ROOT)),
            "words": [],
            "kanji": kanji,
            "kind": "kanji",
        })
    return lessons


def build_paths() -> dict[str, dict]:
    """id -> {name, lessons, role}."""
    paths: dict[str, dict] = {}

    vocab = discover_vocabulary()
    if vocab:
        paths["japanese_vocabulary"] = {
            "name": "Japanese Vocabulary",
            "role": "spoken_vocabulary",
            "lessons": vocab,
        }

    for grade in range(1, 7):
        gk = discover_grade_kanji(grade)
        if gk:
            paths[f"grade_{grade}_kanji"] = {
                "name": f"Grade {grade} Kanji Soundtrack",
                "role": "kanji",
                "lessons": gk,
            }
        gc = discover_grade_compounds(grade)
        if gc:
            paths[f"grade_{grade}_compounds"] = {
                "name": f"Grade {grade} School Compounds",
                "role": "compounds",
                "lessons": gc,
            }

    pe = discover_post_elementary_kanji()
    if pe:
        paths["post_elementary_kanji"] = {
            "name": "Post-Elementary Kanji",
            "role": "kanji",
            "lessons": pe,
        }
    pec = discover_post_elementary_compounds()
    if pec:
        paths["post_elementary_compounds"] = {
            "name": "Post-Elementary Compounds",
            "role": "compounds",
            "lessons": pec,
        }

    foundations = discover_foundations()
    if foundations:
        paths["foundations"] = {
            "name": "Foundations (Heisig)",
            "role": "kanji",
            "lessons": foundations,
        }

    # Global educational progression (learner perspective, not upload order).
    # Kanji introduction → compound reinforcement → spoken vocabulary.
    global_order = (
        [f"grade_{g}_kanji" for g in range(1, 7)]
        + ["post_elementary_kanji"]
        + [f"grade_{g}_compounds" for g in range(1, 7)]
        + ["post_elementary_compounds"]
        + ["japanese_vocabulary"]
        + ["foundations"]
    )
    global_lessons = []
    seq = 0
    for pid in global_order:
        path = paths.get(pid)
        if not path:
            continue
        for lesson in path["lessons"]:
            seq += 1
            global_lessons.append({
                **lesson,
                "order": seq,
                "source_path": pid,
                "label": lesson["label"],
                "global_index": seq,
            })
    paths["channel_global"] = {
        "name": "Complete Channel (global learning path)",
        "role": "global",
        "lessons": global_lessons,
    }
    return paths


# --------------------------------------------------------------------------
# Reference loaders
# --------------------------------------------------------------------------

def sha256_short(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def load_jlpt_sets() -> dict[str, set[str]]:
    sets: dict[str, set[str]] = {}
    reading_sets: dict[str, set[str]] = {}
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        path = REPO_ROOT / CONFIG["reference"]["jlpt_wordlists"][level]
        exprs: set[str] = set()
        readings: set[str] = set()
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                expr = (row.get("expression") or "").strip()
                reading = (row.get("reading") or "").strip()
                if expr:
                    exprs.add(expr)
                if reading:
                    readings.add(reading)
        sets[level] = exprs
        reading_sets[level] = readings
    sets["__readings__"] = reading_sets  # type: ignore[assignment]
    return sets


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


def load_joyo() -> dict[str, dict]:
    """kanji -> {grade, joyo_index}."""
    path = REPO_ROOT / CONFIG["reference"]["joyo_kanji"]
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            k = (row.get("kanji") or "").strip()
            if k:
                out[k] = {"grade": row.get("grade"), "joyo_index": row.get("joyo_index")}
    return out


def load_kanji_jlpt() -> dict[str, str]:
    path = REPO_ROOT / "kml/data/kanji/kanji_master.csv"
    out: dict[str, str] = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            k = (row.get("kanji") or "").strip()
            level = (row.get("jlpt") or "").strip()
            if k and level:
                out[k] = level
    return out


def load_master_vocabulary() -> dict[str, dict]:
    path = REPO_ROOT / CONFIG["sources"]["master_vocabulary"]
    data = json.loads(path.read_text(encoding="utf-8"))
    index = {}
    for e in data.get("entries", []):
        index[e["jp"]] = {"jlpt": e.get("jlpt")}
    return index


def to_hiragana(text: str) -> str:
    norm = unicodedata.normalize("NFKC", text)
    return "".join(chr(ord(c) - 96) if "ァ" <= c <= "ヶ" else c for c in norm)


def word_in_jlpt(jp: str, reading: str, jlpt_sets: dict[str, set[str]], level: str) -> bool:
    if jp in jlpt_sets[level]:
        return True
    if KANA_ONLY_RE.match(jp):
        hira = to_hiragana(jp)
        return hira in jlpt_sets["__readings__"].get(level, set())
    return False


def lemma_rank(jp: str, ranks: dict[str, int]) -> tuple[int | None, str | None]:
    if jp in ranks:
        return ranks[jp], jp
    tokens = list(TAGGER(jp))
    if len(tokens) == 1:
        lemma = tokens[0].feature.orthBase
        if lemma and lemma in ranks:
            return ranks[lemma], lemma
    return None, None


def pct(part: float, whole: float) -> float:
    return round(100.0 * part / whole, 2) if whole else 0.0


def mean(values: list[float | int]) -> float | None:
    return round(sum(values) / len(values), 2) if values else None


def exposure_band_id(count: int) -> str | None:
    if count < 1:
        return None
    for band in EXPOSURE_BANDS:
        lo = int(band["min"])
        hi = band["max"]
        if hi is None:
            if count >= lo:
                return band["id"]
        elif lo <= count <= int(hi):
            return band["id"]
    return EXPOSURE_BANDS[-1]["id"]


def band_distribution(counts: list[int], population: int | None = None) -> dict:
    """Bucket encounter counts into exposure bands.

    If population is set, percents are of that reference set (unseen → remainder).
    Otherwise percents are of items that have been seen (len(counts)).
    """
    seen = len(counts)
    denom = population if population is not None else seen
    buckets: dict[str, int] = {b["id"]: 0 for b in EXPOSURE_BANDS}
    for c in counts:
        bid = exposure_band_id(c)
        if bid:
            buckets[bid] += 1
    out = {}
    for band in EXPOSURE_BANDS:
        bid = band["id"]
        c = buckets[bid]
        out[bid] = {
            "label": band["label"],
            "meaning": band["meaning"],
            "min": band["min"],
            "max": band["max"],
            "count": c,
            "percent": pct(c, denom) if denom else 0.0,
        }
    if population is not None:
        unseen = max(0, population - seen)
        out["unseen"] = {
            "label": "Unseen",
            "meaning": "Never encountered",
            "min": 0,
            "max": 0,
            "count": unseen,
            "percent": pct(unseen, population) if population else 0.0,
        }
    return out


def depth_coverage(counts_by_item: dict[str, int], universe: set[str],
                   depths: list[int] | None = None) -> dict:
    """Share of universe with at least N video encounters."""
    depths = depths or EXPOSURE_DEPTHS
    total = len(universe)
    out = {}
    for d in depths:
        n = sum(1 for item in universe if counts_by_item.get(item, 0) >= d)
        out[f"at_least_{d}"] = {
            "min_encounters": d,
            "covered": n,
            "total": total,
            "percent": pct(n, total),
        }
    return out


def cohort_exposure(counts_by_item: dict[str, int], cohort: set[str]) -> dict:
    """Exposure stats for a named reference cohort (e.g. Joyo, JLPT N3 kanji)."""
    seen_counts = [counts_by_item[i] for i in cohort if i in counts_by_item]
    return {
        "cohort_size": len(cohort),
        "encountered": len(seen_counts),
        "encountered_percent": pct(len(seen_counts), len(cohort)),
        "average_encounters_among_seen": mean(seen_counts),
        "average_encounters_across_cohort": mean(
            [counts_by_item.get(i, 0) for i in cohort]
        ),
        "bands": band_distribution(seen_counts, population=len(cohort)),
        "depth": depth_coverage(counts_by_item, cohort),
    }


# --------------------------------------------------------------------------
# Coverage engine
# --------------------------------------------------------------------------

@dataclass
class WordInfo:
    jp: str
    reading: str
    en: str
    first_lesson_order: int
    first_lesson_label: str
    appearances: list[int] = field(default_factory=list)
    jlpt_levels: set[str] = field(default_factory=set)  # membership in lists
    freq_rank: int | None = None
    lemma: str | None = None


def build_exposure_snapshot(
    word_video_counts: dict[str, int],
    kanji_video_counts: dict[str, int],
    word_raw_counts: dict[str, int],
    kanji_raw_counts: dict[str, int],
    seen_words: dict[str, WordInfo],
    joyo_set: set[str],
    kanji_jlpt_sets: dict[str, set[str]],
    jlpt_sets: dict[str, set[str]],
) -> dict:
    word_counts = list(word_video_counts.values())
    kanji_counts = list(kanji_video_counts.values())

    multi_context_words = sum(1 for c in word_counts if c >= 2)
    multi_context_kanji = sum(1 for c in kanji_counts if c >= 2)

    # JLPT word cohorts: words in curriculum that belong to each list,
    # plus depth vs the full list.
    jlpt_word_exposure = {}
    for lv in ["N5", "N4", "N3", "N2", "N1"]:
        # Map curriculum words → encounter count if they hit this JLPT list
        curriculum_in_level = {
            jp: word_video_counts[jp]
            for jp, w in seen_words.items()
            if lv in w.jlpt_levels
        }
        # Also score the full list: count encounters for list members
        # (0 if never seen). Match by surface form only for cohort depth.
        list_counts = {
            expr: word_video_counts.get(expr, 0) for expr in jlpt_sets[lv]
        }
        jlpt_word_exposure[lv] = {
            "curriculum_items": len(curriculum_in_level),
            "average_encounters_among_curriculum": mean(list(curriculum_in_level.values())),
            "list_depth": depth_coverage(list_counts, jlpt_sets[lv]),
            "average_encounters_across_list": mean(list(list_counts.values())),
        }

    joyo_exposure = cohort_exposure(kanji_video_counts, joyo_set)
    jlpt_kanji_exposure = {
        lv: cohort_exposure(kanji_video_counts, kanji_jlpt_sets[lv])
        for lv in kanji_jlpt_sets
    }

    statements = exposure_statements(
        word_video_counts, kanji_video_counts, word_counts, kanji_counts,
        multi_context_words, multi_context_kanji,
        joyo_exposure, jlpt_kanji_exposure, jlpt_word_exposure,
    )

    return {
        "definition": {
            "encounters": "Distinct videos in which the item appears at least once "
                          "(one encounter per video, regardless of repetitions inside "
                          "that video).",
            "raw_presentations": "Every word slot and every kanji presentation slot "
                                "inside a video (can exceed encounters).",
            "bands": EXPOSURE_BANDS,
        },
        "vocabulary": {
            "unique": len(word_counts),
            "total_encounters": sum(word_counts),
            "total_raw_presentations": sum(word_raw_counts.values()),
            "average_encounters": mean(word_counts),
            "median_encounters": sorted(word_counts)[len(word_counts) // 2] if word_counts else None,
            "max_encounters": max(word_counts) if word_counts else 0,
            "multiple_contexts": multi_context_words,
            "multiple_contexts_percent": pct(multi_context_words, len(word_counts)),
            "bands": band_distribution(word_counts),
            "depth_of_seen": {
                f"at_least_{d}": {
                    "min_encounters": d,
                    "count": sum(1 for c in word_counts if c >= d),
                    "percent_of_seen": pct(sum(1 for c in word_counts if c >= d), len(word_counts)),
                }
                for d in EXPOSURE_DEPTHS
            },
        },
        "kanji": {
            "unique": len(kanji_counts),
            "total_encounters": sum(kanji_counts),
            "total_raw_presentations": sum(kanji_raw_counts.values()),
            "average_encounters": mean(kanji_counts),
            "median_encounters": sorted(kanji_counts)[len(kanji_counts) // 2] if kanji_counts else None,
            "max_encounters": max(kanji_counts) if kanji_counts else 0,
            "multiple_contexts": multi_context_kanji,
            "multiple_contexts_percent": pct(multi_context_kanji, len(kanji_counts)),
            "bands": band_distribution(kanji_counts),
            "depth_of_seen": {
                f"at_least_{d}": {
                    "min_encounters": d,
                    "count": sum(1 for c in kanji_counts if c >= d),
                    "percent_of_seen": pct(sum(1 for c in kanji_counts if c >= d), len(kanji_counts)),
                }
                for d in EXPOSURE_DEPTHS
            },
        },
        "joyo": joyo_exposure,
        "jlpt_kanji": jlpt_kanji_exposure,
        "jlpt_words": jlpt_word_exposure,
        "statements": statements,
    }


def exposure_statements(
    word_video_counts, kanji_video_counts, word_counts, kanji_counts,
    multi_context_words, multi_context_kanji,
    joyo_exposure, jlpt_kanji_exposure, jlpt_word_exposure,
) -> list[str]:
    stmts: list[str] = []

    # Joyo depth statements
    for key, label in [
        ("at_least_1", "at least once"),
        ("at_least_2", "at least twice"),
        ("at_least_3", "at least three times"),
        ("at_least_6", "at least six times"),
        ("at_least_10", "at least ten times"),
    ]:
        d = joyo_exposure["depth"].get(key)
        if d and d["covered"]:
            stmts.append(
                f"{d['percent']}% of the Joyo kanji have been encountered {label} "
                f"({d['covered']} of {d['total']})."
            )

    if multi_context_words:
        stmts.append(
            f"{multi_context_words} vocabulary items have appeared in multiple contexts "
            f"({pct(multi_context_words, len(word_counts))}% of seen vocabulary)."
        )
    if multi_context_kanji:
        stmts.append(
            f"{multi_context_kanji} kanji have appeared in multiple contexts "
            f"({pct(multi_context_kanji, len(kanji_counts))}% of seen kanji)."
        )

    for lv in ["N5", "N4", "N3", "N2", "N1"]:
        avg = jlpt_kanji_exposure[lv]["average_encounters_among_seen"]
        n = jlpt_kanji_exposure[lv]["encountered"]
        if avg is not None and n:
            stmts.append(
                f"The average JLPT {lv} kanji (among those seen) has been encountered "
                f"{avg} times ({n} of {jlpt_kanji_exposure[lv]['cohort_size']})."
            )

    for lv in ["N5", "N4", "N3", "N2", "N1"]:
        avg = jlpt_word_exposure[lv]["average_encounters_among_curriculum"]
        n = jlpt_word_exposure[lv]["curriculum_items"]
        if avg is not None and n:
            stmts.append(
                f"The average JLPT {lv} vocabulary item in the curriculum has been "
                f"encountered {avg} times ({n} items)."
            )

    # Band highlights for vocabulary and joyo
    vb = band_distribution(word_counts)
    for band in EXPOSURE_BANDS:
        bid = band["id"]
        if vb[bid]["count"]:
            stmts.append(
                f"{vb[bid]['count']} vocabulary items are at the "
                f"“{band['label']}” stage ({band['meaning']})."
            )

    jb = joyo_exposure["bands"]
    for band in EXPOSURE_BANDS:
        bid = band["id"]
        if jb[bid]["count"]:
            stmts.append(
                f"{jb[bid]['percent']}% of Joyo kanji are at the "
                f"“{band['label']}” stage ({jb[bid]['count']} characters)."
            )

    return stmts


def learning_value_stars(total: int) -> str:
    """Magnitude stars (not a competitive ranking)."""
    for stars in sorted(LV_STAR_THRESHOLDS.keys(), reverse=True):
        if total >= LV_STAR_THRESHOLDS[stars]:
            return "★" * stars + "☆" * (5 - stars)
    return "☆☆☆☆☆"


def classify_educational_role(new_total: int, reinforced_total: int) -> dict:
    """Describe what this video is for in the learning path."""
    total = new_total + reinforced_total
    if total == 0:
        return {
            "id": "empty",
            "label": "Empty",
            "description": "No vocabulary or kanji content detected.",
        }
    if total <= LV_LIGHT_MAX_TOTAL:
        return {
            "id": "light",
            "label": "Light touch",
            "description": "Small content load — a short review or transitional lesson.",
        }
    new_share = new_total / total
    reinforce_share = reinforced_total / total
    if reinforce_share <= LV_INTRO_MAX_REINFORCE:
        return {
            "id": "introduction",
            "label": "Introduction",
            "description": "Primarily introduces new material.",
        }
    if new_share <= LV_CONSOL_MAX_NEW:
        return {
            "id": "consolidation",
            "label": "Consolidation",
            "description": "Primarily reinforces previously seen material.",
        }
    return {
        "id": "balanced",
        "label": "Balanced",
        "description": "Mix of new introductions and reinforcement.",
    }


def compute_video_learning_value(
    *,
    new_kanji: int,
    reinforced_kanji: int,
    new_vocabulary: int,
    reinforced_vocabulary: int,
    jlpt_word_gain: dict[str, int],
    jlpt_kanji_gain: dict[str, int],
    spoken_gain: dict[str, int],
) -> dict:
    new_total = new_kanji + new_vocabulary
    reinforced_total = reinforced_kanji + reinforced_vocabulary
    total = new_total + reinforced_total
    jlpt_words_gained = sum(jlpt_word_gain.values())
    jlpt_kanji_gained = sum(jlpt_kanji_gain.values())
    # Prefer top-1000 spoken gain as the headline spoken metric; also keep bands.
    spoken_headline = spoken_gain.get("top_1000", 0)
    role = classify_educational_role(new_total, reinforced_total)
    return {
        "new_kanji": new_kanji,
        "reinforced_kanji": reinforced_kanji,
        "new_vocabulary": new_vocabulary,
        "reinforced_vocabulary": reinforced_vocabulary,
        "new_total": new_total,
        "reinforced_total": reinforced_total,
        "total_learning_value": total,
        "stars": learning_value_stars(total),
        "star_count": learning_value_stars(total).count("★"),
        "educational_role": role,
        "jlpt_gain": {
            "words_by_level": jlpt_word_gain,
            "kanji_by_level": jlpt_kanji_gain,
            "words_total": jlpt_words_gained,
            "kanji_total": jlpt_kanji_gained,
            "combined": jlpt_words_gained + jlpt_kanji_gained,
        },
        "spoken_frequency_gain": {
            **{f"top_{b}": spoken_gain.get(f"top_{b}", 0) for b in FREQ_BANDS},
            "headline_top_1000": spoken_headline,
            "any_band": spoken_gain.get("any_band", 0),
        },
    }


def summarize_learning_values(per_lesson: list[dict]) -> dict:
    """Path-level view of video roles and standout lessons."""
    rows = [L["learning_value"] for L in per_lesson if L.get("learning_value")]
    if not rows:
        return {}
    by_role: Counter = Counter(r["educational_role"]["id"] for r in rows)
    # Exemplars the user asked about — pick high-signal lessons per role
    introducers = sorted(
        (L for L in per_lesson if L.get("learning_value", {}).get("educational_role", {}).get("id") == "introduction"),
        key=lambda L: L["learning_value"]["new_total"],
        reverse=True,
    )[:5]
    consolidators = sorted(
        (L for L in per_lesson
         if L.get("learning_value", {}).get("educational_role", {}).get("id") == "consolidation"),
        key=lambda L: L["learning_value"]["reinforced_total"],
        reverse=True,
    )[:5]
    balanced = sorted(
        (L for L in per_lesson
         if L.get("learning_value", {}).get("educational_role", {}).get("id") == "balanced"),
        key=lambda L: L["learning_value"]["total_learning_value"],
        reverse=True,
    )[:5]
    highest = sorted(
        per_lesson,
        key=lambda L: L.get("learning_value", {}).get("total_learning_value", 0),
        reverse=True,
    )[:10]

    def brief(L: dict) -> dict:
        lv = L["learning_value"]
        return {
            "label": L["label"],
            "id": L["id"],
            "new": lv["new_total"],
            "reinforced": lv["reinforced_total"],
            "total": lv["total_learning_value"],
            "stars": lv["stars"],
            "role": lv["educational_role"]["label"],
            "new_kanji": lv["new_kanji"],
            "reinforced_kanji": lv["reinforced_kanji"],
            "new_vocabulary": lv["new_vocabulary"],
            "reinforced_vocabulary": lv["reinforced_vocabulary"],
            "jlpt_gain": lv["jlpt_gain"]["combined"],
            "spoken_top_1000_gain": lv["spoken_frequency_gain"]["headline_top_1000"],
        }

    return {
        "videos": len(rows),
        "role_counts": dict(by_role),
        "average_total_learning_value": mean([r["total_learning_value"] for r in rows]),
        "average_new": mean([r["new_total"] for r in rows]),
        "average_reinforced": mean([r["reinforced_total"] for r in rows]),
        "highest_learning_value": [brief(L) for L in highest],
        "top_introduction_lessons": [brief(L) for L in introducers],
        "top_consolidation_lessons": [brief(L) for L in consolidators],
        "top_balanced_lessons": [brief(L) for L in balanced],
        "comparison_table": [
            {
                "lesson": L["label"],
                "new": L["learning_value"]["new_total"],
                "reinforced": L["learning_value"]["reinforced_total"],
                "total_learning_value": L["learning_value"]["total_learning_value"],
                "stars": L["learning_value"]["stars"],
                "role": L["learning_value"]["educational_role"]["label"],
            }
            for L in per_lesson
        ],
    }


def build_search_index(
    seen_words: dict[str, WordInfo],
    word_video_counts: dict[str, int],
    word_latest_label: dict[str, str],
    word_first_path: dict[str, str],
    kanji_video_counts: dict[str, int],
    kanji_first_label: dict[str, str],
    kanji_latest_label: dict[str, str],
    kanji_first_path: dict[str, str],
    kanji_lessons: dict[str, list[int]],
    joyo_set: set[str],
    kanji_jlpt: dict[str, str],
) -> dict:
    """Compact searchable inventory for the dashboard (analytics-only)."""
    vocab = []
    for jp, w in sorted(seen_words.items(), key=lambda x: (x[1].first_lesson_order, x[0])):
        enc = word_video_counts.get(jp, 0)
        band = exposure_band_id(enc)
        band_meta = next((b for b in EXPOSURE_BANDS if b["id"] == band), None)
        easiest = None
        for lv in ["N5", "N4", "N3", "N2", "N1"]:
            if lv in w.jlpt_levels:
                easiest = lv
                break
        vocab.append({
            "jp": jp,
            "reading": w.reading,
            "en": w.en,
            "encounters": enc,
            "first_order": w.first_lesson_order,
            "first_lesson": w.first_lesson_label,
            "latest_lesson": word_latest_label.get(jp, w.first_lesson_label),
            "first_path": word_first_path.get(jp),
            "stage": (band_meta or {}).get("label"),
            "stage_id": band,
            "jlpt": easiest,
            "spoken_rank": w.freq_rank,
        })

    kanji_rows = []
    for k, enc in sorted(kanji_video_counts.items(), key=lambda x: (min(kanji_lessons.get(x[0], [10**9])), x[0])):
        band = exposure_band_id(enc)
        band_meta = next((b for b in EXPOSURE_BANDS if b["id"] == band), None)
        orders = kanji_lessons.get(k) or [0]
        kanji_rows.append({
            "kanji": k,
            "encounters": enc,
            "first_order": min(orders),
            "first_lesson": kanji_first_label.get(k),
            "latest_lesson": kanji_latest_label.get(k),
            "first_path": kanji_first_path.get(k),
            "stage": (band_meta or {}).get("label"),
            "stage_id": band,
            "joyo": k in joyo_set,
            "jlpt": kanji_jlpt.get(k),
        })

    return {
        "vocabulary": vocab,
        "kanji": kanji_rows,
        "counts": {"vocabulary": len(vocab), "kanji": len(kanji_rows)},
    }


def analyze_path(
    path_id: str,
    path: dict,
    jlpt_sets: dict[str, set[str]],
    freq_ranks: dict[str, int],
    joyo: dict[str, dict],
    kanji_jlpt: dict[str, str],
    master: dict[str, dict],
) -> dict:
    lessons = path["lessons"]
    joyo_set = set(joyo)
    jlpt_sizes = {lv: len(jlpt_sets[lv]) for lv in ["N5", "N4", "N3", "N2", "N1"]}
    joyo_size = len(joyo_set)
    kanji_jlpt_sets = {
        lv: {k for k, v in kanji_jlpt.items() if v == lv}
        for lv in ["N5", "N4", "N3", "N2", "N1"]
    }

    seen_words: dict[str, WordInfo] = {}
    seen_kanji: set[str] = set()
    seen_lemmas_in_band: dict[int, set[str]] = {b: set() for b in FREQ_BANDS}
    jlpt_hits: dict[str, set[str]] = {lv: set() for lv in jlpt_sizes}
    joyo_hits: set[str] = set()
    kanji_jlpt_hits: dict[str, set[str]] = {lv: set() for lv in kanji_jlpt_sets}

    # Encounters = distinct videos; raw = every presentation slot
    word_video_counts: dict[str, int] = defaultdict(int)
    kanji_video_counts: dict[str, int] = defaultdict(int)
    word_raw_counts: dict[str, int] = defaultdict(int)
    kanji_raw_counts: dict[str, int] = defaultdict(int)
    word_lessons: dict[str, list[int]] = defaultdict(list)
    kanji_lessons: dict[str, list[int]] = defaultdict(list)
    word_latest_label: dict[str, str] = {}
    kanji_first_label: dict[str, str] = {}
    kanji_latest_label: dict[str, str] = {}
    word_first_path: dict[str, str] = {}
    kanji_first_path: dict[str, str] = {}

    progress = []
    per_lesson = []

    for lesson in lessons:
        order = lesson["order"]
        label = lesson["label"]
        source_path = lesson.get("source_path", path_id)
        new_words: list[str] = []
        new_kanji: list[str] = []
        reviewed_words: list[str] = []
        reviewed_kanji: list[str] = []

        words_this_video: set[str] = set()
        kanji_this_video: set[str] = set()

        # Snapshot coverage before this video (for gain deltas)
        jlpt_words_before = {lv: len(jlpt_hits[lv]) for lv in jlpt_sizes}
        jlpt_kanji_before = {lv: len(kanji_jlpt_hits[lv]) for lv in kanji_jlpt_sets}
        spoken_before = {band: set(seen_lemmas_in_band[band]) for band in FREQ_BANDS}
        spoken_any_before = set().union(*(spoken_before[b] for b in FREQ_BANDS)) if FREQ_BANDS else set()

        for jp, reading, en, _role in lesson["words"]:
            word_raw_counts[jp] += 1
            word_lessons[jp].append(order)
            words_this_video.add(jp)

            if jp not in seen_words:
                rank, lemma = lemma_rank(jp, freq_ranks)
                levels = {lv for lv in jlpt_sizes if word_in_jlpt(jp, reading, jlpt_sets, lv)}
                master_lv = (master.get(jp) or {}).get("jlpt")
                if master_lv:
                    levels.add(master_lv)
                seen_words[jp] = WordInfo(
                    jp=jp, reading=reading, en=en,
                    first_lesson_order=order, first_lesson_label=label,
                    appearances=[order], jlpt_levels=levels,
                    freq_rank=rank, lemma=lemma,
                )
                word_first_path[jp] = source_path
                new_words.append(jp)
                for lv in levels:
                    if lv in jlpt_hits:
                        jlpt_hits[lv].add(jp)
                if rank is not None:
                    key = lemma or jp
                    for band in FREQ_BANDS:
                        if rank <= band:
                            seen_lemmas_in_band[band].add(key)
            else:
                seen_words[jp].appearances.append(order)
                reviewed_words.append(jp)

            for k in KANJI_RE.findall(jp):
                kanji_raw_counts[k] += 1
                kanji_this_video.add(k)

        for k in lesson["kanji"]:
            kanji_raw_counts[k] += 1
            kanji_this_video.add(k)

        # One encounter per distinct video
        for jp in words_this_video:
            word_video_counts[jp] += 1
            word_latest_label[jp] = label
        for k in kanji_this_video:
            kanji_lessons[k].append(order)
            if k not in seen_kanji:
                seen_kanji.add(k)
                new_kanji.append(k)
                kanji_first_label[k] = label
                kanji_first_path[k] = source_path
                if k in joyo_set:
                    joyo_hits.add(k)
                lv = kanji_jlpt.get(k)
                if lv in kanji_jlpt_hits:
                    kanji_jlpt_hits[lv].add(k)
            else:
                reviewed_kanji.append(k)
            kanji_video_counts[k] += 1
            kanji_latest_label[k] = label

        new_kanji_n = len(set(new_kanji))
        # Reinforced = previously seen items that appear in this video
        reinforced_kanji_n = len(kanji_this_video) - new_kanji_n
        new_vocab_n = len(set(new_words))
        reinforced_vocab_n = len(words_this_video) - new_vocab_n

        jlpt_word_gain = {
            lv: len(jlpt_hits[lv]) - jlpt_words_before[lv] for lv in jlpt_sizes
        }
        jlpt_kanji_gain = {
            lv: len(kanji_jlpt_hits[lv]) - jlpt_kanji_before[lv]
            for lv in kanji_jlpt_sets
        }
        spoken_gain = {
            f"top_{band}": len(seen_lemmas_in_band[band] - spoken_before[band])
            for band in FREQ_BANDS
        }
        spoken_any_after = set().union(*(seen_lemmas_in_band[b] for b in FREQ_BANDS)) if FREQ_BANDS else set()
        spoken_gain["any_band"] = len(spoken_any_after - spoken_any_before)

        lv = compute_video_learning_value(
            new_kanji=new_kanji_n,
            reinforced_kanji=reinforced_kanji_n,
            new_vocabulary=new_vocab_n,
            reinforced_vocabulary=reinforced_vocab_n,
            jlpt_word_gain=jlpt_word_gain,
            jlpt_kanji_gain=jlpt_kanji_gain,
            spoken_gain=spoken_gain,
        )

        # Spaced-repetition opportunities after this lesson
        sr_words = [
            jp for jp, orders in word_lessons.items()
            if word_video_counts[jp] == 1 and min(orders) <= order - REVIEW_GAP
        ]
        sr_kanji = [
            k for k, orders in kanji_lessons.items()
            if kanji_video_counts[k] == 1 and min(orders) <= order - REVIEW_GAP
        ]

        jlpt_cov = {
            lv_name: {
                "covered": len(jlpt_hits[lv_name]),
                "total": jlpt_sizes[lv_name],
                "percent": pct(len(jlpt_hits[lv_name]), jlpt_sizes[lv_name]),
            }
            for lv_name in jlpt_sizes
        }
        freq_cov = {
            f"top_{band}": {
                "covered": len(seen_lemmas_in_band[band]),
                "total": band,
                "percent": pct(len(seen_lemmas_in_band[band]), band),
            }
            for band in FREQ_BANDS
        }
        joyo_cov = {
            "covered": len(joyo_hits),
            "total": joyo_size,
            "percent": pct(len(joyo_hits), joyo_size),
        }
        kanji_jlpt_cov = {
            lv_name: {
                "covered": len(kanji_jlpt_hits[lv_name]),
                "total": len(kanji_jlpt_sets[lv_name]),
                "percent": pct(len(kanji_jlpt_hits[lv_name]), len(kanji_jlpt_sets[lv_name])),
            }
            for lv_name in kanji_jlpt_sets
        }

        joyo_depth = depth_coverage(kanji_video_counts, joyo_set)
        vocab_bands = band_distribution(list(word_video_counts.values()))
        kanji_bands = band_distribution(list(kanji_video_counts.values()))

        snap = {
            "after_order": order,
            "after_lesson_id": lesson["id"],
            "after_lesson_label": label,
            "source_path": lesson.get("source_path", path_id),
            "unique_vocabulary": len(seen_words),
            "unique_kanji": len(seen_kanji),
            "new_vocabulary": new_vocab_n,
            "new_kanji": new_kanji_n,
            "reviewed_vocabulary": reinforced_vocab_n,
            "reviewed_kanji": reinforced_kanji_n,
            "jlpt_word_coverage": jlpt_cov,
            "jlpt_kanji_coverage": kanji_jlpt_cov,
            "joyo_coverage": joyo_cov,
            "spoken_frequency_coverage": freq_cov,
            "review_opportunities": {
                "vocabulary_due": len(sr_words),
                "kanji_due": len(sr_kanji),
            },
            "learning_value": lv,
            "exposure": {
                "vocabulary_multiple_contexts": sum(
                    1 for c in word_video_counts.values() if c >= 2
                ),
                "kanji_multiple_contexts": sum(
                    1 for c in kanji_video_counts.values() if c >= 2
                ),
                "vocabulary_bands": {
                    bid: vocab_bands[bid]["count"] for bid in vocab_bands
                },
                "kanji_bands": {
                    bid: kanji_bands[bid]["count"] for bid in kanji_bands
                },
                "joyo_depth": {
                    k: v["percent"] for k, v in joyo_depth.items()
                },
                "joyo_average_encounters_among_seen": mean(
                    [kanji_video_counts[k] for k in joyo_hits]
                ),
            },
        }
        progress.append(snap)
        per_lesson.append({
            "order": order,
            "id": lesson["id"],
            "label": label,
            "title": lesson["title"],
            "kind": lesson["kind"],
            "source_path": lesson.get("source_path", path_id),
            "words_presented": len(lesson["words"]),
            "kanji_presented": len(lesson["kanji"]),
            "new_unique_vocabulary": sorted(set(new_words)),
            "new_unique_kanji": sorted(set(new_kanji)),
            "review_vocabulary_count": reinforced_vocab_n,
            "review_kanji_count": reinforced_kanji_n,
            "learning_value": lv,
        })

    milestones = compute_milestones(progress, path["name"])
    final = progress[-1] if progress else None
    exposure = build_exposure_snapshot(
        dict(word_video_counts), dict(kanji_video_counts),
        dict(word_raw_counts), dict(kanji_raw_counts),
        seen_words, joyo_set, kanji_jlpt_sets, jlpt_sets,
    )
    learning_values = summarize_learning_values(per_lesson)
    # Full search index only on the global path (dashboard primary corpus).
    # Independent paths would largely duplicate it and bloat the JSON.
    search_index = None
    if path_id == "channel_global":
        search_index = build_search_index(
            seen_words, dict(word_video_counts), word_latest_label, word_first_path,
            dict(kanji_video_counts), kanji_first_label, kanji_latest_label, kanji_first_path,
            dict(kanji_lessons), joyo_set, kanji_jlpt,
        )

    result = {
        "path_id": path_id,
        "name": path["name"],
        "role": path["role"],
        "lessons_in_path": len(lessons),
        "final": final,
        "exposure": exposure,
        "learning_values": learning_values,
        "milestones": milestones,
        "milestone_statements": milestone_statements(milestones),
        "progress": progress,
        "per_lesson": per_lesson,
        "reference_sizes": {
            "jlpt_words": jlpt_sizes,
            "joyo_kanji": joyo_size,
            "jlpt_kanji": {lv: len(kanji_jlpt_sets[lv]) for lv in kanji_jlpt_sets},
            "frequency_bands": FREQ_BANDS,
        },
    }
    if search_index is not None:
        result["search_index"] = search_index
    return result


def compute_milestones(progress: list[dict], path_name: str) -> dict:
    """First lesson where each threshold is reached for each metric."""
    metrics = {}

    def track(key: str, display: str, getter):
        hits = {}
        for thr in THRESHOLDS:
            for snap in progress:
                if getter(snap) >= thr:
                    hits[str(thr)] = {
                        "threshold_percent": thr,
                        "after_lesson_label": snap["after_lesson_label"],
                        "after_lesson_id": snap["after_lesson_id"],
                        "after_order": snap["after_order"],
                        "actual_percent": getter(snap),
                        "path_name": path_name,
                    }
                    break
            else:
                hits[str(thr)] = None  # not yet reached
        metrics[key] = {"display": display, "thresholds": hits}

    for lv in ["N5", "N4", "N3", "N2", "N1"]:
        track(
            f"jlpt_{lv.lower()}_words",
            f"JLPT {lv}",
            lambda s, lv=lv: s["jlpt_word_coverage"][lv]["percent"],
        )
    for band in FREQ_BANDS:
        track(
            f"spoken_top_{band}",
            f"Top {band} spoken",
            lambda s, band=band: s["spoken_frequency_coverage"][f"top_{band}"]["percent"],
        )
    track("joyo_kanji", "Joyo Kanji", lambda s: s["joyo_coverage"]["percent"])
    for lv in ["N5", "N4", "N3", "N2", "N1"]:
        track(
            f"jlpt_{lv.lower()}_kanji",
            f"JLPT {lv} Kanji",
            lambda s, lv=lv: s["jlpt_kanji_coverage"][lv]["percent"],
        )
    return metrics


def milestone_statements(milestones: dict) -> list[str]:
    statements = []
    # Prefer the headline metrics the user asked for
    order = (
        [f"jlpt_n{n}_words" for n in (5, 4, 3, 2, 1)]
        + [f"spoken_top_{b}" for b in FREQ_BANDS]
        + ["joyo_kanji"]
        + [f"jlpt_n{n}_kanji" for n in (5, 4, 3, 2, 1)]
    )
    for key in order:
        meta = milestones.get(key)
        if not meta:
            continue
        for thr in THRESHOLDS:
            hit = meta["thresholds"].get(str(thr))
            if hit:
                statements.append(
                    f"{thr}% of {meta['display']} reached after {hit['after_lesson_label']}."
                )
    return statements


# --------------------------------------------------------------------------
# Report + main
# --------------------------------------------------------------------------

def write_report(results: dict, path: Path) -> None:
    lines: list[str] = []
    a = lines.append
    a("# KML Channel Learning Analytics")
    a("")
    a(f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}. "
      f"Regenerated by `analyze_channel_learning.py` — do not edit by hand._")
    a("")
    a("This report measures **educational progression** from the learner's "
      "perspective: cumulative unique vocabulary and kanji after every video, "
      "with coverage of JLPT word lists, Joyo kanji, spoken-frequency bands, "
      "and **exposure depth** (how many times each item was seen).")
    a("")

    summary = results["summary"]
    a("## Channel summary")
    a("")
    a("| Metric | Value |")
    a("|---|---|")
    a(f"| Independent learning paths | {summary['independent_paths']} |")
    a(f"| Videos in global path | {summary['global_videos']} |")
    a(f"| Unique vocabulary (global) | {summary['global_unique_vocabulary']} |")
    a(f"| Unique kanji (global) | {summary['global_unique_kanji']} |")
    a(f"| Joyo coverage (global) | {summary['global_joyo_percent']}% |")
    if summary.get("joyo_at_least_3_percent") is not None:
        a(f"| Joyo encountered ≥3 times | {summary['joyo_at_least_3_percent']}% |")
    if summary.get("vocab_multiple_contexts") is not None:
        a(f"| Vocabulary in multiple contexts | {summary['vocab_multiple_contexts']} |")
    a("")

    global_path = results["paths"].get("channel_global", {})
    exposure = global_path.get("exposure") or {}
    learning_values = global_path.get("learning_values") or {}

    if learning_values:
        a("## Learning value per video (global path)")
        a("")
        a("Stars measure **magnitude of learning activity** in that video "
          "(new + reinforced items), not a competitive ranking. Roles describe "
          "whether a lesson primarily introduces or consolidates.")
        a("")
        a("| Role | Videos |")
        a("|---|---|")
        for role_id, count in sorted((learning_values.get("role_counts") or {}).items()):
            a(f"| {role_id} | {count} |")
        a("")
        a(f"Average total learning value per video: "
          f"**{learning_values.get('average_total_learning_value')}** "
          f"(new {learning_values.get('average_new')}, "
          f"reinforced {learning_values.get('average_reinforced')}).")
        a("")
        a("### Comparison examples")
        a("")
        a("| Lesson | New | Reinforced | Total | Value | Role |")
        a("|---|---|---|---|---|---|")
        # Show mix: top introducers, consolidators, and a few spoken-vocab samples
        shown = set()
        samples = []
        for group in ("top_introduction_lessons", "top_consolidation_lessons",
                      "top_balanced_lessons", "highest_learning_value"):
            for row in learning_values.get(group) or []:
                key = row["label"]
                if key in shown:
                    continue
                shown.add(key)
                samples.append(row)
                if len(samples) >= 15:
                    break
            if len(samples) >= 15:
                break
        for row in samples:
            a(f"| {row['label']} | {row['new']} | {row['reinforced']} "
              f"| {row['total']} | {row['stars']} | {row['role']} |")
        a("")
        a("### Full per-video table (global path)")
        a("")
        a("| Lesson | New kanji | Reinforced kanji | New vocab | Reinforced vocab "
          "| New | Reinforced | Total | Stars | Role | JLPT gain | Spoken top-1000 gain |")
        a("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for L in global_path.get("per_lesson") or []:
            lv = L.get("learning_value") or {}
            a(
                f"| {L['label']} "
                f"| {lv.get('new_kanji', 0)} | {lv.get('reinforced_kanji', 0)} "
                f"| {lv.get('new_vocabulary', 0)} | {lv.get('reinforced_vocabulary', 0)} "
                f"| {lv.get('new_total', 0)} | {lv.get('reinforced_total', 0)} "
                f"| {lv.get('total_learning_value', 0)} | {lv.get('stars', '')} "
                f"| {(lv.get('educational_role') or {}).get('label', '')} "
                f"| {(lv.get('jlpt_gain') or {}).get('combined', 0)} "
                f"| {(lv.get('spoken_frequency_gain') or {}).get('headline_top_1000', 0)} |"
            )
        a("")

    a("## Exposure depth (global path)")
    a("")
    a("An **encounter** is one distinct video in which the item appears "
      "(repetitions inside the same video still count as one encounter).")
    a("")
    a("| Exposure | Meaning |")
    a("|---|---|")
    for band in EXPOSURE_BANDS:
        a(f"| {band['meaning']} | {band['label']} |")
    a("")

    if exposure:
        a("### Exposure statements")
        a("")
        for stmt in exposure.get("statements") or []:
            a(f"- {stmt}")
        a("")

        vb = (exposure.get("vocabulary") or {}).get("bands") or {}
        a("### Vocabulary exposure bands")
        a("")
        a("| Stage | Meaning | Items | % of seen vocab |")
        a("|---|---|---|---|")
        for band in EXPOSURE_BANDS:
            b = vb.get(band["id"]) or {}
            a(f"| {band['label']} | {band['meaning']} | {b.get('count', 0)} "
              f"| {b.get('percent', 0)}% |")
        a("")

        jb = (exposure.get("joyo") or {}).get("bands") or {}
        a("### Joyo kanji exposure bands")
        a("")
        a("| Stage | Meaning | Characters | % of Joyo |")
        a("|---|---|---|---|")
        for band in EXPOSURE_BANDS:
            b = jb.get(band["id"]) or {}
            a(f"| {band['label']} | {band['meaning']} | {b.get('count', 0)} "
              f"| {b.get('percent', 0)}% |")
        unseen = jb.get("unseen") or {}
        if unseen:
            a(f"| Unseen | Never encountered | {unseen.get('count', 0)} "
              f"| {unseen.get('percent', 0)}% |")
        a("")

        a("### Average encounters by JLPT kanji level")
        a("")
        a("| Level | Seen | Cohort | Avg among seen | Avg across cohort |")
        a("|---|---|---|---|---|")
        for lv in ["N5", "N4", "N3", "N2", "N1"]:
            e = (exposure.get("jlpt_kanji") or {}).get(lv) or {}
            a(f"| {lv} | {e.get('encountered', 0)} | {e.get('cohort_size', 0)} "
              f"| {e.get('average_encounters_among_seen')} "
              f"| {e.get('average_encounters_across_cohort')} |")
        a("")

    a("## Milestone reports")
    a("")
    a("Thresholds: " + ", ".join(f"{t}%" for t in THRESHOLDS) + ".")
    a("")

    a("### Complete channel (global learning path)")
    a("")
    for stmt in global_path.get("milestone_statements", []):
        a(f"- {stmt}")
    if not global_path.get("milestone_statements"):
        a("_No coverage thresholds reached yet on the global path._")
    a("")

    a("### Per-path milestone highlights")
    a("")
    for pid, pdata in results["paths"].items():
        if pid == "channel_global":
            continue
        stmts = pdata.get("milestone_statements") or []
        highlights = [s for s in stmts if any(f"{t}% of" in s for t in (50, 75, 90, 95, 100))]
        if not highlights:
            continue
        a(f"#### {pdata['name']}")
        a("")
        for s in highlights:
            a(f"- {s}")
        a("")

    a("## Path inventory")
    a("")
    a("| Path | Role | Lessons | Unique words | Unique kanji | Joyo % | N5 words % | Top 1000 spoken % |")
    a("|---|---|---|---|---|---|---|---|")
    for pid, pdata in results["paths"].items():
        f = pdata.get("final") or {}
        a(
            f"| {pdata['name']} | {pdata['role']} | {pdata['lessons_in_path']} "
            f"| {f.get('unique_vocabulary', 0)} | {f.get('unique_kanji', 0)} "
            f"| {(f.get('joyo_coverage') or {}).get('percent', 0)} "
            f"| {((f.get('jlpt_word_coverage') or {}).get('N5') or {}).get('percent', 0)} "
            f"| {((f.get('spoken_frequency_coverage') or {}).get('top_1000') or {}).get('percent', 0)} |"
        )
    a("")

    a("## Methodology")
    a("")
    a("- Each playlist is an independent cumulative path.")
    a("- The global path follows educational order: Grade 1–6 kanji → "
      "post-elementary kanji → grade compounds → post-elementary compounds → "
      "Japanese Vocabulary → Foundations.")
    a("- JLPT word coverage = unique curriculum words present in that level's "
      "word list ÷ list size.")
    a("- Spoken-frequency coverage uses OpenSubtitles 2018 Japanese lemmas "
      "(UniDic), band size as denominator.")
    a("- Joyo coverage = unique joyo kanji introduced ÷ 2,136.")
    a("- Exposure / encounter = distinct videos containing the item "
      "(one count per video).")
    a("- Learning value per video = new items + reinforced items "
      "(kanji + vocabulary). Stars are magnitude bands, not rankings. "
      "JLPT / spoken gains are coverage deltas caused by that video.")
    a("- Review opportunities: items introduced ≥ "
      f"{REVIEW_GAP} lessons ago that have not reappeared.")
    a("")
    a("---")
    a("")
    a("Machine-readable curves and per-video snapshots: "
      "`kml/analytics/output/kml_channel_learning.json`.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not OUTPUT_DIR.resolve().is_relative_to(ANALYTICS_DIR):
        sys.exit("Refusing to write outside kml/analytics/ — check output_dir.")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Discovering learning paths…")
    paths = build_paths()
    print(f"  {len(paths)} paths "
          f"({sum(len(p['lessons']) for p in paths.values())} lesson slots incl. global)")

    print("Loading reference data…")
    jlpt_sets = load_jlpt_sets()
    freq_ranks = load_frequency()
    joyo = load_joyo()
    kanji_jlpt = load_kanji_jlpt()
    master = load_master_vocabulary()

    results_paths = {}
    for pid, path in paths.items():
        print(f"  analyzing {pid} ({len(path['lessons'])} videos)…")
        results_paths[pid] = analyze_path(
            pid, path, jlpt_sets, freq_ranks, joyo, kanji_jlpt, master,
        )

    global_final = (results_paths.get("channel_global") or {}).get("final") or {}
    global_exposure = (results_paths.get("channel_global") or {}).get("exposure") or {}
    joyo_depth = ((global_exposure.get("joyo") or {}).get("depth") or {})
    summary = {
        "independent_paths": len(paths) - (1 if "channel_global" in paths else 0),
        "global_videos": len((paths.get("channel_global") or {}).get("lessons") or []),
        "global_unique_vocabulary": global_final.get("unique_vocabulary", 0),
        "global_unique_kanji": global_final.get("unique_kanji", 0),
        "global_joyo_percent": (global_final.get("joyo_coverage") or {}).get("percent", 0),
        "joyo_at_least_3_percent": (joyo_depth.get("at_least_3") or {}).get("percent"),
        "vocab_multiple_contexts": (global_exposure.get("vocabulary") or {}).get("multiple_contexts"),
        "coverage_thresholds": THRESHOLDS,
        "frequency_bands": FREQ_BANDS,
        "exposure_bands": EXPOSURE_BANDS,
    }

    output = {
        "schema": "kml.analytics.channel_learning",
        "schema_version": 4,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "kml/analytics/scripts/analyze_channel_learning.py",
        "note": "Generated analytics. Never edit by hand; regenerate by rerunning.",
        "summary": summary,
        "paths": results_paths,
    }

    out_json = OUTPUT_DIR / CHANNEL_CFG.get("output_json", "kml_channel_learning.json")
    out_md = OUTPUT_DIR / CHANNEL_CFG.get("output_report", "CHANNEL_LEARNING_REPORT.md")
    out_json.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(output, out_md)

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(f"Global: {summary['global_unique_vocabulary']} words, "
          f"{summary['global_unique_kanji']} kanji, "
          f"{summary['global_joyo_percent']}% joyo")
    if summary.get("joyo_at_least_3_percent") is not None:
        print(f"  Joyo ≥3 encounters: {summary['joyo_at_least_3_percent']}%")
    if summary.get("vocab_multiple_contexts") is not None:
        print(f"  Vocab multi-context: {summary['vocab_multiple_contexts']}")
    ge = global_exposure
    if ge:
        for stmt in (ge.get("statements") or [])[:8]:
            print("  ·", stmt)

if __name__ == "__main__":
    main()
