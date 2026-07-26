# GFQL engines — measurements and full inventories

Detail behind the engine guidance in `SKILL.md`. The decision rules live there; this file holds the
numbers, the full decline list, and the index DDL surface.

## Measured performance

All figures measured locally, not quoted from docs.

### CPU: pandas vs polars (seeded 1-hop, polars engine)

| graph | pandas | polars |
| --- | --- | --- |
| 10k nodes / 80k edges | 3.06ms | 1.53ms |
| 200k nodes / 1.6M edges | 12.77ms | 6.97ms |

Upstream additionally reports 5.6–38x on the Cypher row-pipeline surface at 1M rows, and places the
pandas→polars crossover at roughly 50–100k rows.

### GPU: NVIDIA GB10, string-keyed graphs

| workload | `polars` (CPU) | `cudf` | `polars-gpu` |
| --- | --- | --- | --- |
| 1.6M edges, 2-hop | 486.9ms | 322.6ms | **284.8ms** |
| 8M edges, 1-hop | 1379.4ms | **762.8ms** | 1499.6ms |
| 8M edges, 2-hop | 2433.5ms | **1376.6ms** | 3410.0ms |

Single-hop `MATCH (a)-[e]->(b) WHERE ... RETURN b` across sizes: **0.83x at 100k rows (GPU slower than
CPU), 1.41x at 1M, 0.98x at 5M.**

`polars-gpu` wins a middle band and loses to CPU Polars at 8M edges, where `cudf` is ~2x faster than
either. Two upstream facts explain the shape: `cudf_polars` still ingests a *host* polars frame (so
already-on-device cuDF frames skip a transfer `polars-gpu` pays), and multi-hop GPU fusion is an
acknowledged follow-up where the win "dilutes".

### CPU streaming

`set_cpu_streaming(True)` measures ~1.04–1.11x on large traversals (10M nodes / 80M edges) upstream, but
~0.86x — a regression — on small/interactive sizes. Opt-in, default off.

### Index

Seeded chain query on 200k nodes / 1.6M edges, polars: **8.90ms → 1.68ms (5.3x)** with an
`edge_out_adj` index. Both Cypher spellings (`WHERE a.id = ...` and inline `{id: ...}`) were **not
consulted at all** and did not improve.

## Surfaces that decline under a Polars engine

These raise `NotImplementedError` rather than bridging. Run the step on `engine='pandas'` and report
pandas as the engine that executed:

- undirected `min_hops>1`
- a direct `hop(min_hops>1)` (use `chain()` / `gfql()` instead)
- multi-entity `rows(binding_ops=…)`
- cross-entity same-path `WHERE`
- exotic expressions (CASE / list / map / temporal)

## Index surface detail

```python
from graphistry.compute.gfql.index import create_index, drop_index, show_indexes, index_trace

gi = create_index(g, 'edge_out_adj', engine='polars')   # kinds: edge_out_adj | edge_in_adj | node_id
with index_trace() as steps:
    out = gi.gfql([n({'id': 'acct-42'}), e_forward(), n()], engine='polars')
steps[0]['path']             # 'index' or 'scan'
steps[0]['decision_reason']  # e.g. 'frontier below cost gate -> index'
```

Index DDL is accepted as the query and routed to the registry instead of the traversal executor:

```python
g2 = g.gfql('CREATE GFQL INDEX FOR edge_out_adj')   # -> Plottable carrying the index
g2.gfql('SHOW GFQL INDEXES')                        # -> DataFrame of resident indexes
g3 = g2.gfql('DROP GFQL INDEX FOR edge_out_adj')    # -> Plottable without it
```

Cost gate override: `set_cost_gate_frac(engine, frac)`. Build cost is O(E log E) once, amortized over
later seeded queries.

## Call-mode scoping

`set_call_mode` is process-global, so scope it yourself and restore in a `finally:` when only one step
must be strict. A per-call parameter is requested upstream in
[pygraphistry#1778](https://github.com/graphistry/pygraphistry/issues/1778) — if it lands, update the
SKILL.md engine section and the `polars_strict_call_mode_benchmark_integrity` eval case.

The released `gfql()` signature is `query, engine, output, policy, where, language, params, validate,
shortest_path_backend` — no `call_mode`, no `strict`.
