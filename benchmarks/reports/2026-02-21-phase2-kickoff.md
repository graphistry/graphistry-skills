# 2026-02-21 Phase2 Kickoff Quick Check

- Generated: `2026-02-21T21:07:52.693266+00:00`
- Inputs:
  - `/home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/quick_alljourneys_on_rows.jsonl`

## Overall

- Pass: `14/16` (87.5%)
- KPI intents (`execution_grade,realistic_capability`): `5/6` (83.3%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| alignment_legacy | 1 | 2 | 50.0% | 15701.5 | 0.8333 |
| execution_grade | 2 | 2 | 100.0% | 21910.5 | 1.0000 |
| guardrail | 2 | 2 | 100.0% | 11438.5 | 1.0000 |
| realistic_capability | 3 | 4 | 75.0% | 41498.2 | 0.9875 |
| runtime_smoke | 4 | 4 | 100.0% | 8122.0 | 1.0000 |
| skill_pressure | 2 | 2 | 100.0% | 12553.5 | 1.0000 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 14 | 16 | 87.5% | 20105.6 | 0.9760 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 14 | 16 | 87.5% | 20105.6 | 0.9760 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | on | 2 | 3 | 66.7% | 24923.0 | 0.9833 |
| codex | on | 3 | 3 | 100.0% | 45015.0 | 1.0000 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | on | 6 | 8 | 75.0% | 14691.8 | 0.9521 |
| codex | on | 8 | 8 | 100.0% | 25519.4 | 1.0000 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | on | 6 | 8 | 75.0% | 14691.8 | 0.9521 |
| codex | default | on | 8 | 8 | 100.0% | 25519.4 | 1.0000 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | on | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_edge_query_filter | 0.6667 | 11530.0 | /home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/quick_alljourneys_on_rows.jsonl |
| claude | default | on | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_csv_degree_gfql_viz_private | 0.9500 | 37364.0 | /home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/quick_alljourneys_on_rows.jsonl |
