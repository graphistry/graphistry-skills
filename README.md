# graphistry-skills

Skill files for AI agents (including Claude Code and OpenAI Codex) to better use the Graphistry ecosystem.

Graphistry is a graph intelligence ecosystem with fast-moving capabilities across graph ETL/shaping, visualization, GFQL graph querying, and AI workflows. These skills help agents use more of that surface area correctly and reach good results faster.

Strong frontier models often already know core Graphistry/PyGraphistry patterns due to ecosystem maturity and backward compatibility. The skills add high-value guidance on newer features, preferred workflow patterns, and safer/more reliable execution details.

## Skills Coverage

- `graphistry`: umbrella router across interfaces (SDK + REST; JS-ready routing path).
- `graphistry-rest-api`: REST specialist for auth, upload lifecycle, URL controls, sessions, and sharing safety.
- `pygraphistry`: Python SDK router.
- `pygraphistry-core`: auth, shaping, and first plot workflows.
- `pygraphistry-visualization`: bindings/encodings/layout/privacy/share patterns.
- `pygraphistry-gfql`: GFQL extraction/pattern workflows.
- `pygraphistry-ai`: embedding, UMAP/DBSCAN, anomaly workflows.
- `pygraphistry-connectors`: connector/integration workflows.

## Install

Recommended (mixed SDK + REST usage):

```bash
npx skills add graphistry/graphistry-skills \
  --agent codex \
  --agent claude-code \
  --skill graphistry \
  --skill graphistry-rest-api \
  --skill pygraphistry \
  --skill pygraphistry-core \
  --skill pygraphistry-gfql \
  --skill pygraphistry-visualization \
  --skill pygraphistry-ai \
  --skill pygraphistry-connectors \
  --yes
```

REST-only minimal install:

```bash
npx skills add graphistry/graphistry-skills \
  --agent codex \
  --agent claude-code \
  --skill graphistry \
  --skill graphistry-rest-api \
  --yes
```

## How To Use

- For REST endpoint tasks, ask directly for endpoint-level output (for example: "show curl for PersonalKey -> JWT and upload dataset with private sharing URL").
- For Python SDK tasks, ask for PyGraphistry workflows (for example: "table to graph + plot with bindings + privacy").
- For mixed workflows, ask for both in one prompt; `graphistry` routes to the right specialist skill.

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

## REST Example (Snippet Ask)

Example prompt:

```text
Provide a concise Graphistry REST snippet that:
1) gets JWT via /api-token-auth/ from env vars,
2) uploads dataset via /api/v2/upload/datasets/ with private visibility,
3) prints graph.html?dataset=... URL.
```

## Evals

These skills are regularly benchmarked and tuned against standard Graphistry user journeys (baseline vs skills, multiple runtimes/models).

For reproducible commands and sweep workflows, see [DEVELOP.md](DEVELOP.md).

Current checked-in benchmark packs show skills improving pass rates significantly:

- REST phase2 full sweep (`codex`, REST journeys, `skills=both`, 33 cases × 2):
  - `skills=on`: **90.9% pass (30/33)**, avg `13.0s`
  - `skills=off`: **27.3% pass (9/33)**, avg `17.0s`
  - **Delta: +63.6pp pass rate improvement**
- REST gapfix final sweep (`codex`, REST journeys, `skills=both`, 26 cases × 2):
  - `skills=on`: **92.3% pass (24/26)**, avg `13.1s`
  - `skills=off`: **30.8% pass (8/26)**, avg `18.9s`
  - **Delta: +61.5pp pass rate improvement**
- REST-focused eval sweep (`codex`, REST journeys, `skills=both`, 20 cases × 2):
  - `skills=on`: **95% pass (19/20)**, avg `14.2s`
  - `skills=off`: **35% pass (7/20)**, avg `20.4s`
  - **Delta: +60pp pass rate improvement**
- Fresh eval sweep with isolated baseline (`codex`, `skills=both`, 56 cases × 2):
  - `skills=on`: **91% pass (51/56)**, avg `47.4s`
  - `skills=off`: **52% pass (29/56)**, avg `46.4s`
  - **Delta: +39pp pass rate improvement**
- Prior sweep for reference (note: had baseline contamination bug):
  - `skills=on`: `88/100` pass
  - `skills=off`: `81/100` pass

See:
- [benchmarks/reports/2026-03-07-rest-phase2-full-sweep.md](benchmarks/reports/2026-03-07-rest-phase2-full-sweep.md) - Latest REST phase2 full sweep
- [benchmarks/reports/2026-03-07-rest-gapfix-final-sweep.md](benchmarks/reports/2026-03-07-rest-gapfix-final-sweep.md) - Latest REST gapfix sweep
- [benchmarks/reports/2026-03-07-rest-skills-optimization-sweep.md](benchmarks/reports/2026-03-07-rest-skills-optimization-sweep.md) - Latest REST-focused sweep
- [benchmarks/reports/2026-03-01-baseline-isolation-sweep.md](benchmarks/reports/2026-03-01-baseline-isolation-sweep.md) - Latest sweep with baseline fix
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
