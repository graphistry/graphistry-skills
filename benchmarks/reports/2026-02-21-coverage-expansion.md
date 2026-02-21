# 2026-02-21 Coverage Expansion Journey

- Generated: `2026-02-21T21:31:39.890741+00:00`
- Inputs:
  - `/home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/coverage_expansion_both_rows.jsonl`

## Overall

- Pass: `10/12` (83.3%)
- KPI intents (`execution_grade,realistic_capability`): `10/12` (83.3%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| realistic_capability | 10 | 12 | 83.3% | 35161.2 | 0.9762 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 10 | 12 | 83.3% | 35161.2 | 0.9762 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 10 | 12 | 83.3% | 35161.2 | 0.9762 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 3 | 3 | 100.0% | 15374.7 | 1.0000 |
| claude | on | 3 | 3 | 100.0% | 19013.0 | 1.0000 |
| codex | off | 2 | 3 | 66.7% | 69657.7 | 0.9524 |
| codex | on | 2 | 3 | 66.7% | 36599.3 | 0.9524 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 3 | 3 | 100.0% | 15374.7 | 1.0000 |
| claude | on | 3 | 3 | 100.0% | 19013.0 | 1.0000 |
| codex | off | 2 | 3 | 66.7% | 69657.7 | 0.9524 |
| codex | on | 2 | 3 | 66.7% | 36599.3 | 0.9524 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | off | 3 | 3 | 100.0% | 15374.7 | 1.0000 |
| claude | default | on | 3 | 3 | 100.0% | 19013.0 | 1.0000 |
| codex | default | off | 2 | 3 | 66.7% | 69657.7 | 0.9524 |
| codex | default | on | 2 | 3 | 66.7% | 36599.3 | 0.9524 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| codex | default | off | realistic_capability | pygraphistry_coverage_expansion_v1 | coverage_analyst_social_claim_reuse | 0.8571 | 55887.0 | /home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/coverage_expansion_both_rows.jsonl |
| codex | default | on | realistic_capability | pygraphistry_coverage_expansion_v1 | coverage_analyst_connector_triage | 0.8571 | 26858.0 | /home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/coverage_expansion_both_rows.jsonl |
