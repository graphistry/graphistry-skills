# Changelog

All notable changes to graphistry-skills are documented in this file.

The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Development]
<!-- Do Not Erase This Section - Used for tracking unreleased changes -->

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
