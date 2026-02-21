#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

ENV_DIR="${ROOT_DIR}/evals/env/codex"
SKILLS_CSV="pygraphistry,pygraphistry-core,pygraphistry-visualization,pygraphistry-gfql,pygraphistry-ai,pygraphistry-connectors"
PROMPT="What skills are loaded in this session? Reply with comma-separated skill names only."
OUT_DIR="/tmp/codex_skill_smoke_$(date +%Y%m%d-%H%M%S)"

show_help() {
  cat <<'EOF'
Usage: bin/evals/codex-skills-smoke.sh [options]

Options:
  --env-dir DIR     Env dir containing .codex/skills (default: evals/env/codex)
  --skills CSV      Comma-separated skill names to symlink from .agents/skills
  --prompt TEXT     Prompt to run
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

cat > "${OUT_DIR}/summary.txt" <<EOF
env_dir=${ENV_DIR}
raw_out=${RAW_OUT}
response_text=${RESPONSE_TEXT}
EOF

echo "Codex native skills smoke summary"
cat "${OUT_DIR}/summary.txt"
