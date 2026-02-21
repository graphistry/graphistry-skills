---
name: pygraphistry-visualization
description: "Build PyGraphistry visualizations with bindings, encodings, layout controls, static export, and privacy-aware sharing. Use for color/size/icon/badge styling, layout tuning, map/static output, and plot link sharing workflows."
---

# PyGraphistry Visualization

## Core pattern
```python
g2 = (
    # Keep a plain 'type' column on both nodes and edges for legend-friendly defaults
    g.bind(point_label='label', point_color='type', edge_color='type')
     .encode_point_color('type', categorical_mapping={'agent': '#3b82f6'}, default_mapping='#94a3b8')
     # Optional: default node sizing is often degree for exploratory passes
     .encode_point_size('degree')
     .settings(url_params={'play': 3000, 'info': True})
)
g2.plot()
```

## External layout pattern
```python
# nodes_df contains x/y layout columns
g2 = graphistry.edges(edges_df, 'src', 'dst').nodes(nodes_df, 'id').bind(point_x='x', point_y='y').settings(url_params={'play': 0})
g2.plot()
```

## Icon/badge pattern
```python
g2 = (
    g.encode_point_icon('type', categorical_mapping={'person': 'user', 'org': 'building'})
     .encode_point_badge('risk', categorical_mapping={'high': 'exclamation-triangle'})
)
g2.plot()
```

Use valid Font Awesome names and keep icon mappings category-driven by `type`.
See `references/fa-icons.md` for lookup links and examples.

## Continuous-color pattern (beyond categorical maps)
```python
g2 = g.encode_edge_color('amount', palette=['#46327e', '#1fa187', '#fde724'], as_continuous=True)
g2.plot()
```

## Focused subgraph views (collection-like workflow)
```python
# Use GFQL slices to publish multiple focused views from one base graph
high_risk = g.gfql([...]).name('high-risk-slice')
partner_flow = g.gfql([...]).name('partner-flow-slice')
urls = [high_risk.plot(render=False), partner_flow.plot(render=False)]
```

## Privacy-safe sharing pattern
```python
graphistry.privacy(mode='private')
plot_url = g.plot(render=False)
```

## Common tasks
- Encodings: `encode_point_color`, `encode_edge_color`, `encode_point_size`, `encode_point_icon`, `encode_point_badge`.
- Layouts: runtime force layout settings, ring/GIB/modularity, graphviz/igraph/cugraph plugin layouts.
- Static outputs: `plot_static()` for SVG/PNG and text engines like `graphviz-dot`/`mermaid-code`.
- Sharing controls: `graphistry.privacy(mode='private'|'organization'|'public')`.
- For advanced gradients, use `palette=[...]` with `as_continuous=True` on `encode_point_color`/`encode_edge_color`.
- For large investigations, generate multiple focused GFQL slices instead of one overloaded plot.

## Big-graph defaults
- Filter and aggregate before plotting.
- Keep only essential columns (drop large text blobs unless needed).
- Use focused subgraphs (time slice, one-hop neighborhood, top-k signals).
- Prefer plain `type` columns on both nodes and edges so legends and default category encodings stay stable.
- Avoid dotted column names like `node.type` / `edge.type`; prefer plain names.
- Use native datetime types for time encodings and time-sliced comparisons.

## Canonical docs
- Visualization hub: https://pygraphistry.readthedocs.io/en/latest/visualization/index.html
- 10min visualization: https://pygraphistry.readthedocs.io/en/latest/visualization/10min.html
- Layout guide: https://pygraphistry.readthedocs.io/en/latest/visualization/layout/intro.html
- Layout catalog: https://pygraphistry.readthedocs.io/en/latest/visualization/layout/catalog.html
- Privacy/sharing: https://pygraphistry.readthedocs.io/en/latest/server/privacy.html
- Visualization notebooks index: https://pygraphistry.readthedocs.io/en/latest/notebooks/visualization.html
- Icon lookup reference: `references/fa-icons.md`
