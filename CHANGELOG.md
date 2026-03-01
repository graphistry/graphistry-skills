# Changelog

All notable changes to graphistry-skills are documented in this file.

The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Development]
<!-- Do Not Erase This Section - Used for tracking unreleased changes -->

### Added

### Fixed

### Changed

### Tests

---

## [0.2.0 - 2026-03-01]

### Fixed
- **Evals / baseline isolation**: Skills=off baseline runs now execute from isolated `/tmp` directory to prevent filesystem-based skill access. Prior evals had contaminated baselines where codex could browse to skill files.
- **Evals / trace_checks**: Relaxed `heavy_clone_allowed_*` trace checks to accept either `git clone` OR reading from existing local pygraphistry repo.

### Changed
- **README**: Updated benchmark numbers with fresh eval sweep showing +30pp skill improvement (98% vs 68% pass rate).

### Tests
- **Evals / fresh sweep**: Ran 112 eval rows across 11 journeys with proper baseline isolation.
  - Skills ON: 98.2% pass (55/56), 47.4s avg latency
  - Skills OFF: 67.9% pass (38/56), 46.4s avg latency
  - Delta: +30.4pp pass rate improvement

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
