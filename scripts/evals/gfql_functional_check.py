#!/usr/bin/env python3
"""
Post-eval functional checker for GFQL eval cases.

Extracts Python code blocks from eval responses, executes them in an
isolated namespace with pygraphistry available, and validates:
  - No exceptions during execution
  - Expected output strings present in stdout
  - Result objects have expected properties (non-empty nodes, etc.)

Usage:
    python3 scripts/evals/gfql_functional_check.py --rows /tmp/run/rows.jsonl
    python3 scripts/evals/gfql_functional_check.py --rows /tmp/run/rows.jsonl --pygraphistry-path ~/Work/pygraphistry

Outputs a JSON summary to stdout and per-case details to stderr.
"""
import argparse
import io
import json
import re
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path


def extract_code_blocks(text: str) -> list[str]:
    """Extract Python code blocks from markdown-formatted text."""
    blocks = re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if not blocks:
        blocks = re.findall(r"```\s*\n(.*?)```", text, re.DOTALL)
    return blocks


def execute_code(code: str) -> dict:
    """Execute a Python code string and capture output + exceptions."""
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    result = {
        "executed": False,
        "exception": None,
        "exception_type": None,
        "stdout": "",
        "stderr": "",
        "traceback": None,
    }

    # Build isolated namespace with common imports available
    namespace = {"__builtins__": __builtins__}

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, namespace)
        result["executed"] = True
    except Exception as exc:
        result["exception"] = str(exc)
        result["exception_type"] = type(exc).__name__
        result["traceback"] = traceback.format_exc()

    result["stdout"] = stdout_capture.getvalue()
    result["stderr"] = stderr_capture.getvalue()
    return result


def check_functional(exec_result: dict, functional_cfg: dict) -> dict:
    """Validate execution result against functional expectations."""
    checks = {}
    all_pass = True

    if functional_cfg.get("expect_no_exception", False):
        passed = exec_result["executed"] and exec_result["exception"] is None
        checks["no_exception"] = {
            "pass": passed,
            "detail": exec_result["exception"] if not passed else "OK",
        }
        if not passed:
            all_pass = False

    expect_output = functional_cfg.get("expect_output_contains")
    if expect_output:
        stdout = exec_result["stdout"]
        passed = expect_output in stdout
        checks["output_contains"] = {
            "pass": passed,
            "expected": expect_output,
            "actual_stdout_head": stdout[:500],
        }
        if not passed:
            all_pass = False

    if functional_cfg.get("expect_result_nodes_gt") is not None:
        threshold = functional_cfg["expect_result_nodes_gt"]
        # Try to extract RESULT_COUNT from stdout
        match = re.search(r"RESULT_COUNT:\s*(\d+)", exec_result["stdout"])
        if match:
            count = int(match.group(1))
            passed = count > threshold
            checks["result_nodes_gt"] = {
                "pass": passed,
                "expected_gt": threshold,
                "actual": count,
            }
        else:
            passed = False
            checks["result_nodes_gt"] = {
                "pass": False,
                "detail": "Could not extract RESULT_COUNT from stdout",
            }
        if not passed:
            all_pass = False

    return {"pass": all_pass, "checks": checks}


def main():
    parser = argparse.ArgumentParser(description="GFQL functional post-eval checker")
    parser.add_argument("--rows", required=True, help="Path to rows.jsonl from eval run")
    parser.add_argument(
        "--pygraphistry-path",
        default=None,
        help="Path to pygraphistry source (added to sys.path)",
    )
    parser.add_argument(
        "--journey-dir",
        default="evals/journeys",
        help="Journey directory for loading functional configs",
    )
    args = parser.parse_args()

    # Add pygraphistry to path if specified
    if args.pygraphistry_path:
        sys.path.insert(0, str(Path(args.pygraphistry_path).resolve()))

    rows_path = Path(args.rows)
    if not rows_path.exists():
        print(json.dumps({"error": f"rows file not found: {rows_path}"}))
        sys.exit(1)

    # Load journey configs to get functional specs
    journey_dir = Path(args.journey_dir)
    functional_cfgs = {}
    for jf in journey_dir.glob("*.json"):
        try:
            journey = json.loads(jf.read_text())
            for case in journey.get("cases", []):
                fc = case.get("functional")
                if fc and fc.get("enabled"):
                    functional_cfgs[case["id"]] = fc
        except Exception:
            pass

    # Process each row
    results = []
    rows = [json.loads(line) for line in rows_path.read_text().strip().splitlines()]

    for row in rows:
        case_id = row.get("case_id", "")
        response_text = row.get("response_text", "")

        # Skip cases without functional config
        if case_id not in functional_cfgs:
            continue

        fc = functional_cfgs[case_id]

        # Extract code
        blocks = extract_code_blocks(response_text)
        if not blocks:
            results.append({
                "case_id": case_id,
                "functional_pass": False,
                "detail": "No Python code block found in response",
                "checks": {},
            })
            print(f"  SKIP {case_id}: no code block", file=sys.stderr)
            continue

        # Combine all code blocks (some responses have setup + query in separate blocks)
        combined_code = "\n\n".join(blocks)

        # Execute
        print(f"  EXEC {case_id} ({len(combined_code)} chars)...", file=sys.stderr)
        exec_result = execute_code(combined_code)

        # Check functional expectations
        func_result = check_functional(exec_result, fc)

        entry = {
            "case_id": case_id,
            "functional_pass": func_result["pass"],
            "executed": exec_result["executed"],
            "exception": exec_result["exception"],
            "exception_type": exec_result["exception_type"],
            "stdout_head": exec_result["stdout"][:500],
            "checks": func_result["checks"],
        }
        results.append(entry)

        status = "PASS" if func_result["pass"] else "FAIL"
        detail = ""
        if exec_result["exception"]:
            detail = f" ({exec_result['exception_type']}: {exec_result['exception'][:80]})"
        print(f"  {status} {case_id}{detail}", file=sys.stderr)

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["functional_pass"])

    summary = {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total > 0 else 0,
        "cases": results,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
