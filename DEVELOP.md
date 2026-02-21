# Development Guide

This file is for contributors working on skills and eval harnesses.

## Prerequisites

- Run from repo root: `/home/lmeyerov/Work/graphistry-skills`
- CLIs on `PATH`: `codex`, `claude`, `jq`
- Auth configured for each runtime (`~/.codex`, `~/.claude`)

Optional (for OTel trace capture + inspection):

- Local OTel stack running (from sibling repo workflow): `./dc-otel`
- Health check: `./bin/otel/status`

## Repo Map

- Skills: `.agents/skills/<skill>/SKILL.md`
- Journeys: `evals/journeys/*.json`
- Runner: `bin/agent.sh`
- Core eval engine: `scripts/agent_eval_loop.py`
- Checked-in benchmark packs: `benchmarks/data/*` and `benchmarks/reports/*`

## Validate Skills Before Sweeps

```bash
python3 scripts/ci/validate_skills.py
./bin/evals/codex-skills-smoke.sh
./bin/evals/claude-skills-smoke.sh
```

## Native Skill Env Setup (Manual)

```bash
./scripts/evals/setup_codex_skill_env.sh --env-dir evals/env/codex
./scripts/evals/setup_claude_skill_env.sh --env-dir evals/env/claude
```

Notes:

- Codex native skills are loaded from `.codex/skills/` under runtime CWD.
- Claude native skills are loaded from `.claude/skills/` under runtime CWD.

## Fast Iteration (Subset Cases)

Use this while editing skill text.

```bash
./bin/agent.sh \
  --codex --claude \
  --journeys pygraphistry_persona_journeys_v1 \
  --case-ids persona_novice_fraud_table_to_viz_algo,persona_connector_analyst_workflow \
  --skills-mode both \
  --skills-delivery native \
  --max-workers 2 \
  --failfast
```

## Sweep Recipes

### 1) Persona sweep, baseline vs skills (codex + claude)

```bash
OUT="/tmp/graphistry_skills_persona_$(date +%Y%m%d-%H%M%S)"
./bin/agent.sh \
  --codex --claude \
  --journeys pygraphistry_persona_journeys_v1 \
  --skills-mode both \
  --skills-delivery native \
  --max-workers 2 \
  --failfast \
  --out "$OUT"
```

### 2) Model matrix sweep (Codex family)

```bash
OUT="/tmp/graphistry_skills_codex_model_matrix_$(date +%Y%m%d-%H%M%S)"
./bin/agent.sh \
  --codex \
  --journeys pygraphistry_persona_journeys_v1 \
  --case-ids persona_novice_fraud_table_to_viz_algo,persona_advanced_coloring_with_gfql_slices,persona_connector_analyst_workflow \
  --skills-mode both \
  --skills-delivery native \
  --codex-models gpt-5,gpt-5-codex,gpt-5.3-codex,gpt-5.3-codex-spark \
  --max-workers 2 \
  --failfast \
  --out "$OUT"
```

### 3) Model matrix sweep (Claude tiers)

```bash
OUT="/tmp/graphistry_skills_claude_model_matrix_$(date +%Y%m%d-%H%M%S)"
./bin/agent.sh \
  --claude \
  --journeys pygraphistry_persona_journeys_v1 \
  --case-ids persona_novice_fraud_table_to_viz_algo,persona_advanced_coloring_with_gfql_slices,persona_connector_analyst_workflow \
  --skills-mode both \
  --skills-delivery native \
  --claude-models sonnet,opus \
  --max-workers 2 \
  --failfast \
  --out "$OUT"
```

### 4) Combined cross-runtime matrix (Codex + Claude)

