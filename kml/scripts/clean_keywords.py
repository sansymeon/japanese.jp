import os
import re

BASE_DIR = "contents/books/book_01/lessons"

pattern = re.compile(r'(<span class="kanji-keyword">)([^<]*)(</span>)')

def clean_keyword(text):
    text = text.replace("_", " ")
    text = text.replace("variant", "")
    text = " ".join(text.split())
    return text.strip()

for root, _, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith(".html") and file.startswith("lesson_"):
            path = os.path.join(root, file)

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            def replace(match):
                start, inner, end = match.groups()
                cleaned = clean_keyword(inner)
                return f"{start}{cleaned}{end}"

            new_content = pattern.sub(replace, content)

            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"Cleaned: {path}")

print("✅ All lesson keywords cleaned.")