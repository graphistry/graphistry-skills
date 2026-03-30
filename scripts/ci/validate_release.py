#!/usr/bin/env python3
"""Validate release preconditions and post-release state.

Usage:
  python3 scripts/ci/validate_release.py --pre          # before cutting release
  python3 scripts/ci/validate_release.py --post vX.Y.Z  # after release
  python3 scripts/ci/validate_release.py --pr            # during PR review
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(cmd: str, check: bool = False) -> tuple[int, str]:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout.strip()


def check_pre() -> list[str]:
    """Check preconditions before cutting a release."""
    errors: list[str] = []
    warnings: list[str] = []

    # Clean working tree
    _, status = run("git status --short")
    if status:
        errors.append(f"Working tree not clean:\n{status}")

    # On main
    _, branch = run("git branch --show-current")
    if branch != "main":
        warnings.append(f"Not on main (on '{branch}') — expected for release branch creation")

    # Up to date with origin
    run("git fetch origin")
    rc, _ = run("git diff --quiet HEAD origin/main")
    if rc != 0:
        _, diff = run("git log --oneline HEAD..origin/main")
        errors.append(f"Local main is behind origin:\n{diff}")

    # Changelog has [Development] content
    changelog = (ROOT / "CHANGELOG.md").read_text()
    dev_match = re.search(r"## \[Development\].*?\n(.*?)(?=\n## \[|\Z)", changelog, re.DOTALL)
    if dev_match:
        content = dev_match.group(1).strip()
        # Strip the HTML comment
        content = re.sub(r"<!--.*?-->", "", content).strip()
        if not content:
            errors.append("CHANGELOG.md [Development] section is empty — nothing to release")
    else:
        errors.append("CHANGELOG.md missing [Development] section")

    # Skills validate
    rc, out = run("python3 scripts/ci/validate_skills.py")
    if rc != 0:
        errors.append(f"Skills validation failed:\n{out}")

    # No direct-to-main pushes since last tag
    _, last_tag = run("git describe --tags --abbrev=0 2>/dev/null")
    if last_tag:
        _, commits = run(f"git log --oneline {last_tag}..HEAD --no-merges")
        non_pr = [l for l in commits.splitlines() if l and "(#" not in l]
        if non_pr:
            warnings.append(f"Commits since {last_tag} without PR reference:\n" +
                          "\n".join(f"  {l}" for l in non_pr))

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"FAIL: {e}")
    if not errors:
        print(f"PRE-RELEASE: OK ({len(warnings)} warnings)")
    return errors


def check_post(version: str) -> list[str]:
    """Check post-release state."""
    errors: list[str] = []

    # Tag exists
    rc, _ = run(f"git tag -l {version}")
    if rc != 0 or not _:
        errors.append(f"Tag {version} does not exist locally")

    # Tag on remote
    rc, _ = run(f"git ls-remote --tags origin {version}")
    if not _:
        errors.append(f"Tag {version} not found on remote")

    # Changelog has version section
    changelog = (ROOT / "CHANGELOG.md").read_text()
    v_num = version.lstrip("v")
    if f"## [{v_num}" not in changelog:
        errors.append(f"CHANGELOG.md missing section for [{v_num}]")

    # [Development] is empty (content was moved to version section)
    dev_match = re.search(r"## \[Development\].*?\n(.*?)(?=\n## \[|\Z)", changelog, re.DOTALL)
    if dev_match:
        content = re.sub(r"<!--.*?-->", "", dev_match.group(1))
        content = re.sub(r"^-{3,}\s*$", "", content, flags=re.MULTILINE).strip()
        if content:
            errors.append("[Development] section not empty after release — entries should have moved to version section")

    # Release branch cleaned up
    rc, _ = run(f"git branch -l release/{version}")
    if _.strip():
        errors.append(f"Local branch release/{version} still exists — clean it up")
    rc, _ = run(f"git ls-remote --heads origin release/{version}")
    if _.strip():
        errors.append(f"Remote branch release/{version} still exists — clean it up")

    # On main
    _, branch = run("git branch --show-current")
    if branch != "main":
        errors.append(f"Not on main after release (on '{branch}')")

    for e in errors:
        print(f"FAIL: {e}")
    if not errors:
        print(f"POST-RELEASE {version}: OK")
    return errors


def check_pr() -> list[str]:
    """Check PR health during review."""
    errors: list[str] = []
    warnings: list[str] = []

    _, branch = run("git branch --show-current")
    if branch == "main":
        errors.append("On main — expected to be on a feature/release branch")
        return errors

    # Branch up to date with main
    run("git fetch origin")
    _, behind = run("git rev-list --count HEAD..origin/main")
    if behind and int(behind) > 0:
        errors.append(f"Branch is {behind} commits behind main — rebase or merge")

    # Skills validate
    rc, out = run("python3 scripts/ci/validate_skills.py")
    if rc != 0:
        errors.append(f"Skills validation failed:\n{out}")

    # Eval JSONs are valid
    import json
    for f in sorted((ROOT / "evals" / "journeys").glob("*.json")):
        try:
            json.loads(f.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in {f.name}: {e}")

    # Check for common mistakes
    _, diff = run("git diff origin/main -- . ':!*.jsonl' ':!*.json'")
    if "os.environ[" in diff and "os.environ.get(" not in diff:
        warnings.append("New code uses os.environ[] (may crash on missing vars) — prefer os.environ.get()")
    if ".chain(" in diff:
        warnings.append("New code references .chain() — this is deprecated, use .gfql()")

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"FAIL: {e}")
    if not errors:
        print(f"PR CHECK ({branch}): OK ({len(warnings)} warnings)")
    return errors


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "--pre":
        errors = check_pre()
    elif mode == "--post":
        if len(sys.argv) < 3:
            print("Usage: --post vX.Y.Z")
            sys.exit(1)
        errors = check_post(sys.argv[2])
    elif mode == "--pr":
        errors = check_pr()
    else:
        print(__doc__)
        sys.exit(1)

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
