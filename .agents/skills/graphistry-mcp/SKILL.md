---
name: graphistry-mcp
description: "Drive a live Graphistry visualization session from any MCP client. Covers connecting to the viz MCP endpoint, personal-key and JWT auth, session ownership, the tool surface, and GFQL sent as JSON over the wire. Use when an external agent must query or recolor the graph a user is currently looking at."
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

Streamable HTTP at `POST /mcp`. `tools/call` carries a credential on the `Authorization` header;
`initialize` and `tools/list` do not.

Two credentials work. Prefer a personal key: it does not expire, so a long-running agent will not
start returning `401` partway through a conversation the way a JWT does.

| Credential | Header | Expires |
|---|---|---|
| Personal key `key_id:key` | `Authorization: Bearer <key_id>:<key>` or `PersonalKey <key_id>:<key>` | no |
| Viewer JWT | `Authorization: Bearer <jwt>` | yes, about an hour |

Create a personal key on the Graphistry account page at `/users/personal/key/`. Both schemes are
accepted for it because most MCP clients only expose a single "Bearer token" field.

```bash
curl -si https://<host>/mcp \
  -H "Authorization: Bearer $GRAPHISTRY_PERSONAL_KEY" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{
        "protocolVersion":"2024-11-05","capabilities":{},
        "clientInfo":{"name":"my-agent","version":"1.0"}}}'
```

`initialize` returns an `Mcp-Session-Id` response header. Send it back as the `mcp-session-id`
header on every subsequent request. This is the MCP transport session and is distinct from the
Graphistry viz `session_id` the tools take. If it expires the server answers `404` — reinitialize
and retry rather than treating the call as failed.

The server currently reports protocol version `2024-11-05`.

Client config for MCP-aware tools:

```json
{
  "mcpServers": {
    "graphistry": {
      "type": "http",
      "url": "https://<host>/mcp",
      "headers": { "Authorization": "Bearer ${GRAPHISTRY_PERSONAL_KEY}" }
    }
  }
}
```

## Session model

Tools other than `list_sessions` require a `session_id` identifying a live viz session.

- **A client cannot create a session.** A session exists because a user has the graph open in a
  browser. Discover one with `list_sessions`.
- **Pass the session you were given.** `list_sessions` returns bare ids with nothing to tell them
  apart, so when a user has two graphs open an agent that discovers one instead of using the one it
  was handed will silently answer about the wrong graph. A client that knows which graph is on
  screen should supply `session_id` rather than discover it.
- **Only the owner may mutate.** The credential's user must be the user whose browser holds that
  session, or the collection tools return
  `403 Forbidden: only the session owner may modify this session`. Reads may still succeed for a
  non-owner who has access to the underlying dataset; without it they return
  `403 Forbidden: caller cannot access this session`. `list_sessions` shows only the caller's own
  sessions, so a shared service account will not see an end user's session.
- **A closed tab means no session.** With no live owner the call returns
  `410 Session owner unavailable`. A `410` can also mean the owner lookup itself failed, so retry
  once before concluding the graph is gone.
- **`list_sessions` can return `[]` while your session is alive.** It sees only the sessions owned
  by the server process that happened to receive the request. Emptiness is not evidence of no
  session — another reason to pass the `session_id` you were given.

Other statuses a client must tell apart:

| Status | Meaning | Retry? |
|---|---|---|
| `403 Talk2Graph is not enabled for this account` | credential is valid, the account lacks the entitlement | no — every `tools/call` will fail |
| `503 Entitlement check unavailable` | the access check itself failed | yes |
| `504 Tool call timeout` | the owning process did not answer in time | yes |
| `400 Missing mcp-session-id` | the header was absent | send the header; this is not the 404 case |
| `404 Unknown or expired mcp-session-id` | the transport session lapsed | reinitialize |

The transport session expires after 5 minutes idle, sliding on each use, so a slow agent should
expect a `404` and reinitialize rather than treat it as a failure. A revoked credential keeps
working for up to 60 seconds because verification is cached.

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

`query_graph` returns at most 50 rows when the expression names columns and 20 when it does not,
projected to the id column plus the columns the expression referenced; the reported count is the
true total. A value list read from a truncated result cannot prove that a value is absent.

`create_collection` keeps at most 10 collections, evicting the oldest, replaces any existing
collection of the same name, and returns a cached result for an identical call repeated within
30 seconds. `list_collections` reports only collections this MCP session created, never ones the
user made in the browser, and it is emptied when the user's socket reconnects.

`gfql_operations` is a **JSON-encoded string**, not a nested object. `order` lists collection ids
top-to-bottom; the first renders on top. For a solid color pass a hex `node_color`; use `palette`
only when a named palette is explicitly requested. On `update_collection`, omit a field to leave
it unchanged — do not pass `null`.

## GFQL over the wire

Sent as a JSON string. The operation types you need are `Node`, `Edge`, `Call`, `Let`, and `Ref`.

```json
[{"type": "Node", "filter_dict": {"category": "Malware"}}]
```

`Node` filters; a predicate object such as `{"type": "GT", "val": 10}` inside `filter_dict`
thresholds. `Edge` traverses and returns its matched relationship subgraph — it does not project a
single endpoint kind. Every row-pipeline step (`rows`, `group_by`, `order_by`, `limit`) is a
`Call`. `Let` with a `Ref` isolates one endpoint kind and is passed as a **top-level object, never
wrapped in an array**. `query_graph` also accepts one read-only Cypher string.

