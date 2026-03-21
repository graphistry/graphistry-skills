# GFQL Skills Expansion Eval (2026-03-21)

- Generated: `2026-03-21T21:46:58.049149+00:00`
- Inputs: redacted (`2` file(s))

## Overall

- Pass: `28/66` (42.4%)
- KPI intents (`execution_grade,realistic_capability`): `18/40` (45.0%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| functional | 3 | 14 | 21.4% | 73419.5 | 0.6568 |
| guardrails | 7 | 12 | 58.3% | 19190.4 | 0.8975 |
| realistic_capability | 18 | 40 | 45.0% | 38869.9 | 0.7842 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 28 | 66 | 42.4% | 42620.5 | 0.7778 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 28 | 66 | 42.4% | 42620.5 | 0.7778 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 1 | 20 | 5.0% | 59824.4 | 0.6164 |
| claude | on | 17 | 20 | 85.0% | 17915.3 | 0.9519 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 2 | 33 | 6.1% | 62983.1 | 0.6245 |
| claude | on | 26 | 33 | 78.8% | 22257.9 | 0.9310 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | off | 2 | 33 | 6.1% | 62983.1 | 0.6245 |
| claude | default | on | 26 | 33 | 78.8% | 22257.9 | 0.9310 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | off | functional | pygraphistry_gfql_functional_v1 | func_chain_hop_bounds | 0.5000 | 122426.0 |
| claude | default | off | functional | pygraphistry_gfql_functional_v1 | func_chain_hop_filter | 0.8182 | 74133.0 |
| claude | default | off | functional | pygraphistry_gfql_functional_v1 | func_cypher_match_filter | 0.8182 | 87377.0 |
| claude | default | off | functional | pygraphistry_gfql_functional_v1 | func_cypher_order_limit | 0.2727 | 120434.0 |
| claude | default | off | functional | pygraphistry_gfql_functional_v1 | func_edge_directions | 0.5000 | 114903.0 |
| claude | default | off | functional | pygraphistry_gfql_functional_v1 | func_graph_constructor | 0.3000 | 120591.0 |
| claude | default | off | functional | pygraphistry_gfql_functional_v1 | func_let_ref_dag | 0.3000 | 122359.0 |
| claude | default | off | guardrails | pygraphistry_gfql_backward_fixes_v1 | correct_imports | 0.8333 | 9429.0 |
| claude | default | off | guardrails | pygraphistry_gfql_backward_fixes_v1 | cypher_not_blocked | 0.8889 | 53093.0 |
| claude | default | off | guardrails | pygraphistry_gfql_backward_fixes_v1 | no_deprecated_chain | 0.3333 | 8417.0 |
| claude | default | off | guardrails | pygraphistry_gfql_backward_fixes_v1 | no_hallucinated_methods | 0.8571 | 17584.0 |
| claude | default | off | guardrails | pygraphistry_gfql_backward_fixes_v1 | remote_accepts_cypher | 0.8571 | 16337.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_cypher_v1 | cypher_auto_detect | 0.3333 | 14274.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_cypher_v1 | cypher_basic_match_return | 0.8333 | 11142.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_cypher_v1 | cypher_graph_constructor | 0.5000 | 93311.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_cypher_v1 | cypher_multi_stage_use | 0.3333 | 120562.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_cypher_v1 | cypher_multihop_pattern | 0.5000 | 34174.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_cypher_v1 | cypher_order_limit_params | 0.8571 | 119177.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_cypher_v1 | cypher_remote_execution | 0.3333 | 120507.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_cypher_v1 | cypher_type_alternation | 0.5000 | 33688.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_cypher_v1 | cypher_where_filter | 0.8333 | 59136.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_let_dag_v1 | let_basic_bindings | 0.3333 | 120608.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_let_dag_v1 | let_nested | 0.6667 | 29483.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_let_dag_v1 | let_ref_chain | 0.3333 | 25229.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_let_dag_v1 | let_with_astcall | 0.5714 | 25035.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_row_pipeline_v1 | astcall_degree_in_chain | 0.8000 | 21004.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_row_pipeline_v1 | astcall_layout_in_pipeline | 0.8000 | 13765.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_row_pipeline_v1 | mixed_chain_and_cypher | 0.6667 | 120601.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_row_pipeline_v1 | row_group_by_aggregation | 0.6667 | 120508.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_row_pipeline_v1 | row_order_limit | 0.6667 | 16137.0 |
| claude | default | off | realistic_capability | pygraphistry_gfql_row_pipeline_v1 | row_unwind | 0.8000 | 9827.0 |
| claude | default | on | functional | pygraphistry_gfql_functional_v1 | func_cypher_match_filter | 0.8182 | 15958.0 |
| claude | default | on | functional | pygraphistry_gfql_functional_v1 | func_cypher_order_limit | 0.8182 | 14465.0 |
| claude | default | on | functional | pygraphistry_gfql_functional_v1 | func_edge_directions | 0.7500 | 71767.0 |
| claude | default | on | functional | pygraphistry_gfql_functional_v1 | func_let_ref_dag | 0.3000 | 120429.0 |
| claude | default | on | realistic_capability | pygraphistry_gfql_let_dag_v1 | let_nested | 0.6667 | 20269.0 |
| claude | default | on | realistic_capability | pygraphistry_gfql_let_dag_v1 | let_with_astcall | 0.5714 | 17047.0 |
| claude | default | on | realistic_capability | pygraphistry_gfql_row_pipeline_v1 | astcall_layout_in_pipeline | 0.8000 | 10091.0 |
