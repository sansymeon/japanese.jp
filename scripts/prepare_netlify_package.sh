#!/usr/bin/env bash
# Prepare a Netlify upload directory from a clean checkout.
#
# Copies the public site into a separate directory and leaves development
# paths out of that copy. The source checkout is not modified, files stay
# tracked in Git, and nothing is deployed.
#
# kml/analytics/output/kml_channel_learning.json stays in the package.
# kml/analytics/dashboard/index.html fetches it. The other files in
# output/ are reports and unused JSON, so they stay out.
#
# Twelve Ambient film-tool HTML pages stay out. They are production and
# prototype tools, not public lessons. kml/tools/ambient/js/stroke-order-player.js
# stays, because the kana pages load it. Public stroke-order pages stay
# under kml/tools/strokes/.
#
# rsync -a copies symlinks as symlinks. It does not follow them, so a link
# such as kml/tools/ambient/assets -> ../../assets is not turned into a
# second copy of the site, and the target is not deleted.
#
# Usage, from anywhere:
#   scripts/prepare_netlify_package.sh SOURCE DEST
#
# SOURCE is a clean checkout, usually a detached worktree:
#   git worktree add --detach /home/sjnelson/japanese-deploy-<sha> <sha>
# DEST is a new directory. This script refuses to overwrite an existing
# destination, and it refuses to write into the source checkout.
#
# Then, when you are ready to publish (not part of this script):
#   export PATH="/home/sjnelson/.local/opt/node-v22.21.0-linux-x64/bin:$PATH"
#   export CI=1
#   netlify deploy --prod \
#     --site=d7738adc-b3cc-4ac8-8e4b-d608e7d09819 \
#     --dir=DEST \
#     --message="..."
#
# Deploy DEST, not the working tree and not the full clean checkout.

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 SOURCE DEST" >&2
  exit 2
fi

SOURCE="$(cd "$1" && pwd)"
DEST="$2"

if [[ -e "$DEST" ]]; then
  echo "refusing to overwrite existing destination: $DEST" >&2
  exit 2
fi

mkdir -p "$(dirname "$DEST")"
DEST="$(cd "$(dirname "$DEST")" && pwd)/$(basename "$DEST")"