Full JSON for each form, including the aggregation pipeline and the `Let`/`Ref` projection:
`references/gfql-wire-format.md`.

## Shapes that fail silently

These return `success: true` with wrong or empty results rather than erroring. **A zero-row answer
produced by any of them is not evidence of a real zero.**

- `filter_nodes_by_dict` / `filter_edges_by_dict` match exact stored values only. A predicate
  object matches nothing — threshold with a `Node` operation instead.
- "External/public IP" and "internal/private IP" are derived properties, not requirements for
  a dedicated status column. Inspect the live schema and values for the actual IP column first.
  Unless the dataset documents another policy, treat RFC1918 IPv4 (`10/8`, `172.16/12`,
  `192.168/16`), loopback, link-local, unspecified, multicast, and shared CGNAT (`100.64/10`)
  as non-external; apply analogous IPv6 ULA/link-local/loopback/unspecified/multicast rules.
  Documentation/reserved examples such as `198.51.100.0/24` and `203.0.113.0/24` are not
  RFC1918 internal addresses, so do not silently discard them unless the dataset explicitly
  defines them as non-external fixtures. Match the exact stored representation; do not apply
  IPv4 rules to IPv6, host:port, URL, or CIDR strings without validating them. Use a positive
  GFQL pattern where supported, or `IsIn` only from an exhaustive value set. A limited/sample
  table cannot prove a complement; if the value set is truncated or GFQL cannot express the
  classification, report that limitation instead of claiming a complete collection.
- Put both graph filters before `rows`. After a `rows` on the edge table a filter is dropped and
  the aggregation reports unfiltered counts.
- `where_rows` accepts `expr` (a string like `"n > 10"`) and `filter_dict`. In `filter_dict` only
  exact stored values match, so a predicate object there matches nothing; use `expr` to compare.
- `get_session_info` returns column names only, never stored values, so it can never establish
  that a value is absent.

## Errors you will actually see

These fail loudly with a specific message. Read it — it names the cause, so it is worth acting on
rather than rewriting the expression blindly.

- `rows` defaults to `table: "nodes"`. Grouping by an edge column without `{"table": "edges"}`
  fails as a missing column.
- `Edge` requires `direction`, one of `forward`, `reverse`, `undirected`. `both` is invalid.
  `create_collection` fills in `undirected` when it is absent, so an expression that validated
  there can still fail in `query_graph` — set it explicitly.
- A bare `{"type": "rows"}`, `{"type": "group_by"}`, `{"type": "order_by"}`, or
  `{"type": "limit"}` is invalid. Wrap every one as a `Call`.
- Predicate `type` names are case-sensitive: `GT` works, `gt` fails with an opaque error.
- `create_collection` takes JSON GFQL only. Cypher is accepted by `query_graph` alone.
- `create_collection` refuses an expression whose result stops identifying graph nodes — one that
  groups rows, projects the id away, renames or drops it, or reads the edge table. Ordering by a
  community column is refused separately, because that ranks by community id rather than size. Both
  refusals name the repair: select the nodes themselves, usually a `Node` filter, or report the
  sizes with `query_graph` instead. Act on it rather than reporting failure.
- If a collection is refused because the service could **not evaluate** the expression, that is a
  different case: report the failure. Do not reword the filter and retry — the expression was not
  the problem.

## Workflow

1. `list_sessions` to find the live session.
2. `get_session_info` for the schema. Choose columns from the list it returns, most useful first.
   If a line ends with `(+K more not listed)` the list is truncated and the count in parentheses is
   the real total — a column's absence from the list is not evidence it does not exist, so ask
   rather than invent a name. `unavailable (schema could not be read)` means the schema was never
   read; treat that as a failed inspection, not as a graph without columns. Being listed is
   necessary but not sufficient: some columns are computed for rendering and cannot be filtered.
3. **Inspect stored values before filtering on them.** Natural-language nouns from the user are
   unobserved candidates, never literals. Aggregate the distinct values of the relevant column
   first and compare case-sensitively — `Hashtag` will not match a search for `hashtag`.
4. Validate the expression with `query_graph` before mutating.
5. `create_collection` reusing that exact validated JSON unchanged, and report the match count it
   returns. `create_collection` accepts a narrower set of shapes than `query_graph` validates: a
   chain that aggregates or leaves the node axis will pass `query_graph` and still be refused here.
   When that happens the refusal names the repair — use it. The count is not guaranteed — when
   the preflight cannot produce one the collection is still applied and the reply says so. Report "applied, count unavailable" rather than inventing
   a number or omitting the outcome.

Stop and report a GFQL error rather than retrying with an invented operation name. A failed query
is not an inspection result.

Zero rows never establishes absence when any value in the expression came from the user's wording
rather than from a tool result. Confirm every value was tool-observed before reporting an empty
result.

## Decision Rules

- Use this skill when the graph is already open and the task is to query or recolor it.
- Route to `pygraphistry-gfql` for GFQL written as Python AST objects (`n()`, `e_forward()`) or
  for `g.gfql()` in a notebook. This skill covers the JSON wire format only.
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

- Graphistry Hub docs: https://hub.graphistry.com/docs/
- MCP specification: https://modelcontextprotocol.io/specification/
- REST auth docs: https://hub.graphistry.com/docs/api/1/rest/auth/
