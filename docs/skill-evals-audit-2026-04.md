# Skill Evals Audit - April 2026

Sanity check of all user-facing skills against skill-creator best practices.
Focus: missing evals, weak trigger phrases, description anti-patterns, tier sizing.

---

## Scope

Skills audited (all user-facing, `~/.claude/skills/`):

| Skill | Lines | Has `evals/` |
|---|---|---|
| `graphistry` (router) | 32 | No |
| `pygraphistry` (router) | 48 | No |
| `pygraphistry-ai` | 68 | No |
| `pygraphistry-connectors` | 79 | No |
| `pygraphistry-core` | 84 | No |
| `pygraphistry-visualization` | 168 | No |
| `graphistry-rest-api` | 268 | No (has `references/`) |
| `pygraphistry-gfql` | 232 | No |

Skills already with evals (not audited): `ad-attack-paths`, `azure`, `cyber-umap-anomaly`,
`defender-incident-graph`, `disk-cleanup`, `extract-skill`, `gmail-*`, `kusto-security-graph`,
`network-segmentation`, `sentinel-graph-hunt`, `threat-hunt-splunk-graph`, `vpc-flow-graph`,
`zeek-network-graph`, `zendesk`.

---

## Best Practices Reference (from skill-creator)

1. **Evals** - every skill needs `evals/evals.json` with 2-3 positive test cases + 1 negative
2. **Description trigger phrases** - use `"Use when asked to [phrase]"` and `"Also triggers on [phrase]"` patterns with quoted realistic user phrases; be "pushy" (Claude undertriggers by default)
3. **Proactive suggest** - add `"Proactively suggest when [context clue]"` for skills with clear ambient signals
4. **No negative conditions in description** - "Don't use for X" belongs in the skill body, not frontmatter
5. **Tier sizing:**
   - Minimal: <100 lines - single SKILL.md only
   - Middle: 100-300 lines - SKILL.md + `examples/`
   - References tier: 300+ lines - SKILL.md + `references/` dir
6. **Negative assertions** - at least one eval should verify the skill does NOT fire for an adjacent domain

---

## Findings by Skill

### graphistry (router) - CRITICAL

**Current description:**
> Umbrella router for Graphistry workflows across SDK and API surfaces. Use to dispatch between Python SDK, REST API, and (future) JavaScript SDK workflows.

**Issues:**
- No evals
- Description has zero quoted trigger phrases; a user saying "graph my logs with graphistry" or "how do I use the graphistry API" may not reliably trigger this
- "(future) JavaScript SDK workflows" is dead weight - signals a half-finished feature to the model
- No proactive suggest
- At 32 lines it is appropriately minimal, but the description needs more trigger surface

**Recommended description:**
```yaml
description: >
  Umbrella router for Graphistry workflows across SDK and API surfaces.
  Use when asked to "visualize with graphistry", "use graphistry", "graph this
  data in graphistry", "graphistry plot", or any question mixing Python SDK
  and REST API concerns. Also triggers on "graphistry SDK vs API", "how do I
  share a graphistry graph", or "graphistry authentication". Routes to
  pygraphistry for Python SDK tasks and graphistry-rest-api for curl/REST tasks.
  Proactively suggest when the user mentions Graphistry Hub, graph visualization,
  or network graph sharing without specifying an interface.
```

**Evals needed:** 3 cases: Python SDK intent, REST API intent, ambiguous cross-interface intent; 1 negative for a domain that is NOT graphistry (e.g., networkx-only graph analysis)

---

### pygraphistry (router) - CRITICAL

**Current description:**
> TOC router for PyGraphistry tasks. Use when a request involves PyGraphistry and you need to choose the right workflow: loading/ETL shaping, visualization/layout/sharing, GFQL queries (Cypher, chain-lists, Let/DAG, GRAPH constructors), AI/UMAP/embed/semantic-search workflows, or connector-specific ingestion.

