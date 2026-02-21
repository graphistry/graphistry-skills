#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime as dt
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JOURNEY_DIR = ROOT / "evals" / "journeys"
DEFAULT_SKILLS_PROFILES = ROOT / "evals" / "skills_profiles.json"
DEFAULT_OTEL_DIR = ROOT / "bin" / "otel"
DEFAULT_OTEL_PY = DEFAULT_OTEL_DIR / "_python"
DEFAULT_OTEL_LOG_EVENT = DEFAULT_OTEL_DIR / "log_event.py"


def now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def shell_join(values: list[str]) -> str:
    return ",".join(v for v in values if v)


def run_git_rev_parse(arg: str) -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", arg], cwd=ROOT, text=True)
        return out.strip() or None
    except Exception:
        return None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def variant_key(harness: str, model: str = "") -> str:
    model_token = model if model else "default"
    return f"{harness}::{model_token}"


def resolve_harness_variants(
    harnesses: list[str],
    claude_models_csv: str,
    codex_models_csv: str,
) -> list[dict[str, str]]:
    claude_models = parse_csv(claude_models_csv)
    codex_models = parse_csv(codex_models_csv)
    variants: list[dict[str, str]] = []

    for harness in harnesses:
        if harness == "claude" and claude_models:
            for model in claude_models:
                variants.append({"harness": harness, "model": model})
            continue
        if harness == "codex" and codex_models:
            for model in codex_models:
                variants.append({"harness": harness, "model": model})
            continue
        variants.append({"harness": harness, "model": ""})

    return variants


def parse_skills_modes(value: str) -> list[str]:
    val = value.strip().lower()
    if val == "both":
        return ["off", "on"]
    modes = parse_csv(val)
    invalid = [m for m in modes if m not in {"on", "off"}]
    if invalid:
        raise ValueError(f"Invalid skills mode(s): {invalid}")
    return modes or ["off"]


