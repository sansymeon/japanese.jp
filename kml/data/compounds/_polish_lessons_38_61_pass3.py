#!/usr/bin/env python3
"""Pass 3: rewrite last-resort mega-templates only, with capped collocation families."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from _build_lessons_01_10 import ruby_segments
from _build_lessons_38_61 import mashita, masu, has_word, analyze
from _polish_lessons_38_61 import KEEP_JA, HAND, gloss_head, subjects, fix_incidental

HERE = Path(__file__).resolve().parent

BAD = (
    "雨の日は、その",
    "思ったより簡単",
    "困ったので、兄",
    "のことは、母に聞き",
    "まだはっきりしません",
    "短い文で",
    "初めてその",
    "休むほうが大切",
    "あとで休みます",
    "一度、",
    "仕方を教えました",
    "思ったより時間が",
    "仕事で",
    "朝から",
    "手紙を書きました",
)


def bad(ja: str) -> bool:
    return any(x in ja for x in BAD)


def pick(capped: Counter, pairs: list[tuple[str, str]], cap: int = 8) -> tuple[str, str]:
    for ja, en in pairs:
        core = ja  # caller already has surface in ja; cap by full pattern key without digits
        key = "".join(ch if ch == "X" or ord(ch) < 128 else "X" if "\u4e00" <= ch <= "\u9fff" else ch for ch in ja)
        # simpler: cap on english pattern? Use normalized core replacing kana/kanji runs
        if capped[ja.split("。")[0][-6:] if len(ja) > 6 else ja] < cap:
            capped[ja.split("。")[0][-6:]] += 1
            return ja, en
    return pairs[-1]


def rewrite(lesson, surface, reading, meaning, h, capped: Counter) -> tuple[str, str, str | None]:
    if (lesson, surface) in HAND:
        return HAND[(lesson, surface)]
    m = (meaning or "").lower()
    g = gloss_head(meaning)
    gl = g.lower()
    who, subj = subjects(h)
    pos1, pos3, _c, ntok = analyze(surface)

    if has_word(m, "beheading", "pass away", "passing away", "heart attack", "infarction", "murder"):
        return f"授業で{surface}を学びました。", f"We learned about {gl} in class.", None

    # adverbs / connective
    if pos3 == "副詞可能" or has_word(m, "furthermore", "recently", "still", "really", "most", "finally", "again"):
        adv = [
            (f"{surface}、雨が強くなりました。", f"{g}, the rain grew stronger."),
            (f"{surface}、兄は帰ってきました。", f"{g}, my older brother came home."),
            (f"{surface}、風が止みました。", f"{g}, the wind stopped."),
        ]
        return adv[h % 3][0], adv[h % 3][1], None

    if pos1 == "形容詞":
        return f"この道は{surface}です。", f"This road is {gl}.", None
    if pos1 == "形状詞" or pos3 == "形状詞可能":
        na = [
            (f"山の景色は{surface}です。", f"The mountain view is {gl}."),
            (f"彼の仕事は{surface}でした。", f"His work was {gl}."),
            (f"あの判断は{surface}です。", f"That decision is {gl}."),
        ]
        return na[h % 3][0], na[h % 3][1], None

    if pos1 == "動詞":
        form = mashita(surface) if h % 2 == 0 else masu(surface)
        return f"{who}{form}。", f"{subj} {gl[3:] if gl.startswith('to ') else gl}.", None

    sahen = ntok == 1 and pos3 == "サ変可能" and not has_word(m, "phone", "mobile", "shop", "store")
    if sahen or surface.endswith("する"):
        pairs = [
            (f"昨日、事務所で{surface}しました。", f"Yesterday I did {gl} at the office."),
            (f"兄は丁寧に{surface}しました。", f"My older brother carefully did {gl}."),
            (f"{surface}のあと、お茶を飲みました。", f"After {gl}, I drank tea."),
            (f"朝、学校で{surface}しました。", f"In the morning I did {gl} at school."),
            (f"{surface}がうまくいきました。", f"The {gl} went well."),
            (f"母は昼から{surface}しています。", f"Mother has been doing {gl} since noon."),
            (f"雨でも{surface}を続けました。", f"I kept up the {gl} even in the rain."),
            (f"先生と一緒に{surface}しました。", f"I did {gl} together with the teacher."),
            (f"{surface}の準備をしました。", f"I prepared for the {gl}."),
            (f"夕方まで{surface}しました。", f"I did {gl} until evening."),
            (f"{who}{surface}してから、帰りました。", f"{subj} did {gl}, then went home."),
            (f"一度だけ{surface}したことがあります。", f"I have done {gl} just once.") if lesson >= 45 else (f"一度だけ{surface}しました。", f"I did {gl} just once."),
        ]
        ja, en = pairs[h % len(pairs)]
        return ja, en, None

    if has_word(
        m,
        "man",
        "woman",
        "friend",
        "uncle",
        "aunt",
        "official",
        "clerk",
        "teacher",
        "doctor",
        "child",
        "count",
        "collector",
        "manager",
        "fellow",
        "guy",
    ):
        return f"{surface}と道で会いました。", f"I met {gl} on the road.", None
    if has_word(m, "sweet", "sweets", "snack", "cake", "fruit", "food", "rice", "bread", "tea", "confection"):
        return f"お茶のあと、{surface}を食べました。", f"After tea I ate {gl}.", None
    if has_word(m, "hobby"):
        return f"兄の{surface}は絵を描くことです。", f"My older brother's {gl} is drawing.", None
    if has_word(m, "signal", "light"):
        return f"角の{surface}が赤になりました。", f"The {gl} on the corner turned red.", None
    if has_word(m, "kitchen", "bathroom", "shop", "store", "company"):
        return f"朝、{surface}を掃除しました。", f"In the morning I cleaned the {gl}.", None
    if has_word(m, "pencil", "brush", "book"):
        return f"新しい{surface}で名前を書きました。", f"I wrote my name with a new {gl}.", None
    if has_word(m, "travel", "trip"):
        return f"来月、海へ{surface}する予定です。", f"I plan to {gl} to the sea next month.", None
    if has_word(m, "smile"):
        return f"子供の{surface}を見て、安心しました。", f"I felt relieved seeing the child's {gl}.", None
    if has_word(m, "pine"):
        return f"庭の{surface}に雪が載っています。", f"Snow sits on the {gl} in the garden.", None
    if has_word(m, "law", "rule"):
        return f"新しい{surface}を壁に貼りました。", f"I posted the new {gl} on the wall.", None
    if has_word(m, "invitation"):
        return f"結婚式の{surface}が届きました。", f"The wedding {gl} arrived.", None
    if has_word(m, "funeral"):
        return f"昨日、村で{surface}がありました。", f"Yesterday there was a {gl} in the village.", None
    if has_word(m, "barefoot"):
        return f"夏は{surface}で川を歩きます。", f"In summer I walk in the river {gl}.", None
    if has_word(m, "result", "effect"):
        return f"努力の{surface}が、少しずつ出ています。", f"The {gl} of the effort is showing little by little.", None
    if has_word(m, "mind", "spirit", "soul"):
        return f"静かな寺は{surface}にいいです。", f"A quiet temple is good for the {gl}.", None
    if has_word(m, "task", "theme", "subject", "course"):
        return f"今日の{surface}は長いです。", f"Today's {gl} is long.", None
    if has_word(m, "faith", "trust", "confidence", "reliance"):
        return f"私はまだその人を{surface}しています。", f"I still {gl} that person.", None if "faith" not in m else None

    # concrete vs abstract fallbacks, many frames, capped by hash
    if has_word(
        m,
        "handle",
        "board",
        "coin",
        "stone",
        "shell",
        "tree",
        "flower",
        "bag",
        "box",
        "door",
        "window",
        "house",
        "gate",
        "bridge",
        "boat",
        "car",
        "road",
        "field",
        "cloth",
        "clothes",
        "hat",
        "shoe",
    ):
        pairs = [
            (f"店で{surface}を買いました。", f"I bought {gl} at the shop."),
            (f"家に{surface}を置きました。", f"I put the {gl} in the house."),
            (f"古い{surface}を直しています。", f"I am fixing the old {gl}."),
            (f"川のそばで{surface}を拾いました。", f"I picked up {gl} by the river."),
            (f"{surface}を持って歩きました。", f"I walked carrying the {gl}."),
            (f"雨で{surface}が濡れました。", f"The {gl} got wet in the rain."),
            (f"新しい{surface}は軽いです。", f"The new {gl} is light."),
            (f"兄は{surface}を貸してくれました。", f"My older brother lent me the {gl}."),
        ]
        return pairs[h % 8][0], pairs[h % 8][1], None

    pairs = [
        (f"{surface}が必要になりました。", f"{g} became necessary."),
        (f"その{surface}を忘れないでください。", f"Please do not forget that {gl}."),
        (f"{surface}の話は、もう終わりました。", f"Talk of the {gl} is already over."),
        (f"兄は{surface}に詳しいです。", f"My older brother knows {gl} well."),
        (f"{surface}で時間がなくなりました。", f"I ran out of time because of {gl}."),
        (f"静かに{surface}を待っています。", f"I am waiting quietly for the {gl}."),
        (f"{surface}は来週まで続きそうです。", f"The {gl} looks likely to continue until next week."),
        (f"母は{surface}を心配しています。", f"Mother is worried about the {gl}."),
        (f"{surface}のせいではありません。", f"It is not because of the {gl}."),
        (f"小さな{surface}でも十分です。", f"Even a small {gl} is enough."),
        (f"{surface}を先に済ませました。", f"I finished the {gl} first."),
        (f"今日は{surface}はありません。", f"There is no {gl} today."),
        (f"{surface}について、メモを取りました。", f"I took notes about the {gl}."),
        (f"その{surface}は、まだ先です。", f"That {gl} is still ahead."),
        (f"{who}{surface}を頼みました。", f"{subj} asked for the {gl}."),
        (f"{surface}のあとで、道を歩きましょう。", f"After the {gl}, let's walk the road."),
    ]
    ja, en = pairs[h % len(pairs)]
    return ja, en, None


def main() -> int:
    lessons = [n for n in range(38, 62) if n != 42]
    capped: Counter = Counter()
    stats = Counter()
    ruby_err = 0
    gex_b = gex_a = 0
    changed = []
    for n in lessons:
        path = HERE / f"lesson_{n:02d}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        used = set()
        for ch in data["characters"]:
            for c in ch["compounds"]:
                used.add(c["example"]["ja"])
        for ch in data["characters"]:
            for c in ch["compounds"]:
                stats["inspected"] += 1
                ja0, en0 = c["example"]["ja"], c["example"]["en"]
                if (c.get("qa") or {}).get("grammarException"):
                    gex_b += 1
                if ja0 in KEEP_JA or ((n, c["surface"]) in HAND and ja0 == HAND[(n, c["surface"])][0]):
                    stats["PASS"] += 1
                    if (c.get("qa") or {}).get("grammarException"):
                        gex_a += 1
                    continue
                if not bad(ja0):
                    stats["PASS"] += 1
                    if (c.get("qa") or {}).get("grammarException"):
                        gex_a += 1
                    continue
                stats["REWRITE"] += 1
                h = abs(hash(f"p3|{n}|{c['surface']}|{c['reading']}"))
                ja, en, exc = rewrite(n, c["surface"], c["reading"], c["meaning"], h, capped)
                if ja in used:
                    ja = "今朝、" + ja if not ja.startswith("今朝") else "夕方、" + ja
                used.add(ja)
                segs = ruby_segments(ja, c["surface"], c["reading"])
                fix_incidental(ja, segs)
                if "".join(s.get("text", "") for s in segs) != ja:
                    segs = [{"text": ja}]
                    ruby_err += 1
                c["example"] = {"ja": ja, "en": en, "segments": segs}
                changed.append((n, c["surface"], ja0, ja, en))
                qa = dict(c.get("qa") or {})
                if exc:
                    qa["grammarException"] = True
                    qa["reason"] = exc
                if qa.get("grammarException"):
                    gex_a += 1
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
    print(dict(stats), "ruby_err", ruby_err, "gex", gex_b, gex_a)
    print("top", pat.most_common(12))
    (HERE / "_polish_report_38_61_pass3.json").write_text(
        json.dumps(
            {
                "stats": dict(stats),
                "ruby_err": ruby_err,
                "gex": [gex_b, gex_a],
                "top": pat.most_common(15),
                "n_changes": len(changed),
                "samples": [{"lesson": a, "surface": b, "before": c, "after": d, "en": e} for a, b, c, d, e in changed[:40]],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0 if ruby_err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
