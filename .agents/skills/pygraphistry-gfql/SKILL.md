---
name: pygraphistry-gfql
description: "Construct and run GFQL graph queries in PyGraphistry for pattern matching, hop constraints, predicates, temporal filtering, and remote execution. Use when requests involve subgraph extraction, path-style matching, or GPU/remote graph query workflows."
---

# PyGraphistry GFQL

## Quick start
```python
from graphistry import n, e_forward

g2 = g.gfql([
    n({'type': 'person'}),
    e_forward({'relation': 'transfers_to'}, min_hops=1, max_hops=3),
    n({'risk': True})
])
```

## High-value patterns
- Use `name=` labels for intermediate matches when you need constraints.
- Use `where=[...]` for cross-step/path constraints.
- Use `min_hops`/`max_hops` and `output_min_hops`/`output_max_hops` for traversal vs returned slice.
- Use predicates (`is_in`, numeric/date predicates) for concise filtering.
- Use `engine='auto'` by default; force `cudf`/`pandas` only when needed.

## Remote mode
```python
# Existing remote dataset
rg = graphistry.bind(dataset_id='my-dataset')
res = rg.gfql_remote([n(), e_forward(), n()], engine='auto')
```

## Validation and safety
- Validate user-derived query fragments before execution.
- Normalize datetime columns before temporal predicates.
- Prefer small column subsets for remote result transfer.

## Canonical docs
- GFQL index: https://pygraphistry.readthedocs.io/en/latest/gfql/index.html
- GFQL overview: https://pygraphistry.readthedocs.io/en/latest/gfql/overview.html
- GFQL quick reference: https://pygraphistry.readthedocs.io/en/latest/gfql/quick.html
- Predicate quick reference: https://pygraphistry.readthedocs.io/en/latest/gfql/predicates/quick.html
- GFQL remote mode: https://pygraphistry.readthedocs.io/en/latest/gfql/remote.html
- GFQL validation: https://pygraphistry.readthedocs.io/en/latest/gfql/validation/index.html
