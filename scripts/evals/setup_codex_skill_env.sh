#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

ENV_DIR="${ROOT_DIR}/evals/env/codex"
SKILLS_CSV="pygraphistry,pygraphistry-core,pygraphistry-visualization,pygraphistry-gfql,pygraphistry-ai,pygraphistry-connectors"

show_help() {
  cat <<'EOF'
Usage: scripts/evals/setup_codex_skill_env.sh [options]

Options:
  --env-dir DIR     Target env dir (default: evals/env/codex)
  --skills CSV      Comma-separated skill directories under .agents/skills
  -h, --help        Show help

Examples:
  ./scripts/evals/setup_codex_skill_env.sh
  ./scripts/evals/setup_codex_skill_env.sh --skills pygraphistry,pygraphistry-core
  ./scripts/evals/setup_codex_skill_env.sh --env-dir /tmp/codex-env
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

TARGET_SKILLS_DIR="${ENV_DIR}/.codex/skills"
mkdir -p "${TARGET_SKILLS_DIR}"

IFS=',' read -r -a skills <<< "${SKILLS_CSV}"
if [[ ${#skills[@]} -eq 0 ]]; then
  echo "No skills requested" >&2
  exit 2
fi

while IFS= read -r -d '' p; do
  rm -f "$p"
done < <(find "${TARGET_SKILLS_DIR}" -mindepth 1 -maxdepth 1 -type l -print0)

linked=()
for skill in "${skills[@]}"; do
  skill="${skill// /}"
  if [[ -z "${skill}" ]]; then
    continue
  fi
  src="${ROOT_DIR}/.agents/skills/${skill}"
  if [[ ! -f "${src}/SKILL.md" ]]; then
    echo "Missing SKILL.md for ${skill}: ${src}/SKILL.md" >&2
    exit 2
  fi
  ln -sfn "${src}" "${TARGET_SKILLS_DIR}/${skill}"
  linked+=("${skill}")
done

if [[ ${#linked[@]} -eq 0 ]]; then
  echo "No valid skills linked" >&2
  exit 2
fi

echo "Codex native skill env ready"
echo "env_dir=${ENV_DIR}"
echo "skills_dir=${TARGET_SKILLS_DIR}"
echo "linked_skills=$(IFS=,; echo "${linked[*]}")"
