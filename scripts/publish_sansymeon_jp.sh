#!/usr/bin/env bash
# Package a clean commit and publish it manually to sansymeon-jp.
# This does not start a Git-triggered Netlify build.
#
# Usage:
#   scripts/publish_sansymeon_jp.sh <commit>
#
# Example:
#   scripts/publish_sansymeon_jp.sh b29383fa14c6e69eba15872f74215ea489668cb3

set -euo pipefail

SITE_ID="d7738adc-b3cc-4ac8-8e4b-d608e7d09819"
SITE_NAME="sansymeon-jp"
SITE_DOMAIN="www.sansymeon.jp"
REPO="/home/sjnelson/japanese.jp"

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <commit>" >&2
  exit 2
fi

if [[ ! -x "$REPO/scripts/prepare_netlify_package.sh" ]]; then
  echo "missing $REPO/scripts/prepare_netlify_package.sh" >&2
  exit 2
fi

COMMIT="$(git -C "$REPO" rev-parse --verify "$1^{commit}")"
SHORT="$(git -C "$REPO" rev-parse --short=12 "$COMMIT")"
SOURCE="/home/sjnelson/japanese-deploy-$SHORT"
DEST="/home/sjnelson/japanese-netlify-package-$SHORT"

echo "Checking Netlify site $SITE_ID"
SITE_JSON="$(netlify api getSite --data "{\"site_id\":\"$SITE_ID\"}")"
export SITE_JSON
python3 - "$SITE_ID" "$SITE_NAME" "$SITE_DOMAIN" <<'PY'
import json, os, sys
expected_id, expected_name, expected_domain = sys.argv[1:]
site = json.loads(os.environ["SITE_JSON"])
name = site.get("name")
domain = site.get("custom_domain")
repo = (site.get("build_settings") or {}).get("repo_url")
if site.get("id") != expected_id or name != expected_name or domain != expected_domain:
    print(f"refusing to publish: site is {name} {domain} {site.get('id')}", file=sys.stderr)
    sys.exit(1)
if repo != "https://github.com/sansymeon/japanese.jp":
    print(f"refusing to publish: repo is {repo}", file=sys.stderr)
    sys.exit(1)
print(f"site: {name} ({domain})")
print(f"repo: {repo}")
PY

if [[ -e "$SOURCE" || -e "$DEST" ]]; then
  echo "refusing to overwrite $SOURCE or $DEST" >&2
  echo "remove the old directory yourself if you want to reuse this commit." >&2
  exit 2
fi

echo "Creating a clean checkout of $COMMIT"
git -C "$REPO" worktree add --detach "$SOURCE" "$COMMIT"

cleanup_source() {
  git -C "$REPO" worktree remove --force "$SOURCE" >/dev/null 2>&1 || true
}
trap cleanup_source EXIT

echo "Building the streamlined package"
"$REPO/scripts/prepare_netlify_package.sh" "$SOURCE" "$DEST"
trap - EXIT

python3 - "$DEST" <<'PY'
import os, sys
dest = sys.argv[1]
files = 0
total = 0
for dirpath, dirnames, filenames in os.walk(dest, followlinks=False):
    dirnames[:] = [d for d in dirnames if d != ".git"]
    for name in filenames:
        path = os.path.join(dirpath, name)
        files += 1
        if os.path.islink(path) or not os.path.isfile(path):
            continue
        total += os.path.getsize(path)
print()
print("Package preview")
print(f"  directory: {dest}")
print(f"  files:     {files}")
print(f"  size:      {total / (1024 ** 3):.2f} GiB ({total} bytes)")
PY

echo
echo "This will upload that directory to $SITE_NAME only."
echo "Site ID: $SITE_ID"
echo "Commit:  $COMMIT"
echo
read -r -p "Type publish to continue, or press Enter to stop: " ANSWER
if [[ "$ANSWER" != "publish" ]]; then
  echo "Stopped. The package is still at $DEST"
  echo "The clean checkout is still at $SOURCE"
  exit 0
fi

export PATH="/home/sjnelson/.local/opt/node-v22.21.0-linux-x64/bin:$PATH"
export CI=1
netlify deploy --prod \
  --site="$SITE_ID" \
  --dir="$DEST" \
  --message="Publish the streamlined package from $SHORT"

echo "Published $SHORT to $SITE_NAME ($SITE_ID)"
echo "Left the checkout at $SOURCE and the package at $DEST"
