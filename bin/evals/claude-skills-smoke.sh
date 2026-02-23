#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

ENV_DIR="${ROOT_DIR}/evals/env/claude"
SKILLS_CSV="pygraphistry,pygraphistry-core,pygraphistry-visualization,pygraphistry-gfql,pygraphistry-ai,pygraphistry-connectors"
PROMPT="What skills are loaded in this session? Reply with comma-separated skill names only. Do not use tool calls."
REQUIRE_SKILLS_CSV="pygraphistry-core,pygraphistry-gfql,pygraphistry-visualization"
OUT_DIR="/tmp/claude_skill_smoke_$(date +%Y%m%d-%H%M%S)"
PERMISSION_MODE="${AGENT_CLAUDE_PERMISSION_MODE:-bypassPermissions}"

show_help() {
  cat <<'EOF'
Usage: bin/evals/claude-skills-smoke.sh [options]

Options:
  --env-dir DIR     Env dir containing .claude/skills (default: evals/env/claude)
  --skills CSV      Comma-separated skill names to symlink from .agents/skills
  --prompt TEXT     Prompt to run (default asks loaded skills only)
  --require-skills CSV Comma-separated skill names that must appear in loaded/init skills or response
  --out DIR         Output directory for raw stream-json and summary
  -h, --help        Show help

Examples:
  ./bin/evals/claude-skills-smoke.sh
  ./bin/evals/claude-skills-smoke.sh --skills pygraphistry,pygraphistry-core
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

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude CLI not found in PATH" >&2
  exit 2
fi

"${ROOT_DIR}/scripts/evals/setup_claude_skill_env.sh" \
  --env-dir "${ENV_DIR}" \
  --skills "${SKILLS_CSV}" > "${OUT_DIR}/setup.log"

RAW_OUT="${OUT_DIR}/claude.stream.jsonl"
(
  cd "${ENV_DIR}"
  claude --verbose -p --output-format stream-json --permission-mode "${PERMISSION_MODE}" "${PROMPT}"
) > "${RAW_OUT}"

LOADED_SKILLS="$(jq -rc 'select(.type=="system" and .subtype=="init") | (.skills // [])' "${RAW_OUT}" | head -n 1)"
if [[ -z "${LOADED_SKILLS}" ]]; then
  LOADED_SKILLS="[]"
fi

RESPONSE_TEXT="$(jq -r '
  if .type=="assistant" then
    [ .message.content[]? | select(.type=="text") | .text ] | join("\n")
  elif .type=="result" then
    (.result // empty)
  else
    empty
  end
' "${RAW_OUT}" | tail -n 1)"

TOOL_CALL_COUNT="$(jq '
  [ select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") ] | length
' "${RAW_OUT}" | tail -n 1)"
if [[ -z "${TOOL_CALL_COUNT}" ]]; then
  TOOL_CALL_COUNT="0"
fi

cat > "${OUT_DIR}/summary.txt" <<EOF
env_dir=${ENV_DIR}
raw_out=${RAW_OUT}
loaded_skills=${LOADED_SKILLS}
tool_call_count=${TOOL_CALL_COUNT}
response_text=${RESPONSE_TEXT}
EOF

echo "Claude native skills smoke summary"
cat "${OUT_DIR}/summary.txt"

if [[ "${TOOL_CALL_COUNT}" != "0" ]]; then
  echo "Unexpected tool call(s) detected in smoke test" >&2
  exit 3
fi

if [[ "${LOADED_SKILLS}" == "[]" ]]; then
  echo "No loaded skills detected in Claude init payload" >&2
  exit 4
fi

IFS=',' read -r -a required_skills <<< "${REQUIRE_SKILLS_CSV}"
for skill in "${required_skills[@]}"; do
  skill="${skill// /}"
  [[ -z "${skill}" ]] && continue
  if [[ "${LOADED_SKILLS}" != *"${skill}"* && "${RESPONSE_TEXT}" != *"${skill}"* ]]; then
    echo "Required skill missing from smoke output: ${skill}" >&2
    exit 5
  fi
done
