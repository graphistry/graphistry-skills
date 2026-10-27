---
name: graphistry-mcp
description: "Drive a live Graphistry visualization session from any MCP client. Covers connecting to the viz MCP endpoint, personal-key and JWT auth, session ownership, the tool surface, and the Cypher subset the server runs. Use when an external agent must query or recolor the graph a user is currently looking at."
---

# Graphistry MCP

## Scope

Use this skill to operate a **live Graphistry visualization session** from an MCP client: inspect
its schema, run Cypher queries against it, and create colored collections the user sees update in
their browser.

Needs a server whose `create_collection` accepts Cypher. On an older server `create_collection`
fails with "requires JSON GFQL" and `get_session_info` has no `Node id column:` line.

## Connect

Streamable HTTP at `POST /mcp`. Send the credential on `tools/call` as
`Authorization: Bearer <key_id>:<key>` (a personal key, which does not expire; create one at
`/users/personal/key/`) or `Authorization: Bearer <jwt>` (expires in about an hour). `initialize`
returns an `Mcp-Session-Id` header; send it back as `mcp-session-id` on every request, and when the
server answers `404` for it, reinitialize and retry.

Tools other than `list_sessions` take a `session_id` for a graph a user has open in a browser; a
client cannot create one. Pass the `session_id` you were given rather than discovering one:
`list_sessions` returns bare ids and can be empty while the session is alive. Only the session's
owner may change collections. A `410` means the owner's tab is gone or the lookup failed; retry once.
Curl and client-config examples, every status code, and timeouts are in
`references/connection.md`.

## Tool surface

Read:

| Tool | Required | Optional |
|---|---|---|
| `list_sessions` | — | — |
| `get_session_info` | `session_id` | — |
| `query_graph` | `session_id`, `gfql_operations` | `output_type` (`shape` default, `nodes`, `edges`, `all`), `format` |
| `list_collections` | `session_id` | — |

Mutate (these change what the user sees):

| Tool | Required | Optional |
|---|---|---|
| `create_collection` | `session_id`, `name`, `gfql_operations`, and one of `node_color` / `palette` | the other of `node_color` / `palette`, `description` |
| `update_collection` | `session_id`, `collection_id` | `name`, `node_color`, `palette` |
| `delete_collection` | `session_id`, `collection_id` | — |
| `reorder_collections` | `session_id`, `order` | — |
| `reset_collections` | `session_id` | — |

`create_collection` keeps at most 10 collections, dropping the bottom one, replaces any collection
of the same name, and returns a cached result for an identical call repeated within 30 seconds. Every
change through these tools replaces the session's whole collection list, so collections the user
made in the browser are removed. `list_collections` reports only collections these tools
created, and it is emptied when the user's socket reconnects.

`gfql_operations` is a string holding one Cypher query. Send Cypher only, never JSON, even when an
error mentions JSON. `order` lists collection ids
top-to-bottom; the first renders on top. For a solid color pass a hex `node_color`; use `palette`
only when a named palette is explicitly requested. On `update_collection`, omit a field to leave
it unchanged — do not pass `null`.

## Query in Cypher

