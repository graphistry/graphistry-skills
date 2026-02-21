#!/usr/bin/env python3
"""
Decode OpenTelemetry protobuf trace files from benchmark evaluations.
Extracts LLM prompts, tool calls, and results.

Usage:
    ./bin/otel/decode_pb.py <trace.pb> [--output output.json] [--prompts] [--full]
"""

import sys
import json
import argparse
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from opentelemetry.proto.trace.v1 import trace_pb2
from opentelemetry.proto.common.v1 import common_pb2


def decode_value(value: common_pb2.AnyValue) -> any:  # type: ignore
    """Decode protobuf AnyValue to Python type."""
    if value.HasField("string_value"):
        return value.string_value
    elif value.HasField("bool_value"):
        return value.bool_value
    elif value.HasField("int_value"):
        return value.int_value
    elif value.HasField("double_value"):
        return value.double_value
    elif value.HasField("array_value"):
        return [decode_value(v) for v in value.array_value.values]
    elif value.HasField("kvlist_value"):
        return {kv.key: decode_value(kv.value) for kv in value.kvlist_value.values}
    elif value.HasField("bytes_value"):
        return value.bytes_value.hex()
    return None


def extract_span_info(span: trace_pb2.Span) -> dict:
    """Extract key information from a span."""
    attributes = {}
    for attr in span.attributes:
        attributes[attr.key] = decode_value(attr.value)

    events = []
    for event in span.events:
        event_attrs = {}
        for attr in event.attributes:
            event_attrs[attr.key] = decode_value(attr.value)
        events.append({
            "name": event.name,
            "time_unix_nano": event.time_unix_nano,
            "attributes": event_attrs
        })

    return {
        "span_id": span.span_id.hex(),
        "parent_span_id": span.parent_span_id.hex() if span.parent_span_id else None,
        "name": span.name,
        "start_time_unix_nano": span.start_time_unix_nano,
        "end_time_unix_nano": span.end_time_unix_nano,
        "attributes": attributes,
        "events": events,
        "status": {
            "code": span.status.code,
            "message": span.status.message
        }
    }


def decode_trace_file(filepath: Path) -> dict:
    """Decode an OpenTelemetry trace protobuf file."""
    with open(filepath, "rb") as f:
        data = f.read()

    # Try to parse as TracesData (collection of ResourceSpans)
    traces_data = trace_pb2.TracesData()
    try:
        traces_data.ParseFromString(data)
    except Exception as e:
        print(f"Error parsing as TracesData: {e}", file=sys.stderr)
        return {"error": str(e), "spans": []}

    all_spans = []
    for resource_spans in traces_data.resource_spans:
        resource_attrs = {}
        if resource_spans.resource:
            for attr in resource_spans.resource.attributes:
                resource_attrs[attr.key] = decode_value(attr.value)

        for scope_spans in resource_spans.scope_spans:
            scope_name = scope_spans.scope.name if scope_spans.scope else "unknown"

            for span in scope_spans.spans:
                span_info = extract_span_info(span)
                span_info["resource"] = resource_attrs
                span_info["scope"] = scope_name
                all_spans.append(span_info)

    return {
        "file": str(filepath),
        "total_spans": len(all_spans),
        "spans": all_spans
    }


def extract_llm_info(decoded_data: dict) -> list[dict]:
    """Extract LLM-related information from decoded spans."""
    llm_spans = []

    for span in decoded_data.get("spans", []):
        attrs = span.get("attributes", {})

        # Look for LLM spans (gen_ai.* or llm.* attributes)
        if any(k.startswith(("gen_ai.", "llm.")) for k in attrs.keys()):
            llm_info = {
                "span_name": span["name"],
                "span_id": span["span_id"],
                "model": attrs.get("gen_ai.request.model") or attrs.get("llm.model_name"),
                "input_tokens": attrs.get("gen_ai.usage.prompt_tokens"),
                "output_tokens": attrs.get("gen_ai.usage.completion_tokens"),
                "events": []
            }

            # Extract prompt/response from events
            for event in span.get("events", []):
                event_attrs = event.get("attributes", {})
                if "gen_ai.prompt" in event_attrs or "gen_ai.completion" in event_attrs:
                    llm_info["events"].append({
                        "name": event["name"],
                        "prompt": event_attrs.get("gen_ai.prompt"),
                        "completion": event_attrs.get("gen_ai.completion")
                    })

            llm_spans.append(llm_info)

    return llm_spans


def extract_tool_calls(decoded_data: dict) -> list[dict]:
    """Extract tool call information from decoded spans."""
    tool_spans = []

    for span in decoded_data.get("spans", []):
        if span["name"].startswith("tool."):
            attrs = span.get("attributes", {})
            tool_info = {
                "span_name": span["name"],
                "span_id": span["span_id"],
                "tool_name": attrs.get("tool.name"),
                "tool_method": attrs.get("tool.method"),
                "run_id": attrs.get("tool.run.id"),
                "args_count": attrs.get("tool.args.count"),
                "status": span["status"]
            }
            tool_spans.append(tool_info)

    return tool_spans


def main():
    parser = argparse.ArgumentParser(description="Decode OTel trace files from benchmarks")
    parser.add_argument("trace_file", type=Path, help="Path to .pb trace file")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file (default: stdout)")
    parser.add_argument("--prompts", action="store_true", help="Extract only LLM prompts")
    parser.add_argument("--full", action="store_true", help="Include full span details")
    parser.add_argument("--tools", action="store_true", help="Extract only tool calls")

    args = parser.parse_args()

    if not args.trace_file.exists():
        print(f"Error: File not found: {args.trace_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Decoding {args.trace_file}...", file=sys.stderr)
    decoded = decode_trace_file(args.trace_file)

    if args.prompts:
        result = extract_llm_info(decoded)
    elif args.tools:
        result = extract_tool_calls(decoded)
    elif not args.full:
        # Summary by default
        result = {
            "file": decoded["file"],
            "total_spans": decoded["total_spans"],
            "llm_calls": len(extract_llm_info(decoded)),
            "tool_calls": len(extract_tool_calls(decoded)),
            "span_names": list(set(s["name"] for s in decoded["spans"]))
        }
    else:
        result = decoded

    output_json = json.dumps(result, indent=2)

    if args.output:
        args.output.write_text(output_json)
        print(f"Wrote output to {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
