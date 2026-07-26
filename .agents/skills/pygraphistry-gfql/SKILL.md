---
name: pygraphistry-gfql
description: >
  Construct and run GFQL graph queries in PyGraphistry using chain-list syntax or Cypher strings.
  Use when asked to "query my graph with GFQL", "MATCH pattern in graphistry", "find paths between nodes",
  "hop constraints", "let bindings", "GRAPH constructor", or "run Cypher on my graph".
  Also triggers on "g.gfql()", "n() e_forward() n()", "chain-list query", "subgraph extraction",
  "remote graph query", or "pattern matching in graphistry". Proactively suggest when the user
  wants multi-hop traversal or pattern matching on a graph already loaded in PyGraphistry.
---

# PyGraphistry GFQL

## Doc routing (local + canonical)
- First route with `../pygraphistry/references/pygraphistry-readthedocs-toc.md`.
- Use `../pygraphistry/references/pygraphistry-readthedocs-top-level.tsv` for section-level shortcuts.
- Only scan `../pygraphistry/references/pygraphistry-readthedocs-sitemap.xml` when a needed page is missing.
- Use one batched discovery read before deep-page reads; avoid `cat *` and serial micro-reads.
- In user-facing answers, prefer canonical `https://pygraphistry.readthedocs.io/en/latest/...` links.

## Two syntaxes, one entrypoint

`g.gfql()` accepts **both** chain-list (Python AST objects) **and** Cypher strings. It auto-detects the language from the argument type:

```python
# Chain-list syntax (Python AST objects)
g2 = g.gfql([n({'type': 'person'}), e_forward(), n()])

# Cypher string syntax (auto-detected)
g2 = g.gfql("MATCH (p:Person)-[r:KNOWS]->(q:Person) RETURN p.name, q.name")

# Explicit language parameter (optional)
g2 = g.gfql(query_string, language="cypher")
```

**When to use which:**
- **Chain-list**: Programmatic composition, dynamic parameterization, when building queries from code
- **Cypher**: Readability, familiarity for Cypher users, complex pattern matching with RETURN/ORDER BY/LIMIT

## Quick start — chain-list
```python
from graphistry import n, e_forward

g2 = g.gfql([
    n({'type': 'person'}),
    e_forward({'relation': 'transfers_to'}, min_hops=1, max_hops=3),
    n({'risk': True})
])
```

## Quick start — Cypher
```python
# Simple pattern match
g2 = g.gfql("MATCH (p:Person)-[r:KNOWS]->(q:Person) WHERE p.age > 30 RETURN p.name, q.name")

# Variable-length paths
g2 = g.gfql("MATCH (a:Account)-[*1..3]->(m:Merchant) RETURN a, m")

# Parameterized queries
g2 = g.gfql(
    "MATCH (n) WHERE n.score > $cutoff RETURN n.id, n.score ORDER BY n.score DESC LIMIT $top_n",
    params={"cutoff": 50, "top_n": 10}
)

# Relationship type alternation
g2 = g.gfql("MATCH (a:Person)-[:KNOWS|COLLABORATES_WITH]->(b:Person) RETURN a.name, b.name")
```

See `references/gfql-cypher.md` for the full clause/function inventory and label-column mapping.

## GRAPH constructor and Let/DAG bindings

```python
from graphistry import n, e_forward, let, ref

# Subgraph as a graph object (not a table)
subgraph = g.gfql("GRAPH { MATCH (a)-[r]->(b) WHERE a.risk_score > 7 }")

# Named bindings forming a DAG; ref() operates on the referenced binding's output
result = g.gfql(let({
    'high_risk': n({'risk_score': {'$gt': 0.8}}),
    'neighborhoods': ref('high_risk', [e_forward(max_hops=2), n()])
}), output='neighborhoods')
```

Independent bindings operate on the root graph. See `references/gfql-cypher.md` for multi-stage DAGs,
nested `let` scope rules, and the GRAPH/USE pipeline form.

## Targeted patterns (high signal)
```python
# Edge query filtering
g2 = g.gfql([n(), e_forward(edge_query="type == 'replied_to' and submolt == 'X'"), n()])
```

