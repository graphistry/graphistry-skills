# Graphistry Skills Baseline Isolation Sweep (2026-03-01)

- Generated: `2026-03-01T18:02:12.893510+00:00`
- Inputs: redacted (`3` file(s))

## Overall

- Pass: `80/112` (71.4%)
- KPI intents (`execution_grade,realistic_capability`): `24/34` (70.6%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| alignment_legacy | 10 | 14 | 71.4% | 40059.6 | 0.8548 |
| execution_grade | 6 | 6 | 100.0% | 25974.7 | 1.0000 |
| guardrail | 10 | 12 | 83.3% | 22348.2 | 0.9556 |
| policy_behavior | 6 | 10 | 60.0% | 108011.5 | 0.8833 |
| realistic_capability | 18 | 28 | 64.3% | 78479.4 | 0.9193 |
| runtime_smoke | 7 | 10 | 70.0% | 22654.2 | 0.9083 |
| skill_pressure | 18 | 26 | 69.2% | 17278.0 | 0.8481 |
| speed_routing | 5 | 6 | 83.3% | 52535.2 | 0.9333 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 74 | 102 | 72.5% | 40914.4 | 0.9010 |
| deterministic+trace | 6 | 10 | 60.0% | 108011.5 | 0.8833 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 80 | 112 | 71.4% | 46905.2 | 0.8995 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| codex | off | 8 | 17 | 47.1% | 62980.2 | 0.8777 |
| codex | on | 16 | 17 | 94.1% | 75447.5 | 0.9893 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| codex | off | 29 | 56 | 51.8% | 46429.4 | 0.8163 |
| codex | on | 51 | 56 | 91.1% | 47380.9 | 0.9826 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| codex | default | off | 29 | 56 | 51.8% | 46429.4 | 0.8163 |
| codex | default | on | 51 | 56 | 91.1% | 47380.9 | 0.9826 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| codex | default | off | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_edge_query_filter | 0.3333 | 49740.0 |
| codex | default | off | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_output_hop_slicing | 0.8000 | 49955.0 |
| codex | default | off | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_remote_nodes_subset | 0.5000 | 38452.0 |
| codex | default | off | alignment_legacy | pygraphistry_moltbook_alignment_v1 | gfql_where_owner_compare | 0.3333 | 141297.0 |
| codex | default | off | guardrail | pygraphistry_guardrails_v1 | connector_routing_with_fallback | 0.8000 | 18965.0 |
| codex | default | off | guardrail | pygraphistry_guardrails_v1 | privacy_private_not_public | 0.6667 | 10366.0 |
| codex | default | off | policy_behavior | pygraphistry_docs_source_policy_v1 | heavy_clone_allowed_tag | 0.5000 | 104191.0 |
| codex | default | off | policy_behavior | pygraphistry_docs_source_policy_v1 | light_rtd_blocked_fallback_github | 0.6667 | 53821.0 |
| codex | default | off | realistic_capability | pygraphistry_coverage_expansion_v1 | coverage_analyst_connector_triage | 0.9091 | 144452.0 |
| codex | default | off | realistic_capability | pygraphistry_coverage_expansion_v1 | coverage_analyst_social_claim_reuse | 0.8571 | 99240.0 |
| codex | default | off | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_connector_dataframe_to_plot | 0.7333 | 64234.0 |
| codex | default | off | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_hypergraph_temporal_gfql_layout | 0.5455 | 75662.0 |
| codex | default | off | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_remote_slim_ai_gfql_viz | 0.8889 | 163933.0 |
| codex | default | off | realistic_capability | pygraphistry_persona_journeys_v1 | persona_advanced_coloring_with_gfql_slices | 0.8000 | 47623.0 |
| codex | default | off | realistic_capability | pygraphistry_persona_journeys_v1 | persona_novice_fraud_table_to_viz_algo | 0.9375 | 51761.0 |
| codex | default | off | realistic_capability | pygraphistry_persona_journeys_v1 | persona_precomputed_embeddings_flow | 0.7500 | 60662.0 |
| codex | default | off | realistic_capability | pygraphistry_persona_journeys_v1 | persona_umap_text_featurization | 0.5000 | 22921.0 |
| codex | default | off | runtime_smoke | pygraphistry_louie_subset_v1 | louie_ai_search | 0.6667 | 35751.0 |
| codex | default | off | runtime_smoke | pygraphistry_louie_subset_v1 | louie_privacy_snippet | 0.7500 | 14456.0 |
| codex | default | off | skill_pressure | pygraphistry_skill_pressure_v1 | ai_semantic_search | 0.5000 | 17592.0 |
| codex | default | off | skill_pressure | pygraphistry_skill_pressure_v1 | auth_safety | 0.8000 | 6234.0 |
| codex | default | off | skill_pressure | pygraphistry_skill_pressure_v1 | core_first_plot_with_auth | 0.8750 | 11469.0 |
| codex | default | off | skill_pressure | pygraphistry_skill_pressure_v1 | gfql_remote_python_remote_postprocess | 0.5000 | 19406.0 |
| codex | default | off | skill_pressure | pygraphistry_skill_pressure_v1 | hypergraph_plus_materialize | 0.0000 | 19929.0 |
| codex | default | off | skill_pressure | pygraphistry_skill_pressure_v1 | privacy_safe_share_url | 0.5000 | 17950.0 |
| codex | default | off | skill_pressure | pygraphistry_skill_pressure_v1 | static_export_text_modes | 0.0000 | 9145.0 |
| codex | default | off | speed_routing | pygraphistry_router_speed_v1 | speed_route_viz_geo_icons | 0.6000 | 38845.0 |
| codex | default | on | policy_behavior | pygraphistry_docs_source_policy_v1 | heavy_clone_allowed_tag | 0.8333 | 240021.0 |
| codex | default | on | policy_behavior | pygraphistry_docs_source_policy_v1 | light_rtd_blocked_fallback_github | 0.8333 | 66454.0 |
| codex | default | on | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_hypergraph_temporal_gfql_layout | 0.8182 | 190431.0 |
| codex | default | on | runtime_smoke | pygraphistry_louie_subset_v1 | louie_ai_search | 0.6667 | 17869.0 |
| codex | default | on | skill_pressure | pygraphistry_skill_pressure_v1 | core_first_plot_with_auth | 0.8750 | 11394.0 |
