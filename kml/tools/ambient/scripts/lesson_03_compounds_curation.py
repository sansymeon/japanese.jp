"""Curate Lesson 3 compounds for the exhibition — quality over quantity.

Source: kml/contents/books/book_01/compounds/lesson_03.html
Skips obscure entries, long phrases, and vocabulary-exhibition repeats.
"""

from __future__ import annotations

# slug → ordered compound jp (must exist in compounds HTML)
SELECTED_BY_SLUG: dict[str, list[str]] = {
    "tongue": ["毒舌", "舌打ち", "二枚舌"],
    "measuring_box": ["一升", "升酒", "升目"],
    "rise": ["昇進", "昇格", "昇る", "上昇"],
    "round": ["丸", "丸ごと", "日の丸", "弾丸", "丸太"],
    "measurement": ["寸法", "寸前", "一寸"],
    "elbow": ["肘", "肘掛け"],
    "specialty": ["専門", "専用", "専攻", "専念"],
    "knowledgeable": ["博士", "博物館", "博識", "博覧会"],
    "signal": ["占卜", "卜占", "卜う"],
    "fortune_telling": ["占う", "占い", "独占"],
    "up": ["上", "上がる", "上げる", "向上", "上手"],
    "below": ["下", "下がる", "下げる", "地下", "下手"],
    "eminent": ["卓球", "卓上", "卓越", "卓見"],
    "morning": ["朝", "今朝", "毎朝", "朝食", "朝日"],
    "derision": ["嘲笑", "嘲る", "冷嘲"],
    "only": ["只", "只今"],
    "shellfish": ["貝", "貝殻", "巻貝", "貝類", "真珠貝"],
    "pop_song": ["唄", "子守唄", "唄声"],
    "virtue": ["貞節", "貞操", "不貞"],
    "employee": ["社員", "店員", "職員", "全員", "会員", "議員"],
}
