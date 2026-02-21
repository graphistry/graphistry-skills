# 2026-02-21 Phase2 Combined

- Generated: `2026-02-21T21:31:50.001342+00:00`
- Inputs:
  - `/home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/quick_alljourneys_on_rows.jsonl`
  - `/home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/coverage_expansion_both_rows.jsonl`

## Overall

- Pass: `24/28` (85.7%)
- KPI intents (`execution_grade,realistic_capability`): `15/18` (83.3%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| alignment_legacy | 1 | 2 | 50.0% | 15701.5 | 0.8333 |
| execution_grade | 2 | 2 | 100.0% | 21910.5 | 1.0000 |
| guardrail | 2 | 2 | 100.0% | 11438.5 | 1.0000 |
| realistic_capability | 13 | 16 | 81.2% | 36745.4 | 0.9790 |
| runtime_smoke | 4 | 4 | 100.0% | 8122.0 | 1.0000 |
| skill_pressure | 2 | 2 | 100.0% | 12553.5 | 1.0000 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 24 | 28 | 85.7% | 26558.0 | 0.9761 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 24 | 28 | 85.7% | 26558.0 | 0.9761 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 3 | 3 | 100.0% | 15374.7 | 1.0000 |
| claude | on | 5 | 6 | 83.3% | 21968.0 | 0.9917 |
| codex | off | 2 | 3 | 66.7% | 69657.7 | 0.9524 |
| codex | on | 5 | 6 | 83.3% | 40807.2 | 0.9762 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 3 | 3 | 100.0% | 15374.7 | 1.0000 |
| claude | on | 9 | 11 | 81.8% | 15870.3 | 0.9652 |
| codex | off | 2 | 3 | 66.7% | 69657.7 | 0.9524 |
| codex | on | 10 | 11 | 90.9% | 28541.2 | 0.9870 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | off | 3 | 3 | 100.0% | 15374.7 | 1.0000 |
| claude | default | on | 9 | 11 | 81.8% | 15870.3 | 0.9652 |
| codex | default | off | 2 | 3 | 66.7% | 69657.7 | 0.9524 |
| codex | default | on | 10 | 11 | 90.9% | 28541.2 | 0.9870 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | on | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_edge_query_filter | 0.6667 | 11530.0 | /home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/quick_alljourneys_on_rows.jsonl |
| claude | default | on | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_csv_degree_gfql_viz_private | 0.9500 | 37364.0 | /home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/quick_alljourneys_on_rows.jsonl |
| codex | default | off | realistic_capability | pygraphistry_coverage_expansion_v1 | coverage_analyst_social_claim_reuse | 0.8571 | 55887.0 | /home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/coverage_expansion_both_rows.jsonl |
| codex | default | on | realistic_capability | pygraphistry_coverage_expansion_v1 | coverage_analyst_connector_triage | 0.8571 | 26858.0 | /home/lmeyerov/Work/graphistry-skills/benchmarks/data/2026-02-21-phase2-kickoff/coverage_expansion_both_rows.jsonl |