```python
# Same-path constraints with where + compare/col
from graphistry import col, compare
g2 = g.gfql([n(name='a'), e_forward(name='e'), n(name='b')], where=[compare(col('a', 'owner_id'), '==', col('b', 'owner_id'))])
```

```python
# Traverse 2-4 hops but only return hops 3-4
g2 = g.gfql([e_forward(min_hops=2, max_hops=4, output_min_hops=3, output_max_hops=4)])
```

## Edge direction variants
- `e_forward()` — source-to-destination
- `e_reverse()` — destination-to-source
- `e_undirected()` — both directions
- `e()` — alias for any direction

## High-value patterns
- `g.gfql()` is the unified entrypoint — pass chain-lists OR Cypher strings.
- **NEVER use `.chain()` or `.hop()`** — they are deprecated and emit warnings. Always use `g.gfql([...])` for chain-list syntax or `g.gfql("MATCH ...")` for Cypher.
- When user explicitly asks for GFQL, final snippets must include explicit `.gfql(...)`.
- When the task says remote execution/dataset, use `gfql_remote(...)`.
- Use `name=` labels for intermediate matches when you need constraints.
- Use `where=[...]` for cross-step/path constraints.
- Use `min_hops`/`max_hops` and `output_min_hops`/`output_max_hops` for traversal vs returned slice.
- Use predicates (`is_in`, numeric/date predicates) for concise filtering.
- Use an explicit engine when performance or result frame type matters; `engine='auto'` does not select Polars.

## Execution engines: pandas, Polars, cuDF, and Polars-GPU

Use the same query with the engine suited to the workload. Input frame type and execution engine are independent; GFQL converts inputs once and returns frames in the selected engine's type.

```python
query = "MATCH (a)-[e]->(b) WHERE a.risk_score > $cutoff RETURN b"

cpu_out = g.gfql(query, params={'cutoff': 7}, engine='polars')
gpu_out = g.gfql(query, params={'cutoff': 7}, engine='polars-gpu')

# Polars/Polars-GPU outputs are polars.DataFrame objects
nodes_pd = cpu_out._nodes.to_pandas()  # only for pandas-only downstream APIs
```

- Valid literals are exactly `'pandas'`, `'cudf'`, `'dask'`, `'dask_cudf'`, `'polars'`, `'polars-gpu'`,
  `'auto'`. `'polars-gpu'` is hyphenated; `polars_gpu` is not an engine.
- For a Polars input graph **`engine='auto'` resolves to pandas** — pass `engine='polars'` to stay native.
- Outputs follow the selected engine: Polars for `polars`/`polars-gpu`, cuDF for `cudf`. Convert
  intentionally before pandas-only operations such as `.iloc` or `groupby().apply()`.
- `polars-gpu` requires the RAPIDS stack and is **GPU-or-error** — it never silently falls back to CPU.

### Analytics under Polars engines

Whole-graph `call()` analytics such as UMAP, hypergraph, layouts, or `compute_cugraph` are not native Polars operations. With the default `call_mode='auto'`, GFQL bridges them off-engine (pandas for Polars; cuDF for Polars-GPU) and converts the result back. Use strict mode when an off-engine bridge would violate a benchmark, memory, or execution constraint:

```python
from graphistry.compute.gfql.lazy import set_call_mode

set_call_mode('strict')  # reject an off-engine analytic before it runs
try:
    result = g.gfql(query, engine='polars')
except NotImplementedError as exc:
    ...  # strict mode declined an off-engine analytic
```

`gfql()` takes no `strict=` or `call_mode=` argument. Mode is process-level via
`set_call_mode('auto'|'strict')` or `GFQL_POLARS_CALL_MODE` (Python override > env > default `'auto'`),
read live per call. Strict raises **`NotImplementedError`** — not `RuntimeError`, not a warning. Because
it is process-global, scope it and restore in a `finally:` when only one step must be strict
(`references/gfql-engines.md`).

