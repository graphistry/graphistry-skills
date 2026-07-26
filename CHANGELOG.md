# Changelog

All notable changes to graphistry-skills are documented in this file.

The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Development]
<!-- Do Not Erase This Section - Used for tracking unreleased changes -->

### Added
- **Evals / pygraphistry_skill_evals_v1**: 32 per-skill capability cases covering routing, auth/ETL, GFQL, visualization, AI, connectors, and REST — ported from the April 2026 skill-evals audit (originally `.agents/skills/*/evals/evals.json`, a parallel format nothing in the repo executed). The original semantic assertions became oracle `rubric` entries and `forbidden_concepts`; deterministic checks anchor only explicit code/API tokens, so run this journey with `--grading hybrid`.

### Changed
- **Skills / pygraphistry-gfql**: Made three buried facts scannable — the parity-or-`NotImplementedError` contract as a bulleted list (including "report the engine that actually executed"), strict-vs-autofix conversion as a table, and collect-once host-to-device (H2D) as an explicit bullet. No claim changed, only retrievability. This came out of the codex run below, where the model missed facts the skill already stated in prose.
- **Evals / pygraphistry_gfql_polars_engines_v1**: Relaxed two over-specific deterministic checks that failed correct answers — `to_pandas()` required empty parens (an answer used `to_pandas(use_pyarrow_extension_array=True)`), and the auto-engine case required the literal word "auto" (an answer said "its default Pandas execution engine", which is the same claim).
- **Skills**: Description trigger phrases rewritten across the eight user-facing skills — quoted user phrasings, symbol triggers (`g.plot()`, `.gfql()`, `engine='polars'`), explicit dispatch targets, and proactive-suggestion cues. Original work by Thomas Cook (#23), rebased onto the v0.5.0 engine/index guidance. Audit findings kept in `docs/skill-evals-audit-2026-04.md`.

### Fixed
- **Harness / codex.sh, claude.sh**: Close stdin on the CLI invocation (`< /dev/null`). `codex exec` blocks on `"Reading additional input from stdin..."` whenever it inherits a stdin that never reaches EOF — i.e. any background or non-tty caller — so cells burned their entire per-cell timeout and scored empty responses. The same cells complete in 19-26s with stdin closed. The prompt is passed as an argument, so neither CLI needs stdin.

### Removed
- **Skills / `*/evals/evals.json`**: Removed the per-skill eval format after porting its cases into the journey harness. It duplicated the journey system and had no runner, so those 32 cases had never executed.

---

### Tests
- **Cross-harness follow-up on the GFQL Polars pack (2026-07-26, `codex` `gpt-5.6-terra`, medium effort, hybrid grading, sonnet judge, released `graphistry==0.58.0`, 12 cases x skills on/off)**:
  - `skills=on` **6/12**, `skills=off` **5/12** — **+8.3pp**, 0 harness errors.
  - **Much weaker than the Claude result on the same journey, and that gap is the point.** Terra's misses were content, not phrasing: it wrote `RuntimeError` where the skill says `NotImplementedError`, omitted the autofix warning, and skipped the collect-once H2D rationale. Making those scannable moved two cases on re-run (`polars_gpu_executor_selection` 0.76 -> 0.93 pass). Skill guidance only one model can extract is under-specified guidance.
  - **Not comparable** to the Claude rows in the same report: different model and a journey that grew from 7 to 12 cases.
  - Six cases still fail with skills on under terra; terra keeps substituting `RuntimeError` for strict-mode declines despite the skill stating `NotImplementedError` in both prose and code — a model behavior, not a docs gap.
- **Per-skill evals pack (2026-07-25, `claude-sonnet-5`, released `graphistry==0.58.0`, 32 cases x skills on/off, hybrid grading)**:
  - `skills=on`: **100% pass (32/32)**, avg score 0.97, avg `18.9s`
  - `skills=off`: **50.0% pass (16/32)**, avg score 0.80, avg `27.8s`
  - **Delta: +50.0pp, 0 regressions**, ~1.5x faster with skills. Baseline isolation verified; environment SHA-verified identical before and after every run.
  - Run on Sonnet for cost, so **not comparable** to earlier packs which used the default Opus model.
  - **Eight expectations were corrected after seeing model output**, each validated against the installed library: `from_neo4j()` does not exist, `umap()` auto-featurizes, networkx ships Louvain natively, `plot_static` is real where the rubric expected `play:0`, `settings(url_params=...)` is the documented iframe path, and several regexes pinned one spelling of an equivalent answer. Both arms improved (`skills=off` 13/32 -> 16/32), and the overfitting risk is disclosed in the report.
  - At 100% skills-on the pack no longer discriminates at the top; it is kept as a regression harness.
  - Data: `benchmarks/data/2026-07-25-per-skill-evals`, report: `benchmarks/reports/2026-07-25-per-skill-evals.md`.

## [0.5.0 - 2026-07-25]

### Added
- **Skills / internal/review**: New maintainer review skill. Builds context by walking from every changed file to the repo root and reading applicable Markdown guidance (`AGENTS.md`, `SECURITY.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, `DEVELOP.md`, `README.md`) before judging the diff; severity-ordered findings; drafts GitHub comments locally and requires confirmation before posting.
- **Skills / pygraphistry-gfql**: Execution-engine section for `pandas` / `polars` / `cudf` / `polars-gpu` — explicit engine selection, result frame types, the exact engine literals (`polars-gpu` is hyphenated), off-engine analytic bridging under `call_mode='auto'`, `set_call_mode('strict')` / `GFQL_POLARS_CALL_MODE` for benchmark integrity, and GPU-or-error semantics for `polars-gpu`.
- **Skills / pygraphistry-core, pygraphistry-ai, pygraphistry**: Polars/Polars-GPU engine guidance and routing; `gfql()` has no `strict=` argument.
- **Evals / pygraphistry_gfql_polars_engines_v1**: New 12-case journey. Seven cover explicit Polars output types, a functional native-Polars round trip (asserts the result frame module is `polars`), auto-engine regression debugging, strict off-engine analytic policy, the unsupported `hypergraph()` Polars path, and GPU fallback ownership. Five more target the perf/tuning layer where reading the source misleads: GPU-is-not-a-blanket-speedup, the CPU-streaming tradeoff, refusing to relabel a pandas fallback as `engine='polars'`, executor selection, and strict-vs-autofix conversion.
- **Skills / pygraphistry-gfql**: Engine tuning section (`set_gpu_executor`, `set_cpu_streaming`, `set_call_mode` with values/defaults/env vars and Python-override > env > default live resolution), the parity-or-`NotImplementedError` contract with the surfaces that decline today, and performance guidance that refuses to promise a speedup.
- **Skills / pygraphistry-gfql**: Physical indexes — `create_index` / `show_indexes` / `index_trace`, the per-call `index_policy` kwarg (`'off'|'use'|'auto'|'force'`), index DDL (`CREATE GFQL INDEX FOR <kind>`, `SHOW GFQL INDEXES`, `DROP ...`), and the engine-aware cost gate (pandas ~0.5 of distinct source keys, polars/GPU ~0.02). Measured: a seeded chain query goes 8.90ms -> 1.68ms (5.3x) with an index, while both Cypher spellings never consult one.
- **Skills / pygraphistry-gfql**: "Which engine when" decision procedure ordered declines -> where the frames already live -> indexing -> CPU engine -> GPU, with measured numbers rather than assumed ones.
- **Docs / DEVELOP.md**: GPU verification harness (prebuilt `nvcr.io` RAPIDS image + named volume so the graphistry install stays warm, `--system-site-packages` to expose `cudf_polars`), the stale-install precondition, and the environment-integrity checksum procedure.

### Tests
- **GFQL Polars engine pack (2026-07-25, `claude`, verified-clean `graphistry==0.58.0`, 7 cases x skills on/off, hybrid grading)**:
  - `skills=on`: 85.7% pass (6/7), avg score 0.94, avg `70.3s`
  - `skills=off`: 85.7% pass (6/7), avg score 0.92, avg `102.1s`
  - **0pp pass-rate delta**; the measurable difference is latency (~1.45x faster with skills). Both arms fail the same case. Baseline isolation verified; environment SHA-verified before and after the run.
  - Kept as a regression harness for the Polars/Polars-GPU surface — **not** as evidence of pass-rate improvement.
  - Data: `benchmarks/data/2026-07-25-gfql-polars-engines`, report: `benchmarks/reports/2026-07-25-gfql-polars-engines.md`.
- **Retracted**: an earlier run of this pack reported `skills=off` 5/7 vs `skills=on` 7/7 (+28.6pp). An agent *under evaluation* had patched the installed library inside the eval venv (`graphistry/Engine.py`, `resolve_engine` polars branch, `Engine.PANDAS` -> `Engine.POLARS`) at 07:21 UTC; every row of that matrix ran at 07:41 UTC or later. The case driving the delta asks why a result is pandas without an explicit engine — a premise the patch invalidated. In a clean environment that baseline cell passes.
- **Grading**: judgment cases need `--grading hybrid --oracle-harness claude`. Deterministic regex repeatedly failed substantively correct answers, which inflated apparent lift.
- **Claude only.** The `codex` half could not run — usage credits exhausted for the window; every cell returned `You've hit your usage limit`, produced no model output, and was discarded rather than scored. Re-run on `codex` before treating the pack as cross-harness.
- **Eval environment is load-bearing for this pack.** Agents probe the installed `graphistry` before answering. Against a stale 0.45.4 install (predating the Polars engines) both arms collapse; against a source checkout on `PYTHONPATH` both reach 100%. Only a released `graphistry>=0.58` install measures the skill. `DEVELOP.md` documents the precondition and the venv/`PYTHONPATH` setup.

### Changed
- **Skills / internal/plan**: Slimmed to periodic plan-file maintenance at natural handoff points instead of per-action reloads; plan files are opt-in rather than the default for single-session work.
- **Skills / pygraphistry-core**: Do not recommend `hypergraph(..., engine='polars'|'polars-gpu')`. The type annotation lists both, but `graphistry/hyper_dask.py` has no dispatch and the call fails at runtime (`AttributeError: 'ValueError' object has no attribute 'copy'`). Filed upstream as [pygraphistry#1775](https://github.com/graphistry/pygraphistry/issues/1775).

---

## [0.4.2 - 2026-03-30]

### Changed
- **Skills / pygraphistry-gfql**: Restored nested let example now that pygraphistry#968 is fixed in v0.53.7. Added scope rules documentation (inner bindings don't leak to outer, inner can read outer via lexical closure, siblings may reuse names).

---

## [0.4.1 - 2026-03-22]

### Added
- **Docs / RELEASE.md**: Maintainer release guide with standard workflow (release branch, changelog cut, PR merge, tag, GitHub release).
- **Skills / internal/release**: Internal release skill pointing to RELEASE.md and validator commands.
- **CI / validate_release.py**: Automated release flow validator with `--pre`, `--post`, and `--pr` modes. Checks: clean tree, up-to-date branch, changelog state, skills validation, eval JSON validity, common mistakes.

### Changed
- **Skills / pygraphistry-gfql**: Fixed broken nested let example (replaced with working flat sequential refs, filed pygraphistry#968). Consolidated duplicate deprecation messaging. Clarified Cypher label-to-column guidance (recommend property filter first).
- **Skills / pygraphistry-core**: Standardized auth to `os.environ.get()` (was `os.environ[]`).
- **Evals**: Added `python_ast_parse` checks to 15 code-producing cases across skill_pressure, e2e_big_journeys, moltbook. Fixed `groupby` regex variant in row_pipeline.

### Tests
- **Full sweep (claude, all 63 cases, skills ON vs OFF)**:
  - `skills=on`: **71% pass (45/63)**, avg 23.4s
  - `skills=off`: **19% pass (12/63)**, avg 46.6s
  - **Delta: +52pp (3.7x), 2x faster, 0 regressions**

---

## [0.4.0 - 2026-03-22]

### Added
- **Skills / pygraphistry-gfql**: Major expansion — added Cypher string support (MATCH/WHERE/RETURN/ORDER BY/LIMIT, parameterized queries, type alternation, variable-length paths), GRAPH {} constructor with multi-stage USE pipelines, Let/DAG bindings (let/ref/output/nested), edge direction variants (e_forward/e_reverse/e_undirected/e), and remote mode for Cypher + Let queries.
- **Evals / GFQL journeys**: Added 5 new eval suites with 33 total cases:
  - `pygraphistry_gfql_cypher_v1` (9 cases): Cypher basics, advanced patterns, GRAPH constructor, remote execution.
  - `pygraphistry_gfql_let_dag_v1` (5 cases): Let/DAG bindings, ref chains, output selection, nested lets, ASTCall integration.
  - `pygraphistry_gfql_backward_fixes_v1` (6 cases): guardrails for deprecated chain(), correct imports, no hallucinated methods, Cypher acknowledgment, edge directions, remote Cypher.
  - `pygraphistry_gfql_row_pipeline_v1` (6 cases): GROUP BY/aggregation, ORDER BY/LIMIT, UNWIND, ASTCall degree/layout, mixed chain+Cypher paradigm.
  - `pygraphistry_gfql_functional_v1` (7 cases): Functional execution evals — generated code must be self-contained, executable, and produce correct results. Multi-level grading: regex, AST parse, execution, result correctness.
- **Evals / Functional checker**: Added `scripts/evals/gfql_functional_check.py` — post-eval script that extracts code from eval responses, executes with pygraphistry, and validates output correctness.
- **Skills / cross-repo consistency**: Updated pygraphistry router, graphistry umbrella router, and pygraphistry-core to reflect Cypher/Let/DAG routing and chain()/hop() deprecation.

### Changed
- **Skills / pygraphistry-gfql**: Marked `chain()` and `hop()` as deprecated — skill now directs agents to use `gfql()` exclusively. Updated description to reflect Cypher + Let/DAG coverage. Added Cypher label-to-column mapping guidance. Added new canonical doc URLs for Cypher syntax guide and Cypher-GFQL mapping.
- **Skills / pygraphistry (router)**: Updated routing to mention Cypher/Let/DAG/GRAPH explicitly; removed deprecated hop/chain terminology.
- **Skills / pygraphistry-core**: Replaced chain()/hop() shorthand guidance with deprecation notice.
- **Skills / graphistry (umbrella)**: Added Cypher/Let/DAG mention to Python SDK routing line.

### Tests
- **Evals / GFQL full suite (claude, skills=on, 33 cases)**:
  - `skills=on`: **82% pass (27/33)**, avg score 0.95
  - No regressions on existing suites (skill_pressure + guardrails + e2e: 15/23 with GFQL cases all passing)
- **Evals / GFQL functional execution (separate checker, skills=on, 7 cases)**:
  - 4/7 cases produce correct executable GFQL code (chain-list, GRAPH constructor pass)
  - Cypher label-to-column mapping bug caught by functional testing (fixed in skill)
  - Functional testing validates code actually runs, not just pattern-matches

---

## [0.3.0 - 2026-03-08]

### Added
- **Skills / graphistry-rest-api**: Added explicit admin healthcheck coverage (`/healthcheck/`, `/ht/`, `healthz`, service health routes), REST vs Python/GFQL boundary guidance, and advanced iframe URL API patterns (`showCollections`, collections global colors).
- **Skills / REST references**: Added validated REST docs reference pack under `.agents/skills/graphistry-rest-api/references/` with:
  - `hub-rest-docs-toc.md` (curated TOC),
  - `hub-rest-docs-links.tsv` (machine-checkable URL inventory with status/timestamp),
  - `README.md` (refresh/validation policy).
- **Evals / REST journeys**: Added deterministic REST cases for advanced iframe+collections URL API, admin healthchecks, and REST-vs-GFQL/Python boundaries.
- **Benchmarks**: Added new benchmark pack `2026-03-07-rest-gapfix-final-sweep` with public-safe metrics + report.
- **Benchmarks**: Added new benchmark pack `2026-03-07-rest-phase2-full-sweep` with public-safe metrics + report.

### Fixed
- **Evals / docs fallback policy**: Replaced local Nexus path dependency with user-facing canonical Hub docs fallback checks.
- **Evals / boundary checks**: Fixed contradictory GFQL boundary assertions in deterministic checks and improved regex robustness for do-not phrasing.
- **Skills / response control**: Tightened deterministic adapters for sessions short-form and file lifecycle endpoint-sequence outputs.
- **Harness / secret handling**: Redacted JWT/token/password-like values from Codex harness raw output before downstream parsing to reduce credential leakage in run artifacts.

### Changed
- **README / benchmarks docs**: Updated published REST benchmark claims and links to include the new gapfix final sweep.
- **README / benchmarks docs**: Updated published REST benchmark claims and links to include the REST phase2 full sweep.
- **Skills / REST guidance**: Kept named-endpoint guidance user-facing (`/functions/...` for definition lifecycle, `/run/...` for execution), removed internal backend distinctions, and added explicit deployment caveat wording for `/api/v2/share/link/`.
- **Harness / Codex isolation**: Added configurable Codex execution flags (`AGENT_CODEX_SANDBOX_MODE`, `AGENT_CODEX_EPHEMERAL_MODE`) and moved per-run `CODEX_HOME` clones into a dedicated cache-root instance path.
- **Harness / cleanup and permissions**: Tightened copied auth/config file permissions to `0600` and added best-effort cleanup of temporary `CODEX_HOME` clones after eval completion.

### Tests
- **Evals / full REST rerun after reference updates (codex)**: `pygraphistry_rest_eval_ports_v1` + `pygraphistry_rest_first_principles_v1` with `skills=both` (66 rows).
  - Skills ON: 78.8% pass (26/33), 14.4s avg latency
  - Skills OFF: 24.2% pass (8/33), 17.9s avg latency
  - Delta: +54.6pp pass-rate improvement and lower latency with skills
  - Harness OK: 65/66
- **Evals / full REST phase2 sweep (codex)**: `pygraphistry_rest_eval_ports_v1` + `pygraphistry_rest_first_principles_v1` with `skills=both` (66 rows).
  - Skills ON: 90.9% pass (30/33), 13.0s avg latency
  - Skills OFF: 27.3% pass (9/33), 17.0s avg latency
  - Delta: +63.6pp pass-rate improvement and lower latency with skills
- **Evals / full REST sweep (codex)**: `pygraphistry_rest_eval_ports_v1` + `pygraphistry_rest_first_principles_v1` with `skills=both` (52 rows).
  - Skills ON: 92.3% pass (24/26), 13.1s avg latency
  - Skills OFF: 30.8% pass (8/26), 18.9s avg latency
  - Delta: +61.5pp pass-rate improvement and lower latency with skills
- **Evals / targeted regressions**: Follow-up targeted reruns validated fixes for remaining `skills=on` misses in sessions, REST/Python-GFQL boundary wording, and nodes/edges format endpoint patterns.

---

## [0.2.0 - 2026-03-01]

### Fixed
- **Evals / baseline isolation**: Skills=off baseline runs now execute from isolated `/tmp` directory to prevent filesystem-based skill access. Prior evals had contaminated baselines where codex could browse to skill files.
- **Evals / trace_checks**: Relaxed `heavy_clone_allowed_*` trace checks to accept either `git clone` OR reading from existing local pygraphistry repo.

### Changed
- **README**: Updated benchmark numbers with fresh eval sweep showing +30pp skill improvement (98% vs 68% pass rate).

### Tests
- **Evals / fresh sweep**: Ran 112 eval rows across 11 journeys with proper baseline isolation.
  - Skills ON: 91% pass (51/56), 47.4s avg latency
  - Skills OFF: 52% pass (29/56), 46.4s avg latency
  - Delta: +39pp pass rate improvement

---

## [0.1.0 - 2026-02-28]

### Added
- **Skills / pygraphistry-core**: Core PyGraphistry skill covering registration, edges/nodes binding, plot methods.
- **Skills / pygraphistry-visualization**: Visualization skill for encodings, url_params, layout settings.
- **Skills / pygraphistry-gfql**: GFQL skill covering chain patterns, predicates, remote execution.
- **Skills / pygraphistry-connectors**: Connectors skill for Neo4j, Neptune, Splunk, etc.
- **Skills / pygraphistry**: Umbrella skill aggregating all PyGraphistry capabilities.
- **Evals / journeys**: 11 eval journeys covering skill pressure, persona scenarios, guardrails, policy behavior, and smoke tests.
- **Evals / harness**: Multi-harness eval runner supporting codex, claude, and louie with deterministic + oracle grading.
- **Docs / RTD fallback**: RTD-first doc lookup with GitHub clone fallback policy for skills.

### Infra
- **CI**: GitHub Actions workflow for skill validation and eval runs.
- **Scripts**: `agent_eval_loop.py` for eval orchestration, `make_report.py` for benchmark reports.
