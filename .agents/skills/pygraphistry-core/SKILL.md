---
name: pygraphistry-core
description: "Core PyGraphistry workflow for authentication, shaping edges/nodes/hypergraphs, and plotting. Use for first-run setup, converting tables to graphs, and producing an initial interactive graph quickly and safely."
---

# PyGraphistry Core

## Quick workflow
1. Register to a Graphistry server.
2. Build graph from edges/nodes (or hypergraph from wide rows).
3. Bind visual columns as needed.
4. Plot and iterate.

## Minimal baseline
```python
import os
import graphistry

graphistry.register(
    api=3,
    username=os.environ['GRAPHISTRY_USERNAME'],
    password=os.environ['GRAPHISTRY_PASSWORD']
)
```

## Auth variants (org + key flows)
```python
# Organization-scoped login (SSO or user/pass org routing)
graphistry.register(api=3, org_name=os.environ['GRAPHISTRY_ORG_NAME'], idp_name=os.environ.get('GRAPHISTRY_IDP_NAME'))
```

```python
# Service account / personal key flow
graphistry.register(
    api=3,
    personal_key_id=os.environ['GRAPHISTRY_PERSONAL_KEY_ID'],
    personal_key_secret=os.environ['GRAPHISTRY_PERSONAL_KEY_SECRET']
)
```

```python
# edges_df: src,dst,... and nodes_df: id,...
g = graphistry.edges(edges_df, 'src', 'dst').nodes(nodes_df, 'id')
g.plot()
```

## Hypergraph baseline
```python
# Build graph from multiple entity columns in one table
hg = graphistry.hypergraph(df, ['actor', 'event', 'location'])
hg['graph'].plot()
```

## ETL shaping checklist
- Normalize identifier columns before binding (`src/dst/id` type consistency, null handling).
- Deduplicate high-volume repeated rows before first upload.
- Materialize nodes for node-centric steps:
```python
g = graphistry.edges(edges_df, 'src', 'dst').materialize_nodes()
```

## Practical checks
- Confirm source/destination columns are non-null and correctly typed.
- Materialize nodes if needed (`g.materialize_nodes()`) before node-centric operations.
- Start with smaller slices for first render on large data.
- For neighborhood expansion and pattern mining, use `hop()/chain()` or route to GFQL for stricter pattern constraints.
- Keep credentials in environment variables only; do not hardcode usernames/passwords/tokens.

## Canonical docs
- Core 10min: https://pygraphistry.readthedocs.io/en/latest/10min.html
- Register/auth: https://pygraphistry.readthedocs.io/en/latest/server/register.html
- Install: https://pygraphistry.readthedocs.io/en/latest/install/index.html
- For analysts/devs notebooks: https://pygraphistry.readthedocs.io/en/latest/notebooks/intro.html
- Loading/shaping + AI combos: https://pygraphistry.readthedocs.io/en/latest/gfql/combo.html