```bash
OUT="/tmp/graphistry_skills_cross_runtime_matrix_$(date +%Y%m%d-%H%M%S)"
./bin/agent.sh \
  --codex --claude \
  --journeys pygraphistry_persona_journeys_v1 \
  --case-ids persona_novice_fraud_table_to_viz_algo,persona_advanced_coloring_with_gfql_slices,persona_connector_analyst_workflow \
  --skills-mode both \
  --skills-delivery native \
  --codex-models gpt-5,gpt-5-codex,gpt-5.3-codex,gpt-5.3-codex-spark \
  --claude-models sonnet,opus \
  --max-workers 2 \
  --failfast \
  --out "$OUT"
```

## OTel-Enabled Sweeps

Enable OTel on any sweep:

```bash
OUT="/tmp/graphistry_skills_otel_$(date +%Y%m%d-%H%M%S)"
./bin/agent.sh \
  --codex --claude \
  --journeys pygraphistry_persona_journeys_v1 \
  --skills-mode both \
  --skills-delivery native \
  --max-workers 2 \
  --failfast \
  --otel \
  --out "$OUT"
```

Verify traces were recorded:

```bash
TRACE_ID="$(tail -n 1 "$OUT/rows.jsonl" | jq -r '.trace_id')"
./bin/otel/cmds/trace2tree "$TRACE_ID"
```

Notes:

- `rows.jsonl` stores per-row `trace_id` and `traceparent`.
- `otel_ids.json` and `report.md` are emitted when run finalization completes.

## Minimal Result Slices

All rows:

```bash
jq -r '[.case_id,.harness,.model,.skills_enabled,.pass_bool,.latency_ms] | @tsv' "$OUT/rows.jsonl" | column -t
```

Summary:

```bash
jq -s '
  {
    total: length,
    pass: (map(select(.pass_bool)) | length),
    off_total: (map(select(.skills_enabled|not)) | length),
    off_pass: (map(select((.skills_enabled|not) and .pass_bool)) | length),
    on_total: (map(select(.skills_enabled)) | length),
    on_pass: (map(select(.skills_enabled and .pass_bool)) | length)
  }' "$OUT/rows.jsonl"
```

By model:

```bash
jq -s '
  group_by(.model) |
  map({
    model: .[0].model,
    off: ((map(select((.skills_enabled|not) and .pass_bool)) | length|tostring) + "/" + (map(select(.skills_enabled|not)) | length|tostring)),
    on: ((map(select(.skills_enabled and .pass_bool)) | length|tostring) + "/" + (map(select(.skills_enabled)) | length|tostring))
  })' "$OUT/rows.jsonl"
```

## Generate a Report

Create a markdown + JSON report from one run:

```bash
python3 scripts/benchmarks/make_report.py \
  --rows "$OUT/rows.jsonl" \
  --title "Graphistry Skills Eval Report" \
  --out-md "$OUT/report.md" \
  --out-json "$OUT/report.json"
```

Create one combined report from multiple run outputs:

```bash
python3 scripts/benchmarks/make_report.py \
  --rows /tmp/graphistry_skills_persona_YYYYMMDD-HHMMSS/rows.jsonl \
  --rows /tmp/graphistry_skills_codex_model_matrix_YYYYMMDD-HHMMSS/rows.jsonl \
  --rows /tmp/graphistry_skills_claude_model_matrix_YYYYMMDD-HHMMSS/rows.jsonl \
  --title "Graphistry Skills Combined Report" \
  --out-md benchmarks/reports/$(date +%Y-%m-%d)-local-sweep.md \
  --out-json benchmarks/data/$(date +%Y-%m-%d)-local-sweep/combined_metrics.json
```

## Baseline Isolation Notes

For Codex native-mode evals, `agent_eval_loop.py` creates mode-scoped native env dirs and mode-scoped `CODEX_HOME` under each run directory. This avoids baseline contamination from globally installed skills when comparing `skills-mode off` vs `on`.

## Publishing Benchmarks

Suggested process:

1. Run clean sweeps into `/tmp/...`.
2. Copy finalized run artifacts into `benchmarks/data/<date-tag>/runs/...`.
3. Regenerate/refresh combined metrics/report files under `benchmarks/data/<date-tag>/`.
4. Update or add report markdown under `benchmarks/reports/`.
