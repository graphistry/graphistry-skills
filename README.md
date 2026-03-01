# graphistry-skills

Skill files for AI agents (including Claude Code and OpenAI Codex) to better use the Graphistry ecosystem.

Graphistry is a graph intelligence ecosystem with fast-moving capabilities across graph ETL/shaping, visualization, GFQL graph querying, and AI workflows. These skills help agents use more of that surface area correctly and reach good results faster.

Strong frontier models often already know core Graphistry/PyGraphistry patterns due to ecosystem maturity and backward compatibility. The skills add high-value guidance on newer features, preferred workflow patterns, and safer/more reliable execution details.

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

These skills are regularly benchmarked and tuned against standard Graphistry user journeys (baseline vs skills, multiple runtimes/models).

For reproducible commands and sweep workflows, see [DEVELOP.md](DEVELOP.md).

Current checked-in benchmark packs show skills improving pass rates significantly:

- Fresh eval sweep with isolated baseline (`codex`, `skills=both`, 56 cases × 2):
  - `skills=on`: **98.2% pass (55/56)**, avg `47.4s`
  - `skills=off`: **67.9% pass (38/56)**, avg `46.4s`
  - **Delta: +30.4pp pass rate improvement**
- Prior sweep for reference (note: had baseline contamination bug):
  - `skills=on`: `88/100` pass
  - `skills=off`: `81/100` pass

See:
- [plans/fresh-eval-sweep-2026-02-28/plan.md](plans/fresh-eval-sweep-2026-02-28/plan.md) - Latest sweep with baseline fix
- [benchmarks/reports/2026-02-23-postcleanup-fullsweep.md](benchmarks/reports/2026-02-23-postcleanup-fullsweep.md) - Prior sweep

## Docs

- [Contributor/dev workflows and sweep commands](DEVELOP.md)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Code of conduct](CODE_OF_CONDUCT.md)
- [License](LICENSE)
- [Report generator](scripts/benchmarks/make_report.py)
- [Scenario coverage audit tool](scripts/benchmarks/scenario_coverage_audit.py)
- [Benchmark artifact structure](benchmarks/README.md)
- [Latest eval sweep plan](plans/fresh-eval-sweep-2026-02-28/plan.md)
