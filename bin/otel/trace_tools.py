#!/usr/bin/env python3
"""Small Tempo helpers for local OTel traces."""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterable, List, Optional


def tempo_url() -> str:
    return os.environ.get("OTEL_TEMPO_URL", "http://localhost:3200").rstrip("/")


def log_url() -> str:
    return os.environ.get("OTEL_LOG_URL", "http://localhost:3100").rstrip("/")


def default_service_name() -> str:
    return os.environ.get("OTEL_SERVICE_NAME", "py-louie")


def default_query(service_name: str) -> str:
    return '{resource.service.name="%s"}' % service_name


def parse_since_to_seconds(value: str) -> int:
    if value.isdigit():
        return int(value)
    match = re.match(r"^(\d+)([smhd])$", value)
    if not match:
        raise ValueError(f"Unsupported --since value: {value}")
    amount = int(match.group(1))
    unit = match.group(2)
    multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    return amount * multipliers[unit]


def parse_time_to_seconds(value: str) -> int:
    if value.isdigit():
        return int(value)
    normalized = value.replace(" ", "T")
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Unsupported time value: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return int(parsed.timestamp())


def ns_to_iso(ns: int) -> str:
    if not ns:
        return ""
    return dt.datetime.fromtimestamp(ns / 1_000_000_000, tz=dt.timezone.utc).isoformat()


def resolve_time_range(
    since: str,
    start: Optional[str],
    end: Optional[str],
) -> tuple[int, int]:
    now_s = int(dt.datetime.now(tz=dt.timezone.utc).timestamp())
    end_s = parse_time_to_seconds(end) if end else now_s
    if start:
        start_s = parse_time_to_seconds(start)
    else:
        start_s = end_s - parse_since_to_seconds(since)
    return start_s, end_s


def add_time_range_args(
    parser: argparse.ArgumentParser,
    since_default: str,
    since_help: str,
    include_start_end: bool = True,
) -> None:
    parser.add_argument("--since", default=since_default, help=since_help)
    if include_start_end:
        parser.add_argument("--start", help="Start time")
        parser.add_argument("--end", help="End time")


def add_limit_arg(parser: argparse.ArgumentParser, default: int, help_text: str) -> None:
    parser.add_argument("--limit", type=int, default=default, help=help_text)


def add_service_arg(parser: argparse.ArgumentParser, help_text: str) -> None:
    parser.add_argument("--service", help=help_text)


def parse_int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def parse_bool_env(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "y", "on")


def auto_log_headroom(max_bytes_config: int) -> int:
    if max_bytes_config <= 0:
        return 0
    one_percent = max_bytes_config // 100
    return min(max_bytes_config, max(1024, min(16_384, one_percent)))


