# Graphistry Skills Quick All-Journeys Checkpoint (2026-02-21)

- Generated: `2026-02-21T20:49:16.023030+00:00`
- Inputs:
  - `/tmp/graphistry_skills_quick_alljourneys_sample_20260221-124527/rows.jsonl`

## Overall

- Pass: `14/16` (87.5%)
- KPI intents (`execution_grade,realistic_capability`): `5/6` (83.3%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| alignment_legacy | 1 | 2 | 50.0% | 13465.5 | 0.8333 |
| execution_grade | 2 | 2 | 100.0% | 24895.5 | 1.0000 |
| guardrail | 2 | 2 | 100.0% | 9418.5 | 1.0000 |
| realistic_capability | 3 | 4 | 75.0% | 38932.0 | 0.9875 |
| runtime_smoke | 4 | 4 | 100.0% | 6861.8 | 1.0000 |
| skill_pressure | 2 | 2 | 100.0% | 12149.0 | 1.0000 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | on | 2 | 3 | 66.7% | 23966.0 | 0.9833 |
| codex | on | 3 | 3 | 100.0% | 44540.3 | 1.0000 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | on | 7 | 8 | 87.5% | 13110.2 | 0.9938 |
| codex | on | 7 | 8 | 87.5% | 24768.8 | 0.9583 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | on | 7 | 8 | 87.5% | 13110.2 | 0.9938 |
| codex | default | on | 7 | 8 | 87.5% | 24768.8 | 0.9583 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | on | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_csv_degree_gfql_viz_private | 0.9500 | 45720.0 | /tmp/graphistry_skills_quick_alljourneys_sample_20260221-124527/rows.jsonl |
| codex | default | on | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_edge_query_filter | 0.6667 | 17370.0 | /tmp/graphistry_skills_quick_alljourneys_sample_20260221-124527/rows.jsonl |
