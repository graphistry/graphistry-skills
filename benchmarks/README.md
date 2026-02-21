# Benchmarks

Checked-in benchmark artifacts for skills/eval regression tracking.

## Latest Clean Rerun Pack
- Data: `data/2026-02-20-clean-rerun`
- Report: `reports/2026-02-20-clean-rerun.md`

## Data Contents
- `runs/*/manifest.json`: run config + harness settings
- `runs/*/summary.json`: pre-aggregated pass/latency metrics
- `runs/*/rows.jsonl`: per-case records
- `combined_metrics.json`: normalized aggregates across runs
- `combined_rows.csv`: flattened table for quick slicing/charting

## Notes
- `runs/contaminated/*` preserves pre-fix measurements for auditability.
- `runs/clean/*` uses Codex baseline isolation (`CODEX_HOME` + native cwd).
