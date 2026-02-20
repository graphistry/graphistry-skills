---
name: pygraphistry-visualization
description: "Build PyGraphistry visualizations with bindings, encodings, layout controls, static export, and privacy-aware sharing. Use for color/size/icon/badge styling, layout tuning, map/static output, and plot link sharing workflows."
---

# PyGraphistry Visualization

## Core pattern
```python
g2 = (
    g.bind(point_label='label', point_color='type', edge_color='etype')
     .encode_point_size('score')
     .settings(url_params={'play': 3000, 'info': True})
)
g2.plot()
```

## Common tasks
- Encodings: `encode_point_color`, `encode_edge_color`, `encode_point_size`, icons, badges.
- Layouts: runtime force layout settings, ring/GIB/modularity, graphviz/igraph/cugraph plugin layouts.
- Static outputs: `plot_static()` for SVG/PNG and DOT/Mermaid text modes.
- Sharing controls: `graphistry.privacy(mode='private'|'organization'|'public')`.

## Big-graph defaults
- Filter and aggregate before plotting.
- Keep only essential columns (drop large text blobs unless needed).
- Use focused subgraphs (time slice, one-hop neighborhood, top-k signals).

## Canonical docs
- Visualization hub: https://pygraphistry.readthedocs.io/en/latest/visualization/index.html
- 10min visualization: https://pygraphistry.readthedocs.io/en/latest/visualization/10min.html
- Layout guide: https://pygraphistry.readthedocs.io/en/latest/visualization/layout/intro.html
- Layout catalog: https://pygraphistry.readthedocs.io/en/latest/visualization/layout/catalog.html
- Privacy/sharing: https://pygraphistry.readthedocs.io/en/latest/server/privacy.html
- Visualization notebooks index: https://pygraphistry.readthedocs.io/en/latest/notebooks/visualization.html