`polars-gpu` analytics are GPU-or-error: if the GPU/cuDF stack is unavailable, they decline rather than move the work to host pandas.

### Engine tuning knobs

Three process-level settings live in `graphistry.compute.gfql.lazy`, each resolving
**Python override > env var > default** and read live per collect (not frozen at import):

| setting | values | default | env var |
| --- | --- | --- | --- |
| `set_call_mode` | `'auto'`, `'strict'` | `'auto'` | `GFQL_POLARS_CALL_MODE` |
| `set_gpu_executor` | `'in-memory'`, `'streaming'` | `'in-memory'` | `GFQL_POLARS_GPU_EXECUTOR` |
| `set_cpu_streaming` | `True`, `False` | `False` | `GFQL_POLARS_CPU_STREAMING` |

Read the current value with `call_mode()`, `gpu_executor()`, `cpu_streaming()`; pass `None` to a setter to
reset to env/default. `'polars'` and `'polars-gpu'` are one lazy engine with two collect targets, so the plan
is built once and collected once. That transfer-once design is what makes GPU pay off:

- **Collect-once avoids repeated host-to-device (H2D) transfers.** Per-op eager collection re-copies the
  frame to the device on every operation, which benchmarked as a GPU *regression*.
- The knobs resolve **Python override > env var > default**, read live per collect — not frozen at import.

### Physical indexes: seeded lookups

GFQL ships pay-as-you-go adjacency/node-id indexes (`graphistry.compute.gfql.index`) for seeded traversal.
Two rules decide whether an index helps:

- **Query shape — only the chain/hop form consults the index.** Measured: a seeded chain went
  **8.90ms → 1.68ms (5.3x)**, while both Cypher spellings were never consulted and did not improve.
  Write the chain form if you want index acceleration.
- **Frontier size, engine-aware.** The planner gates index-vs-scan on the frontier as a fraction of
  distinct source keys: **pandas ~0.5, polars/cuDF/GPU ~0.02**. Vectorized engines scan fast enough that an
  index only wins for very selective seeds. Past the gate it falls back to scan, so it never loses.

```python
from graphistry.compute.gfql.index import create_index, index_trace
gi = create_index(g, 'edge_out_adj', engine='polars')   # edge_out_adj | edge_in_adj | node_id
with index_trace() as steps:
    out = gi.gfql([n({'id': 'acct-42'}), e_forward(), n()], engine='polars')
steps[0]['path']   # confirm 'index', do not assume it
```

`index_policy=` **is** a per-call `gfql()` keyword (unlike call mode): `'use'` (default, resident +
cost-gated), `'auto'` (build on demand), `'force'` (skip the gate), `'off'`. With no resident index,
`'use'` silently scans. Index DDL, trace fields, and the cost-gate override: `references/gfql-engines.md`.

### Choosing an engine on performance

Do not promise a speedup you have not measured.

- **pandas → polars**: worth it above roughly 50–100k rows; below that conversion can dominate. Measured ~2x on seeded 1-hop.
- **polars → polars-gpu is not a blanket win.** Measured on an NVIDIA GB10: **0.83x at 100k rows (slower
  than CPU), 1.41x at 1M, 0.98x at 5M** — a band, not a rising curve. At 8M edges `cudf` beat both.
  Never state a general "polars-gpu beats cudf" rule.
- **`set_cpu_streaming(True)` is opt-in and can be slower** — ~0.86x on small/interactive sizes. Large
  batch CPU work only; the name sounds faster than it is.
- Full measurement tables: `references/gfql-engines.md`.

### Which engine when — a decision procedure

Work in order; stop at the first that decides.

1. **Does a step decline under Polars?** Run that step on `engine='pandas'` and report pandas as the engine.
2. **Where do the frames already live?** `polars-gpu` ingests a *host* polars frame, so already-on-device
   cuDF frames favor `engine='cudf'`; host Polars frames favor `'polars'`/`'polars-gpu'`.
3. **Seeded lookup with a small frontier?** Index it and use the chain form — the biggest single win
   available (5.3x), independent of engine choice.
