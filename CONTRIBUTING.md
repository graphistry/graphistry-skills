# Contributing

Thanks for contributing to `graphistry-skills`.

## Where to Start

- Read `README.md` for install/usage.
- Read `DEVELOP.md` for local validation, sweeps, and reporting workflows.

## Contribution Types

- improve or add skills under `.agents/skills/`
- add/update eval journeys in `evals/journeys/`
- improve harness/benchmark tooling in `bin/` and `scripts/`
- fix docs in `README.md`, `DEVELOP.md`, and `benchmarks/`

## Local Validation

Run before opening a PR:

```bash
python3 scripts/ci/validate_skills.py
./bin/evals/codex-skills-smoke.sh
./bin/evals/claude-skills-smoke.sh
```

If you changed eval logic or skills behavior, run a focused sweep and include results:

```bash
./bin/agent.sh \
  --codex --claude \
  --journeys pygraphistry_persona_journeys_v1 \
  --case-ids persona_novice_fraud_table_to_viz_algo,persona_connector_analyst_workflow \
  --skills-mode both \
  --skills-delivery native \
  --max-workers 2 \
  --failfast
```

## PR Guidelines

- Keep changes scoped and reviewable.
- Explain what changed, why, and any behavior impacts.
- Link related issues.
- Include benchmark deltas when relevant.
- Do not commit secrets, tokens, or credentials.

## Commit Style

We prefer conventional-style commit messages:

- `feat(...)`
- `fix(...)`
- `docs(...)`
- `infra(...)`
- `refactor(...)`
- `security(...)`

## Security Issues

Do not file sensitive vulnerability details in public issues. Follow `SECURITY.md`.
