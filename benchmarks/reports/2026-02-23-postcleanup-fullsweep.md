# Graphistry Skills Post-cleanup Full Sweep (2026-02-23)

- Generated: `2026-02-24T10:54:28.877927+00:00`
- Inputs: redacted (`1` file(s))

## Overall

- Pass: `169/200` (84.5%)
- KPI intents (`execution_grade,realistic_capability`): `55/68` (80.9%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| alignment_legacy | 22 | 28 | 78.6% | 21865.0 | 0.8119 |
| execution_grade | 12 | 12 | 100.0% | 17760.8 | 1.0000 |
| guardrail | 21 | 24 | 87.5% | 22888.0 | 0.9572 |
| realistic_capability | 43 | 56 | 76.8% | 52551.5 | 0.9556 |
| runtime_smoke | 14 | 20 | 70.0% | 12558.4 | 0.9083 |
| skill_pressure | 45 | 48 | 93.8% | 32939.4 | 0.9646 |
| speed_routing | 12 | 12 | 100.0% | 49753.2 | 1.0000 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 169 | 200 | 84.5% | 33734.2 | 0.9384 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 169 | 200 | 84.5% | 33734.2 | 0.9384 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 11 | 17 | 64.7% | 33959.0 | 0.9296 |
| claude | on | 13 | 17 | 76.5% | 19134.1 | 0.9616 |
| codex | off | 15 | 17 | 88.2% | 74751.0 | 0.9733 |
| codex | on | 16 | 17 | 94.1% | 57803.6 | 0.9893 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 35 | 50 | 70.0% | 23501.0 | 0.8560 |
| claude | on | 40 | 50 | 80.0% | 13811.8 | 0.9277 |
| codex | off | 46 | 50 | 92.0% | 55367.3 | 0.9802 |
| codex | on | 48 | 50 | 96.0% | 42256.6 | 0.9897 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | off | 35 | 50 | 70.0% | 23501.0 | 0.8560 |
| claude | default | on | 40 | 50 | 80.0% | 13811.8 | 0.9277 |
| codex | default | off | 46 | 50 | 92.0% | 55367.3 | 0.9802 |
| codex | default | on | 48 | 50 | 96.0% | 42256.6 | 0.9897 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | default | off | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_edge_query_filter | 0.3333 | 12953.0 |
| claude | default | off | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_output_hop_slicing | 0.0000 | 7274.0 |
| claude | default | off | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_remote_nodes_subset | 0.0000 | 36307.0 |
| claude | default | off | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_where_owner_compare | 0.0000 | 8447.0 |
| claude | default | off | guardrail | pygraphistry_guardrails_v1 | gfql_real_methods_only | 0.7500 | 9118.0 |
| claude | default | off | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_connector_dataframe_to_plot | 0.8000 | 19521.0 |
| claude | default | off | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_hypergraph_temporal_gfql_layout | 0.6364 | 20054.0 |
| claude | default | off | realistic_capability | pygraphistry_persona_journeys_v1 | persona_novice_fraud_table_to_viz_algo | 0.9375 | 15209.0 |
| claude | default | off | realistic_capability | pygraphistry_persona_journeys_v1 | persona_org_and_api_key_navigation | 0.9286 | 6878.0 |
| claude | default | off | realistic_capability | pygraphistry_persona_journeys_v1 | persona_precomputed_embeddings_flow | 0.7500 | 12321.0 |
| claude | default | off | realistic_capability | pygraphistry_persona_journeys_v1 | persona_umap_text_featurization | 0.7500 | 21580.0 |
| claude | default | off | runtime_smoke | pygraphistry_louie_subset_v1 | louie_ai_search | 0.6667 | 6403.0 |
| claude | default | off | runtime_smoke | pygraphistry_louie_subset_v1 | louie_privacy_snippet | 0.7500 | 5642.0 |
| claude | default | off | skill_pressure | pygraphistry_skill_pressure_v1 | hypergraph_plus_materialize | 0.0000 | 10666.0 |
| claude | default | off | skill_pressure | pygraphistry_skill_pressure_v1 | privacy_safe_share_url | 0.5000 | 33190.0 |
| claude | default | on | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_output_hop_slicing | 0.4000 | 13017.0 |
| claude | default | on | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_where_owner_compare | 0.0000 | 12324.0 |
| claude | default | on | guardrail | pygraphistry_guardrails_v1 | auth_env_no_literal_creds | 0.8889 | 9320.0 |
| claude | default | on | guardrail | pygraphistry_guardrails_v1 | privacy_private_not_public | 0.3333 | 5921.0 |
| claude | default | on | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_connector_dataframe_to_plot | 0.8000 | 19911.0 |
| claude | default | on | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_hypergraph_temporal_gfql_layout | 0.8182 | 32511.0 |
| claude | default | on | realistic_capability | pygraphistry_persona_journeys_v1 | persona_advanced_coloring_with_gfql_slices | 0.8000 | 18961.0 |
| claude | default | on | realistic_capability | pygraphistry_persona_journeys_v1 | persona_org_and_api_key_navigation | 0.9286 | 7215.0 |
| claude | default | on | runtime_smoke | pygraphistry_louie_subset_v1 | louie_ai_search | 0.6667 | 5330.0 |
| claude | default | on | runtime_smoke | pygraphistry_louie_subset_v1 | louie_privacy_snippet | 0.7500 | 4980.0 |
| codex | default | off | realistic_capability | pygraphistry_coverage_expansion_v1 | coverage_analyst_connector_triage | 0.9091 | 112241.0 |
| codex | default | off | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_hypergraph_temporal_gfql_layout | 0.6364 | 151056.0 |
| codex | default | off | runtime_smoke | pygraphistry_louie_subset_v1 | louie_ai_search | 0.6667 | 36435.0 |
| codex | default | off | skill_pressure | pygraphistry_skill_pressure_v1 | auth_safety | 0.8000 | 10271.0 |
| codex | default | on | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_hypergraph_temporal_gfql_layout | 0.8182 | 119072.0 |
| codex | default | on | runtime_smoke | pygraphistry_louie_subset_v1 | louie_ai_search | 0.6667 | 13326.0 |
