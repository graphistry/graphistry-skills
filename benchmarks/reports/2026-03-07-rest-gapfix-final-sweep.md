# REST Skills Gapfix Final Sweep (Codex, 2026-03-07)

- Generated: `2026-03-07T22:31:39.199421+00:00`
- Inputs: redacted (`1` file(s))

## Overall

- Pass: `32/52` (61.5%)
- KPI intents (`execution_grade,realistic_capability`): `16/26` (61.5%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| alignment_legacy | 16 | 26 | 61.5% | 16079.6 | 0.8692 |
| realistic_capability | 16 | 26 | 61.5% | 15957.7 | 0.8678 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 32 | 52 | 61.5% | 16018.7 | 0.8685 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 32 | 52 | 61.5% | 16018.7 | 0.8685 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| codex | off | 5 | 13 | 38.5% | 18598.4 | 0.8209 |
| codex | on | 11 | 13 | 84.6% | 13317.0 | 0.9147 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| codex | off | 8 | 26 | 30.8% | 18907.8 | 0.7797 |
| codex | on | 24 | 26 | 92.3% | 13129.5 | 0.9573 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| codex | default | off | 8 | 26 | 30.8% | 18907.8 | 0.7797 |
| codex | default | on | 24 | 26 | 92.3% | 13129.5 | 0.9573 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_admin_healthchecks_compact | 0.7500 | 9736.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_auth_env_or_token_no_literals | 0.8750 | 16192.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_auth_troubleshooting_checklist | 0.4000 | 7944.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_boundary_remote_gfql_python | 0.5000 | 6254.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_docs_fallback_policy_canonical | 0.6000 | 6301.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_iframe_collections_tricky_url_api | 0.8750 | 20987.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_no_token_in_query_params | 0.6000 | 5188.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_org_and_personal_key_navigation | 0.6000 | 38517.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_privacy_and_share_url | 0.6000 | 9803.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_url_params_layout_and_encoding_bridge | 0.8000 | 37622.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_admin_healthcheck_routes | 0.7500 | 14395.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_collections_url_param_guidance | 0.5000 | 13811.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_dataset_lifecycle_endpoints | 0.7500 | 18954.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_no_fake_rest_endpoints | 0.8571 | 12646.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_password_to_jwt_then_list_files | 0.7143 | 15622.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_rest_vs_python_gfql_boundary | 0.6000 | 5998.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_sessions_experimental_behavior | 0.7500 | 24576.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_single_use_token_gateway_flow | 0.7500 | 21129.0 |
| codex | default | on | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_nodes_edges_format_endpoints | 0.0909 | 23364.0 |
| codex | default | on | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_rest_vs_python_gfql_boundary | 0.8000 | 15148.0 |
