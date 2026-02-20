#!/usr/bin/env bash
set -euo pipefail

CHECK_ONLY=false
if [[ "${1:-}" == "--check-only" ]]; then
  CHECK_ONLY=true
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "error: must run inside a git repository" >&2
  exit 1
fi

cd "$(git rev-parse --show-toplevel)"

if command -v detect-secrets >/dev/null 2>&1; then
  DETECT_SECRETS=(detect-secrets)
elif command -v uvx >/dev/null 2>&1 && uvx --from detect-secrets detect-secrets --version >/dev/null 2>&1; then
  DETECT_SECRETS=(uvx --from detect-secrets detect-secrets)
elif command -v uv >/dev/null 2>&1 && uv tool run detect-secrets --version >/dev/null 2>&1; then
  DETECT_SECRETS=(uv tool run detect-secrets)
else
  echo "error: detect-secrets not found. Install detect-secrets or add it to your uv environment." >&2
  exit 1
fi

EXCLUDE_REGEX='^(plans/|AI_PROGRESS/|tmp/)'

block_staged_plan_paths() {
  local blocked
  blocked=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^(plans/|AI_PROGRESS/)' || true)
  if [[ -n "$blocked" ]]; then
    echo "error: committing files under plans/ or AI_PROGRESS/ is not allowed." >&2
    echo "$blocked" >&2
    exit 1
  fi
}

block_staged_plan_paths

if [[ ! -f .secrets.baseline ]]; then
  echo "warning: .secrets.baseline not found. Creating initial baseline." >&2
  "${DETECT_SECRETS[@]}" scan --exclude-files "$EXCLUDE_REGEX" > .secrets.baseline
  echo "created .secrets.baseline; review and commit it." >&2
  exit 0
fi

if [[ "$CHECK_ONLY" == true ]]; then
  mapfile -d '' STAGED_FILES < <(git diff --cached --name-only -z --diff-filter=ACM)

  FILTERED=()
  for path in "${STAGED_FILES[@]}"; do
    [[ -z "$path" ]] && continue
    if [[ "$path" =~ ^plans/ ]] || [[ "$path" =~ ^AI_PROGRESS/ ]] || [[ "$path" =~ ^tmp/ ]] || [[ "$path" == ".secrets.baseline" ]]; then
      continue
    fi
    FILTERED+=("$path")
  done

  if [[ ${#FILTERED[@]} -eq 0 ]]; then
    echo "secret check: no staged files to scan"
    exit 0
  fi

  TEMP_BASELINE=$(mktemp)
  TEMP_SCAN=$(mktemp)
  cp .secrets.baseline "$TEMP_BASELINE"

  "${DETECT_SECRETS[@]}" scan --baseline "$TEMP_BASELINE" "${FILTERED[@]}" > "$TEMP_SCAN" 2>/dev/null || true

  if [[ -s "$TEMP_SCAN" ]]; then
    if ! python3 - "$TEMP_SCAN" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

count = sum(len(items) for items in data.get("results", {}).values())
raise SystemExit(0 if count == 0 else 1)
PY
    then
      rm -f "$TEMP_SCAN" "$TEMP_BASELINE"
      echo "error: new secrets detected in staged files" >&2
      exit 1
    fi
  fi

  rm -f "$TEMP_SCAN" "$TEMP_BASELINE"
  echo "secret check: passed"
  exit 0
fi

TEMP_BASELINE=$(mktemp)
cp .secrets.baseline "$TEMP_BASELINE"
cleanup() {
  rm -f "$TEMP_BASELINE"
}
trap cleanup EXIT

"${DETECT_SECRETS[@]}" scan --baseline "$TEMP_BASELINE" --exclude-files "$EXCLUDE_REGEX"
"${DETECT_SECRETS[@]}" scan --baseline "$TEMP_BASELINE" --only-verified --exclude-files "$EXCLUDE_REGEX"

echo "secret check: passed"
