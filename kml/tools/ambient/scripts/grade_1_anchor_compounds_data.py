"""Grade 1 anchor compound seed data — school edition.

Collection axes:
  contentType: compounds
  edition: school
  grade: 1

Working prototype source list (80 kanji). Individual anchors may be revised later.
"""

from __future__ import annotations

from typing import Any, TypedDict


class AnchorCompoundEntry(TypedDict, total=False):
    kanji: str
    anchor: str
    reading: str
    exception: bool
    emphasize: str
    grade: int
    lesson: int | None
    part: int | None
    displayOrder: int
    exceptionReason: str
    visualWeightTarget: str
    notes: str


def _entry(
    kanji: str,
    anchor: str,
    reading: str,
    *,
    display_order: int,
    exception: bool = False,
    emphasize: str | None = None,
    exception_reason: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "kanji": kanji,
        "anchor": anchor,
        "reading": reading,
        "grade": 1,
        "lesson": None,
        "part": None,
        "displayOrder": display_order,
        "exception": exception,
    }
    if exception:
        target = emphasize or kanji
        item["visualWeightTarget"] = target
        item["emphasize"] = target
        if exception_reason:
            item["exceptionReason"] = exception_reason
    if notes:
        item["notes"] = notes
    return item


# Grade 1 anchor compounds — prototype seed list (display order 1–80).
GRADE_1_ANCHOR_SEED: list[dict[str, Any]] = [
    _entry("一", "一つ", "ひとつ", display_order=1),
    _entry("右", "右手", "みぎて", display_order=2),
    _entry("雨", "雨", "あめ", display_order=3),
    _entry("円", "円い", "まるい", display_order=4),
    _entry("王", "王さま", "おうさま", display_order=5),
    _entry("音", "音楽", "おんがく", display_order=6),
    _entry("下", "下りる", "おりる", display_order=7),
    _entry("火", "火山", "かざん", display_order=8),
    _entry("花", "花火", "はなび", display_order=9),
    _entry("貝", "貝がら", "かいがら", display_order=10),
    _entry("学", "学校", "がっこう", display_order=11),
    _entry("気", "気分", "きぶん", display_order=12),
    _entry("九", "九つ", "ここのつ", display_order=13),
    _entry("休", "休む", "やすむ", display_order=14),
    _entry("玉", "玉ねぎ", "たまねぎ", display_order=15),
    _entry("金", "金魚", "きんぎょ", display_order=16),
    _entry("空", "空気", "くうき", display_order=17),
    _entry("月", "月", "つき", display_order=18),
    _entry("犬", "犬小屋", "いぬごや", display_order=19),
    _entry("見", "見える", "みえる", display_order=20),
    _entry("五", "五つ", "いつつ", display_order=21),
    _entry("口", "口ぐせ", "くちぐせ", display_order=22),
    _entry("校", "校長", "こうちょう", display_order=23),
    _entry("左", "左手", "ひだりて", display_order=24),
    _entry("三", "三つ", "みっつ", display_order=25),
    _entry("山", "山道", "やまみち", display_order=26),
    _entry("子", "子ども", "こども", display_order=27),
    _entry("四", "四つ", "よっつ", display_order=28),
    _entry("糸", "糸電話", "いとでんわ", display_order=29),
    _entry("字", "文字", "もじ", display_order=30),
    _entry("耳", "耳", "みみ", display_order=31),
    _entry("七", "七つ", "ななつ", display_order=32),
    _entry(
        "車",
        "自転車",
        "じてんしゃ",
        display_order=33,
        exception=True,
        emphasize="車",
        exception_reason="high-value compound; target kanji not initial",
    ),
    _entry("手", "手紙", "てがみ", display_order=34),
    _entry("十", "十日", "とおか", display_order=35),
    _entry("出", "出口", "でぐち", display_order=36),
    _entry("女", "女の子", "おんなのこ", display_order=37),
    _entry("小", "小石", "こいし", display_order=38),
    _entry("上", "上手", "じょうず", display_order=39),
    _entry("森", "森林", "しんりん", display_order=40),
    _entry("人", "人形", "にんぎょう", display_order=41),
    _entry("水", "水玉", "みずたま", display_order=42),
    _entry("正", "正月", "しょうがつ", display_order=43),
    _entry("生", "生きる", "いきる", display_order=44),
    _entry("青", "青空", "あおぞら", display_order=45),
    _entry("夕", "夕日", "ゆうひ", display_order=46),
    _entry("石", "石ころ", "いしころ", display_order=47),
    _entry("赤", "赤ちゃん", "あかちゃん", display_order=48),
    _entry("千", "千円", "せんえん", display_order=49),
    _entry("川", "川原", "かわら", display_order=50),
    _entry("先", "先生", "せんせい", display_order=51),
    _entry("早", "早口", "はやくち", display_order=52),
    _entry("草", "草花", "くさばな", display_order=53),
    _entry("足", "足音", "あしおと", display_order=54),
    _entry("村", "村人", "むらびと", display_order=55),
    _entry("大", "大人", "おとな", display_order=56),
    _entry("男", "男の子", "おとこのこ", display_order=57),
    _entry("竹", "竹馬", "たけうま", display_order=58),
    _entry("中", "中身", "なかみ", display_order=59),
    _entry("虫", "虫めがね", "むしめがね", display_order=60),
    _entry("町", "町", "まち", display_order=61),
    _entry("天", "天気", "てんき", display_order=62),
    _entry("田", "田んぼ", "たんぼ", display_order=63),
    _entry("土", "土", "つち", display_order=64),
    _entry("二", "二つ", "ふたつ", display_order=65),
    _entry("日", "日よう日", "にちようび", display_order=66),
    _entry("入", "入り口", "いりぐち", display_order=67),
    _entry("年", "年上", "としうえ", display_order=68),
    _entry("白", "白線", "はくせん", display_order=69),
    _entry("八", "八つ", "やっつ", display_order=70),
    _entry("百", "百円", "ひゃくえん", display_order=71),
    _entry("文", "文字", "もじ", display_order=72),
    _entry("木", "木かげ", "こかげ", display_order=73),
    _entry("本", "本屋", "ほんや", display_order=74),
    _entry("名", "名前", "なまえ", display_order=75),
    _entry("目", "目玉", "めだま", display_order=76),
    _entry("立", "立つ", "たつ", display_order=77),
    _entry("力", "力もち", "ちからもち", display_order=78),
    _entry("林", "林", "はやし", display_order=79),
    _entry("六", "六つ", "むっつ", display_order=80),
]

# Back-compat alias for earlier prototype imports.
PROTOTYPE_ENTRIES = GRADE_1_ANCHOR_SEED

ANCHOR_BY_KANJI: dict[str, dict] = {entry["kanji"]: entry for entry in GRADE_1_ANCHOR_SEED}


def ordered_anchor_entries() -> list[dict]:
    """Grade 1 anchors in school joyo_index order (matches stroke-order parts)."""
    from grade_1_kanji import load_grade_1_kanji

    ordered: list[dict] = []
    for joyo in load_grade_1_kanji():
        entry = ANCHOR_BY_KANJI.get(joyo.kanji)
        if not entry:
            raise KeyError(f"Missing anchor seed for Grade 1 kanji: {joyo.kanji}")
        ordered.append(entry)
    return ordered
