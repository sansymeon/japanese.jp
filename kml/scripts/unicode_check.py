import csv

bad_chars = ["⼀","⼁","⼂","⼃","⼄","⼅","⼆","⼇","⼈","⼉","⼊","⼋"]

with open("data/kanji/kanji_master.csv", encoding="utf-8") as f:
    text = f.read()

for ch in bad_chars:
    if ch in text:
        print("⚠️ Found variant:", ch)