# GFQL wire format

The GFQL that the server's Cypher transpiles into, written as JSON. `SKILL.md` covers the Cypher
entry point; read this only when Cypher cannot express a shape, when an error names a GFQL operation,
or when you are unsure how a query is evaluated.

JSON GFQL is passed as a **JSON-encoded string**, never a nested object. The operation types
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

Predicate `type` names are **case-sensitive** — `GT` works; `gt` is corrected only in a top-level
`filter_dict` passed to `query_graph` and fails everywhere else — and the key carrying the operand
differs by family:

| Family | Types | Operand key |
|---|---|---|
| comparison | `GT` `LT` `GE` `LE` `EQ` `NE` | `val` |
| range | `Between` | `lower`, `upper` |
| set | `IsIn` | `options` |
| string | `Contains` `Startswith` `Endswith` `Match` `Fullmatch` | `pat` |
| null | `IsNA` `NotNA` `IsNull` `NotNull` | none |
| shape | `IsNumeric` `IsAlpha` `Duplicated` and similar | none |

The server normalizes predicate-name casing — and, for string predicates only, fills `pat` from
`val`/`value`/`substring` — for `filter_dict` on a top-level operation array; no other operand key
is corrected, so `value` is never accepted for `val`. Inside `edge_match`, inside a `Let`, and
anywhere in `create_collection`, write the exact form.

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

To color a ranked top-N, compute the metric, order, and limit, and pass the chain unchanged to
`create_collection`. Replace `<N>` with the count the user asked for:

```json
[{"type":"Call","function":"compute_igraph","params":{"alg":"pagerank"}},
 {"type":"Call","function":"order_by","params":{"keys":[["pagerank","desc"]]}},
 {"type":"Call","function":"limit","params":{"value":<N>}}]
```

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

## Shapes that fail silently

These return `success: true` with wrong or empty results rather than erroring. **A zero-row answer
produced by any of them is not evidence of a real zero.**

- `filter_nodes_by_dict` / `filter_edges_by_dict` match exact stored values only. A predicate
  object matches nothing — threshold with a `Node` operation instead.
- Put both graph filters before `rows`. After a `rows` on the edge table a filter is dropped and
  the aggregation reports unfiltered counts.
- `where_rows` accepts `expr` (a string like `"n > 10"`) and `filter_dict`. In `filter_dict` only
  exact stored values match, so a predicate object there matches nothing; use `expr` to compare.

## Errors

These fail loudly. Most messages name the cause, so act on it rather than rewriting the expression
blindly.

- `rows` needs the `table` whose columns you group by — `{"table": "edges"}` for edge columns.
  Omitting `table`, or grouping an edge column under `nodes`, fails.
- `Edge` requires `direction`, one of `forward`, `reverse`, `undirected`. `both` is invalid.
  `create_collection` fills in `undirected` when it is absent, so an expression that validated
  there can still fail in `query_graph` — set it explicitly.
- A bare `{"type": "rows"}`, `{"type": "group_by"}`, `{"type": "order_by"}`, or
  `{"type": "limit"}` is invalid. Wrap every one as a `Call`.
- Predicate `type` names are case-sensitive: `GT` works. `gt` is corrected only in a top-level
  `filter_dict` passed to `query_graph`; everywhere else it fails with an opaque error. Write
  predicates in their exact form before validating.
- `create_collection` refuses an expression whose result stops identifying graph nodes — one that
  groups rows, projects the id away, renames or drops it, or reads the edge table. Ordering by a
  community column is refused separately, because that ranks by community id rather than size. Both
  refusals name the repair: select the nodes themselves, usually a `Node` filter, or report the
  sizes with `query_graph` instead. Act on it rather than reporting failure.
- A collection refused because the service could **not evaluate** the expression quotes the
  service's message. A Mongo-style `$gt`, an invented predicate name, a wrong operand key, a
  lowercase predicate name, or `val` on a string predicate land here with a terse message (`'type'`,
  `'InList'`, `unexpected keyword argument 'values'`); check the expression against the predicate
  table above, fix it, validate it with `query_graph`, and retry. A message that names nothing in
  the expression, or a refusal that says the service returned an error before validating it, is a
  service failure: report it and do not retry.

## Output

`output_type` selects what comes back: `shape` (default, counts only), `nodes`, `edges`, or `all`.
Use `nodes` or `edges` to read actual values — `shape` on an aggregation returns the number of
aggregation rows, not the values inside them, which is an easy way to misread a result.

A JSON result's rows are capped at 50 and projected to the id column plus the columns the
expression filters or groups on (an `order_by` or `edge_match` column it does not also filter is not
kept). A Cypher result, or a JSON result holding none of those columns (an edge result), returns
every column, capped at 20 rows. The reported count is the true total,
so a group_by with more distinct values than the cap is truncated: a value list read from it cannot
prove that some value is absent.
