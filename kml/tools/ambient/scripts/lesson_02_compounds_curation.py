"""Curate Lesson 2 compounds for the exhibition — quality over quantity.

Source: kml/contents/books/book_01/compounds/lesson_02.html
Skips obscure entries, long phrases, and vocabulary-exhibition repeats.
"""

from __future__ import annotations

# slug → ordered compound jp (must exist in compounds HTML)
SELECTED_BY_SLUG: dict[str, list[str]] = {
    "prosperous": ["昌盛", "繁昌", "昌平"],
    "chant": ["唱歌", "合唱", "提唱", "唱える"],
    "sparkle": ["結晶", "水晶", "明晶"],
    "goods": ["商品", "品物", "上品", "名品", "品定め"],
    "spine": ["呂律", "背筋（脊呂）"],
    "early": ["早朝", "早速", "早退", "早起き", "早口"],
    "rising_sun": ["旭日", "旭光", "旭川", "旭日旗"],
    "generation": ["世界", "世代", "世話", "世間", "世紀"],
    "stomach": ["胃腸", "胃薬", "胃痛", "胃炎", "胃液"],
    "dawn": ["元旦", "一旦", "旦那", "旦暮"],
    "gallbladder": ["胆石", "大胆", "胆力", "胆のう"],
    "span": ["亘る", "全国に亘る", "長年に亘り"],
    "concave": ["凹凸", "凹レンズ", "凹面鏡", "凹む", "凹み"],
    "convex": ["凸凹", "凸レンズ", "凸面鏡", "凸出", "凸型"],
    "olden_times": ["旧友", "旧姓", "旧式", "旧市街", "旧正月"],
    "oneself": ["自分", "自然", "自由", "自動車", "自信"],
    "white": ["白紙", "白夜", "告白", "白鳥", "白い"],
    "hundred": ["百円", "百貨店", "百科事典", "百人一首", "百倍"],
    "middle": ["中心", "中国", "中学校", "水中", "真ん中"],
    "thousand": ["千円", "千年", "千人", "千本桜", "千差万別"],
}