4. **CPU: prefer `polars` over `pandas`** for anything non-trivial.
5. **GPU: only when the workload is big enough**, and pick the GPU engine by measurement, not by name.

Below a few milliseconds of work, engine choice is noise — indexing and query shape matter more.

### Parity-or-decline: do not invent workarounds

**Refuse to mislabel first, then solve the problem.** If a user asks you to keep reporting
`engine='polars'` for work that pandas executed — to keep a dashboard green, a benchmark comparable, or an
API contract stable — say no before writing any code. A wrapper that exposes `engine='polars'` while
pandas runs underneath is mislabeling even when a second field records the truth: the primary label is the
one people read. This is the one request in this skill you should push back on rather than implement.

Honest alternatives to offer: run the step on `engine='pandas'` and report pandas, or keep the pipeline
polars-native by avoiding the declining surface.

With that settled, the mechanics: traversal, filter, and row ops under a Polars engine are
**parity-or-`NotImplementedError`**.

- The engine **never silently falls back** to pandas — a hidden bridge would misreport pandas performance as Polars.
- An unsupported surface raises **`NotImplementedError`** (not `RuntimeError`, not a warning).
- Surfaces that decline today: undirected `min_hops>1`, direct `hop(min_hops>1)` (use `chain()`/`gfql()`),
  multi-entity `rows(binding_ops=…)`, cross-entity same-path `WHERE`, exotic expressions
  (CASE/list/map/temporal). Full list: `references/gfql-engines.md`.

Conversion into an engine follows the repo-wide `validate`/`warn` convention. On a mixed-type object column
that Arrow cannot represent:

| `validate` | behavior |
| --- | --- |
| `'strict'` | **raises an error** (`NotImplementedError` for polars); the column is left unchanged |
| `'autofix'` | **coerces the column to string and emits a warning** — data is silently rewritten unless you read the warning |

Use `'strict'` for any job that must never change data without telling you.

## Remote mode
```python
# Remote with chain-list
rg = graphistry.bind(dataset_id='my-dataset')
res = rg.gfql_remote([n(), e_forward(), n()], engine='auto')
```

```python
# Remote with Cypher string
res = rg.gfql_remote("MATCH (n:Person)-[r]->(m) WHERE n.risk_level = 'critical' RETURN n, r, m")
```

```python
# Remote with Let/DAG
res = rg.gfql_remote(let({...}))
```

```python
# Remote slim payload (only required columns)
res = rg.gfql_remote([n(), e_forward(), n()], output_type='nodes', node_col_subset=['node_id', 'time'])
```

```python
# Post-process on remote side when you want trimmed transfer payloads
res = rg.python_remote_table(lambda g: g._edges[['src', 'dst']].head(1000))
```

## Validation and safety
- Validate user-derived query fragments before execution.
- Normalize datetime columns before temporal predicates.
- Prefer small column subsets for remote result transfer.
- Preflight Cypher: `from graphistry.compute.gfql.cypher import parse_cypher, compile_cypher`

## Canonical docs
- GFQL index: https://pygraphistry.readthedocs.io/en/latest/gfql/index.html
- GFQL overview: https://pygraphistry.readthedocs.io/en/latest/gfql/overview.html
- GFQL quick reference: https://pygraphistry.readthedocs.io/en/latest/gfql/quick.html
- Predicate quick reference: https://pygraphistry.readthedocs.io/en/latest/gfql/predicates/quick.html
- GFQL remote mode: https://pygraphistry.readthedocs.io/en/latest/gfql/remote.html
- GFQL validation: https://pygraphistry.readthedocs.io/en/latest/gfql/validation/index.html
- Engine guide: https://pygraphistry.readthedocs.io/en/latest/gfql/engines.html
- GFQL + loaders/AI patterns: https://pygraphistry.readthedocs.io/en/latest/gfql/combo.html
- Cypher syntax guide: https://pygraphistry.readthedocs.io/en/latest/gfql/cypher.html
- Cypher-GFQL mapping: https://pygraphistry.readthedocs.io/en/latest/gfql/spec/cypher_mapping.html