Write every query as one read-only Cypher string. Graphistry runs a **subset of openCypher**:
the server transpiles it into
[GFQL](https://github.com/graphistry/pygraphistry), Graphistry's open-source graph query
language, and runs that.

**At most one relationship per query, always directed:** `(a)-[e]->(b)` or `(a)<-[e]-(b)`,
counting every `MATCH` and `OPTIONAL MATCH`. Undirected patterns, any variable length (`[*]`,
`[*1..n]`), and a second relationship anywhere in the query, such as `(a)-->(b)-->(c)`, can return
wrong rows without an error: go one directed hop per query, collect the ids, and start the next
hop from `WHERE a.<id_column> IN [...]`.

Most other unsupported queries fail with an error, but these mistakes also return wrong rows
without one:

- A value of the wrong type for the column, from its type in `get_session_info`. A `date` column
  takes an ISO string, `e.time >= '2023-12-09'`; a number column takes a number, `n.score > 10`,
  and an epoch column an epoch number in its unit: check its range first, since seconds against
  milliseconds match everything or nothing. A quoted number, or a date written for a column of
  another type, matches nothing. A number stored as text (`string`) sorts as text: convert it,
  `RETURN toFloat(n.rank) AS r ORDER BY r DESC`.
- A whole-number id longer than 15 digits, which comes back rounded. Collect
  `toString(n.<id_column>)`, or `toString(nodeId)` after a `CALL`, and filter with
  `WHERE toString(n.<id_column>) IN ['...']`.
- A backslash in a string literal, which `NOT` or `OR` reads twice. Write a regex dot as `[.]`, or
  use `STARTS WITH` or `CONTAINS`: `NOT n.ip =~ '10[.].*'`.
- A pattern in `WHERE`, such as `WHERE NOT (n)-[]->()`, under an aggregate; `collect()` is an
  aggregate too. Count nodes with a pattern with `MATCH (n)-[]->() RETURN count(DISTINCT n)`, and
  nodes without one with `CALL graphistry.degree() YIELD nodeId, degree_out WITH nodeId, degree_out
  WHERE degree_out = 0 RETURN count(*)`; collect through `WITH`:
  `MATCH (n) WHERE NOT (n)-[]->() WITH n.<id_column> AS id RETURN collect(id) AS ids`.

A failed query's error names its cause in brackets. Fix what it names and call again, at most three
times, then report the last error. For `column-not-found`, fix the name from the columns the error
lists; if the column the request needs is not there, including one `get_session_info` lists but the
error does not, say plainly it cannot be done instead of using another column. Degree through
`CALL graphistry.degree()` is the same measure, not a substitution. Never retry with an invented
operation name.

`<id_column>` below is the column on the `Node id column:` line of `get_session_info`; filtering
another column by id matches nothing. A column named `id` that is not on that line can be a row
number the server adds (0 to N-1), not an id. Copy each id exactly as returned: a string stays
quoted, a number unquoted, and never strip a prefix or reshape an id to fit another column.

```cypher
MATCH (n) RETURN count(DISTINCT n.kind) AS k
MATCH (n) RETURN n.kind AS v, count(*) AS c ORDER BY c DESC LIMIT 20
MATCH ()-[e]->() RETURN e.rel AS v, count(*) AS c ORDER BY c DESC LIMIT 20
MATCH (n) WHERE n.score > 10 RETURN n.<id_column> AS id, n.score AS s ORDER BY s DESC LIMIT 10
MATCH (a)-[e]->(b) WHERE e.rel = 'mentions' RETURN DISTINCT b.<id_column> AS id
CALL graphistry.degree() YIELD nodeId, degree RETURN nodeId, degree ORDER BY degree DESC LIMIT 10
CALL graphistry.igraph.pagerank() YIELD nodeId, pagerank RETURN nodeId, pagerank ORDER BY pagerank DESC LIMIT 10
CALL graphistry.igraph.community_multilevel({directed: false}) YIELD nodeId, community_multilevel
  RETURN community_multilevel AS community, count(*) AS size ORDER BY size DESC LIMIT 10
```

Pass `output_type: "nodes"` to read rows; the default `shape` returns counts only. A result shows at
most 20 rows, and a `LIMIT` also caps the reported count, so count values with `count(DISTINCT ...)`
before listing them; a cut list cannot prove a value is absent. Return named properties
(`RETURN n.<id_column> AS id`) rather than whole nodes, which return every column.

## Supported Cypher

| Supported | Not supported, and what to write instead |
|---|---|
| `MATCH`, `WHERE`, `RETURN`, `WITH`, `ORDER BY`, `SKIP`, `LIMIT`, `DISTINCT` | writes: `CREATE`, `DELETE`, `SET`, `MERGE` |
| `count`, `sum`, `avg`, `min`, `max`, `collect` | `ORDER BY` a column you did not return: return it, then order by its alias |
| two node-only patterns in one `MATCH (a), (b)` | a second `MATCH` that shares no alias with the first: write one `MATCH (a), (b)`, with no relationship in it |
| `OPTIONAL MATCH`, `UNWIND`, `UNION` (partial), `IN [...]`, `IS NULL`, `CONTAINS`, `STARTS WITH`, `=~`, `toLower()` | `toLower()` in a query with a relationship: match the exact stored value |
| a column name containing `.` or `-`, in backticks: ``n.`user.name` `` | |
| `CALL graphistry.degree()`, `CALL graphistry.igraph.<algorithm>()` | `graphistry.nx.*` procedures are refused; use `graphistry.igraph.*` |
| a label `(n:Hashtag)`, matched against the `type` column | a label with no `type` column fails with `column-not-found` `label__Hashtag` |
| a relationship type `[e:MENTIONS]`, matched against the edge `type` column | a relationship type with no edge `type` column fails with `column-not-found` |
| an edge's properties: `RETURN a.<id_column> AS src, b.<id_column> AS dst, e.rel AS rel` | in `query_graph`, `RETURN e` returns the edge's attributes without its endpoints; in `create_collection` it colors the connections (Coloring) |

`community_multilevel` needs `{directed: false}`, and its community ids change on every run, so
never reuse one from an earlier query. The `degree`, `degree_in`, and `degree_out`
columns `get_session_info` lists exist only for rendering and fail in a query; use
`CALL graphistry.degree()`. Run a `graphistry.igraph.*` call before judging it: only when it fails
with `Vertex attribute conflict` (older servers, on a graph with a `name` node column) report that
the algorithm cannot run, without retrying.

## Coloring

`create_collection` takes Cypher that returns one node alias whole, or the relationship `e` of one
directed hop whole. Cypher with `CALL`, `UNION`, aggregates, projections, or any other pattern is
refused as a collection, and the refusal names the supported shapes; rewrite to one of them rather
than reporting failure. Adding `DISTINCT` to a returned endpoint is the repair only for one
directed relationship.

- the matched nodes: `MATCH (n) WHERE n.score > 10 RETURN n`
- one endpoint of one directed relationship: `MATCH (a)-[e]->(b) WHERE e.rel = 'mentions' RETURN DISTINCT b`
- the connections themselves, when the request asks for connections, or the filtered value lives in
  an edge column and the request names no node kind:
  `MATCH (a)-[e]->(b) WHERE e.rel = 'mentions' RETURN e`. When connections are defined only by their
  endpoints' kinds ("from accounts to hashtags"), filter `a` and `b` and add no edge-value filter,
  which silently drops edges of other types.
  - `ORDER BY`, `LIMIT`, and projections are refused.
  - In `WHERE`, use plain comparisons joined by `AND`, without parentheses. `OR`, `NOT`,
    `toLower()`, arithmetic, and a filter after `WITH` are refused; `IN [...]` works only as the
    only condition.
  - For several values plus another condition, make one collection per value; for both directions
    around a node, one `->` and one `<-` collection.
- anything else, such as a node and its neighbors, a longer path, or nodes a `CALL` ranks or groups:
  collect the ids with `query_graph`, one directed hop at a time, then color the list

```cypher
MATCH (a)-[]->(b) WHERE a.<id_column> = 'x' RETURN collect(DISTINCT b.<id_column>) AS ids
MATCH (b)-[]->(a) WHERE a.<id_column> = 'x' RETURN collect(DISTINCT b.<id_column>) AS ids
CALL graphistry.degree() YIELD nodeId, degree
  WITH nodeId, degree ORDER BY degree DESC LIMIT 50 RETURN collect(nodeId) AS ids
MATCH (n) WHERE n.<id_column> IN ['x', 'a', 'b'] RETURN n
```

The first two collect a node's out- and in-neighbors; color them with the node itself. A top N and
a community are id lists too: rank or group and `collect()` in one query, then color
`MATCH (n) WHERE n.<id_column> IN [...] RETURN n`:

```cypher
CALL graphistry.igraph.pagerank() YIELD nodeId, pagerank
  WITH nodeId, pagerank ORDER BY pagerank DESC LIMIT <N> RETURN collect(nodeId) AS ids
CALL graphistry.igraph.community_multilevel({directed: false}) YIELD nodeId, community_multilevel
  WITH community_multilevel AS c, collect(nodeId) AS ids, count(*) AS size
  ORDER BY size DESC LIMIT 1 RETURN size, ids
// the community containing node 'x'
CALL graphistry.igraph.community_multilevel({directed: false}) YIELD nodeId, community_multilevel
  WITH community_multilevel AS c, collect(nodeId) AS ids WHERE 'x' IN ids RETURN size(ids) AS size, ids
// the highest-degree node in an id list
CALL graphistry.degree() YIELD nodeId, degree
  WITH nodeId, degree WHERE nodeId IN ['a', 'b'] ORDER BY degree DESC LIMIT 1 RETURN nodeId, degree
```

A query is limited to 64 KB. If an `IN` list would pass about 60,000 characters, split it; for a
node's neighbors, color `MATCH (a)-[e]->(b) WHERE a.<id_column> = 'x' RETURN DISTINCT b`, its `<-`
form, and the node itself instead. A session keeps at most 10 collections, so for a list too long
for a few parts, report its size instead of coloring it.

A request colored as several collections (both directions, one per value, a split list) takes one
`create_collection` call per part: give the parts distinct names and the same color, make every
call, and report the distinct total, from the id list when there is one: parts can overlap, so their
counts do not add up. For an id list, the match count should equal the number of ids; if it does
not, re-check the list.

## Workflow

1. Use the `session_id` you were given; call `list_sessions` only when you have none.
2. `get_session_info` for the schema; choose columns only from it. A line ending
   `(+K more not listed)` is truncated, so a missing column is not evidence it does not exist: ask
   rather than invent a name. `unavailable (schema could not be read)` is a failed inspection. It
   lists columns, not stored values, so it never proves a value is absent.
3. **Inspect stored values before filtering on them.** Natural-language nouns from the user are
   unobserved candidates, never literals. Count the distinct values of the relevant column with
   `count(DISTINCT ...)`, then return them, and match them exactly. Look up a named node or word
   directly, since a top-20 list hides the rest. Only in a node-only query, `MATCH (n)`, compare
   `toLower()` on both sides; for free text use `toLower(n.<column>) CONTAINS '<word>'`, which also
   catches plurals. When a word can mean more than one stored set, say which one you counted.
4. **Filter on every node kind the request names**, in every query, rankings included: "top 10
   accounts by followers" needs the kind filter, because other kinds can carry the same column. When
   the request names the kind of the result ("the hashtags X links to"), color those nodes,
   `RETURN DISTINCT b` with a kind filter on `b`, not the connections.
5. Validate with `query_graph` the exact Cypher query you will pass to `create_collection`. Fix
   what any error names and call again.
6. `create_collection` with that exact validated query, and report the match count it returns.
   When the preflight cannot produce a count, the collection is still applied and the reply says
   so: report "applied, count unavailable" rather than inventing a number.

A failed query is not an inspection result. Zero rows never establishes absence when any value in
the query came from the user's wording rather than from a tool result. Confirm every value was
tool-observed before reporting an empty result.

"External/public" and "internal/private" IP are derived properties, not columns; classify the
stored IP values with `references/ip-classification.md`.

## Decision Rules

- Use this skill when the graph is already open and the task is to query or recolor it.
- Route to `pygraphistry-gfql` for GFQL written as Python AST objects (`n()`, `e_forward()`) or
  for `g.gfql()` in a notebook. This skill covers the MCP tools only.
- Route to `pygraphistry`, or the separate PyGraphistry MCP (`github.com/graphistry/graphistry-mcp`),
  to build or upload a graph.
- Route to `graphistry-rest-api` for auth, upload, and dataset endpoints.

## Safety Rules

- Keep credentials in environment variables. Never hardcode a username, password, personal key, or
  JWT.
- Send the credential in the `Authorization` header. Never put one in a URL query parameter. No
  documented tool parameter takes a credential, so it stays out of the model's context — never
  add one to `arguments` yourself.
- Treat mutation tools as user-visible: only create, update, or delete a collection when the user
  asked to change the visualization.

## References

- `references/connection.md`: credentials, transport session, session ownership, status codes.
- `references/ip-classification.md`: external/internal IP rules.
- Graphistry Hub docs: https://hub.graphistry.com/docs/
- MCP specification: https://modelcontextprotocol.io/specification/
- REST auth docs: https://hub.graphistry.com/docs/api/1/rest/auth/
