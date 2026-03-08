# REST Phase2 Full Sweep (2026-03-07)

- Generated: `2026-03-08T00:27:04.688472+00:00`
- Inputs: redacted (`1` file(s))

## Overall

- Pass: `39/66` (59.1%)
- KPI intents (`execution_grade,realistic_capability`): `19/30` (63.3%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| alignment_legacy | 20 | 36 | 55.6% | 13579.6 | 0.8327 |
| realistic_capability | 19 | 30 | 63.3% | 16685.6 | 0.8785 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 39 | 66 | 59.1% | 14991.4 | 0.8535 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 39 | 66 | 59.1% | 14991.4 | 0.8535 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| codex | off | 5 | 15 | 33.3% | 19993.5 | 0.7837 |
| codex | on | 14 | 15 | 93.3% | 13377.6 | 0.9733 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| codex | off | 9 | 33 | 27.3% | 16968.2 | 0.7290 |
| codex | on | 30 | 33 | 90.9% | 13014.5 | 0.9780 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| codex | default | off | 9 | 33 | 27.3% | 16968.2 | 0.7290 |
| codex | default | on | 30 | 33 | 90.9% | 13014.5 | 0.9780 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_admin_files_for_specific_user | 0.6250 | 6396.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_admin_find_old_files_runbook | 0.6000 | 22634.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_admin_list_users_boundary | 0.7143 | 7480.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_auth_env_or_token_no_literals | 0.7500 | 31295.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_auth_troubleshooting_checklist | 0.4000 | 7080.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_boundary_remote_gfql_python | 0.5000 | 5500.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_docs_fallback_policy_canonical | 0.6000 | 5046.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_iframe_collections_tricky_url_api | 0.7500 | 16675.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_no_token_in_query_params | 0.6000 | 6066.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_org_and_personal_key_navigation | 0.8000 | 19004.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_privacy_and_share_url | 0.6000 | 14532.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_url_params_layout_and_encoding_bridge | 0.6000 | 10606.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_viz_gfql_handoff_boundary | 0.4286 | 7130.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_viz_url_debug_blank_graph | 0.3333 | 6878.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_admin_healthcheck_routes | 0.7500 | 18390.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_author_field_user_scoping_caveat | 0.5000 | 19336.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_collections_url_param_guidance | 0.7500 | 20864.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_dataset_lifecycle_endpoints | 0.7500 | 21149.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_gfql_to_rest_viz_handoff_example | 0.8333 | 6315.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_no_fake_rest_endpoints | 0.8571 | 14560.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_password_to_jwt_then_list_files | 0.7143 | 16590.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_rest_vs_python_gfql_boundary | 0.6000 | 6890.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_sessions_experimental_behavior | 0.7500 | 39763.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_single_use_token_gateway_flow | 0.2500 | 16156.0 |
| codex | default | on | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_admin_files_for_specific_user | 0.8750 | 11257.0 |
| codex | default | on | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_url_params_layout_and_encoding_bridge | 0.8000 | 10805.0 |
| codex | default | on | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_rest_vs_python_gfql_boundary | 0.6000 | 5890.0 |
