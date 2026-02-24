#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

err=0

echo "public-benchmarks: checking for disallowed raw benchmark artifacts"

disallowed_patterns=(
  'benchmarks/data/**/rows.jsonl'
  'benchmarks/data/**/combined_rows.jsonl'
  'benchmarks/data/**/combined_rows.csv'
  'benchmarks/data/**/manifest.json'
  'benchmarks/data/**/otel_ids.json'
  'benchmarks/data/**/runs/**'
)

for pattern in "${disallowed_patterns[@]}"; do
  matches="$(git ls-files "$pattern")"
  if [[ -n "$matches" ]]; then
    echo "ERROR: tracked disallowed benchmark artifact(s) for pattern: $pattern"
    echo "$matches"
    err=1
  fi
done

echo "public-benchmarks: checking for disallowed sensitive literals in checked-in benchmark artifacts"
if rg -n -S 'redacted_test_user|redacted_test_pass|/home/USER/|/tmp/graphistry_skills' benchmarks/data benchmarks/reports benchmarks/README.md >/dev/null; then
  rg -n -S 'redacted_test_user|redacted_test_pass|/home/USER/|/tmp/graphistry_skills' benchmarks/data benchmarks/reports benchmarks/README.md || true
  echo "ERROR: sensitive/local literals found in checked-in benchmark artifacts"
  err=1
fi

echo "public-benchmarks: checking sanitized metrics/report shapes"
if rg -n -S '"source"\s*:' benchmarks/data/*/combined_metrics.json >/dev/null; then
  rg -n -S '"source"\s*:' benchmarks/data/*/combined_metrics.json || true
  echo 'ERROR: combined_metrics.json still contains per-failure source paths'
  err=1
fi

if rg -n -S '^\|.*\bsource\b.*\|' benchmarks/reports/*.md >/dev/null; then
  rg -n -S '^\|.*\bsource\b.*\|' benchmarks/reports/*.md || true
  echo 'ERROR: benchmark report markdown still contains source column'
  err=1
fi

if [[ "$err" -ne 0 ]]; then
  echo "public-benchmarks: FAILED"
  exit 1
fi

echo "public-benchmarks: passed"
