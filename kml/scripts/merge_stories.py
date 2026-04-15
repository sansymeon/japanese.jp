import csv

MASTER = "data/kanji/kanji_master.csv"
STORIES = "data/kanji/lesson_01_stories.csv"
OUTPUT = "data/kanji/kanji_master_updated.csv"


def load_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_csv(path, rows, fieldnames):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# Load data
master = load_csv(MASTER)
stories = load_csv(STORIES)

# Build lookup
story_map = {row["slug"]: row for row in stories}

updated = 0
skipped = 0
missing = 0

for row in master:
    slug = row.get("slug")

    if not slug:
        continue

    story = story_map.get(slug)

    if not story:
        missing += 1
        continue

    # Only fill if empty (safe merge)
    if not row.get("jp_verse") and story.get("jp_verse"):
        row["jp_verse"] = story["jp_verse"]
        updated += 1
    else:
        skipped += 1

    if not row.get("en_verse") and story.get("en_verse"):
        row["en_verse"] = story["en_verse"]

# Save
fieldnames = master[0].keys()
save_csv(OUTPUT, master, fieldnames)

print("✅ Merge complete")
print(f"Updated: {updated}")
print(f"Skipped (already had data): {skipped}")
print(f"No match in stories: {missing}")
print(f"➡ Output: {OUTPUT}")