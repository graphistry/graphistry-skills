---
name: release
description: Internal maintainer skill for cutting graphistry-skills releases (changelog bump, PR merge, semver tag, and GitHub release publish).
metadata:
  internal: true
---

# Release Skill (Internal Maintainer)

Use this for release operations on this repository. This is not a user-facing Graphistry domain skill.

## Use This Skill For

- Cutting a new version from `CHANGELOG.md` `[Development]`
- Creating the release PR (`release/vX.Y.Z` -> `main`)
- Tagging the merged release on `main`
- Publishing a GitHub Release

## Workflow

Follow `RELEASE.md` in the repo root. Key commands:

```bash
python3 scripts/ci/validate_release.py --pre           # 1. preflight
python3 scripts/ci/validate_release.py --pr            # during PR review
python3 scripts/ci/validate_release.py --post vX.Y.Z   # after release
```

## Guardrails

- Do not release from an unmerged feature branch.
- Do not tag before the release PR is merged to `main`.
- Do not put secrets or raw eval artifacts in release notes.

## Related Files

- `RELEASE.md` — full step-by-step release guide
- `scripts/ci/validate_release.py` — automated pre/post/PR checks
- `CHANGELOG.md`
- `.agents/skills/internal/benchmarks/SKILL.md`
