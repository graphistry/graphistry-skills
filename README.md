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

## Claude Code Example (Live URL)

Run from a project where these skills are installed and `graphistry` + `pandas` are available.

```bash
export GRAPHISTRY_USERNAME="your_user"
export GRAPHISTRY_PASSWORD="your_pass"
export GRAPHISTRY_SERVER="hub.graphistry.com"
export GRAPHISTRY_PROTOCOL="https"

PROMPT='Using Bash tool calls, run (without creating files) a tiny PyGraphistry
cyber hunt demo (5-10 rows) with realistic devices/users/processes/ips/domains
and event entities that include explicit event_time timestamps, include node and
edge type fields, style with icons plus risk coloring, set
graphistry.privacy(mode='"'"'public'"'"', notify=False), call plot(render=False),
and print only the final live URL.'

claude -p \
  --model opus \
  --permission-mode bypassPermissions \
  --tools Bash \
  "$PROMPT"
```

Sample output (validated on `2026-02-21`, `model=opus`, runtime `~68.2s`):

```text
https://hub.graphistry.com/graph/graph.html?dataset=17743ba9ff3549729fdb4d9c1c071bbc&type=arrow&viztoken=e968954a-c0e5-4206-85a6-3d950817a6d4&usertag=ef9e6f8d-pygraphistry-0.50.6&splashAfter=1771659185&info=true
```

## Evals

These skills are regularly evaluated and tuned against standard PyGraphistry user journeys (baseline vs skills, multiple runtimes/models).

For reproducible commands and sweep workflows, see [DEVELOP.md](DEVELOP.md).

Current checked-in benchmark pack shows skills improving success rates and speed on harder cases, especially on Codex model-matrix runs:

- Codex `skills=on`: `13/13` pass, avg `41.8s`
- Codex `skills=off`: `10/13` pass, avg `65.8s`

See [benchmarks/reports/2026-02-21-phase2-combined.md](benchmarks/reports/2026-02-21-phase2-combined.md) for details.

## Docs

- [Contributor/dev workflows and sweep commands](DEVELOP.md)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Code of conduct](CODE_OF_CONDUCT.md)
- [License](LICENSE)
- [Report generator](scripts/benchmarks/make_report.py)
- [Scenario coverage audit tool](scripts/benchmarks/scenario_coverage_audit.py)
- [Benchmark artifact structure](benchmarks/README.md)
- [Latest checked-in benchmark report](benchmarks/reports/2026-02-21-phase2-combined.md)
