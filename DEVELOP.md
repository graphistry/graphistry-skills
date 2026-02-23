# Development Guide

This file is for contributors working on skills and eval harnesses.

## Prerequisites

- Run from repo root: `/home/USER/Work/graphistry-skills`
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

## Grading Modes (Deterministic / Oracle / Hybrid)

Default eval scoring is deterministic checks from each journey case.

Oracle grading scaffold is also available:

```bash
OUT="/tmp/graphistry_skills_oracle_smoke_$(date +%Y%m%d-%H%M%S)"
./bin/agent.sh \
  --codex \
  --journeys runtime_smoke \
  --case-ids echo_token \
  --skills-mode off \
  --grading oracle \
  --oracle-harness codex \
  --out "$OUT"
```

Hybrid grading (deterministic + oracle conjunction) is enabled via `--grading hybrid`.

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

### 5) Codex effort A/B (high vs medium, full journeys)

Run with the same matrix and only change `AGENT_CODEX_REASONING_EFFORT`.

```bash
# high
OUT="/tmp/graphistry_skills_codex_full_effort_high_$(date +%Y%m%d-%H%M%S)"
AGENT_EVAL_NATIVE_SKILLS_MOUNT_MODE=copy \
AGENT_EVAL_NATIVE_DOCS_MODE=web-only \
AGENT_CODEX_REASONING_EFFORT=high \
./bin/agent.sh \
  --codex \
  --journeys all \
  --skills-mode both \
  --skills-profile pygraphistry_core \
  --skills-delivery native \
  --codex-models gpt-5.3-codex \
  --timeout-s 240 \
  --max-workers 2 \
  --out "$OUT"
```

```bash
# medium
OUT="/tmp/graphistry_skills_codex_full_effort_medium_$(date +%Y%m%d-%H%M%S)"
AGENT_EVAL_NATIVE_SKILLS_MOUNT_MODE=copy \
AGENT_EVAL_NATIVE_DOCS_MODE=web-only \
AGENT_CODEX_REASONING_EFFORT=medium \
./bin/agent.sh \
  --codex \
  --journeys all \
  --skills-mode both \
  --skills-profile pygraphistry_core \
  --skills-delivery native \
  --codex-models gpt-5.3-codex \
  --timeout-s 240 \
  --max-workers 2 \
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

## Coverage Audit (Scenario Breadth)

Run a coverage scan across all journeys:

```bash
python3 scripts/benchmarks/scenario_coverage_audit.py \
  --journey-dir evals/journeys \
  --out-md benchmarks/reports/$(date +%Y-%m-%d)-scenario-coverage.md \
  --out-json benchmarks/data/$(date +%Y-%m-%d)-scenario-coverage.json
```

Use this before adding new journeys to close zero-bucket or severely imbalanced dimensions.

## Baseline Isolation Notes

For Codex native-mode evals, `agent_eval_loop.py` creates mode-scoped native env dirs and mode-scoped `CODEX_HOME` under each run directory. This avoids baseline contamination from globally installed skills when comparing `skills-mode off` vs `on`.

For docs-mode control in native mode, use strict mount mode:

```bash
AGENT_EVAL_NATIVE_SKILLS_MOUNT_MODE=copy \
AGENT_EVAL_NATIVE_DOCS_MODE=toc \
./scripts/agent_eval_loop.py ...
```

and rerun with `AGENT_EVAL_NATIVE_DOCS_MODE=web-only`.

Why:
- `copy` mode isolates skill files under the run env.
- TOC mode in `copy` removes local docs mirror subtree if present.
- `manifest.json` now records `native_skills_mount_mode`, `native_docs_mode`, and `native_docs_ref`.

Note:
- Local docs mirror tooling is intentionally not part of the default shipped workflow in this repo revision.
- Reintroduce mirror experiments only in a dedicated branch with clear KPI evidence.

## Publishing Benchmarks

Suggested process:

1. Run clean sweeps into `/tmp/...`.
2. Copy finalized run artifacts into `benchmarks/data/<date-tag>/runs/...`.
3. Regenerate/refresh combined metrics/report files under `benchmarks/data/<date-tag>/`.
4. Update or add report markdown under `benchmarks/reports/`.
