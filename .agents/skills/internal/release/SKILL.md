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

## Preconditions

- Working tree is clean (`git status --short`)
- You are in repo root
- GitHub CLI is authenticated (`gh auth status`)

## Workflow

### 1) Preflight
```bash
git fetch origin
git checkout main
git pull --ff-only
python3 scripts/ci/validate_skills.py
```

### 2) Cut release branch
```bash
git checkout -b release/vX.Y.Z
```

### 3) Update changelog
- Move all `[Development]` entries into `## [X.Y.Z - YYYY-MM-DD]`.
- Keep `[Development]` header and comment in place for future entries.

### 4) Commit and push
```bash
git add CHANGELOG.md
git commit -m "chore(release): bump changelog to X.Y.Z"
git push -u origin release/vX.Y.Z
```

### 5) Open release PR
```bash
gh pr create \
  --base main \
  --head release/vX.Y.Z \
  --title "chore(release): bump changelog to X.Y.Z"
```

### 6) Merge and tag
After PR merge:
```bash
git checkout main
git pull --ff-only
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

### 7) Clean up release branch
```bash
git branch -d release/vX.Y.Z
git push origin --delete release/vX.Y.Z
```

### 8) Publish GitHub release
```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --generate-notes
```

## Guardrails

- Do not release from an unmerged feature branch.
- Do not tag before the release PR is merged to `main`.
- Do not put secrets or raw eval artifacts in release notes.

## Related Files

- `RELEASE.md`
- `CHANGELOG.md`
- `.agents/skills/internal/benchmarks/SKILL.md`
