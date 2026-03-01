#!/usr/bin/env python3
"""
Generate README-ready benchmark snippets from rows.jsonl files.

Usage:
    python3 scripts/benchmarks/readme_snippet.py --rows /tmp/*/rows.jsonl

Outputs markdown snippet suitable for pasting into README.md Evals section.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_rows(paths: list[str]) -> list[dict]:
    """Load all rows from jsonl files."""
    import glob as glob_module
    rows = []
    for pattern in paths:
        matched = glob_module.glob(pattern) if "*" in pattern else [pattern]
        for path_str in matched:
            path = Path(path_str)
            if path.exists():
                with open(path) as f:
                    for line in f:
                        if line.strip():
                            rows.append(json.loads(line))
    return rows


def compute_metrics(rows: list[dict]) -> dict:
    """Compute pass rates by harness and skills mode."""
    # Group by harness -> mode
    data = defaultdict(lambda: defaultdict(lambda: {"pass": 0, "total": 0, "latencies": []}))

    for row in rows:
        harness = row.get("harness", "unknown")
        mode = row.get("skills_mode", "unknown")
        passed = row.get("pass_bool", False)
        latency = row.get("latency_ms", 0) / 1000

        data[harness][mode]["total"] += 1
        if passed:
            data[harness][mode]["pass"] += 1
        data[harness][mode]["latencies"].append(latency)

    return data


def format_readme_snippet(data: dict, title: str = None) -> str:
    """Format metrics as README markdown snippet."""
    lines = []

    if title:
        lines.append(f"- {title}:")

    for harness in sorted(data.keys()):
        modes = data[harness]
        on = modes.get("on", {"pass": 0, "total": 0, "latencies": []})
        off = modes.get("off", {"pass": 0, "total": 0, "latencies": []})

        on_rate = 100 * on["pass"] / on["total"] if on["total"] else 0
        off_rate = 100 * off["pass"] / off["total"] if off["total"] else 0
        on_lat = sum(on["latencies"]) / len(on["latencies"]) if on["latencies"] else 0
        off_lat = sum(off["latencies"]) / len(off["latencies"]) if off["latencies"] else 0
        delta = on_rate - off_rate

        harness_label = harness.capitalize()
        cases = on["total"]  # Assumes same number of cases for on/off

        lines.append(f"  - {harness_label} (`skills=both`, {cases} cases × 2):")
        lines.append(f"    - `skills=on`: **{on_rate:.0f}% pass ({on['pass']}/{on['total']})**, avg `{on_lat:.1f}s`")
        lines.append(f"    - `skills=off`: **{off_rate:.0f}% pass ({off['pass']}/{off['total']})**, avg `{off_lat:.1f}s`")
        lines.append(f"    - **Delta: +{delta:.0f}pp pass rate improvement**")

    return "\n".join(lines)


def format_table(data: dict) -> str:
    """Format metrics as markdown table."""
    lines = [
        "| Harness | Skills ON | Skills OFF | Delta |",
        "|---------|-----------|------------|-------|",
    ]

    for harness in sorted(data.keys()):
        modes = data[harness]
        on = modes.get("on", {"pass": 0, "total": 0})
        off = modes.get("off", {"pass": 0, "total": 0})

        on_rate = 100 * on["pass"] / on["total"] if on["total"] else 0
        off_rate = 100 * off["pass"] / off["total"] if off["total"] else 0
        delta = on_rate - off_rate

        lines.append(
            f"| {harness} | {on['pass']}/{on['total']} ({on_rate:.0f}%) | "
            f"{off['pass']}/{off['total']} ({off_rate:.0f}%) | +{delta:.0f}pp |"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate README benchmark snippets")
    parser.add_argument("--rows", action="append", required=True, help="Path to rows.jsonl (supports globs)")
    parser.add_argument("--title", default=None, help="Optional title for the snippet")
    parser.add_argument("--format", choices=["snippet", "table"], default="snippet", help="Output format")
    args = parser.parse_args()

    rows = load_rows(args.rows)
    if not rows:
        print("No rows found", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(rows)} rows", file=sys.stderr)

    data = compute_metrics(rows)

    if args.format == "table":
        print(format_table(data))
    else:
        print(format_readme_snippet(data, args.title))


if __name__ == "__main__":
    main()
