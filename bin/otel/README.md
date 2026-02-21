# OTel Helpers (Tempo + Logs)

Minimal helpers for local OpenTelemetry traces/logs. Start the stack with `./dc-otel`
and export spans/logs via
`OTEL_EXPORTER_OTLP_ENDPOINT_GRPC=http://localhost:4317`.

`dc-otel` starts:
- Tempo (traces): http://localhost:3200
- Logs backend: http://localhost:3100
- Grafana: http://localhost:3000
- OTel Collector: http://localhost:4317

## Environment

- `OTEL_TEMPO_URL` (default `http://localhost:3200`)
- `OTEL_LOG_URL` (default `http://localhost:3100`)
- `OTEL_SERVICE_NAME` (default `py-louie`)
- `OTEL_COLLECTOR_URL` (default `http://localhost:13133`)
- `GRAPHISTRY_TOKEN` or `LOUIE_TOKEN` (optional, used by `bin/otel/status`)

Trace correlation uses `traceparent` headers (bots notebook emits these automatically).
Ports can be overridden via `data/custom.env`, `.env`, or environment variables
(see `infra/docker-compose.telemetry.yml`).
`bin/otel/status` will auto-detect API base via `.louie-ports` or `LOUIE_API_URL` when run from repo root.

## Quick Start

```bash
bin/otel/status
bin/otel/inspect --latest
bin/otel/inspect --errors
bin/otel/inspect <bots_run_id>
bin/otel/inspect <run_id> --prompts --full
bin/otel/inspect <trace_id> --logs
```

## Stack Choices (Pick One)

- Grafana stack (default): `./dc-otel` → Tempo (traces) + Loki (logs) + Prometheus (metrics) + Grafana UI.
- Phoenix only: run Phoenix + set `OTEL_EXPORTER_OTLP_ENDPOINT_GRPC` to Phoenix; LLM‑focused traces only, no Loki/Prometheus.
- Both: requires collector fan‑out or dual exporters (not in default scripts); easiest is one at a time.
- None: no OTel backend; logs stay in stdout/file only.

## Optional: Phoenix (OpenInference) Quick Test

Phoenix is a popular OSS LLM observability UI that understands OpenInference and OTel
spans. This is separate from the default `dc-otel` stack and uses its own storage.
It can run locally and ingest OTLP traces.

```bash
docker run -d --name phoenix-otel -p 6006:6006 -p 4319:4317 arizephoenix/phoenix:latest
OTEL_EXPORTER_OTLP_ENDPOINT_GRPC=http://localhost:4319 OTEL_LLM_IO_CAPTURE=true \
  ./bin/desktop-slim serve --auto-port
OTEL_EXPORTER_OTLP_ENDPOINT_GRPC=http://localhost:4319 \
  ./bin/bots/run.sh -q "1,2" -j 1 -d -t 180 -s http://localhost:$LOUIE_WEB_PORT
```

Notes:
- Phoenix does not accept OTLP logs; `StatusCode.UNIMPLEMENTED` for logs is expected.
- `OTEL_LLM_IO_CAPTURE=true` emits prompt/response events to spans; full Loki logs
  still require `OTEL_LLM_LOG_CAPTURE=true` and the local OTel collector stack.
- Phoenix UI: http://localhost:6006 (project name: `default`).

## ID Cheat Sheet

- `trace_id`: 32 hex chars (Tempo trace ID)
- `run_id`: `R_...` (Louie run id)
- `session_id`: UUID (browser session)
- `bots_run_id`: `bots_YYYYMMDD_HHMMSS`

## If You Have X, Run Y

- `bots_run_id` → `bin/otel/cmds/run-status <bots_run_id>`
- `session_id` → `bin/otel/cmds/session2runs <session_id>`
- `run_id` → `bin/otel/cmds/run2llm <run_id> [--prompts|--full|--logs|--json]` (use `--prompts --full` for preview + full)
- `trace_id` → `bin/otel/cmds/trace2tree <trace_id>` or `bin/otel/cmds/trace2logs <trace_id>`

## Command Map

- `bin/otel/inspect`: smart entry for trace/run/session/bots ids (`--errors` filters to error sessions).
- `bin/otel/status`: stack health + API capabilities summary (`--json` for artifacts).
- `bin/otel/cmds/list-sessions`: list recent sessions.
- `bin/otel/cmds/session2runs`: session → run ids.
- `bin/otel/cmds/run2llm`: run → LLM call details (`--full` uses logs backend, `--logs` shows span logs, `--json` for artifacts).
- `bin/otel/cmds/run-status`: bots run id → summary table (use `--logs` for raw logs).
- `bin/otel/cmds/list-traces`: list recent traces.
- `bin/otel/cmds/trace2tree|trace2spans|trace2events|trace2logs`: trace breakdowns.
- `bin/otel/cmds/find-errors`: error spans for a trace.
- `bin/otel/cmds/search-logs`: log search by substring.

Notes:
- Tempo span IDs are base64; `trace2logs` normalizes to hex for log queries.
- `run2llm --full` requires `OTEL_LLM_LOG_CAPTURE=true`.
- `status` will attempt `/auth/anonymous` on localhost if no token is set.
- With `LOGGING_MODE=loki-export`, enabling `OTEL_LLM_LOG_CAPTURE=true` exports LLM logs without requiring `LOG_LEVEL=TRACE`.
- Use `--service bots-client` (or `OTEL_SERVICE_NAME=bots-client`) when looking for client-side traces.
- Tool calls emit spans named `tool.<tool>.<method>` with `tool.*` attributes (name/method/args.count/run.id/dthread.id/cell.id).
- LLM spans emit `gen_ai.*` and OpenInference-compatible `llm.*` attributes, plus
  `gen_ai.client.inference.operation.details` events (when `OTEL_LLM_IO_CAPTURE=true`).
- LLM spans also include `input.value_*`/`output.value_*` metadata (sha256/bytes/truncated) for archive-ready correlation.
