---
name: graphistry-mcp
description: "Drive a live Graphistry visualization session from any MCP client. Covers connecting to the viz MCP endpoint, personal-key and JWT auth, session ownership, the tool surface, and the Cypher subset the server runs. Use when an external agent must query or recolor the graph a user is currently looking at."
---

# Graphistry MCP

## Scope

Use this skill to operate a **live Graphistry visualization session** from an MCP client: inspect
its schema, run GFQL queries against it, and create colored collections the user sees update in
their browser.

## Two servers share the name "graphistry mcp"

Pick the right one before writing any code.

| Server | Use it for |
|---|---|
| **Viz MCP** — `https://<graphistry-host>/mcp` | Reading and mutating the graph a user already has open. Session-scoped. **This skill.** |
| **PyGraphistry MCP** — `github.com/graphistry/graphistry-mcp` | Building and uploading new visualizations from scratch. Hub-scoped, unrelated to this skill. |

If the task starts from a graph the user is looking at, use the viz MCP. If it starts from a
DataFrame or a file, use the PyGraphistry MCP or the `pygraphistry` skill.

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

`create_collection` keeps at most 10 collections, evicting the oldest, replaces any existing
collection of the same name, and returns a cached result for an identical call repeated within
30 seconds. `list_collections` reports only collections this MCP session created, never ones the
user made in the browser, and it is emptied when the user's socket reconnects.

`gfql_operations` is a string: one Cypher query, or JSON-encoded GFQL. `order` lists collection ids
top-to-bottom; the first renders on top. For a solid color pass a hex `node_color`; use `palette`
only when a named palette is explicitly requested. On `update_collection`, omit a field to leave
it unchanged — do not pass `null`.

## Query in Cypher

