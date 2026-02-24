# Security Public-Readiness Audit

Audit date: 2026-02-24  
Last refreshed: 2026-02-24 (post-`main` history rewrite + live GitHub status check)  
Branch: `audit/security-public-readiness`

## Scope

- Repository content and tracked artifacts
- Secret-leak risk in current files
- GitHub repo security posture (settings/rules/scanning)
- CI/workflow hardening baseline

## What Was Checked

- Secret checks: `scripts/ci/secret-detection.sh` (passed)
- Targeted scans for credential patterns and personal test strings
- Workflow review: `.github/workflows/*.yml`
- Repo settings via GitHub API:
  - `security_and_analysis`
  - branch protection
  - rulesets

## Findings

## Critical Before Public

1. GitHub security analysis features are still incomplete
- Live evidence (`gh api repos/graphistry/graphistry-skills`):
  - `dependabot_security_updates=enabled`
  - `secret_scanning=disabled`
  - `secret_scanning_push_protection=disabled`
  - `code_security=disabled`
- Risk: no server-side secret leak prevention and weaker security scanning coverage.
- Required action:
  - Enable secret scanning
  - Enable secret scanning push protection
  - Enable code security / code scanning

2. Branch governance is only partially configured
- Live evidence:
  - `main` branch protection exists with PR review requirement (`required_approving_review_count=1`)
  - force-push/delete disabled
  - required status checks list is currently empty
  - repository rulesets list is empty (`[]`)
- Risk: changes can merge without CI gates; missing repository-level policy controls.
- Required action:
  - Configure required status checks on `main`
  - Add at least one repository ruleset

3. Historical test credential rotation confirmation is still pending
- Evidence: historical test credential literals previously appeared in history before rewrite.
- Risk: if those credentials were ever real, they are compromised.
- Required action:
  - Confirm whether they were real
  - Rotate/revoke if applicable, and confirm invalidation

## Critical Items Closed Since Initial Audit

1. Benchmark publication surface hardened
- Raw benchmark corpora and run artifacts removed from checked-in state/history.
- Public-safe benchmark policy now enforced via CI (`scripts/ci/validate_public_benchmarks.sh`).

2. Git history rewrite completed on default branch
- `origin/main` now points to rewritten scrubbed history (`c342f9d`).

## Important Hardening (Should Do)

1. README includes a live Graphistry URL/tokenized sample
- Evidence: `README.md` sample output includes a full live URL with `dataset` + `viztoken`.
- Action: replace with redacted placeholder URL unless explicitly intended to remain public forever.

2. GitHub Actions are tag-pinned (`@v4`) not SHA-pinned
- Evidence: `actions/checkout@v4`, `actions/setup-node@v4`.
- Risk: supply-chain drift from moving tags.
- Action: pin third-party actions to full commit SHAs for stricter provenance.

3. OTel helper uses insecure gRPC exporter mode by default
- Evidence: `bin/otel/log_event.py` uses `OTLPLogExporter(..., insecure=True)`.
- Action: keep local-default behavior only if clearly documented; gate with env toggle for non-local use.

## Low-Risk Improvements

1. Add `CODEOWNERS` for security-sensitive paths
- Suggested owners for:
  - `.github/workflows/**`
  - `scripts/ci/**`
  - `.agents/skills/**`
  - `benchmarks/**`

2. Add a pre-public release checklist doc and CI policy check
- Validate no benchmark raw rows/logs are added without explicit allowlist.

## Quick Fixes Applied in This Branch

1. Removed personal test credential strings from active journey specs
- Replaced historical test literals with non-personal sentinel literals.

2. Tightened CI workflow token permissions
- Added `permissions: contents: read` to `.github/workflows/ci.yml`.

3. Improved ignore rules for local temporary artifacts
- Added `.tmp/` and `tmp/` to `.gitignore`.

## Go-Public Gate (Recommended)

Do **not** switch visibility to public until all Critical items above are complete.

Minimum gate:
1. Credentials rotated/revoked (if ever real) and artifact cleanup complete
2. Benchmark publication policy enforced; sensitive artifacts removed
3. GitHub security scanning + push protection enabled
4. Main branch protection/ruleset enabled

## Strike List: Operator-Owned

- [ ] Rotate/revoke any potentially exposed credentials (including any prior historical test credential usage if real), then confirm they are dead.
- [x] Decide benchmark publication policy for public repo:
- public-safe summaries only vs full raw eval corpora in-repo.
- [x] If policy excludes raw corpora: approve history rewrite strategy (rewrite vs preserve and move private).
- [ ] In GitHub repo settings, enable:
- Secret scanning
- Secret scanning push protection
- Code security / code scanning
- [x] Protect `main`:
- require pull requests
- disallow force pushes/deletions
- [ ] Protect `main`: require status checks
- [ ] Add/approve org ruleset(s) for default branch governance.
- [ ] Decide whether README keeps a live tokenized sample URL or switches to redacted placeholder.
- [ ] Decide CODEOWNERS ownership map for security-sensitive paths.

## Strike List: Agent-Owned

- [x] Implement benchmark sanitization pipeline (public-safe benchmark report mode and redacted aggregate outputs).
- [x] Apply publication policy to existing benchmark artifacts and produce a clean public-safe benchmark set.
- [x] Add CI guard that fails on non-compliant benchmark artifacts.
- [ ] Pin third-party GitHub Actions to immutable SHAs.
- [ ] Add `.github/CODEOWNERS` once owner mapping is confirmed.
- [ ] Redact README live sample URL if operator chooses redaction.
- [x] Run full secret/leak scans after sanitization and publish a signed-off audit rerun.
- [ ] Produce final pre-public checklist report with explicit pass/fail gate status.

## Completion Update (2026-02-24)

- Completed git history rewrite on branch `audit/security-public-readiness` to:
  - remove historical benchmark data/report blobs from history
  - replace historical credential/local-path literals in remaining history
- Restored a curated public-safe benchmark set:
  - `benchmarks/data/2026-02-23-postcleanup-fullsweep/combined_metrics.json`
  - `benchmarks/data/2026-02-23-codex-effort-ab/combined_metrics.json`
  - `benchmarks/data/2026-02-21-scenario-coverage-audit-v2.json`
  - `benchmarks/reports/2026-02-23-postcleanup-fullsweep.md`
  - `benchmarks/reports/2026-02-23-codex-effort-ab.md`
- Validation rerun after rewrite:
  - `scripts/ci/secret-detection.sh` passed
  - `scripts/ci/validate_public_benchmarks.sh` passed
  - `scripts/ci/validate_skills.py` passed
  - `git fsck --full` passed

## Live Status Recheck (2026-02-24)

Checked with GitHub API:
- `gh api repos/graphistry/graphistry-skills`
- `gh api repos/graphistry/graphistry-skills/branches/main/protection`
- `gh api repos/graphistry/graphistry-skills/rulesets`

Observed:
- Repo still private (`private=true`)
- Default branch is `main`
- `main` branch protection enabled (PR review required, force-push/delete blocked)
- Required status checks list currently empty
- Rulesets list empty
- `dependabot_security_updates=enabled`
- `secret_scanning=disabled`
- `secret_scanning_push_protection=disabled`
- `code_security=disabled`
