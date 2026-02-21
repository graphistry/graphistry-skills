#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT / ".agents" / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def strip_quotes(value: str) -> str:
    v = value.strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    return v


def parse_frontmatter(content: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    data: dict[str, str] = {}

    if not content.startswith("---\n"):
        return data, ["Missing YAML frontmatter start marker ('---')."]

    end_marker = "\n---\n"
    end_idx = content.find(end_marker, 4)
    if end_idx == -1:
        return data, ["Missing YAML frontmatter end marker ('---')."]

    fm = content[4:end_idx]
    lines = fm.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue

        key = m.group(1)
        val = m.group(2).strip()

        if val in {"|", ">", "|-", ">-"}:
            i += 1
            block: list[str] = []
            while i < len(lines):
                next_line = lines[i]
                if not next_line.startswith((" ", "\t")):
                    break
                block.append(next_line.lstrip())
                i += 1
            data[key] = "\n".join(block).strip()
            continue

        data[key] = strip_quotes(val)
        i += 1

    return data, errors


def validate_skill_dir(skill_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    name = skill_dir.name

    if not skill_md.exists():
        return [f"{name}: Missing SKILL.md"], warnings

    content = skill_md.read_text(encoding="utf-8")
    frontmatter, fm_errors = parse_frontmatter(content)
    if fm_errors:
        return [f"{name}: {err}" for err in fm_errors], warnings

    skill_name = frontmatter.get("name", "").strip()
    if not skill_name:
        errors.append(f"{name}: Missing frontmatter field 'name'.")
    else:
        if skill_name != name:
            errors.append(f"{name}: name '{skill_name}' does not match directory '{name}'.")
        if not NAME_RE.match(skill_name):
            errors.append(
                f"{name}: name '{skill_name}' must match ^[a-z0-9]+(?:-[a-z0-9]+)*$."
            )
        if len(skill_name) > 64:
            errors.append(f"{name}: name length {len(skill_name)} exceeds 64.")

    description = frontmatter.get("description", "").strip()
    if not description:
        errors.append(f"{name}: Missing or empty frontmatter field 'description'.")
    else:
        if len(description) > 1024:
            errors.append(f"{name}: description length {len(description)} exceeds 1024.")

    line_count = len(content.splitlines())
    if line_count > 500:
        warnings.append(f"{name}: SKILL.md is {line_count} lines; target <=500 lines.")

    return errors, warnings


def main() -> int:
    if not SKILLS_DIR.exists():
        print(f"ERROR: Skills directory not found: {SKILLS_DIR}", file=sys.stderr)
        return 1

    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
    if not skill_dirs:
        print(f"ERROR: No skill directories found in {SKILLS_DIR}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    all_warnings: list[str] = []
    names_seen: dict[str, Path] = {}

    for d in skill_dirs:
        errors, warnings = validate_skill_dir(d)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

        skill_md = d / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            frontmatter, _ = parse_frontmatter(content)
            skill_name = frontmatter.get("name", "").strip()
            if skill_name:
                if skill_name in names_seen and names_seen[skill_name] != d:
                    all_errors.append(
                        f"{d.name}: duplicate skill name '{skill_name}' already used by '{names_seen[skill_name].name}'."
                    )
                names_seen[skill_name] = d

    for w in all_warnings:
        print(f"WARNING: {w}")

    if all_errors:
        for e in all_errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"Skill validation failed with {len(all_errors)} error(s).", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} skill directories successfully.")
    if all_warnings:
        print(f"Validation completed with {len(all_warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
