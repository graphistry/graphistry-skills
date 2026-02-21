#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

HARNESSES=()
JOURNEYS="runtime_smoke"
SKILLS_MODE="off"
SKILLS_PROFILE="pygraphistry_core"
CASE_IDS=""
OUT_DIR=""
GRADING="deterministic"
ORACLE_HARNESS="codex"
ORACLE_MODEL=""
ORACLE_TIMEOUT_S="120"
ORACLE_MIN_SCORE_DEFAULT="0.8"
ORACLE_STRICT="false"
LOUIE_URL="${LOUIE_URL:-http://localhost:8501}"
TIMEOUT_S="240"
CLAUDE_CWD=""
CODEX_CWD=""
ORACLE_CLAUDE_CWD=""
ORACLE_CODEX_CWD=""
CLAUDE_MODELS=""
CODEX_MODELS=""
SKILLS_DELIVERY="native"
OTEL="false"
OTEL_SERVICE="agent-eval-runner"
OTEL_ENDPOINT="${OTEL_EXPORTER_OTLP_ENDPOINT_GRPC:-}"
FAILFAST="false"
MAX_WORKERS="1"

show_help() {
  cat <<'USAGE'
Usage: ./bin/agent.sh [options]

Harness flags:
  --codex            Include codex harness
  --claude           Include claude harness
  --louie            Include louie harness
  --auto             Include auto harness (codex->claude fallback)

Options:
  --journeys CSV     Journey IDs or 'all' (default: runtime_smoke)
  --skills-mode X    on|off|both|CSV (default: off)
  --skills-profile X Skills profile name (default: pygraphistry_core)
  --case-ids CSV     Optional case-id filter (rerun only selected cases)
  --out DIR          Output run directory
  --grading X        deterministic|oracle|hybrid (default: deterministic)
  --oracle-harness X codex|claude|louie (default: codex)
  --oracle-model X   Optional oracle model override
  --oracle-timeout-s N Oracle call timeout seconds (default: 120)
  --oracle-min-score-default F Default oracle min score (default: 0.8)
  --oracle-strict    Fail closed if oracle grading errors
  --louie-url URL    Louie base URL (default: http://localhost:8501)
  --timeout-s N      Per-harness timeout seconds (default: 240)
  --claude-cwd DIR   Working directory for claude harness (for native .claude/skills tests)
  --codex-cwd DIR    Working directory for codex harness (for native .codex/skills tests)
  --oracle-claude-cwd DIR Optional cwd override for oracle claude harness
  --oracle-codex-cwd DIR Optional cwd override for oracle codex harness
  --claude-models CSV Optional claude model list (e.g., sonnet,opus)
  --codex-models CSV Optional codex model list (e.g., o4-mini,o3)
  --skills-delivery X native|inject|auto (default: native)
  --otel             Emit OTel lifecycle events via graphistrygpt helper
  --failfast         Fail fast per harness after first harness error (with Louie preflight)
  --max-workers N    Parallel harness workers per case (default: 1)
  --otel-service X   OTel service name (default: agent-eval-runner)
  --otel-endpoint X  OTLP endpoint (default: OTEL_EXPORTER_OTLP_ENDPOINT_GRPC)
  -h, --help         Show help

Examples:
  ./bin/agent.sh --codex --claude --journeys runtime_smoke
  ./bin/agent.sh --codex --claude --louie --skills-mode both --otel
  ./bin/agent.sh --claude --journeys runtime_smoke --claude-models sonnet,opus --skills-mode both
  ./bin/agent.sh --codex --claude --journeys pygraphistry_persona_journeys_v1 --case-ids persona_novice_fraud_table_to_viz_algo,persona_connector_analyst_workflow --max-workers 2
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --codex)
      HARNESSES+=("codex")
      shift
      ;;
    --claude)
      HARNESSES+=("claude")
      shift
      ;;
    --louie)
      HARNESSES+=("louie")
      shift
      ;;
    --auto)
      HARNESSES+=("auto")
      shift
      ;;
    --journeys)
      JOURNEYS="$2"
      shift 2
      ;;
    --skills-mode)
      SKILLS_MODE="$2"
      shift 2
      ;;
    --skills-profile)
      SKILLS_PROFILE="$2"
      shift 2
      ;;
    --case-ids)
      CASE_IDS="$2"
      shift 2
      ;;
    --out)
      OUT_DIR="$2"
      shift 2
      ;;
    --grading)
      GRADING="$2"
      shift 2
      ;;
    --oracle-harness)
      ORACLE_HARNESS="$2"
      shift 2
      ;;
    --oracle-model)
      ORACLE_MODEL="$2"
      shift 2
      ;;
    --oracle-timeout-s)
      ORACLE_TIMEOUT_S="$2"
      shift 2
      ;;
    --oracle-min-score-default)
      ORACLE_MIN_SCORE_DEFAULT="$2"
      shift 2
      ;;
    --oracle-strict)
      ORACLE_STRICT="true"
      shift
      ;;
    --louie-url)
      LOUIE_URL="$2"
      shift 2
      ;;
    --timeout-s)
      TIMEOUT_S="$2"
      shift 2
      ;;
    --claude-cwd)
      CLAUDE_CWD="$2"
      shift 2
      ;;
    --codex-cwd)
      CODEX_CWD="$2"
      shift 2
      ;;
    --oracle-claude-cwd)
      ORACLE_CLAUDE_CWD="$2"
      shift 2
      ;;
    --oracle-codex-cwd)
      ORACLE_CODEX_CWD="$2"
      shift 2
      ;;
    --claude-models)
      CLAUDE_MODELS="$2"
      shift 2
      ;;
    --codex-models)
      CODEX_MODELS="$2"
      shift 2
      ;;
    --skills-delivery)
      SKILLS_DELIVERY="$2"
      shift 2
      ;;
    --otel)
      OTEL="true"
      shift
      ;;
    --failfast)
      FAILFAST="true"
      shift
      ;;
    --max-workers)
      MAX_WORKERS="$2"
      shift 2
      ;;
    --otel-service)
      OTEL_SERVICE="$2"
      shift 2
      ;;
    --otel-endpoint)
      OTEL_ENDPOINT="$2"
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

