#!/usr/bin/env python3
"""Pass 4: fix adverb misfires and spread leftover abstract frames."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from _build_lessons_01_10 import ruby_segments
from _polish_lessons_38_61 import HAND, KEEP_JA, gloss_head, subjects, fix_incidental

HERE = Path(__file__).resolve().parent

HAND.update(
    {
        (38, "取扱注意"): (
            "箱に取扱注意と書いてあります。",
            "Handle with care is written on the box.",
            None,
        ),
        (38, "更に"): (
            "風が強く、更に雨も降りました。",
            "The wind was strong, and it rained as well.",
            None,
        ),
        (45, "最も"): (
            "この村で最も高い山へ行きました。",
            "I went to the highest mountain in this village.",
            None,
        ),
        (61, "果して"): (
            "果して、彼は約束の時間に来ましたか。",
            "Did he really come at the promised time?",
            None,
        ),
        (45, "最近"): (
            "最近、兄は早く帰ります。",
            "Lately my older brother comes home early.",
            None,
        ),
        (61, "最近"): (
            "最近、この道は静かです。",
            "This road has been quiet lately.",
            None,
        ),
    }
)

GENERIC = (
    "来週まで続きそうです",
    "あとで、道を歩きましょう",
    "せいではありません",
    "静かに",
    "時間がなくなりました",
    "今日はXはありません",
    "メモを取りました",
    "が必要になりました",
    "まだ先です",
    "忘れないでください",
    "先に済ませました",
    "心配しています",
    "話は、もう終わりました",
    "に詳しいです",
    "頼みました",
    "小さな",
)


def frames(surface: str, g: str, gl: str, who: str, subj: str, lesson: int) -> list[tuple[str, str]]:
    return [
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
        (f"{surface}のあとで、少し歩きましょう。", f"After the {gl}, let's walk a little."),
        (f"{surface}をノートの上に書きました。", f"I wrote the {gl} at the top of my notebook."),
        (f"雨のせいではなく、{surface}のせいです。", f"It is because of {gl}, not the rain."),
        (f"{surface}が終わるまで、待ちます。", f"I will wait until the {gl} ends."),
        (f"初めて{surface}が分かりました。", f"I understood {gl} for the first time."),
        (f"{surface}は、まだ始まったばかりです。", f"The {gl} has only just begun."),
        (f"父は{surface}に反対しました。", f"Father opposed the {gl}."),
        (f"{surface}を理由に、休みました。", f"I took a rest because of {gl}."),
        (f"{surface}の意味を、辞書で見ました。", f"I looked up the meaning of {gl}."),
        (f"夜は{surface}を考えません。", f"At night I do not think about {gl}."),
        (f"{surface}より先に、手紙を出します。", f"I will send the letter before the {gl}."),
        (f"子供にも{surface}が分かります。", f"Even a child understands {gl}."),
        (f"{surface}が遅くなって、すみません。", f"Sorry that the {gl} is late."),
        (f"村では、その{surface}が有名です。", f"That {gl} is famous in the village."),
        (f"{surface}を止めないでください。", f"Please do not stop the {gl}."),
        (f"今の{surface}で十分です。", f"The present {gl} is enough."),
        (f"{surface}の前に、手を洗いました。", f"I washed my hands before the {gl}."),
        (f"誰も{surface}を知りません。", f"Nobody knows the {gl}."),
        (f"{surface}は来月からです。", f"The {gl} is from next month."),
        (f"短い{surface}でも助かります。", f"Even a short {gl} helps."),
        (f"{surface}を見て、安心しました。", f"I felt relieved when I saw the {gl}."),
        (f"途中で{surface}を変えました。", f"I changed the {gl} halfway."),
        (f"{surface}がない日は、静かです。", f"Days without {gl} are quiet."),
        (f"妹は{surface}が好きです。", f"My little sister likes {gl}."),
        (f"{surface}のあと、湯を飲みました。", f"After the {gl}, I drank hot water."),
        (f"その{surface}は、古い話です。", f"That {gl} is an old story."),
        (f"{surface}を一つ選びました。", f"I chose one {gl}."),
        (f"駅で{surface}を聞きました。", f"I heard about the {gl} at the station."),
        (f"{surface}が近いので、急ぎます。", f"The {gl} is near, so I hurry."),
        (f"長い{surface}に疲れました。", f"I grew tired of the long {gl}."),
        (f"{surface}は午後からです。", f"The {gl} is from the afternoon."),
        (f"私は{surface}を信じています。", f"I believe the {gl}.") if lesson >= 50 else (f"私は{surface}を知っています。", f"I know the {gl}."),
        (f"{surface}でも、行きます。", f"I will go even with {gl}."),
        (f"昨日の{surface}を覚えています。", f"I remember yesterday's {gl}."),
        (f"{surface}の順を間違えました。", f"I mixed up the order of the {gl}."),
        (f"春は{surface}が多いです。", f"There is a lot of {gl} in spring."),
        (f"{surface}を声に出して読みました。", f"I read the {gl} aloud."),
        (f"隣の人に{surface}を聞きました。", f"I asked the person next to me about the {gl}."),
        (f"{surface}が終わって、空が晴れました。", f"The {gl} ended, and the sky cleared."),
        (f"軽い{surface}から入りました。", f"I started with a light {gl}."),
        (f"{surface}は、まだ早いと思います。", f"I think it is still early for {gl}.") if lesson >= 50 else (f"{surface}は、まだ早いです。", f"It is still early for {gl}."),
        (f"机の{surface}を片付けました。", f"I put away the {gl} on the desk."),
        (f"{surface}の途中で、雨が降りました。", f"Rain fell in the middle of the {gl}."),
        (f"同じ{surface}を繰り返しました。", f"I repeated the same {gl}."),
        (f"{surface}があるので、助かります。", f"Having {gl} helps."),
    ]


def main() -> int:
    lessons = [n for n in range(38, 62) if n != 42]
    stats = Counter()
    ruby_err = 0
    used: set[str] = set()
    for n in lessons:
        path = HERE / f"lesson_{n:02d}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for ch in data["characters"]:
            for c in ch["compounds"]:
                used.add(c["example"]["ja"])
        for ch in data["characters"]:
            for c in ch["compounds"]:
                stats["inspected"] += 1
                ja0 = c["example"]["ja"]
                surf = c["surface"]
                if ja0 in KEEP_JA:
                    stats["PASS"] += 1
                    continue
                force = (n, surf) in HAND and ja0 != HAND[(n, surf)][0]
                generic = any(x in ja0 for x in GENERIC)
                if not force and not generic:
                    stats["PASS"] += 1
                    continue
                stats["REWRITE"] += 1
                if (n, surf) in HAND:
                    ja, en, exc = HAND[(n, surf)]
                else:
                    g = gloss_head(c["meaning"])
                    who, subj = subjects(abs(hash(surf + str(n))))
                    bank = frames(surf, g, g.lower(), who, subj, n)
                    ja, en = bank[abs(hash(f"p4|{n}|{surf}")) % len(bank)]
                    exc = None
                if ja in used and ja != ja0:
                    ja = "夕方、" + ja
                used.add(ja)
                segs = ruby_segments(ja, surf, c["reading"])
                fix_incidental(ja, segs)
                if "".join(s.get("text", "") for s in segs) != ja:
                    segs = [{"text": ja}]
                    ruby_err += 1
                c["example"] = {"ja": ja, "en": en, "segments": segs}
                if exc:
                    qa = dict(c.get("qa") or {})
                    qa["grammarException"] = True
                    qa["reason"] = exc
                    c["qa"] = qa
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("lesson", n)
    pat = Counter()
    for n in lessons:
        data = json.loads((HERE / f"lesson_{n:02d}.json").read_text(encoding="utf-8"))
        for ch in data["characters"]:
            for c in ch["compounds"]:
                pat[c["example"]["ja"].replace(c["surface"], "X")] += 1
    print(dict(stats), "ruby_err", ruby_err)
    print("top", pat.most_common(15))
    print("max", pat.most_common(1)[0])
    return 0 if ruby_err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
