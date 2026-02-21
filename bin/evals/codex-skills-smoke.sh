#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

ENV_DIR="${ROOT_DIR}/evals/env/codex"
SKILLS_CSV="pygraphistry,pygraphistry-core,pygraphistry-visualization,pygraphistry-gfql,pygraphistry-ai,pygraphistry-connectors"
PROMPT="What skills are loaded in this session? Reply with comma-separated skill names only. Do not use tool calls."
REQUIRE_SKILLS_CSV="pygraphistry-core,pygraphistry-gfql,pygraphistry-visualization"
OUT_DIR="/tmp/codex_skill_smoke_$(date +%Y%m%d-%H%M%S)"

show_help() {
  cat <<'EOF'
Usage: bin/evals/codex-skills-smoke.sh [options]

Options:
  --env-dir DIR     Env dir containing .codex/skills (default: evals/env/codex)
  --skills CSV      Comma-separated skill names to symlink from .agents/skills
  --prompt TEXT     Prompt to run
  --require-skills CSV Comma-separated skill names that must appear in response
  --out DIR         Output directory for raw json and summary
  -h, --help        Show help

Examples:
  ./bin/evals/codex-skills-smoke.sh
  ./bin/evals/codex-skills-smoke.sh --skills pygraphistry,pygraphistry-core
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env-dir)
      ENV_DIR="$2"
      shift 2
      ;;
    --skills)
      SKILLS_CSV="$2"
      shift 2
      ;;
    --prompt)
      PROMPT="$2"
      shift 2
      ;;
    --require-skills)
      REQUIRE_SKILLS_CSV="$2"
      shift 2
      ;;
    --out)
      OUT_DIR="$2"
      shift 2
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      show_help >&2
      exit 2
      ;;
  esac
done

mkdir -p "${OUT_DIR}"

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI not found in PATH" >&2
  exit 2
fi

"${ROOT_DIR}/scripts/evals/setup_codex_skill_env.sh" \
  --env-dir "${ENV_DIR}" \
  --skills "${SKILLS_CSV}" > "${OUT_DIR}/setup.log"

RAW_OUT="${OUT_DIR}/codex.jsonl"
(
  cd "${ENV_DIR}"
  codex exec --json --skip-git-repo-check --color never "${PROMPT}"
) > "${RAW_OUT}"

RESPONSE_TEXT="$(jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text' "${RAW_OUT}" | tail -n 1)"
if [[ -z "${RESPONSE_TEXT}" ]]; then
  RESPONSE_TEXT="$(tail -n 1 "${RAW_OUT}")"
fi

TOOL_CALL_COUNT="$(jq '[select(.type=="item.completed" and .item.type=="command_execution")] | length' "${RAW_OUT}" | tail -n 1)"
if [[ -z "${TOOL_CALL_COUNT}" ]]; then
  TOOL_CALL_COUNT="0"
fi

cat > "${OUT_DIR}/summary.txt" <<EOF
env_dir=${ENV_DIR}
raw_out=${RAW_OUT}
tool_call_count=${TOOL_CALL_COUNT}
response_text=${RESPONSE_TEXT}
EOF

echo "Codex native skills smoke summary"
cat "${OUT_DIR}/summary.txt"

if [[ "${TOOL_CALL_COUNT}" != "0" ]]; then
  echo "Unexpected command execution tool call(s) detected in Codex smoke test" >&2
  exit 3
fi

IFS=',' read -r -a required_skills <<< "${REQUIRE_SKILLS_CSV}"
for skill in "${required_skills[@]}"; do
  skill="${skill// /}"
  [[ -z "${skill}" ]] && continue
  if [[ "${RESPONSE_TEXT}" != *"${skill}"* ]]; then
    echo "Required skill missing from Codex smoke output: ${skill}" >&2
    exit 4
  fi
done
