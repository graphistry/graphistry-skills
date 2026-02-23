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
- `runs/*/manifest.json`: run config + harness settings
- `runs/*/summary.json`: pre-aggregated pass/latency metrics
- `runs/*/rows.jsonl`: per-case records
- `combined_metrics.json`: normalized aggregates across runs
- `combined_rows.jsonl`: flattened per-row records for quick slicing/charting

## Notes
- Keep only benchmark packs tied to current docs claims and release decisions.
- Avoid checking in experiment packs that do not materially improve quality/speed claims.
