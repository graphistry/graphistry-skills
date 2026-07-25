# Benchmarks

Checked-in benchmark artifacts for skills/eval regression tracking.

## Latest Checked-in Packs
- GFQL Polars engine pack (2026-07-25, Claude, released `graphistry==0.58.0`):
  - Data: `data/2026-07-25-gfql-polars-engines`
  - Report: `reports/2026-07-25-gfql-polars-engines.md`
  - Skills ON: 100% pass (7/7), avg score 1.00, avg 83.4s; Skills OFF: 71.4% pass (5/7), avg score 0.92, avg 132.3s — **+28.6pp delta, 0 regressions**
  - Claude only — the `codex` half was blocked by exhausted usage credits and is not represented
  - Environment-sensitive: run against a released `graphistry>=0.58` install. A stale install collapses both arms; a source checkout on `PYTHONPATH` sends both to 100%. See the report's methodology section.
- GFQL expansion eval (2026-03-21, Claude):
  - Data: `data/2026-03-21-gfql-expansion`
  - Report: `reports/2026-03-21-gfql-expansion.md`
  - Skills ON: 82% pass (27/33), avg score 0.95
  - Includes functional execution testing (4/7 cases produce correct executable code)
- REST phase2 full sweep (2026-03-07):
  - Data: `data/2026-03-07-rest-phase2-full-sweep`
  - Report: `reports/2026-03-07-rest-phase2-full-sweep.md`
  - Skills ON: 90.9% pass (30/33), Skills OFF: 27.3% pass (9/33), **+63.6pp delta**
- REST gapfix final sweep (2026-03-07):
  - Data: `data/2026-03-07-rest-gapfix-final-sweep`
  - Report: `reports/2026-03-07-rest-gapfix-final-sweep.md`
  - Skills ON: 92.3% pass (24/26), Skills OFF: 30.8% pass (8/26), **+61.5pp delta**
- REST skills optimization sweep (2026-03-07):
  - Data: `data/2026-03-07-rest-skills-optimization-sweep`
  - Report: `reports/2026-03-07-rest-skills-optimization-sweep.md`
  - Skills ON: 95% pass (19/20), Skills OFF: 35% pass (7/20), **+60pp delta**
- Baseline isolation sweep (2026-03-01):
  - Data: `data/2026-03-01-baseline-isolation-sweep`
  - Report: `reports/2026-03-01-baseline-isolation-sweep.md`
  - Skills ON: 91% pass (51/56), Skills OFF: 52% pass (29/56), **+39pp delta**
- Post-cleanup full sweep (2026-02-23, had baseline contamination):
  - Data: `data/2026-02-23-postcleanup-fullsweep`
  - Report: `reports/2026-02-23-postcleanup-fullsweep.md`
- Codex effort A/B (`gpt-5.3-codex`, high vs medium):
  - Data: `data/2026-02-23-codex-effort-ab`
  - Report: `reports/2026-02-23-codex-effort-ab.md`

## Data Contents
- `data/*/combined_metrics.json`: normalized aggregate metrics (public-safe; source paths redacted)
- `reports/*.md`: rendered scorecards derived from benchmark runs (public-safe)
- `data/*scenario-coverage*.json`: scenario metadata coverage audits

## Notes
- Keep only benchmark packs tied to current docs claims and release decisions.
- Avoid checking in experiment packs that do not materially improve quality/speed claims.
- Keep raw run artifacts local/private (`rows.jsonl`, `manifest.json`, `otel_ids.json`, run logs, and traces).
