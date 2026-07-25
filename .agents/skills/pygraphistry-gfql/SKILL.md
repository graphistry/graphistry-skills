---
name: pygraphistry-gfql
description: "Construct and run GFQL graph queries in PyGraphistry using chain-list syntax OR Cypher strings. Covers pattern matching, hop constraints, predicates, let/DAG bindings, GRAPH constructors, and remote execution. Use when requests involve subgraph extraction, path-style matching, Cypher queries, or GPU/remote graph query workflows."
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

### Cypher node labels and DataFrame columns
GFQL Cypher maps `:Label` to boolean columns `label__<Label>`, not string columns. **Prefer property filters** (simpler, works with any column):

```python
# Recommended: property filter (works with any string/numeric column)
g2 = g.gfql("MATCH (p) WHERE p.type = 'Person' AND p.age > 30 RETURN p.name")

# Alternative: pre-create boolean label columns for Cypher :Label syntax
nodes['label__Person'] = nodes['type'] == 'Person'
g = graphistry.edges(edges, 'src', 'dst').nodes(nodes, 'id')
g2 = g.gfql("MATCH (p:Person) WHERE p.age > 30 RETURN p.name")
```

### Supported Cypher clauses
- **Full**: MATCH, WHERE, RETURN, WITH, ORDER BY, SKIP, LIMIT, DISTINCT, CALL graphistry.*, GRAPH {}, USE
- **Partial**: OPTIONAL MATCH (bounded subset), UNWIND (top-level), UNION/UNION ALL (direct g.gfql() only)
- **Not supported**: CREATE, MERGE, DELETE, SET, REMOVE (GFQL is read-only)

### Cypher functions
- **Scalar**: labels(), type(), keys(), properties(), abs(), sqrt(), coalesce(), substring(), tointeger(), tofloat(), toboolean(), tostring()
- **Aggregation**: count(), sum(), min(), max(), avg(), collect(), count(DISTINCT ...)
- **Operators**: =, <>, <, <=, >, >=, IN, STARTS WITH, ENDS WITH, CONTAINS, IS NULL, IS NOT NULL, AND, OR, NOT

## GRAPH constructor (Cypher extension)
```python
# Extract subgraph as a graph object (not a table)
subgraph = g.gfql("GRAPH { MATCH (a)-[r]->(b) WHERE a.risk_score > 7 }")

# Multi-stage pipeline with named GRAPH bindings and USE
result = g.gfql("""
    GRAPH g1 = GRAPH { MATCH (a)-[r]->(b) WHERE a.event_count > 100 }
    GRAPH g2 = GRAPH { USE g1 CALL graphistry.degree.write() }
    USE g2 MATCH (n) RETURN n.id, n.degree ORDER BY n.degree DESC LIMIT 10
""")
```

## Let/DAG bindings
```python
from graphistry import n, e_forward, let, ref

# Named bindings forming a DAG
result = g.gfql(let({
    'high_risk': n({'risk_score': {'$gt': 0.8}}),
    'neighborhoods': ref('high_risk', [e_forward(max_hops=2), n()])
}))

# Select specific binding output
result = g.gfql(let({...}), output='neighborhoods')
```

```python
# Multi-stage DAG: sequential refs build on each other
result = g.gfql(let({
    'people': n({'type': 'person'}),
    'contacts': ref('people', [e_forward({'rel': 'contacts'}), n()]),
    'owned': ref('contacts', [e_forward({'rel': 'owns'}), n()])
}), output='owned')
```

```python
# Nested let: inner DAGs execute as opaque units for parallel-friendly pipelines
result = g.gfql(let({
    'social': let({
        'people': n({'type': 'person'}),
        'friends': ref('people', [e_forward({'rel': 'knows'}), n()]),
    }),
    'infra': let({
        'servers': n({'type': 'server'}),
        'traffic': ref('servers', [e_forward({'rel': 'serves'}), n()]),
    }),
    'combined': ref('social', [e_forward(), n()])
}), output='combined')
```

