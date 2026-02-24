# Security Public-Readiness Audit

Audit date: 2026-02-24  
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

1. GitHub security analysis features are disabled
- Evidence: repo `security_and_analysis` shows disabled for code security, Dependabot security updates, secret scanning, and push protection.
- Risk: no server-side leak/vuln detection on PRs or pushes.
- Required action:
  - Enable secret scanning + push protection
  - Enable Dependabot security updates
  - Enable code scanning / code security

2. `main` is not protected and no rulesets are configured
- Evidence: branch protection API returns `Branch not protected`; rulesets list is empty.
- Risk: accidental direct pushes, no required checks/review gates, weaker change control.
- Required action:
  - Protect `main` (require PR + required status checks + disallow force-push)
  - Add at least one ruleset for repository-wide branch policy

3. Benchmarks include high-risk publication content (privacy/leakage surface)
- Evidence includes:
  - absolute local paths (for example `/home/<user>/...`) in benchmark manifests
  - full prompt/response corpora in checked-in `rows.jsonl`
  - historical test credential strings in benchmark data (`<test_user>`, `<test_pass>`)
  - runtime metadata/trace identifiers in checked-in artifacts (for example `otel_ids.json`)
- Risk: leaks workstation identity/pathing, sensitive prompt contents, and potential credential material over time.
- Required action:
  - Define and enforce a benchmark publication policy:
    - public repo keeps only sanitized summaries/aggregates
    - raw rows/log/trace artifacts remain private
  - Purge non-compliant benchmark artifacts before public launch

4. Possible credential exposure history for historical test credentials
- Evidence: strings existed in tracked files and benchmark artifacts; they were used in checks and are present in git history.
- Risk: if those credentials were real at any point, they are compromised.
- Required action:
  - Treat as exposed and rotate/revoke immediately
  - Remove all remaining occurrences from tracked files
  - Decide whether to rewrite history before going public

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
- [ ] Decide benchmark publication policy for public repo:
- public-safe summaries only vs full raw eval corpora in-repo.
- [ ] If policy excludes raw corpora: approve history rewrite strategy (rewrite vs preserve and move private).
- [ ] In GitHub repo settings, enable:
- Secret scanning
- Secret scanning push protection
- Dependabot security updates
- Code security / code scanning
- [ ] Protect `main`:
- require pull requests
- require status checks
- disallow force pushes/deletions
- [ ] Add/approve org ruleset(s) for default branch governance.
- [ ] Decide whether README keeps a live tokenized sample URL or switches to redacted placeholder.
- [ ] Decide CODEOWNERS ownership map for security-sensitive paths.

## Strike List: Agent-Owned

- [ ] Implement benchmark sanitization pipeline (strip local paths, redact tokenized URLs, block credential-like literals).
- [ ] Apply publication policy to existing benchmark artifacts and produce a clean public-safe benchmark set.
- [ ] Add CI guard that fails on non-compliant benchmark artifacts.
- [ ] Pin third-party GitHub Actions to immutable SHAs.
- [ ] Add `.github/CODEOWNERS` once owner mapping is confirmed.
- [ ] Redact README live sample URL if operator chooses redaction.
- [ ] Run full secret/leak scans after sanitization and publish a signed-off audit rerun.
- [ ] Produce final pre-public checklist report with explicit pass/fail gate status.
