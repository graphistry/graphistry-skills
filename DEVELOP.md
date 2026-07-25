# Development Guide

This file is for contributors working on skills and eval harnesses.

## Prerequisites

- Run from repo root: `graphistry-skills/`
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
- Checked-in benchmark artifacts (public-safe): `benchmarks/data/*/combined_metrics.json` and `benchmarks/reports/*`
- Release workflow (maintainers): `RELEASE.md`

## Skill Scope Conventions

- User-facing/published skills are the `pygraphistry*` set.
- Internal maintainer skills live under `.agents/skills/internal/` (for example: `.agents/skills/internal/plan`, `.agents/skills/internal/eval-otel`, `.agents/skills/internal/benchmarks`) and are flagged with `metadata.internal: true`.
- Keep internal maintainer skills out of default end-user install snippets.

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

## GFQL Expansion Evals

Run the GFQL-specific eval suites (deterministic):

```bash
./bin/agent.sh \
  --claude \
  --journeys pygraphistry_gfql_cypher_v1,pygraphistry_gfql_let_dag_v1,pygraphistry_gfql_backward_fixes_v1,pygraphistry_gfql_row_pipeline_v1 \
  --skills-mode both \
  --skills-delivery native \
  --max-workers 2 \
  --out "$OUT"
```

Run functional execution evals (code is actually executed with pygraphistry):

```bash
# Step 1: Generate responses
./bin/agent.sh \
  --claude \
  --journeys pygraphistry_gfql_functional_v1 \
  --skills-mode on \
  --skills-delivery native \
  --max-workers 2 \
  --out "$OUT"

# Step 2: Execute generated code and validate results
cd ~/Work/pygraphistry && PYTHONPATH="$PWD" python3 \
  /path/to/graphistry-skills/scripts/evals/gfql_functional_check.py \
  --rows "$OUT/rows.jsonl" \
  --journey-dir /path/to/graphistry-skills/evals/journeys
```

The functional checker extracts Python code blocks from responses, runs them with pygraphistry, and validates: no exceptions, expected output strings, correct result shapes.

**Precondition — keep the eval box's `graphistry` current.** Agents under evaluation often probe the
installed package before answering. If the importable `graphistry` predates a feature the skills
document, the agent "verifies" against a stale install and answers wrongly — e.g. a 0.45.x install
reports `'polars-gpu' is not a valid EngineAbstract`, so `pygraphistry_gfql_polars_engines_v1` cases
get answered with `engine='cudf'` and invented policy hooks. The Polars/Polars-GPU engines require
`graphistry>=0.58`. Check with `python3 -c "import graphistry; print(graphistry.__version__)"` before a
sweep, and prefer running against a source checkout via `PYTHONPATH` when evaluating unreleased
behavior. This confound hits `skills=on` and `skills=off` equally, so it does not bias the delta, but it
does depress both.

Non-invasive fix for a sweep — point the agents' `python3` at a current checkout instead of upgrading
the system interpreter:

```bash
PYTHONPATH="$HOME/Work/pygraphistry" ./bin/agent.sh --claude \
  --journeys pygraphistry_gfql_polars_engines_v1 --skills-mode both ...
```

Or benchmark the configuration a real user has — a venv holding the released package. `python3 -m venv`
may be unusable on Debian/Ubuntu boxes without `ensurepip`; `uv` works:

```bash
uv venv /tmp/gs-eval-venv
uv pip install --python /tmp/gs-eval-venv/bin/python 'graphistry==0.58.0' 'polars>=1.29' pandas pyarrow
PATH="/tmp/gs-eval-venv/bin:$PATH" ./bin/agent.sh --claude --journeys ... --skills-mode both
```

### GPU verification (`polars-gpu`) on dgx-spark

`engine='polars-gpu'` needs the RAPIDS `cudf_polars` stack, which is not installed on the CPU dev box.
Use the prebuilt NVIDIA RAPIDS image on `dgx-spark` (NVIDIA GB10, aarch64) — the same image family
`pygraphistry/docker/test-rapids-official-local.sh` uses. A named volume keeps the graphistry install
warm across runs, so only the first invocation pays for the pip step:

```bash
# one-time: reusable venv volume layered on the image's RAPIDS stack
ssh dgx-spark 'docker volume create gfql-gpu-venv'
ssh dgx-spark 'docker run --rm --gpus all --user root -v gfql-gpu-venv:/opt/gfql-venv \
  nvcr.io/nvidia/rapidsai/base:26.02-cuda13-py3.13 bash -lc "
    python -m venv --system-site-packages /opt/gfql-venv &&
    /opt/gfql-venv/bin/pip -q install --no-cache-dir graphistry==0.58.0 &&
    chmod -R a+rwX /opt/gfql-venv"'

# each run: mount the volume plus /tmp for the script under test
scp probe.py dgx-spark:/tmp/
ssh dgx-spark 'docker run --rm --gpus all --user root \
  -v gfql-gpu-venv:/opt/gfql-venv -v /tmp:/hosttmp \
  nvcr.io/nvidia/rapidsai/base:26.02-cuda13-py3.13 /opt/gfql-venv/bin/python /hosttmp/probe.py'
```

`--system-site-packages` is what makes the image's `cudf` / `cudf_polars` visible to the venv. Verified
stack: `graphistry 0.58.0`, `polars 1.35.2`, `cudf_polars 26.02.01`.

Use this to check claims that cannot be tested on CPU — that `polars-gpu` executes on device and returns
Polars frames matching the CPU result, and where the GPU actually wins. Measured on GB10 for a single-hop
`MATCH ... RETURN b`: **0.83x at 100k rows (slower than CPU), 1.41x at 1M, 0.98x at 5M** — so treat
"GPU is faster" as a claim to verify per query shape, not a default.

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
2. Keep raw run artifacts local/private (`rows.jsonl`, `manifest.json`, traces, logs).
3. Generate public-safe outputs:
```bash
python3 scripts/benchmarks/make_report.py \
  --public-safe \
  --rows /tmp/<run>/rows.jsonl \
  --title "<report title>" \
  --out-md benchmarks/reports/<date-tag>.md \
  --out-json benchmarks/data/<date-tag>/combined_metrics.json
```
4. Generate README snippet:
```bash
python3 scripts/benchmarks/readme_snippet.py \
  --rows "/tmp/<run>/rows.jsonl" \
  --title "Fresh eval sweep with isolated baseline"
```
5. Update `README.md` Evals section with the generated snippet.
6. Update `benchmarks/README.md` with the new pack reference.
7. Check in sanitized report, `combined_metrics.json`, and README updates.

## Releasing Versions

For semver bump + publish steps (release branch, changelog cut, PR merge, tag, GitHub release), use:

- `RELEASE.md` (maintainer release guide)
- `.agents/skills/internal/release/SKILL.md` (internal release skill)
