# REST Skills Optimization Sweep (Codex, 2026-03-07)

- Generated: `2026-03-07T21:15:30.196845+00:00`
- Inputs: redacted (`1` file(s))

## Overall

- Pass: `26/40` (65.0%)
- KPI intents (`execution_grade,realistic_capability`): `15/20` (75.0%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| alignment_legacy | 11 | 20 | 55.0% | 15687.5 | 0.8229 |
| realistic_capability | 15 | 20 | 75.0% | 18926.0 | 0.9232 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 26 | 40 | 65.0% | 17306.7 | 0.8730 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic | 26 | 40 | 65.0% | 17306.7 | 0.8730 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| codex | off | 5 | 10 | 50.0% | 21590.7 | 0.8464 |
| codex | on | 10 | 10 | 100.0% | 16261.2 | 1.0000 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| codex | off | 7 | 20 | 35.0% | 20387.8 | 0.7561 |
| codex | on | 19 | 20 | 95.0% | 14225.6 | 0.9900 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| codex | default | off | 7 | 20 | 35.0% | 20387.8 | 0.7561 |
| codex | default | on | 19 | 20 | 95.0% | 14225.6 | 0.9900 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_auth_env_or_token_no_literals | 0.7500 | 22382.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_auth_troubleshooting_checklist | 0.4000 | 6328.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_docs_fallback_policy_nexus | 0.2500 | 27560.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_no_token_in_query_params | 0.8000 | 4625.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_org_and_personal_key_navigation | 0.2000 | 12213.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_privacy_and_share_url | 0.8000 | 12298.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_real_endpoints_only | 0.8571 | 47681.0 |
| codex | default | off | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_url_params_layout_and_encoding_bridge | 0.6000 | 33404.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_collections_url_param_guidance | 0.7500 | 23419.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_dataset_lifecycle_endpoints | 0.5000 | 13762.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_password_to_jwt_then_list_files | 0.7143 | 6840.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_sessions_experimental_behavior | 0.7500 | 27419.0 |
| codex | default | off | realistic_capability | pygraphistry_rest_first_principles_v1 | fp_single_use_token_gateway_flow | 0.7500 | 27902.0 |
| codex | default | on | alignment_legacy | pygraphistry_rest_eval_ports_v1 | rest_url_params_layout_and_encoding_bridge | 0.8000 | 12988.0 |
