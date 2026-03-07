# Benchmarks

Checked-in benchmark artifacts for skills/eval regression tracking.

## Latest Checked-in Packs
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