if [[ "$DEST" == "$SOURCE" || "$DEST" == "$SOURCE"/* ]]; then
  echo "refusing to write the package inside the source checkout" >&2
  exit 2
fi

if [[ ! -f "$SOURCE/netlify.toml" || ! -f "$SOURCE/_redirects" ]]; then
  echo "source is missing netlify.toml or _redirects: $SOURCE" >&2
  exit 2
fi

if [[ -n "$(git -C "$SOURCE" status --porcelain)" ]]; then
  echo "source checkout is not clean: $SOURCE" >&2
  echo "use a detached worktree. do not package the working tree." >&2
  exit 2
fi

# Paths omitted from the upload only. They remain in SOURCE and in Git.
EXCLUDES=(
  --exclude /.git
  --exclude /scripts/publish_sansymeon_jp.sh
  --exclude /scripts/README-publish-sansymeon-jp.md
  --exclude /scripts/prepare_netlify_package.sh
  --exclude /kml/tools/ambient/collections/
  --exclude /kml/assets/covers.png/
  --exclude /kml/data/kanji/
  --exclude /kml/kanjidic2.xml
  --include=/kml/analytics/output/kml_channel_learning.json
  --exclude=/kml/analytics/output/*
  --exclude /lesson_assignments_v2.json
  --exclude /lesson_visual_layout_v2.json
  --exclude /lesson_visual_styles_v1.json
  --exclude /kml/tools/ambient/index.html
  --exclude /kml/tools/ambient/exhibition.html
  --exclude /kml/tools/ambient/digital-art-exhibition.html
  --exclude /kml/tools/ambient/prototype-editions.html
  --exclude /kml/tools/ambient/kanji-components.html
  --exclude /kml/tools/ambient/hiragana_lesson.html
  --exclude /kml/tools/ambient/katakana_lesson.html
  --exclude /kml/tools/ambient/grade-1-compounds-prototype.html
  --exclude /kml/tools/ambient/grade4-prototype.html
  --exclude /kml/tools/ambient/glow-stress.html
  --exclude /kml/tools/ambient/anchor-compounds-compare.html
  --exclude /kml/tools/ambient/quiet_cinematic_review/index.html
)

echo "source: $SOURCE"
echo "dest:   $DEST"
echo "commit: $(git -C "$SOURCE" rev-parse HEAD)"

rsync -a "${EXCLUDES[@]}" "$SOURCE/" "$DEST/"

python3 - "$SOURCE" "$DEST" <<'PY'
import os
import sys

source, dest = sys.argv[1], sys.argv[2]

excluded = [
    "scripts/publish_sansymeon_jp.sh",
    "scripts/README-publish-sansymeon-jp.md",
    "scripts/prepare_netlify_package.sh",
    "kml/tools/ambient/collections",
    "kml/assets/covers.png",
    "kml/data/kanji",
    "kml/kanjidic2.xml",
    "kml/analytics/output/CHANNEL_LEARNING_REPORT.md",
    "kml/analytics/output/CURRICULUM_REPORT.md",
    "kml/analytics/output/kml_channel_statistics.json",
    "kml/analytics/output/kml_curriculum_analysis.json",
    "kml/analytics/output/kml_frequency_statistics.json",
    "kml/analytics/output/kml_jlpt_statistics.json",
    "lesson_assignments_v2.json",
    "lesson_visual_layout_v2.json",
    "lesson_visual_styles_v1.json",
    "kml/tools/ambient/index.html",
    "kml/tools/ambient/exhibition.html",
    "kml/tools/ambient/digital-art-exhibition.html",
    "kml/tools/ambient/prototype-editions.html",
    "kml/tools/ambient/kanji-components.html",
    "kml/tools/ambient/hiragana_lesson.html",
    "kml/tools/ambient/katakana_lesson.html",
    "kml/tools/ambient/grade-1-compounds-prototype.html",
    "kml/tools/ambient/grade4-prototype.html",
    "kml/tools/ambient/glow-stress.html",
    "kml/tools/ambient/anchor-compounds-compare.html",
    "kml/tools/ambient/quiet_cinematic_review/index.html",
]
required = [
    "netlify.toml",
    "_redirects",
    "index.html",
    "museum/index.html",
    "kml/contents/books/book_01/lessons/lesson_01.html",
    "kml/assets/covers/lesson_01.jpg",
    "kml/assets/studies/one.jpg",
    "kml/tools/strokes/pages/one.html",
    "kml/assets/site/js/kml.js",
    "kml/assets/site/css/kml_style.css",
    "kml/assets/site/data/kanji-lookup.json",
    "statistics/index.html",
    "statistics/data/project_stats.json",
    "statistics/js/statistics.js",
    "kml/analytics/dashboard/index.html",
    "kml/analytics/dashboard/js/dashboard.js",
    "kml/analytics/output/kml_channel_learning.json",
    "kanken/index.html",
    "kanken/level-5/lesson-05.html",
    "kanken/level-4/lesson-09.html",
    "freds-adventure/index.html",
    "data/archive/kanjivg",
    "start-here/rooms/index.html",
    "kml/vocabulary/index.html",
    "kml/contents/books/book_01/compounds/lesson_01.html",
    "kml/data/compounds/lesson_01.json",
    "kml/kana/hiragana/a/index.html",
    "kml/tools/ambient/js/stroke-order-player.js",
    "collections/index.html",
    "ja/index.html",
]

def measure(root):
    files = 0
    total = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            path = os.path.join(dirpath, name)
            if os.path.islink(path):
                files += 1
                continue
            if os.path.isfile(path):
                files += 1
                total += os.path.getsize(path)
    return files, total

def gib(n):
    return f"{n / (1024 ** 3):.2f} GiB"

src_files, src_bytes = measure(source)
dst_files, dst_bytes = measure(dest)
print(f"source files: {src_files}")
print(f"source bytes: {src_bytes} ({gib(src_bytes)})")
print(f"package files: {dst_files}")
print(f"package bytes: {dst_bytes} ({gib(dst_bytes)})")
print(f"omitted bytes: {src_bytes - dst_bytes} ({gib(src_bytes - dst_bytes)})")
print(f"omitted files: {src_files - dst_files}")

failed = False
for rel in excluded:
    src_path = os.path.join(source, rel)
    dst_path = os.path.join(dest, rel)
    if not os.path.lexists(src_path):
        print(f"MISSING FROM SOURCE: {rel}")
        failed = True
    if os.path.lexists(dst_path):
        print(f"STILL IN PACKAGE: {rel}")
        failed = True
for rel in required:
    if not os.path.lexists(os.path.join(dest, rel)):
        print(f"MISSING FROM PACKAGE: {rel}")
        failed = True

# Absolute paths of the omitted trees. The public site folder
# collections/ is a different directory and stays in the package.
needles = (
    "kml/tools/ambient/collections",
    "tools/ambient/collections",
    "/covers.png",
    "kml/assets/covers.png",
    "kml/data/kanji",
    "/data/kanji/",
    "kanjidic2.xml",
    "lesson_visual_layout_v2.json",
    "lesson_assignments_v2.json",
    "lesson_visual_styles_v1.json",
)
tool_prefixes = ("kml/tools/ambient/", "kml/analytics/")
public_hits = []
for dirpath, dirnames, filenames in os.walk(dest, followlinks=False):
    dirnames[:] = [d for d in dirnames if d != ".git"]
    for name in filenames:
        if not name.endswith((".html", ".js", ".css")):
            continue
        path = os.path.join(dirpath, name)
        if os.path.islink(path):
            continue
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        rel = os.path.relpath(path, dest)
        found = [n for n in needles if n in text]
        if found and not rel.startswith(tool_prefixes):
            public_hits.append((rel, found))
        # Gallery tools load ./collections/ beside themselves. That folder
        # is the omitted production stills, not the public /collections/ site.
        if rel.startswith("kml/tools/ambient/") and "collections/" in text:
            print(f"tool page uses omitted collection files: {rel}")
learning = os.path.join(dest, "kml/analytics/output/kml_channel_learning.json")
dashboard_js = os.path.join(dest, "kml/analytics/dashboard/js/dashboard.js")
if os.path.isfile(learning) and os.path.isfile(dashboard_js):
    dash = open(dashboard_js, encoding="utf-8", errors="replace").read()
    if "kml_channel_learning.json" in dash:
        print("dashboard JSON included for kml/analytics/dashboard/")
    else:
        print("DASHBOARD NO LONGER NAMES kml_channel_learning.json")
        failed = True
print("public pages referencing an omitted path:")
if not public_hits:
    print("  none")
for rel, found in public_hits:
    print(f"  {rel}: {', '.join(found)}")
# homepage.js names the channel-learning JSON, then fetches it only when
# #stats or #statVideos is on the page. The published homepages have neither.
# The JSON is still packaged because the analytics dashboard fetches it.
unexpected = [rel for rel, _found in public_hits if rel != "assets/js/homepage.js"]
if unexpected:
    print("UNEXPECTED PUBLIC REFERENCES")
    failed = True

# Symlinks must remain links. Following them would duplicate kml/assets
# or the stroke pages and could hide a deleted target.
for rel, expect in (
    ("kml/tools/ambient/assets", "../../assets"),
    ("kml/tools/ambient/strokes", "../strokes"),
):
    link = os.path.join(dest, rel)
    if not os.path.islink(link):
        print(f"SYMLINK NOT PRESERVED: {rel}")
        failed = True
        continue
    raw = os.readlink(link)
    if raw != expect:
        print(f"SYMLINK TARGET CHANGED: {rel} -> {raw}")
        failed = True
    resolved = os.path.normpath(os.path.join(os.path.dirname(link), raw))
    if not resolved.startswith(dest + os.sep) or not os.path.exists(resolved):
        print(f"SYMLINK TARGET MISSING INSIDE PACKAGE: {rel} -> {raw}")
        failed = True
    else:
        print(f"symlink kept: {rel} -> {raw}")

film_paths = [
    rel for rel in excluded
    if rel.startswith("kml/tools/ambient/") and rel.endswith(".html")
]
public_film = []
for dirpath, dirnames, filenames in os.walk(dest, followlinks=False):
    dirnames[:] = [d for d in dirnames if d != ".git"]
    for name in filenames:
        if not name.endswith((".html", ".js", ".css")):
            continue
        path = os.path.join(dirpath, name)
        if os.path.islink(path):
            continue
        rel = os.path.relpath(path, dest)
        if rel.startswith("kml/tools/ambient/") and rel != "kml/tools/ambient/js/stroke-order-player.js":
            continue
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        hits = [n for n in film_paths if n in text or os.path.basename(n) in text and os.path.basename(n) != "index.html"]
        if hits:
            public_film.append((rel, hits))
print("public pages naming an excluded film-tool page:")
if not public_film:
    print("  none")
for rel, hits in public_film:
    print(f"  {rel}: {', '.join(hits)}")
    failed = True

same_config = True
for name in ("netlify.toml", "_redirects"):
    with open(os.path.join(source, name), "rb") as a, open(os.path.join(dest, name), "rb") as b:
        if a.read() != b.read():
            print(f"CONFIG MISMATCH: {name}")
            same_config = False
print("netlify.toml and _redirects match source" if same_config else "CONFIG CHECK FAILED")
if failed or not same_config:
    sys.exit(1)
PY
