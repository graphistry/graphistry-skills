# GFQL wire format

Full JSON forms for `gfql_operations`. The decision-critical rules live in `SKILL.md`; this file
holds the complete examples.

`gfql_operations` is always a **JSON-encoded string**, never a nested object. The operation types
you need are `Node`, `Edge`, `Call`, `Let`, and `Ref`.

## Node

Filters nodes. Equality against a stored value:

```json
[{"type": "Node", "filter_dict": {"category": "Malware"}}]
```

Threshold with a predicate object. The predicate goes inside `filter_dict`, keyed by column:

```json
[{"type": "Node", "filter_dict": {"event_count": {"type": "GT", "val": 10}}}]
```

Predicate `type` names are **case-sensitive** — `GT` works, `gt` fails with an opaque error — and
the key carrying the operand differs by family:

| Family | Types | Operand key |
|---|---|---|
| comparison | `GT` `LT` `GE` `LE` `EQ` `NE` | `val` |
| range | `Between` | `lower`, `upper` |
| set | `IsIn` | `options` |
| string | `Contains` `Startswith` `Endswith` `Match` `Fullmatch` | `pat` |
| null | `IsNA` `NotNA` `IsNull` `NotNull` | none |
| shape | `IsNumeric` `IsAlpha` `Duplicated` and similar | none |

The server normalizes casing and key names only for `filter_dict` on a top-level operation array.
Inside `edge_match`, inside a `Let`, and anywhere in `create_collection`, write the exact form.

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

This chain is a `query_graph` answer, not a collection. It aggregates away the node id, so
`create_collection` refuses it — color the nodes with a separate `Node` filter built from the
values it returns.

`aggregations` is a list of `[alias, function, column]` triples. Only `count` may be the
2-element `[alias, "count"]`; every other function — `count_distinct`, `sum`, `min`, `max`, `avg`,
`mean`, `collect`, `collect_distinct` — requires the column it aggregates, and `"*"` is rejected
for them. Counting rows where the question asked for distinct values returns a plausible table
answering a different question.

`order_by` `keys` is a list of `[column, direction]` pairs; the direction is mandatory and must be
`asc` or `desc`.

Put graph filters (`filter_nodes_by_dict`, `filter_edges_by_dict`) before `rows`. After a `rows`
on the edge table the filter is dropped and the aggregation reports unfiltered counts.

`where_rows` accepts `expr` (a string like `"n > 10"`) and `filter_dict`. In `filter_dict` only
exact stored values match, so a predicate object there matches nothing; use `expr` to compare.

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

`query_graph` accepts one whole read-only Cypher string in place of the operation list. One
statement per call; no writes. `create_collection` does not — it takes JSON GFQL only.

## Output

`output_type` selects what comes back: `shape` (default, counts only), `nodes`, `edges`, or `all`.
Use `nodes` or `edges` to read actual values — `shape` on an aggregation returns the number of
aggregation rows, not the values inside them, which is an easy way to misread a result.

Rows are capped at 50 when the expression names columns and 20 when it does not, and are projected
to the id column plus the columns the expression referenced. The reported count is the true total,
so a group_by with more distinct values than the cap is truncated: a value list read from it cannot
prove that some value is absent.
