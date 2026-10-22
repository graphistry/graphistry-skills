# Connecting and sessions

Full connection, credential, session, and status details for the viz MCP. `SKILL.md` keeps the
rules an agent needs on every call; read this when connecting a new client or when a call returns a
status `SKILL.md` does not explain.

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