def load_skills_profiles(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    payload = load_json(path)
    if not isinstance(payload, dict):
        return {}
    out: dict[str, list[str]] = {}
    for key, value in payload.items():
        if not isinstance(key, str):
            continue
        if isinstance(value, list):
            out[key] = [str(v) for v in value]
    return out


def resolve_skill_names(profile: str, profiles: dict[str, list[str]]) -> list[str]:
    if profile in profiles:
        return profiles[profile]
    return parse_csv(profile)


def summarize_skill_text(text: str, limit: int = 1200) -> str:
    body = text.strip()
    if len(body) <= limit:
        return body
    return body[: limit - 3] + "..."


def _clear_symlinks(path: Path) -> None:
    if not path.exists():
        return
    for child in path.iterdir():
        if child.is_symlink():
            child.unlink(missing_ok=True)


def prepare_native_skill_env(
    out_dir: Path,
    profile_name: str,
    mode_name: str,
    harness: str,
    skill_names: list[str],
) -> str:
    env_dir = out_dir / "native_env" / f"{profile_name}-{mode_name}-{harness}"
    env_dir.mkdir(parents=True, exist_ok=True)

    if harness == "claude":
        target_skills_dir = env_dir / ".claude" / "skills"
    elif harness == "codex":
        target_skills_dir = env_dir / ".codex" / "skills"
    else:
        return str(env_dir)

    target_skills_dir.mkdir(parents=True, exist_ok=True)
    _clear_symlinks(target_skills_dir)

    for skill in skill_names:
        src = ROOT / ".agents" / "skills" / skill
        if not (src / "SKILL.md").exists():
            continue
        dst = target_skills_dir / skill
        dst.unlink(missing_ok=True)
        dst.symlink_to(src, target_is_directory=True)

    return str(env_dir)


def prepare_codex_home(
    env_dir: Path,
    otel_enabled: bool = False,
    otel_endpoint: str = "",
) -> str:
    codex_home = env_dir / ".codex"
    codex_home.mkdir(parents=True, exist_ok=True)

    source_home = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
    try:
        if source_home.resolve() == codex_home.resolve():
            return str(codex_home)
    except Exception:
        pass

    for name in ("auth.json", "config.toml", "version.json"):
        src = source_home / name
        dst = codex_home / name
        if src.exists():
            shutil.copy2(src, dst)

    if otel_enabled:
        cfg_path = codex_home / "config.toml"
        cfg_text = cfg_path.read_text(encoding="utf-8") if cfg_path.exists() else ""
        if not re.search(r"(?m)^\[otel\]\s*$", cfg_text):
            endpoint = (otel_endpoint or "http://localhost:4317").strip()
            endpoint = endpoint.replace('"', '\\"')
            block = (
                "[otel]\n"
                'environment = "dev"\n'
                f'trace_exporter = {{ otlp-grpc = {{ endpoint = "{endpoint}" }} }}\n'
            )
            next_text = (cfg_text.rstrip() + "\n\n" + block) if cfg_text.strip() else block
            cfg_path.write_text(next_text, encoding="utf-8")

    return str(codex_home)


def spawn_codex_home_instance(
    base_codex_home: str,
    out_dir: Path,
    mode: str,
    instance_id: str,
) -> str:
    base = Path(base_codex_home)
    suffix = re.sub(r"[^A-Za-z0-9._-]", "_", instance_id)[:48] or uuid.uuid4().hex[:12]
    target = out_dir / "codex_home_instances" / f"{mode}-{suffix}"
    target.mkdir(parents=True, exist_ok=True)

    for name in ("auth.json", "config.toml", "version.json"):
        src = base / name
        dst = target / name
        if src.exists():
            shutil.copy2(src, dst)

    src_skills = base / "skills"
    dst_skills = target / "skills"
    if src_skills.exists():
        shutil.copytree(src_skills, dst_skills, dirs_exist_ok=True, symlinks=True)

    return str(target)


def materialize_skills(
    out_dir: Path,
    profile_name: str,
    skill_names: list[str],
    enabled: bool,
) -> dict[str, Any]:
    mode_name = "on" if enabled else "off"
    materialized_dir = out_dir / "effective_skills" / f"{profile_name}-{mode_name}"
    materialized_dir.mkdir(parents=True, exist_ok=True)

    manifest_entries: list[dict[str, str]] = []
    prompt_blocks: list[str] = []

    if not enabled:
        return {
            "skills_enabled": False,
            "skills_profile": profile_name,
            "skills_manifest": manifest_entries,
            "skills_prompt_text": "",
            "skills_dir": str(materialized_dir),
        }

    for skill in skill_names:
        src = ROOT / ".agents" / "skills" / skill / "SKILL.md"
        if not src.exists():
            manifest_entries.append({
                "skill": skill,
                "path": str(src),
                "sha256": "missing",
            })
            continue

        raw = read_text(src)
        sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        dst = materialized_dir / skill / "SKILL.md"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        manifest_entries.append({
            "skill": skill,
            "path": str(src),
            "sha256": sha,
        })

        prompt_blocks.append(
            f"[skill:{skill}]\n{summarize_skill_text(raw)}"
        )

    prompt_text = "\n\n".join(prompt_blocks)
    return {
        "skills_enabled": True,
        "skills_profile": profile_name,
        "skills_manifest": manifest_entries,
        "skills_prompt_text": prompt_text,
        "skills_dir": str(materialized_dir),
    }


def load_journey(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid journey file: {path}")
    if "id" not in payload or "cases" not in payload:
        raise ValueError(f"Journey missing required keys id/cases: {path}")
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ValueError(f"Journey cases must be a list: {path}")
    return payload


def resolve_journey_files(journey_dir: Path, selection: str) -> list[Path]:
    if selection == "all":
        files = sorted(journey_dir.glob("*.json"))
        if not files:
            raise ValueError(f"No journey files found in {journey_dir}")
        return files

    out: list[Path] = []
    for token in parse_csv(selection):
        maybe_path = Path(token)
        if maybe_path.is_file():
            out.append(maybe_path.resolve())
            continue
        candidate = journey_dir / f"{token}.json"
        if not candidate.exists():
            raise ValueError(f"Journey not found: {token} ({candidate})")
        out.append(candidate)
    return out


def make_traceparent() -> tuple[str, str]:
    trace_id = uuid.uuid4().hex
    span_id = f"{random.getrandbits(64):016x}"
    traceparent = f"00-{trace_id}-{span_id}-01"
    return traceparent, trace_id


def emit_otel_event(
    enabled: bool,
    event_name: str,
    attrs: dict[str, Any],
    service: str,
    endpoint: str | None,
) -> None:
    if not enabled:
        return

    py_cmd = Path(os.environ.get("AGENT_EVAL_OTEL_PY", str(DEFAULT_OTEL_PY)))
    log_script = Path(os.environ.get("AGENT_EVAL_OTEL_LOG_EVENT", str(DEFAULT_OTEL_LOG_EVENT)))
    if not py_cmd.exists() or not log_script.exists():
        return

    cmd = [str(py_cmd), str(log_script), event_name, "--service", service]
    if endpoint:
        cmd.extend(["--endpoint", endpoint])

    for key, value in attrs.items():
        cmd.extend(["--attr", f"{key}={value}"])

    subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_harness(
    harness: str,
    prompt: str,
    out_dir: Path,
    traceparent: str,
    timeout_s: int,
    louie_url: str,
    skills_text: str,
    model: str = "",
    harness_cwd: str = "",
    harness_env: dict[str, str] | None = None,
) -> dict[str, Any]:
    harness_script = ROOT / "bin" / "harness" / f"{harness}.sh"
    if not harness_script.exists():
        return {
            "ok": False,
            "harness": harness,
            "error": f"Harness script not found: {harness_script}",
            "response_text": "",
            "latency_ms": 0,
        }

    stamp = int(time.time() * 1000)
    safe = f"{harness}-{stamp}-{uuid.uuid4().hex[:8]}"
    prompt_file = out_dir / "raw" / f"{safe}.prompt.txt"
    skills_file = out_dir / "raw" / f"{safe}.skills.txt"
    raw_out = out_dir / "raw" / f"{safe}.log"

    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(prompt, encoding="utf-8")
    skills_file.write_text(skills_text, encoding="utf-8")

    cmd = [
        str(harness_script),
        "--prompt-file",
        str(prompt_file),
        "--skills-text-file",
        str(skills_file),
        "--raw-out",
        str(raw_out),
        "--traceparent",
        traceparent,
        "--timeout-s",
        str(timeout_s),
        "--louie-url",
        louie_url,
    ]
    if harness_cwd and harness in {"claude", "codex"}:
        cmd.extend(["--cd", harness_cwd])
    if model and harness in {"claude", "codex"}:
        cmd.extend(["--model", model])

    started = time.time()
    try:
        child_env = os.environ.copy()
        if harness_env:
            child_env.update(harness_env)
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            env=child_env,
            capture_output=True,
            text=True,
            timeout=timeout_s + 10,
        )
        elapsed_ms = int((time.time() - started) * 1000)
    except subprocess.TimeoutExpired as exc:
        elapsed_ms = int((time.time() - started) * 1000)
        return {
            "ok": False,
            "harness": harness,
            "error": f"Harness process timeout after {timeout_s + 10}s",
            "response_text": "",
            "latency_ms": elapsed_ms,
            "raw_ref": str(raw_out),
            "stdout_tail": (exc.stdout or "")[-2000:],
            "stderr_tail": (exc.stderr or "")[-2000:],
            "command_exit_code": None,
        }

    payload: dict[str, Any] | None = None
    stdout = proc.stdout.strip()
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
            if isinstance(parsed, dict):
                payload = parsed
                break
        except Exception:
            continue

    if payload is None:
        payload = {
            "ok": False,
            "harness": harness,
            "error": "Harness did not emit JSON payload",
            "response_text": "",
            "latency_ms": elapsed_ms,
            "stdout_tail": stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
            "raw_ref": str(raw_out),
        }

    payload.setdefault("harness", harness)
    payload.setdefault("latency_ms", elapsed_ms)
    payload.setdefault("response_text", "")
    payload.setdefault("raw_ref", str(raw_out))
    payload["command_exit_code"] = proc.returncode

    if proc.returncode != 0 and payload.get("ok") is True:
        payload["ok"] = False
        payload["error"] = f"Harness command exited with code {proc.returncode}"

    return payload


def grade_response(response_text: str, checks: dict[str, Any]) -> tuple[bool, float, dict[str, Any]]:
    details: dict[str, Any] = {
        "must_contain": [],
        "must_not_contain": [],
        "regex": [],
        "must_not_regex": [],
        "max_lines": [],
        "min_lines": [],
        "python_block": [],
        "python_ast_parse": [],
        "python_ast_calls": [],
        "python_ast_call_kwargs": [],
    }

    total = 0
    passed = 0

    def content_line_count(text: str) -> int:
        lines = []
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            # Ignore markdown code fences when applying line-count guardrails.
            if line.startswith("```"):
                continue
            lines.append(line)
        return len(lines)

    def extract_code_blocks(text: str, language: str | None = None) -> list[str]:
        pattern: re.Pattern[str]
        if language:
            pattern = re.compile(rf"```{re.escape(language)}\s*\n(.*?)```", re.IGNORECASE | re.DOTALL)
        else:
            pattern = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
        return [m.group(1).strip() for m in pattern.finditer(text) if m.group(1).strip()]

    python_blocks = extract_code_blocks(response_text, "python") + extract_code_blocks(response_text, "py")
    if not python_blocks:
        python_blocks = extract_code_blocks(response_text)
    python_source = python_blocks[0] if python_blocks else ""
    parsed_tree: ast.AST | None = None
    parsed_error: str | None = None

    def ensure_parsed() -> bool:
        nonlocal parsed_tree, parsed_error
        if parsed_tree is not None:
            return True
        if parsed_error is not None:
            return False
        if not python_source.strip():
            parsed_error = "No code block found for AST parsing"
            return False
        try:
            parsed_tree = ast.parse(python_source)
            return True
        except SyntaxError as exc:
            parsed_error = str(exc)
            return False

    def call_name(call_node: ast.Call) -> str | None:
        func = call_node.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return None

    def node_value(node: ast.AST) -> Any:
        try:
            return ast.literal_eval(node)
        except Exception:
            if isinstance(node, ast.Name) and node.id in {"True", "False", "None"}:
                return {"True": True, "False": False, "None": None}[node.id]
            if hasattr(ast, "unparse"):
                try:
                    return ast.unparse(node)
                except Exception:
                    return None
            return None

    must_contain = checks.get("must_contain") or []
    if isinstance(must_contain, list):
        for item in must_contain:
            total += 1
            expected = str(item)
            ok = expected in response_text
            details["must_contain"].append({"value": expected, "ok": ok})
            if ok:
                passed += 1

    must_not_contain = checks.get("must_not_contain") or []
    if isinstance(must_not_contain, list):
        for item in must_not_contain:
            total += 1
            blocked = str(item)
            ok = blocked not in response_text
            details["must_not_contain"].append({"value": blocked, "ok": ok})
            if ok:
                passed += 1

    regex_checks = checks.get("regex") or []
    if isinstance(regex_checks, list):
        for item in regex_checks:
            total += 1
            pattern = str(item)
            ok = False
            error = None
            try:
                ok = re.search(pattern, response_text) is not None
            except re.error as exc:
                error = str(exc)
                ok = False
            details["regex"].append({"value": pattern, "ok": ok, "error": error})
            if ok:
                passed += 1

    must_not_regex = checks.get("must_not_regex") or []
    if isinstance(must_not_regex, list):
        for item in must_not_regex:
            total += 1
            pattern = str(item)
            ok = False
            error = None
            try:
                ok = re.search(pattern, response_text) is None
            except re.error as exc:
                error = str(exc)
                ok = False
            details["must_not_regex"].append({"value": pattern, "ok": ok, "error": error})
            if ok:
                passed += 1

    python_block_required = checks.get("python_block")
    if python_block_required is True:
        total += 1
        ok = bool(python_source.strip())
        details["python_block"].append({"required": True, "ok": ok})
        if ok:
            passed += 1

    python_ast_parse_required = checks.get("python_ast_parse")
    if python_ast_parse_required is True:
        total += 1
        ok = ensure_parsed()
        details["python_ast_parse"].append({"required": True, "ok": ok, "error": parsed_error})
        if ok:
            passed += 1

    python_ast_calls = checks.get("python_ast_calls") or []
    if isinstance(python_ast_calls, list):
        call_names: set[str] = set()
        parsed_ok = ensure_parsed()
        if parsed_ok and parsed_tree is not None:
            for node in ast.walk(parsed_tree):
                if isinstance(node, ast.Call):
                    name = call_name(node)
                    if name:
                        call_names.add(name)
        for item in python_ast_calls:
            total += 1
            expected = str(item)
            ok = parsed_ok and expected in call_names
            details["python_ast_calls"].append({
                "value": expected,
                "ok": ok,
                "error": parsed_error if not parsed_ok else None,
            })
            if ok:
                passed += 1

    python_ast_call_kwargs = checks.get("python_ast_call_kwargs") or []
    if isinstance(python_ast_call_kwargs, list):
        parsed_ok = ensure_parsed()
        call_nodes: list[ast.Call] = []
        if parsed_ok and parsed_tree is not None:
            call_nodes = [node for node in ast.walk(parsed_tree) if isinstance(node, ast.Call)]

        sentinel = object()
        for item in python_ast_call_kwargs:
            total += 1
            spec = item if isinstance(item, dict) else {}
            call_expected = str(spec.get("call") or "")
            kw_expected = str(spec.get("kw") or "")
            value_expected = spec.get("value", sentinel)
            ok = False
            observed_values: list[Any] = []
            if parsed_ok:
                for call in call_nodes:
                    if call_expected and call_name(call) != call_expected:
                        continue
                    for kw in call.keywords:
                        if kw.arg != kw_expected:
                            continue
                        observed = node_value(kw.value)
                        observed_values.append(observed)
                        if value_expected is sentinel:
                            ok = True
                        elif observed == value_expected:
                            ok = True
                    if ok:
                        break
            details["python_ast_call_kwargs"].append({
                "call": call_expected,
                "kw": kw_expected,
                "value": None if value_expected is sentinel else value_expected,
                "observed": observed_values,
                "ok": ok,
                "error": parsed_error if not parsed_ok else None,
            })
            if ok:
                passed += 1

    max_lines_raw = checks.get("max_lines")
    if isinstance(max_lines_raw, int) and max_lines_raw >= 0:
        total += 1
        non_empty_line_count = content_line_count(response_text)
        ok = non_empty_line_count <= max_lines_raw
        details["max_lines"].append({
            "value": max_lines_raw,
            "line_count": non_empty_line_count,
            "ok": ok,
        })
        if ok:
            passed += 1

    min_lines_raw = checks.get("min_lines")
    if isinstance(min_lines_raw, int) and min_lines_raw >= 0:
        total += 1
        non_empty_line_count = content_line_count(response_text)
        ok = non_empty_line_count >= min_lines_raw
        details["min_lines"].append({
            "value": min_lines_raw,
            "line_count": non_empty_line_count,
            "ok": ok,
        })
        if ok:
            passed += 1

    if total == 0:
        ok = bool(response_text.strip())
        score = 1.0 if ok else 0.0
        return ok, score, details

    score = passed / total
    return passed == total, score, details


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_harness: dict[str, dict[str, Any]] = {}
    by_harness_and_model: dict[str, dict[str, Any]] = {}
    by_skills_mode: dict[str, dict[str, Any]] = {}
    by_harness_and_mode: dict[str, dict[str, Any]] = {}
    by_harness_model_and_mode: dict[str, dict[str, Any]] = {}
    by_eval_intent: dict[str, dict[str, Any]] = {}

    for row in rows:
        harness = str(row.get("harness"))
        model = str(row.get("model") or "")
        skills_mode = str(row.get("skills_mode"))
        eval_intent = str(row.get("eval_intent") or "unspecified")

        if harness not in by_harness:
            by_harness[harness] = {
                "total": 0,
                "passed": 0,
                "scores": [],
                "latency_ms": [],
                "harness_ok": 0,
            }

        if skills_mode not in by_skills_mode:
            by_skills_mode[skills_mode] = {
                "total": 0,
                "passed": 0,
                "scores": [],
                "latency_ms": [],
                "harness_ok": 0,
            }

        if eval_intent not in by_eval_intent:
            by_eval_intent[eval_intent] = {
                "eval_intent": eval_intent,
                "total": 0,
                "passed": 0,
                "scores": [],
                "latency_ms": [],
                "harness_ok": 0,
            }

        harness_model_key = variant_key(harness, model)
        if harness_model_key not in by_harness_and_model:
            by_harness_and_model[harness_model_key] = {
                "harness": harness,
                "model": model if model else "default",
                "total": 0,
                "passed": 0,
                "scores": [],
                "latency_ms": [],
                "harness_ok": 0,
            }

        harness_mode_key = f"{harness}::{skills_mode}"
        if harness_mode_key not in by_harness_and_mode:
            by_harness_and_mode[harness_mode_key] = {
                "harness": harness,
                "skills_mode": skills_mode,
                "total": 0,
                "passed": 0,
                "scores": [],
                "latency_ms": [],
                "harness_ok": 0,
            }

        harness_model_mode_key = f"{variant_key(harness, model)}::{skills_mode}"
        if harness_model_mode_key not in by_harness_model_and_mode:
            by_harness_model_and_mode[harness_model_mode_key] = {
                "harness": harness,
                "model": model if model else "default",
                "skills_mode": skills_mode,
                "total": 0,
                "passed": 0,
                "scores": [],
                "latency_ms": [],
                "harness_ok": 0,
            }

        bucket = by_harness[harness]
        bucket["total"] += 1
        if bool(row.get("pass_bool")):
            bucket["passed"] += 1
        if bool(row.get("harness_ok")):
            bucket["harness_ok"] += 1
        bucket["scores"].append(float(row.get("score", 0.0)))
        bucket["latency_ms"].append(int(row.get("latency_ms", 0)))

        bucket_mode = by_skills_mode[skills_mode]
        bucket_mode["total"] += 1
        if bool(row.get("pass_bool")):
            bucket_mode["passed"] += 1
        if bool(row.get("harness_ok")):
            bucket_mode["harness_ok"] += 1
        bucket_mode["scores"].append(float(row.get("score", 0.0)))
        bucket_mode["latency_ms"].append(int(row.get("latency_ms", 0)))

        bucket_intent = by_eval_intent[eval_intent]
        bucket_intent["total"] += 1
        if bool(row.get("pass_bool")):
            bucket_intent["passed"] += 1
        if bool(row.get("harness_ok")):
            bucket_intent["harness_ok"] += 1
        bucket_intent["scores"].append(float(row.get("score", 0.0)))
        bucket_intent["latency_ms"].append(int(row.get("latency_ms", 0)))

        bucket_hm_model = by_harness_and_model[harness_model_key]
        bucket_hm_model["total"] += 1
        if bool(row.get("pass_bool")):
            bucket_hm_model["passed"] += 1
        if bool(row.get("harness_ok")):
            bucket_hm_model["harness_ok"] += 1
        bucket_hm_model["scores"].append(float(row.get("score", 0.0)))
        bucket_hm_model["latency_ms"].append(int(row.get("latency_ms", 0)))

        bucket_hm = by_harness_and_mode[harness_mode_key]
        bucket_hm["total"] += 1
        if bool(row.get("pass_bool")):
            bucket_hm["passed"] += 1
        if bool(row.get("harness_ok")):
            bucket_hm["harness_ok"] += 1
        bucket_hm["scores"].append(float(row.get("score", 0.0)))
        bucket_hm["latency_ms"].append(int(row.get("latency_ms", 0)))

        bucket_hmm = by_harness_model_and_mode[harness_model_mode_key]
        bucket_hmm["total"] += 1
        if bool(row.get("pass_bool")):
            bucket_hmm["passed"] += 1
        if bool(row.get("harness_ok")):
            bucket_hmm["harness_ok"] += 1
        bucket_hmm["scores"].append(float(row.get("score", 0.0)))
        bucket_hmm["latency_ms"].append(int(row.get("latency_ms", 0)))

    def finalize_bucket(bucket: dict[str, Any]) -> None:
        total = bucket["total"]
        bucket["pass_rate"] = (bucket["passed"] / total) if total else 0.0
        bucket["harness_ok_rate"] = (bucket["harness_ok"] / total) if total else 0.0
        scores = bucket.pop("scores", [])
        lats = bucket.pop("latency_ms", [])
        bucket["avg_score"] = (sum(scores) / len(scores)) if scores else 0.0
        bucket["avg_latency_ms"] = int(sum(lats) / len(lats)) if lats else 0

    for bucket in by_harness.values():
        finalize_bucket(bucket)

    for bucket in by_skills_mode.values():
        finalize_bucket(bucket)

    for bucket in by_harness_and_model.values():
        finalize_bucket(bucket)

    for bucket in by_harness_and_mode.values():
        finalize_bucket(bucket)

    for bucket in by_harness_model_and_mode.values():
        finalize_bucket(bucket)

    for bucket in by_eval_intent.values():
        finalize_bucket(bucket)

    total_all = len(rows)
    passed_all = sum(1 for row in rows if bool(row.get("pass_bool")))
    harness_ok_all = sum(1 for row in rows if bool(row.get("harness_ok")))

    return {
        "total_rows": total_all,
        "passed_rows": passed_all,
        "overall_pass_rate": (passed_all / total_all) if total_all else 0.0,
        "harness_ok_rows": harness_ok_all,
        "harness_ok_rate": (harness_ok_all / total_all) if total_all else 0.0,
        "by_harness": by_harness,
        "by_harness_and_model": by_harness_and_model,
        "by_skills_mode": by_skills_mode,
        "by_harness_and_mode": by_harness_and_mode,
        "by_harness_model_and_mode": by_harness_model_and_mode,
        "by_eval_intent": by_eval_intent,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run eval loops across codex/claude/louie harnesses")
    parser.add_argument("--journeys", default="runtime_smoke", help="CSV of journey IDs or 'all'")
    parser.add_argument("--journey-dir", default=str(DEFAULT_JOURNEY_DIR), help="Journey JSON directory")
    parser.add_argument("--harnesses", default="codex,claude,louie", help="CSV harness list")
    parser.add_argument("--case-ids", default="", help="CSV case IDs filter (optional)")
    parser.add_argument("--skills-mode", default="off", help="on|off|both|CSV")
    parser.add_argument("--skills-profile", default="pygraphistry_core", help="Skills profile name or CSV of skill names")
    parser.add_argument("--skills-profiles-file", default=str(DEFAULT_SKILLS_PROFILES), help="Skills profiles JSON")
    parser.add_argument("--out", default="", help="Output run directory")
    parser.add_argument("--otel", action="store_true", help="Emit OTel lifecycle logs")
    parser.add_argument("--failfast", action="store_true", help="Fail fast per harness after first harness error; includes Louie preflight")
    parser.add_argument("--otel-service", default="agent-eval-runner", help="OTel service name for lifecycle events")
    parser.add_argument("--otel-endpoint", default=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT_GRPC", ""), help="OTLP gRPC endpoint")
    parser.add_argument("--louie-url", default=os.environ.get("LOUIE_URL", "http://localhost:8501"), help="Louie server URL")
    parser.add_argument("--claude-cwd", default="", help="Working directory for claude harness (for native .claude/skills env tests)")
    parser.add_argument("--codex-cwd", default="", help="Working directory for codex harness (for native .codex/skills env tests)")
    parser.add_argument("--claude-models", default="", help="CSV model list for claude harness (optional)")
    parser.add_argument("--codex-models", default="", help="CSV model list for codex harness (optional)")
    parser.add_argument(
        "--skills-delivery",
        default="native",
        choices=["native", "inject", "auto"],
        help="How skills are provided to harnesses: native (default), inject, or auto (native for codex/claude + inject for others)",
    )
    parser.add_argument("--timeout-s", type=int, default=240, help="Timeout for each harness invocation")
    parser.add_argument("--max-workers", type=int, default=1, help="Max parallel harness workers per case (>=1)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    harnesses = parse_csv(args.harnesses)
    if not harnesses:
        raise ValueError("At least one harness is required")
    harness_variants = resolve_harness_variants(
        harnesses=harnesses,
        claude_models_csv=args.claude_models,
        codex_models_csv=args.codex_models,
    )

    modes = parse_skills_modes(args.skills_mode)
    max_workers = max(1, args.max_workers)

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"agent_eval_{timestamp}"
    out_dir = Path(args.out) if args.out else (ROOT / "runs" / run_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    profiles = load_skills_profiles(Path(args.skills_profiles_file))
    profile_name = args.skills_profile
    skill_names = resolve_skill_names(profile_name, profiles)

    skill_configs: dict[str, dict[str, Any]] = {}
    for mode in modes:
        skill_configs[mode] = materialize_skills(
            out_dir=out_dir,
            profile_name=profile_name,
            skill_names=skill_names,
            enabled=(mode == "on"),
        )

    journey_files = resolve_journey_files(Path(args.journey_dir), args.journeys)
    journeys = [load_journey(path) for path in journey_files]

    case_filter = set(parse_csv(args.case_ids))
    if case_filter:
        filtered_journeys: list[dict[str, Any]] = []
        matched_case_ids: set[str] = set()
        for journey in journeys:
            original_cases = journey.get("cases") or []
            kept_cases = []
            for case in original_cases:
                case_id = str(case.get("id") or "")
                if case_id in case_filter:
                    kept_cases.append(case)
                    matched_case_ids.add(case_id)
            if kept_cases:
                next_journey = dict(journey)
                next_journey["cases"] = kept_cases
                filtered_journeys.append(next_journey)

        missing = sorted(case_filter - matched_case_ids)
        if missing:
            print(f"WARN: case IDs not found and skipped: {','.join(missing)}", file=sys.stderr)

        if not filtered_journeys:
            raise ValueError(f"No cases matched --case-ids: {args.case_ids}")
        journeys = filtered_journeys

    git_sha = run_git_rev_parse("HEAD")
    git_branch = run_git_rev_parse("--abbrev-ref")

    manifest = {
        "run_id": run_id,
        "created_at": now_iso(),
        "cwd": str(ROOT),
        "git_sha": git_sha,
        "git_branch": git_branch,
        "harnesses": harnesses,
        "harness_variants": harness_variants,
        "journeys": [j.get("id") for j in journeys],
        "case_ids_filter": sorted(case_filter),
        "skills_mode": modes,
        "skills_profile": profile_name,
        "skills": {mode: cfg.get("skills_manifest", []) for mode, cfg in skill_configs.items()},
        "otel_enabled": bool(args.otel),
        "failfast": bool(args.failfast),
        "otel_service": args.otel_service,
        "otel_endpoint": args.otel_endpoint,
        "louie_url": args.louie_url,
        "claude_cwd": args.claude_cwd,
        "codex_cwd": args.codex_cwd,
        "claude_models": parse_csv(args.claude_models),
        "codex_models": parse_csv(args.codex_models),
        "skills_delivery": args.skills_delivery,
        "timeout_s": args.timeout_s,
        "max_workers": max_workers,
    }

    native_envs: dict[str, dict[str, str]] = {mode: {} for mode in modes}
    codex_homes: dict[str, str] = {}
    for mode in modes:
        for h in harnesses:
            if h in {"claude", "codex"}:
                native_envs[mode][h] = prepare_native_skill_env(
                    out_dir=out_dir,
                    profile_name=profile_name,
                    mode_name=mode,
                    harness=h,
                    skill_names=skill_names if mode == "on" else [],
                )
                if h == "codex":
                    codex_homes[mode] = prepare_codex_home(
                        Path(native_envs[mode][h]),
                        otel_enabled=bool(args.otel),
                        otel_endpoint=args.otel_endpoint or "http://localhost:4317",
                    )
    manifest["native_envs"] = native_envs
    manifest["codex_homes"] = codex_homes

    failed_harnesses: dict[str, str] = {}
    preflight_results: dict[str, Any] = {}

    # Louie commonly fails with endpoint timeout when unavailable.
    # In failfast mode, run one short preflight and skip remaining Louie rows if it fails.
    if args.failfast and "louie" in harnesses:
        preflight_timeout = max(5, min(args.timeout_s, 20))
        pre_traceparent, _ = make_traceparent()
        pre_result = run_harness(
            harness="louie",
            prompt="Reply with exactly GRAPHISTRY_OK.",
            out_dir=out_dir,
            traceparent=pre_traceparent,
            timeout_s=preflight_timeout,
            louie_url=args.louie_url,
            skills_text="",
            harness_cwd="",
        )
        preflight_results["louie"] = {
            "ok": bool(pre_result.get("ok")),
            "error": pre_result.get("error"),
            "latency_ms": int(pre_result.get("latency_ms") or 0),
            "timeout_s": preflight_timeout,
            "raw_ref": pre_result.get("raw_ref"),
        }
        if not bool(pre_result.get("ok")):
            failed_harnesses[variant_key("louie", "")] = (
                f"preflight_failed: {pre_result.get('error') or 'unknown error'}"
            )

    manifest["preflight"] = preflight_results

    emit_otel_event(
        enabled=args.otel,
        event_name="agent_eval.run.start",
        attrs={
            "agent_eval.run_id": run_id,
            "agent_eval.harnesses": shell_join(harnesses),
            "agent_eval.harness_variants": shell_join(
                [variant_key(str(v.get("harness") or ""), str(v.get("model") or "")) for v in harness_variants]
            ),
            "agent_eval.journeys": shell_join([str(j.get("id")) for j in journeys]),
        },
        service=args.otel_service,
        endpoint=args.otel_endpoint or None,
    )

    rows: list[dict[str, Any]] = []
    rows_path = out_dir / "rows.jsonl"

    with rows_path.open("w", encoding="utf-8") as rows_file:
        for journey in journeys:
            journey_id = str(journey.get("id"))
            journey_intent = str(journey.get("eval_intent") or "unspecified")
            journey_cases = journey.get("cases") or []

            emit_otel_event(
                enabled=args.otel,
                event_name="agent_eval.journey.start",
                attrs={
                    "agent_eval.run_id": run_id,
                    "agent_eval.journey_id": journey_id,
                },
                service=args.otel_service,
                endpoint=args.otel_endpoint or None,
            )

            for case in journey_cases:
                case_id = str(case.get("id") or f"case_{len(rows) + 1}")
                prompt = str(case.get("prompt") or "").strip()
                checks = case.get("checks") if isinstance(case.get("checks"), dict) else {}

                for mode in modes:
                    skills_cfg = skill_configs[mode]
                    skills_text = str(skills_cfg.get("skills_prompt_text", ""))

                    emit_otel_event(
                        enabled=args.otel,
                        event_name="agent_eval.skills.load.start",
                        attrs={
                            "agent_eval.run_id": run_id,
                            "agent_eval.journey_id": journey_id,
                            "agent_eval.case_id": case_id,
                            "agent_eval.skills_enabled": skills_cfg.get("skills_enabled"),
                            "agent_eval.skills_profile": profile_name,
                        },
                        service=args.otel_service,
                        endpoint=args.otel_endpoint or None,
                    )

                    emit_otel_event(
                        enabled=args.otel,
                        event_name="agent_eval.skills.load.success",
                        attrs={
                            "agent_eval.run_id": run_id,
                            "agent_eval.journey_id": journey_id,
                            "agent_eval.case_id": case_id,
                            "agent_eval.skills_enabled": skills_cfg.get("skills_enabled"),
                            "agent_eval.skills_profile": profile_name,
                        },
                        service=args.otel_service,
                        endpoint=args.otel_endpoint or None,
                    )

                    def run_case_for_harness(harness_idx: int, harness_variant: dict[str, str]) -> dict[str, Any]:
                        harness = str(harness_variant.get("harness") or "")
                        model = str(harness_variant.get("model") or "")
                        hkey = variant_key(harness, model)
                        traceparent, trace_id = make_traceparent()

                        emit_otel_event(
                            enabled=args.otel,
                            event_name="agent_eval.case.start",
                            attrs={
                                "agent_eval.run_id": run_id,
                                "agent_eval.harness": harness,
                                "agent_eval.model": model if model else "default",
                                "agent_eval.journey_id": journey_id,
                                "agent_eval.case_id": case_id,
                                "agent_eval.skills_enabled": skills_cfg.get("skills_enabled"),
                                "agent_eval.trace_id": trace_id,
                            },
                            service=args.otel_service,
                            endpoint=args.otel_endpoint or None,
                        )

                        if args.failfast and hkey in failed_harnesses:
                            result = {
                                "ok": False,
                                "harness": harness,
                                "error": f"failfast_skip: {failed_harnesses[hkey]}",
                                "response_text": "",
                                "latency_ms": 0,
                                "raw_ref": None,
                                "command_exit_code": None,
                            }
                        else:
                            harness_cwd = ""
                            harness_env: dict[str, str] = {}
                            if harness == "claude" and args.claude_cwd:
                                harness_cwd = args.claude_cwd
                            elif harness == "codex" and args.codex_cwd:
                                harness_cwd = args.codex_cwd

                            deliver = args.skills_delivery
                            skills_text_for_harness = ""
                            if deliver == "inject":
                                if mode == "on":
                                    skills_text_for_harness = skills_text
                            elif deliver in {"native", "auto"}:
                                if harness in {"claude", "codex"}:
                                    if not harness_cwd:
                                        harness_cwd = native_envs.get(mode, {}).get(harness, "")
                                elif mode == "on" and deliver == "auto":
                                    skills_text_for_harness = skills_text

                            if harness == "codex" and not args.codex_cwd:
                                codex_home_base = codex_homes.get(mode, "")
                                if codex_home_base:
                                    codex_home = codex_home_base
                                    if max_workers > 1:
                                        codex_home = spawn_codex_home_instance(
                                            base_codex_home=codex_home_base,
                                            out_dir=out_dir,
                                            mode=mode,
                                            instance_id=f"{journey_id}-{case_id}-{harness_idx}-{uuid.uuid4().hex[:8]}",
                                        )
                                    harness_env["CODEX_HOME"] = codex_home

                            result = run_harness(
                                harness=harness,
                                prompt=prompt,
                                out_dir=out_dir,
                                traceparent=traceparent,
                                timeout_s=args.timeout_s,
                                louie_url=args.louie_url,
                                skills_text=skills_text_for_harness,
                                model=model,
                                harness_cwd=harness_cwd,
                                harness_env=harness_env,
                            )

                        response_text = str(result.get("response_text") or "")
                        pass_bool, score, breakdown = grade_response(response_text, checks)

                        row = {
                            "run_id": run_id,
                            "timestamp": now_iso(),
                            "journey_id": journey_id,
                            "eval_intent": journey_intent,
                            "case_id": case_id,
                            "case_prompt": prompt,
                            "harness": harness,
                            "model": model if model else "default",
                            "skills_mode": mode,
                            "skills_enabled": bool(skills_cfg.get("skills_enabled")),
                            "skills_profile": profile_name,
                            "trace_id": trace_id,
                            "traceparent": traceparent,
                            "harness_ok": bool(result.get("ok")),
                            "harness_error": result.get("error"),
                            "response_text": response_text,
                            "pass_bool": pass_bool,
                            "score": score,
                            "check_breakdown": breakdown,
                            "latency_ms": int(result.get("latency_ms") or 0),
                            "raw_ref": result.get("raw_ref"),
                            "runtime_ids": {
                                "session_id": result.get("session_id"),
                                "thread_id": result.get("thread_id"),
                                "louie_run_id": result.get("run_id"),
                                "dthread_id": result.get("dthread_id"),
                            },
                            "usage": result.get("usage", {}),
                            "selected_harness": result.get("selected_harness"),
                            "delegates": result.get("delegates"),
                            "command_exit_code": result.get("command_exit_code"),
                            "__harness_idx": harness_idx,
                        }

                        emit_otel_event(
                            enabled=args.otel,
                            event_name="agent_eval.case.end",
                            attrs={
                                "agent_eval.run_id": run_id,
                                "agent_eval.harness": harness,
                                "agent_eval.model": model if model else "default",
                                "agent_eval.journey_id": journey_id,
                                "agent_eval.case_id": case_id,
                                "agent_eval.skills_enabled": skills_cfg.get("skills_enabled"),
                                "agent_eval.outcome": "pass" if pass_bool else "fail",
                                "agent_eval.score": f"{score:.3f}",
                                "agent_eval.latency_ms": row["latency_ms"],
                                "agent_eval.trace_id": trace_id,
                            },
                            service=args.otel_service,
                            endpoint=args.otel_endpoint or None,
                        )

                        return row

                    case_rows: list[dict[str, Any]] = []
                    worker_count = min(max_workers, len(harness_variants)) if harness_variants else 1
                    if worker_count <= 1 or len(harness_variants) <= 1:
                        for harness_idx, harness_variant in enumerate(harness_variants):
                            case_rows.append(run_case_for_harness(harness_idx, harness_variant))
                    else:
                        with ThreadPoolExecutor(max_workers=worker_count) as pool:
                            futures = {
                                pool.submit(run_case_for_harness, harness_idx, harness_variant): harness_idx
                                for harness_idx, harness_variant in enumerate(harness_variants)
                            }
                            for fut in as_completed(futures):
                                case_rows.append(fut.result())

                    case_rows.sort(key=lambda r: int(r.pop("__harness_idx", 0)))
                    for row in case_rows:
                        harness = str(row.get("harness") or "")
                        model = str(row.get("model") or "")
                        if (
                            args.failfast
                            and not bool(row.get("harness_ok"))
                            and not str(row.get("harness_error") or "").startswith("failfast_skip:")
                        ):
                            failed_harnesses[variant_key(harness, model)] = str(
                                row.get("harness_error") or "unknown error"
                            )

                        rows.append(row)
                        rows_file.write(json.dumps(row, sort_keys=True) + "\n")
                        rows_file.flush()

                    emit_otel_event(
                        enabled=args.otel,
                        event_name="agent_eval.skills.unload.success",
                        attrs={
                            "agent_eval.run_id": run_id,
                            "agent_eval.journey_id": journey_id,
                            "agent_eval.case_id": case_id,
                            "agent_eval.skills_enabled": skills_cfg.get("skills_enabled"),
                            "agent_eval.skills_profile": profile_name,
                        },
                        service=args.otel_service,
                        endpoint=args.otel_endpoint or None,
                    )

            emit_otel_event(
                enabled=args.otel,
                event_name="agent_eval.journey.end",
                attrs={
                    "agent_eval.run_id": run_id,
                    "agent_eval.journey_id": journey_id,
                },
                service=args.otel_service,
                endpoint=args.otel_endpoint or None,
            )

    summary = summarize_rows(rows)
    otel_ids = {
        "run_id": run_id,
        "rows": [
            {
                "journey_id": row["journey_id"],
                "case_id": row["case_id"],
                "harness": row["harness"],
                "model": row.get("model"),
                "skills_mode": row["skills_mode"],
                "trace_id": row.get("trace_id"),
                "runtime_ids": row.get("runtime_ids", {}),
            }
            for row in rows
        ],
    }

    write_json(out_dir / "manifest.json", manifest)
    write_json(out_dir / "summary.json", summary)
    write_json(out_dir / "otel_ids.json", otel_ids)

    emit_otel_event(
        enabled=args.otel,
        event_name="agent_eval.run.end",
        attrs={
            "agent_eval.run_id": run_id,
            "agent_eval.total_rows": summary["total_rows"],
            "agent_eval.overall_pass_rate": f"{summary['overall_pass_rate']:.3f}",
        },
        service=args.otel_service,
        endpoint=args.otel_endpoint or None,
    )

    print(json.dumps({
        "run_id": run_id,
        "out_dir": str(out_dir),
        "summary": summary,
    }, indent=2))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"agent_eval_loop failed: {exc}", file=sys.stderr)
        raise
