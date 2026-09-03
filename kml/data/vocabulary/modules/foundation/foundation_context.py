"""Presentation-layer context expansions for Foundation F1–F6.

Locked target headwords and sequence live in foundation_module.json.
This file only adds short Japanese after a target.

Coverage: expansions never receive target credit. The bold target is what
the learner is responsible for; everything else is an invitation.

Each line is a valid stopping point. Later lines are invitations, not
prerequisites. Markup {漢字|かんじ} becomes ruby in the exhibition JSON.

Foundation may deliberately preview useful Japanese (〜たい, 〜ましょう,
な-adjectives, て-form, あります, counters, time, casual speech, etc.) so
it can return later as a target. Preview is not a requirement to cram
grammar into every item, and it is never taught merely because it appears.
"""

from __future__ import annotations

LEARNER_NOTE = "Each step is optional. Follow the Japanese as far as you like."


def sh(jp: str, en: str, where: str) -> dict:
    return {"jp": jp, "en": en, "source": "start-here", "startHere": where}


def x(markup: str, en: str) -> dict:
    return {"m": markup, "en": en, "source": "expansion"}


# jp → expansions. Every expansion must stand alone as a complete stopping point.
CONTEXT: dict[str, list[dict]] = {
    # ── F1 わたしと あなた ──────────────────────────────────────────
    "わたし": [
        x("わたしの", "my / mine"),
        x("これは{私|わたし}の。", "This is mine."),
        x("これは{私|わたし}の{猫|ねこ}です。", "This is my cat."),
    ],
    "あなた": [
        x("あなたの", "your / yours"),
        x("あなたの{犬|いぬ}", "your dog"),
        x("あなたの{犬|いぬ}はどれですか。", "Which one is your dog?"),
    ],
    "だれ": [
        x("だれ？", "Who?"),
        x("あの{方|かた}はだれですか。", "Who is that person?"),
    ],
    "これ": [
        sh("これは ほんです。", "This is a book.", "Room 7, Room 40"),
        sh("これは なんですか。", "What is this?", "Room 9"),
        x("これは{面白|おもしろ}いです。", "This is interesting."),
    ],
    "それ": [
        x("それは{何|なん}？", "What's that?"),
        x("それ、おいしい？", "Is that good? / Does that taste good?"),
        x("それ、どこで{買|か}ったの？", "Where did you buy that?"),
    ],
    "あれ": [
        x("あれ、{見|み}て。", "Look at that."),
        x("あれは{何|なん}ですか。", "What's that?"),
        x("あれは{富士山|ふじさん}です。", "That's Mt. Fuji."),
    ],
    "この": [
        x("この{本|ほん}", "this book"),
        x("この{本|ほん}を{買|か}いました。", "I bought this book."),
        x("{昨日|きのう}、この{本|ほん}を{買|か}いました。", "Yesterday, I bought this book."),
    ],
    "その": [
        x("その{人|ひと}", "that person"),
        x("その{人|ひと}、{知|し}ってる？", "Do you know that person?"),
        x(
            "その{人|ひと}、{昨日|きのう}{会|あ}った{人|ひと}じゃないですか？",
            "Isn't that the person we met yesterday?",
        ),
    ],
    "あの": [
        x("あの{店|みせ}", "that shop"),
        x("あの{店|みせ}、もう{閉|し}まった。", "That shop already closed."),
    ],
    "ここ": [
        x("ここが{好|す}き。", "I like it here."),
        x(
            "ここから{駅|えき}まで{歩|ある}いて{何分|なんぷん}ですか？",
            "How many minutes is it from here to the station on foot?",
        ),
    ],
    "そこ": [
        x("そこに{置|お}いて。", "Put it there."),
        x("そこに{座|すわ}ってもいいですか？", "May I sit there?"),
    ],
    "あそこ": [
        x("あそこに{山|やま}があります。", "There is a mountain over there."),
        x("あそこにきれいな{山|やま}があります。", "There is a beautiful mountain over there."),
    ],
    "どこ": [
        x("どこ？", "Where?"),
        x("{駅|えき}はどこですか。", "Where is the station?"),
        x("{地下鉄|ちかてつ}の{駅|えき}はどこですか。", "Where is the subway station?"),
    ],
    "なん": [
        sh("おなまえは なんですか。", "What is your name?", "Room 3, Room 4 (Budokan name song)"),
        sh("これは なんですか。", "What is this?", "Room 9"),
        x("{今日|きょう}、{何|なに}を{食|た}べたいですか？", "What do you want to eat today?"),
    ],
    "はい": [
        sh("はい、げんきです。", "Yes, I'm well.", "Room 1"),
        x("はい、わかりました。", "Okay, I understand."),
        x(
            "「{明日|あした}は{九時|くじ}からです。」\n「はい。」",
            "“Tomorrow starts at nine.”\n“Okay.”",
        ),
    ],
    "いいえ": [
        x("いいえ、{違|ちが}います。", "No, that's not right."),
        x(
            "「これ、{全部|ぜんぶ}{一人|ひとり}で{食|た}べるんですか？」\n「いいえ、みんなで{食|た}べましょう！」",
            "“Are you going to eat all of this by yourself?”\n“No, let's all eat together!”",
        ),
    ],
    "こんにちは": [
        x(
            "「こんにちは。{今日|きょう}は{暑|あつ}いですね。」",
            "Hello. It's hot today, isn't it?",
        ),
        x(
            "「そうですね。でも、{風|かぜ}が{気持|きも}ちいいです。」",
            "Yes, it is. But the breeze feels nice.",
        ),
    ],
    "おはよう": [
        x("おはようございます。", "Good morning."),
        x(
            "「おはようございます。よく{眠|ねむ}れましたか？」",
            "Good morning. Did you sleep well?",
        ),
        x(
            "「はい、よく{眠|ねむ}れました。{今日|きょう}はいい{天気|てんき}ですね。」",
            "Yes, I slept well. Nice weather today, isn't it?",
        ),
    ],
    "こんばんは": [
        x(
            "「こんばんは。{遅|おそ}くなってすみません。」",
            "Good evening. Sorry I'm late.",
        ),
        x(
            "「{大丈夫|だいじょうぶ}ですよ。どうぞ{入|はい}ってください。」",
            "It's fine. Please come in.",
        ),
        x(
            "「ありがとうございます。お{邪魔|じゃま}します。」",
            "Thank you. Excuse me for intruding.",
        ),
    ],
    "さようなら": [
        x("「{先生|せんせい}、さようなら！」", "Goodbye, teacher!"),
        x("「さようなら。また{明日|あした}。」", "Goodbye. See you tomorrow."),
        x(
            "「じゃあ、また{明日|あした}。」\n「はい、また{明日|あした}。」",
            "“Well then, see you tomorrow.”\n“Yes, see you tomorrow.”",
        ),
    ],
    "よろしく": [
        x(
            "「はじめまして。ジョンです。よろしくお{願|ねが}いします。」",
            "Nice to meet you. I'm John.",
        ),
        x(
            "「はじめまして。マリアです。こちらこそ、よろしくお{願|ねが}いします。」",
            "Nice to meet you. I'm Maria. Likewise.",
        ),
        x(
            "「{明日|あした}の{会議|かいぎ}、よろしくお{願|ねが}いします。」",
            "Thanks in advance for your help with tomorrow's meeting.",
        ),
        x("「じゃ、よろしく！」", "Okay, I'm counting on you! / Thanks!"),
    ],
    "げんき": [
        sh("げんきですか？", "How are you?", "Room 1"),
        sh("はい、げんきです。", "Yes, I'm well.", "Room 1"),
        x(
            "「お{母|かあ}さんはお{元気|げんき}ですか？」",
            "How is your mother?",
        ),
        x(
            "「はい、とても{元気|げんき}です。{毎朝|まいあさ}、{公園|こうえん}を{散歩|さんぽ}しています。」",
            "Yes, she's very well. She takes a walk in the park every morning.",
        ),
    ],
    "ありがとう": [
        x(
            "「これ、どうぞ。」\n「ありがとう！」",
            "“Here you go.”\n“Thanks!”",
        ),
        x(
            "「{手伝|てつだ}ってくれて、ありがとうございます。」",
            "Thank you for helping me.",
        ),
        x(
            "「{昨日|きのう}は{本当|ほんとう}にありがとう。とても{助|たす}かりました。」",
            "Thank you so much for yesterday. You really helped me.",
        ),
    ],
    "すみません": [
        x(
            "「すみません、{駅|えき}はどこですか？」",
            "Excuse me, where is the station?",
        ),
        x(
            "「すみません、これをお{願|ねが}いします。」",
            "Excuse me, this one please.",
        ),
        x("「{遅|おそ}くなって、すみません。」", "I'm sorry I'm late."),
        x(
            "「これ、{落|お}としましたよ。」\n「あっ、すみません。ありがとうございます！」",
            "“You dropped this.”\n“Oh! Thank you!”",
        ),
    ],
    "だいじょうぶ": [
        sh("だいじょうぶですか？", "Are you okay?", "Room 1"),
        sh("はい、だいじょうぶです。", "Yes, I'm okay.", "Room 1"),
        x(
            "「コーヒー、もう{一杯|いっぱい}いかがですか？」\n「ありがとうございます。でも、だいじょうぶです。」",
            "“Would you like another cup of coffee?”\n“Thank you, but I'm fine.”",
        ),
        x(
            "「{一人|ひとり}で{大丈夫|だいじょうぶ}？」\n「うん、{大丈夫|だいじょうぶ}！」",
            "“Will you be okay by yourself?”\n“Yeah, I'll be fine!”",
        ),
    ],
    # ── F2 うちの ひと ─────────────────────────────────────────────
    # A small family/home world. Recurring previews (〜みたい, 〜でしょう,
    # おいしい／おいしそう, later F2 targets) are intentional.
    "おかあさん": [
        x("お{母|かあ}さん", "mother"),
        x("お{母|かあ}さんが{作|つく}ってくれた。", "Mom made this for me."),
        x(
            "これ、お{母|かあ}さんが{作|つく}ってくれたんです。おいしそうでしょう？",
            "My mother made this for me. Looks delicious, doesn't it?",
        ),
    ],
    "おとうさん": [
        x("お{父|とう}さん", "father"),
        x("お{父|とう}さんはまだ{帰|かえ}ってない。", "Dad isn't home yet."),
        x(
            "{今日|きょう}は{仕事|しごと}が{忙|いそが}しいみたい。",
            "It looks like work is busy today.",
        ),
    ],
    "おねえさん": [
        x("お{姉|ねえ}さん", "older sister"),
        x("お{姉|ねえ}さんは{大学生|だいがくせい}ですか？", "Is your older sister a university student?"),
        x(
            "「はい。{東京|とうきょう}の{大学|だいがく}に{通|かよ}っています。」",
            "Yes. She goes to university in Tokyo.",
        ),
    ],
    "おにいさん": [
        x("お{兄|にい}さんは{出|で}かけてる。", "Older brother's gone out."),
        x("どこに{行|い}ったの？", "Where did he go?"),
        x(
            "{友達|ともだち}と{映画|えいが}を{見|み}に{行|い}ったみたい。",
            "Looks like he went to see a movie with a friend.",
        ),
    ],
    "いもうと": [
        x("{妹|いもうと}", "younger sister"),
        x("{妹|いもうと}が{泣|な}いてる。", "My little sister is crying."),
        x("どうしたの？", "What happened?"),
        x("{転|ころ}んじゃったみたい。", "Looks like she fell down."),
    ],
    "おとうと": [
        x("{弟|おとうと}", "younger brother"),
        x("{弟|おとうと}、まだ{小|ちい}さい。", "My little brother is still young."),
        x("でも、{何|なん}でも{自分|じぶん}でやりたがる。", "But he wants to do everything by himself."),
        x("かわいいでしょう？", "Cute, isn't he?"),
    ],
    "おばあさん": [
        x("お{婆|ばあ}さんの{家|いえ}。", "Grandmother's house."),
        x(
            "{夏休|なつやす}みにお{婆|ばあ}さんの{家|いえ}に{行|い}きます。",
            "We're going to Grandma's house during summer vacation.",
        ),
        x("お{婆|ばあ}さんの{料理|りょうり}はいつもおいしい。", "Grandma's cooking is always delicious."),
        x("{今日|きょう}もおいしそう！", "Looks delicious today, too!"),
    ],
    "おじいさん": [
        x("お{爺|じい}さんが{庭|にわ}にいる。", "Grandfather is in the garden."),
        x("{何|なに}をしているの？", "What's he doing?"),
        x(
            "{花|はな}に{水|みず}をやってる。{毎朝|まいあさ}の{日課|にっか}なんだ。",
            "He's watering the flowers. It's his morning routine.",
        ),
    ],
    "こども": [
        x("{子供|こども}が{三人|さんにん}。", "Three children."),
        x(
            "{子供|こども}が{三人|さんにん}、{公園|こうえん}で{遊|あそ}んでいる。",
            "Three children are playing in the park.",
        ),
        x("{楽|たの}しそうですね。", "They look like they're having fun, don't they?"),
    ],
    "あかちゃん": [
        x("{赤|あか}ちゃん、{寝|ね}てる。", "The baby's asleep."),
        x("しーっ、{起|お}こさないで。", "Shh, don't wake the baby."),
        x("やっと{寝|ね}たところだから。", "They've only just fallen asleep."),
    ],
    "うち": [
        x("うちに{帰|かえ}る。", "I'm going home."),
        x("うちで{待|ま}ってる。", "I'll wait at home."),
        x("{今日|きょう}、うちに{来|こ}ない？", "Want to come over today?"),
        x("いいよ。{何時|なんじ}ごろ？", "Sure. About what time?"),
    ],
    "いえ": [
        x("この{家|いえ}、{古|ふる}い。", "This house is old."),
        x("でも、きれいですね。", "But it's beautiful, isn't it?"),
        x("{祖父|そふ}が{建|た}てた{家|いえ}なんです。", "It's a house my grandfather built."),
    ],
    "ひと": [
        x("あの{人|ひと}", "that person"),
        x("あの{人|ひと}、だれ？", "Who's that person?"),
        x(
            "{田中|たなか}さん。とても{優|やさ}しい{人|ひと}だよ。",
            "That's Tanaka-san. He's a very kind person.",
        ),
        x(
            "{困|こま}ったとき、いつも{助|たす}けてくれる。",
            "Whenever I'm in trouble, he always helps me.",
        ),
    ],
    "ともだち": [
        x("{友達|ともだち}と{会|あ}う。", "I'm meeting a friend."),
        x(
            "{今日|きょう}は{友達|ともだち}と{会|あ}う{約束|やくそく}がある。",
            "I have plans to meet a friend today.",
        ),
        x("どこで{会|あ}うの？", "Where are you meeting?"),
        x(
            "{駅|えき}の{前|まえ}。いっしょにご{飯|はん}を{食|た}べる{予定|よてい}。",
            "In front of the station. We're planning to eat together.",
        ),
    ],
    "かぞく": [
        x("{家族|かぞく}みんなで。", "The whole family together."),
        x(
            "{日曜日|にちようび}は{家族|かぞく}みんなで{出|で}かけます。",
            "On Sundays, the whole family goes out together.",
        ),
        x("{今週|こんしゅう}はどこに{行|い}くの？", "Where are you going this week?"),
        x("{海|うみ}に{行|い}こうと{思|おも}ってる。", "We're thinking of going to the sea."),
    ],
    "みんな": [
        x("{家族|かぞく}みんなで。", "The whole family together."),
        x("みんな、{準備|じゅんび}できた？", "Everyone, are you ready?"),
        x("「うん、{行|い}こう！」", "Yeah, let's go!"),
        x(
            "みんなで{食|た}べると、もっとおいしいね。",
            "When everyone eats together, it's even more delicious.",
        ),
    ],
    "せんせい": [
        x("{先生|せんせい}", "teacher"),
        x(
            "{田中|たなか}{先生|せんせい}、{今|いま}いらっしゃいますか？",
            "Is Tanaka-sensei here now?",
        ),
        x(
            "すみません、{今|いま}、{授業中|じゅぎょうちゅう}です。",
            "I'm sorry, he's in class right now.",
        ),
        x(
            "{授業|じゅぎょう}は{何時|なんじ}に{終|お}わりますか？",
            "What time does class finish?",
        ),
    ],
    "おとこのこ": [
        x("{男|おとこ}の{子|こ}", "boy"),
        x("あの{男|おとこ}の{子|こ}、{何|なに}してるの？", "What's that boy doing?"),
        x("{犬|いぬ}と{遊|あそ}んでる。", "He's playing with a dog."),
        x("{楽|たの}しそうだね。", "Looks like he's having fun."),
    ],
    "おんなのこ": [
        x("{女|おんな}の{子|こ}", "girl"),
        x(
            "あの{女|おんな}の{子|こ}、{何|なに}を{読|よ}んでるの？",
            "What's that girl reading?",
        ),
        x("{日本|にほん}の{昔話|むかしばなし}みたい。", "Looks like a Japanese folktale."),
        x(
            "{面白|おもしろ}そう。{私|わたし}も{読|よ}んでみたい。",
            "Looks interesting. I'd like to read it too.",
        ),
    ],
    "おなまえ": [
        sh("おなまえは なんですか？", "What's your name?", "Room 3, Room 4 (Budokan name song)"),
        x(
            "「お{名前|なまえ}は{何|なん}ですか？」\n「マリアです。」",
            "“What's your name?”\n“I'm Maria.”",
        ),
        x(
            "「お{名前|なまえ}、もう{一度|いちど}お{願|ねが}いします。」\n「マリアです。マ・リ・ア。」",
            "“Your name once more, please.”\n“Maria. Ma-ri-a.”",
        ),
    ],
    "ひとり": [
        x(
            "これ、{全部|ぜんぶ}{一人|ひとり}で{食|た}べるんですか？",
            "Are you going to eat all of this by yourself?",
        ),
        x("{一人|ひとり}で", "alone / by oneself"),
        x("{一人|ひとり}で{行|い}くの？", "Are you going by yourself?"),
        x("「うん。でも、ちょっと{心配|しんぱい}。」", "Yeah. But I'm a little worried."),
        x(
            "「{大丈夫|だいじょうぶ}。{着|つ}いたら{連絡|れんらく}してね。」",
            "You'll be fine. Let me know when you arrive.",
        ),
    ],
    "やさしい": [
        x("{優|やさ}しい{人|ひと}", "a kind person"),
        x(
            "{田中|たなか}{先生|せんせい}はとても{優|やさ}しい。",
            "Tanaka-sensei is very kind.",
        ),
        x(
            "「{日本語|にほんご}がまだ{上手|じょうず}じゃないんですが……」",
            "My Japanese isn't very good yet…",
        ),
        x(
            "「{大丈夫|だいじょうぶ}。ゆっくり{話|はな}しますよ。」",
            "That's okay. I'll speak slowly.",
        ),
        x("{優|やさ}しい{先生|せんせい}ですね。", "What a kind teacher."),
    ],
    "かわいい": [
        x("かわいい！", "So cute!"),
        x(
            "「{見|み}て、{赤|あか}ちゃん{笑|わら}ってる！」\n「ほんとだ。かわいいね。」",
            "“Look, the baby's smiling!”\n“You're right. So cute.”",
        ),
        x(
            "「このカバン、かわいい！」\n「{似合|にあ}いそう。{買|か}うの？」",
            "“This bag is cute!”\n“Looks like it would suit you. Are you going to buy it?”",
        ),
    ],
    "いぬ": [
        x("{犬|いぬ}", "dog"),
        x(
            "「この{犬|いぬ}、かわいいですね。」\n「ありがとうございます。」",
            "This dog is cute, isn't it?\nThank you.",
        ),
        x(
            "「{触|さわ}ってもいいですか？」\n「はい、どうぞ。{人|ひと}が{大好|だいす}きなんです。」",
            "May I pet him/her?\nSure, go ahead. He/she loves people.",
        ),
    ],
    "ねこ": [
        x("{猫|ねこ}", "cat"),
        x("これは{私|わたし}の{猫|ねこ}です。", "This is my cat."),
        x("「{猫|ねこ}、どこにいるの？」", "Where's the cat?"),
        x("「{窓|まど}のそばで{寝|ね}てるよ。」", "It's sleeping by the window."),
        x("「{気持|きも}ちよさそうだね。」", "Looks comfortable, doesn't it?"),
    ],
    # ── F3 へやの なか ─────────────────────────────────────────────
    "へや": [
        x("{部屋|へや}の{中|なか}", "inside the room"),
        x("この{部屋|へや}、{静|しず}かだね。", "This room is quiet, isn't it."),
    ],
    "まど": [
        x("{窓|まど}を{開|あ}けて。", "Open the window."),
        x("{窓|まど}から{海|うみ}が{見|み}える。", "You can see the sea from the window."),
    ],
    "ドア": [
        x("ドア、{閉|し}めて。", "Close the door."),
    ],
    "げんかん": [
        x("{玄関|げんかん}で{靴|くつ}を{脱|ぬ}いで。", "Take your shoes off at the genkan."),
    ],
    "にわ": [
        x("{庭|にわ}に{出|で}よう。", "Let's go out to the garden."),
    ],
    "だいどころ": [
        x("{台所|だいどころ}からいい{匂|にお}い。", "Something smells good from the kitchen."),
    ],
    "おふろ": [
        x("お{風呂|ふろ}、{沸|わ}いたよ。", "The bath's ready."),
    ],
    "トイレ": [
        x("トイレ、どこ？", "Where's the restroom?"),
    ],
    "つくえ": [
        x("{机|つくえ}の{上|うえ}に{本|ほん}がある。", "There's a book on the desk."),
    ],
    "いす": [
        sh("これは いすです。", "This is a chair.", "Room 11"),
        x("その{椅子|いす}に{座|すわ}って。", "Sit on that chair."),
    ],
    "ベッド": [
        x("もうベッドに{入|はい}る。", "I'm going to bed."),
    ],
    "ほん": [
        sh("これは ほんです。", "This is a book.", "Room 7, Room 40"),
        x("その{本|ほん}、{貸|か}して。", "Lend me that book."),
    ],
    "かばん": [
        x("{鞄|かばん}、{忘|わす}れた。", "I forgot my bag."),
    ],
    "かぎ": [
        x("{鍵|かぎ}、どこに{置|お}いた？", "Where did I put the key?"),
    ],
    "とけい": [
        x("{時計|とけい}を{見|み}て。もう{遅|おそ}い。", "Look at the clock. It's already late."),
    ],
    "でんわ": [
        x("{電話|でんわ}、{出|で}て。", "Get the phone."),
    ],
    "テレビ": [
        x("テレビ、{消|け}して。", "Turn off the TV."),
    ],
    "でんき": [
        x("{電気|でんき}、つけといて。", "Leave the light on."),
    ],
    "かさ": [
        x("{傘|かさ}、{持|も}っていった？", "Did you take an umbrella?"),
    ],
    "コップ": [
        x("このコップ、{割|わ}れやすい。", "This glass breaks easily."),
    ],
    "さら": [
        x("{皿|さら}を{洗|あら}っておく。", "I'll wash the plates."),
    ],
    "うえ": [
        x("{机|つくえ}の{上|うえ}", "on the desk"),
        x("{棚|たな}の{上|うえ}に{置|お}いて。", "Put it on the shelf."),
    ],
    "した": [
        x("{椅子|いす}の{下|した}に{猫|ねこ}がいる。", "There's a cat under the chair."),
    ],
    "なか": [
        x("{箱|はこ}の{中|なか}", "inside the box"),
        x("{部屋|へや}の{中|なか}は{暖|あたた}かい。", "It's warm inside the room."),
    ],
    "そと": [
        x("{外|そと}、{寒|さむ}いよ。", "It's cold outside."),
        x("ちょっと{外|そと}、{見|み}てくる。", "I'll just look outside."),
    ],
    # ── F4 まちへ いく ─────────────────────────────────────────────
    "いく": [
        x("もう{行|い}く？", "Shall we go already?"),
        x("{先|さき}に{行|い}くね。", "I'll go on ahead."),
    ],
    "くる": [
        x("{来|く}る？", "Are you coming?"),
        x("また{来週|らいしゅう}{来|く}るね。", "I'll come again next week."),
    ],
    "かえる": [
        x("もう{帰|かえ}る。", "I'm going home now."),
        x("そろそろ{帰|かえ}ろうか。", "Shall we head home soon?"),
    ],
    "あるく": [
        x("{歩|ある}いて{帰|かえ}る。", "I'll walk home."),
        x("{夜|よる}も{歩|ある}く。", "I walk at night too."),
    ],
    "みる": [
        x("{見|み}る。", "Look."),
        x("{空|そら}を{見|み}る。", "Look at the sky."),
    ],
    "まつ": [
        x("{待|ま}つ。", "Wait."),
        x("{駅|えき}で{待|ま}つよ。", "I'll wait at the station."),
    ],
    "あう": [
        x("{友達|ともだち}と{会|あ}う。", "I'm meeting a friend."),
        x("また{会|あ}う。", "We'll meet again."),
    ],
    "がっこう": [
        x("{学校|がっこう}、{休|やす}み？", "Is school off?"),
        x("{学校|がっこう}の{帰|かえ}りに{寄|よ}った。", "I stopped by on the way home from school."),
    ],
    "こうえん": [
        x("{公園|こうえん}で{遊|あそ}んでた。", "I was playing in the park."),
    ],
    "みせ": [
        x("あの{店|みせ}、{高|たか}い。", "That shop is expensive."),
        x("{隣|となり}の{店|みせ}に{入|はい}った。", "I went into the shop next door."),
    ],
    "びょういん": [
        x("{病院|びょういん}に{連|つ}れてって。", "Take me to the hospital."),
    ],
    "ゆうびんきょく": [
        x("{郵便局|ゆうびんきょく}、もう{閉|し}まった。", "The post office already closed."),
    ],
    "まち": [
        x("{町|まち}まで{歩|ある}いた。", "I walked as far as town."),
        x("この{町|まち}、{好|す}き。", "I like this town."),
    ],
    "みち": [
        x("この{道|みち}でいい？", "Is this the right way?"),
        x("{山道|やまみち}は{暗|くら}い。", "The mountain path is dark."),
    ],
    "かど": [
        x("{次|つぎ}の{角|かど}を{右|みぎ}へ。", "Right at the next corner."),
    ],
    "みぎ": [
        x("{右|みぎ}に{曲|ま}がって。", "Turn right."),
    ],
    "ひだり": [
        x("{左|ひだり}の{方|ほう}。", "To the left."),
        x("{左手|ひだりて}に{見|み}える。", "You can see it on the left."),
    ],
    "まっすぐ": [
        x("まっすぐ{行|い}って。", "Go straight."),
        x("この{道|みち}をまっすぐ。", "Straight along this road."),
    ],
    "ちかい": [
        x("{駅|えき}は{近|ちか}いよ。", "The station's nearby."),
    ],
    "とおい": [
        x("{少|すこ}し{遠|とお}い。", "It's a little far."),
        x("{山|やま}が{遠|とお}い。", "The mountains look far away."),
    ],
    "はし": [
        x("{橋|はし}を{渡|わた}って。", "Cross the bridge."),
    ],
    "いま": [
        x("{今|いま}、{行|い}く。", "I'll go now."),
        x("{今|いま}はちょっと。", "Not just now."),
    ],
    "あとで": [
        x("{後|あと}で{電話|でんわ}する。", "I'll call later."),
    ],
    "ゆっくり": [
        sh("ゆっくり、おねがい。", "Slowly, please.", "Room 40"),
        x("ゆっくり{話|はな}して。", "Speak slowly."),
    ],
    "いそぐ": [
        x("{急|いそ}がなくていい。", "You don't have to hurry."),
        x("{朝|あさ}はいつも{急|いそ}いでる。", "Mornings I'm always in a rush."),
    ],
    # ── F5 ごはんを たべる ─────────────────────────────────────────
    "ごはん": [
        x("{ご飯|ごはん}、まだ？", "Is the meal ready yet?"),
        x("{ご飯|ごはん}、できたよ。", "The rice is ready."),
    ],
    "みず": [
        sh("これは みずです。", "This is water.", "Room 40"),
        x("{水|みず}、{冷|つめ}たい。", "The water is cold."),
    ],
    "おちゃ": [
        x("お{茶|ちゃ}、いかが。", "Would you like some tea?"),
        x("お{茶|ちゃ}が{入|はい}った。", "The tea's poured."),
    ],
    "コーヒー": [
        x("コーヒー、{黒|くろ}で。", "Coffee — black."),
    ],
    "パン": [
        x("{朝|あさ}はパン。", "Bread in the morning."),
        x("このパン、{柔|やわ}らかい。", "This bread is soft."),
    ],
    "たまご": [
        sh("たまごを たべます。", "I eat egg.", "Room 18"),
        x("{卵|たまご}、{焼|や}いてる。", "I'm frying an egg."),
    ],
    "おにぎり": [
        sh("おにぎりを たべます。", "I eat a rice ball.", "Room 18"),
        x("{朝|あさ}のおにぎり。", "A morning onigiri."),
    ],
    "すし": [
        sh("すしを たべます。", "I eat sushi.", "Room 18"),
        x("{寿司|すし}、{食|た}べに{行|い}かない？", "Want to go eat sushi?"),
    ],
    "うどん": [
        sh("うどんは おいしいですか。", "Is the udon delicious?", "Room 5"),
        x("{熱|あつ}いうどん。", "Hot udon."),
    ],
    "さかな": [
        x("{魚|さかな}を{焼|や}いてる。", "I'm grilling fish."),
    ],
    "にく": [
        x("{肉|にく}、ちょっと{多|おお}い。", "That's a bit much meat."),
    ],
    "やさい": [
        x("{野菜|やさい}も{食|た}べて。", "Eat your vegetables too."),
    ],
    "くだもの": [
        x("{果物|くだもの}、{冷|ひ}やしといて。", "Chill the fruit."),
    ],
    "たべる": [
        x("{何|なに}を{食|た}べる？", "What are you going to eat?"),
        x("{夜|よる}はあまり{食|た}べない。", "I don't eat much at night."),
    ],
    "たべます": [
        sh("すしを たべます。", "I eat sushi.", "Room 18"),
        x("{今日|きょう}は{何|なに}を{食|た}べますか。", "What will you eat today?"),
    ],
    "のむ": [
        x("{水|みず}は{飲|の}む。", "I do drink water."),
        x("{飲|の}むのは{水|みず}だけ。", "Water is all I drink."),
    ],
    "おいしい": [
        sh("おいしいです。", "It's delicious.", "Room 5, Room 18"),
        sh("はい、おいしいです。", "Yes, it's delicious.", "Room 5"),
        x("これ、すごく{美味|おい}しい。", "This is really delicious."),
    ],
    "あまい": [
        x("{甘|あま}いもの、{好|す}き。", "I like sweet things."),
    ],
    "あつい": [
        x("{熱|あつ}い、{気|き}をつけて。", "It's hot — careful."),
    ],
    "つめたい": [
        x("{冷|つめ}たい{水|みず}がいい。", "Cold water would be good."),
    ],
    "すき": [
        x("{寿司|すし}が{好|す}き。", "I like sushi."),
        x("ここが{好|す}き。", "I like it here."),
    ],
    "きらい": [
        x("{苦|にが}いのは{嫌|きら}い。", "I don't like bitter things."),
    ],
    "おなか": [
        x("お{腹|なか}、すいた。", "I'm hungry."),
        x("お{腹|なか}いっぱい。", "I'm full."),
    ],
    "おはし": [
        x("お{箸|はし}、{忘|わす}れた。", "I forgot chopsticks."),
    ],
    "いただきます": [
        x("じゃあ、いただきます。", "Well then — let's eat."),
    ],
    # ── F6 そらと かぜ ─────────────────────────────────────────────
    "いち": [
        x("{一番|いちばん}。", "Number one. / The first."),
        x("{一|いち}{月|がつ}。", "January."),
    ],
    "に": [
        x("{二|に}", "two"),
        x("{二|に}{番目|ばんめ}。", "The second one."),
    ],
    "さん": [
        x("いち、に、さん", "one, two, three"),
        x("{三人|さんにん}きた。", "Three people came."),
    ],
    "よん": [
        x("{四番|よんばん}。", "Number four."),
        x("{四|よん}{月|がつ}。", "April."),
    ],
    "ご": [
        x("{五番|ごばん}。", "Number five."),
        x("{五|ご}{月|がつ}。", "May."),
    ],
    "ろく": [
        x("{六|ろく}{時|じ}に{出|で}る。", "I leave at six."),
    ],
    "なな": [
        x("{七つ|ななつ}ください。", "Seven, please."),
    ],
    "はち": [
        x("{八|はち}{時|じ}だよ。", "It's eight o'clock."),
    ],
    "きゅう": [
        x("{九番|きゅうばん}。", "Number nine."),
        x("{九|きゅう}{時|じ}。", "Nine o'clock."),
    ],
    "じゅう": [
        x("{十|じゅう}で{止|と}めて。", "Stop at ten."),
    ],
    "きょう": [
        x("{今日|きょう}は{雨|あめ}。", "It's raining today."),
        x("{今日|きょう}はもういい。", "That's enough for today."),
    ],
    "あした": [
        sh("あしたは あめですか。", "Will it rain tomorrow?", "Room 40"),
        x("{明日|あした}、{会|あ}える？", "Can we meet tomorrow?"),
    ],
    "きのう": [
        x("{昨日|きのう}は{寒|さむ}かった。", "Yesterday was cold."),
    ],
    "あさ": [
        x("{朝|あさ}から{忙|いそが}しい。", "Busy since morning."),
        x("お{早|はよ}う。いい{朝|あさ}。", "Good morning. A fine morning."),
    ],
    "よる": [
        x("{夜|よる}の{街|まち}。", "The town at night."),
        x("もう{夜|よる}だね。", "It's night already."),
    ],
    "あめ": [
        sh("あしたは あめですか。", "Will it rain tomorrow?", "Room 40"),
        x("{雨|あめ}が{降|ふ}ってきた。", "It's started to rain."),
    ],
    "かぜ": [
        sh("かぜが よわいです。", "The wind is gentle.", "Room 40"),
        x("{風|かぜ}が{強|つよ}い。", "The wind is strong."),
    ],
    "さむい": [
        x("{外|そと}、{寒|さむ}いよ。", "It's cold outside."),
        x("{冬|ふゆ}は{寒|さむ}い。", "Winter is cold."),
    ],
    "あたたかい": [
        x("{春|はる}は{暖|あたた}かい。", "Spring is warm."),
        x("この{部屋|へや}、{暖|あたた}かい。", "This room is warm."),
    ],
    "はる": [
        x("{春|はる}が{来|き}た。", "Spring has come."),
    ],
    "なつ": [
        x("{夏|なつ}は{海|うみ}へ。", "In summer, to the sea."),
    ],
    "あき": [
        x("{秋|あき}の{風|かぜ}。", "Autumn wind."),
    ],
    "ふゆ": [
        x("{冬|ふゆ}の{朝|あさ}。", "A winter morning."),
        x("{雪|ゆき}の{冬|ふゆ}。", "A winter of snow."),
    ],
    "そら": [
        x("{空|そら}を{見|み}て。", "Look at the sky."),
        x("{空|そら}がきれい。", "The sky is beautiful."),
    ],
    "くも": [
        x("{雲|くも}が{多|おお}い。", "Lots of clouds."),
        x("{白|しろ}い{雲|くも}。", "White clouds."),
    ],
}


def expansions_for(jp: str) -> list[dict]:
    return [e for e in CONTEXT.get(jp, []) if e]
