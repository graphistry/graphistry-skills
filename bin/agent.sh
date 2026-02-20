#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

HARNESSES=()
JOURNEYS="runtime_smoke"
SKILLS_MODE="off"
SKILLS_PROFILE="pygraphistry_core"
OUT_DIR=""
LOUIE_URL="${LOUIE_URL:-http://localhost:8501}"
TIMEOUT_S="240"
OTEL="false"
OTEL_SERVICE="agent-eval-runner"
OTEL_ENDPOINT="${OTEL_EXPORTER_OTLP_ENDPOINT_GRPC:-}"

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
  --out DIR          Output run directory
  --louie-url URL    Louie base URL (default: http://localhost:8501)
  --timeout-s N      Per-harness timeout seconds (default: 240)
  --otel             Emit OTel lifecycle events via graphistrygpt helper
  --otel-service X   OTel service name (default: agent-eval-runner)
  --otel-endpoint X  OTLP endpoint (default: OTEL_EXPORTER_OTLP_ENDPOINT_GRPC)
  -h, --help         Show help

Examples:
  ./bin/agent.sh --codex --claude --journeys runtime_smoke
  ./bin/agent.sh --codex --claude --louie --skills-mode both --otel
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
    --out)
      OUT_DIR="$2"
      shift 2
      ;;
    --louie-url)
      LOUIE_URL="$2"
      shift 2
      ;;
    --timeout-s)
      TIMEOUT_S="$2"
      shift 2
      ;;
    --otel)
      OTEL="true"
      shift
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
  --louie-url "$LOUIE_URL"
  --timeout-s "$TIMEOUT_S"
  --otel-service "$OTEL_SERVICE"
)

if [[ -n "$OUT_DIR" ]]; then
  cmd+=(--out "$OUT_DIR")
fi

if [[ "$OTEL" == "true" ]]; then
  cmd+=(--otel)
fi

if [[ -n "$OTEL_ENDPOINT" ]]; then
  cmd+=(--otel-endpoint "$OTEL_ENDPOINT")
fi

exec "${cmd[@]}"
