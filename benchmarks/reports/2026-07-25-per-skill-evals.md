# Per-skill evals pack (claude sonnet-5, graphistry 0.58.0)

- Generated: `2026-07-26T00:59:50.055223+00:00`
- Inputs: redacted (`1` file(s))

## Overall

- Pass: `48/64` (75.0%)
- KPI intents (`execution_grade,realistic_capability`): `48/64` (75.0%)

## By Eval Intent

| eval_intent | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| realistic_capability | 48 | 64 | 75.0% | 23379.5 | 0.8821 |

## By Grading Source

| grading_source | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| deterministic_fallback | 1 | 1 | 100.0% | 14500.0 | 1.0000 |
| hybrid | 47 | 63 | 74.6% | 23520.4 | 0.8803 |

## By Grading Mode

| grading_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- |
| hybrid | 48 | 64 | 75.0% | 23379.5 | 0.8821 |

## KPI Intents: By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 16 | 32 | 50.0% | 27847.6 | 0.7988 |
| claude | on | 32 | 32 | 100.0% | 18911.4 | 0.9655 |

## By Harness + Skills Mode

| harness | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- |
| claude | off | 16 | 32 | 50.0% | 27847.6 | 0.7988 |
| claude | on | 32 | 32 | 100.0% | 18911.4 | 0.9655 |

## By Harness + Model + Skills Mode

| harness | model | skills_mode | passed | total | pass_rate | avg_latency_ms | avg_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | sonnet | off | 16 | 32 | 50.0% | 27847.6 | 0.7988 |
| claude | sonnet | on | 32 | 32 | 100.0% | 18911.4 | 0.9655 |

## Failures

| harness | model | skills_mode | eval_intent | journey_id | case_id | score | latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | graphistry_01 | 0.8250 | 12114.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | graphistry_03 | 0.3250 | 31088.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | graphistry_rest_api_01 | 0.7250 | 12650.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | graphistry_rest_api_02 | 0.6750 | 31094.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_02 | 0.6750 | 72313.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_03 | 0.6250 | 28155.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_04 | 0.6750 | 16533.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_ai_03 | 0.6250 | 21843.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_connectors_03 | 0.8000 | 41964.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_core_01 | 0.6500 | 21165.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_core_03 | 0.5833 | 24602.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_gfql_01 | 0.5500 | 22485.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_gfql_02 | 0.4250 | 24088.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_visualization_02 | 0.4083 | 25305.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_visualization_03 | 0.7250 | 32893.0 |
| claude | sonnet | off | realistic_capability | pygraphistry_skill_evals_v1 | pygraphistry_visualization_04 | 0.8600 | 18489.0 |

## Result summary

- `skills=on` **32/32 (100%)**, avg score 0.97, avg 18.9s
- `skills=off` **16/32 (50.0%)**, avg score 0.80, avg 27.8s
- **+50.0pp pass rate, 0 regressions**, ~1.5x faster with skills.

## Methodology

- **Model**: `claude-sonnet-5` for both subject and oracle judge (`--claude-models sonnet
  --oracle-model sonnet`), chosen for cost. Earlier packs ran the default (Opus) model, so these numbers
  are **not comparable** to `2026-03-*` or the Polars pack.
- **Grading**: `--grading hybrid`. The ported assertions are English, so the semantic half is graded by
  oracle rubric + `forbidden_concepts`; deterministic checks anchor only explicit code/API tokens.
- **Environment**: released `graphistry==0.58.0` in a dedicated venv, SHA-256 verified identical before
  and after every run in this pack.
- **Isolation**: no `skills=off` run read a `SKILL.md`. 0 harness errors across 64 cells.

## Read this before citing 100%

**Eight expectations were corrected after seeing model output.** Every correction was validated against
the installed library, not chosen to make a run look good — but the sequence (observe failure → verify API
→ relax expectation) carries real overfitting risk, and both arms benefited (`skills=off` also rose,
13/32 → 16/32).

What was wrong, and why:

| expectation | reality |
| --- | --- |
| `from_neo4j(` required | **the method does not exist**; the real path is `register(bolt=…)` + `graphistry.cypher(…)` |
| `embed(` required for text search | `search()` / `search_graph()` is the right entry point for a text query |
| `community\.best_partition` | answer wrote `community_louvain.best_partition`; extractor dropped the module |
| `best_partition` required | networkx ships Louvain natively (`louvain_communities`) — better for a "pure networkx" prompt |
| `featurize(` required with `umap(` | `umap()` auto-featurizes when given column names |
| `os.getenv` required | `os.environ` is equivalent |
| `e_forward(` required | `e_undirected` is at least as correct for "within 3 hops" |
| literal `graph.html` required | `settings(url_params={'menu': False})` is documented and correct |
| `play:0` for static export | `plot_static(format='png', path=…)` is real; the rubric was stale |
| skill names required in answers | the originals tested router dispatch, not answer text |

Two of these were defects inherited from the source evals rather than the port: `from_neo4j()` is an API
that has never existed, and the `play:0` static-export expectation predated `plot_static`. One was a
**judge error**: the oracle called `output_min_hops`/`output_max_hops` fabricated; they are real
`e_forward` parameters.

**A 100% skills-on rate means this pack no longer discriminates at the top.** It is now a regression
harness: useful for catching a skill that stops answering something it used to, not for measuring further
improvement. New cases should target judgment under conflicting constraints — the one class that
consistently separated arms elsewhere — rather than API recall, which a model with the package installed
can recover on its own.
