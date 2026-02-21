#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build markdown benchmark report from rows.jsonl files")
    parser.add_argument(
        "--rows",
        action="append",
        required=True,
        help="Path to rows.jsonl (repeat flag for multiple files)",
    )
    parser.add_argument("--title", default="Benchmark Report", help="Markdown title")
    parser.add_argument("--out-md", required=True, help="Output markdown path")
    parser.add_argument("--out-json", default="", help="Optional output JSON metrics path")
    return parser.parse_args()


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except Exception:
            return None
    return None


def read_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Missing rows file: {path}")
        with path.open("r", encoding="utf-8") as f:
            for lineno, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception as exc:
                    raise ValueError(f"Invalid JSON at {path}:{lineno}: {exc}") from exc
                if not isinstance(row, dict):
                    continue
                row["_source"] = str(path)
                row["_lineno"] = lineno
                rows.append(row)
    return rows


def skills_mode(row: dict[str, Any]) -> str:
    explicit = str(row.get("skills_mode", "")).strip().lower()
    if explicit in {"on", "off"}:
        return explicit
    return "on" if parse_bool(row.get("skills_enabled")) else "off"


def model_name(row: dict[str, Any]) -> str:
    model = str(row.get("model", "")).strip()
    return model or "default"


def eval_intent_name(row: dict[str, Any]) -> str:
    intent = str(row.get("eval_intent", "")).strip()
    return intent or "unspecified"