**Issues:**
- No evals
- Description uses "Use when a request involves PyGraphistry" - Claude must already know it's PyGraphistry; misses users who say "how do I plot a graph in Python" or "my edges dataframe won't plot"
- No quoted realistic user phrases
- No proactive suggest clause
- Body has good routing logic, but description alone may not pull in the right cases

**Recommended description:**
```yaml
description: >
  TOC router for PyGraphistry Python SDK tasks. Use when asked to "plot a graph",
  "visualize my edges", "load a dataframe into graphistry", "import graphistry",
  "run UMAP on my graph", "query my graph with GFQL or Cypher", or "connect
  graphistry to Neo4j/Splunk/Kusto". Also triggers on "graphistry.register",
  "g.plot()", ".gfql()", "chain-list", or "hypergraph". Routes to specialized
  sub-skills (pygraphistry-core, pygraphistry-gfql, pygraphistry-ai, etc.).
  Proactively suggest when the user shares an edges/nodes DataFrame and asks
  about graph analysis or visualization.
```

**Evals needed:** 3 cases: ETL+plot, GFQL/Cypher query, UMAP/ML workflow; 1 negative for REST-only request (should route to graphistry-rest-api, not this skill)

---

### pygraphistry-ai - HIGH

**Current description:**
> Apply PyGraphistry graph ML/AI workflows such as UMAP, DBSCAN, embedding-based anomaly analysis, and fit/transform pipelines on nodes or edges. Use for feature-driven exploration, clustering, anomaly triage, and graph-AI notebook workflows.

**Issues:**
- No evals
- Passive "Apply ... such as" format - no trigger phrases
- No "Use when asked to..." pattern
- No proactive suggest
- 68 lines - fits minimal tier, no resizing needed

**Recommended description:**
```yaml
description: >
  Apply PyGraphistry graph ML/AI workflows: UMAP, DBSCAN, embeddings, and
  anomaly detection. Use when asked to "run UMAP on my graph", "cluster nodes",
  "find anomalies in my network data", "embed nodes", "fit-transform pipeline",
  or "semantic search over graph nodes". Also triggers on "graphistry umap",
  "dbscan clusters", "node embeddings", or "anomaly triage". Proactively suggest
  when the user has a node feature table and asks about outliers, clusters, or
  similarity.
```

**Evals needed:** 3 cases: UMAP run, DBSCAN clustering, anomaly triage; 1 negative for a scikit-learn-only clustering task with no graphistry

---

### pygraphistry-connectors - HIGH

**Current description:**
> Select and use PyGraphistry connector and plugin workflows for graph databases, SQL/data platforms, SIEM/log sources, and layout/compute plugins. Use when requests involve Neo4j/Neptune/Splunk/Kusto/Databricks/SQL/TigerGraph and similar integrations.

**Issues:**
- No evals
- "Use when requests involve" is passive; no quoted trigger phrases
- Good connector enumeration but reads like a capabilities list, not a trigger guide
- 79 lines - appropriate minimal tier

**Recommended description:**
```yaml
description: >
  PyGraphistry connector workflows for external data sources and graph databases.
  Use when asked to "connect graphistry to Neo4j", "load from Splunk into graphistry",
  "query Kusto/ADX and visualize", "Databricks graph", "TigerGraph with pygraphistry",
  or "ingest SQL into a graph". Also triggers on Neptune, Postgres, BigQuery,
  Memgraph, or any "graphistry + [platform]" request. Proactively suggest when
  the user has data in an external system and wants graph visualization.
```

**Evals needed:** 3 cases: Neo4j load, Splunk ingest, SQL-to-graph; 1 negative for a direct DataFrame plot with no external connector

---

### pygraphistry-core - HIGH

**Current description:**
> Core PyGraphistry workflow for authentication, shaping edges/nodes/hypergraphs, and plotting. Use for first-run setup, converting tables to graphs, and producing an initial interactive graph quickly and safely.

