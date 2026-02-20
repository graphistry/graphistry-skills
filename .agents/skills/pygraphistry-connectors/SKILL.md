---
name: pygraphistry-connectors
description: "Select and use PyGraphistry connector and plugin workflows for graph databases, SQL/data platforms, SIEM/log sources, and layout/compute plugins. Use when requests involve Neo4j/Neptune/Splunk/Kusto/Databricks/SQL/TigerGraph and similar integrations."
---

# PyGraphistry Connectors

## Strategy
- Prefer dataframe-first ingestion when practical, then bind with `edges()/nodes()`.
- Use connector-specific notebook patterns when auth/query semantics are specialized.
- For very large datasets, push filtering/aggregation upstream before plotting.

## Connector families
- Graph DBs: Neo4j, Neptune, TigerGraph, Memgraph, Arango.
- Data/SQL: Databricks, PostgreSQL, Spanner, warehouse-style pipelines.
- Logs/SIEM: Splunk, Kusto, AlienVault.
- Compute/layout plugins: networkx, graphviz, cugraph, igraph, hypernetx.

## Minimal examples
```python
# Neo4j-style cypher path (example)
g = graphistry.cypher('MATCH (a)-[r]->(b) RETURN a,b,r')
g.plot()
```

```python
# Generic dataframe path after source-specific query/extract
# edges_df: src,dst,...
g = graphistry.edges(edges_df, 'src', 'dst')
g.plot()
```

## Canonical docs
- Plugins overview: https://pygraphistry.readthedocs.io/en/latest/plugins.html
- Connector notebooks: https://pygraphistry.readthedocs.io/en/latest/notebooks/plugins.connectors.html
- Compute/layout plugin notebooks: https://pygraphistry.readthedocs.io/en/latest/notebooks/plugins.compute.html
- Notebooks index: https://pygraphistry.readthedocs.io/en/latest/notebooks/index.html
