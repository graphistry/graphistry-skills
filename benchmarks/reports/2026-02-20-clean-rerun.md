# Benchmark Report: Clean Rerun After Codex Baseline Isolation

Date: 2026-02-20

## Scope
Compared previously contaminated benchmark runs against clean reruns where Codex baseline (`skills=off`) is isolated from both:
- repo-local auto-discovered skills
- global user skills in `~/.codex/skills`

Isolation is implemented in `scripts/agent_eval_loop.py` by setting per-mode native cwd and per-mode `CODEX_HOME`.

## Source Artifacts
- Data root: `benchmarks/data/2026-02-20-clean-rerun`
- Contaminated runs:
  - `runs/contaminated/persona_refresh_20260220-174344`
  - `runs/contaminated/model_matrix_focus_20260220-185129`
- Clean runs:
  - `runs/clean/persona_refresh_clean_20260220-192535`
  - `runs/clean/model_matrix_focus_clean_20260220-193826`
- Aggregates:
  - `combined_metrics.json`
  - `combined_rows.csv`

## Combined Results (52 rows total)

### Contaminated (before)
- Claude off: `10/13` (`76.9%`), avg latency `16.4s`
- Claude on: `9/13` (`69.2%`), avg latency `25.6s`
- Codex off: `13/13` (`100%`), avg latency `36.0s`
- Codex on: `12/13` (`92.3%`), avg latency `36.6s`

### Clean (after fix)
- Claude off: `11/13` (`84.6%`), avg latency `25.5s`
- Claude on: `10/13` (`76.9%`), avg latency `23.4s`
- Codex off: `10/13` (`76.9%`), avg latency `65.8s`
- Codex on: `13/13` (`100%`), avg latency `41.8s`

### Delta (clean - contaminated)
- Claude off: `+7.7pp`
- Claude on: `+7.7pp`
- Codex off: `-23.1pp` (baseline was inflated before fix)
- Codex on: `+7.7pp`

## Sonnet vs Opus (clean model-matrix run)
From `runs/clean/model_matrix_focus_clean_20260220-193826/summary.json`:
- Sonnet: `4/6` (`66.7%`), avg latency `13.1s`
- Opus: `6/6` (`100%`), avg latency `25.5s`

By skills mode:
- Sonnet off: `2/3`; on: `2/3`
- Opus off: `3/3`; on: `3/3`

## Takeaways
- The contamination fix materially changed Codex baseline estimates.
- With clean isolation, Codex shows clear value from skills in this benchmark slice (`off 76.9%` vs `on 100%`).
- Opus remains more reliable than Sonnet on strict rubric-style checks, at higher latency.
