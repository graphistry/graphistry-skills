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
- `pygraphistry-gfql`: GFQL extraction/pattern workflows — chain-list syntax, Cypher strings, Let/DAG bindings, GRAPH constructors, remote execution.
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

## Skill Scope

This repository intentionally includes two skill tiers:

- User-facing published skills: `pygraphistry*` (the install snippet above lists these).
- Internal maintainer skills live under `.agents/skills/internal/` (for example: `.agents/skills/internal/plan`, `.agents/skills/internal/eval-otel`, `.agents/skills/internal/benchmarks`) and are marked `metadata.internal: true`.

Internal maintainer skills are kept in-repo for contributor workflows and are not part of the default end-user install set.

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

- PyGraphistry suite (baseline isolation sweep, `codex`, `skills=both`, 56 cases × 2):
  - `skills=on`: **91% pass (51/56)**, avg `47.4s`
  - `skills=off`: **52% pass (29/56)**, avg `46.4s`
  - **Delta: +39pp pass rate improvement**
- REST suite (phase2 full sweep, `codex`, REST journeys, `skills=both`, 33 cases × 2):
  - `skills=on`: **90.9% pass (30/33)**, avg `13.0s`
  - `skills=off`: **27.3% pass (9/33)**, avg `17.0s`
  - **Delta: +63.6pp pass rate improvement**

- GFQL expansion suite (`claude`, GFQL Cypher/Let/DAG/functional journeys, `skills=both`, 33 cases × 2):
  - `skills=on`: **82% pass (27/33)**, avg score 0.95
  - `skills=off`: **6% pass (2/33)**
  - **Delta: +76pp pass rate improvement**
  - Separate functional execution check (code actually runs with pygraphistry): 4/7 produce correct results

See:
- [benchmarks/reports/2026-03-01-baseline-isolation-sweep.md](benchmarks/reports/2026-03-01-baseline-isolation-sweep.md) - PyGraphistry suite benchmark
- [benchmarks/reports/2026-03-07-rest-phase2-full-sweep.md](benchmarks/reports/2026-03-07-rest-phase2-full-sweep.md) - REST suite benchmark
- [benchmarks/reports/2026-03-21-gfql-expansion.md](benchmarks/reports/2026-03-21-gfql-expansion.md) - GFQL expansion benchmark
- [benchmarks/README.md](benchmarks/README.md) - full benchmark pack history

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
