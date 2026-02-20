#!/usr/bin/env bash
set -euo pipefail

PROMPT=""
PROMPT_FILE=""
SKILLS_TEXT_FILE=""
RAW_OUT=""
TRACEPARENT=""
TIMEOUT_S="${AGENT_HARNESS_TIMEOUT_S:-240}"
WORKDIR="${AGENT_HARNESS_WORKDIR:-$PWD}"

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
    --cd)
      WORKDIR="$2"
      shift 2
      ;;
    --louie-url)
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -n "$PROMPT_FILE" ]]; then
  PROMPT="$(cat "$PROMPT_FILE")"
fi

SKILLS_TEXT=""
if [[ -n "$SKILLS_TEXT_FILE" && -f "$SKILLS_TEXT_FILE" ]]; then
  SKILLS_TEXT="$(cat "$SKILLS_TEXT_FILE")"
fi

if [[ -z "$PROMPT" ]]; then
  echo '{"ok":false,"harness":"codex","error":"Missing prompt","response_text":"","latency_ms":0}'
  exit 0
fi

if [[ -z "$RAW_OUT" ]]; then
  RAW_OUT="/tmp/codex-harness.$$.log"
fi
mkdir -p "$(dirname "$RAW_OUT")"

FINAL_PROMPT="$PROMPT"
if [[ -n "$SKILLS_TEXT" ]]; then
  TMP_PROMPT="$(mktemp)"
  {
    echo "Use the following skill guidance when relevant:"
    echo
    echo "$SKILLS_TEXT"
    echo
    echo "User task:"
    echo "$PROMPT"
  } > "$TMP_PROMPT"
  FINAL_PROMPT="$(cat "$TMP_PROMPT")"
  rm -f "$TMP_PROMPT"
fi

start_ms=$(date +%s%3N)
set +e
timeout "$TIMEOUT_S" codex exec --json --skip-git-repo-check --color never --cd "$WORKDIR" "$FINAL_PROMPT" > "$RAW_OUT" 2>&1
exit_code=$?
set -e
end_ms=$(date +%s%3N)
latency_ms=$((end_ms - start_ms))

python3 - "$RAW_OUT" "$exit_code" "$latency_ms" "$TRACEPARENT" <<'PY'
import json
import sys
from pathlib import Path

raw_path = Path(sys.argv[1])
exit_code = int(sys.argv[2])
latency_ms = int(sys.argv[3])
traceparent = sys.argv[4]

thread_id = None
response_text = ""
usage = {}
error = None

raw_text = ""
if raw_path.exists():
    raw_text = raw_path.read_text(encoding="utf-8", errors="replace")

for line in raw_text.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        payload = json.loads(line)
    except Exception:
        continue

    if payload.get("type") == "thread.started":
        thread_id = payload.get("thread_id")

    if payload.get("type") == "item.completed":
        item = payload.get("item") or {}
        if item.get("type") == "agent_message":
            response_text = str(item.get("text") or "")

    if payload.get("type") == "turn.completed":
        usage = payload.get("usage") or {}

if not response_text and raw_text.strip():
    response_text = raw_text.strip().splitlines()[-1]

if exit_code != 0:
    error = f"codex exec exited with code {exit_code}"

trace_id = None
parts = traceparent.split("-") if traceparent else []
if len(parts) == 4:
    trace_id = parts[1]

result = {
    "ok": exit_code == 0 and bool(response_text.strip()),
    "harness": "codex",
    "response_text": response_text,
    "latency_ms": latency_ms,
    "thread_id": thread_id,
    "trace_id": trace_id,
    "usage": usage,
    "raw_ref": str(raw_path),
}

if error:
    result["error"] = error

print(json.dumps(result))
PY
