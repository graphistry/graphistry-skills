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
  "Using Bash tool calls, create and run a tiny PyGraphistry cyber hunt demo (5-10 rows) with realistic devices/users/processes/ips/domains and event edges, include node and edge type fields, style with icons plus risk coloring, set graphistry.privacy(mode='public', notify=False), call plot(render=False), and print only the final live URL."
```

Sample output (validated on `2026-02-21`, `model=opus`, runtime `~65.7s`):

```text
https://hub.graphistry.com/graph/graph.html?dataset=b70ec48e8e444ebcad0219fd41805a17&type=arrow&viztoken=d71dcdf3-041a-4d03-8862-4f44364131c3&usertag=ef9e6f8d-pygraphistry-0.50.6&splashAfter=1771659004&info=true&pointSize=0.8&edgeCurvature=0.2
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
