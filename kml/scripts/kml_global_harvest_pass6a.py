#!/usr/bin/env python3
"""
PASS 6A — Global component family harvest (dictionary only, review-first).

Scans kanji_master_with_components.v4.csv + KanjiVG stroke pages.
Does NOT modify the master CSV or create v5.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
V4 = BASE / "data/kanji/kanji_master_with_components.v4.csv"
V1_DICT = BASE / "data/kanji/primitive_dictionary.csv"
MASTER = BASE / "data/kanji/kanji_master.csv"
STROKES_DIR = BASE / "tools/strokes/pages"
OUT_DICT = BASE / "data/kanji/primitive_dictionary.v2.csv"
OUT_REPORT = BASE / "data/kanji/global_harvest_report.txt"

FIELDNAMES = [
    "symbol",
    "preferred_name",
    "alternate_name",
    "first_use",
    "first_kanji",
    "status",
    "notes",
]

# IME-easy atoms / ultra-common radicals — not family cognition targets.
GENERIC_SKIP = frozenset(
    "口日月木水人女土火十一二三八儿又力大小王白田心手目石金言糸辶宀艹"
    "虫竹米車門馬牛羊魚鳥雨黒音足身毛"
)

# Stroke/radical forms — skip as family hubs (structural, not cognition families).
RADICAL_SKIP = frozenset(
    "亠丿乂厶攵匕卩欠殳龶覀彡毋廾廿幺允冋皿穴羽彳龵业兀龰"
)

# Known cognition hubs — include even when KanjiVG signal is weak.
CURATED_FAMILY: dict[str, str] = {
    "商": "deal",
    "竟": "compete",
    "啇": "merchant",
    "曷": "why",
    "袁": "robe_family",
    "戈": "halberd",
    "俞": "yu",
    "夂": "winter",
    "胡": "barbarian",
    "肖": "resemblance",
    "可": "can",
    "寺": "temple",
    "各": "each",
    "是": "just_so",
    "真": "true",
    "青": "blue",
    "韋": "tanned_leather",
    "監": "oversee",
    "京": "capital",
    "尚": "esteem",
    "軍": "army",
    "喿": "noisy",
}


@dataclass
class HarvestHit:
    symbol: str
    phon_parents: set[str] = field(default_factory=set)
    right_parents: set[str] = field(default_factory=set)
    v4_parents: set[str] = field(default_factory=set)
    curated: bool = False

    @property
    def parent_count(self) -> int:
        return len(self.all_parents())

    def all_parents(self) -> set[str]:
        return self.phon_parents | self.right_parents | self.v4_parents


def parse_kanjivg() -> dict[str, HarvestHit]:
    hits: dict[str, HarvestHit] = {}
    for fp in STROKES_DIR.glob("*.html"):
        text = fp.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'class="kanji-main-font">([^<]+)<', text)
        if not m:
            continue
        kanji = m.group(1).strip()
        if len(kanji) != 1:
            continue
        for line in text.splitlines():
            em = re.search(r'kvg:element="([^"]+)"', line)
            pm = re.search(r'kvg:phon="([^"]+)"', line)
            posm = re.search(r'kvg:position="([^"]+)"', line)
            if pm:
                for ch in pm.group(1):
                    if "\u4e00" <= ch <= "\u9fff":
                        hits.setdefault(ch, HarvestHit(ch)).phon_parents.add(kanji)
                        break
            if em and posm and posm.group(1) in ("right", "bottom", "nyo"):
                el = em.group(1)
                if len(el) == 1 and "\u4e00" <= el <= "\u9fff":
                    hits.setdefault(el, HarvestHit(el)).right_parents.add(kanji)
    return hits


def load_v1() -> list[dict[str, str]]:
    with open(V1_DICT, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_v4_meta() -> tuple[dict[str, dict], dict[str, set[str]]]:
    meta: dict[str, dict] = {}
    token_parents: dict[str, set[str]] = defaultdict(set)
    with open(V4, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            k = (row.get("kanji") or "").strip()
            if not k:
                continue
            meta[k] = row
            prim = (row.get("kml_primitives") or "").strip()
            for t in prim.split("|"):
                t = t.strip()
                if t:
                    token_parents[t].add(k)
    return meta, token_parents


def load_master() -> dict[str, dict]:
    out: dict[str, dict] = {}
    with open(MASTER, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            k = (row.get("kanji") or "").strip()
            if k:
                out[k] = row
    return out


def lesson_num(row: dict | None) -> int:
    if not row:
        return 9999
    raw = (row.get("lesson_number") or row.get("lesson_start") or "").strip()
    m = re.search(r"\d+", raw)
    return int(m.group()) if m else 9999


def pick_first_parent(parents: set[str], v4_meta: dict, master: dict) -> str:
    if not parents:
        return ""
    return sorted(
        parents,
        key=lambda p: (
            lesson_num(v4_meta.get(p) or master.get(p)),
            master.get(p, {}).get("heisig_number", "9999"),
            p,
        ),
    )[0]


def classify(hit: HarvestHit, strokes: int) -> str | None:
    sym = hit.symbol
    if sym in GENERIC_SKIP or sym in RADICAL_SKIP:
        return None
    phon_n = len(hit.phon_parents)
    if hit.curated or sym in CURATED_FAMILY:
        return "family_anchor"
    if phon_n >= 3:
        return "family_anchor"
    if phon_n == 2:
        return "uncertain_candidate"
    if phon_n == 1 and len(hit.right_parents) >= 6 and strokes >= 8:
        return "probable_family"
    return None


def build_notes(hit: HarvestHit, status: str) -> str:
    parts = [
        "pass6a harvest",
        f"phon_parents={len(hit.phon_parents)}",
        f"right_parents={len(hit.right_parents)}",
        f"v4_token_parents={len(hit.v4_parents)}",
    ]
    if hit.curated:
        parts.append("curated_hub")
    sample = sorted(hit.all_parents())[:8]
    if sample:
        parts.append("sample=" + ",".join(sample))
    parts.append("sources=kanjivg,v4")
    if status == "uncertain_candidate":
        parts.append("review=human")
    return "; ".join(parts)


def main() -> None:
    v1_rows = load_v1()
    v1_symbols = {r["symbol"] for r in v1_rows}
    v4_meta, v4_tokens = load_v4_meta()
    master = load_master()
    kg = parse_kanjivg()

    # Enrich with v4 token parents and curated flags.
    for sym, parents in v4_tokens.items():
        if len(sym) == 1 and "\u4e00" <= sym <= "\u9fff":
            kg.setdefault(sym, HarvestHit(sym)).v4_parents |= parents
    for sym in CURATED_FAMILY:
        kg.setdefault(sym, HarvestHit(sym)).curated = True

    new_rows: list[dict[str, str]] = []
    skipped: list[tuple[str, str]] = []
    uncertain: list[tuple[str, int, list[str]]] = []
    anchors: list[tuple[str, int, list[str]]] = []
    hubs: list[tuple[str, int, int, int]] = []

    for sym, hit in sorted(kg.items(), key=lambda x: (-len(x[1].phon_parents), x[0])):
        if sym in v1_symbols:
            continue
        strokes = int(master.get(sym, {}).get("strokes") or 0)
        status = classify(hit, strokes)
        if not status:
            reason = "generic" if sym in GENERIC_SKIP else "radical" if sym in RADICAL_SKIP else "low_signal"
            if hit.parent_count >= 2:
                skipped.append((sym, reason))
            continue

        parents = hit.all_parents()
        first_k = pick_first_parent(parents, v4_meta, master)
        if not first_k and sym in v4_meta:
            first_k = sym
        first_row = v4_meta.get(first_k) or master.get(first_k, {})
        ln = lesson_num(first_row)
        first_use = f"lesson_{ln:02d}" if ln < 9999 else ""

        kw = (
            CURATED_FAMILY.get(sym)
            or (master.get(sym, {}).get("keyword") or "").strip()
            or (v4_meta.get(sym, {}).get("keyword") or "").strip()
        )
        preferred = kw.replace(" ", "_") if kw else f"{sym}_family"
        alt = preferred if preferred.endswith("_family") else f"{preferred}_family"

        row = {
            "symbol": sym,
            "preferred_name": preferred,
            "alternate_name": alt,
            "first_use": first_use,
            "first_kanji": first_k,
            "status": status,
            "notes": build_notes(hit, status),
        }
        new_rows.append(row)

        sample = sorted(parents)[:6]
        if status == "uncertain_candidate":
            uncertain.append((sym, hit.parent_count, sample))
        else:
            anchors.append((sym, hit.parent_count, sample))
        if len(hit.phon_parents) >= 4:
            hubs.append(
                (sym, len(hit.phon_parents), len(hit.right_parents), len(hit.v4_parents))
            )

    # Stable sort new rows: status tier, then parent count desc, then symbol.
    tier = {"family_anchor": 0, "probable_family": 1, "uncertain_candidate": 2}
    new_rows.sort(
        key=lambda r: (
            tier.get(r["status"], 9),
            -int(re.search(r"phon_parents=(\d+)", r["notes"]).group(1)),
            r["symbol"],
        )
    )

    out_rows = v1_rows + new_rows
    with open(OUT_DICT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(out_rows)

    # Report
    lines = [
        "PASS 6A — GLOBAL COMPONENT FAMILY HARVEST REPORT",
        "=" * 70,
        "",
        "Review-first exploratory pass. Does NOT modify kanji_master.",
        f"Source master: {V4.name}",
        f"Source dictionary: {V1_DICT.name}",
        f"KanjiVG pages scanned: {len(list(STROKES_DIR.glob('*.html')))}",
        "",
        "## SUMMARY",
        "",
        f"  v1 dictionary entries (preserved):     {len(v1_rows)}",
        f"  new harvested entries:                 {len(new_rows)}",
        f"  v2 dictionary total:                   {len(out_rows)}",
        f"    family_anchor:                       {sum(1 for r in new_rows if r['status']=='family_anchor')}",
        f"    probable_family:                     {sum(1 for r in new_rows if r['status']=='probable_family')}",
        f"    uncertain_candidate:                 {sum(1 for r in new_rows if r['status']=='uncertain_candidate')}",
        "",
        "## NEW PROBABLE FAMILY ANCHORS",
        "(phonetic-family signal >= 3 parents, or curated hub)",
        "",
    ]
    for sym, n, sample in sorted(anchors, key=lambda x: -x[1])[:80]:
        kw = master.get(sym, {}).get("keyword", "")
        lines.append(f"  {sym}\tparents≈{n}\tkeyword={kw}\tsample={','.join(sample)}")

    lines += [
        "",
        "## UNCERTAIN CANDIDATES",
        "(phonetic-family signal = 2 parents — human review recommended)",
        "",
    ]
    for sym, n, sample in sorted(uncertain, key=lambda x: -x[1])[:60]:
        lines.append(f"  {sym}\tparents≈{n}\tsample={','.join(sample)}")

    lines += [
        "",
        "## HIGH-FREQUENCY RECURRING STRUCTURES (phon hubs)",
        "",
    ]
    for sym, pn, rn, vn in sorted(hubs, key=lambda x: -x[1])[:40]:
        lines.append(f"  {sym}\tphon={pn}\tright={rn}\tv4={vn}")

    lines += [
        "",
        "## POSSIBLE GLOSSARY-FAMILY HUBS",
        "(curated + strong cross-system recurrence)",
        "",
    ]
    for sym in sorted(CURATED_FAMILY):
        hit = kg.get(sym, HarvestHit(sym))
        lines.append(
            f"  {sym}\t{CURATED_FAMILY[sym]}\tphon={len(hit.phon_parents)} "
            f"right={len(hit.right_parents)} v4={len(hit.v4_parents)}"
        )

    lines += [
        "",
        "## STRUCTURES SKIPPED INTENTIONALLY",
        "(generic IME atoms, stroke radicals, or insufficient family signal)",
        "",
    ]
    for sym, reason in sorted(skipped, key=lambda x: (-len(kg[x[0]].all_parents()), x[0]))[:50]:
        hit = kg[sym]
        lines.append(
            f"  {sym}\treason={reason}\tphon={len(hit.phon_parents)} "
            f"right={len(hit.right_parents)}"
        )

    lines += [
        "",
        "## RECURRING V4 PIPE CHUNKS (informational)",
        "Multi-token patterns from harvested L1–22 rows — not promoted to dictionary.",
        "",
    ]
    chunk_ct: dict[str, int] = defaultdict(int)
    with open(V4, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            prim = (row.get("kml_primitives") or "").strip()
            if not prim or "pass4: harvested" not in (row.get("notes") or ""):
                continue
            parts = prim.split("|")
            for i in range(len(parts)):
                for j in range(i + 2, min(i + 4, len(parts) + 1)):
                    chunk = "|".join(parts[i:j])
                    if len(chunk) > 1:
                        chunk_ct[chunk] += 1
    for chunk, n in sorted(chunk_ct.items(), key=lambda x: -x[1]):
        if n >= 2:
            lines.append(f"  {chunk!r}\tcount={n}")

    lines += [
        "",
        "## KEY PRINCIPLE",
        "",
        "  Discover probable KML cognition families — NOT finalize decomposition.",
        "",
        f"Output dictionary: {OUT_DICT.name}",
        f"Output report:     {OUT_REPORT.name}",
        "",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_DICT} ({len(out_rows)} rows, +{len(new_rows)} new)")
    print(f"Wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
