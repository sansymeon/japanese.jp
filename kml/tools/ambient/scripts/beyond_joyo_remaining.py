#!/usr/bin/env python3
"""Generate Beyond Jōyō compounds for parts 5+ from remaining master-list kanji.

Party-kanji rewards are scattered through the full series (parts 2, 4, 6… plus a
few early odds) by assemble_series_entries() in build_beyond_joyo_compounds.py.
𰻞 (biáng) remains the absolute last entry (series finale).
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
MASTER_CSV = REPO / "data" / "kanji" / "kanji_master.csv"

# Mid-series party rewards (order = presentation order across reward parts).
# 𰻞 is reserved for the finale — not listed here.
PARTY_REWARDS: list[dict[str, Any]] = [
    {
        "anchor": "轟音",
        "reading": "ごうおん",
        "en": "rumble / roar",
        "ruby": [("轟", "ごう"), ("音", "おん")],
        "masterKanji": ["轟"],
        "reward": True,
    },
    {
        "anchor": "鑫",
        "reading": "キン",
        "en": "three golds — party kanji",
        "ruby": [("鑫", "キン")],
        "masterKanji": ["鑫"],
        "reward": True,
    },
    {
        "anchor": "焱",
        "reading": "エン",
        "en": "three fires — party kanji",
        "ruby": [("焱", "エン")],
        "masterKanji": ["焱"],
        "reward": True,
    },
    {
        "anchor": "淼",
        "reading": "ビョウ",
        "en": "three waters — party kanji",
        "ruby": [("淼", "ビョウ")],
        "masterKanji": ["淼"],
        "reward": True,
    },
    {
        "anchor": "犇",
        "reading": "ホン",
        "en": "three oxen — party kanji",
        "ruby": [("犇", "ホン")],
        "masterKanji": ["犇"],
        "reward": True,
    },
    {
        "anchor": "鱻",
        "reading": "セン",
        "en": "three fish — party kanji",
        "ruby": [("鱻", "セン")],
        "masterKanji": ["鱻"],
        "reward": True,
    },
    {
        "anchor": "靐",
        "reading": "ホウ",
        "en": "three thunders — party kanji",
        "ruby": [("靐", "ホウ")],
        "masterKanji": ["靐"],
        "reward": True,
    },
    {
        "anchor": "麤",
        "reading": "ソ",
        "en": "three deer — party kanji",
        "ruby": [("麤", "ソ")],
        "masterKanji": ["麤"],
        "reward": True,
    },
    {
        "anchor": "毳",
        "reading": "ゼイ",
        "en": "three furs — party kanji",
        "ruby": [("毳", "ゼイ")],
        "masterKanji": ["毳"],
        "reward": True,
    },
    {
        "anchor": "垚",
        "reading": "ヨウ",
        "en": "three earths — party kanji",
        "ruby": [("垚", "ヨウ")],
        "masterKanji": ["垚"],
        "reward": True,
    },
    {
        "anchor": "猋",
        "reading": "ヒョウ",
        "en": "three dogs — party kanji",
        "ruby": [("猋", "ヒョウ")],
        "masterKanji": ["猋"],
        "reward": True,
    },
    {
        "anchor": "龘",
        "reading": "トウ",
        "en": "three dragons — party kanji",
        "ruby": [("龘", "トウ")],
        "masterKanji": ["龘"],
        "reward": True,
    },
]

BIANG_FINALE: dict[str, Any] = {
    "anchor": "𰻞",
    "reading": "ビャンビャン",
    "en": "biáng — biáng biáng noodles",
    "ruby": [("𰻞", "ビャンビャン")],
    "masterKanji": ["𰻞"],
    "reward": True,
    "celebration": "fireworks",
    "finale": True,
}

# Scatter rewards through the series: even parts 2…18, plus early odds 3/5/7
# so all twelve party glyphs appear (not clustered only near the end).
PARTY_REWARD_PARTS: list[int] = [2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18]

PART_SIZE = 50


def load_master_rows() -> list[dict]:
    with MASTER_CSV.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_remaining_entries(used_master: set[str]) -> list[dict[str, Any]]:
    """Return remaining regular compounds only (no party rewards, no biáng)."""
    rows = load_master_rows()
    corpus: set[str] = set()
    joyo: set[str] = set()
    by: dict[str, dict] = {}
    for r in rows:
        by[r["kanji"]] = r
        if r.get("category") == "joyo":
            joyo.add(r["kanji"])
        if (r.get("grade") == "H") or r.get("category") in {
            "heisig_extra",
            "party_kanji",
        }:
            corpus.add(r["kanji"])

    party_ids = {m for e in PARTY_REWARDS for m in e["masterKanji"]}
    party_ids.add("𰻞")

    remain_rows: list[dict] = []
    seen: set[str] = set()
    for r in rows:
        k = r["kanji"]
        if k in seen or k in used_master or k in party_ids:
            continue
        if k not in corpus:
            continue
        if r.get("category") == "party_kanji":
            continue
        seen.add(k)
        remain_rows.append(r)

    # Familiarity-ish: frequency rank ascending
    remain_rows.sort(key=lambda r: int(r.get("frequency_rank") or 99999))

    regular: list[dict[str, Any]] = []
    for r in remain_rows:
        entry = _auto_entry(r)
        # Skip curated that fail validation (e.g. missing partner kanji)
        if not _validate_entry(entry, corpus | party_ids, joyo):
            # Fallback to safe auto without curated
            kanji = r["kanji"]
            if kanji in CURATED:
                kun = _parse_kun(r)
                en = _keyword_en(r)
                on = _first_on(r)
                if kun:
                    surface, reading = kun
                    okuri = surface[len(kanji) :] if surface != kanji else ""
                    stem = reading[: len(reading) - len(okuri)] if okuri else reading
                    entry = {
                        "anchor": surface,
                        "reading": reading,
                        "en": en,
                        "ruby": [(kanji, stem)] + ([(okuri, "")] if okuri else []),
                        "masterKanji": [kanji],
                    }
                else:
                    entry = {
                        "anchor": kanji,
                        "reading": on or en,
                        "en": en,
                        "ruby": [(kanji, on)] if on else [(kanji, "")],
                        "masterKanji": [kanji],
                    }
        if not _validate_entry(entry, corpus | party_ids, joyo):
            raise SystemExit(f"Cannot build entry for {r['kanji']}")
        regular.append(entry)

    return regular


def assemble_series_entries(
    curated: list[dict[str, Any]],
    remaining_regular: list[dict[str, Any]],
    *,
    reward_parts: list[int] | None = None,
    rewards: list[dict[str, Any]] | None = None,
    finale: dict[str, Any] | None = None,
    part_size: int = PART_SIZE,
) -> list[dict[str, Any]]:
    """Merge curated + remaining, inject party rewards on chosen parts, append biáng."""
    reward_parts = list(reward_parts or PARTY_REWARD_PARTS)
    rewards = list(rewards if rewards is not None else PARTY_REWARDS)
    finale = dict(finale if finale is not None else BIANG_FINALE)

    if len(reward_parts) != len(rewards):
        raise SystemExit(
            f"reward_parts ({len(reward_parts)}) must match rewards ({len(rewards)})"
        )

    regular = list(curated) + list(remaining_regular)
    reward_at = {part: rewards[i] for i, part in enumerate(reward_parts)}

    out: list[dict[str, Any]] = []
    ri = 0
    part = 1
    # Fill complete parts until regular is exhausted enough for finale padding.
    # Final part is assembled after the loop with leftover regular + biáng.
    while True:
        remaining_regular_n = len(regular) - ri
        # Stop when leftover regular fits in a short finale part (with biáng).
        # Keep going while we still owe reward parts or have a full part of regulars.
        needs_reward = part in reward_at
        if not needs_reward and remaining_regular_n <= part_size - 1:
            break
        if needs_reward:
            take = part_size - 1
            chunk = regular[ri : ri + take]
            if len(chunk) < take:
                raise SystemExit(
                    f"Part {part}: need {take} regulars for reward slot, have {len(chunk)}"
                )
            ri += take
            out.extend(chunk)
            out.append(dict(reward_at[part]))
        else:
            take = part_size
            chunk = regular[ri : ri + take]
            if len(chunk) < take:
                break
            ri += take
            out.extend(chunk)
        part += 1

    leftover = regular[ri:]
    out.extend(leftover)
    out.append(finale)
    return out


# High-value remaining compounds (kanji → entry). Prefer these over auto fallback.
CURATED: dict[str, dict[str, Any]] = {
    "伊": {"anchor": "伊達", "reading": "だて", "en": "dandy / Date", "ruby": [("伊", "だ"), ("達", "て")], "masterKanji": ["伊"]},
    "之": {"anchor": "之", "reading": "これ", "en": "this / of (classical)", "ruby": [("之", "これ")], "masterKanji": ["之"]},
    "彦": {"anchor": "彦", "reading": "ひこ", "en": "handsome man / -hiko", "ruby": [("彦", "ひこ")], "masterKanji": ["彦"]},
    "也": {"anchor": "也", "reading": "なり", "en": "also / classical copula", "ruby": [("也", "なり")], "masterKanji": ["也"]},
    "弘": {"anchor": "弘い", "reading": "ひろい", "en": "vast", "ruby": [("弘", "ひろ"), ("い", "")], "masterKanji": ["弘"]},
    "阿": {"anchor": "阿部", "reading": "あべ", "en": "Abe", "ruby": [("阿", "あ"), ("部", "べ")], "masterKanji": ["阿"]},
    "浩": {"anchor": "浩然", "reading": "こうぜん", "en": "vast / abundant spirit", "ruby": [("浩", "こう"), ("然", "ぜん")], "masterKanji": ["浩"]},
    "乃": {"anchor": "乃木", "reading": "のぎ", "en": "Nogi", "ruby": [("乃", "の"), ("木", "ぎ")], "masterKanji": ["乃"]},
    "昌": {"anchor": "昌盛", "reading": "しょうせい", "en": "prosperity", "ruby": [("昌", "しょう"), ("盛", "せい")], "masterKanji": ["昌"]},
    "宏": {"anchor": "宏大", "reading": "こうだい", "en": "grand / vast", "ruby": [("宏", "こう"), ("大", "だい")], "masterKanji": ["宏"]},
    "祐": {"anchor": "神祐", "reading": "しんゆう", "en": "divine aid", "ruby": [("神", "しん"), ("祐", "ゆう")], "masterKanji": ["祐"]},
    "嘉": {"anchor": "嘉日", "reading": "かじつ", "en": "auspicious day", "ruby": [("嘉", "か"), ("日", "じつ")], "masterKanji": ["嘉"]},
    "幡": {"anchor": "旗幡", "reading": "きはん", "en": "banners / flags", "ruby": [("旗", "き"), ("幡", "はん")], "masterKanji": ["幡"]},
    "輔": {"anchor": "輔佐", "reading": "ほさ", "en": "assistance / aide", "ruby": [("輔", "ほ"), ("佐", "さ")], "masterKanji": ["輔"]},
    "庄": {"anchor": "庄屋", "reading": "しょうや", "en": "village headman", "ruby": [("庄", "しょう"), ("屋", "や")], "masterKanji": ["庄"]},
    "筑": {"anchor": "筑波", "reading": "つくば", "en": "Tsukuba", "ruby": [("筑", "つく"), ("波", "ば")], "masterKanji": ["筑"]},
    "嶋": {"anchor": "嶋", "reading": "しま", "en": "island (variant)", "ruby": [("嶋", "しま")], "masterKanji": ["嶋"]},
    "菅": {"anchor": "菅", "reading": "すげ", "en": "sedge", "ruby": [("菅", "すげ")], "masterKanji": ["菅"]},
    "淳": {"anchor": "淳朴", "reading": "じゅんぼく", "en": "simple honesty", "ruby": [("淳", "じゅん"), ("朴", "ぼく")], "masterKanji": ["淳"]},
    "亮": {"anchor": "亮々", "reading": "りょうりょう", "en": "clear / distinct", "ruby": [("亮", "りょう"), ("々", "りょう")], "masterKanji": ["亮"]},
    "哉": {"anchor": "哉", "reading": "かな", "en": "alas (particle)", "ruby": [("哉", "かな")], "masterKanji": ["哉"]},
    "辰": {"anchor": "辰", "reading": "たつ", "en": "dragon (zodiac)", "ruby": [("辰", "たつ")], "masterKanji": ["辰"]},
    "劉": {"anchor": "劉", "reading": "りゅう", "en": "Liu", "ruby": [("劉", "りゅう")], "masterKanji": ["劉"]},
    "圭": {"anchor": "圭角", "reading": "けいかく", "en": "sharp edges / angularity", "ruby": [("圭", "けい"), ("角", "かく")], "masterKanji": ["圭"]},
    "斐": {"anchor": "斐然", "reading": "ひぜん", "en": "brilliant / striking", "ruby": [("斐", "ひ"), ("然", "ぜん")], "masterKanji": ["斐"]},
    "晋": {"anchor": "晋", "reading": "しん", "en": "Jin / advance", "ruby": [("晋", "しん")], "masterKanji": ["晋"]},
    "敦": {"anchor": "敦厚", "reading": "とんこう", "en": "sincere / warm-hearted", "ruby": [("敦", "とん"), ("厚", "こう")], "masterKanji": ["敦"]},
    "晃": {"anchor": "晃々", "reading": "こうこう", "en": "brilliantly clear", "ruby": [("晃", "こう"), ("々", "こう")], "masterKanji": ["晃"]},
    "槻": {"anchor": "槻", "reading": "つき", "en": "zelkova", "ruby": [("槻", "つき")], "masterKanji": ["槻"]},
    "秦": {"anchor": "秦", "reading": "しん", "en": "Qin", "ruby": [("秦", "しん")], "masterKanji": ["秦"]},
    "靖": {"anchor": "靖国", "reading": "やすくに", "en": "Yasukuni", "ruby": [("靖", "やす"), ("国", "くに")], "masterKanji": ["靖"]},
    "玲": {"anchor": "玲", "reading": "れい", "en": "tinkling (jewel)", "ruby": [("玲", "れい")], "masterKanji": ["玲"]},
    "宋": {"anchor": "宋", "reading": "そう", "en": "Song dynasty", "ruby": [("宋", "そう")], "masterKanji": ["宋"]},
    "莉": {"anchor": "莉", "reading": "り", "en": "jasmine (in names)", "ruby": [("莉", "り")], "masterKanji": ["莉"]},
    "巳": {"anchor": "巳", "reading": "み", "en": "snake (zodiac)", "ruby": [("巳", "み")], "masterKanji": ["巳"]},
    "佑": {"anchor": "天佑", "reading": "てんゆう", "en": "heavenly aid", "ruby": [("天", "てん"), ("佑", "ゆう")], "masterKanji": ["佑"]},
    "梶": {"anchor": "梶", "reading": "かじ", "en": "oar / helm", "ruby": [("梶", "かじ")], "masterKanji": ["梶"]},
    "郁": {"anchor": "郁郁", "reading": "いくいく", "en": "fragrant / cultured", "ruby": [("郁", "いく"), ("郁", "いく")], "masterKanji": ["郁"]},
    "帖": {"anchor": "画帖", "reading": "がじょう", "en": "picture album", "ruby": [("画", "が"), ("帖", "じょう")], "masterKanji": ["帖"]},
    "牝": {"anchor": "牝", "reading": "めす", "en": "female (animal)", "ruby": [("牝", "めす")], "masterKanji": ["牝"]},
    "邑": {"anchor": "邑", "reading": "むら", "en": "village / settlement", "ruby": [("邑", "むら")], "masterKanji": ["邑"]},
    "渕": {"anchor": "渕", "reading": "ふち", "en": "abyss (variant)", "ruby": [("渕", "ふち")], "masterKanji": ["渕"]},
    "遼": {"anchor": "遼遠", "reading": "りょうえん", "en": "faraway", "ruby": [("遼", "りょう"), ("遠", "えん")], "masterKanji": ["遼"]},
    "喰": {"anchor": "喰う", "reading": "くう", "en": "to eat (vulgar)", "ruby": [("喰", "く"), ("う", "")], "masterKanji": ["喰"]},
    "峯": {"anchor": "峯", "reading": "みね", "en": "peak (variant)", "ruby": [("峯", "みね")], "masterKanji": ["峯"]},
    "耶": {"anchor": "耶", "reading": "や", "en": "exclamation (classical)", "ruby": [("耶", "や")], "masterKanji": ["耶"]},
    "箕": {"anchor": "箕", "reading": "み", "en": "winnowing basket", "ruby": [("箕", "み")], "masterKanji": ["箕"]},
    "栖": {"anchor": "栖", "reading": "すみか", "en": "dwelling", "ruby": [("栖", "すみか")], "masterKanji": ["栖"]},
    "纂": {"anchor": "編纂", "reading": "へんさん", "en": "compilation / editing", "ruby": [("編", "へん"), ("纂", "さん")], "masterKanji": ["纂"]},
    "黎": {"anchor": "黎明", "reading": "れいめい", "en": "dawn", "ruby": [("黎", "れい"), ("明", "めい")], "masterKanji": ["黎"]},
    "寅": {"anchor": "寅", "reading": "とら", "en": "tiger (zodiac)", "ruby": [("寅", "とら")], "masterKanji": ["寅"]},
    "亘": {"anchor": "亘る", "reading": "わたる", "en": "to span / extend across", "ruby": [("亘", "わた"), ("る", "")], "masterKanji": ["亘"]},
    "鴻": {"anchor": "鴻", "reading": "おおとり", "en": "large goose", "ruby": [("鴻", "おおとり")], "masterKanji": ["鴻"]},
    "舘": {"anchor": "舘", "reading": "やかた", "en": "mansion (variant)", "ruby": [("舘", "やかた")], "masterKanji": ["舘"]},
    "胤": {"anchor": "皇胤", "reading": "こういん", "en": "imperial descendant", "ruby": [("皇", "こう"), ("胤", "いん")], "masterKanji": ["胤"]},
    "鄭": {"anchor": "鄭重", "reading": "ていちょう", "en": "courteous / careful", "ruby": [("鄭", "てい"), ("重", "ちょう")], "masterKanji": ["鄭"]},
    "迦": {"anchor": "釈迦", "reading": "しゃか", "en": "Shakyamuni / Buddha", "ruby": [("釈", "しゃ"), ("迦", "か")], "masterKanji": ["迦"]},
    "丞": {"anchor": "丞相", "reading": "じょうしょう", "en": "chancellor", "ruby": [("丞", "じょう"), ("相", "しょう")], "masterKanji": ["丞"]},
    "爾": {"anchor": "爾", "reading": "なんじ", "en": "thou (classical)", "ruby": [("爾", "なんじ")], "masterKanji": ["爾"]},
    "狗": {"anchor": "天狗", "reading": "てんぐ", "en": "tengu", "ruby": [("天", "てん"), ("狗", "ぐ")], "masterKanji": ["狗"]},
    "腔": {"anchor": "口腔", "reading": "こうくう", "en": "oral cavity", "ruby": [("口", "こう"), ("腔", "くう")], "masterKanji": ["腔"]},
    "惹": {"anchor": "惹く", "reading": "ひく", "en": "to attract", "ruby": [("惹", "ひ"), ("く", "")], "masterKanji": ["惹"]},
    "廟": {"anchor": "廟", "reading": "びょう", "en": "mausoleum / shrine", "ruby": [("廟", "びょう")], "masterKanji": ["廟"]},
    "汐": {"anchor": "汐", "reading": "しお", "en": "tide / eventide", "ruby": [("汐", "しお")], "masterKanji": ["汐"]},
    "稔": {"anchor": "稔る", "reading": "みのる", "en": "to bear fruit / ripen", "ruby": [("稔", "みの"), ("る", "")], "masterKanji": ["稔"]},
    "綬": {"anchor": "綬", "reading": "じゅ", "en": "ribbon / cord", "ruby": [("綬", "じゅ")], "masterKanji": ["綬"]},
    "撰": {"anchor": "撰ぶ", "reading": "えらぶ", "en": "to select (literary)", "ruby": [("撰", "えら"), ("ぶ", "")], "masterKanji": ["撰"]},
    "擢": {"anchor": "抜擢", "reading": "ばってき", "en": "selection / promotion", "ruby": [("抜", "ばっ"), ("擢", "てき")], "masterKanji": ["擢"]},
    "挺": {"anchor": "一挺", "reading": "いっちょう", "en": "one (gun/tool)", "ruby": [("一", "いっ"), ("挺", "ちょう")], "masterKanji": ["挺"]},
}


def _keyword_en(row: dict) -> str:
    kw = (row.get("display_keyword") or row.get("keyword") or row.get("slug") or "").strip()
    return kw.replace("_", " ")


def _first_on(row: dict) -> str:
    on = (row.get("on_reading") or "").strip()
    if not on:
        return ""
    # Prefer first katakana chunk
    parts = re.split(r"[、,\s/]+", on)
    return parts[0] if parts else on


def _parse_kun(row: dict) -> tuple[str, str] | None:
    """Return (surface_with_okurigana, full_reading) or None."""
    raw = (row.get("kun_readings") or "").strip()
    if not raw:
        return None
    # Take first reading; forms like ひろ-い or わた-る or かさ
    first = re.split(r"[、,\s/]+", raw)[0]
    if not first:
        return None
    kanji = row["kanji"]
    if "-" in first:
        stem, okuri = first.split("-", 1)
        return f"{kanji}{okuri}", f"{stem}{okuri}"
    if "." in first:
        stem, okuri = first.split(".", 1)
        return f"{kanji}{okuri}", f"{stem}{okuri}"
    return kanji, first


def _auto_entry(row: dict) -> dict[str, Any]:
    kanji = row["kanji"]
    if kanji in CURATED:
        entry = dict(CURATED[kanji])
        # Drop curated entries that reference missing partners later
        return entry

    kun = _parse_kun(row)
    en = _keyword_en(row)
    if kun:
        surface, reading = kun
        if surface == kanji:
            ruby = [(kanji, reading)]
        else:
            # kanji + okurigana
            okuri = surface[len(kanji) :]
            stem = reading[: len(reading) - len(okuri)] if okuri else reading
            ruby = [(kanji, stem)] + ([(okuri, "")] if okuri else [])
        return {
            "anchor": surface,
            "reading": reading,
            "en": en,
            "ruby": ruby,
            "masterKanji": [kanji],
        }

    on = _first_on(row)
    return {
        "anchor": kanji,
        "reading": on or en,
        "en": en,
        "ruby": [(kanji, on)] if on else [(kanji, "")],
        "masterKanji": [kanji],
    }


def _validate_entry(entry: dict[str, Any], corpus: set[str], joyo: set[str]) -> bool:
    for mk in entry["masterKanji"]:
        if mk not in corpus:
            return False
    for surf, _reading in entry["ruby"]:
        for ch in surf:
            if ch in {"々", "ゝ", "ゞ", "ヽ", "ヾ"}:
                continue
            # okurigana / kana
            if "\u3040" <= ch <= "\u30ff" or "\uff66" <= ch <= "\uff9d":
                continue
            if ch.isascii():
                continue
            if ch not in corpus and ch not in joyo:
                return False
    return True


if __name__ == "__main__":
    used: set[str] = set()
    remaining = build_remaining_entries(used)
    series = assemble_series_entries([], remaining)
    print(len(series), "entries")
    print(
        "rewards",
        sum(1 for e in series if e.get("reward") and not e.get("finale")),
    )
    print("finale", series[-1].get("celebration"), series[-1]["anchor"])
    for i, e in enumerate(series):
        if e.get("reward"):
            part = i // PART_SIZE + 1
            slot = i % PART_SIZE + 1
            print(f"  part {part:02d} slot {slot:02d}: {e['anchor']}")
