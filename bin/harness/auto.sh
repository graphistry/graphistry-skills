#!/usr/bin/env bash
set -euo pipefail

PROMPT=""
PROMPT_FILE=""
SKILLS_TEXT_FILE=""
RAW_OUT=""
TRACEPARENT=""
TIMEOUT_S="${AGENT_HARNESS_TIMEOUT_S:-240}"
LOUIE_URL="${LOUIE_URL:-http://localhost:8501}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt)
      PROMPT="$2"
      shift 2
      ;;
    --prompt-file)
      PROMPT_FILE="$2"
      shift 2
      ;;
    --skills-text-file)
      SKILLS_TEXT_FILE="$2"
      shift 2
      ;;
    --raw-out)
      RAW_OUT="$2"
      shift 2
      ;;
    --traceparent)
      TRACEPARENT="$2"
      shift 2
      ;;
    --timeout-s)
      TIMEOUT_S="$2"
      shift 2
      ;;
    --louie-url)
      LOUIE_URL="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$RAW_OUT" ]]; then
  RAW_OUT="/tmp/auto-harness.$$.log"
fi

mkdir -p "$(dirname "$RAW_OUT")"
base="${RAW_OUT%.log}"
codex_raw="${base}.codex.log"
claude_raw="${base}.claude.log"

common_args=(
  --raw-out "$codex_raw"
  --traceparent "$TRACEPARENT"
  --timeout-s "$TIMEOUT_S"
  --louie-url "$LOUIE_URL"
)

if [[ -n "$PROMPT_FILE" ]]; then
  common_args+=(--prompt-file "$PROMPT_FILE")
else
  common_args+=(--prompt "$PROMPT")
fi
if [[ -n "$SKILLS_TEXT_FILE" ]]; then
  common_args+=(--skills-text-file "$SKILLS_TEXT_FILE")
fi

codex_json="$({ "$(dirname "$0")/codex.sh" "${common_args[@]}"; } 2>/dev/null || true)"

common_args[1]="$claude_raw"
claude_json="$({ "$(dirname "$0")/claude.sh" "${common_args[@]}"; } 2>/dev/null || true)"

python3 - "$codex_json" "$claude_json" <<'PY'
import json
import sys

raw_codex = sys.argv[1].strip()
raw_claude = sys.argv[2].strip()


def parse(payload: str, name: str) -> dict:
    for line in reversed(payload.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return {
        "ok": False,
        "harness": name,
        "response_text": "",
        "latency_ms": 0,
        "error": "Missing JSON output",
    }

codex = parse(raw_codex, "codex")
claude = parse(raw_claude, "claude")

selected = codex if codex.get("ok") else claude
if not selected.get("ok"):
    selected = codex

result = {
    "ok": bool(selected.get("ok")),
    "harness": "auto",
    "selected_harness": selected.get("harness"),
    "response_text": selected.get("response_text", ""),
    "latency_ms": int(codex.get("latency_ms", 0)) + int(claude.get("latency_ms", 0)),
    "trace_id": selected.get("trace_id"),
    "thread_id": selected.get("thread_id"),
    "session_id": selected.get("session_id"),
    "usage": {
        "codex": codex.get("usage", {}),
        "claude": claude.get("usage", {}),
    },
    "delegates": {
        "codex": {
            "ok": codex.get("ok"),
            "raw_ref": codex.get("raw_ref"),
            "error": codex.get("error"),
        },
        "claude": {
            "ok": claude.get("ok"),
            "raw_ref": claude.get("raw_ref"),
            "error": claude.get("error"),
        },
    },
    "raw_ref": selected.get("raw_ref"),
}

if not result["ok"]:
    result["error"] = "Both codex and claude failed"

print(json.dumps(result))
PY
