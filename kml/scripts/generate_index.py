import csv

def load_csv(csv_file):
    with open(csv_file, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def generate_index(total_lessons):
    links = []

    for i in range(1, total_lessons + 1):
        num = str(i).zfill(2)
        links.append(
            f'<a class="lesson-btn" href="book_01/lessons/lesson_{num}.html">Lesson {num}</a>'
        )

    html = open("contents/books/index.html", encoding="utf-8").read()
    html = html.replace("{{LESSON_LINKS}}", "\n".join(links))

    with open("contents/books/index.html", "w", encoding="utf-8") as f:
        f.write(html)


# ===== RUN =====

data = load_csv("data/kanji/kanji_master.csv")
total_lessons = (len(data) + 19) // 20

generate_index(total_lessons)