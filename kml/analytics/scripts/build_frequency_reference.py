#!/usr/bin/env python3
"""Build the modern-spoken-Japanese frequency reference list.

Input : reference/ja_opensubtitles_full.txt
        (word<space>count, surface-form tokens, OpenSubtitles 2018 corpus,
        via hermitdave/FrequencyWords - CC-BY-SA)

Output: reference/ja_spoken_frequency_lemmas.tsv
        (rank<TAB>lemma<TAB>count) - surface forms are lemmatized with
        UniDic/fugashi and aggregated, punctuation/symbols/pure numbers
        are dropped, so ranks reflect dictionary-form words as they are
        used in modern spoken Japanese (film & TV subtitles).

This script only reads reference data and writes inside kml/analytics/.
It never touches the master vocabulary database.
"""

from collections import defaultdict
from pathlib import Path
import re

import fugashi

REF_DIR = Path(__file__).resolve().parent.parent / "reference"
SRC = REF_DIR / "ja_opensubtitles_full.txt"
OUT = REF_DIR / "ja_spoken_frequency_lemmas.tsv"

SKIP_POS1 = {"補助記号", "記号", "空白"}
JP_CHAR = re.compile(r"[ぁ-んァ-ヶー一-龯々〆〤]")


def main() -> None:
    tagger = fugashi.Tagger()
    counts: defaultdict[str, int] = defaultdict(int)

    with SRC.open(encoding="utf-8") as f:
        for line in f:
            parts = line.rsplit(" ", 1)
            if len(parts) != 2:
                continue
            surface, count_s = parts[0].strip(), parts[1].strip()
            if not surface or not count_s.isdigit():
                continue
            if not JP_CHAR.search(surface):
                continue
            count = int(count_s)
            for word in tagger(surface):
                if word.feature.pos1 in SKIP_POS1:
                    continue
                lemma = word.feature.orthBase or word.surface
                if not lemma or not JP_CHAR.search(lemma):
                    continue
                counts[lemma] += count

    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    with OUT.open("w", encoding="utf-8") as f:
        f.write("# rank\tlemma\tcount\n")
        for rank, (lemma, count) in enumerate(ranked, start=1):
            f.write(f"{rank}\t{lemma}\t{count}\n")

    print(f"Wrote {len(ranked)} lemmas to {OUT}")


if __name__ == "__main__":
    main()
