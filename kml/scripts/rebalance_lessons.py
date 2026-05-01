import os
import re

LESSON_DIR = "contents/books/book_01/lessons"
LESSON_SIZE = 20

entry_pattern = re.compile(r'<section class="kanji-entry".*?</section>', re.DOTALL)

# 1. Collect all entries from lesson 13 onward
all_entries = []

files = sorted([f for f in os.listdir(LESSON_DIR) if f.startswith("lesson_")])

for f in files:
    num = int(f.split("_")[1].split(".")[0])
    if num >= 13:
        path = os.path.join(LESSON_DIR, f)
        with open(path, encoding="utf-8") as file:
            content = file.read()
            entries = entry_pattern.findall(content)
            all_entries.extend(entries)

# 2. Re-slice into clean lessons
lesson_number = 13
index = 0

while index < len(all_entries):
    chunk = all_entries[index:index+LESSON_SIZE]

    file_name = f"lesson_{str(lesson_number).zfill(2)}.html"
    path = os.path.join(LESSON_DIR, file_name)

    with open(path, encoding="utf-8") as f:
        html = f.read()

    # Replace KANJI_BLOCKS section
    new_blocks = "\n".join(chunk)

    html = re.sub(
        r'<!-- KANJI BLOCKS -->.*?<!-- CTA -->',
        f'<!-- KANJI BLOCKS -->\n{new_blocks}\n\n<!-- CTA -->',
        html,
        flags=re.DOTALL
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Fixed: {file_name}")

    index += LESSON_SIZE
    lesson_number += 1

print("✅ Lessons rebalanced.")