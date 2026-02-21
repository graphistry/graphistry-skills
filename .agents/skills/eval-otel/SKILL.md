---
name: eval-otel
description: Validate eval telemetry capture and retrieval for Codex, Claude, and Louie runs. Use when proving prompt input/output recording, trace correlation, and OTel/log inspection for agent evals. (project)
---

# Eval OTel Skill

## Use This Skill For
- Proving we can record and retrieve prompt input/output during eval runs.
- Debugging missing trace/session/run correlation in `rows.jsonl`.
- Running a repeatable telemetry validation loop across `codex`, `claude`, and `louie`.

## Success Criteria (Do Not Skip)
- For each runtime under test:
  - `rows.jsonl` has non-empty `case_prompt`.
  - `rows.jsonl` has non-empty `response_text` for successful runs.
  - `rows.jsonl` includes `trace_id` and `raw_ref`.
  - `raw_ref` file exists and is readable.
- OTel/log retrieval is demonstrated for the same run IDs/trace IDs when available.
- Any runtime not proven is explicitly marked as not proven (with error evidence).

## Preconditions
- OTel stack is up:
  - `./bin/otel/status`
- Eval loop is available:
  - `./bin/agent.sh`
- Harness CLIs are installed and authenticated as needed (`codex`, `claude`).
- Louie endpoint is reachable for Louie proof:
  - `LOUIE_URL` or `--louie-url`
  - auth environment as required by local setup

## Minimal Proof Loop

### 1) Run evals with telemetry enabled
```bash
./bin/agent.sh \
  --codex --claude --louie \
  --journeys runtime_smoke \
  --skills-mode off \
  --otel \
  --failfast \
  --out /tmp/agent_eval_otel_smoke
```

### 2) Verify artifact-level prompt in/out capture
```bash
sed -n '1,40p' /tmp/agent_eval_otel_smoke/rows.jsonl
ls -la /tmp/agent_eval_otel_smoke/raw
```

Check:
- `case_prompt` is present (input capture).
- `response_text` is present for successful rows (output capture).
- `raw_ref` points to a real log file.

### 3) Verify OTel/log retrieval
Use a `trace_id` from `rows.jsonl`:
```bash
./bin/otel/inspect <trace_id> --logs --full
```

If trace lookup fails, record that explicitly and do not claim full OTel proof.

## Runtime-Specific Notes

### Codex
- Harness parses `codex exec --json`.
- Expect `runtime_ids.thread_id` and usage fields on success.
- Can route through proxy with `OPENAI_BASE_URL` when needed.

### Claude
- Harness parses `claude --verbose -p --output-format stream-json`.
- Expect `runtime_ids.session_id` and usage fields on success.

### Louie
- Harness sends `traceparent` and attempts single-shot then `/api/chat/`.
- If requests time out, do not claim prompt output proof for Louie.
- Keep timeout evidence in `rows.jsonl` and raw logs.

## Reporting Template
- `codex`: proven / not proven
- `claude`: proven / not proven
- `louie`: proven / not proven
- `artifact-level prompt in/out`: proven / partial
- `otel-level retrieval`: proven / partial
- `blockers`: concise list with concrete error messages

## Guardrails
- Do not hardcode credentials in tracked files.
- Do not claim success based on assumptions or docs alone.
- Distinguish:
  - artifact capture proof (`rows.jsonl` + raw logs)
  - OTel backend retrieval proof (`bin/otel/inspect`)
