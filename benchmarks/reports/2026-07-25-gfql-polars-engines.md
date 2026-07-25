# GFQL Polars engine pack (claude, graphistry 0.58.0)

- Generated: `2026-07-25T08:13:34.380922+00:00`
- Inputs: redacted (`1` file(s))

## Overall

- Pass: `12/14` (85.7%)
- KPI intents (`execution_grade,realistic_capability`): `12/14` (85.7%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| realistic_capability | 12 | 14 | 85.7% | 107825.5 | 0.9612 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 12 | 14 | 85.7% | 107825.5 | 0.9612 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 12 | 14 | 85.7% | 107825.5 | 0.9612 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 5 | 7 | 71.4% | 132300.0 | 0.9224 |
| claude | on | 7 | 7 | 100.0% | 83351.0 | 1.0000 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 5 | 7 | 71.4% | 132300.0 | 0.9224 |
| claude | on | 7 | 7 | 100.0% | 83351.0 | 1.0000 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | off | 5 | 7 | 71.4% | 132300.0 | 0.9224 |
| claude | default | on | 7 | 7 | 100.0% | 83351.0 | 1.0000 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | off | realistic_capability | pygraphistry_gfql_polars_engines_v1 | polars_auto_engine_regression | 0.8571 | 343047.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_polars_engines_v1 | polars_gpu_availability_fallback_ownership | 0.6000 | 135042.0 |

## Methodology and caveats

- **Harness**: `claude` only. The `codex` half could not run — usage credits were exhausted for the
  window (every cell returned `You've hit your usage limit`, produced no model output, and was
  discarded rather than scored). Re-run the pack on `codex` before treating these as cross-harness.
- **Environment matters more than usual for this pack.** Agents probe the installed `graphistry`
  before answering. This run used a dedicated venv with the **released `graphistry==0.58.0`** plus
  `polars` on `PATH`, i.e. the configuration a real user has.
  - Against a stale install (0.45.4, predating the Polars engines) both arms collapse: agents
    "verify" that Polars does not exist and answer with `engine='cudf'`.
  - Against a source checkout on `PYTHONPATH` both arms reach 100%: the baseline simply reads the
    implementation.
  Only the released-install configuration reported here measures the skill rather than the box.
- **Composition**: 12 cells from one matrix run plus 2 cells (`hypergraph_polars_engine_refusal`)
  re-run after a deterministic check was widened, and 1 baseline cell
  (`polars_auto_engine_regression`, skills=off) re-run at a 600s timeout because its first attempt hit
  the 240s limit. All 14 rows are graded under the same final check set; no row carries a harness error.
- **Baseline isolation**: verified — no `skills=off` run read a `SKILL.md`.
- **Check tuning disclosure**: three deterministic checks were widened during development because they
  failed answers that were correct on the substance (a program written to a file rather than inlined;
  "does not pick the engine"/"GPU-or-error" instead of the literal word "fallback"; "zero Polars
  branches" instead of "no dispatch"). The substance bar was not lowered, but the phrasing latitude was
  tuned against observed correct answers, so a small overfitting risk remains.
- **Where the baseline actually loses** (both genuine content failures, not timeouts):
  - `polars_auto_engine_regression` (0.85): never states that the default/automatic engine resolves a
    Polars input graph to pandas — it treats the pandas output as a mystery rather than the documented
    behavior.
  - `polars_gpu_availability_fallback_ownership` (0.60): does not establish that `polars-gpu` is
    GPU-or-error and that the application, not PyGraphistry, owns the fallback.