Write every query as one read-only Cypher string. Graphistry runs a **subset of openCypher**
(neo4j-style syntax and functions): the server transpiles it into
[GFQL](https://github.com/graphistry/pygraphistry), Graphistry's open-source graph query
language, and runs that. A query outside the subset fails with an error. Two comparisons fail
silently instead, matching nothing: a date column against epoch milliseconds, and a number column
against a quoted string (`n.score > '10'`).

When a query fails, the tool returns the error from transpiling or from running the GFQL, and it
names the construct: `invalid-cypher-syntax`, `unsupported-cypher-query` with the clause, or
`column-not-found` with the column. Other failures, such as a refused procedure or an algorithm
error, carry their own message. Fix that construct and call again; after three failed attempts,
report the last error. If the error means the request cannot be satisfied as asked (an unreadable
or missing column, an unsupported operation), say plainly it cannot be done instead of retrying or
substituting a different column; computing the same measure another way, such as degree through
`CALL graphistry.degree()`, is not a substitution. Never answer an error by retrying with an
invented operation name.

```cypher
MATCH (n) RETURN n.kind AS v, count(*) AS c ORDER BY c DESC LIMIT 20
MATCH ()-[e]->() RETURN e.rel AS v, count(*) AS c ORDER BY c DESC LIMIT 20
MATCH (n) WHERE n.score > 10 RETURN n.id AS id, n.score AS s ORDER BY s DESC LIMIT 10
MATCH (a)-[e]->(b) WHERE e.rel = 'mentions' RETURN DISTINCT b.id AS id
CALL graphistry.degree() YIELD nodeId, degree RETURN nodeId, degree ORDER BY degree DESC LIMIT 10
CALL graphistry.igraph.pagerank() YIELD nodeId, pagerank RETURN nodeId, pagerank ORDER BY pagerank DESC LIMIT 10
CALL graphistry.igraph.community_multilevel({directed: false}) YIELD nodeId, community_multilevel
  RETURN community_multilevel AS community, count(*) AS size ORDER BY size DESC LIMIT 10
```

Pass `output_type: "nodes"` to read rows; the default `shape` returns counts only. A Cypher result
holds the columns you `RETURN`, capped at 20 rows, and the reported count is the true total, so a
truncated value list cannot prove a value is absent. Return named properties (`RETURN n.id AS id`)
rather than whole nodes, which return every column.

## Supported Cypher

| Supported | Not supported, and what to write instead |
|---|---|
| `MATCH`, `WHERE`, `RETURN`, `WITH`, `ORDER BY`, `SKIP`, `LIMIT`, `DISTINCT` | writes: `CREATE`, `DELETE`, `SET`, `MERGE` |
| `count`, `sum`, `avg`, `min`, `max`, `collect` | `ORDER BY` a column you did not return: return it, then order by its alias |
| directed and undirected single-hop patterns, `[*1..3]` variable length | `RETURN n.id, count(r)` over `(n)-[r]-()`: `WITH n, count(r) AS d RETURN n.id AS id, d` |
| `OPTIONAL MATCH`, `UNWIND`, `UNION` (partial) | several disconnected `MATCH` patterns joined together: split into separate queries |
| `IN [...]`, `IS NULL`, `CONTAINS`, `STARTS WITH`, `=~`, `toLower()` | a column whose name contains `.` or `-`: no quoting is supported; use a JSON `Node` filter |
| `CALL graphistry.degree()`, `CALL graphistry.igraph.<algorithm>()` | `graphistry.nx.*` procedures are refused; use `graphistry.igraph.*` |
| comparing a date column to an ISO string, `e.time >= '2023-12-09'` | comparing a date column to epoch milliseconds matches nothing, silently |
| a label `(n:Hashtag)`, matched against the `type` column | a label with no `type` column fails with `column-not-found` `label__Hashtag` |
| a relationship type `[e:MENTIONS]`, matched against the edge `type` column | a relationship type with no edge `type` column fails with `column-not-found` |
| an edge's properties: `RETURN a.id AS src, b.id AS dst, e.rel AS rel` | `RETURN e` returns the edge's attributes without its endpoints |

`community_multilevel` needs `{directed: false}`, and its community ids are relabeled on every run, so
compute and filter a community in one query rather than reusing an id from an earlier one. The `degree`, `degree_in`, and `degree_out`
columns `get_session_info` lists exist only for rendering and fail in a query; use
`CALL graphistry.degree()`. Being listed is necessary but not sufficient. A misspelled or absent
column fails with `column-not-found`.

## Coloring

`create_collection` takes Cypher that returns one node alias whole:

- the matched nodes themselves: `MATCH (n) WHERE n.score > 10 RETURN n`
- one endpoint of a pattern, with `DISTINCT`: `MATCH (a)-[e]->(b) WHERE e.rel = 'mentions' RETURN DISTINCT b`
- up to 20 ids a query returned: `MATCH (n) WHERE n.id IN ['a', 'b'] RETURN n` (a Cypher result shows
  at most 20 rows, so a longer list is incomplete)

For the edges themselves, a neighborhood that includes its anchor, or a ranked top-N larger than
20, use the JSON GFQL shape in `references/gfql-wire-format.md`: an `Edge` chain, an anchor `Node`
then `Edge` then empty `Node`, or a `compute_igraph` ranking chain. Cypher with `CALL`, `UNION`,
aggregates, projections, or an endpoint returned without `DISTINCT` is refused as a collection, and
the refusal names the repair; act on it rather than reporting failure.

## When to read the GFQL reference

`references/gfql-wire-format.md` documents the GFQL that Cypher transpiles into, as JSON. Read it
only when you need a shape the Cypher subset cannot express (the coloring shapes above, a dotted
column name), when an error names a GFQL operation rather than a Cypher clause, or when you are
unsure how a Cypher query will be evaluated. It also lists the JSON shapes that return wrong or
empty results without erroring.

## Workflow

1. Use the `session_id` you were given; call `list_sessions` only when you have none.
2. `get_session_info` for the schema. Choose columns from the list it returns, most useful first.
   If a line ends with `(+K more not listed)` the list is truncated and the count in parentheses is
   the real total — a column's absence from the list is not evidence it does not exist, so ask
   rather than invent a name. `unavailable (schema could not be read)` means the schema was never
   read; treat that as a failed inspection, not as a graph without columns. It lists columns, not
   every stored value, so it can never establish that a value is absent.
3. **Inspect stored values before filtering on them.** Natural-language nouns from the user are
   unobserved candidates, never literals. Return the distinct values of the relevant column first
   and match them exactly, or compare `toLower()` on both sides.
4. Validate with `query_graph` the exact expression you will pass to `create_collection` — the
   Cypher query, or the JSON shape when Coloring calls for one. Fix what any error names and call
   again.
5. `create_collection` reusing that exact validated expression, and report the match count it
   returns. `create_collection` accepts a narrower set of shapes than `query_graph` validates; when
   it refuses, the refusal names the repair — use it. The count is not guaranteed — when the
   preflight cannot produce one the collection is still applied and the reply says so. Report
   "applied, count unavailable" rather than inventing a number or omitting the outcome.

A failed query is not an inspection result. Zero rows never establishes absence when any value in
the query came from the user's wording rather than from a tool result. Confirm every value was
tool-observed before reporting an empty result.

"External/public" and "internal/private" IP are derived properties, not columns; classify the
stored IP values with `references/ip-classification.md`.

## Decision Rules

- Use this skill when the graph is already open and the task is to query or recolor it.
- Route to `pygraphistry-gfql` for GFQL written as Python AST objects (`n()`, `e_forward()`) or
  for `g.gfql()` in a notebook. This skill covers the MCP tools only.
- Route to `pygraphistry` to build or upload a graph.
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
- `references/gfql-wire-format.md`: the GFQL that Cypher transpiles into, as JSON, and its pitfalls.
- `references/ip-classification.md`: external/internal IP rules.
- Graphistry Hub docs: https://hub.graphistry.com/docs/
- MCP specification: https://modelcontextprotocol.io/specification/
- REST auth docs: https://hub.graphistry.com/docs/api/1/rest/auth/
