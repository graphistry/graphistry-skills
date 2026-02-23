# Codex Effort A/B (gpt-5.3-codex, high vs medium, 2026-02-23)

- Generated: `2026-02-23T06:21:20.681289+00:00`
- Inputs:
  - `/tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl`
  - `/tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl`

## Overall

- Pass: `173/200` (86.5%)
- KPI intents (`execution_grade,realistic_capability`): `55/68` (80.9%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| alignment_legacy | 28 | 28 | 100.0% | 19903.7 | 1.0000 |
| execution_grade | 12 | 12 | 100.0% | 15706.6 | 1.0000 |
| guardrail | 22 | 24 | 91.7% | 20311.2 | 0.9875 |
| realistic_capability | 43 | 56 | 76.8% | 43219.0 | 0.9478 |
| runtime_smoke | 17 | 20 | 85.0% | 14864.2 | 0.9542 |
| skill_pressure | 41 | 48 | 85.4% | 23918.3 | 0.9401 |
| speed_routing | 10 | 12 | 83.3% | 35081.8 | 0.9500 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 173 | 200 | 86.5% | 27599.3 | 0.9619 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 173 | 200 | 86.5% | 27599.3 | 0.9619 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| codex | off | 26 | 34 | 76.5% | 43561.6 | 0.9396 |
| codex | on | 29 | 34 | 85.3% | 33166.2 | 0.9744 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| codex | off | 82 | 100 | 82.0% | 32539.1 | 0.9441 |
| codex | on | 91 | 100 | 91.0% | 22659.5 | 0.9797 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| codex | gpt-5.3-codex | off | 82 | 100 | 82.0% | 32539.1 | 0.9441 |
| codex | gpt-5.3-codex | on | 91 | 100 | 91.0% | 22659.5 | 0.9797 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| codex | gpt-5.3-codex | off | guardrail | pygraphistry_guardrails_v1 | connector_routing_with_fallback | 0.8000 | 7548.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | off | guardrail | pygraphistry_guardrails_v1 | gfql_remote_edge_pattern_real_methods | 0.9000 | 31634.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | off | realistic_capability | pygraphistry_coverage_expansion_v1 | coverage_analyst_connector_triage | 0.9091 | 67542.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | off | realistic_capability | pygraphistry_coverage_expansion_v1 | coverage_analyst_social_claim_reuse | 0.8571 | 71077.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | off | realistic_capability | pygraphistry_coverage_expansion_v1 | coverage_analyst_social_claim_reuse | 0.8571 | 29965.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | off | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_connector_dataframe_to_plot | 0.9333 | 51132.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | off | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_connector_dataframe_to_plot | 0.8000 | 39690.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | off | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_hypergraph_temporal_gfql_layout | 0.4545 | 102045.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | off | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_hypergraph_temporal_gfql_layout | 0.6364 | 58554.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | off | realistic_capability | pygraphistry_persona_journeys_v1 | persona_precomputed_embeddings_flow | 0.5000 | 39299.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | off | runtime_smoke | pygraphistry_louie_subset_v1 | louie_ai_search | 0.6667 | 29285.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | off | runtime_smoke | pygraphistry_louie_subset_v1 | louie_privacy_snippet | 0.7500 | 14404.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | off | skill_pressure | pygraphistry_skill_pressure_v1 | core_first_plot_with_auth | 0.8750 | 17871.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | off | skill_pressure | pygraphistry_skill_pressure_v1 | core_first_plot_with_auth | 0.8750 | 14391.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | off | skill_pressure | pygraphistry_skill_pressure_v1 | privacy_safe_share_url | 0.5000 | 38476.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | off | skill_pressure | pygraphistry_skill_pressure_v1 | privacy_safe_share_url | 0.5000 | 28697.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | off | skill_pressure | pygraphistry_skill_pressure_v1 | static_export_text_modes | 0.0000 | 40210.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | off | speed_routing | pygraphistry_router_speed_v1 | speed_route_viz_geo_icons | 0.6000 | 15266.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | on | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_connector_dataframe_to_plot | 0.8000 | 30266.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | on | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_hypergraph_temporal_gfql_layout | 0.8182 | 75132.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | on | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_hypergraph_temporal_gfql_layout | 0.8182 | 42667.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | on | realistic_capability | pygraphistry_e2e_big_journeys_v1 | e2e_remote_slim_ai_gfql_viz | 0.7778 | 124013.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | on | realistic_capability | pygraphistry_persona_journeys_v1 | persona_connector_analyst_workflow | 0.9167 | 29240.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
| codex | gpt-5.3-codex | on | runtime_smoke | pygraphistry_louie_subset_v1 | louie_ai_search | 0.6667 | 18530.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | on | skill_pressure | pygraphistry_skill_pressure_v1 | core_first_plot_with_auth | 0.8750 | 21175.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | on | skill_pressure | pygraphistry_skill_pressure_v1 | privacy_safe_share_url | 0.5000 | 19132.0 | /tmp/graphistry_skills_codex_full_effort_high_20260222-183309/rows.jsonl |
| codex | gpt-5.3-codex | on | speed_routing | pygraphistry_router_speed_v1 | speed_route_viz_geo_icons | 0.8000 | 48322.0 | /tmp/graphistry_skills_codex_full_effort_medium_nofailfast_20260222-193835/rows.jsonl |