```python
# Let + degree computation + visual encoding
from graphistry import n, e_forward, let, ref, call
result = g.gfql(let({
    'seeds': n({'risk_flag': True}),
    'neighborhood': ref('seeds', [e_forward(max_hops=2), n()]),
}))
# Then compute degrees and encode color
result = result.get_degrees().encode_point_color('degree', as_continuous=True)
```

- **Independent bindings** operate on the root graph
- **ref()** bindings operate on the referenced binding's output
- **Nested let** scope rules (requires pygraphistry >= 0.53.7):
  - Inner bindings do NOT leak to outer scope
  - Inner bindings CAN read outer bindings (lexical closure)
  - Sibling nested lets may reuse names without collision
  - Each nested let is an opaque execution unit (parallel-friendly)

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

- `pandas`: default-compatible option and fallback for a few unsupported/exotic features.
- `polars`: explicit CPU columnar engine; choose it for common traversal, filter, order, and aggregation workloads without a GPU.
- `cudf`: RAPIDS GPU engine.
- `polars-gpu`: explicit GPU Polars execution. Require the compatible GPU/cuDF stack; do not describe it as silently falling back to CPU.
- Valid literals are exactly `'pandas'`, `'cudf'`, `'dask'`, `'dask_cudf'`, `'polars'`, `'polars-gpu'`, `'auto'`. `'polars-gpu'` is hyphenated; `polars_gpu` is not a valid engine.
- For a Polars input graph, `engine='auto'` resolves to pandas, so use `engine='polars'` to remain native end-to-end.
- Outputs follow the selected engine: Polars for `polars`/`polars-gpu`, cuDF for `cudf`. Convert intentionally before pandas-specific operations such as `.iloc` or `groupby().apply()`.

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

`gfql()` takes no `strict=` argument: mode is process-level via `set_call_mode('auto'|'strict')` or the
`GFQL_POLARS_CALL_MODE` env var (Python override > env > default `'auto'`), read live per call. Strict mode
raises `NotImplementedError` instead of bridging.

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
is built once and collected once — that transfer-once design is what makes GPU pay off, and it is why
per-op eager collection is a GPU regression (repeated host-to-device copies).

### Choosing an engine on performance

Do not promise a speedup you have not measured. The honest defaults:

- **pandas → polars**: worth it above roughly 50–100k rows; below that, pandas is competitive and the
  conversion can dominate. Upstream reports 5.6–38x on the Cypher row-pipeline surface at 1M rows.
- **polars → polars-gpu is not a blanket win.** Measured on an NVIDIA GB10, single-hop
  `MATCH (a)-[e]->(b) WHERE ... RETURN b`: **0.83x at 100k rows (slower than CPU), 1.41x at 1M, 0.98x at 5M.**
  The GPU win is a band, not a curve that keeps rising — it depends on plan shape and how much of the work
  is GPU-executable. Benchmark the actual query before switching.
- **`set_cpu_streaming(True)` is opt-in and can be slower.** Upstream measures ~1.04–1.11x on large
  traversals (10M nodes / 80M edges) but ~0.86x — a regression — on small/interactive sizes. Use it for
  large batch CPU work only; do not enable it by default because the name sounds faster.
- Prefer measuring both engines on a representative slice over reasoning about which "should" be faster.

### Parity-or-decline: do not invent workarounds

Traversal, filter, and row ops under a Polars engine are **parity-or-`NotImplementedError`** — the engine
never silently falls back to pandas, because a hidden bridge would misreport pandas performance as Polars.
Surfaces that decline today include undirected `min_hops>1`, a direct `hop(min_hops>1)` (use `chain()`/`gfql()`),
multi-entity `rows(binding_ops=…)`, cross-entity same-path `WHERE`, and exotic expressions
(CASE/list/map/temporal). When one of these raises, the correct advice is `engine='pandas'` for that step —
not a hand-rolled conversion presented as a Polars result.

Conversion into an engine follows the repo-wide `validate`/`warn` convention: on a mixed-type object column
that Arrow cannot represent, `validate='strict'` raises (`NotImplementedError` for polars) and `'autofix'`
coerces the column to string and warns.

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
