#!/usr/bin/env python3
"""Sentence-quality polish for Compounds 38–61. Vocabulary and pages stay put."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from _build_lessons_01_10 import masu, ruby_segments
from _build_lessons_38_61 import TAGGER, mashita, has_word, analyze

HERE = Path(__file__).resolve().parent

KEEP_JA = {
    "現在、兄は京都に住んでいます。",
    "妹は今、大学に在学しています。",
    "店の在庫を夕方に数えました。",
    "叔父は長年、北海道に在住しています。",
    "予約は三日乃至五日かかります。",
    "博物館で古い木乃伊を見ました。",
    "乃木坂の駅で友達と会いました。",
    "古文に乃公という言葉が出ます。",
    "答えは乃ち、この道を行くことです。",
    "新しい機械の取扱説明書を読みました。",
    "彼女は今年、殻を破って歌いました。",
    "列車は桑名に止まりました。",
    "夏に桑の実を摘んで食べました。",
    "昔の役所には胥吏が働いていました。",
    "その瞬間、風が止みました。",
    "一瞬、雨が強くなりました。",
    "寒いと耳が冷たくなります。",
    "夜は耳栓をして寝ます。",
    "明日、耳鼻科へ行きます。",
    "その話は初耳です。",
    "電車のあと、耳鳴りがしました。",
    "母は写真を取りました。",
    "強い光に、小さく瞬きをしました。",
    "兄は歌舞伎を見たことがあります。",
    "来月、歌舞伎座へ行く予定です。",
    "伯父と駅で会いました。",
    "伯母と駅で会いました。",
    "伯父さんと道で会いました。",
    "授業で昔の風俗を学びました。",
    "この本には俗語が多いです。",
    "案内の人は「古い民俗です」と言いました。",
    "村の神社は山の近くです。",
    "神について、先生に聞きました。",
    "夜、古い神話の話を聞きました。",
    "警察は朝から捜査しています。",
    "山で捜索しなければならないと思います。",
    "父は鍵を捜してから、家へ帰りました。",
    "緊張すると、神経がとがります。",
    "弟は笑いながらドアを押します。",
    "その町は汎米会議を開きました。",
    "雨が降っても、学校へ行きます。",
    "説明が曖昧模糊で、まだ分かりません。",
    "歴史の本に采女の仕事が書いてあります。",
    "博物館で古い勾玉を見ました。",
    "寺の縁側に古い勾欄が残っています。",
}

HAND: dict[tuple[int, str], tuple[str, str, str | None]] = {
    (38, "存在"): (
        "古い寺は今も存在しています。",
        "The old temple still exists.",
        None,
    ),
    (38, "隻翼"): (
        "傷ついた鳥は隻翼のまま飛びました。",
        "The injured bird flew on with only one wing.",
        "隻翼 is literary; a narrative past sentence is the honest register.",
    ),
    (39, "友情"): (
        "二人の友情は今も続いています。",
        "The friendship between the two of them still continues.",
        None,
    ),
    (39, "友達"): (
        "公園で友達と会ってから、家へ帰りました。",
        "After meeting a friend in the park, I went home.",
        None,
    ),
}

WEAK_CORE = re.compile(
    r"(授業でXを学びました|本でXを知りました|ノートにXを書きました|辞書でXを調べました|"
    r"新聞でXを読みました|ラジオでXの話を聞きました|友達にXを教えました|"
    r"Xの話を聞きました|会社はXしています|Xしてから、手紙を書きました|"
    r"Xなので、少し休みました|来年もXを使うつもりです|この説明はXほど難しくありません|"
    r"兄はXという言葉を使います|Xのほうが簡単だと思います|Xについて考えました|"
    r"Xについて、先生に聞きました|私はXしたことがあります|"
    r"(父|兄|母|妹|私)はXします|"
    r"(妹|兄|母|父|私)はXしなければならないと思います|"
    r"今日はXです|Xは山の近くです|また、)"
)


def gloss_head(meaning: str) -> str:
    g = re.sub(r"^\([^)]*\)\s*", "", (meaning or "").strip())
    g = g.split(",")[0].split(";")[0].split("/")[0].split("(")[0].strip()
    return g or "it"


def en_do(who: str) -> str:
    return "do" if who == "私は" else "does"


def subjects(h: int) -> tuple[str, str]:
    who = ["私は", "兄は", "母は", "妹は", "父は"][h % 5]
    subj = {
        "私は": "I",
        "兄は": "My older brother",
        "母は": "My mother",
        "妹は": "My little sister",
        "父は": "My father",
    }[who]
    return who, subj


def fix_incidental(ja: str, segs: list[dict]) -> None:
    for seg in segs:
        if seg.get("text") == "米" and seg.get("reading") == "べい" and "米国" not in ja:
            seg["reading"] = "こめ"


def classify(ja: str, surface: str, meaning: str) -> str:
    if ja in KEEP_JA or (38, surface) in HAND or surface in {k[1] for k in HAND}:
        if ja in KEEP_JA:
            return "PASS"
    core = ja.replace(surface, "X")
    m = (meaning or "").lower()
    if WEAK_CORE.search(core) or ja.startswith("また、"):
        return "REPAIR" if any(
            x in core
            for x in (
                "手紙を書きました",
                "使うつもり",
                "ほど難しく",
                "言葉を使います",
                "のほうが簡単",
                "しなければならない",
                "会社はXしています",
                "今日はXです",
            )
        ) or ja.startswith("また、") else "POLISH"
    if has_word(m, "beheading", "pass away", "heart attack") and "授業で" in ja:
        return "PASS"
    return "PASS"


def collocate(lesson: int, surface: str, reading: str, meaning: str, h: int) -> tuple[str, str, str | None]:
    key = (lesson, surface)
    if key in HAND:
        return HAND[key]
    m = (meaning or "").lower()
    g = gloss_head(meaning).lower()
    who, subj = subjects(h)
    pos1, pos3, _ctype, ntok = analyze(surface)
    sahen = surface.endswith("する") or (ntok == 1 and pos3 == "サ変可能")
    verbish = pos1 == "動詞"
    adj = pos1 == "形容詞" or (surface.endswith("い") and reading.endswith("い") and pos1 != "名詞")

    if has_word(m, "beheading", "behead", "pass away", "passing away", "heart attack", "infarction", "murder"):
        return f"授業で{surface}を学びました。", f"We learned about {g} in class.", None

    if adj:
        if has_word(m, "near", "close", "far"):
            return f"駅は家から{surface}です。", f"The station is {g} from home.", None
        if has_word(m, "hard", "soft", "hot", "cold", "warm", "sweet", "spicy"):
            return f"このパンは{surface}です。", f"This bread is {g}.", None
        if has_word(m, "tall", "high", "low", "wide", "narrow", "long", "short"):
            return f"この木は{surface}です。", f"This tree is {g}.", None
        return f"今日の風は{surface}です。", f"Today's wind is {g}.", None

    if pos3 == "副詞可能" and has_word(m, "moment", "instant", "suddenly", "finally", "really", "furthermore", "again"):
        return f"{surface}、雨がやみました。", f"{g.capitalize()}, the rain stopped.", None

    if verbish and not sahen:
        form = mashita(surface) if (h % 2 == 0 or lesson >= 44) else masu(surface)
        if "を" in surface:
            return f"{who}{form}。", f"{subj} {g[3:] if g.startswith('to ') else g}.", None
        obj = ""
        if has_word(m, "search", "look"):
            obj = "鍵を"
        elif has_word(m, "eat"):
            obj = "ご飯を"
        elif has_word(m, "drink"):
            obj = "水を"
        elif has_word(m, "write"):
            obj = "名前を"
        elif has_word(m, "read"):
            obj = "手紙を"
        elif has_word(m, "push"):
            obj = "ドアを"
        elif has_word(m, "pull"):
            obj = "ドアを"
        elif has_word(m, "cut", "sever"):
            obj = "糸を"
        elif has_word(m, "refuse", "decline"):
            obj = "招待を"
        elif has_word(m, "pray"):
            obj = "神に"
            form = mashita(surface) if form.endswith("ました") else masu(surface)
            return f"{who}{obj}{form}。", f"{subj} {g[3:] if g.startswith('to ') else g}.", None
        elif has_word(m, "swear"):
            obj = "成功を"
        elif has_word(m, "break", "snap", "fold"):
            obj = "枝を"
        elif has_word(m, "angry"):
            return f"{who}遅く帰った兄に{form}。", f"{subj} {g[3:] if g.startswith('to ') else g}.", None
        if lesson >= 52 and h % 6 == 0 and obj:
            return (
                f"{who}{obj}{form}から、家へ帰りました。",
                f"{subj} {g[3:] if g.startswith('to ') else g}, then went home.",
                None,
            )
        if obj:
            return f"{who}{obj}{form}。", f"{subj} {g[3:] if g.startswith('to ') else g}.", None
        return f"{who}{form}。", f"{subj} {g[3:] if g.startswith('to ') else g}.", None

    if sahen:
        if has_word(m, "breathe", "breathing"):
            return f"息を吸って、ゆっくり{surface}します。", "I breathe in, then breathe slowly.", None
        if has_word(m, "change"):
            return f"明日の予定を{surface}しました。", f"I {g}d tomorrow's plans.", None
        if has_word(m, "renew"):
            return f"免許を{surface}しました。", f"I {g}d my license.", None
        if has_word(m, "protect"):
            return f"この森は法律で{surface}されています。", f"This forest is {g}ed by law.", None
        if has_word(m, "investigate"):
            return f"警察は朝から{surface}しています。", f"The police have been {g[:-1] if g.endswith('e') else g}ing since morning.", None
        if has_word(m, "search"):
            return f"山で人を{surface}しています。", f"They are {g}ing for people in the mountains.", None
        if has_word(m, "cooperate"):
            return f"皆で{surface}して、荷物を運びました。", f"Everyone {g}d and carried the bags.", None
        if has_word(m, "study"):
            return f"夜遅くまで{surface}しました。", f"I {g}d until late at night.", None
        if has_word(m, "absorb"):
            return f"スポンジが水を{surface}しました。", f"The sponge {g}ed the water.", None
        if has_word(m, "spread", "diffuse"):
            return f"新しい歌が町に{surface}しました。", f"The new song {g}d through town.", None
        if has_word(m, "capture"):
            return f"川で魚を{surface}しました。", f"I {g}d a fish in the river.", None
        if has_word(m, "acquire", "obtain"):
            return f"必要な資料を{surface}しました。", f"I {g}d the papers we needed.", None
        if has_word(m, "harvest"):
            return f"秋に米を{surface}しました。", f"We {g}ed the rice in autumn.", None
        if has_word(m, "care", "nursing"):
            return f"母は祖母の{surface}をしています。", f"Mother is doing {g} for grandmother.", None
        if has_word(m, "pass", "passing grade"):
            return f"弟は試験に{surface}しました。", f"My little brother {g} the exam.", None
        if lesson >= 48 and h % 4 == 0:
            return f"{surface}してから、家へ帰りました。", f"After {g}, I went home.", None
        if h % 3 == 0:
            return f"朝から{surface}しています。", f"I have been doing {g} since morning.", None
        return f"{who}{surface}しました。", f"{subj} did {g}.", None

    if has_word(m, "friend", "uncle", "aunt", "husband", "wife", "teacher", "doctor", "child", "twins", "cousin", "guard", "clerk", "official", "chef", "manager"):
        return f"{surface}と駅で会いました。", f"I met {g} at the station.", None
    if has_word(m, "tea", "milk", "rice", "fruit", "food", "meal", "bread", "fish", "meat", "sweet", "cake", "vegetable"):
        return f"夕食に{surface}を食べました。", f"I ate {g} for dinner.", None
    if has_word(m, "hand", "eye", "ear", "nose", "finger", "leg", "arm", "joint", "shoulder", "neck") and not surface.endswith(("科", "院")):
        return f"寒いと{surface}が冷たくなります。", f"When it is cold, my {g} gets cold.", None
    if surface.endswith(("科", "院", "局", "署")):
        return f"明日、{surface}へ行きます。", f"Tomorrow I will go to the {g}.", None
    if has_word(m, "place", "city", "town", "prefecture", "station", "temple", "shrine", "mountain", "river", "sea", "island", "lake"):
        if lesson >= 50 and h % 2 == 0:
            return f"来月、{surface}へ行く予定です。", f"I am scheduled to go to {surface} next month.", None
        return f"{surface}は山の近くです。", f"{g.capitalize()} is near the mountains.", None
    if has_word(m, "history"):
        return f"祖父は戦争の{surface}をよく話します。", f"Grandfather often talks about the {g} of the war.", None
    if has_word(m, "phone", "mobile"):
        return f"電車の中で{surface}を見ます。", f"I look at my {g} on the train.", None
    if has_word(m, "manual", "book", "letter", "newspaper"):
        return f"夜、{surface}を読みました。", f"I read the {g} at night.", None
    if has_word(m, "rain", "snow", "wind", "cloud", "storm"):
        return f"朝から{surface}が続いています。", f"The {g} has continued since morning.", None
    if has_word(m, "festival"):
        return f"夏に村の{surface}へ行きました。", f"In summer I went to the village {g}.", None
    if has_word(m, "god", "myth", "spirit", "soul"):
        return f"夜、古い{surface}の話を聞きました。", f"At night I heard an old story about {g}.", None
    if has_word(m, "inventory", "stock"):
        return f"店の{surface}を数えました。", f"I counted the shop's {g}.", None
    if has_word(m, "meeting", "conference"):
        return f"午後から{surface}があります。", f"There is a {g} in the afternoon.", None

    # capped situation bank — X occupies a real role
    bank = [
        (f"その{surface}が分かりません。", f"I do not understand that {g}."),
        (f"{surface}が足りません。", f"There is not enough {g}."),
        (f"{surface}を確かめました。", f"I checked the {g}."),
        (f"{surface}を忘れました。", f"I forgot the {g}."),
        (f"{surface}が気になります。", f"The {g} bothers me."),
        (f"昨日の{surface}は大変でした。", f"Yesterday's {g} was hard."),
        (f"{surface}が始まりました。", f"The {g} started."),
        (f"{surface}が終わりました。", f"The {g} ended."),
        (f"{surface}を頼まれました。", f"I was asked to handle the {g}."),
        (f"{surface}を断りました。", f"I declined the {g}."),
        (f"{surface}のおかげで助かりました。", f"The {g} saved me."),
        (f"{surface}が残っています。", f"Some {g} remains."),
        (f"机の上に{surface}を置きました。", f"I put the {g} on the desk."),
        (f"{surface}を持って駅へ行きました。", f"I took the {g} to the station."),
        (f"母に{surface}を見せました。", f"I showed mother the {g}."),
        (f"兄は{surface}を知りません。", f"My older brother does not know the {g}."),
        (f"{surface}が必要です。", f"{g.capitalize()} is necessary."),
        (f"{surface}はまだ早いです。", f"It is still early for {g}."),
        (f"小さな{surface}から始めました。", f"I started from a small {g}."),
        (f"{surface}を待っています。", f"I am waiting for the {g}."),
        (f"窓から{surface}が見えます。", f"I can see the {g} from the window."),
        (f"雨の日は{surface}を使いません。", f"I do not use {g} on rainy days."),
        (f"静かな{surface}が好きです。", f"I like quiet {g}."),
        (f"{surface}の音がします。", f"I hear the sound of {g}."),
        (f"古い{surface}を直しました。", f"I fixed the old {g}."),
        (f"新しい{surface}を買いました。", f"I bought a new {g}."),
        (f"{surface}を箱に入れました。", f"I put the {g} in a box."),
        (f"庭に{surface}があります。", f"There is {g} in the garden.") if has_word(m, "tree", "flower", "stone", "gate", "house", "well") else (f"{surface}が大切です。", f"{g.capitalize()} matters."),
        (f"この{surface}で十分です。", f"This {g} is enough."),
        (f"{surface}より、休んだほうがいいです。", f"It is better to rest than {g}.") if lesson >= 50 else (f"{surface}のあと、休みました。", f"After the {g}, I rested."),
        (f"{surface}なので、早く帰りました。", f"Because of {g}, I went home early.") if lesson >= 46 else (f"{surface}のあと、帰りました。", f"After the {g}, I went home."),
        (f"{surface}について母に聞きました。", f"I asked my mother about {g}.") if lesson >= 50 else (f"母に{surface}を聞きました。", f"I asked my mother about the {g}."),
        (f"{surface}のほうが分かりやすいです。", f"The {g} is easier to understand.") if lesson >= 50 else (f"{surface}は簡単です。", f"The {g} is easy."),
        (f"来年もこの{surface}を使うつもりです。", f"I intend to use this {g} next year too.") if lesson >= 50 else (f"またこの{surface}を使います。", f"I will use this {g} again."),
        (f"{who}{surface}したことがあります。", f"{subj} {'have' if who=='私は' else 'has'} done {g} before.") if sahen and lesson >= 45 else (f"{surface}を見たことがあります。", f"I have seen {g} before.") if lesson >= 45 and has_word(m, "mountain", "sea", "temple", "film", "picture", "flower", "tree", "festival", "castle") else (f"{surface}を思い出しました。", f"I remembered the {g}."),
    ]
    ja, en = bank[h % len(bank)]
    return ja, en, None


def main() -> int:
    lessons = [n for n in range(38, 62) if n != 42]
    stats = Counter()
    used: set[str] = set()
    changed = []
    ruby_changed = 0
    en_changed = 0
    gex_before = 0
    gex_after = 0
    review = []

    for n in lessons:
        path = HERE / f"lesson_{n:02d}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for ch in data["characters"]:
            for c in ch["compounds"]:
                stats["inspected"] += 1
                ja0 = c["example"]["ja"]
                en0 = c["example"]["en"]
                if (c.get("qa") or {}).get("grammarException"):
                    gex_before += 1
                label = classify(ja0, c["surface"], c["meaning"])
                if (n, c["surface"]) in HAND:
                    label = "POLISH" if ja0 != HAND[(n, c["surface"])][0] else "PASS"
                stats[label] += 1
                if label == "PASS":
                    used.add(ja0)
                    if (c.get("qa") or {}).get("grammarException"):
                        gex_after += 1
                    continue
                ja, en, exc = collocate(n, c["surface"], c["reading"], c["meaning"], abs(hash(f"{n}|{c['surface']}|{c['reading']}")))
                if ja in used:
                    ja = "昨日、" + ja if not ja.startswith("昨日") else "今朝、" + ja
                    if en and not en.startswith("Yesterday"):
                        en = "Yesterday, " + en[0].lower() + en[1:]
                used.add(ja)
                if ja != ja0:
                    stats["ja_changed"] += 1
                    changed.append(
                        {
                            "lesson": n,
                            "surface": c["surface"],
                            "label": label,
                            "before_ja": ja0,
                            "before_en": en0,
                            "after_ja": ja,
                            "after_en": en,
                        }
                    )
                    segs = ruby_segments(ja, c["surface"], c["reading"])
                    fix_incidental(ja, segs)
                    if "".join(s["text"] for s in segs) != ja:
                        segs = [{"text": ja}]
                        stats["ruby_err"] += 1
                    c["example"] = {"ja": ja, "en": en, "segments": segs}
                    ruby_changed += 1
                    en_changed += 1
                qa = dict(c.get("qa") or {})
                if exc:
                    qa["grammarException"] = True
                    qa["reason"] = exc
                if qa.get("grammarException"):
                    gex_after += 1
                if qa:
                    c["qa"] = qa
                elif "qa" in c and not qa:
                    pass
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("lesson", n, "done")

    # re-count cores
    pat = Counter()
    for n in lessons:
        data = json.loads((HERE / f"lesson_{n:02d}.json").read_text(encoding="utf-8"))
        for ch in data["characters"]:
            for c in ch["compounds"]:
                pat[c["example"]["ja"].replace(c["surface"], "X")] += 1
                if (c.get("qa") or {}).get("review"):
                    review.append((n, c["surface"]))

    report = {
        "stats": dict(stats),
        "gex_before": gex_before,
        "gex_after": gex_after,
        "ruby_changed": ruby_changed,
        "en_changed": en_changed,
        "top_cores_after": pat.most_common(20),
        "review_flags": review,
        "sample_changes": changed[:80],
        "n_changes": len(changed),
    }
    (HERE / "_polish_report_38_61.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(dict(stats))
    print("gex", gex_before, "->", gex_after)
    print("changed", len(changed), "ruby", ruby_changed)
    print("top after", pat.most_common(12))
    print("ruby_err", stats["ruby_err"])
    return 0 if stats["ruby_err"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
