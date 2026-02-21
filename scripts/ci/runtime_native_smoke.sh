#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

ran_any="false"

if command -v claude >/dev/null 2>&1; then
  ran_any="true"
  echo "[runtime-smoke] Running Claude native skill smoke..."
  "${ROOT_DIR}/bin/evals/claude-skills-smoke.sh" \
    --env-dir "${ROOT_DIR}/evals/env/claude" \
    --out "/tmp/claude_native_smoke_ci_$(date +%Y%m%d-%H%M%S)"
else
  echo "[runtime-smoke] Claude CLI not found; skipping Claude smoke."
fi

if command -v codex >/dev/null 2>&1; then
  ran_any="true"
  echo "[runtime-smoke] Running Codex native skill smoke..."
  "${ROOT_DIR}/bin/evals/codex-skills-smoke.sh" \
    --env-dir "${ROOT_DIR}/evals/env/codex" \
    --out "/tmp/codex_native_smoke_ci_$(date +%Y%m%d-%H%M%S)"
else
  echo "[runtime-smoke] Codex CLI not found; skipping Codex smoke."
fi

if [[ "${ran_any}" != "true" ]]; then
  echo "[runtime-smoke] No runtime CLI available on this runner; skipping."
fi
