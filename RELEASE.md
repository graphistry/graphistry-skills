# Release Guide (Maintainers)

This document defines the standard release process for `graphistry-skills`.

## Scope

- This repository is consumed from GitHub (for example via `npx skills add graphistry/graphistry-skills`).
- "Publish" means:
1. release changes merged to `main`,
2. semver tag created and pushed,
3. GitHub Release published with notes.

## Versioning

Use semver `vX.Y.Z`.

- Patch (`Z`): fixes, docs corrections, small harness updates
- Minor (`Y`): new skills/journeys, meaningful capability expansion
- Major (`X`): breaking format/workflow changes

## Preflight Checklist

- Local checkout is clean: `git status --short`
- Local `main` is up to date: `git fetch origin && git checkout main && git pull --ff-only`
- `CHANGELOG.md` has complete entries under `[Development]`
- Skills validation passes:
```bash
python3 scripts/ci/validate_skills.py
```

## Standard Release Workflow

1. Create release branch from latest `main`
```bash
git checkout main
git pull --ff-only
git checkout -b release/vX.Y.Z
```

2. Cut changelog version section
- Move current `[Development]` entries under a new heading:
  - `## [X.Y.Z - YYYY-MM-DD]`
- Leave `[Development]` empty for future work.

3. Commit and push
```bash
git add CHANGELOG.md
git commit -m "chore(release): bump changelog to X.Y.Z"
git push -u origin release/vX.Y.Z
```

4. Open and merge release PR
- Base: `main`
- Head: `release/vX.Y.Z`
- Use squash merge after review/approval policy is satisfied.

5. Tag from updated `main`
```bash
git checkout main
git pull --ff-only
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

6. Publish GitHub Release
```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --notes-file /tmp/release_vX.Y.Z.md
```

## Post-Release Verification

```bash
git tag --list --sort=v:refname | tail -n 5
gh release view vX.Y.Z --json url,publishedAt,tagName,targetCommitish
```

Verify:
- tag exists on remote,
- release is published (not draft),
- target commit is `main`.

## Related Maintainer Docs

- `CHANGELOG.md`
- `DEVELOP.md`
- `.agents/skills/internal/benchmarks/SKILL.md`
- `.agents/skills/internal/release/SKILL.md`
