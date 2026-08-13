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

Streamable HTTP at `POST /mcp`. Every request carries a credential on the `Authorization` header.

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

`initialize` and `tools/list` need no credential; `tools/call` requires one.

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
  `410 Session owner unavailable`. Reconnect after the user reopens the graph.

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
| `create_collection` | `session_id`, `name`, `gfql_operations` | `node_color`, `palette`, `description` |
| `update_collection` | `session_id`, `collection_id` | `name`, `node_color`, `palette` |
| `delete_collection` | `session_id`, `collection_id` | — |
| `reorder_collections` | `session_id`, `order` | — |
| `reset_collections` | `session_id` | — |

`gfql_operations` is a **JSON-encoded string**, not a nested object. `order` lists collection ids
top-to-bottom; the first renders on top. For a solid color pass a hex `node_color`; use `palette`
only when a named palette is explicitly requested. On `update_collection`, omit a field to leave
it unchanged — do not pass `null`.

## GFQL over the wire

Sent as a JSON string. Only five operation types are valid: `Node`, `Edge`, `Call`, `Let`, `Ref`.

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
- Both graph filters must precede `rows`. Placed after it they are ignored and the aggregation
  reports unfiltered counts.
- `where_rows` takes an `expr` string such as `"n > 10"`. A `filter_dict` argument matches nothing.
- `rows` defaults to `table: "nodes"`. Set it to the table holding the columns you group by, or
  the query fails on a missing column.
- `Edge` `direction` must be `forward`, `reverse`, or `undirected`. `both` is invalid and fails.
- A bare `{"type": "rows"}`, `{"type": "group_by"}`, `{"type": "order_by"}`, or
  `{"type": "limit"}` is invalid. Wrap every one as a `Call`.
- `get_session_info` returns column names only, never stored values, so it can never establish
  that a value is absent.

## Workflow

1. `list_sessions` to find the live session.
2. `get_session_info` for the schema. Choose columns only from what it returns.
3. **Inspect stored values before filtering on them.** Natural-language nouns from the user are
   unobserved candidates, never literals. Aggregate the distinct values of the relevant column
   first and compare case-sensitively — `Hashtag` will not match a search for `hashtag`.
4. Validate the expression with `query_graph` before mutating.
5. `create_collection` reusing that exact validated JSON unchanged, and report the match count it
   returns.

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
- Send the credential in the `Authorization` header. Never put one in a URL query parameter. No tool
  takes a credential as a parameter, so it stays out of the model's context.
- Treat mutation tools as user-visible: only create, update, or delete a collection when the user
  asked to change the visualization.

## References

- Graphistry Hub docs: https://hub.graphistry.com/docs/
- MCP specification: https://modelcontextprotocol.io/specification/
- REST auth docs: https://hub.graphistry.com/docs/api/1/rest/auth/
