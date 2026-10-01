#!/usr/bin/env python3
"""Second polish pass: break leftover mega-templates and semantic mismatches."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from _build_lessons_01_10 import masu, ruby_segments
from _build_lessons_38_61 import TAGGER, mashita, has_word, analyze
from _polish_lessons_38_61 import KEEP_JA, HAND, gloss_head, subjects, fix_incidental

HERE = Path(__file__).resolve().parent

NONSENSE = (
    "朝から",
    "してから、家へ帰りました",
    "はXしました。",
    "はまだ早いです",
    "このXで十分です",
    "を確かめました",
    "古いXを直しました",
    "窓からXが見えます",
    "のおかげで助かりました",
    "を箱に入れました",
    "が終わりました",
    "を忘れました",
    "机の上に",
    "が始まりました",
    "を頼まれました",
    "を断りました",
    "が足りません",
    "が気になります",
    "昨日のXは大変",
    "を持って駅へ",
    "雨の日はXを使いません",
    "静かなXが好き",
    "の音がします",
    "新しいXを買いました",
    "小さなXから",
    "を待っています",
    "Xより、休んだ",
)


def nonsense(core: str) -> bool:
    return any(x.replace("X", "X") in core or x in core for x in NONSENSE) or any(
        p in core
        for p in (
            "朝から",
            "家へ帰りました",
            "まだ早い",
            "で十分です",
            "確かめました",
            "古い",
            "窓から",
            "おかげで",
            "箱に入れ",
            "が終わり",
            "を忘れ",
            "机の上",
            "が始まり",
            "頼まれ",
            "断りました",
            "足りません",
            "気になります",
            "大変でした",
            "持って駅",
            "使いません",
            "が好きです",
            "の音がします",
            "買いました",
            "から始め",
            "待っています",
            "休んだほうが",
        )
    )


def kind(surface: str, meaning: str) -> str:
    m = (meaning or "").lower()
    pos1, pos3, _c, ntok = analyze(surface)
    if pos1 == "形状詞" or pos3 == "形状詞可能":
        return "naadj"
    if pos1 == "形容詞":
        return "iadj"
    if pos1 == "動詞":
        return "verb"
    if has_word(
        m,
        "friend",
        "uncle",
        "aunt",
        "husband",
        "wife",
        "teacher",
        "doctor",
        "child",
        "official",
        "officer",
        "clerk",
        "guard",
        "chef",
        "pitcher",
        "manager",
        "fellow",
        "guy",
        "cousin",
        "twins",
        "priest",
        "prince",
        "princess",
    ):
        return "person"
    if has_word(
        m,
        "city",
        "town",
        "prefecture",
        "station",
        "temple",
        "shrine",
        "mountain",
        "river",
        "sea",
        "island",
        "lake",
        "field",
        "road",
        "slope",
        "pass",
        "village",
    ):
        return "place"
    if has_word(m, "tea", "milk", "rice", "fruit", "food", "meal", "bread", "fish", "meat", "sweet", "cake"):
        return "food"
    if has_word(m, "hand", "eye", "ear", "nose", "finger", "leg", "arm", "body", "limb"):
        return "body"
    if has_word(m, "tree", "flower", "grass", "mulberry", "leaf", "plant"):
        return "plant"
    if ntok == 1 and pos3 == "サ変可能" and (
        m.startswith("to ")
        or has_word(
            m,
            "tion",
            "sion",
            "ment",
            "recovery",
            "attack",
            "defense",
            "investment",
            "renewal",
            "absorption",
            "partnership",
            "carrying",
            "reference",
            "diffusion",
            "rage",
            "sinking",
            "restoration",
            "rehabilitation",
            "hardening",
            "rigidity",
        )
        or any(m.endswith(x) for x in ("tion", "sion", "ment", "ing"))
    ):
        return "sahen"
    return "noun"


SAHEN_OBJ = [
    (("water", "absorb"), "スポンジが水を{s}しました。", "The sponge absorbed the water."),
    (("renew",), "免許を{s}しました。", "I renewed my license."),
    (("partner", "alliance"), "近くの店と{s}しました。", "We partnered with a nearby shop."),
    (("carry", "carrying"), "荷物を{s}しました。", "I carried the bags with me."),
    (("mention", "reference"), "手紙でその問題に{s}しました。", "I mentioned that problem in the letter."),
    (("spread", "diffus"), "新しい歌が町に{s}しました。", "The new song spread through town."),
    (("defend", "defense"), "兄は友達を{s}しました。", "My older brother defended his friend."),
    (("rage", "fury"), "母は遅く帰った兄に{s}しました。", "Mother flew into a rage at my brother who came home late."),
    (("invest",), "少しだけお金を{s}しました。", "I invested a little money."),
    (("attack",), "ニュースでその{s}を知りました。", "I heard about that attack on the news."),
    (("sink", "sinking"), "古い船が港で{s}しました。", "The old ship sank in the harbor."),
    (("recover",), "風邪から{s}してから、学校へ行きました。", "After recovering from a cold, I went to school."),
    (("restore", "rehabilit"), "壊れた橋を{s}しています。", "They are restoring the broken bridge."),
    (("harden",), "寒い朝、道が{s}しました。", "The road hardened on the cold morning."),
    (("rigid",), "緊張して体が{s}しました。", "My body went rigid from nerves."),
    (("change",), "明日の予定を{s}しました。", "I changed tomorrow's plans."),
    (("protect",), "この鳥は法律で{s}されています。", "This bird is protected by law."),
    (("breathe",), "息を吸って、ゆっくり{s}します。", "I breathe in, then breathe slowly."),
    (("coopera",), "皆で{s}して荷物を運びました。", "Everyone cooperated and carried the bags."),
    (("absorb", "adsorption", "suction"), "布が水を{s}しました。", "The cloth took up the water."),
    (("harvest",), "秋に米を{s}しました。", "We harvested the rice in autumn."),
    (("capture",), "川で魚を{s}しました。", "I caught a fish in the river."),
    (("study",), "夜遅くまで{s}しました。", "I studied until late at night."),
    (("pass", "grade"), "弟は試験に{s}しました。", "My little brother passed the exam."),
]


def rewrite(lesson: int, surface: str, reading: str, meaning: str, h: int) -> tuple[str, str, str | None]:
    if (lesson, surface) in HAND:
        return HAND[(lesson, surface)]
    m = (meaning or "").lower()
    g = gloss_head(meaning)
    gl = g.lower()
    who, subj = subjects(h)
    k = kind(surface, meaning)
    pos1, pos3, _c, ntok = analyze(surface)

    if has_word(m, "beheading", "behead", "pass away", "passing away", "heart attack", "infarction", "murder"):
        return f"授業で{surface}を学びました。", f"We learned about {gl} in class.", None

    if k == "iadj":
        if has_word(m, "near", "close"):
            return f"駅は家から{surface}です。", f"The station is {gl} from home.", None
        if has_word(m, "hard", "soft", "hot", "cold", "warm"):
            return f"このパンは{surface}です。", f"This bread is {gl}.", None
        return f"この道は{surface}です。", f"This road is {gl}.", None

    if k == "naadj":
        frames = [
            (f"山の景色は{surface}です。", f"The mountain view is {gl}."),
            (f"彼の仕事は{surface}です。", f"His work is {gl}."),
            (f"あの判断は{surface}でした。", f"That decision was {gl}."),
            (f"彼女の態度は{surface}です。", f"Her manner is {gl}."),
        ]
        return frames[h % 4][0], frames[h % 4][1], None

    if k == "verb":
        form = mashita(surface) if h % 2 == 0 else masu(surface)
        obj = ""
        if has_word(m, "search", "look"):
            obj = "鍵を"
        elif has_word(m, "eat"):
            obj = "ご飯を"
        elif has_word(m, "write"):
            obj = "名前を"
        elif has_word(m, "read"):
            obj = "手紙を"
        elif has_word(m, "push"):
            obj = "ドアを"
        elif has_word(m, "cut", "sever"):
            obj = "糸を"
        elif has_word(m, "refuse"):
            obj = "招待を"
        elif has_word(m, "pray"):
            return f"{who}神に{form}。", f"{subj} prayed.", None
        elif has_word(m, "break", "snap", "fold"):
            obj = "枝を"
        elif has_word(m, "angry"):
            return f"{who}遅く帰った兄に{form}。", f"{subj} got angry.", None
        return f"{who}{obj}{form}。", f"{subj} {gl[3:] if gl.startswith('to ') else gl}.", None

    if k == "sahen":
        for keys, ja, en in SAHEN_OBJ:
            if any(x in m for x in keys):
                return ja.format(s=surface), en, None
        # honest work/school use of a する-noun
        opts = [
            (f"仕事で{surface}が必要になりました。", f"{g} became necessary at work."),
            (f"その{surface}は、思ったより時間がかかりました。", f"That {gl} took longer than I thought."),
            (f"先生は{surface}の仕方を教えました。", f"The teacher showed us how to do {gl}."),
            (f"一度、{surface}を手伝いました。", f"I helped with {gl} once."),
        ]
        return opts[h % 4][0], opts[h % 4][1], None

    if k == "person":
        return f"{surface}と駅で会いました。", f"I met {gl} at the station.", None
    if k == "place":
        return f"休みに{surface}へ行きました。", f"I went to {surface} on a day off.", None
    if k == "food":
        return f"夕食に{surface}を食べました。", f"I ate {gl} for dinner.", None
    if k == "body":
        return f"寒いと{surface}が冷たくなります。", f"When it is cold, my {gl} gets cold.", None
    if k == "plant":
        return f"庭に{surface}が残っています。", f"{g} is still left in the garden.", None

    # phones / devices used as things despite サ変
    if has_word(m, "phone", "mobile"):
        return f"電車の中で{surface}を見ています。", f"I look at my {gl} on the train.", None
    if has_word(m, "coin", "money"):
        return f"財布に{surface}を入れました。", f"I put {gl} in my wallet.", None
    if has_word(m, "history", "fact"):
        return f"祖父は戦争の{surface}をよく話します。", f"Grandfather often talks about that {gl}.", None
    if has_word(m, "book", "letter", "manual", "board"):
        return f"壁の{surface}を読みました。" if "board" in m else f"夜、{surface}を読みました。", f"I read the {gl}.", None
    if has_word(m, "height", "stature", "length"):
        return f"服の{surface}を直しました。", f"I adjusted the {gl} of the clothes.", None
    if has_word(m, "dog", "cat", "bird", "fish", "animal"):
        return f"朝、{surface}と散歩しました。", f"In the morning I walked with the {gl}.", None
    if has_word(m, "story", "ghost"):
        return f"夜、{surface}を聞いて眠れませんでした。", f"I heard a {gl} at night and could not sleep.", None
    if has_word(m, "skill", "technique"):
        return f"兄の{surface}は、まだ私より上です。", f"My older brother's {gl} is still above mine.", None
    if has_word(m, "mineral", "stone", "rock"):
        return f"川原で{surface}を拾いました。", f"I picked up {gl} by the river.", None
    if has_word(m, "nail", "clipper"):
        return f"机の上に{surface}を置きました。", f"I put the {gl} on the desk.", None
    if has_word(m, "shell"):
        return f"浜で{surface}を拾いました。", f"I picked up a {gl} on the beach.", None
    if has_word(m, "stalk", "stem"):
        return f"花の{surface}を短く切りました。", f"I cut the {gl} of the flower short.", None
    if has_word(m, "prey"):
        return f"鳥が{surface}を加えて飛びました。", f"The bird flew off with its {gl}.", None
    if has_word(m, "mulberry"):
        return f"夏に{surface}の実を食べました。", f"In summer I ate the fruit of the {gl}.", None
    if has_word(m, "two-way", "both"):
        return f"この道は{surface}に通れます。", f"You can go both ways on this road.", None
    if has_word(m, "seed"):
        return f"鉢に{surface}が出てきました。", f"{g} came up in the pot.", None
    if has_word(m, "outstanding", "excellent"):
        return f"今日の料理は{surface}でした。", f"Today's cooking was {gl}.", None
    if has_word(m, "coin"):
        return f"自動販売機に{surface}を入れました。", f"I put a {gl} in the vending machine.", None

    # last-resort abstract/noun: situation, not classroom dump
    last = [
        (f"その{surface}が、まだはっきりしません。", f"That {gl} is still not clear."),
        (f"{surface}のことは、母に聞きました。", f"I asked my mother about the {gl}."),
        (f"今は{surface}より、休むほうが大切です。", f"Rest matters more than {gl} right now.")
        if lesson >= 50
        else (f"今は{surface}のあとで休みます。", f"I will rest after the {gl}."),
        (f"{surface}で困ったので、兄に助けてもらいました。", f"I had trouble with {gl}, so my older brother helped me."),
        (f"短い文で{surface}を説明しました。", f"I explained the {gl} in a short sentence."),
        (f"{surface}は、思ったより簡単でした。", f"The {gl} was easier than I had thought."),
        (f"雨の日は、その{surface}をやめました。", f"On a rainy day I stopped that {gl}."),
        (f"初めてその{surface}を知りました。", f"I learned of that {gl} for the first time."),
    ]
    return last[h % len(last)][0], last[h % len(last)][1], None


def main() -> int:
    lessons = [n for n in range(38, 62) if n != 42]
    # first pass: core frequencies
    items = []
    cores = Counter()
    for n in lessons:
        data = json.loads((HERE / f"lesson_{n:02d}.json").read_text(encoding="utf-8"))
        for ch in data["characters"]:
            for c in ch["compounds"]:
                ja = c["example"]["ja"]
                core = ja.replace(c["surface"], "X")
                cores[core] += 1
                items.append((n, c["surface"], core, ja))
    core_n = dict(cores)

    stats = Counter()
    used: set[str] = set()
    changed = []
    gex_before = gex_after = 0
    ruby_err = 0

    for n in lessons:
        path = HERE / f"lesson_{n:02d}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for ch in data["characters"]:
            for c in ch["compounds"]:
                ja0 = c["example"]["ja"]
                en0 = c["example"]["en"]
                core = ja0.replace(c["surface"], "X")
                if (c.get("qa") or {}).get("grammarException"):
                    gex_before += 1
                keep = ja0 in KEEP_JA or (n, c["surface"]) in HAND and ja0 == HAND[(n, c["surface"])][0]
                freq = core_n.get(core, 1)
                need = (not keep) and (freq >= 6 or nonsense(core))
                stats["inspected"] += 1
                if not need:
                    stats["PASS"] += 1
                    used.add(ja0)
                    if (c.get("qa") or {}).get("grammarException"):
                        gex_after += 1
                    continue
                stats["REWRITE"] += 1
                h = abs(hash(f"{n}|{c['surface']}|{c['reading']}|p2"))
                ja, en, exc = rewrite(n, c["surface"], c["reading"], c["meaning"], h)
                if ja in used:
                    ja = ("昨日、" + ja) if not ja.startswith("昨日") else ("夕方、" + ja)
                used.add(ja)
                if ja != ja0:
                    segs = ruby_segments(ja, c["surface"], c["reading"])
                    fix_incidental(ja, segs)
                    if "".join(s["text"] for s in segs) != ja:
                        segs = [{"text": ja}]
                        ruby_err += 1
                    c["example"] = {"ja": ja, "en": en, "segments": segs}
                    changed.append((n, c["surface"], ja0, en0, ja, en))
                    stats["ja_changed"] += 1
                qa = dict(c.get("qa") or {})
                if exc:
                    qa["grammarException"] = True
                    qa["reason"] = exc
                if qa.get("grammarException"):
                    gex_after += 1
                if qa:
                    c["qa"] = qa
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("lesson", n)

    pat = Counter()
    for n in lessons:
        data = json.loads((HERE / f"lesson_{n:02d}.json").read_text(encoding="utf-8"))
        for ch in data["characters"]:
            for c in ch["compounds"]:
                pat[c["example"]["ja"].replace(c["surface"], "X")] += 1
    print(dict(stats), "ruby_err", ruby_err, "gex", gex_before, gex_after)
    print("top", pat.most_common(15))
    report = {
        "stats": dict(stats),
        "ruby_err": ruby_err,
        "gex_before": gex_before,
        "gex_after": gex_after,
        "top": pat.most_common(20),
        "changes": [
            {"lesson": a, "surface": b, "before_ja": c, "before_en": d, "after_ja": e, "after_en": f}
            for a, b, c, d, e, f in changed[:100]
        ],
        "n_changes": len(changed),
    }
    (HERE / "_polish_report_38_61_pass2.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0 if ruby_err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
