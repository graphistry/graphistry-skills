# GFQL wire format

Full JSON forms for `gfql_operations`. The decision-critical rules live in `SKILL.md`; this file
holds the complete examples.

`gfql_operations` is always a **JSON-encoded string**, never a nested object. Only five operation
types are valid: `Node`, `Edge`, `Call`, `Let`, `Ref`.

## Node

Filters nodes. Equality against a stored value:

```json
[{"type": "Node", "filter_dict": {"category": "Malware"}}]
```

Threshold with a predicate object. The predicate goes inside `filter_dict`, keyed by column:

```json
[{"type": "Node", "filter_dict": {"event_count": {"type": "GT", "val": 10}}}]
```

Predicate `type` values follow the GFQL comparison set (`GT`, `LT`, `GE`, `LE`, `EQ`, `NE`).

An **empty** `Node` operation (`{"type": "Node"}`) accumulates both endpoints of a preceding
`Edge` rather than filtering. Use it when the request names two node kinds joined by "and"/"or".

## Edge

Traverses. Takes `direction`, `hops`, and `edge_match`:

```json
[{"type": "Edge", "direction": "undirected", "hops": 1,
  "edge_match": {"rel_type": "mentioned"}}]
```

`direction` must be `forward`, `reverse`, or `undirected`. `both` is invalid and fails.

`Edge` returns its matched relationship subgraph — it does **not** project a single endpoint kind.
Both endpoints come back. To isolate one kind, use `Let`/`Ref` below.

## Call

Every row-pipeline step is a `Call`. A bare `{"type": "rows"}`, `{"type": "group_by"}`,
`{"type": "order_by"}`, or `{"type": "limit"}` is invalid.

```json
[{"type":"Call","function":"rows","params":{"table":"edges"}},
 {"type":"Call","function":"group_by","params":{"keys":["<edge_column>"],"aggregations":[["n","count"]]}},
 {"type":"Call","function":"order_by","params":{"keys":[["n","desc"]]}},
 {"type":"Call","function":"limit","params":{"value":20}}]
```

`rows` defaults to `table: "nodes"`. Set it to the table holding the columns you group by, or the
query fails on a missing column.

`aggregations` is a list of `[output_name, function]` pairs. `order_by` `keys` is a list of
`[column, direction]` pairs.

Graph filters (`filter_nodes_by_dict`, `filter_edges_by_dict`) must precede `rows`. Placed after
it they are ignored and the aggregation reports unfiltered counts.

`where_rows` takes an `expr` string such as `"n > 10"`. A `filter_dict` argument matches nothing.

## Let and Ref

Isolate one endpoint kind: bind the edge subgraph, then filter that binding through the `Ref`'s
`chain`. Pass as a **top-level object, never wrapped in an array**:

```json
{"type":"Let","bindings":{
  "connections":{"type":"Edge","direction":"undirected","hops":1,"edge_match":{"<edge_column>":"<observed_value>"}},
  "requested_endpoints":{"type":"Ref","ref":"connections","chain":[{"type":"Node","filter_dict":{"<node_kind_column>":"<observed_kind>"}}]}}}
```

Use this when the request names one endpoint kind modified by a relationship — "accounts connected
by transfers" wants accounts, not the transfers and their far side.

When the request instead names two kinds joined by "and"/"or", use an `Edge` followed by an empty
`Node` so both sides accumulate.

## Cypher

`query_graph` also accepts one whole read-only Cypher string in place of the operation list. One
statement per call; no writes.

## Output

`output_type` selects what comes back: `shape` (default, counts only), `nodes`, `edges`, or `all`.
Use `nodes` or `edges` to read actual values — `shape` on an aggregation returns the number of
aggregation rows, not the values inside them, which is an easy way to misread a result.
