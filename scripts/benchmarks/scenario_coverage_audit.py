#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JOURNEY_DIR = ROOT / "evals" / "journeys"


PERSONA_BUCKETS = ["novice", "analyst", "engineer", "admin", "unspecified"]
DOMAIN_BUCKETS = ["fraud", "cybersecurity", "social-media", "platform", "generic"]
TASK_BUCKETS = [
    "runtime_smoke",
    "safety_guardrail",
    "auth",
    "ingest_etl",
    "shaping_viz",
    "gfql_query",
    "ai_ml",
    "connectors",
    "other",
]
INPUT_LEVEL_BUCKETS = ["raw_table", "events_table", "bound_graph", "remote_dataset", "conceptual"]
OUTPUT_DEPTH_BUCKETS = ["one_liner", "snippet", "workflow", "e2e_workflow", "bullets_or_links"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit scenario coverage of eval journeys")
    parser.add_argument("--journey-dir", default=str(DEFAULT_JOURNEY_DIR), help="Journey directory")
    parser.add_argument("--out-md", required=True, help="Output markdown report path")
    parser.add_argument("--out-json", required=True, help="Output json report path")
    return parser.parse_args()


def load_journey(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid journey file: {path}")
    return data


def first_match_bucket(text: str, pairs: list[tuple[str, str]], default: str) -> str:
    for pattern, bucket in pairs:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return bucket
    return default


def normalize_bucket(value: Any, buckets: list[str], default: str) -> str:
    if isinstance(value, str):
        v = value.strip().lower()
        if v in buckets:
            return v
    return default


def infer_persona(prompt: str, journey_id: str) -> str:
    t = f"{journey_id}\n{prompt}"
    return first_match_bucket(
        t,
        [
            (r"\bnovice\b", "novice"),
            (r"\banalyst\b", "analyst"),
            (r"\badmin\b|org|api[_ -]?key|idp", "admin"),
            (r"\bengineer\b|developer|workflow", "engineer"),
        ],
        "unspecified",
    )


def infer_domain(prompt: str, journey_id: str) -> str:
    t = f"{journey_id}\n{prompt}"
    return first_match_bucket(
        t,
        [
            (r"fraud|transaction", "fraud"),
            (r"cyber|security|device|process|domain|ip", "cybersecurity"),
            (r"social|content|claim|astroturf|spam", "social-media"),
            (r"graphistry|org|auth|runtime|connector", "platform"),
        ],
        "generic",
    )


def infer_task(prompt: str, journey_id: str, eval_intent: str) -> str:
    t = f"{journey_id}\n{prompt}\n{eval_intent}"
    return first_match_bucket(
        t,
        [
            (r"runtime_smoke|reply with exactly|echo", "runtime_smoke"),
            (r"guardrail|literal creds|public mode|invented", "safety_guardrail"),
            (r"register\(|personal_key|org_name|idp_name|auth", "auth"),
            (r"read_csv|DataFrame|load|ingest|etl", "ingest_etl"),
            (r"encode_|settings\(|plot\(", "shaping_viz"),
            (r"gfql|where=|e_forward|gfql_remote", "gfql_query"),
            (r"umap|dbscan|featurize|search|embedding", "ai_ml"),
            (r"neo4j|splunk|connector", "connectors"),
        ],
        "other",
    )


def infer_input_level(prompt: str, journey_id: str) -> str:
    t = f"{journey_id}\n{prompt}"
    return first_match_bucket(
        t,
        [
            (r"read_csv|raw CSV|transactions table|DataFrame", "raw_table"),
            (r"events table|row-oriented events", "events_table"),
            (r"existing bound graph|edges\(\)\+nodes\(\)|bound graph", "bound_graph"),
            (r"dataset_id|gfql_remote", "remote_dataset"),
        ],
        "conceptual",
    )


def infer_output_depth(prompt: str, journey_id: str) -> str:
    t = f"{journey_id}\n{prompt}"
    return first_match_bucket(
        t,
        [
            (r"exactly one|one line|one concise line", "one_liner"),
            (r"short snippet|concise snippet|compact code block", "snippet"),
            (r"workflow|pipeline", "workflow"),
            (r"end-to-end|e2e|starts from raw", "e2e_workflow"),
            (r"bullets|links|one URL per line", "bullets_or_links"),
        ],
        "snippet",
    )


def pct(count: int, total: int) -> float:
    return (count / total * 100.0) if total else 0.0


def dim_table(counter: Counter[str], buckets: list[str], total: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for b in buckets:
        c = int(counter.get(b, 0))
        rows.append({"bucket": b, "count": c, "pct": round(pct(c, total), 1)})
    return rows


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    journey_dir = Path(args.journey_dir)
    files = sorted(journey_dir.glob("*.json"))
    if not files:
        raise SystemExit(f"No journey files found in {journey_dir}")

    case_rows: list[dict[str, Any]] = []
    for path in files:
        journey = load_journey(path)
        journey_id = str(journey.get("id", path.stem))
        eval_intent = str(journey.get("eval_intent", "unspecified"))
        coverage_defaults = journey.get("coverage_defaults") if isinstance(journey.get("coverage_defaults"), dict) else {}
        for case in journey.get("cases", []) or []:
            if not isinstance(case, dict):
                continue
            case_id = str(case.get("id", ""))
            prompt = str(case.get("prompt", ""))
            coverage = case.get("coverage") if isinstance(case.get("coverage"), dict) else {}

            persona = normalize_bucket(
                coverage.get("persona", coverage_defaults.get("persona")),
                PERSONA_BUCKETS,
                infer_persona(prompt, journey_id),
            )
            domain = normalize_bucket(
                coverage.get("domain", coverage_defaults.get("domain")),
                DOMAIN_BUCKETS,
                infer_domain(prompt, journey_id),
            )
            task_family = normalize_bucket(
                coverage.get("task_family", coverage_defaults.get("task_family")),
                TASK_BUCKETS,
                infer_task(prompt, journey_id, eval_intent),
            )
            input_level = normalize_bucket(
                coverage.get("input_level", coverage_defaults.get("input_level")),
                INPUT_LEVEL_BUCKETS,
                infer_input_level(prompt, journey_id),
            )
            output_depth = normalize_bucket(
                coverage.get("output_depth", coverage_defaults.get("output_depth")),
                OUTPUT_DEPTH_BUCKETS,
                infer_output_depth(prompt, journey_id),
            )

            row = {
                "journey_id": journey_id,
                "case_id": case_id,
                "eval_intent": eval_intent,
                "persona": persona,
                "domain": domain,
                "task_family": task_family,
                "input_level": input_level,
                "output_depth": output_depth,
            }
            case_rows.append(row)

    total_cases = len(case_rows)
    persona_counter = Counter(r["persona"] for r in case_rows)
    domain_counter = Counter(r["domain"] for r in case_rows)
    task_counter = Counter(r["task_family"] for r in case_rows)
    input_counter = Counter(r["input_level"] for r in case_rows)
    output_counter = Counter(r["output_depth"] for r in case_rows)

    persona_task_matrix: dict[str, Counter[str]] = {}
    for r in case_rows:
        p = r["persona"]
        t = r["task_family"]
        persona_task_matrix.setdefault(p, Counter())
        persona_task_matrix[p][t] += 1

    metrics = {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "journey_dir": str(journey_dir),
        "total_journeys": len(files),
        "total_cases": total_cases,
        "distributions": {
            "persona": dim_table(persona_counter, PERSONA_BUCKETS, total_cases),
            "domain": dim_table(domain_counter, DOMAIN_BUCKETS, total_cases),
            "task_family": dim_table(task_counter, TASK_BUCKETS, total_cases),
            "input_level": dim_table(input_counter, INPUT_LEVEL_BUCKETS, total_cases),
            "output_depth": dim_table(output_counter, OUTPUT_DEPTH_BUCKETS, total_cases),
        },
        "persona_task_matrix": {
            persona: {task: int(count) for task, count in sorted(counter.items())}
            for persona, counter in sorted(persona_task_matrix.items())
        },
        "under_covered": {
            "persona": [b for b in PERSONA_BUCKETS if persona_counter.get(b, 0) == 0],
            "domain": [b for b in DOMAIN_BUCKETS if domain_counter.get(b, 0) == 0],
            "task_family": [b for b in TASK_BUCKETS if task_counter.get(b, 0) == 0],
            "input_level": [b for b in INPUT_LEVEL_BUCKETS if input_counter.get(b, 0) == 0],
            "output_depth": [b for b in OUTPUT_DEPTH_BUCKETS if output_counter.get(b, 0) == 0],
        },
        "cases": case_rows,
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines.append("# Journey Coverage Audit")
    lines.append("")
    lines.append(f"- Generated: `{metrics['generated_at']}`")
    lines.append(f"- Journey dir: `{metrics['journey_dir']}`")
    lines.append(f"- Journeys: `{metrics['total_journeys']}`")
    lines.append(f"- Cases: `{metrics['total_cases']}`")
    lines.append("")

    for dim in ["persona", "domain", "task_family", "input_level", "output_depth"]:
        lines.append(f"## {dim.replace('_', ' ').title()}")
        rows = metrics["distributions"][dim]
        lines.append(
            markdown_table(
                ["bucket", "count", "pct"],
                [[str(r["bucket"]), str(r["count"]), f"{r['pct']:.1f}%"] for r in rows],
            )
        )
        missing = metrics["under_covered"][dim]
        lines.append("")
        lines.append(f"- Missing buckets: `{', '.join(missing) if missing else '(none)'}`")
        lines.append("")

    lines.append("## Persona x Task Matrix")
    matrix_headers = ["persona"] + TASK_BUCKETS
    matrix_rows: list[list[str]] = []
    for p in PERSONA_BUCKETS:
        counter = persona_task_matrix.get(p, Counter())
        matrix_rows.append([p] + [str(int(counter.get(t, 0))) for t in TASK_BUCKETS])
    lines.append(markdown_table(matrix_headers, matrix_rows))
    lines.append("")

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote coverage markdown: {out_md}")
    print(f"Wrote coverage json: {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