def mean_or_zero(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def group_metrics(rows: list[dict[str, Any]], group_keys: list[str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in rows:
        key_vals: list[str] = []
        for key in group_keys:
            if key == "skills_mode":
                key_vals.append(skills_mode(row))
            elif key == "model":
                key_vals.append(model_name(row))
            elif key == "eval_intent":
                key_vals.append(eval_intent_name(row))
            else:
                key_vals.append(str(row.get(key, "")).strip() or "unknown")
        key = tuple(key_vals)
        grouped.setdefault(key, []).append(row)

    out: list[dict[str, Any]] = []
    for key, members in sorted(grouped.items()):
        latencies = [v for v in (parse_float(r.get("latency_ms")) for r in members) if v is not None]
        scores = [v for v in (parse_float(r.get("score")) for r in members) if v is not None]
        total = len(members)
        passed = sum(1 for r in members if parse_bool(r.get("pass_bool")))
        harness_ok = sum(1 for r in members if parse_bool(r.get("harness_ok", True)))
        row_out: dict[str, Any] = {
            "total": total,
            "passed": passed,
            "pass_rate": (passed / total) if total else 0.0,
            "harness_ok": harness_ok,
            "harness_ok_rate": (harness_ok / total) if total else 0.0,
            "avg_latency_ms": mean_or_zero(latencies),
            "avg_score": mean_or_zero(scores),
        }
        for idx, k in enumerate(group_keys):
            row_out[k] = key[idx]
        out.append(row_out)
    return out


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows_"
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        vals = []
        for col in columns:
            v = row.get(col, "")
            if isinstance(v, float):
                if col.endswith("rate"):
                    vals.append(f"{v * 100:.1f}%")
                elif col.endswith("_ms"):
                    vals.append(f"{v:.1f}")
                else:
                    vals.append(f"{v:.4f}")
            else:
                vals.append(str(v))
        body.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep] + body)


def build_metrics(rows: list[dict[str, Any]], sources: list[str]) -> dict[str, Any]:
    total = len(rows)
    passed = sum(1 for r in rows if parse_bool(r.get("pass_bool")))
    harness_mode = group_metrics(rows, ["harness", "skills_mode"])
    harness_model_mode = group_metrics(rows, ["harness", "model", "skills_mode"])
    eval_intent_mode = group_metrics(rows, ["eval_intent", "harness", "skills_mode"])
    by_eval_intent = group_metrics(rows, ["eval_intent"])

    kpi_intents = {"realistic_capability", "execution_grade"}
    kpi_rows = [r for r in rows if eval_intent_name(r) in kpi_intents]
    kpi_total = len(kpi_rows)
    kpi_passed = sum(1 for r in kpi_rows if parse_bool(r.get("pass_bool")))
    kpi_harness_mode = group_metrics(kpi_rows, ["harness", "skills_mode"])

    failures: list[dict[str, Any]] = []
    for r in rows:
        if parse_bool(r.get("pass_bool")):
            continue
        failures.append(
            {
                "harness": str(r.get("harness", "unknown")),
                "model": model_name(r),
                "skills_mode": skills_mode(r),
                "eval_intent": eval_intent_name(r),
                "journey_id": str(r.get("journey_id", "")),
                "case_id": str(r.get("case_id", "")),
                "score": parse_float(r.get("score")) or 0.0,
                "latency_ms": parse_float(r.get("latency_ms")) or 0.0,
                "source": str(r.get("_source", "")),
            }
        )

    failures.sort(
        key=lambda f: (
            f["harness"],
            f["model"],
            f["skills_mode"],
            f["eval_intent"],
            f["journey_id"],
            f["case_id"],
        )
    )

    return {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "inputs": sources,
        "overall": {
            "total": total,
            "passed": passed,
            "pass_rate": (passed / total) if total else 0.0,
        },
        "by_harness_and_mode": harness_mode,
        "by_harness_model_and_mode": harness_model_mode,
        "by_eval_intent": by_eval_intent,
        "by_eval_intent_harness_and_mode": eval_intent_mode,
        "kpi": {
            "intents": sorted(kpi_intents),
            "total": kpi_total,
            "passed": kpi_passed,
            "pass_rate": (kpi_passed / kpi_total) if kpi_total else 0.0,
            "by_harness_and_mode": kpi_harness_mode,
        },
        "failures": failures,
    }


def build_markdown(title: str, metrics: dict[str, Any]) -> str:
    overall = metrics["overall"]
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"- Generated: `{metrics['generated_at']}`")
    lines.append("- Inputs:")
    for src in metrics["inputs"]:
        lines.append(f"  - `{src}`")
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append(
        f"- Pass: `{overall['passed']}/{overall['total']}` ({overall['pass_rate'] * 100:.1f}%)"
    )
    lines.append(
        f"- KPI intents (`{','.join(metrics['kpi']['intents'])}`): "
        f"`{metrics['kpi']['passed']}/{metrics['kpi']['total']}` "
        f"({metrics['kpi']['pass_rate'] * 100:.1f}%)"
    )
    lines.append("")
    lines.append("## By Eval Intent")
    lines.append("")
    lines.append(
        markdown_table(
            metrics["by_eval_intent"],
            [
                "eval_intent",
                "passed",
                "total",
                "pass_rate",
                "avg_latency_ms",
                "avg_score",
            ],
        )
    )
    lines.append("")
    lines.append("## KPI Intents: By Harness + Skills Mode")
    lines.append("")
    lines.append(
        markdown_table(
            metrics["kpi"]["by_harness_and_mode"],
            [
                "harness",
                "skills_mode",
                "passed",
                "total",
                "pass_rate",
                "avg_latency_ms",
                "avg_score",
            ],
        )
    )
    lines.append("")
    lines.append("## By Harness + Skills Mode")
    lines.append("")
    lines.append(
        markdown_table(
            metrics["by_harness_and_mode"],
            [
                "harness",
                "skills_mode",
                "passed",
                "total",
                "pass_rate",
                "avg_latency_ms",
                "avg_score",
            ],
        )
    )
    lines.append("")
    lines.append("## By Harness + Model + Skills Mode")
    lines.append("")
    lines.append(
        markdown_table(
            metrics["by_harness_model_and_mode"],
            [
                "harness",
                "model",
                "skills_mode",
                "passed",
                "total",
                "pass_rate",
                "avg_latency_ms",
                "avg_score",
            ],
        )
    )
    lines.append("")
    lines.append("## Failures")
    lines.append("")
    if not metrics["failures"]:
        lines.append("_None_")
    else:
        lines.append(
            markdown_table(
                metrics["failures"],
                [
                    "harness",
                    "model",
                    "skills_mode",
                    "eval_intent",
                    "journey_id",
                    "case_id",
                    "score",
                    "latency_ms",
                    "source",
                ],
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    rows_paths = [Path(p).resolve() for p in args.rows]
    rows = read_rows(rows_paths)
    metrics = build_metrics(rows, [str(p) for p in rows_paths])
    report_md = build_markdown(args.title, metrics)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(report_md, encoding="utf-8")

    if args.out_json:
        out_json = Path(args.out_json)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Wrote markdown report: {out_md}")
    if args.out_json:
        print(f"Wrote JSON metrics: {Path(args.out_json)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
