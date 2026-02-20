---
name: pygraphistry-ai
description: "Apply PyGraphistry graph ML/AI workflows such as UMAP, DBSCAN, embedding-based anomaly analysis, and fit/transform pipelines on nodes or edges. Use for feature-driven exploration, clustering, anomaly triage, and graph-AI notebook workflows."
---

# PyGraphistry AI

## Typical workflow
1. Build graph from nodes/edges.
2. Run feature/embedding method (`umap`, `embed`, optional `dbscan`).
3. Inspect derived columns/features and visualize.
4. Iterate on feature columns and sampling strategy.

## Baseline examples
```python
# Similarity embedding / projection
g2 = graphistry.nodes(df, 'id').umap(X=['f1', 'f2', 'f3'])
g2.plot()
```

```python
# Fit/transform flow for consistent projection on new batches
g_train = graphistry.nodes(df_train, 'id').umap(X=['f1', 'f2'])
g_batch = g_train.transform_umap(df_batch, return_graph=True)
g_batch.plot()
```

## Practical guardrails
- Start with small/representative samples before full runs.
- Keep explicit feature lists (`X=...`) for reproducibility.
- Track engine/dataframe type for CPU vs GPU behavior.
- For anomaly workflows, document thresholds and false-positive assumptions.

## Canonical docs
- GFQL + AI combos: https://pygraphistry.readthedocs.io/en/latest/gfql/combo.html
- API AI reference: https://pygraphistry.readthedocs.io/en/latest/api/ai.html
- AI notebook index: https://pygraphistry.readthedocs.io/en/latest/notebooks/ai.html
- Example RGCN notebook: https://pygraphistry.readthedocs.io/en/latest/demos/more_examples/graphistry_features/embed/simple-ssh-logs-rgcn-anomaly-detector.html
