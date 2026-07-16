"""Curate Lesson 4 compounds for the exhibition — quality over quantity.

Source: kml/contents/books/book_01/compounds/lesson_04.html
Skips obscure entries, long phrases, and vocabulary-exhibition repeats.
"""

from __future__ import annotations

# slug → ordered compound jp (must exist in compounds HTML)
SELECTED_BY_SLUG: dict[str, list[str]] = {
    "post_a_bill": ["貼る", "貼り紙", "貼付"],
    "see": ["見る", "見える", "見学", "発見"],
    "newborn": ["新生児", "幼児", "児童", "胎児"],
    "beginning": ["元", "元気", "地元", "元日"],
    "page": ["頁", "頁数", "最終頁"],
    "stubborn": ["頑張る", "頑固", "頑丈", "頑健"],
    "mediocre": ["平凡", "凡人", "非凡", "凡庸"],
    "defeat": ["負ける", "勝負", "負傷", "背負う"],
    "ten_thousand": ["一万", "万一", "万歳", "万人"],
    "phrase": ["句", "文句", "句読点", "警句"],
    "texture": ["肌", "肌触り", "肌色", "素肌"],
    "ten_days": ["上旬", "中旬", "下旬", "旬"],
    "ladle": ["勺", "一勺", "酒勺"],
    "bulls_eye": ["的", "目的", "具体的", "標的"],
    "neck": ["首", "首都", "首相", "部首"],
    "hook": ["乙", "乙女", "甲乙"],
    "riot": ["混乱", "暴乱", "乱暴", "乱用"],
    "straightaway": ["直す", "正直", "直接", "直行"],
    "tool": ["家具", "具合", "筆記具", "具現化"],
    "true": ["真実", "写真", "真剣", "真夜中"],
}
