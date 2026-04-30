import os
import re

BASE_DIR = "contents/books/book_01/compounds"

# Match image block
img_pattern = re.compile(
    r'<div class="kanji-img-center">\s*<img[^>]*>\s*</div>',
    re.DOTALL
)

# Extract kanji from label
label_pattern = re.compile(
    r'<div class="kanji-label">([^（\s]+)'
)

for root, _, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            labels = label_pattern.findall(content)

            def replacer(match):
                # pop next kanji in order
                if labels:
                    kanji = labels.pop(0)
                else:
                    kanji = "?"

                return f'''
<div class="kanji-img-center">
  <span class="kanji-compound-font">{kanji}</span>
</div>
'''

            new_content = img_pattern.sub(replacer, content)

            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"Fixed: {path}")

print("✅ Compound pages updated correctly.")