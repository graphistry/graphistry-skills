# graphistry-skills

Public PyGraphistry skills for agent runtimes (Codex, Claude Code, and compatible skill loaders).

## Install

```bash
npx skills add graphistry/graphistry-skills \
  --agent codex \
  --agent claude-code \
  --skill pygraphistry \
  --skill pygraphistry-core \
  --skill pygraphistry-gfql \
  --skill pygraphistry-visualization \
  --skill pygraphistry-ai \
  --skill pygraphistry-connectors \
  --yes
```

## Skill Pack

- `pygraphistry`
- `pygraphistry-core`
- `pygraphistry-gfql`
- `pygraphistry-visualization`
- `pygraphistry-ai`
- `pygraphistry-connectors`

## Quick Eval

```bash
./bin/agent.sh \
  --codex --claude \
  --journeys pygraphistry_persona_journeys_v1 \
  --skills-mode both \
  --skills-delivery native
```

## Docs

- Contributor/dev workflows and sweep commands: `DEVELOP.md`
- Contributing guide: `CONTRIBUTING.md`
- Security policy: `SECURITY.md`
- Code of conduct: `CODE_OF_CONDUCT.md`
- License: `LICENSE`
- Report generator: `scripts/benchmarks/make_report.py`
- Benchmark artifact structure: `benchmarks/README.md`
- Latest checked-in benchmark report: `benchmarks/reports/2026-02-20-clean-rerun.md`