def fetch_json(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read().decode("utf-8")
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Non-JSON response from {url}") from exc


def collector_url() -> str:
    return os.environ.get("OTEL_COLLECTOR_URL", "http://localhost:13133").rstrip("/")


def load_louie_ports(path: Optional[str] = None) -> Dict[str, str]:
    ports_path = path or os.path.join(os.getcwd(), ".louie-ports")
    if not os.path.exists(ports_path):
        return {}
    ports: Dict[str, str] = {}
    try:
        with open(ports_path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                ports[key.strip()] = value.strip()
    except Exception:
        return {}
    return ports


def normalize_api_base(base: str) -> str:
    trimmed = base.rstrip("/")
    if trimmed.endswith("/api"):
        trimmed = trimmed[:-4]
    return trimmed


def resolve_api_base(explicit: Optional[str]) -> Optional[str]:
    if explicit:
        return normalize_api_base(explicit)
    env_url = os.environ.get("LOUIE_API_URL") or os.environ.get("LOUIE_API_BASE_URL")
    if env_url:
        return normalize_api_base(env_url)
    ports = load_louie_ports()
    api_port = ports.get("LOUIE_API_PORT")
    if api_port:
        return f"http://localhost:{api_port}"
    base_url = ports.get("LOUIE_BASE_URL")
    if base_url:
        return normalize_api_base(base_url)
    env_port = os.environ.get("LOUIE_API_PORT") or os.environ.get("DESKTOP_API_PORT")
    if env_port:
        host = os.environ.get("DESKTOP_API_HOST", "localhost")
        return f"http://{host}:{env_port}"
    return None


def resolve_web_base(explicit: Optional[str] = None) -> Optional[str]:
    if explicit:
        return explicit.rstrip("/")
    env_url = os.environ.get("LOUIE_BASE_URL") or os.environ.get("LOUIE_WEB_URL")
    if env_url:
        return env_url.rstrip("/")
    ports = load_louie_ports()
    base_url = ports.get("LOUIE_BASE_URL")
    if base_url:
        return base_url.rstrip("/")
    web_port = ports.get("LOUIE_WEB_PORT") or os.environ.get("LOUIE_WEB_PORT") or os.environ.get("DESKTOP_WEB_PORT")
    if web_port:
        return f"http://localhost:{web_port}"
    return None


def check_http(
    url: str,
    headers: Optional[Dict[str, str]] = None,
) -> tuple[bool, int, str, Optional[str]]:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return True, resp.getcode(), resp.reason or "OK", body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return False, exc.code, exc.reason or "HTTPError", body
    except Exception as exc:
        return False, 0, str(exc), None


def post_json(
    url: str,
    payload: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> tuple[bool, int, str, Optional[str]]:
    body = json.dumps(payload or {}).encode("utf-8")
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8", errors="replace")
            return True, resp.getcode(), resp.reason or "OK", data
    except urllib.error.HTTPError as exc:
        data = exc.read().decode("utf-8", errors="replace")
        return False, exc.code, exc.reason or "HTTPError", data
    except Exception as exc:
        return False, 0, str(exc), None


def normalize_span_id(span_id: str) -> tuple[str, Optional[str]]:
    """Normalize span ID to hex if the input is base64."""
    raw = span_id.strip()
    if re.fullmatch(r"[0-9a-fA-F]{16}", raw):
        return raw.lower(), None
    try:
        padded = raw + "=" * ((4 - (len(raw) % 4)) % 4)
        decoded = base64.b64decode(padded, validate=False)
    except Exception:
        return raw, None
    if len(decoded) == 8:
        return decoded.hex(), raw
    return raw, None


def parse_kv_pairs(message: str) -> Dict[str, str]:
    parts = message.split()
    data: Dict[str, str] = {}
    if not parts:
        return data
    data["event"] = parts[0]
    for part in parts[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        data[key] = value
    return data


def is_uuid(value: str) -> bool:
    return re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", value) is not None


def span_status_label(span: Dict[str, Any]) -> str:
    status = span.get("status", {}) or {}
    code = status.get("code") or status.get("statusCode")
    attrs = span.get("attrs", {}) or {}
    if attrs.get("error") or str(code).lower() in ("2", "error", "status_code_error"):
        return "x"
    return "✓"


def attr_value(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    if "stringValue" in value:
        return value["stringValue"]
    if "intValue" in value:
        try:
            return int(value["intValue"])
        except Exception:
            return value["intValue"]
    if "doubleValue" in value:
        try:
            return float(value["doubleValue"])
        except Exception:
            return value["doubleValue"]
    if "boolValue" in value:
        return bool(value["boolValue"])
    if "arrayValue" in value:
        return [
            attr_value(item.get("value"))
            for item in value.get("arrayValue", {}).get("values", [])
        ]
    if "kvlistValue" in value:
        return {
            item.get("key"): attr_value(item.get("value"))
            for item in value.get("kvlistValue", {}).get("values", [])
        }
    return value


def collect_spans(trace: Dict[str, Any]) -> List[Dict[str, Any]]:
    spans: List[Dict[str, Any]] = []
    for batch in trace.get("batches", []) or []:
        batch_spans = batch.get("spans")
        if batch_spans is None:
            batch_spans = []
            for scope_span in batch.get("scopeSpans", []) or []:
                batch_spans.extend(scope_span.get("spans", []) or [])
        for span in batch_spans:
            attrs = {
                attr.get("key"): attr_value(attr.get("value"))
                for attr in span.get("attributes", []) or []
            }
            start_ns = int(span.get("startTimeUnixNano") or 0)
            end_ns = int(span.get("endTimeUnixNano") or 0)
            duration_ms = (end_ns - start_ns) / 1_000_000 if start_ns and end_ns else 0.0
            spans.append({
                "span_id": span.get("spanId", ""),
                "parent_id": span.get("parentSpanId", ""),
                "name": span.get("name", ""),
                "start_ns": start_ns,
                "end_ns": end_ns,
                "duration_ms": duration_ms,
                "status": span.get("status", {}),
                "attrs": attrs,
                "events": span.get("events", []) or [],
            })
    return spans


def root_spans(spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    span_ids = {span["span_id"] for span in spans}
    roots: List[Dict[str, Any]] = []
    for span in spans:
        parent_id = span.get("parent_id") or ""
        if not parent_id or parent_id not in span_ids or parent_id == "0000000000000000":
            roots.append(span)
    return sorted(roots, key=lambda s: s["start_ns"])


def iter_span_tree(spans: List[Dict[str, Any]]) -> Iterable[tuple[int, Dict[str, Any]]]:
    children: Dict[str, List[Dict[str, Any]]] = {}
    for span in spans:
        children.setdefault(span.get("parent_id") or "", []).append(span)
    for kids in children.values():
        kids.sort(key=lambda s: s["start_ns"])

    def walk(span: Dict[str, Any], depth: int) -> Iterable[tuple[int, Dict[str, Any]]]:
        yield depth, span
        for child in children.get(span["span_id"], []):
            yield from walk(child, depth + 1)

    for root in root_spans(spans):
        yield from walk(root, 0)


def list_traces(args: argparse.Namespace) -> None:
    service = args.service or default_service_name()
    query = args.query or default_query(service)
    start_s, end_s = resolve_time_range(args.since, args.start, args.end)

    params = {
        "q": query,
        "start": start_s,
        "end": end_s,
        "limit": args.limit,
    }
    data = fetch_json(f"{tempo_url()}/api/search", params=params)
    traces = data.get("traces", []) or []
    if not traces:
        print("No traces found.")
        return
    print("trace_id\tduration_ms\troot_service\troot_name\tstart_time")
    for trace in traces:
        trace_id = trace.get("traceID") or trace.get("traceId") or trace.get("trace_id") or ""
        root_service = trace.get("rootServiceName") or ""
        root_name = trace.get("rootTraceName") or ""
        duration_ms = trace.get("durationMs")
        if duration_ms is None and trace.get("duration"):
            duration_ms = int(trace.get("duration")) / 1_000_000
        start_time = ns_to_iso(int(trace.get("startTimeUnixNano") or 0))
        print(f"{trace_id}\t{duration_ms}\t{root_service}\t{root_name}\t{start_time}")


def get_trace(trace_id: str) -> Dict[str, Any]:
    return fetch_json(f"{tempo_url()}/api/traces/{trace_id}")


def span_name_matches(span: Dict[str, Any], match: Optional[str]) -> bool:
    if not match:
        return True
    try:
        return re.search(match, span.get("name", "")) is not None
    except re.error:
        return match in span.get("name", "")

def trace_to_spans(args: argparse.Namespace) -> List[Dict[str, Any]]:
    trace = get_trace(args.trace_id)
    spans = collect_spans(trace)
    spans.sort(key=lambda s: s["start_ns"])
    return spans

def trace2tree(args: argparse.Namespace) -> None:
    spans = trace_to_spans(args)
    if not spans:
        print("No spans found.")
        return
    for depth, span in iter_span_tree(spans):
        if not span_name_matches(span, args.match):
            continue
        indent = "  " * depth
        print(f"{indent}{span.get('name')} [{span.get('duration_ms'):.2f}ms]")


def trace2spans(args: argparse.Namespace) -> None:
    spans = trace_to_spans(args)
    if not spans:
        print("No spans found.")
        return
    filtered = [s for s in spans if span_name_matches(s, getattr(args, "match", None))]
    if not filtered:
        print("No spans matched.")
        return

    show_queue = any("queue_delay_ms" in (s.get("attrs") or {}) for s in filtered)
    show_loop = any("event_loop_id" in (s.get("attrs") or {}) for s in filtered)
    headers = ["span_id", "parent_id", "duration_ms", "name", "status"]
    if show_queue:
        headers.append("queue_delay_ms")
    if show_loop:
        headers.append("event_loop_id")
    print("\t".join(headers))

    for span in filtered:
        attrs = span.get("attrs", {}) or {}
        row = [
            span.get("span_id", ""),
            span.get("parent_id", ""),
            f"{span.get('duration_ms', 0.0):.2f}",
            span.get("name", ""),
            span_status_label(span),
        ]
        if show_queue:
            row.append(str(attrs.get("queue_delay_ms", "")))
        if show_loop:
            row.append(str(attrs.get("event_loop_id", "")))
        print("\t".join(row))


def trace2events(args: argparse.Namespace) -> None:
    spans = trace_to_spans(args)
    if not spans:
        print("No spans found.")
        return
    span_id = getattr(args, "span", None)
    match = getattr(args, "event", None)
    include_attrs = getattr(args, "attrs", False)
    print("timestamp\tspan\tlevel\tmessage")
    for span in spans:
        if span_id and span.get("span_id") != span_id:
            continue
        for event in span.get("events", []) or []:
            name = event.get("name", "")
            if match and not span_name_matches({"name": name}, match):
                continue
            attrs = {
                attr.get("key"): attr_value(attr.get("value"))
                for attr in event.get("attributes", []) or []
            }
            level = attrs.get("level") or attrs.get("severity") or attrs.get("severity_text") or ""
            message = attrs.get("msg") or attrs.get("message") or name
            if include_attrs:
                message = f"{message} {json.dumps(attrs, ensure_ascii=True)}"
            timestamp = ns_to_iso(int(event.get("timeUnixNano") or 0))
            print(f"{timestamp}\t{span.get('name','')}\t{level}\t{message}")


def find_errors(args: argparse.Namespace) -> None:
    spans = trace_to_spans(args)
    if not spans:
        print("No spans found.")
        return
    headers = ["span_id", "duration_ms", "name", "status"]
    print("\t".join(headers))
    for span in spans:
        if not span_name_matches(span, getattr(args, "match", None)):
            continue
        if span_status_label(span) != "x":
            continue
        print(
            f"{span.get('span_id','')}\t{span.get('duration_ms',0.0):.2f}\t"
            f"{span.get('name','')}\t{span_status_label(span)}"
        )

def _query_log_backend(
    query: str,
    limit: int,
    start_ns: int,
    end_ns: int,
) -> tuple[List[Dict[str, Any]], Optional[str]]:
    params = {
        "query": query,
        "limit": str(limit),
        "start": str(start_ns),
        "end": str(end_ns),
    }
    url = f"{log_url()}/loki/api/v1/query_range?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.load(resp)
    except Exception as e:
        return [], f"Error querying logs backend: {e}"

    if data.get("status") != "success":
        return [], f"Log query failed: {data}"

    results = data.get("data", {}).get("result", [])
    return results, None


def collect_log_lines(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    all_logs: List[Dict[str, Any]] = []
    for stream in results:
        labels = stream.get("stream", {})
        level = labels.get("severity_text", labels.get("detected_level", "INFO"))
        for ts_ns, message in stream.get("values", []):
            ts_ns_int = int(ts_ns)
            all_logs.append({
                "ts_ns": ts_ns_int,
                "timestamp": ns_to_iso(ts_ns_int),
                "level": level,
                "message": message,
            })
    all_logs.sort(key=lambda x: x["ts_ns"])
    return all_logs


def fetch_span_logs(
    span_id: str,
    service: str,
    start_s: int,
    end_s: int,
    trace_id: Optional[str] = None,
    limit: int = 200,
) -> List[Dict[str, Any]]:
    start_ns = start_s * int(1e9)
    end_ns = end_s * int(1e9)
    span_hex, span_original = normalize_span_id(span_id)
    base_selector = f'{{service_name="{service}"}}'
    span_filters = [f'span_id="{span_hex}"', f'otelSpanID="{span_hex}"']
    if span_original and span_original != span_hex:
        span_filters.extend([f'span_id="{span_original}"', f'otelSpanID="{span_original}"'])
    trace_filters = []
    if trace_id:
        trace_filters = [f'trace_id="{trace_id}"', f'otelTraceID="{trace_id}"']

    queries = [
        *(f'{base_selector} | {tf} | {sf}' for tf in trace_filters for sf in span_filters),
        *(f'{base_selector} | {sf}' for sf in span_filters),
    ]
    for query in queries:
        results, _ = _query_log_backend(query, limit, start_ns, end_ns)
        logs = collect_log_lines(results)
        if logs:
            return logs
    return []


def trace2logs(args: argparse.Namespace) -> None:
    """Query the logs backend for logs correlated with a trace_id."""
    trace_id = args.trace_id
    limit = getattr(args, "limit", 100)
    service = getattr(args, "service", None) or default_service_name()
    span_id = getattr(args, "span", None)
    full = getattr(args, "full", False)
    start_s, end_s = resolve_time_range(getattr(args, "since", "1h"), None, None)

    logs: List[Dict[str, Any]] = []
    last_error: Optional[str] = None
    if span_id:
        logs = fetch_span_logs(span_id, service, start_s, end_s, trace_id=trace_id, limit=limit)
        if not logs:
            print("Span-scoped logs not found; falling back to trace-level logs")

    if not logs:
        start_ns = start_s * int(1e9)
        end_ns = end_s * int(1e9)
        base_selector = f'{{service_name="{service}"}}'
        for query in (
            f'{base_selector} | trace_id="{trace_id}"',
            f'{base_selector} | otelTraceID="{trace_id}"',
        ):
            results, last_error = _query_log_backend(query, limit, start_ns, end_ns)
            logs = collect_log_lines(results)
            if logs:
                break

    if not logs:
        if last_error:
            print(last_error)
        suffix = f" span_id={span_id}" if span_id else ""
        print(f"No logs found for trace_id={trace_id}{suffix}")
        return

    print_logs(logs, full)

def print_logs(logs: List[Dict[str, str]], full: bool) -> None:
    print("timestamp\tlevel\tmessage")
    for entry in logs:
        message = entry["message"]
        if full:
            msg_display = message.replace("\n", "\\n")
        else:
            msg_display = message[:200] + "..." if len(message) > 200 else message
        print(f"{entry['timestamp']}\t{entry['level']}\t{msg_display}")


def search_logs(args: argparse.Namespace) -> None:
    service = args.service or default_service_name()
    if not args.contains:
        print("Missing --contains value")
        return
    start_s, end_s = resolve_time_range(args.since, args.start, args.end)
    start_ns = start_s * int(1e9)
    end_ns = end_s * int(1e9)
    query = f'{{service_name="{service}"}} |= "{args.contains}"'
    results, err = _query_log_backend(query, args.limit, start_ns, end_ns)
    logs = collect_log_lines(results)
    if logs:
        print_logs(logs, args.full)
    else:
        print("No logs found.")
    if err:
        print(f"log query error: {err}")


def _collect_session_runs(
    session_id: str,
    start_s: int,
    end_s: int,
    service: str,
    limit: int,
) -> List[Dict[str, Any]]:
    query = f'{{name="api_run" && resource.service.name="{service}"}}'
    params = {
        "q": query,
        "start": start_s,
        "end": end_s,
        "limit": limit,
    }
    data = fetch_json(f"{tempo_url()}/api/search", params=params)
    traces = data.get("traces", []) or []
    runs: List[Dict[str, Any]] = []
    for trace_meta in traces:
        trace_id = trace_meta.get("traceID") or trace_meta.get("traceId") or trace_meta.get("trace_id") or ""
        if not trace_id:
            continue
        try:
            trace = get_trace(trace_id)
        except Exception:
            continue
        spans = collect_spans(trace)
        for span in spans:
            attrs = span.get("attrs", {}) or {}
            span_session = attrs.get("session.id") or attrs.get("session_id")
            if span_session != session_id:
                continue
            runs.append({
                "span": span,
                "trace_id": trace_id,
            })
    runs.sort(key=lambda r: r["span"].get("start_ns", 0))
    return runs


def _collect_sessions(
    start_s: int,
    end_s: int,
    service: str,
    limit: int,
    query: Optional[str] = None,
) -> List[Dict[str, Any]]:
    search_query = query or f'{{name="api_run" && resource.service.name="{service}"}}'
    params = {
        "q": search_query,
        "start": start_s,
        "end": end_s,
        "limit": limit,
    }
    data = fetch_json(f"{tempo_url()}/api/search", params=params)
    traces = data.get("traces", []) or []
    sessions: Dict[str, Dict[str, Any]] = {}
    for trace_meta in traces:
        trace_id = trace_meta.get("traceID") or trace_meta.get("traceId") or trace_meta.get("trace_id") or ""
        if not trace_id:
            continue
        try:
            trace = get_trace(trace_id)
        except Exception:
            continue
        spans = collect_spans(trace)
        for span in spans:
            attrs = span.get("attrs", {}) or {}
            session_id = attrs.get("session.id") or attrs.get("session_id")
            if not session_id:
                continue
            run_id = attrs.get("run.id") or attrs.get("run_id")
            git_sha = attrs.get("git.sha") or attrs.get("git_sha")
            git_dirty = attrs.get("git.dirty") or attrs.get("git_dirty")
            entry = sessions.setdefault(session_id, {
                "start_ns": span.get("start_ns", 0),
                "end_ns": span.get("end_ns", 0),
                "runs": set(),
                "status": "✓",
                "git_sha": git_sha or "-",
                "git_dirty": git_dirty or "-",
            })
            entry["start_ns"] = min(entry["start_ns"], span.get("start_ns", 0) or entry["start_ns"])
            entry["end_ns"] = max(entry["end_ns"], span.get("end_ns", 0))
            if run_id:
                entry["runs"].add(run_id)
            if span_status_label(span) == "x":
                entry["status"] = "x"
            if git_sha and entry["git_sha"] == "-":
                entry["git_sha"] = git_sha
            if git_dirty and entry["git_dirty"] == "-":
                entry["git_dirty"] = git_dirty

    rows = []
    for session_id, entry in sessions.items():
        start_ns = entry["start_ns"]
        end_ns = entry["end_ns"]
        duration_s = (end_ns - start_ns) / 1_000_000_000 if start_ns and end_ns else 0
        rows.append({
            "session_id": session_id,
            "time": ns_to_iso(start_ns),
            "duration_s": duration_s,
            "runs": len(entry["runs"]),
            "status": entry["status"],
            "git_sha": entry["git_sha"],
            "git_dirty": entry["git_dirty"],
            "start_ns": start_ns,
        })
    rows.sort(key=lambda r: r["time"], reverse=True)
    return rows


def list_sessions(args: argparse.Namespace) -> None:
    service = args.service or default_service_name()
    start_s, end_s = resolve_time_range(args.since, args.start, args.end)
    limit = getattr(args, "limit", 200)
    rows = _collect_sessions(start_s, end_s, service, limit, args.query)
    if not rows:
        print("No sessions found.")
        return
    print("session_id\ttime\tduration_s\truns\tstatus\tgit_sha\tgit_dirty")
    for row in rows:
        print(
            f"{row['session_id']}\t{row['time']}\t{row['duration_s']:.1f}\t"
            f"{row['runs']}\t{row['status']}\t{row['git_sha']}\t{row['git_dirty']}"
        )


def session2runs(args: argparse.Namespace) -> None:
    service = args.service or default_service_name()
    session_id = args.session_id
    start_s, end_s = resolve_time_range(args.since, args.start, args.end)
    runs = _collect_session_runs(session_id, start_s, end_s, service, args.limit)
    if not runs:
        print("turn\trun_id\tdthread_id\tduration_ms\tagent\tstatus\ttrace_id")
        return
    print("turn\trun_id\tdthread_id\tduration_ms\tagent\tstatus\ttrace_id")
    for idx, item in enumerate(runs, 1):
        span = item["span"]
        attrs = span.get("attrs", {}) or {}
        print(
            f"{idx}\t{attrs.get('run.id','')}\t{attrs.get('dthread.id','')}\t"
            f"{span.get('duration_ms',0.0):.0f}\t{attrs.get('agent','')}\t"
            f"{span_status_label(span)}\t{item['trace_id']}"
        )


def _resolve_run_trace_for_dthread(
    dthread_id: str,
    start_s: int,
    end_s: int,
    service: str,
    limit: int = 10,
) -> tuple[str, str]:
    query = f'{{span.dthread.id="{dthread_id}" && resource.service.name="{service}"}}'
    params = {
        "q": query,
        "start": start_s,
        "end": end_s,
        "limit": limit,
    }
    data = fetch_json(f"{tempo_url()}/api/search", params=params)
    traces = data.get("traces", []) or []
    for trace_meta in traces:
        trace_id = trace_meta.get("traceID") or trace_meta.get("traceId") or trace_meta.get("trace_id") or ""
        if not trace_id:
            continue
        try:
            trace = get_trace(trace_id)
        except Exception:
            continue
        spans = collect_spans(trace)
        for span in spans:
            attrs = span.get("attrs", {}) or {}
            if attrs.get("dthread.id") == dthread_id:
                run_id = attrs.get("run.id") or attrs.get("run_id") or ""
                return run_id, trace_id
    return "", ""

def _resolve_runs_for_bots_run(
    bots_run_id: str,
    start_s: int,
    end_s: int,
    service: str,
    limit: int = 50,
) -> Dict[str, Dict[str, str]]:
    query = f'{{span.bots.run_id="{bots_run_id}" && resource.service.name="{service}"}}'
    params = {
        "q": query,
        "start": start_s,
        "end": end_s,
        "limit": limit,
    }
    data = fetch_json(f"{tempo_url()}/api/search", params=params)
    traces = data.get("traces", []) or []
    results: Dict[str, Dict[str, str]] = {}
    for trace_meta in traces:
        trace_id = trace_meta.get("traceID") or trace_meta.get("traceId") or trace_meta.get("trace_id") or ""
        if not trace_id:
            continue
        try:
            trace = get_trace(trace_id)
        except Exception:
            continue
        spans = collect_spans(trace)
        run_id = ""
        dthread_id = ""
        for span in spans:
            attrs = span.get("attrs", {}) or {}
            if not run_id:
                run_id = attrs.get("run.id") or attrs.get("run_id") or ""
            if not dthread_id:
                dthread_id = (
                    attrs.get("dthread.id")
                    or attrs.get("dthread_id")
                    or attrs.get("bots.thread_id")
                    or ""
                )
            if run_id and dthread_id:
                break
        for span in spans:
            attrs = span.get("attrs", {}) or {}
            qid_raw = attrs.get("bots.question_id") or attrs.get("bots.qid") or ""
            if not qid_raw:
                continue
            qid = qid_raw if qid_raw.startswith("Q") else f"Q{qid_raw}"
            entry = results.setdefault(qid, {})
            entry.setdefault("trace_id", trace_id)
            if run_id:
                entry.setdefault("run_id", run_id)
            if dthread_id:
                entry.setdefault("dthread_id", dthread_id)
    return results

def run_status(args: argparse.Namespace) -> None:
    target = args.run_id
    start_s, end_s = resolve_time_range(args.since, args.start, args.end)

    is_trace_id = len(target) == 32 and all(c in "0123456789abcdef" for c in target.lower())
    is_run_id = target.startswith("R_") or target.startswith("run_")
    if is_trace_id or is_run_id:
        print(f"=== Run {target} ===")
        run_args = argparse.Namespace(
            run_id=target,
            since=args.since,
            start=args.start,
            end=args.end,
            service=default_service_name(),
            prompts=False,
            full=args.full,
            logs=False,
            index=None,
            span=None,
        )
        run2llm(run_args)
        return

    if args.logs:
        start_ns = start_s * int(1e9)
        end_ns = end_s * int(1e9)
        services = [("runner", args.runner_service), ("client", args.client_service)]
        for label, service in services:
            query = f'{{service_name="{service}"}} |= "bots.run_id={target}"'
            results, err = _query_log_backend(query, args.limit, start_ns, end_ns)
            logs = collect_log_lines(results)
            print(f"=== {label} logs ({service}) ===")
            if logs:
                print_logs(logs, args.full)
            else:
                print("No logs found.")
            if err:
                print(f"{label} log query error: {err}")
            print()
        return

    runner_service = args.runner_service
    client_service = args.client_service
    runner_query = f'{{service_name="{runner_service}"}} |= "bots.run_id={target}"'
    client_query = f'{{service_name="{client_service}"}} |= "bots.run_id={target}"'
    start_ns = start_s * int(1e9)
    end_ns = end_s * int(1e9)
    runner_results, _ = _query_log_backend(runner_query, args.limit, start_ns, end_ns)
    client_results, _ = _query_log_backend(client_query, args.limit, start_ns, end_ns)
    runner_logs = collect_log_lines(runner_results)
    client_logs = collect_log_lines(client_results)

    questions: Dict[str, Dict[str, Any]] = {}
    for entry in runner_logs:
        data = parse_kv_pairs(entry["message"])
        event = data.get("event", "")
        if not event.startswith("bots.question."):
            continue
        status = event.split(".")[-1]
        qid_raw = data.get("bots.qid") or data.get("bots.question_id") or ""
        if not qid_raw:
            continue
        qid = qid_raw if qid_raw.startswith("Q") else f"Q{qid_raw}"
        qstate = questions.setdefault(qid, {})
        qstate["status"] = status
        if "duration_s" in data:
            qstate["duration_s"] = data["duration_s"]

    for entry in client_logs:
        data = parse_kv_pairs(entry["message"])
        if data.get("event") != "bots.add_cell.start":
            continue
        qid_raw = data.get("bots.question_id") or data.get("bots.qid") or ""
        if not qid_raw:
            continue
        qid = qid_raw if qid_raw.startswith("Q") else f"Q{qid_raw}"
        dthread_id = data.get("bots.thread_id") or ""
        if not dthread_id:
            continue
        qstate = questions.setdefault(qid, {})
        if not qstate.get("dthread_id"):
            qstate["dthread_id"] = dthread_id

    service = default_service_name()
    trace_hits = _resolve_runs_for_bots_run(target, start_s, end_s, args.client_service, args.limit)
    trace_cache: Dict[str, tuple[str, str]] = {}
    for qid, qstate in questions.items():
        if qid in trace_hits:
            hit = trace_hits[qid]
            if not qstate.get("dthread_id") and hit.get("dthread_id"):
                qstate["dthread_id"] = hit["dthread_id"]
            qstate.setdefault("run_id", hit.get("run_id", ""))
            qstate.setdefault("trace_id", hit.get("trace_id", ""))
        dthread_id = qstate.get("dthread_id")
        if not dthread_id:
            continue
        if dthread_id not in trace_cache:
            trace_cache[dthread_id] = _resolve_run_trace_for_dthread(dthread_id, start_s, end_s, service)
        run_id, trace_id = trace_cache[dthread_id]
        qstate["run_id"] = run_id
        qstate["trace_id"] = trace_id

    print("question\tstatus\tduration_s\tdthread_id\trun_id\ttrace_id")
    for qid in sorted(questions.keys(), key=lambda v: int(v[1:]) if v[1:].isdigit() else v):
        qstate = questions[qid]
        print(
            f"{qid}\t{qstate.get('status','')}\t{qstate.get('duration_s','')}\t"
            f"{qstate.get('dthread_id','')}\t{qstate.get('run_id','')}\t{qstate.get('trace_id','')}"
        )

def status(args: argparse.Namespace) -> None:
    results: List[Dict[str, Any]] = []

    def add_result(
        component: str,
        url: str,
        ok: bool,
        code: int,
        detail: str,
        status_override: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        if status_override:
            status_label = status_override
        elif ok:
            status_label = "ok"
        elif code in (401, 403):
            status_label = "unauthorized"
        elif code == 0:
            status_label = "error"
        else:
            status_label = "fail"
        entry = {
            "component": component,
            "status": status_label,
            "url": url or "-",
            "detail": detail,
        }
        if data:
            entry["data"] = data
        results.append(entry)

    def optional_check(component: str, url: str, explicit: bool, missing_hint: str) -> None:
        ok, code, reason, _ = check_http(url)
        detail = f"{code} {reason}" if code else reason
        if ok or explicit:
            add_result(component, url, ok, code, detail)
        else:
            add_result(component, url, False, 0, missing_hint, status_override="skip")

    optional_check(
        "tempo",
        f"{tempo_url()}/ready",
        os.environ.get("OTEL_TEMPO_URL") is not None,
        "not detected (Tempo optional; set OTEL_TEMPO_URL to check)",
    )
    optional_check(
        "logs",
        f"{log_url()}/ready",
        os.environ.get("OTEL_LOG_URL") is not None,
        "not detected (logs backend optional; set OTEL_LOG_URL to check)",
    )
    collector_arg = getattr(args, "collector", None)
    collector_env = os.environ.get("OTEL_COLLECTOR_URL")
    collector = collector_arg or collector_env or collector_url()
    optional_check(
        "collector",
        collector,
        collector_arg is not None or collector_env is not None,
        "not detected (set --collector or OTEL_COLLECTOR_URL to check)",
    )

    log_capture = parse_bool_env("OTEL_LLM_LOG_CAPTURE", False)
    max_bytes = parse_int_env("OTEL_LLM_LOG_MAX_CHARS", 1_048_576)
    headroom_cfg = parse_int_env("OTEL_LLM_LOG_HEADROOM_BYTES", -1)
    if max_bytes <= 0:
        headroom_bytes = 0
        budget_label = "unlimited"
        max_label = "unlimited"
        headroom_mode = "n/a"
    else:
        headroom_bytes = auto_log_headroom(max_bytes) if headroom_cfg < 0 else min(max_bytes, max(0, headroom_cfg))
        budget_label = str(max(0, max_bytes - headroom_bytes))
        max_label = str(max_bytes)
        headroom_mode = "auto" if headroom_cfg < 0 else "fixed"
    limit_detail = (
        f"capture={int(log_capture)} max_bytes={max_label} "
        f"headroom_bytes={headroom_bytes} budget_bytes={budget_label} headroom_mode={headroom_mode}"
    )
    limit_data = {
        "capture": log_capture,
        "max_bytes": max_bytes,
        "headroom_bytes": headroom_bytes,
        "budget_bytes": max(0, max_bytes - headroom_bytes) if max_bytes > 0 else 0,
        "headroom_mode": headroom_mode,
        "max_bytes_source": "default",
        "headroom_source": "auto" if headroom_cfg < 0 else "fixed",
    }
    add_result(
        "llm.log.limit",
        "-",
        True,
        200,
        limit_detail,
        status_override="skip" if not log_capture else None,
        data=limit_data,
    )

    api_base = resolve_api_base(getattr(args, "api", None))
    token = None
    if not api_base:
        add_result("api.health", "-", False, 0, "no API base (set --api or run from repo root)", status_override="skip")
        add_result("api.capabilities", "-", False, 0, "no API base (set --api or run from repo root)", status_override="skip")
    else:
        api_health = f"{api_base}/api/health"
        ok, code, reason, _ = check_http(api_health)
        add_result("api.health", api_health, ok, code, f"{code} {reason}" if code else reason)

        token = (
            getattr(args, "token", None)
            or os.environ.get("GRAPHISTRY_TOKEN")
            or os.environ.get("LOUIE_TOKEN")
            or os.environ.get("LOUIE_ANON_TOKEN")
        )
        if not token:
            anon_failed = False
            web_base = resolve_web_base()
            if web_base and ("localhost" in web_base or "127.0.0.1" in web_base):
                ok, code, reason, body = post_json(f"{web_base}/auth/anonymous")
                if ok and body:
                    try:
                        payload = json.loads(body)
                    except json.JSONDecodeError:
                        payload = {}
                    token = payload.get("token")
                if not token:
                    detail = f"{code} {reason}" if code else reason
                    add_result(
                        "api.capabilities",
                        f"{api_base}/api/capabilities",
                        False,
                        0,
                        f"missing --token (anon failed: {detail})",
                        status_override="skip",
                    )
                    anon_failed = True
            if not token and not anon_failed:
                add_result("api.capabilities", f"{api_base}/api/capabilities", False, 0, "missing --token", status_override="skip")
        else:
            caps_url = f"{api_base}/api/capabilities"
            ok, code, reason, body = check_http(caps_url, headers={"Authorization": f"Bearer {token}"})
            detail = f"{code} {reason}" if code else reason
            if ok and body:
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    detail = f"{detail} (non-JSON response)"
                else:
                    site = payload.get("site") if isinstance(payload, dict) else None
                    otel_data = site.get("otel") if isinstance(site, dict) else None
                    if otel_data:
                        endpoint = otel_data.get("endpoint") or "hidden"
                        detail = (
                            f"{detail} otel.enabled={otel_data.get('enabled')} "
                            f"traces={otel_data.get('traces_enabled')} logs={otel_data.get('logs_enabled')} "
                            f"metrics={otel_data.get('metrics_enabled')} endpoint={endpoint}"
                        )
                    else:
                        detail = f"{detail} (no site-level OTel info)"
            add_result("api.capabilities", caps_url, ok, code, detail)

    if getattr(args, "json", False):
        print(json.dumps(results, indent=2))
    else:
        print("component\tstatus\turl\tdetail")
        for entry in results:
            print(f"{entry['component']}\t{entry['status']}\t{entry['url']}\t{entry['detail']}")

        if not api_base:
            print("Hint: pass --api http://localhost:$LOUIE_API_PORT or run from repo root with .louie-ports")


def collect_llm_calls(
    run_id: str,
    service: str,
    start_s: int,
    end_s: int,
    include_prompts: bool,
) -> List[Dict[str, Any]]:
    def _format_messages(value: Any) -> str:
        if value is None:
            return ""
        data: Any = value
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                return data
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            return str(data)
        lines: List[str] = []
        for msg in data:
            if not isinstance(msg, dict):
                lines.append(str(msg))
                continue
            role = msg.get("role") or msg.get("message.role") or ""
            parts = msg.get("parts")
            content = ""
            if isinstance(parts, list):
                chunks: List[str] = []
                for part in parts:
                    if isinstance(part, dict):
                        for key in ("content", "result", "text"):
                            if key in part and part[key]:
                                chunks.append(str(part[key]))
                                break
                    elif part is not None:
                        chunks.append(str(part))
                content = "\n".join(chunks)
            if not content:
                content = str(msg.get("content") or msg.get("message.content") or msg.get("text") or "")
            prefix = f"[{role}]" if role else "[message]"
            lines.append(f"{prefix}\n{content}".strip())
        return "\n\n".join([line for line in lines if line])

    query = '{span.run.id = "%s" && resource.service.name="%s"}' % (run_id, service)
    params = {
        "q": query,
        "start": start_s,
        "end": end_s,
        "limit": 50,
    }
    data = fetch_json(f"{tempo_url()}/api/search", params=params)
    traces = data.get("traces", []) or []

    llm_calls: List[Dict[str, Any]] = []
    for trace_meta in traces:
        trace_id = trace_meta.get("traceID") or trace_meta.get("traceId") or ""
        if not trace_id:
            continue
        try:
            trace = get_trace(trace_id)
        except Exception:
            continue

        spans = collect_spans(trace)
        for span in spans:
            name = span.get("name", "")
            name_lower = name.lower()
            attrs = span.get("attrs", {})
            events = span.get("events", []) or []
            has_llm_attrs = any(
                key in attrs
                for key in (
                    "llm.model",
                    "model",
                    "prompt_tokens",
                    "completion_tokens",
                    "llm.model_name",
                    "llm.system",
                    "gen_ai.request.model",
                    "gen_ai.usage.input_tokens",
                    "openinference.span.kind",
                )
            )
            has_llm_events = any(
                event.get("name") in ("llm.prompt", "llm.response", "gen_ai.client.inference.operation.details")
                for event in events
            )
            if "llm" in name_lower or "completion" in name_lower or has_llm_attrs or has_llm_events:
                prompt_text = ""
                response_text = ""
                if include_prompts:
                    for event in events:
                        event_name = event.get("name", "")
                        event_attrs = {
                            a.get("key"): attr_value(a.get("value"))
                            for a in event.get("attributes", []) or []
                        }
                        if event_name == "llm.prompt":
                            prompt_text = str(event_attrs.get("msg", ""))[:500]
                        elif event_name == "llm.response":
                            response_text = str(event_attrs.get("msg", ""))[:500]
                        elif event_name == "gen_ai.client.inference.operation.details":
                            prompt_text = prompt_text or _format_messages(event_attrs.get("gen_ai.input.messages"))[:500]
                            response_text = response_text or _format_messages(event_attrs.get("gen_ai.output.messages"))[:500]
                    if not prompt_text:
                        prompt_text = _format_messages(attrs.get("input.value"))[:500]
                    if not response_text:
                        response_text = _format_messages(attrs.get("output.value"))[:500]
                llm_calls.append({
                    "name": name,
                    "trace_id": trace_id,
                    "span_id": span.get("span_id", ""),
                    "start_ns": span.get("start_ns", 0),
                    "duration_ms": span.get("duration_ms", 0),
                    "model": attrs.get("model", attrs.get("llm.model", attrs.get("llm.model_name", attrs.get("gen_ai.request.model", "")))),
                    "tokens_in": attrs.get("prompt_tokens", attrs.get("tokens_in", attrs.get("gen_ai.usage.input_tokens", attrs.get("llm.token_count.prompt", "")))),
                    "tokens_out": attrs.get("completion_tokens", attrs.get("tokens_out", attrs.get("gen_ai.usage.output_tokens", attrs.get("llm.token_count.completion", "")))),
                    "prompt_chars": attrs.get("prompt_chars", ""),
                    "completion_chars": attrs.get("completion_chars", ""),
                    "prompt": prompt_text,
                    "response": response_text,
                    "input_sha256": attrs.get("input.value_sha256", ""),
                    "output_sha256": attrs.get("output.value_sha256", ""),
                    "input_bytes": attrs.get("input.value_bytes", ""),
                    "output_bytes": attrs.get("output.value_bytes", ""),
                    "input_truncated": attrs.get("input.value_truncated", ""),
                    "output_truncated": attrs.get("output.value_truncated", ""),
                })

    llm_calls.sort(key=lambda c: c["start_ns"])
    return llm_calls


def run2llm(args: argparse.Namespace) -> None:
    """Show LLM calls for a specific run."""
    run_id = args.run_id
    service = args.service or default_service_name()
    start_s, end_s = resolve_time_range(args.since, args.start, args.end)
    llm_calls = collect_llm_calls(run_id, service, start_s, end_s, args.prompts)

    if not llm_calls:
        print("name\tduration_ms\tmodel\ttokens_in\ttokens_out\ttrace_id")
        print(f"No LLM calls found for run: {run_id}")
        print("LLM spans should have 'llm', 'chat', or 'completion' in name")
        return

    show_full = getattr(args, "full", False)
    show_logs = getattr(args, "logs", False)
    show_json = getattr(args, "json", False)
    show_prompt_preview = bool(getattr(args, "prompts", False))
    index_filter = getattr(args, "index", None)

    def _token_pair(call: Dict[str, Any]) -> tuple[str, str]:
        return call["tokens_in"] or "-", call["tokens_out"] or "-"

    def _prompt_preview(text: str) -> str:
        lines = text.split("\n")
        content_lines = [
            line for line in lines
            if not line.startswith("[") or not line.endswith("]")
        ]
        base = (content_lines[0] if content_lines else lines[0]) if lines else ""
        return base[:150]

    def _print_header(call: Dict[str, Any], idx: int, include_span: bool) -> None:
        print(f"=== LLM Call #{idx}: {call['name']} ({call['duration_ms']:.0f}ms) ===")
        print(f"Model: {call['model']}")
        if include_span:
            print(f"Span: {call['span_id']} Trace: {call['trace_id']}")
        tokens_in, tokens_out = _token_pair(call)
        print(f"Tokens: {tokens_in} in, {tokens_out} out")

    def _print_prompt_response(call: Dict[str, Any], prompt_label: str, response_label: str) -> None:
        if call.get("prompt"):
            print(f"{prompt_label}: {_prompt_preview(call['prompt'])}...")
        if call.get("response"):
            print(f"{response_label}: {call['response'].splitlines()[0][:150]}...")

    def _print_span_logs(call: Dict[str, Any]) -> None:
        print(f"=== Logs for Span {call['span_id']} ===")
        trace2logs(argparse.Namespace(
            trace_id=call["trace_id"],
            limit=50,
            since=args.since,
            service=service,
            span=call["span_id"],
            full=args.full,
        ))
        print()

    def _print_full_logs(call: Dict[str, Any]) -> bool:
        logs = fetch_span_logs(
            call["span_id"],
            service,
            start_s,
            end_s,
            trace_id=call.get("trace_id"),
        )
        llm_logs = [
            log for log in logs
            if "llm.prompt" in log["message"] or "llm.response" in log["message"]
        ]
        if not llm_logs:
            print("(no LLM logs found in logs backend)")
            print()
            return False
        for log in llm_logs:
            lines = log["message"].split("\n", 1)
            header = lines[0] if lines else ""
            content = lines[1] if len(lines) > 1 else ""
            kind = "PROMPT" if "llm.prompt" in log["message"] else "RESPONSE"
            print(f"--- {kind} ({header}) ---")
            print(content[:10000] if content else "(empty)")
            print()
        return True

    display_calls = llm_calls
    if index_filter is not None:
        if index_filter < 1 or index_filter > len(llm_calls):
            print(f"Index out of range: {index_filter} (1-{len(llm_calls)})")
            return
        display_calls = [llm_calls[index_filter - 1]]

    if show_json:
        output: List[Dict[str, Any]] = []
        for call in display_calls:
            entry = dict(call)
            if show_full:
                logs = fetch_span_logs(
                    call["span_id"],
                    service,
                    start_s,
                    end_s,
                    trace_id=call.get("trace_id"),
                )
                prompt_text = ""
                response_text = ""
                for log in logs:
                    if "llm.prompt" in log["message"]:
                        prompt_text = log["message"].split("\n", 1)[-1]
                    if "llm.response" in log["message"]:
                        response_text = log["message"].split("\n", 1)[-1]
                if prompt_text:
                    entry["prompt"] = prompt_text
                if response_text:
                    entry["response"] = response_text
            output.append(entry)
        print(json.dumps(output, indent=2))
        return

    if show_full:
        for i, call in enumerate(display_calls, 1):
            _print_header(call, i, include_span=False)
            print()
            if show_prompt_preview:
                _print_prompt_response(call, "Prompt (preview)", "Response (preview)")
                print()
            printed = _print_full_logs(call)
            if show_logs and printed:
                _print_span_logs(call)
    elif args.prompts:
        # Detailed view with prompts/responses (truncated from Tempo)
        for i, call in enumerate(display_calls, 1):
            _print_header(call, i, include_span=True)
            _print_prompt_response(call, "Prompt", "Response")
            print()
            if show_logs:
                _print_span_logs(call)
    else:
        print("name\tduration_ms\tmodel\ttokens_in\ttokens_out\ttrace_id\tspan_id")
        for call in display_calls:
            print(
                f"{call['name']}\t{call['duration_ms']:.0f}\t{call['model']}\t"
                f"{call['tokens_in'] or '-'}\t{call['tokens_out'] or '-'}\t"
                f"{call['trace_id']}\t{call['span_id']}"
            )
        if show_logs:
            for call in display_calls:
                _print_span_logs(call)

    print("Hint: bin/otel/cmds/run2llm --prompts (Tempo preview) | bin/otel/cmds/run2llm --full (logs backend)")

def inspect(args: argparse.Namespace) -> None:
    """Smart inspector that detects ID type and shows relevant details."""
    target = args.target
    svc = args.service or default_service_name()

    if getattr(args, "latest", False):
        rows = _collect_sessions(*resolve_time_range(args.since, None, None), svc, getattr(args, "limit", 50), None)
        if not rows:
            print("No sessions found.")
            return
        target = rows[0]["session_id"]
        print(f"=== Session {target} ===")
        session2runs(argparse.Namespace(
            session_id=target,
            since=args.since,
            start=None,
            end=None,
            service=svc,
            limit=getattr(args, "limit", 200),
        ))
        return

    if getattr(args, "sessions", False):
        list_sessions(argparse.Namespace(
            since=args.since,
            start=None,
            end=None,
            service=svc,
            limit=getattr(args, "limit", 200),
            query=None,
        ))
        return

    if getattr(args, "errors", False) and not target:
        rows = _collect_sessions(*resolve_time_range(args.since, None, None), svc, getattr(args, "limit", 50), None)
        error_rows = [row for row in rows if row.get("status") == "x"]
        if not error_rows:
            print("No error sessions found.")
            return
        print("session_id\ttime\tduration_s\truns\tstatus\tgit_sha\tgit_dirty")
        for row in error_rows:
            print(
                f"{row['session_id']}\t{row['time']}\t{row['duration_s']:.1f}\t"
                f"{row['runs']}\t{row['status']}\t{row['git_sha']}\t{row['git_dirty']}"
            )
        return

    if not target:
        print("=== Recent Traces ===")
        list_traces(argparse.Namespace(
            since=args.since, start=None, end=None, limit=5, query=None, service=svc
        ))
        print("Usage: inspect <trace_id|run_id|session_id|bots_run_id> [--prompts|--full|--logs|--errors]")
        return

    # Trace IDs are hex strings, run IDs have R_ prefix
    is_trace_id = len(target) == 32 and all(c in '0123456789abcdef' for c in target.lower())
    is_run_id = target.startswith("R_") or target.startswith("run_")
    is_session_id = is_uuid(target)
    is_bots_run = target.startswith("bots_")

    if is_trace_id:
        # It's a trace ID - show trace tree
        print(f"=== Trace {target} ===")
        if getattr(args, "errors", False):
            find_errors(argparse.Namespace(trace_id=target, match=args.match))
            return
        trace_args = argparse.Namespace(trace_id=target, match=args.match)
        trace2tree(trace_args)
        if getattr(args, "logs", False):
            trace2logs(argparse.Namespace(trace_id=target, limit=50, since=args.since))
        print("Hint: bin/otel/cmds/trace2tree | bin/otel/cmds/trace2logs")
        return

    if is_run_id:
        # It's a run ID - show LLM calls
        print(f"=== Run {target} ===")
        if getattr(args, "errors", False):
            start_s, end_s = resolve_time_range(args.since, None, None)
            calls = collect_llm_calls(target, svc, start_s, end_s, False)
            trace_ids = sorted({call["trace_id"] for call in calls if call.get("trace_id")})
            if not trace_ids:
                print(f"No traces found for run_id={target}")
                return
            for trace_id in trace_ids:
                print(f"--- Errors for trace {trace_id} ---")
                find_errors(argparse.Namespace(trace_id=trace_id, match=args.match))
            return
        run_args = argparse.Namespace(
            run_id=target, since=args.since, start=None, end=None,
            service=svc, prompts=args.prompts, full=args.full, logs=args.logs, json=False
        )
        run2llm(run_args)
        return

    if is_session_id:
        print(f"=== Session {target} ===")
        if getattr(args, "errors", False):
            start_s, end_s = resolve_time_range(args.since, None, None)
            runs = _collect_session_runs(target, start_s, end_s, svc, getattr(args, "limit", 200))
            error_runs = [
                item for item in runs
                if span_status_label(item.get("span", {})) == "x"
            ]
            if not error_runs:
                print("No error runs found.")
                return
            print("turn\trun_id\tdthread_id\tduration_ms\tagent\tstatus\ttrace_id")
            for idx, item in enumerate(error_runs, 1):
                span = item["span"]
                attrs = span.get("attrs", {}) or {}
                print(
                    f"{idx}\t{attrs.get('run.id','')}\t{attrs.get('dthread.id','')}\t"
                    f"{span.get('duration_ms',0.0):.0f}\t{attrs.get('agent','')}\t"
                    f"{span_status_label(span)}\t{item['trace_id']}"
                )
            print("Hint: bin/otel/cmds/find-errors <trace_id> for details")
            return
        session2runs(argparse.Namespace(
            session_id=target,
            since=args.since,
            start=None,
            end=None,
            service=svc,
            limit=getattr(args, "limit", 200),
        ))
        return

    if is_bots_run:
        print(f"=== Bots Run {target} ===")
        run_status(argparse.Namespace(
            run_id=target,
            since=args.since,
            start=None,
            end=None,
            limit=200,
            runner_service="bots-runner",
            client_service="bots-client",
            full=args.full,
            logs=args.logs,
        ))
        return

    print(f"Unknown target: {target}")
    print("Hint: use inspect --sessions/--latest or pass a trace_id/run_id/session_id/bots_run_id")



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Tempo helper scripts")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # Smart inspector
    inspect_parser = subparsers.add_parser("inspect", help="Smart inspector for trace/run IDs")
    inspect_parser.add_argument("target", nargs="?", help="Trace or run ID")
    add_time_range_args(inspect_parser, "1h", "Lookback window", include_start_end=False)
    add_service_arg(inspect_parser, "Service name")
    inspect_parser.add_argument("--match", help="Filter span names (for trace IDs)")
    inspect_parser.add_argument("--prompts", action="store_true", help="Show prompt/response (for run IDs)")
    inspect_parser.add_argument("--full", action="store_true", help="Show full prompt/response (from logs backend)")
    inspect_parser.add_argument("--logs", action="store_true", help="Show correlated logs (from logs backend)")
    inspect_parser.add_argument("--errors", action="store_true", help="Show error spans or filter sessions")
    inspect_parser.add_argument("--latest", action="store_true", help="Show latest session summary")
    inspect_parser.add_argument("--sessions", action="store_true", help="List recent sessions")
    add_limit_arg(inspect_parser, 200, "Max sessions to scan")
    status_parser = subparsers.add_parser("status", help="Check OTel stack and API configuration")
    status_parser.add_argument("--api", help="API base URL (default: .louie-ports or LOUIE_API_URL)")
    status_parser.add_argument("--token", help="Bearer token for /api/capabilities")
    status_parser.add_argument("--collector", help="OTel collector health URL")
    status_parser.add_argument("--json", action="store_true", help="Emit JSON output")

    r2l_parser = subparsers.add_parser("run2llm", help="Show LLM calls for a run")
    r2l_parser.add_argument("run_id", help="Run ID")
    add_time_range_args(r2l_parser, "1h", "Lookback window")
    add_service_arg(r2l_parser, "Service name")
    r2l_parser.add_argument("--prompts", action="store_true", help="Show prompt/response preview (from Tempo)")
    r2l_parser.add_argument("--full", action="store_true", help="Show full prompt/response (from logs backend)")
    r2l_parser.add_argument("--logs", action="store_true", help="Show correlated logs for each span")
    r2l_parser.add_argument("--json", action="store_true", help="Emit JSON output")
    r2l_parser.add_argument("--index", type=int, help="Select LLM call by 1-based index")

    run_status_parser = subparsers.add_parser("run-status", help="Show summary for a bots run id")
    run_status_parser.add_argument("run_id", help="Bots run ID (e.g., bots_20260114_164601)")
    add_time_range_args(run_status_parser, "30m", "Lookback window")
    add_limit_arg(run_status_parser, 200, "Max log lines to scan per service")
    run_status_parser.add_argument("--runner-service", default="bots-runner", help="Service name for runner logs")
    run_status_parser.add_argument("--client-service", default="bots-client", help="Service name for client logs")
    run_status_parser.add_argument("--full", action="store_true", help="Do not truncate log messages")
    run_status_parser.add_argument("--logs", action="store_true", help="Show raw logs instead of summary")

    # Trace-centric tools (existing)
    list_parser = subparsers.add_parser("list-traces", help="List recent traces")
    add_time_range_args(list_parser, "15m", "Lookback window (e.g., 15m, 2h, 900)", include_start_end=False)
    list_parser.add_argument("--start", help="Start time (epoch seconds or ISO)")
    list_parser.add_argument("--end", help="End time (epoch seconds or ISO)")
    add_limit_arg(list_parser, 20, "Max traces to return")
    list_parser.add_argument("--query", help="TraceQL query")
    add_service_arg(list_parser, "Service name for default query")

    sessions_parser = subparsers.add_parser("list-sessions", help="List recent sessions")
    add_time_range_args(sessions_parser, "30m", "Lookback window")
    add_limit_arg(sessions_parser, 200, "Max sessions to scan")
    add_service_arg(sessions_parser, "Service name for default query")
    sessions_parser.add_argument("--query", help="TraceQL query (defaults to api_run)")

    session_runs_parser = subparsers.add_parser("session2runs", help="List runs for a session id")
    session_runs_parser.add_argument("session_id", help="Session ID")
    add_time_range_args(session_runs_parser, "2h", "Lookback window")
    add_limit_arg(session_runs_parser, 200, "Max traces to scan")
    add_service_arg(session_runs_parser, "Service name for default query")

    tree_parser = subparsers.add_parser("trace2tree", help="Print trace as a tree")
    tree_parser.add_argument("trace_id", help="Trace ID")
    tree_parser.add_argument("--match", help="Regex or substring to filter span names")

    spans_parser = subparsers.add_parser("trace2spans", help="Print trace spans as table")
    spans_parser.add_argument("trace_id", help="Trace ID")
    spans_parser.add_argument("--match", help="Regex or substring to filter span names")

    events_parser = subparsers.add_parser("trace2events", help="Print span events")
    events_parser.add_argument("trace_id", help="Trace ID")
    events_parser.add_argument("--span", help="Span ID to filter events")
    events_parser.add_argument("--event", help="Event name filter (regex or substring)")
    events_parser.add_argument("--attrs", action="store_true", help="Include event attributes in output")

    logs_parser = subparsers.add_parser("trace2logs", help="Query logs backend by trace_id")
    logs_parser.add_argument("trace_id", help="Trace ID")
    add_limit_arg(logs_parser, 100, "Max log lines")
    add_time_range_args(logs_parser, "1h", "Lookback window (e.g., 1h, 30m)", include_start_end=False)
    add_service_arg(logs_parser, "Service name (default: OTEL_SERVICE_NAME)")
    logs_parser.add_argument("--span", help="Span ID to filter logs")
    logs_parser.add_argument("--full", action="store_true", help="Do not truncate log messages (escape newlines)")

    errors_parser = subparsers.add_parser("find-errors", help="List error spans in a trace")
    errors_parser.add_argument("trace_id", help="Trace ID")
    errors_parser.add_argument("--match", help="Regex or substring to filter span names")

    search_parser = subparsers.add_parser("search-logs", help="Search logs backend by text")
    add_service_arg(search_parser, "Service name (default: OTEL_SERVICE_NAME)")
    add_time_range_args(search_parser, "1h", "Lookback window")
    add_limit_arg(search_parser, 200, "Max log lines")
    search_parser.add_argument("--contains", required=True, help="Substring to match in logs")
    search_parser.add_argument("--full", action="store_true", help="Do not truncate log messages")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    cmd = args.cmd
    handlers = {
        "inspect": inspect,
        "status": status,
        "run2llm": run2llm,
        "run-status": run_status,
        "list-traces": list_traces,
        "list-sessions": list_sessions,
        "session2runs": session2runs,
        "trace2tree": trace2tree,
        "trace2spans": trace2spans,
        "trace2events": trace2events,
        "trace2logs": trace2logs,
        "find-errors": find_errors,
        "search-logs": search_logs,
    }
    handler = handlers.get(cmd)
    if not handler:
        parser.error(f"Unknown command: {cmd}")
    handler(args)


if __name__ == "__main__":
    main()
