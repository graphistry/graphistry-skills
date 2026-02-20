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

if [[ -n "$PROMPT_FILE" ]]; then
  PROMPT="$(cat "$PROMPT_FILE")"
fi

SKILLS_TEXT=""
if [[ -n "$SKILLS_TEXT_FILE" && -f "$SKILLS_TEXT_FILE" ]]; then
  SKILLS_TEXT="$(cat "$SKILLS_TEXT_FILE")"
fi

if [[ -z "$PROMPT" ]]; then
  echo '{"ok":false,"harness":"louie","error":"Missing prompt","response_text":"","latency_ms":0}'
  exit 0
fi

if [[ -z "$RAW_OUT" ]]; then
  RAW_OUT="/tmp/louie-harness.$$.log"
fi
mkdir -p "$(dirname "$RAW_OUT")"

python3 - "$PROMPT" "$SKILLS_TEXT" "$RAW_OUT" "$TRACEPARENT" "$TIMEOUT_S" "$LOUIE_URL" <<'PY'
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

prompt = sys.argv[1]
skills_text = sys.argv[2]
raw_out = Path(sys.argv[3])
traceparent = sys.argv[4]
timeout_s = int(sys.argv[5])
base_url = sys.argv[6].rstrip("/")

start = time.time()

final_prompt = prompt
if skills_text.strip():
    final_prompt = (
        "Use the following skill guidance when relevant:\n\n"
        + skills_text
        + "\n\nUser task:\n"
        + prompt
    )

def trace_id_from_traceparent(value: str) -> str | None:
    parts = value.split("-") if value else []
    if len(parts) == 4:
        return parts[1]
    return None


def post_json(url: str, body: dict, headers: dict[str, str], timeout: int) -> tuple[int, str]:
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def post_empty(url: str, headers: dict[str, str], timeout: int) -> tuple[int, str]:
    req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def parse_api_chat(raw_text: str) -> tuple[str, str | None, str | None]:
    response_text = ""
    dthread_id = None
    run_id = None

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if len(lines) == 1:
        try:
            payload = json.loads(lines[0])
            if isinstance(payload, dict):
                txt = payload.get("response") or payload.get("final_answer")
                if txt:
                    response_text = str(txt)
                dthread_id = payload.get("dthread_id") or dthread_id
                run_id = payload.get("run_id") or run_id
        except Exception:
            pass

    for line in lines:
        try:
            payload = json.loads(line)
        except Exception:
            continue

        if isinstance(payload, dict):
            if "dthread_id" in payload:
                dthread_id = payload.get("dthread_id") or dthread_id
            if "run_id" in payload:
                run_id = payload.get("run_id") or run_id

            obj = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
            if obj.get("type") == "TextElement":
                response_text = str(obj.get("text") or response_text)

            if not response_text and payload.get("type") == "TextElement":
                response_text = str(payload.get("text") or response_text)

    return response_text, dthread_id, run_id


result = {
    "ok": False,
    "harness": "louie",
    "response_text": "",
    "latency_ms": 0,
    "trace_id": trace_id_from_traceparent(traceparent),
    "raw_ref": str(raw_out),
}

try:
    token = None
    if "LOUIE_TOKEN" in os.environ and os.environ["LOUIE_TOKEN"].strip():
        token = os.environ["LOUIE_TOKEN"].strip()
    elif "GRAPHISTRY_TOKEN" in os.environ and os.environ["GRAPHISTRY_TOKEN"].strip():
        token = os.environ["GRAPHISTRY_TOKEN"].strip()

    if token is None:
        headers = {"Content-Type": "application/json"}
        status, body = post_empty(f"{base_url}/auth/anonymous", headers=headers, timeout=min(timeout_s, 60))
        data = json.loads(body)
        token = data.get("token")
        if not token:
            raise RuntimeError(f"Anonymous auth failed (status={status})")

    common_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    if traceparent:
        common_headers["traceparent"] = traceparent

    query = urllib.parse.urlencode({
        "query": final_prompt,
        "agent": "LouieAgent",
        "ignore_traces": "false",
        "share_mode": "Private",
    })
    single_url = f"{base_url}/web/chat_singleshot/?{query}"

    try:
        req = urllib.request.Request(
            single_url,
            headers={k: v for k, v in common_headers.items() if k != "Content-Type"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            raw_out.write_text(raw, encoding="utf-8")
            parsed = json.loads(raw)
            response_text = str(parsed.get("response") or parsed.get("final_answer") or "")
            result.update({
                "ok": bool(response_text.strip()) and resp.status == 200,
                "response_text": response_text,
            })
            if not result["ok"]:
                result["error"] = "Single-shot response missing text"

    except Exception as first_error:
        api_chat_url = f"{base_url}/api/chat/?agent=LouieAgent&name=agent-eval"
        status, body = post_json(api_chat_url, {"query": final_prompt}, headers=common_headers, timeout=timeout_s)
        raw_out.write_text(body, encoding="utf-8")
        response_text, dthread_id, run_id = parse_api_chat(body)

        result.update({
            "ok": bool(response_text.strip()) and status == 200,
            "response_text": response_text,
            "dthread_id": dthread_id,
            "run_id": run_id,
        })

        if not result["ok"]:
            result["error"] = f"api/chat missing text; singleshot error: {first_error}"

except Exception as exc:
    result["ok"] = False
    result["error"] = str(exc)

result["latency_ms"] = int((time.time() - start) * 1000)
print(json.dumps(result))
PY
