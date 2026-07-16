"""Grade 2 anchor compound seed data — school edition.

Collection axes:
  contentType: compounds
  edition: school
  grade: 2

Part 1 (引 → 間) through Part 8 (歩 → 朋) — full 161-kanji school jukugo series.
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
        "grade": 2,
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


# Grade 2 anchor compounds — Parts 1–8 (display order 1–161).
GRADE_2_ANCHOR_SEED: list[dict[str, Any]] = [
    _entry("引", "引力", "いんりょく", display_order=1),
    _entry("羽", "羽毛", "うもう", display_order=2),
    _entry("雲", "雲海", "うんかい", display_order=3),
    _entry("園", "園長", "えんちょう", display_order=4),
    _entry("遠", "遠足", "えんそく", display_order=5),
    _entry("何", "何人", "なんにん", display_order=6),
    _entry("科", "科学", "かがく", display_order=7),
    _entry("夏", "夏休み", "なつやすみ", display_order=8),
    _entry("家", "家族", "かぞく", display_order=9),
    _entry("歌", "歌手", "かしゅ", display_order=10),
    _entry("画", "画家", "がか", display_order=11),
    _entry("回", "回数", "かいすう", display_order=12),
    _entry("会", "会話", "かいわ", display_order=13),
    _entry("海", "海岸", "かいがん", display_order=14),
    _entry("絵", "絵本", "えほん", display_order=15),
    _entry("外", "外国", "がいこく", display_order=16),
    _entry("角", "角度", "かくど", display_order=17),
    _entry("楽", "楽器", "がっき", display_order=18),
    _entry("活", "活動", "かつどう", display_order=19),
    _entry("間", "間隔", "かんかく", display_order=20),
    _entry("丸", "丸太", "まるた", display_order=21),
    _entry("岩", "岩石", "がんせき", display_order=22),
    _entry("顔", "顔色", "がんしょく", display_order=23),
    _entry("汽", "汽車", "きしゃ", display_order=24),
    _entry("記", "記者", "きしゃ", display_order=25),
    _entry("帰", "帰国", "きこく", display_order=26),
    _entry("弓", "弓道", "きゅうどう", display_order=27),
    _entry("牛", "牛肉", "ぎゅうにく", display_order=28),
    _entry("魚", "魚屋", "さかなや", display_order=29),
    _entry("京", "京都", "きょうと", display_order=30),
    _entry("強", "強風", "きょうふう", display_order=31),
    _entry("教", "教室", "きょうしつ", display_order=32),
    _entry("近", "近所", "きんじょ", display_order=33),
    _entry("兄", "兄弟", "きょうだい", display_order=34),
    _entry("形", "形状", "けいじょう", display_order=35),
    _entry("計", "計画", "けいかく", display_order=36),
    _entry("元", "元気", "げんき", display_order=37),
    _entry("言", "言語", "げんご", display_order=38),
    _entry("原", "原因", "げんいん", display_order=39),
    _entry("戸", "戸外", "こがい", display_order=40),
    _entry("古", "古代", "こだい", display_order=41),
    _entry("午", "午後", "ごご", display_order=42),
    _entry("後", "後半", "こうはん", display_order=43),
    _entry("語", "語学", "ごがく", display_order=44),
    _entry("工", "工事", "こうじ", display_order=45),
    _entry("公", "公園", "こうえん", display_order=46),
    _entry("広", "広場", "ひろば", display_order=47),
    _entry("交", "交通", "こうつう", display_order=48),
    _entry("光", "光明", "こうみょう", display_order=49),
    _entry("考", "考古", "こうこ", display_order=50),
    _entry("行", "行事", "ぎょうじ", display_order=51),
    _entry("高", "高校", "こうこう", display_order=52),
    _entry("黄", "黄色", "きいろ", display_order=53),
    _entry("合", "合図", "あいず", display_order=54),
    _entry("谷", "谷間", "たにま", display_order=55),
    _entry("国", "国語", "こくご", display_order=56),
    _entry("黒", "黒板", "こくばん", display_order=57),
    _entry("今", "今日", "きょう", display_order=58),
    _entry("才", "才能", "さいのう", display_order=59),
    _entry("細", "細工", "さいく", display_order=60),
    _entry("作", "作品", "さくひん", display_order=61),
    _entry("算", "算数", "さんすう", display_order=62),
    _entry("止", "止点", "していてん", display_order=63),
    _entry("市", "市立", "しりつ", display_order=64),
    _entry("矢", "矢印", "やじるし", display_order=65),
    _entry("姉", "姉妹", "しまい", display_order=66),
    _entry("思", "思想", "しそう", display_order=67),
    _entry("紙", "紙面", "しめん", display_order=68),
    _entry("寺", "寺院", "じいん", display_order=69),
    _entry("自", "自分", "じぶん", display_order=70),
    _entry("時", "時間", "じかん", display_order=71),
    _entry("室", "室内", "しつない", display_order=72),
    _entry("社", "社会", "しゃかい", display_order=73),
    _entry("弱", "弱点", "じゃくてん", display_order=74),
    _entry("首", "首都", "しゅと", display_order=75),
    _entry("秋", "秋分", "しゅうぶん", display_order=76),
    _entry("週", "週間", "しゅうかん", display_order=77),
    _entry("春", "春分", "しゅんぶん", display_order=78),
    _entry("書", "書店", "しょてん", display_order=79),
    _entry("少", "少年", "しょうねん", display_order=80),
    _entry("場", "場所", "ばしょ", display_order=81),
    _entry("色", "色紙", "しきし", display_order=82),
    _entry("食", "食品", "しょくひん", display_order=83),
    _entry("心", "心配", "しんぱい", display_order=84),
    _entry("新", "新聞", "しんぶん", display_order=85),
    _entry("親", "親友", "しんゆう", display_order=86),
    _entry("図", "図工", "ずこう", display_order=87),
    _entry("数", "数学", "すうがく", display_order=88),
    _entry("西", "西口", "にしぐち", display_order=89),
    _entry("声", "声楽", "せいがく", display_order=90),
    _entry("星", "星空", "ほしぞら", display_order=91),
    _entry("晴", "晴天", "せいてん", display_order=92),
    _entry("切", "切手", "きって", display_order=93),
    _entry("雪", "雪国", "ゆきぐに", display_order=94),
    _entry("船", "船長", "せんちょう", display_order=95),
    _entry("線", "線路", "せんろ", display_order=96),
    _entry("前", "前半", "ぜんはん", display_order=97),
    _entry("組", "組合", "くみあい", display_order=98),
    _entry("走", "走行", "そうこう", display_order=99),
    _entry("多", "多数", "たすう", display_order=100),
    _entry("太", "太陽", "たいよう", display_order=101),
    _entry("体", "体育", "たいいく", display_order=102),
    _entry("台", "台風", "たいふう", display_order=103),
    _entry("地", "地図", "ちず", display_order=104),
    _entry("池", "池水", "いけすい", display_order=105),
    _entry("知", "知人", "ちじん", display_order=106),
    _entry("茶", "茶道", "さどう", display_order=107),
    _entry("昼", "昼食", "ちゅうしょく", display_order=108),
    _entry("長", "長所", "ちょうしょ", display_order=109),
    _entry("鳥", "鳥類", "ちょうるい", display_order=110),
    _entry("朝", "朝食", "ちょうしょく", display_order=111),
    _entry("直", "直線", "ちょくせん", display_order=112),
    _entry("通", "通学", "つうがく", display_order=113),
    _entry("弟", "兄弟", "きょうだい", display_order=114),
    _entry("店", "店員", "てんいん", display_order=115),
    _entry("点", "点数", "てんすう", display_order=116),
    _entry("電", "電気", "でんき", display_order=117),
    _entry("刀", "刀工", "とうこう", display_order=118),
    _entry("冬", "冬休み", "ふゆやすみ", display_order=119),
    _entry("当", "当番", "とうばん", display_order=120),
    _entry("東", "東京", "とうきょう", display_order=121),
    _entry("答", "答案", "とうあん", display_order=122),
    _entry("頭", "頭上", "とうじょう", display_order=123),
    _entry("同", "同級", "どうきゅう", display_order=124),
    _entry("道", "道路", "どうろ", display_order=125),
    _entry("読", "読書", "どくしょ", display_order=126),
    _entry("内", "内科", "ないか", display_order=127),
    _entry("南", "南口", "みなみぐち", display_order=128),
    _entry("肉", "肉屋", "にくや", display_order=129),
    _entry("馬", "馬車", "ばしゃ", display_order=130),
    _entry("売", "売店", "ばいてん", display_order=131),
    _entry("買", "買物", "かいもの", display_order=132),
    _entry("麦", "麦茶", "むぎちゃ", display_order=133),
    _entry("半", "半分", "はんぶん", display_order=134),
    _entry("番", "番号", "ばんごう", display_order=135),
    _entry("父", "父母", "ふぼ", display_order=136),
    _entry("風", "風船", "ふうせん", display_order=137),
    _entry("分", "分数", "ぶんすう", display_order=138),
    _entry(
        "聞",
        "新聞",
        "しんぶん",
        display_order=139,
        exception=True,
        emphasize="聞",
        exception_reason="high-value compound; target kanji not initial",
    ),
    _entry("米", "米国", "べいこく", display_order=140),
    _entry("歩", "歩道", "ほどう", display_order=141),
    _entry("母", "母校", "ぼこう", display_order=142),
    _entry("方", "方向", "ほうこう", display_order=143),
    _entry("北", "北口", "きたぐち", display_order=144),
    _entry("毎", "毎日", "まいにち", display_order=145),
    _entry("妹", "姉妹", "しまい", display_order=146),
    _entry("万", "万力", "まんりき", display_order=147),
    _entry("明", "明日", "あした", display_order=148),
    _entry("鳴", "鳴門", "なると", display_order=149),
    _entry("毛", "毛糸", "けいと", display_order=150),
    _entry("門", "門前", "もんぜん", display_order=151),
    _entry("夜", "夜空", "よぞら", display_order=152),
    _entry("野", "野原", "のはら", display_order=153),
    _entry("友", "友人", "ゆうじん", display_order=154),
    _entry("用", "用事", "ようじ", display_order=155),
    _entry("曜", "曜日", "ようび", display_order=156),
    _entry("来", "来年", "らいねん", display_order=157),
    _entry("里", "里山", "さとやま", display_order=158),
    _entry("理", "理科", "りか", display_order=159),
    _entry("話", "話題", "わだい", display_order=160),
    _entry("朋", "朋友", "ほうゆう", display_order=161),
]

ANCHOR_BY_KANJI: dict[str, dict] = {entry["kanji"]: entry for entry in GRADE_2_ANCHOR_SEED}


def ordered_anchor_entries() -> list[dict]:
    """Seeded anchors in displayOrder (curated school jukugo batches)."""
    if not GRADE_2_ANCHOR_SEED:
        raise ValueError("No Grade 2 anchor compound entries seeded.")
    return sorted(GRADE_2_ANCHOR_SEED, key=lambda e: e["displayOrder"])
