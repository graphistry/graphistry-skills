# Benchmarks

Checked-in benchmark artifacts for skills/eval regression tracking.

## Latest Checked-in Packs
- Post-cleanup full sweep:
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
