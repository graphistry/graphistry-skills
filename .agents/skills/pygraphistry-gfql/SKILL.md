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
# Nested let: inner scope builds contact graph, outer traverses ownership
result = g.gfql(let({
    'contacts': let({
        'people': n({'type': 'person'}),
        'direct_contacts': ref('people', [e_forward({'rel': 'contacts'}), n()])
    }),
    'owned': ref('contacts', [e_forward({'rel': 'owns'}), n()])
}), output='owned')
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
- **Nested let**: `let()` can contain other `let()` for sub-DAG composition
- **NEVER use `.chain()`** — it is deprecated. Always use `.gfql()` instead

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
- Use `engine='auto'` by default; force `cudf`/`pandas` only when needed.

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
- GFQL + loaders/AI patterns: https://pygraphistry.readthedocs.io/en/latest/gfql/combo.html
- Cypher syntax guide: https://pygraphistry.readthedocs.io/en/latest/gfql/cypher.html
- Cypher-GFQL mapping: https://pygraphistry.readthedocs.io/en/latest/gfql/spec/cypher_mapping.html
