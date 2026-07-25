#!/usr/bin/env bash
# Cursor beforeShellExecution: block git push to main when daily quota is used.
# Peek-only (does not write the stamp) so a denied attempt does not consume the day.

set -euo pipefail

input="$(cat)"
command=""
if command -v python3 >/dev/null 2>&1; then
  command="$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("command") or "")' 2>/dev/null || true)"
fi

if [[ -z "$command" ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

case "$command" in
  *git*push*) ;;
  *)
    echo '{ "permission": "allow" }'
    exit 0
    ;;
esac

if [[ "$command" == *ALLOW_EXTRA_PUSH=1* ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
TZ_NAME="${PUSH_QUOTA_TZ:-Asia/Tokyo}"
TODAY="$(TZ="$TZ_NAME" date +%Y-%m-%d)"
STAMP="${ROOT:-}/.git/push-quota-main-day"
LAST=""
if [[ -n "$ROOT" && -f "$STAMP" ]]; then
  LAST="$(tr -d '[:space:]' <"$STAMP" || true)"
fi

if [[ -z "$LAST" || "$LAST" != "$TODAY" ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

# Quota used today. Allow explicit non-main ref pushes; block main / bare pushes.
# Examples blocked: `git push`, `git push origin`, `git push origin main`
# Examples allowed: `git push origin feature-branch`
normalized="$(printf '%s' "$command" | tr '\t' ' ' | tr -s ' ')"
if [[ "$normalized" =~ push\ origin\ [A-Za-z0-9._/-]+$ ]] && \
   [[ ! "$normalized" =~ push\ origin\ main$ ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi
if [[ "$normalized" =~ push\ [A-Za-z0-9._/-]+$ ]] && \
   [[ ! "$normalized" =~ push\ (origin|main)$ ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

python3 - <<'PY'
import json
print(json.dumps({
  "permission": "deny",
  "user_message": "Push to main blocked: already used today's Netlify quota (once/day, Asia/Tokyo). Batch commits; push tomorrow. Urgent: ALLOW_EXTRA_PUSH=1 git push.",
  "agent_message": "Do not push to main again today. One main push per day saves Netlify minutes. Analytics JSON can wait — it does not affect YouTube projects. Keep committing locally; override with ALLOW_EXTRA_PUSH=1 git push only if the user asks."
}))
PY
exit 0
