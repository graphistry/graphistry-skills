---
name: benchmarks
description: Internal maintainer skill for running, validating, and publishing eval benchmarks for this repository.
metadata:
  internal: true
---

# Benchmarks Skill (Internal Maintainer)

Use this for repository maintenance workflows. It is not a user-facing Graphistry domain skill.

## Use This Skill For
- Running eval sweeps across journeys (skill pressure, persona, guardrails, etc.)
- Validating baseline isolation (skills=off must not read skill files)
- Generating public-safe benchmark reports
- Updating README.md with fresh benchmark numbers
- Creating CHANGELOG.md entries for benchmark releases
- Git version tagging (semver vX.Y.Z)

## Success Criteria (Do Not Skip)
- Sweeps complete without baseline contamination (verify via log inspection)
- `pass_bool` is used for pass rate calculation (not `score >= 0.8`)
- Reports are public-safe (source paths redacted)
- README.md and benchmarks/README.md are updated with new numbers
- CHANGELOG.md has entry for the sweep
- Git tag created after merge

## Key Metrics
- **pass_bool**: Official pass/fail metric (deterministic checks)
- **Delta**: `skills=on` pass rate minus `skills=off` pass rate (in percentage points)
- **Latency**: Average response time in seconds

## Preconditions
- CLIs on PATH: `codex`, `claude`, `jq`
- Auth configured: `~/.codex`, `~/.claude`
- Working from repo root: `graphistry-skills/`

## Workflow

### 1) Run Eval Sweep
```bash
OUT="/tmp/graphistry_skills_sweep_$(date +%Y%m%d-%H%M%S)"
./bin/agent.sh \
  --codex --claude \
  --journeys all \
  --skills-mode both \
  --skills-delivery native \
  --max-workers 2 \
  --out "$OUT"
```

### 2) Verify Baseline Isolation
Check skills=off logs for no skill file reads:
```bash
grep -l "SKILL.md" "$OUT"/raw/*skills_off* 2>/dev/null && echo "CONTAMINATION DETECTED" || echo "Clean"
```

### 3) Generate Public-Safe Report
```bash
python3 scripts/benchmarks/make_report.py \
  --public-safe \
  --rows "$OUT/rows.jsonl" \
  --title "Eval Sweep $(date +%Y-%m-%d)" \
  --out-md benchmarks/reports/$(date +%Y-%m-%d)-sweep.md \
  --out-json benchmarks/data/$(date +%Y-%m-%d)-sweep/combined_metrics.json
```

### 4) Generate README Snippet
```bash
python3 scripts/benchmarks/readme_snippet.py \
  --rows "$OUT/rows.jsonl" \
  --title "Fresh eval sweep"
```

### 5) Update Files
- Update `README.md` Evals section with generated snippet
- Update `benchmarks/README.md` with new pack reference
- Add entry to `CHANGELOG.md` under `[Development]` section

### 6) Create PR and Tag
After PR merge:
```bash
git fetch origin main && git checkout main && git pull
git tag -a vX.Y.Z -m "Release vX.Y.Z: <summary>"
git push origin vX.Y.Z
```

## Versioning Convention
- **Semver**: vX.Y.Z (following Supabase MCP, Databricks AI Dev Kit patterns)
- **Patch (Z)**: Bug fixes, minor eval improvements
- **Minor (Y)**: New journeys, new skills, notable benchmark changes
- **Major (X)**: Breaking changes to eval harness or skill format

## File Locations
- **Journeys**: `evals/journeys/*.json`
- **Scripts**: `scripts/benchmarks/make_report.py`, `scripts/benchmarks/readme_snippet.py`
- **Reports**: `benchmarks/reports/*.md`
- **Data**: `benchmarks/data/*/combined_metrics.json`
- **Raw artifacts** (private): `rows.jsonl`, `manifest.json`, traces, logs

## Guardrails
- Do not check in raw `rows.jsonl` (contains full prompt/response text)
- Do not check in `manifest.json`, `otel_ids.json`, or raw logs
- Always use `--public-safe` flag for checked-in reports
- Use `pass_bool` for official metrics, not score thresholds
- Verify baseline isolation before publishing results

## Related Skills
- `eval-otel`: OTel trace validation and inspection
- `plan`: Multi-session task planning (for complex benchmark campaigns)
