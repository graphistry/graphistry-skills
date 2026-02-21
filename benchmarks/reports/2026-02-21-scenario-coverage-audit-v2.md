# Journey Coverage Audit

- Generated: `2026-02-21T21:09:13.871699+00:00`
- Journey dir: `evals/journeys`
- Journeys: `9`
- Cases: `46`

## Persona
| bucket | count | pct |
| --- | --- | --- |
| novice | 1 | 2.2% |
| analyst | 3 | 6.5% |
| engineer | 6 | 13.0% |
| admin | 4 | 8.7% |
| unspecified | 32 | 69.6% |

- Missing buckets: `(none)`

## Domain
| bucket | count | pct |
| --- | --- | --- |
| fraud | 1 | 2.2% |
| cybersecurity | 25 | 54.3% |
| social-media | 1 | 2.2% |
| platform | 18 | 39.1% |
| generic | 1 | 2.2% |

- Missing buckets: `(none)`

## Task Family
| bucket | count | pct |
| --- | --- | --- |
| runtime_smoke | 5 | 10.9% |
| safety_guardrail | 5 | 10.9% |
| auth | 7 | 15.2% |
| ingest_etl | 5 | 10.9% |
| shaping_viz | 7 | 15.2% |
| gfql_query | 7 | 15.2% |
| ai_ml | 4 | 8.7% |
| connectors | 1 | 2.2% |
| other | 5 | 10.9% |

- Missing buckets: `(none)`

## Input Level
| bucket | count | pct |
| --- | --- | --- |
| raw_table | 9 | 19.6% |
| events_table | 1 | 2.2% |
| bound_graph | 1 | 2.2% |
| remote_dataset | 3 | 6.5% |
| conceptual | 32 | 69.6% |

- Missing buckets: `(none)`

## Output Depth
| bucket | count | pct |
| --- | --- | --- |
| one_liner | 3 | 6.5% |
| snippet | 27 | 58.7% |
| workflow | 9 | 19.6% |
| e2e_workflow | 1 | 2.2% |
| bullets_or_links | 6 | 13.0% |

- Missing buckets: `(none)`

## Persona x Task Matrix
| persona | runtime_smoke | safety_guardrail | auth | ingest_etl | shaping_viz | gfql_query | ai_ml | connectors | other |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| novice | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| analyst | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 |
| engineer | 0 | 1 | 1 | 0 | 0 | 2 | 2 | 0 | 0 |
| admin | 0 | 0 | 3 | 0 | 1 | 0 | 0 | 0 | 0 |
| unspecified | 5 | 4 | 2 | 4 | 5 | 5 | 2 | 0 | 5 |