**Issues:**
- No evals
- No quoted trigger phrases; a first-time user saying "how do I get started with graphistry" or "my plot() call fails" may not trigger this
- "Use for first-run setup" is too narrow - this is also the baseline for any ETL + plot task
- 84 lines - appropriate minimal tier

**Recommended description:**
```yaml
description: >
  Core PyGraphistry workflow for auth, DataFrame-to-graph shaping, and first
  interactive plot. Use when asked to "register graphistry", "get started with
  pygraphistry", "plot my edges dataframe", "graphistry.register()", "bind src
  and dst columns", "make a hypergraph", or "materialize nodes". Also triggers
  on "first graphistry graph", "graphistry install", "api=3", or any question
  about graphistry auth credentials. Proactively suggest when the user is
  setting up graphistry for the first time or can't get a basic plot working.
```

**Evals needed:** 3 cases: first-time register+plot, ETL shaping, hypergraph build; 1 negative for a GFQL pattern-match query (should route to pygraphistry-gfql)

---

### pygraphistry-gfql - HIGH

**Current description:**
> Construct and run GFQL graph queries in PyGraphistry using chain-list syntax OR Cypher strings. Covers pattern matching, hop constraints, predicates, let/DAG bindings, GRAPH constructors, and remote execution. Use when requests involve subgraph extraction, path-style matching, Cypher queries, or GPU/remote graph query workflows.

**Issues:**
- No evals
- Description is technically good but has no quoted trigger phrases
- "Use when requests involve" is passive
- At 232 lines this is in the middle tier but has no `examples/` directory to offload detail
- Body is well-structured; descriptions need trigger phrase upgrade more than body restructuring

**Recommended description:**
```yaml
description: >
  Construct and run GFQL graph queries in PyGraphistry using chain-list syntax
  or Cypher strings. Use when asked to "query my graph with GFQL", "MATCH pattern
  in graphistry", "find paths between nodes", "hop constraints", "let bindings",
  "GRAPH constructor", or "run Cypher on my graph". Also triggers on "g.gfql()",
  "n() e_forward() n()", "chain-list query", "subgraph extraction", or "remote
  graph query". Proactively suggest when the user wants pattern matching or
  multi-hop traversal on a graph already loaded in PyGraphistry.
```

**Tier note:** At 232 lines, consider adding an `examples/` directory with the extended Cypher/chain-list quick-reference tables to keep SKILL.md under 200 lines.

**Evals needed:** 3 cases: chain-list hop query, Cypher MATCH, Let/DAG binding; 1 negative for a visualization-only request (should route to pygraphistry-visualization)

---

### pygraphistry-visualization - MEDIUM

**Current description:**
> Build PyGraphistry visualizations with bindings, encodings, layout controls, static export, and privacy-aware sharing. Use for color/size/icon/badge styling, layout tuning, map/static output, and plot link sharing workflows.

**Issues:**
- No evals
- Passive "Use for" pattern; no trigger phrases
- 168 lines - sits in middle tier; has `references/` dir for icon lookup, which is good
- Body content is solid

**Recommended description:**
```yaml
description: >
  PyGraphistry visualization: bindings, color/size/icon encodings, layout
  controls, static export, and privacy-safe link sharing. Use when asked to
  "color nodes by type", "set point size", "add icons to nodes", "layout my
  graph", "export graph as PNG", "share a graphistry link privately", or
  "url_params". Also triggers on "encode_point_color", "bind(point_label=...)",
  "settings(url_params=...)", "badge", or "static graph image". Proactively
  suggest when the user has a working plot but wants to customize its appearance
  or control who can see the shared URL.
```

**Evals needed:** 3 cases: color encoding, layout + export, privacy sharing; 1 negative for a GFQL query masquerading as a visualization request

---

### graphistry-rest-api - MEDIUM

