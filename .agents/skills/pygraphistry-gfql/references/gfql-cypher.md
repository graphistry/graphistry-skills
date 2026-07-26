# GFQL Cypher — clause and function inventory

Detail behind the Cypher quick start in `SKILL.md`.

## Supported clauses
- **Full**: MATCH, WHERE, RETURN, WITH, ORDER BY, SKIP, LIMIT, DISTINCT, CALL graphistry.*, GRAPH {}, USE
- **Partial**: OPTIONAL MATCH (bounded subset), UNWIND (top-level), UNION/UNION ALL (direct `g.gfql()` only)
- **Not supported**: CREATE, MERGE, DELETE, SET, REMOVE (GFQL is read-only)

## Functions
- **Scalar**: labels(), type(), keys(), properties(), abs(), sqrt(), coalesce(), substring(), tointeger(), tofloat(), toboolean(), tostring()
- **Aggregation**: count(), sum(), min(), max(), avg(), collect(), count(DISTINCT ...)
- **Operators**: =, <>, <, <=, >, >=, IN, STARTS WITH, ENDS WITH, CONTAINS, IS NULL, IS NOT NULL, AND, OR, NOT

## Node labels and DataFrame columns

GFQL Cypher maps `:Label` to boolean columns `label__<Label>`, not string columns. Prefer property
filters — simpler, and works with any column:

```python
# Recommended
g2 = g.gfql("MATCH (p) WHERE p.type = 'Person' AND p.age > 30 RETURN p.name")

# Alternative: pre-create boolean label columns
nodes['label__Person'] = nodes['type'] == 'Person'
g = graphistry.edges(edges, 'src', 'dst').nodes(nodes, 'id')
g2 = g.gfql("MATCH (p:Person) WHERE p.age > 30 RETURN p.name")
```

## GRAPH constructor

```python
subgraph = g.gfql("GRAPH { MATCH (a)-[r]->(b) WHERE a.risk_score > 7 }")

result = g.gfql("""
    GRAPH g1 = GRAPH { MATCH (a)-[r]->(b) WHERE a.event_count > 100 }
    GRAPH g2 = GRAPH { USE g1 CALL graphistry.degree.write() }
    USE g2 MATCH (n) RETURN n.id, n.degree ORDER BY n.degree DESC LIMIT 10
""")
```

## Let/DAG extended examples

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
result = g.gfql(let({
    'seeds': n({'risk_flag': True}),
    'neighborhood': ref('seeds', [e_forward(max_hops=2), n()]),
}))
result = result.get_degrees().encode_point_color('degree', as_continuous=True)
```

Scope rules for nested `let` (requires pygraphistry >= 0.53.7):
- Inner bindings do NOT leak to outer scope
- Inner bindings CAN read outer bindings (lexical closure)
- Sibling nested lets may reuse names without collision
- Each nested let is an opaque execution unit (parallel-friendly)
