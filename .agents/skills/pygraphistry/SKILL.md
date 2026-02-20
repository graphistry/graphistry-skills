---
name: pygraphistry
description: "TOC router for PyGraphistry tasks. Use when a request involves PyGraphistry and you need to choose the right workflow: core auth/bind/plot, visualization/layout/sharing, GFQL query construction, AI/UMAP/embed workflows, or connector-specific ingestion."
---

# PyGraphistry Router

Use this skill as a dispatcher to specialized skills.

## Route By Intent
- Setup/auth/first plot from tables: use `pygraphistry-core`.
- Styling/layout/static output/privacy and sharing: use `pygraphistry-visualization`.
- Pattern matching, hops/chains, predicates, remote graph queries: use `pygraphistry-gfql`.
- UMAP/DBSCAN/embedding/anomaly and graph-AI notebooks: use `pygraphistry-ai`.
- Database/platform integrations (Neo4j, Splunk, Kusto, Databricks, SQL, etc.): use `pygraphistry-connectors`.

## Default Safety Rules
- Read credentials from environment variables; do not hardcode secrets in tracked files.
- Prefer `api=3` for modern features.
- Set explicit privacy mode before sharing links for sensitive data.
- For large graphs, reduce columns/rows before upload and visualize focused subgraphs first.

## Canonical Docs
- Main docs: https://pygraphistry.readthedocs.io/en/latest/
- 10 minutes core: https://pygraphistry.readthedocs.io/en/latest/10min.html
- Visualization: https://pygraphistry.readthedocs.io/en/latest/visualization/index.html
- GFQL: https://pygraphistry.readthedocs.io/en/latest/gfql/index.html
- Plugins/connectors: https://pygraphistry.readthedocs.io/en/latest/plugins.html
