#!/usr/bin/env python3
"""
PASS 7 — Glossary foundation architecture (scaffolding only).

Builds glossary_family.csv from primitive_dictionary.v2 + v4 master.
Does NOT generate glossary pages or modify lessons.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
V2_DICT = BASE / "data/kanji/primitive_dictionary.v2.csv"
V4 = BASE / "data/kanji/kanji_master_with_components.v4.csv"
OUT_CSV = BASE / "data/kanji/glossary_family.csv"
OUT_REPORT = BASE / "data/kanji/glossary_architecture_report.txt"

FIELDNAMES = [
    "family_id",
    "display_name",
    "anchor_symbol",
    "status",
    "family_type",
    "notes",
    "example_kanji",
    "font_variation_risk",
    "glossary_priority",
]

# Foundation families — human-facing cognition hubs (override auto inference).
CURATED: dict[str, dict[str, str]] = {
    "曷": {
        "family_id": "siesta_family",
        "display_name": "Siesta Family",
        "status": "stable",
        "family_type": "visual_family",
        "font_variation_risk": "font-sensitive",
        "glossary_priority": "high",
        "example_kanji": "渇|喝|褐|謁|葛|掲|靄",
        "notes": "pass7 foundation; siesta/sun-hat visual identity; variation-tolerant",
    },
    "啇": {
        "family_id": "merchant_family",
        "display_name": "Merchant Family",
        "status": "stable",
        "family_type": "phonetic_family",
        "font_variation_risk": "stable-form",
        "glossary_priority": "high",
        "notes": "pass7 foundation; phonetic merchant core; click hub for 嫡/滴/適 cluster",
    },
    "商": {
        "family_id": "deal_family",
        "display_name": "Deal Family",
        "status": "stable",
        "family_type": "visual_family",
        "font_variation_risk": "stable-form",
        "glossary_priority": "high",
        "example_kanji": "商|嫡|滴|適|敵",
        "notes": "pass7 foundation; lesson-facing wrapper hub (嫡→商-family navigation)",
    },
    "袁": {
        "family_id": "robe_family",
        "display_name": "Robe Family",
        "status": "stable",
        "family_type": "visual_family",
        "font_variation_risk": "stable-form",
        "glossary_priority": "high",
        "example_kanji": "遠|園|猿|袁",
        "notes": "pass7 foundation; hidden reusable robe-family anchor (L22)",
    },
    "竟": {
        "family_id": "competition_family",
        "display_name": "Competition Family",
        "status": "experimental",
        "family_type": "visual_repeat",
        "font_variation_risk": "font-sensitive",
        "glossary_priority": "medium",
        "example_kanji": "競|鏡|境|竟",
        "notes": "pass7 foundation; stand+fin visual repeat; review visual mutation",
    },
    "戈": {
        "family_id": "spear_family",
        "display_name": "Spear Family",
        "status": "stable",
        "family_type": "hidden_reusable",
        "font_variation_risk": "stable-form",
        "glossary_priority": "high",
        "notes": "pass7 foundation; weapon-family anchor (L19 hidden reusable)",
    },
    "俞": {
        "family_id": "meeting_family",
        "display_name": "Meeting Family",
        "status": "stable",
        "family_type": "hidden_reusable",
        "font_variation_risk": "stable-form",
        "glossary_priority": "high",
        "notes": "pass7 foundation; meeting-family anchor (L16 hidden reusable)",
    },
    "夂": {
        "family_id": "winter_family",
        "display_name": "Winter Family",
        "status": "stable",
        "family_type": "hidden_reusable",
        "font_variation_risk": "handwriting-shift",
        "glossary_priority": "medium",
        "notes": "pass7 foundation; winter/go-slow component; links 各/客/路 cluster",
    },
    "𧘇": {
        "family_id": "koromo_family",
        "display_name": "Koromo Family",
        "status": "stable",
        "family_type": "visual_family",
        "font_variation_risk": "font-sensitive",
        "glossary_priority": "high",
        "notes": "pass7 foundation; clothes-family primitive (L22); pairs with robe_family",
    },
    "衤": {
        "family_id": "clothes_family",
        "display_name": "Clothes Family",
        "status": "stable",
        "family_type": "structural_primitive",
        "font_variation_risk": "font-sensitive",
        "glossary_priority": "medium",
        "notes": "pass7 foundation; left-clothes radical; lesson vs glossary split",
    },
    "田｜": {
        "family_id": "fishpipe_family",
        "display_name": "Fishpipe Family",
        "status": "stable",
        "family_type": "structural_primitive",
        "font_variation_risk": "compressed-print",
        "glossary_priority": "medium",
        "notes": "pass7 foundation; 魚 internal pipe structure (L10 hidden)",
    },
}

# Extra font-risk hints (anchor → risk label).
FONT_RISK: dict[str, str] = {
    "書": "handwriting-shift",
    "飛": "compressed-print",
    "葛": "font-sensitive",
    "曷": "font-sensitive",
    "竟": "font-sensitive",
    "夂": "handwriting-shift",
    "𧘇": "font-sensitive",
    "衤": "font-sensitive",
    "聿": "handwriting-shift",
}

# Lesson-established cognition hubs promoted to glossary tier.
LESSON_HUBS: dict[str, str] = {
    "肖": "resemblance_family",
    "寺": "temple_family",
    "各": "each_family",
    "青": "blue_family",
    "尚": "esteem_family",
    "可": "can_family",
    "胡": "barbarian_family",
}

MIN_PHON_STABLE = 5
MIN_PHON_CANDIDATE = 3


@dataclass
class DictRow:
    symbol: str
    preferred_name: str
    status: str
    notes: str
    first_kanji: str

    @property
    def phon_count(self) -> int:
        m = re.search(r"phon_parents=(\d+)", self.notes)
        return int(m.group(1)) if m else 0

    @property
    def is_curated_hub(self) -> bool:
        return "curated_hub" in self.notes

    def sample_kanji(self) -> list[str]:
        m = re.search(r"sample=([^;]+)", self.notes)
        if not m:
            return []
        return [x.strip() for x in m.group(1).split(",") if x.strip()]


def title_family(family_id: str) -> str:
    return " ".join(w.capitalize() for w in family_id.replace("-", "_").split("_"))


def load_v2() -> list[DictRow]:
    rows: list[DictRow] = []
    with open(V2_DICT, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(
                DictRow(
                    symbol=(r.get("symbol") or "").strip(),
                    preferred_name=(r.get("preferred_name") or "").strip(),
                    status=(r.get("status") or "").strip(),
                    notes=(r.get("notes") or "").strip(),
                    first_kanji=(r.get("first_kanji") or "").strip(),
                )
            )
    return rows


def load_v4_token_index() -> dict[str, set[str]]:
    idx: dict[str, set[str]] = defaultdict(set)
    with open(V4, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            k = (row.get("kanji") or "").strip()
            prim = (row.get("kml_primitives") or "").strip()
            for t in prim.split("|"):
                t = t.strip()
                if t:
                    idx[t].add(k)
    return idx


def infer_family_id(row: DictRow) -> str:
    if row.preferred_name.endswith("_family"):
        return row.preferred_name
    if row.preferred_name:
        return f"{row.preferred_name}_family"
    return f"{row.symbol}_family"


def infer_display(row: DictRow, family_id: str) -> str:
    if row.preferred_name and not row.preferred_name.endswith("_family"):
        return title_family(f"{row.preferred_name}_family")
    return title_family(family_id)


def infer_type(row: DictRow) -> str:
    if row.status == "hidden_component":
        return "hidden_reusable"
    if row.status == "primitive_only":
        return "structural_primitive"
    if row.phon_count >= 3:
        return "phonetic_family"
    return "visual_family"


def infer_status(row: DictRow) -> str:
    if row.symbol in CURATED:
        return CURATED[row.symbol]["status"]
    if row.status == "hidden_component":
        return "stable"
    if row.status == "uncertain_candidate":
        return "candidate"
    if row.is_curated_hub or row.phon_count >= MIN_PHON_STABLE:
        return "stable"
    if row.phon_count >= MIN_PHON_CANDIDATE:
        return "candidate"
    return "candidate"


def infer_priority(row: DictRow, status: str) -> str:
    if row.symbol in CURATED:
        return CURATED[row.symbol]["glossary_priority"]
    if row.status == "hidden_component":
        return "high"
    if status == "stable" and row.phon_count >= MIN_PHON_STABLE:
        return "medium"
    if status == "experimental":
        return "medium"
    return "low"


def examples_for(row: DictRow, token_idx: dict[str, set[str]], limit: int = 8) -> str:
    samples = row.sample_kanji()
    if not samples:
        samples = sorted(token_idx.get(row.symbol, set()))
    if row.symbol not in samples and row.symbol:
        samples = [row.symbol] + samples
    # drop anchor duplicates at end
    out: list[str] = []
    for k in samples:
        if k not in out:
            out.append(k)
        if len(out) >= limit:
            break
    return "|".join(out)


def should_include(row: DictRow) -> bool:
    if row.symbol in CURATED:
        return True
    if row.status == "hidden_component":
        return True
    if row.symbol in LESSON_HUBS:
        return True
    if row.status == "family_anchor" and (
        row.is_curated_hub or row.phon_count >= MIN_PHON_CANDIDATE
    ):
        return True
    if row.status == "probable_family":
        return True
    return False


def build_family_row(row: DictRow, token_idx: dict[str, set[str]]) -> dict[str, str]:
    cur = CURATED.get(row.symbol, {})
    family_id = cur.get("family_id") or LESSON_HUBS.get(row.symbol) or infer_family_id(row)
    display = cur.get("display_name") or infer_display(row, family_id)
    status = cur.get("status") or infer_status(row)
    family_type = cur.get("family_type") or infer_type(row)
    font_risk = cur.get("font_variation_risk") or FONT_RISK.get(row.symbol, "stable-form")
    priority = cur.get("glossary_priority") or infer_priority(row, status)
    ex = cur.get("example_kanji") or examples_for(row, token_idx)

    notes_parts = [cur.get("notes", "pass7 auto scaffold")]
    if row.phon_count:
        notes_parts.append(f"phon_parents={row.phon_count}")
    if row.is_curated_hub:
        notes_parts.append("curated_hub")
    notes_parts.append("recursive_nav=enabled")
    notes_parts.append("content=review_pending")

    return {
        "family_id": family_id,
        "display_name": display,
        "anchor_symbol": row.symbol,
        "status": status,
        "family_type": family_type,
        "notes": "; ".join(notes_parts),
        "example_kanji": ex,
        "font_variation_risk": font_risk,
        "glossary_priority": priority,
    }


def build_navigation_map(families: list[dict[str, str]]) -> dict[str, list[str]]:
    """kanji → family_id(s) for click-for-details architecture."""
    nav: dict[str, list[str]] = defaultdict(list)
    sym_to_fid = {f["anchor_symbol"]: f["family_id"] for f in families}
    for f in families:
        fid = f["family_id"]
        anchor = f["anchor_symbol"]
        for k in (f.get("example_kanji") or "").split("|"):
            k = k.strip()
            if k and k != anchor:
                nav[k].append(fid)
        nav[anchor].append(fid)
    # explicit lesson cognition links (display vs phonetic core)
    extra = {
        "嫡": ["deal_family", "merchant_family"],
        "褐": ["siesta_family"],
        "渇": ["siesta_family"],
        "適": ["merchant_family", "deal_family"],
        "競": ["competition_family"],
    }
    for k, fids in extra.items():
        for fid in fids:
            if fid not in nav[k]:
                nav[k].append(fid)
    return dict(nav)


def main() -> None:
    v2 = load_v2()
    token_idx = load_v4_token_index()
    by_sym = {r.symbol: r for r in v2}

    families: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    # Curated order first (stable foundation).
    for sym in CURATED:
        if sym in by_sym:
            row = build_family_row(by_sym[sym], token_idx)
            if row["family_id"] not in seen_ids:
                families.append(row)
                seen_ids.add(row["family_id"])

    # Remaining eligible rows sorted by priority signal.
    rest = [r for r in v2 if should_include(r) and r.symbol not in CURATED]
    rest.sort(key=lambda r: (-r.phon_count, r.symbol))
    for row in rest:
        fr = build_family_row(row, token_idx)
        if fr["family_id"] in seen_ids:
            continue
        families.append(fr)
        seen_ids.add(fr["family_id"])

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(families)

    nav = build_navigation_map(families)
    tier = {"high": [], "medium": [], "low": []}
    for f in families:
        tier[f["glossary_priority"]].append(f)

    lines = [
        "PASS 7 — GLOSSARY FOUNDATION ARCHITECTURE REPORT",
        "=" * 70,
        "",
        "Scaffolding pass only. No glossary pages generated.",
        f"Source dictionary: {V2_DICT.name}",
        f"Source master:     {V4.name}",
        "",
        "## SUMMARY",
        "",
        f"  glossary families defined:     {len(families)}",
        f"    stable:                      {sum(1 for f in families if f['status']=='stable')}",
        f"    experimental:                {sum(1 for f in families if f['status']=='experimental')}",
        f"    candidate:                   {sum(1 for f in families if f['status']=='candidate')}",
        f"  high-priority hubs:            {len(tier['high'])}",
        f"  kanji navigation links:        {len(nav)}",
        "",
        "## FOUNDATION TIER (HIGH PRIORITY)",
        "",
    ]
    for f in tier["high"]:
        lines.append(
            f"  {f['family_id']}\t{f['display_name']}\tanchor={f['anchor_symbol']}\t"
            f"type={f['family_type']}\tfont={f['font_variation_risk']}"
        )

    lines += ["", "## CLICK-FOR-DETAILS NAVIGATION (sample)", ""]
    for k in ["嫡", "褐", "渇", "適", "競", "遠", "式", "輸", "各"]:
        fids = nav.get(k, [])
        lines.append(f"  {k} → {', '.join(fids) if fids else '(none yet)'}")

    lines += [
        "",
        "## RECURSIVE GLOSSARY ARCHITECTURE",
        "",
        "  Layer 0: lesson cognition (authoritative in lesson HTML / v4 harvest)",
        "  Layer 1: glossary_family.csv hub row (this pass)",
        "  Layer 2: future glossary page — variation tolerance, family evolution",
        "  Layer 3: future member kanji detail — links back to hub + siblings",
        "",
        "  Navigation rule:",
        "    kanji in example_kanji → click → family hub page",
        "    family hub → lists siblings, font notes, related families",
        "    optional phonetic-core vs display-wrapper split (商 vs 啇)",
        "",
        "## FONT VARIATION METADATA",
        "",
        "  font-sensitive     — glyph shape shifts across fonts (曷, 竟, 𧘇)",
        "  handwriting-shift  — cursive transforms identity (夂, 書, 聿)",
        "  compressed-print   — small-type collapse risk (田｜, 飛)",
        "  stable-form        — robust cross-font identity (啇, 袁, 戈)",
        "",
        "  Families by font risk:",
        "",
    ]
    by_font: dict[str, list[str]] = defaultdict(list)
    for f in families:
        by_font[f["font_variation_risk"]].append(f["family_id"])
    for risk, ids in sorted(by_font.items()):
        lines.append(f"  {risk}: {', '.join(ids[:12])}{'...' if len(ids)>12 else ''}")

    lines += ["", "## FAMILY TYPE LEGEND", ""]
    for label, desc in [
        ("visual_family", "recognizable visual cluster; mutation-tolerant"),
        ("phonetic_family", "sound-family core; stable phonetic identity"),
        ("visual_repeat", "repeated stand/fin pattern (竟/競/鏡)"),
        ("hidden_reusable", "lesson-hidden anchor; glossary expands later"),
        ("structural_primitive", "pipe-editing primitive; not full kanji hub"),
        ("hybrid_family", "mixed visual+phonetic (reserved for review)"),
    ]:
        n = sum(1 for f in families if f["family_type"] == label)
        lines.append(f"  {label:<22} n={n} — {desc}")

    lines += ["", "## STABLE FOUNDATION FAMILIES (full list)", ""]
    for f in families:
        if f["status"] == "stable":
            lines.append(
                f"  {f['family_id']}\t{f['anchor_symbol']}\texamples={f['example_kanji']}"
            )

    lines += ["", "## CANDIDATE / EXPERIMENTAL (review queue)", ""]
    for f in families:
        if f["status"] in ("candidate", "experimental"):
            lines.append(
                f"  {f['family_id']}\t{f['anchor_symbol']}\tstatus={f['status']}\t"
                f"priority={f['glossary_priority']}"
            )

    excluded = [r for r in v2 if r.status == "family_anchor" and not should_include(r)]
    lines += [
        "",
        "## EXCLUDED FROM GLOSSARY LAYER (this pass)",
        f"  family_anchor rows below phon threshold (<{MIN_PHON_CANDIDATE}): {len(excluded)}",
        "  (remain in primitive_dictionary.v2 for editor use; not promoted yet)",
        "",
    ]
    for r in excluded[:25]:
        lines.append(f"  {r.symbol}\tphon={r.phon_count}\tstatus={r.status}")
    if len(excluded) > 25:
        lines.append(f"  ... +{len(excluded)-25} more")

    lines += [
        "",
        "## KEY PRINCIPLE",
        "",
        "  Glossary = recursive cognition map, NOT static decomposition dictionary.",
        "  Lesson cognition stays authoritative; glossary adds precision + exploration.",
        "",
        f"Output CSV:    {OUT_CSV.name}",
        f"Output report: {OUT_REPORT.name}",
        "",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_CSV} ({len(families)} families)")
    print(f"Wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
