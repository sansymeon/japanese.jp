"""Curate Lesson 5 compounds for the exhibition — quality over quantity.

Source: kml/contents/books/book_01/compounds/lesson_05.html
Skips obscure entries, long phrases, and vocabulary-exhibition repeats.
"""

from __future__ import annotations

SELECTED_BY_SLUG: dict[str, list[str]] = {
    "craft": ["工場", "工事", "工学", "大工"],
    "left": ["左", "左右", "左利き", "左翼"],
    "right": ["右", "左右", "右手", "右折"],
    "possess": ["有名", "有る", "所有", "有効"],
    "bribe": ["賄う", "賄賂", "賄費"],
    "tribute": ["貢ぐ", "貢献", "朝貢"],
    "paragraph": ["事項", "条項", "項目", "各項"],
    "sword": ["刀", "日本刀", "短刀"],
    "blade": ["刃", "刃物", "刃先"],
    "cut": ["切る", "大切", "親切", "締切"],
    "seduce": ["召す", "召集", "召喚"],
    "shining": ["昭和", "昭明", "昭然"],
    "rule": ["原則", "規則", "法則", "反則"],
    "vice": ["副社長", "副作用", "副詞", "副収入"],
    "separate": ["別", "別れる", "特別", "区別"],
    "street": ["丁寧", "丁目", "丁度", "丁字路"],
    "town": ["町", "町内", "下町", "町民"],
    "possible": ["可能", "不可", "可決", "許可"],
    "top": ["頂く", "頂点", "山頂", "頂上"],
    "child": ["子供", "様子", "電子", "王子"],
}
