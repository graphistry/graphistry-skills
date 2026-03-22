# GFQL Skills Expansion Eval (2026-03-21, post-audit)

- Generated: `2026-03-22T00:48:12.695566+00:00`
- Inputs: redacted (`1` file(s))

## Overall

- Pass: `27/33` (81.8%)
- KPI intents (`execution_grade,realistic_capability`): `18/20` (90.0%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| functional | 3 | 7 | 42.9% | 42992.4 | 0.8372 |
| guardrails | 6 | 6 | 100.0% | 17143.5 | 1.0000 |
| realistic_capability | 18 | 20 | 90.0% | 18156.1 | 0.9686 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 27 | 33 | 81.8% | 23240.3 | 0.9464 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 27 | 33 | 81.8% | 23240.3 | 0.9464 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | on | 18 | 20 | 90.0% | 18156.1 | 0.9686 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | on | 27 | 33 | 81.8% | 23240.3 | 0.9464 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | on | 27 | 33 | 81.8% | 23240.3 | 0.9464 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | on | functional | pygraphistry_gfql_functional_v1 | func_cypher_match_filter | 0.8182 | 17878.0 |
| claude | default | on | functional | pygraphistry_gfql_functional_v1 | func_cypher_order_limit | 0.9091 | 42038.0 |
| claude | default | on | functional | pygraphistry_gfql_functional_v1 | func_edge_directions | 0.8333 | 77516.0 |
| claude | default | on | functional | pygraphistry_gfql_functional_v1 | func_let_ref_dag | 0.3000 | 122376.0 |
| claude | default | on | realistic_capability | pygraphistry_gfql_let_dag_v1 | let_with_astcall | 0.5714 | 18363.0 |
| claude | default | on | realistic_capability | pygraphistry_gfql_row_pipeline_v1 | astcall_layout_in_pipeline | 0.8000 | 11199.0 |
