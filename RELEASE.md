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

Run the automated preflight check:
```bash
python3 scripts/ci/validate_release.py --pre
```

This verifies: clean working tree, up-to-date with origin, changelog has content, skills validate, no direct-to-main pushes since last tag.

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

6. Clean up release branch
```bash
git branch -d release/vX.Y.Z
git push origin --delete release/vX.Y.Z
```

7. Publish GitHub Release
Generate notes from the changelog section, then publish:
```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --generate-notes
```

## Post-Release Verification

```bash
python3 scripts/ci/validate_release.py --post vX.Y.Z
```

This verifies: tag exists locally and on remote, changelog version section exists, [Development] is empty, release branch cleaned up.

## PR Review Check

During PR review, run:
```bash
python3 scripts/ci/validate_release.py --pr
```

This verifies: branch up-to-date with main, skills validate, eval JSONs valid, no common mistakes (os.environ[], chain()).

## Related Maintainer Docs

- `CHANGELOG.md`
- `DEVELOP.md`
- `.agents/skills/internal/benchmarks/SKILL.md`
- `.agents/skills/internal/release/SKILL.md`
