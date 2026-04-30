import os
import re

BASE_DIR = "contents/books/book_01/lessons"

pattern = re.compile(r'(<div class="kanji-readings">)(.*?)(</div>)', re.DOTALL)

def clean_readings(text):
    text = text.strip()

    # Extract On / Kun if present
    on_match = re.search(r'On:\s*([^・]*)', text)
    kun_match = re.search(r'Kun:\s*([^・]*)', text)

    on = on_match.group(1).strip() if on_match else ""
    kun = kun_match.group(1).strip() if kun_match else ""

    parts = []
    if on:
        parts.append(f"On: {on}")
    if kun:
        parts.append(f"Kun: {kun}")

    return " ・ ".join(parts)

for root, _, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith(".html") and file.startswith("lesson_"):
            path = os.path.join(root, file)

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            def replace(match):
                start, inner, end = match.groups()
                cleaned = clean_readings(inner)
                return f"{start}{cleaned}{end}"

            new_content = pattern.sub(replace, content)

            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"Cleaned readings: {path}")

print("✅ All readings cleaned.")