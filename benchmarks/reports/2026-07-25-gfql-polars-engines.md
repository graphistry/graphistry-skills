# GFQL Polars engine pack (claude, verified-clean graphistry 0.58.0)

- Generated: `2026-07-25T16:46:46.808323+00:00`
- Inputs: redacted (`1` file(s))

## Overall

- Pass: `12/14` (85.7%)
- KPI intents (`execution_grade,realistic_capability`): `12/14` (85.7%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| realistic_capability | 12 | 14 | 85.7% | 86163.5 | 0.9296 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| hybrid | 12 | 14 | 85.7% | 86163.5 | 0.9296 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| hybrid | 12 | 14 | 85.7% | 86163.5 | 0.9296 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 6 | 7 | 85.7% | 102058.7 | 0.9229 |
| claude | on | 6 | 7 | 85.7% | 70268.3 | 0.9364 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 6 | 7 | 85.7% | 102058.7 | 0.9229 |
| claude | on | 6 | 7 | 85.7% | 70268.3 | 0.9364 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | off | 6 | 7 | 85.7% | 102058.7 | 0.9229 |
| claude | default | on | 6 | 7 | 85.7% | 70268.3 | 0.9364 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | off | realistic_capability | pygraphistry_gfql_polars_engines_v1 | polars_gpu_availability_fallback_ownership | 0.8000 | 134467.0 |
| claude | default | on | realistic_capability | pygraphistry_gfql_polars_engines_v1 | polars_gpu_availability_fallback_ownership | 0.8200 | 84255.0 |

## Result summary — parity on pass rate, faster with skills

- `skills=on` 6/7 (85.7%), avg score 0.936, avg **70.3s**
- `skills=off` 6/7 (85.7%), avg score 0.923, avg **102.1s**
- **Pass-rate delta: 0pp.** The measurable difference is latency: skills-on reached the same answers
  ~1.45x faster. Both arms fail the same case (`polars_gpu_availability_fallback_ownership`).

This pack does **not** demonstrate a pass-rate improvement, and should not be cited as one. It is kept as
a regression harness for the Polars/Polars-GPU engine surface and as the record of the methodology
findings below.

## Methodology — read before citing these numbers

- **Environment verified, not assumed.** A SHA-256 baseline over every `.py` in the installed
  `graphistry` package was taken before the run and re-verified after; both equal
  `fc8b85f7…e0889e`. Baseline isolation verified: no `skills=off` run read a `SKILL.md`.
- **This replaces an earlier, invalid run of the same pack.** The first published matrix reported
  `skills=off` 5/7 vs `skills=on` 7/7 (+28.6pp). It was **retracted**: an agent *under evaluation* had
  edited the installed library inside the eval venv — `graphistry/Engine.py`, `resolve_engine`'s polars
  branch, `Engine.PANDAS` → `Engine.POLARS` — at 07:21 UTC, and every row of that matrix ran at 07:41 UTC
  or later. The case that drove the delta, `polars_auto_engine_regression`, asks why a result came back
  as pandas without an explicit engine; under the patched library the premise no longer held, and the
  baseline failed for an environmental reason. In the clean environment that same baseline cell **passes**
  (0.90). Prompts asking why a library behaves a certain way can induce an agent to patch the library.
- **Grading**: `--grading hybrid --oracle-harness claude`. Deterministic regex alone repeatedly failed
  substantively correct answers (a program written to a file rather than inlined; "0.83x (slower)"
  instead of "can be slower"; "zero Polars branches" instead of "no dispatch"), which inflated apparent
  lift. Judgment cases need rubric grading.
- **Harness**: `claude` only; `codex` credits were exhausted for the window and produced no model output.
- **What still discriminates**: in a separate hybrid run of the perf/tuning cases, the one case where the
  baseline substantively failed was `polars_parity_or_decline_no_fake_fallback` (oracle 0.55 vs 0.94) —
  it agreed to report pandas-executed work as `engine='polars'`. Integrity/judgment content
  differentiates; API-recall content does not, because the baseline reads the installed package.