**Current description:**
> Graphistry Hub REST API specialist for auth, upload lifecycle, URL controls, sessions, and sharing safety. Use for curl/requests endpoint guidance independent of SDK choice.

**Issues:**
- No evals
- No quoted trigger phrases; "Use for curl/requests endpoint guidance" is passive
- At 268 lines approaching references tier; already has `references/` dir - good
- "independent of SDK choice" is vague and adds little triggering value

**Recommended description:**
```yaml
description: >
  Graphistry Hub REST API: auth, upload, URL controls, sessions, and sharing.
  Use when asked to "call the graphistry API with curl", "get a JWT token from
  graphistry", "upload a graph via REST", "graph.html URL parameters", "graphistry
  session API", or "share a graph link safely". Also triggers on "/api/v2/",
  "Bearer token", "graphistry upload endpoint", or any direct HTTP endpoint
  question about Graphistry Hub. Prefer this over pygraphistry when the user
  explicitly uses curl, requests, or raw HTTP rather than the Python SDK.
```

**Evals needed:** 3 cases: JWT auth flow, graph upload via REST, URL param control; 1 negative for a Python SDK `.plot()` task (should route to pygraphistry-core, not REST)

---

## Priority Matrix

| Priority | Issue | Skills Affected | Effort |
|---|---|---|---|
| P1 | Missing `evals/evals.json` | All 8 | Medium per skill (3-4 cases each) |
| P2 | No quoted trigger phrases in description | All 8 | Low per skill (rewrite ~3 lines) |
| P3 | No proactive suggest clause | All 8 (routers most critical) | Low (1 line each) |
| P4 | gfql tier sizing (232 lines, no examples/) | pygraphistry-gfql | Low-Medium |
| P5 | Dead-weight content in descriptions | graphistry, graphistry-rest-api | Low |

---

## Implementation Plan

### Phase 1 - Description updates (fast, low-risk)

For each skill, update the `description` frontmatter in `.agents/skills/<skill>/SKILL.md`:
- Add `"Use when asked to [quoted phrase]"` pattern
- Add `"Also triggers on [phrase]"` secondary triggers
- Add `"Proactively suggest when [context]"` where applicable
- Remove passive "Use for" and "Use when requests involve" phrasing
- Remove dead-weight forward-looking notes ("future JS SDK")

Order: graphistry -> pygraphistry (routers first, highest leverage) -> pygraphistry-core -> pygraphistry-gfql -> pygraphistry-ai -> pygraphistry-connectors -> pygraphistry-visualization -> graphistry-rest-api

### Phase 2 - Add evals (main effort)

For each skill, create `.agents/skills/<skill>/evals/evals.json`:
- 2-3 realistic positive prompts (what a real user would type)
- 1 negative prompt (adjacent domain that should NOT trigger this skill)
- `expected_output` description for each
- `assertions` array with `contains` and `negative` type checks

Suggested eval themes per skill are listed in each finding above.

### Phase 3 - Tier review for pygraphistry-gfql

- Review whether chain-list/Cypher quick-reference tables can move to `examples/` to bring SKILL.md under 200 lines
- Assess if this improves model behavior or is purely cosmetic

### Phase 4 - Description optimization loop (optional, post-merge)

Run `scripts/run_loop.py` with trigger evals for the two router skills (graphistry, pygraphistry)
since they have the most triggering surface area. This requires the `claude` CLI.

---

## Acceptance Criteria for PR

- [ ] All 8 skills have `evals/evals.json` with 3+ cases each (2 positive + 1 negative minimum)
- [ ] All 8 skill descriptions include at least 3 quoted trigger phrases
- [ ] All 8 skill descriptions include a "Proactively suggest when" clause
- [ ] No description uses passive "Use for" or "Use when requests involve" as the only trigger guidance
- [ ] No negative conditions ("Don't use for X") in any description frontmatter
- [ ] `validate_skills.py` passes for all modified skills
- [ ] CHANGELOG entry added under `[Unreleased]`
