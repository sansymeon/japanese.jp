#!/usr/bin/env python3
"""Semantic/collocation repair pass for Lessons 1–10. Does not rebuild vocabulary."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from _build_lessons_01_10 import ruby_segments

HERE = Path(__file__).resolve().parent

# (lesson, kanji, surface) -> new example + optional qa
# kanji disambiguates 左右 / 奇妙 / 火災
Rep = dict

REPAIRS: dict[tuple[int, str, str], dict] = {
    # Known cases
    (1, "冒", "冒す"): {
        "ja": "彼は危険を冒します。",
        "en": "He takes a risk.",
        "reason": "Normal collocation is 危険を冒す, not 嵐の海を冒す.",
    },
    (1, "冒", "危険を冒す"): {
        "ja": "彼女は危険を冒して山へ行きました。",
        "en": "She took a risk and went into the mountains.",
        "reason": "The phrase is the target; a short て sequence is inside the early band.",
        "clear_exception": True,
    },
    (1, "冒", "病を冒す"): {
        "ja": "長旅で病を冒しました。",
        "en": "He fell ill on the long journey.",
        "reason": "Listed sense is affliction; dictionary-form その人は病を冒す is not how the phrase is used.",
    },
    (1, "吾", "吾輩"): {
        "ja": "吾輩はこの庭の主である。",
        "en": "I am the master of this garden.",
        "exception": "吾輩 is literary; である marks the old-fashioned register without the cat-novel joke.",
    },
    (1, "吾", "自吾"): {
        "review": "自吾 is not ordinary modern Japanese; no everyday sentence demonstrates it honestly.",
        "reviewNote": "Current 自吾を静かに見ます treats a rare/Buddhist term as a physical object. Left unrepaired pending a source-backed gloss.",
    },
    (1, "冒", "冒涜"): {
        "ja": "その落書きは神への冒涜です。",
        "en": "That graffiti is a desecration of the gods.",
        "reason": "冒涜 collocates as への冒涜, not as a bare predicate 冒涜です.",
    },
    (1, "三", "三倍"): {
        "ja": "今年の客は去年の三倍です。",
        "en": "This year’s visitors are triple last year’s.",
        "reason": "雨は三倍です is not a natural comparison; 三倍 needs an explicit baseline.",
    },
    (1, "田", "田んぼ"): {
        "ja": "朝、田んぼに霧がかかります。",
        "en": "Mist settles on the rice fields in the morning.",
        "reason": "田んぼは霧です is a category error.",
    },
    (1, "六", "第六"): {
        "ja": "第六の選手が出ます。",
        "en": "The sixth athlete comes out.",
        "reason": "第六の人です is not how ordinal 第六 is used.",
    },
    (1, "二", "第二"): {
        "ja": "これは第二の問題です。",
        "en": "This is the second question.",
        "reason": "第二の子 is not the ordinary way to say a second child.",
    },
    (5, "工", "工事"): {
        "ja": "駅の前で工事をしています。",
        "en": "They are doing construction in front of the station.",
        "exception": "Natural 工事 takes をしている, not がある.",
    },
    (5, "工", "大工"): {
        "ja": "大工が家を建てます。",
        "en": "A carpenter is building a house.",
        "reason": "家を作る is the wrong verb; carpenters 建てる a house.",
    },
    (5, "左", "左遷"): {
        "ja": "父は大阪へ左遷されました。",
        "en": "My father was transferred to Osaka on a demotion.",
        "exception": "Natural 左遷 is typically passive; 左遷の町へ行く does not demonstrate the word.",
    },
    (5, "右", "右翼"): {
        "ja": "鳥の右翼は黒いです。",
        "en": "The bird’s right wing is black.",
        "reason": "旗は右翼に付きます mixed airplane/political senses; pair with 左翼 as a bird wing.",
    },
    (5, "賄", "賄う"): {
        "ja": "この金で昼を賄います。",
        "en": "This money covers lunch.",
        "reason": "Inflect; dictionary-form dump.",
    },
    (5, "賄", "賄方"): {
        "ja": "賄方が朝食を作ります。",
        "en": "The cook prepares breakfast.",
        "reason": "朝を作る is not Japanese; the object is 朝食.",
    },
    (5, "貢", "貢ぐ"): {
        "ja": "毎月家に貢ぎます。",
        "en": "I send money home every month.",
        "reason": "Inflect; dictionary-form dump.",
    },
    (5, "貢", "朝貢"): {
        "ja": "昔、周辺の国は中国へ朝貢しました。",
        "en": "In the past, neighboring countries sent tribute to China.",
        "reason": "Historical vocabulary needs a historical statement, not 朝貢がありました.",
    },
    (5, "有", "有る"): {
        "ja": "机の上に本が有ります。",
        "en": "There is a book on the desk.",
        "reason": "Inflect; 有る as あります is the normal polite form.",
    },
    (5, "切", "切る"): {
        "ja": "紙を切ります。",
        "en": "I cut the paper.",
        "reason": "Inflect; dictionary-form dump.",
    },
    (5, "召", "召す"): {
        "ja": "お客様はお茶を召します。",
        "en": "The guest takes tea.",
        "reason": "Honorific 召す should be inflected; register is already honorific.",
    },
    (5, "別", "別れる"): {
        "ja": "駅で友だちと別れます。",
        "en": "I part from my friend at the station.",
        "reason": "Inflect; dictionary-form dump.",
    },
    (5, "頂", "頂く"): {
        "ja": "手紙を頂きました。",
        "en": "I received a letter.",
        "reason": "頂く is typically past for receiving a letter.",
    },
    (5, "昭", "昭然"): {
        "ja": "事実は昭然としています。",
        "en": "The fact is plain to see.",
        "exception": "昭然 is used as 昭然としている, not 昭然です.",
    },
    (5, "則", "法則"): {
        "ja": "この法則は分かりやすいです。",
        "en": "This law is easy to understand.",
        "reason": "A scientific 法則 is not 易しい.",
    },
    (10, "照", "照れくさい"): {
        "ja": "みんなの前でほめられて、少し照れくさいです。",
        "en": "Being praised in front of everyone is a little embarrassing.",
        "exception": "照れくさい needs a situation; the て-form of ほめられる supplies it.",
    },
    (10, "照", "照らす"): {
        "ja": "月が道を照らします。",
        "en": "The moon lights the road.",
        "reason": "Inflect; dictionary-form dump. Sense was already good.",
    },
    (10, "魚", "魚を焼く"): {
        "ja": "庭で魚を焼きます。",
        "en": "I grill fish in the garden.",
        "reason": "Inflect the phrase naturally.",
    },
    (10, "漁", "漁る"): {
        "ja": "犬が庭を漁っています。",
        "en": "The dog is rummaging in the garden.",
        "exception": "あさる is typically ている for an ongoing rummage.",
    },
    (10, "墨", "墨守"): {
        "ja": "彼は古い規則を墨守します。",
        "en": "He sticks rigidly to the old rules.",
        "reason": "古いやり方の墨守です does not show how 墨守 is used as a verb.",
    },
    (10, "灰", "灰になる"): {
        "ja": "紙は灰になりました。",
        "en": "The paper turned to ash.",
        "reason": "The phrase is normally resultative past.",
    },
    (10, "灰", "火山灰"): {
        "ja": "風で火山灰が降ります。",
        "en": "Volcanic ash falls on the wind.",
        "reason": "火山灰が来る is not the usual verb; ash 降る.",
    },
    (10, "尚", "尚書"): {
        "ja": "漢の時代、尚書は高い役職でした。",
        "en": "In the Han period, a Shangshu was a high official.",
        "reason": "Historical office; 昔の尚書の名です teaches nothing.",
    },
    (10, "尚", "尚武"): {
        "ja": "その家は尚武の気風がありました。",
        "en": "That family had a martial spirit.",
        "reason": "尚武の気があります is vague; 気風 is the natural collocation.",
    },
    (10, "埋", "埋める"): {
        "ja": "穴に石を埋めます。",
        "en": "I bury a stone in the hole.",
        "reason": "Inflect; dictionary-form dump.",
    },
    (10, "埋", "埋まる"): {
        "ja": "道が雪で埋まりました。",
        "en": "The road was buried in snow.",
        "reason": "Resultative past is the natural use.",
    },
    (10, "埋", "埋没"): {
        "ja": "その名は歴史に埋没しました。",
        "en": "That name sank into history.",
        "reason": "埋没です is not how the noun-verb is used.",
    },
    (10, "向", "向く"): {
        "ja": "席が窓に向きます。",
        "en": "The seat faces the window.",
        "reason": "Inflect; dictionary-form dump.",
    },
    (10, "向", "向かう"): {
        "ja": "朝、海へ向かいます。",
        "en": "In the morning I head toward the sea.",
        "reason": "Inflect; dictionary-form dump.",
    },
    # Other clear errors / dictionary dumps / meta examples
    (2, "唱", "唱える"): {
        "ja": "寺で人がお経を唱えます。",
        "en": "Someone chants a sutra at the temple.",
        "reason": "Inflect; collocation お経を唱える was already good.",
    },
    (2, "唱", "名を唱える"): {
        "ja": "門の前で名を唱えます。",
        "en": "I state my name at the gate.",
        "reason": "Inflect the set phrase.",
    },
    (2, "唱", "呪文を唱える"): {
        "ja": "子どもが呪文を唱えます。",
        "en": "The child chants a spell.",
        "reason": "Inflect the set phrase.",
    },
    (2, "呂", "背筋（脊呂）"): {
        "review": "Surface includes a parenthetical teaching note, so no fully natural sentence can hide the artifact.",
        "reviewNote": "Kept 本に背筋（脊呂）と書いてあります。 The listed form is not a lexical word.",
    },
    (2, "亘", "亘る"): {
        "ja": "話は三時間に亘ります。",
        "en": "The talk spans three hours.",
        "reason": "A bridge spanning towns is わたる but usually かかる/渡る; に亘る takes duration/range.",
    },
    (2, "亘", "年亘"): {
        "review": "年亘 is not a standard modern word.",
        "reviewNote": "Meta example left in place: 古い記録に年亘とあります。",
    },
    (2, "亘", "問題に亘る"): {
        "ja": "話は多くの問題に亘ります。",
        "en": "The discussion covers many issues.",
        "reason": "Inflect.",
    },
    (2, "凹", "凹む"): {
        "ja": "この缶はすぐ凹みます。",
        "en": "This can dents easily.",
        "reason": "Inflect.",
    },
    (2, "千", "千切る"): {
        "ja": "パンを手で千切ります。",
        "en": "I tear the bread by hand.",
        "reason": "Inflect.",
    },
    (2, "旦", "旦"): {
        "ja": "古い文では朝を旦と書きます。",
        "en": "In old writing, morning is written as 旦.",
        "reason": "旦 as a free noun is archaic; a writing-note sentence is honest. Slight reword.",
    },
    (3, "昇", "昇る"): {
        "ja": "朝、太陽が昇ります。",
        "en": "The sun rises in the morning.",
        "reason": "Inflect.",
    },
    (3, "卜", "卜う"): {
        "ja": "星で明日を卜います。",
        "en": "I divine tomorrow from the stars.",
        "reason": "Inflect. Archaic verb kept in a matching context.",
    },
    (3, "占", "占う"): {
        "ja": "店で運を占います。",
        "en": "I have my fortune told at the shop.",
        "reason": "Inflect; カードで is a bit marked.",
    },
    (3, "上", "上がる"): {
        "ja": "午後に気温が上がります。",
        "en": "The temperature rises in the afternoon.",
        "reason": "Inflect.",
    },
    (3, "上", "上げる"): {
        "ja": "質問の時は手を上げます。",
        "en": "I raise my hand when I have a question.",
        "reason": "Inflect.",
    },
    (3, "下", "下がる"): {
        "ja": "夜は気温が下がります。",
        "en": "The temperature drops at night.",
        "reason": "Inflect.",
    },
    (3, "下", "下げる"): {
        "ja": "店は値段を下げます。",
        "en": "The shop lowers the price.",
        "reason": "Inflect.",
    },
    (3, "卓", "卓越"): {
        "ja": "彼の技術は卓越しています。",
        "en": "His skill is outstanding.",
        "exception": "卓越する/している is the natural predicate, not 卓越です.",
    },
    (3, "舌", "早口舌"): {
        "review": "早口舌 is not a standard lexical item.",
        "reviewNote": "Meta example left: この本に早口舌とあります。",
    },
    (3, "舌", "甘舌"): {
        "review": "甘舌 is not ordinary modern Japanese.",
        "reviewNote": "Meta example left: 昔の話に甘舌という言葉が出ます。",
    },
    (4, "貼", "貼る"): {
        "ja": "壁に写真を貼ります。",
        "en": "I put a photo on the wall.",
        "reason": "Inflect.",
    },
    (4, "貼", "値札を貼る"): {
        "ja": "店員は新しい商品に値札を貼ります。",
        "en": "The clerk puts price tags on the new products.",
        "reason": "Inflect the phrase.",
    },
    (4, "貼", "切手を貼る"): {
        "ja": "手紙に切手を貼ります。",
        "en": "I put a stamp on the letter.",
        "reason": "Inflect the phrase.",
    },
    (4, "貼", "掲示を貼る"): {
        "ja": "先生は廊下に掲示を貼ります。",
        "en": "The teacher posts a notice in the hallway.",
        "reason": "Inflect the phrase.",
    },
    (4, "見", "見る"): {
        "ja": "今夜、家族と映画を見ます。",
        "en": "I will watch a movie with my family tonight.",
        "reason": "Inflect.",
    },
    (4, "見", "見える"): {
        "ja": "ここから海が見えます。",
        "en": "You can see the sea from here.",
        "reason": "Inflect.",
    },
    (4, "見", "見せる"): {
        "ja": "友達に新しい本を見せます。",
        "en": "I show my new book to my friend.",
        "reason": "Inflect.",
    },
    (4, "頑", "頑張る"): {
        "ja": "明日の試合で頑張ります。",
        "en": "I will do my best in tomorrow's match.",
        "reason": "Inflect.",
    },
    (4, "負", "負かす"): {
        "ja": "弟は将棋で兄を負かします。",
        "en": "My younger brother beats my older brother at shogi.",
        "reason": "Inflect.",
    },
    (4, "負", "負う"): {
        "ja": "彼は大きな責任を負います。",
        "en": "He bears a great responsibility.",
        "reason": "Inflect.",
    },
    (4, "負", "負ける"): {
        "ja": "次の試合には負けるかもしれません。",
        "en": "We may lose the next match.",
        "exception": "かもしれない is slightly above the early band; losing a match is the natural frame for 負ける.",
    },
    (4, "負", "背負う"): {
        "ja": "兄は重い荷物を背負います。",
        "en": "My older brother carries heavy luggage on his back.",
        "reason": "Inflect.",
    },
    (4, "直", "直す"): {
        "ja": "午後に椅子を直します。",
        "en": "I will fix the chair this afternoon.",
        "reason": "Inflect.",
    },
    (6, "好", "好む"): {
        "ja": "父は静かな店を好みます。",
        "en": "My father prefers a quiet shop.",
        "reason": "そうです was unnecessary hearsay.",
    },
    (6, "貫", "貫く"): {
        "ja": "彼は最後まで考えを貫きます。",
        "en": "He sticks to the idea to the end.",
        "reason": "そうです was unnecessary; inflect.",
    },
    (6, "貫", "一貫"): {
        "ja": "先生の意見は一貫しています。",
        "en": "The teacher's opinion is consistent.",
        "exception": "一貫する/している, not 一貫です.",
    },
    (6, "兄", "兄弟"): {
        "ja": "あの兄弟はよく似ています。",
        "en": "Those brothers look very much alike.",
        "exception": "Natural 似ている, not 似ます.",
    },
    (6, "如", "少女如"): {
        "review": "少女如 is not a standard modern word.",
        "reviewNote": "Meta quotation left in the example.",
    },
    (6, "如", "権利如"): {
        "review": "権利如 is not a standard modern word.",
        "reviewNote": "Meta quotation left in the example.",
    },
    (6, "肖", "肖る"): {
        "ja": "私も兄の幸運に肖ります。",
        "en": "I hope to share in my brother's good fortune.",
        "reason": "つもりです was extra; inflect 肖る.",
    },
    (7, "砕", "砕ける"): {
        "ja": "波は岩に当たって砕けます。",
        "en": "The waves hit the rocks and break.",
        "reason": "Inflect.",
    },
    (7, "嗅", "嗅ぎ分ける"): {
        "ja": "この犬は二つの香りを嗅ぎ分けます。",
        "en": "This dog tells two scents apart.",
        "reason": "ことができます is later-band potential; the verb itself is enough.",
    },
    (8, "況", "況や"): {
        "ja": "大人にも難しいです。況や子どもには無理です。",
        "en": "It is hard even for adults, much less children.",
        "exception": "況や is a literary correlative; the two-clause shape is the word’s actual grammar.",
    },
    (8, "消", "消す"): {
        "ja": "部屋を出る時は電気を消します。",
        "en": "I turn off the light when I leave the room.",
        "reason": "約束です wrapping was unnecessary.",
    },
    (8, "消", "消える"): {
        "ja": "風でろうそくの火が消えました。",
        "en": "The candle went out in the wind.",
        "reason": "ことがあります was extra.",
    },
    (8, "泊", "泊まる"): {
        "ja": "今夜は湖のそばに泊まります。",
        "en": "I will stay by the lake tonight.",
        "reason": "予定です wrapping was unnecessary.",
    },
    (9, "測", "測る"): {
        "ja": "母は体温を測りました。",
        "en": "My mother took her temperature.",
        "reason": "Relative clause 測る道具 was later-band and hid the verb.",
    },
    (9, "吐", "吐く"): {
        "ja": "ゆっくり息を吐きます。",
        "en": "I breathe out slowly.",
        "reason": "The old sentence lectured about vomiting in public; 息を吐く is the everyday sense.",
    },
    (9, "填", "填める"): {
        "ja": "指輪を填めます。",
        "en": "I put on a ring.",
        "reason": "作業です wrapping; 填める naturally takes 指輪.",
    },
    (9, "灯", "灯をともす"): {
        "ja": "夕方に灯をともします。",
        "en": "I light a lamp in the evening.",
        "reason": "仕事です wrapping around the phrase.",
    },
    (9, "煩", "気に煩う"): {
        "ja": "小さなことを気に煩いません。",
        "en": "I do not fret over small things.",
        "reason": "必要はありません was later-band and weak.",
    },
    (2, "晶", "晶"): {
        "review": "Empty KML gloss; treated as the given name Akira.",
        "reviewNote": "晶は私の友達です。 is a name sentence. Gloss was blank on the source page.",
    },
    (10, "守", "守る"): {
        "review": "Source gloss is broken: “To protect, to守 keep”.",
        "reviewNote": "Sentence 約束を守る is kept as a good simple example. Do not silently rewrite the historical gloss.",
    },
    (1, "吾", "吾妻"): {
        "ja": "昔の人は東の国を吾妻と言いました。",
        "en": "People of old called the eastern lands Azuma.",
        "reason": "Listed senses are the wife/east-country readings, not a writing-instruction meta example.",
    },
    (2, "凸", "凸"): {
        "ja": "この石の上は凸です。",
        "en": "The top of this stone is convex.",
        "reason": "この形には凸があります is a generated existence frame, not how 凸 is used.",
    },
    (2, "凸", "凸出"): {
        "ja": "岩が海へ凸出しています。",
        "en": "The rock juts out into the sea.",
        "reason": "凸出 is a verb-noun; 壁に凸出があります does not demonstrate it.",
        "exception": "Natural 凸出する takes ている.",
    },
    (3, "卓", "卓抜"): {
        "ja": "彼女の演奏は卓抜しています。",
        "en": "Her performance is outstanding.",
        "reason": "卓抜です is possible but 卓抜している is the ordinary predicate.",
        "exception": "卓抜する/している, not a bare 卓抜です.",
    },
    (3, "只", "只"): {
        "ja": "私は只待つだけです。",
        "en": "I am merely waiting.",
        "reason": "Listed gloss is ‘only/just/merely’; 入場料は只です teaches the ‘free’ sense instead.",
    },
    (5, "昭", "昭告"): {
        "ja": "王は民に昭告しました。",
        "en": "The king issued a proclamation to the people.",
        "reason": "昭告 is a formal/historical proclamation, not a town bulletin with があります.",
    },
    (5, "貢", "納貢"): {
        "ja": "秋に米を納貢しました。",
        "en": "They paid tribute in rice in the autumn.",
        "reason": "納貢をします is an empty をします frame; historical tax/tribute needs a historical statement.",
    },
    (8, "原", "原子"): {
        "ja": "理科の授業で原子を学びます。",
        "en": "We study atoms in science class.",
        "reason": "水の中にも小さな原子があります is scientifically muddled as a beginner example.",
    },
    (9, "時", "時代"): {
        "ja": "今は平和な時代です。",
        "en": "This is a peaceful age.",
        "reason": "子どもの時代の話 is not how 時代 is used; ころ is the ordinary word for childhood.",
    },
    (10, "埋", "埋蔵"): {
        "ja": "この山には金が埋蔵されています。",
        "en": "Gold is buried in this mountain.",
        "reason": "埋蔵の金があります is an awkward noun modification; 埋蔵される is the actual verb.",
        "exception": "Natural 埋蔵 requires the passive.",
    },
    (2, "晶", "発光晶体"): {
        "review": "発光晶体 is not ordinary Japanese; the box example is a placeholder.",
        "reviewNote": "Left 箱に発光晶体があります。 pending a source-backed lexical decision.",
    },
    (2, "昌", "昌市"): {
        "review": "昌市 may be a place-name or a nonce ‘prosperous city’ compound.",
        "reviewNote": "Left 地図に昌市があります。",
    },
}


def apply() -> None:
    repaired = 0
    exceptions = []
    reviews = []
    ruby_n = 0
    tr_n = 0
    unchanged_review_only = 0
    for n in range(1, 11):
        path = HERE / f"lesson_{n:02d}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for ch in data["characters"]:
            for c in ch["compounds"]:
                key = (n, ch["kanji"], c["surface"])
                spec = REPAIRS.get(key)
                if not spec:
                    continue
                before_ja = c["example"]["ja"]
                before_en = c["example"]["en"]
                qa = dict(c.get("qa") or {})
                if spec.get("clear_exception"):
                    qa.pop("grammarException", None)
                    qa.pop("reason", None)
                if spec.get("exception"):
                    qa["grammarException"] = True
                    qa["reason"] = spec["exception"]
                    exceptions.append((n, c["surface"], c["reading"], spec["exception"], spec.get("ja", before_ja)))
                if spec.get("review"):
                    qa["review"] = True
                    qa["reviewNote"] = spec.get("reviewNote") or spec["review"]
                    reviews.append((n, c["surface"], c["reading"], c["meaning"], before_ja, spec["review"]))
                if spec.get("ja") and spec["ja"] != before_ja:
                    c["example"]["ja"] = spec["ja"]
                    c["example"]["en"] = spec["en"]
                    c["example"]["segments"] = ruby_segments(spec["ja"], c["surface"], c["reading"])
                    ruby_n += 1
                    tr_n += 1
                    repaired += 1
                elif spec.get("en") and spec["en"] != before_en:
                    c["example"]["en"] = spec["en"]
                    tr_n += 1
                    repaired += 1
                elif spec.get("review") and not spec.get("ja"):
                    unchanged_review_only += 1
                if qa:
                    c["qa"] = qa
                else:
                    c.pop("qa", None)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", path.name)
    print("this-run repaired", repaired, "ruby", ruby_n, "translations", tr_n)
    print("this-run exceptions", len(exceptions))
    print("this-run reviews", len(reviews), "review-only-no-rewrite", unchanged_review_only)

    # Recount from files so a second run still reports the full QA state.
    all_ex, all_rev = [], []
    total = 0
    with_qa_repair_marker = 0
    for i in range(1, 11):
        data = json.loads((HERE / f"lesson_{i:02d}.json").read_text(encoding="utf-8"))
        for ch in data["characters"]:
            for c in ch["compounds"]:
                total += 1
                qa = c.get("qa") or {}
                if qa.get("grammarException"):
                    all_ex.append(
                        {
                            "lesson": i,
                            "surface": c["surface"],
                            "reading": c["reading"],
                            "reason": qa.get("reason", ""),
                            "ja": c["example"]["ja"],
                        }
                    )
                if qa.get("review"):
                    all_rev.append(
                        {
                            "lesson": i,
                            "surface": c["surface"],
                            "reading": c["reading"],
                            "meaning": c["meaning"],
                            "ja": c["example"]["ja"],
                            "note": qa.get("reviewNote") or "",
                        }
                    )
    (HERE / "_qa_l01_10_report.json").write_text(
        json.dumps(
            {
                "total": total,
                "thisRunRepaired": repaired,
                "thisRunRuby": ruby_n,
                "thisRunTranslations": tr_n,
                "exceptions": all_ex,
                "reviews": all_rev,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("corpus exceptions", len(all_ex), "reviews", len(all_rev), "total", total)


if __name__ == "__main__":
    sys.exit(apply() or 0)
