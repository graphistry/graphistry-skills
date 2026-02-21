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

## Claude Code Example (Live URL)

Run from a project where these skills are installed and `graphistry` + `pandas` are available.

```bash
export GRAPHISTRY_USERNAME="your_user"
export GRAPHISTRY_PASSWORD="your_pass"
export GRAPHISTRY_SERVER="hub.graphistry.com"
export GRAPHISTRY_PROTOCOL="https"

claude -p \
  --model opus \
  --permission-mode bypassPermissions \
  --tools Bash \
  "Write and run a minimal Python script that:
  - imports pandas and graphistry
  - calls graphistry.register(api=3) using GRAPHISTRY_* env vars
  - creates tiny edges/nodes tables with src,dst,id,type
  - builds graphistry.edges(...).nodes(...)
  - calls plot(render=False)
  Return only the final live visualization URL."
```

Sample output (validated on `2026-02-21`, `model=opus`, runtime `~35.4s`):

```text
https://hub.graphistry.com/graph/graph.html?dataset=ae5fa55ad196484ba497c1f34b3beaf2&type=arrow&viztoken=fbad826d-6ea3-4d7b-84c1-bf94de52146e&usertag=ef9e6f8d-pygraphistry-0.50.6&splashAfter=1771658593&info=true
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
