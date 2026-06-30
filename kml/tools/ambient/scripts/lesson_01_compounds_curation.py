"""Curate Lesson 1 compounds for the exhibition — quality over quantity.

Source: kml/contents/books/book_01/compounds/lesson_01.html
Skips vocabulary-exhibition repeats and obscure entries.
"""

from __future__ import annotations

# slug → ordered compound jp (must exist in compounds HTML)
SELECTED_BY_SLUG: dict[str, list[str]] = {
    "one": ["一日", "一番", "一生", "一人", "一息"],
    "two": ["二人", "二月", "二重", "二度", "第二"],
    "three": ["三人", "三日", "三角", "三年生", "三倍"],
    "four": ["四日", "四季", "四角", "四年", "四人"],
    "five": ["五月", "五人", "五回", "五感", "五百"],
    "six": ["六月", "六人", "六回", "第六"],
    "seven": ["七月", "七人", "七夕", "第七"],
    "eight": ["八月", "八人", "八百", "第八"],
    "nine": ["九月", "九人", "九回", "第九"],
    "ten": ["十月", "十分", "十人", "十回", "第十"],
    "mouth": ["人口", "口調", "入口", "出口", "口実"],
    "sun": ["日本", "日記", "祝日", "今日", "日焼け"],
    "moon": ["月曜日", "今月", "満月", "月明かり", "お月見"],
    "field": ["田園", "田畑", "田舎", "水田", "田中"],
    "eye": ["目的", "注目", "目標", "目玉", "一目"],
    "old": ["古代", "中古", "古文", "古本", "古寺"],
    "I": ["吾輩", "吾"],
    "risk": ["冒険", "冒頭", "冒す"],
    "companion": ["朋友", "親朋", "朋輩"],
    "bright": ["明日", "説明", "明白", "文明", "明かり"],
}
