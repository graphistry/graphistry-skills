# Per-skill evals pack (claude sonnet-5, graphistry 0.58.0)

- Generated: `2026-07-26T00:29:10.721090+00:00`
- Inputs: redacted (`1` file(s))

## Overall

- Pass: `38/64` (59.4%)
- KPI intents (`execution_grade,realistic_capability`): `38/64` (59.4%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| realistic_capability | 38 | 64 | 59.4% | 23122.7 | 0.8384 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic_fallback | 1 | 1 | 100.0% | 14500.0 | 1.0000 |
| hybrid | 37 | 63 | 58.7% | 23259.6 | 0.8358 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| hybrid | 38 | 64 | 59.4% | 23122.7 | 0.8384 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 13 | 32 | 40.6% | 27200.8 | 0.7743 |
| claude | on | 25 | 32 | 78.1% | 19044.7 | 0.9025 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 13 | 32 | 40.6% | 27200.8 | 0.7743 |
| claude | on | 25 | 32 | 78.1% | 19044.7 | 0.9025 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | sonnet | off | 13 | 32 | 40.6% | 27200.8 | 0.7743 |
| claude | sonnet | on | 25 | 32 | 78.1% | 19044.7 | 0.9025 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | graphistry_01 | 0.8250 | 12114.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | graphistry_03 | 0.3250 | 31088.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | graphistry_rest_api_01 | 0.7250 | 12650.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | graphistry_rest_api_02 | 0.6750 | 31094.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | graphistry_rest_api_03 | 0.8600 | 30834.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_02 | 0.6750 | 72313.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_03 | 0.8000 | 27117.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_04 | 0.6750 | 16533.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_ai_03 | 0.6083 | 30776.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_ai_04 | 0.7933 | 13989.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_connectors_01 | 0.6000 | 32469.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_connectors_03 | 0.8000 | 41964.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_core_01 | 0.5750 | 13330.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_core_03 | 0.5833 | 24602.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_gfql_01 | 0.2750 | 26691.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_gfql_02 | 0.4250 | 24088.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_visualization_02 | 0.4083 | 25305.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_visualization_03 | 0.7250 | 32893.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_visualization_04 | 0.8600 | 18489.0 |
| claude | sonnet | on | realistic_capability | pygraphistry_skill_evals_v1 | graphistry_rest_api_03 | 0.5083 | 15256.0 |
| claude | sonnet | on | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_03 | 0.6500 | 13835.0 |
| claude | sonnet | on | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_ai_03 | 0.6433 | 14986.0 |
| claude | sonnet | on | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_ai_04 | 0.7733 | 14931.0 |
| claude | sonnet | on | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_connectors_01 | 0.6500 | 15934.0 |
| claude | sonnet | on | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_core_01 | 0.8750 | 14561.0 |
| claude | sonnet | on | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_gfql_01 | 0.6250 | 12556.0 |

## Result summary

- `skills=on` 25/32 (78.1%), avg score 0.90, avg 19.0s
- `skills=off` 13/32 (40.6%), avg score 0.77, avg 27.2s
- **+37.5pp pass rate, 0 regressions**, and ~1.4x faster with skills.

## Methodology

- **Model**: `claude-sonnet-5` for both the subject and the oracle judge (`--claude-models sonnet
  --oracle-model sonnet`). This differs from earlier packs, which ran the default (Opus) model — the
  numbers are therefore **not** directly comparable to `2026-03-*` or the Polars pack.
- **Grading**: `--grading hybrid`. These cases came from per-skill assertions written in English, so the
  semantic half is graded by oracle rubric and `forbidden_concepts`; deterministic checks anchor only
  explicit code/API tokens.
- **Environment**: released `graphistry==0.58.0` in a dedicated venv. A SHA-256 baseline over every `.py`
  in the installed package was taken before the sweep and re-verified after both the main run and the
  follow-up cell — identical, so no agent under test modified the library (a failure mode that
  invalidated an earlier pack).
- **Baseline isolation**: verified — no `skills=off` run read a `SKILL.md`. Zero harness errors across 64 cells.

## Case provenance and four corrected expectations

Cases were ported from `.agents/skills/*/evals/evals.json` (PR #23), a per-skill format nothing in the
repo executed. A 12-cell pilot before the full sweep caught four expectations that failed **correct**
answers; all four were fixed before these numbers were produced:

1. **Routing cases graded skill names, not substance.** The originals tested router dispatch; ported into
   an answer-text harness they required the reply to contain e.g. `pygraphistry-visualization`. A correct
   `encode_point_color('category', categorical_mapping=...)` failed, and `skills=on` scored *worse* than
   off because it answered directly instead of narrating routing.
2. **The same framing leaked into `reference_answer`** for 14 cases, so fixing rubrics alone left the
   judge still expecting routing.
3. **A stale static-export expectation** (`play:0`) treated `plot_static` as invented. `plot_static(format='png', path=...)`
   is real in 0.58.0, so a correct answer was marked down. That case now shows real lift (0.40 → 0.92).
4. **A redundant `featurize()` requirement** — `umap()` auto-featurizes when given column names, so the
   concise answer was penalized. Fixing it removed the only apparent regression.

## Remaining failures with skills on (candidate skill gaps)

`graphistry_rest_api_03`, `pygraphistry_03`, `pygraphistry_ai_03`, `pygraphistry_ai_04`,
`pygraphistry_connectors_01`, `pygraphistry_core_01`, `pygraphistry_gfql_01`. These are unreviewed — each
should be checked for whether the skill is genuinely missing guidance or the ported expectation is wrong,
given four such expectations were already found bad.