if [[ ${#HARNESSES[@]} -eq 0 ]]; then
  HARNESSES=("codex" "claude" "louie")
fi

# Preserve user order while removing duplicates.
declare -A seen
uniq_harnesses=()
for h in "${HARNESSES[@]}"; do
  if [[ -z "${seen[$h]:-}" ]]; then
    seen[$h]=1
    uniq_harnesses+=("$h")
  fi
done

HARNESS_CSV=""
for h in "${uniq_harnesses[@]}"; do
  if [[ -n "$HARNESS_CSV" ]]; then
    HARNESS_CSV+=","
  fi
  HARNESS_CSV+="$h"
done

cmd=(
  python3
  "${ROOT_DIR}/scripts/agent_eval_loop.py"
  --journeys "$JOURNEYS"
  --harnesses "$HARNESS_CSV"
  --skills-mode "$SKILLS_MODE"
  --skills-profile "$SKILLS_PROFILE"
  --case-ids "$CASE_IDS"
  --grading "$GRADING"
  --oracle-harness "$ORACLE_HARNESS"
  --oracle-model "$ORACLE_MODEL"
  --oracle-timeout-s "$ORACLE_TIMEOUT_S"
  --oracle-min-score-default "$ORACLE_MIN_SCORE_DEFAULT"
  --louie-url "$LOUIE_URL"
  --timeout-s "$TIMEOUT_S"
  --max-workers "$MAX_WORKERS"
  --claude-cwd "$CLAUDE_CWD"
  --codex-cwd "$CODEX_CWD"
  --oracle-claude-cwd "$ORACLE_CLAUDE_CWD"
  --oracle-codex-cwd "$ORACLE_CODEX_CWD"
  --claude-models "$CLAUDE_MODELS"
  --codex-models "$CODEX_MODELS"
  --skills-delivery "$SKILLS_DELIVERY"
  --otel-service "$OTEL_SERVICE"
)

if [[ -n "$OUT_DIR" ]]; then
  cmd+=(--out "$OUT_DIR")
fi

if [[ "$OTEL" == "true" ]]; then
  cmd+=(--otel)
fi

if [[ "$FAILFAST" == "true" ]]; then
  cmd+=(--failfast)
fi

if [[ "$ORACLE_STRICT" == "true" ]]; then
  cmd+=(--oracle-strict)
fi

if [[ -n "$OTEL_ENDPOINT" ]]; then
  cmd+=(--otel-endpoint "$OTEL_ENDPOINT")
fi

exec "${cmd[@]}"
