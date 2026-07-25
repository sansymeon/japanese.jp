#!/usr/bin/env bash
# Limit pushes that update origin/main to once per calendar day (Asia/Tokyo).
# Saves Netlify build minutes. Analytics JSON is fine at this cadence —
# YouTube lesson work is not blocked by waiting a day to publish stats.
#
# Exit 0 = allow, exit 1 = block.
#
# Override for an urgent deploy:
#   ALLOW_EXTRA_PUSH=1 git push
#
# Stamp (.git/push-quota-main-day) records the last allowed main-push day.

set -euo pipefail

TZ_NAME="${PUSH_QUOTA_TZ:-Asia/Tokyo}"
TODAY="$(TZ="$TZ_NAME" date +%Y-%m-%d)"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$ROOT" ]]; then
  echo "[push-quota] error: not inside a git repository" >&2
  exit 1
fi

STAMP="$ROOT/.git/push-quota-main-day"

if [[ "${ALLOW_EXTRA_PUSH:-}" == "1" ]]; then
  echo "[push-quota] ALLOW_EXTRA_PUSH=1 — allowing extra push to main ($TODAY $TZ_NAME)"
  printf '%s\n' "$TODAY" >"$STAMP"
  exit 0
fi

LAST=""
if [[ -f "$STAMP" ]]; then
  LAST="$(tr -d '[:space:]' <"$STAMP" || true)"
fi

if [[ -n "$LAST" && "$LAST" == "$TODAY" ]]; then
  cat >&2 <<EOF
[push-quota] Blocked: already pushed to main today ($TODAY $TZ_NAME).

One main push per day keeps Netlify minutes down.
Analytics JSON can wait until tomorrow — it does not affect YouTube projects.
  • Keep committing locally; push tomorrow, or
  • Urgent: ALLOW_EXTRA_PUSH=1 git push
EOF
  exit 1
fi

printf '%s\n' "$TODAY" >"$STAMP"
echo "[push-quota] OK: first main push for $TODAY ($TZ_NAME)"
exit 0
