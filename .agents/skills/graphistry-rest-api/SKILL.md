---
name: graphistry-rest-api
description: "Graphistry Hub REST API specialist for auth, upload lifecycle, URL controls, sessions, and sharing safety. Use for curl/requests endpoint guidance independent of SDK choice."
---

# Graphistry REST API

## Scope
Use this skill for Graphistry REST endpoint tasks, including JWT auth, uploads, graph URL controls, sessions, and token-safe sharing.

## Speed-First Rules
- Default to no shell commands and no local repo lookups; answer from this skill's endpoint map/templates.
- Only inspect local files when the user explicitly asks for source-level proof.
- For constrained prompts (line counts, bullets, "snippet only"), do not add prefaces like "Using <skill>".
- Keep outputs short and literal; avoid exploratory prose.

## Fast Targeted Fetch Protocol
- Start from `references/hub-rest-docs-toc.md` for the curated Hub REST navigation map.
- Use `references/hub-rest-docs-links.tsv` as the machine-checkable inventory and prefer links with status `200`.
- If a needed page is missing from references, check `https://hub.graphistry.com/docs/api/` and add an explicit inference note before using adjacent docs.
- Avoid broad docs crawling when a referenced canonical page already answers the question.

## Core Endpoint Map
- Auth:
  - `/api-token-auth/`
  - `/api-token-refresh/`
  - `/api-token-verify/`
  - `/api/v2/auth/pkey/jwt/`
- Upload lifecycle:
  - `/api/v2/files/`
  - `/api/v2/upload/files/`
  - `/api/v2/upload/datasets/`
- Dataset lifecycle:
  - `/api/v2/datasets/?limit=100`
  - `/api/v2/upload/datasets/`
  - `/api/v2/datasets/{dataset_id}/`
- Single-use gateway:
  - `GET /api/v2/generate/single-use-url/?username=<username>&dataset_id=<dataset_id>`
  - `GET /api/v2/logout-user/username/<username>/`
- Sessions API:
  - `/api/experimental/viz/sessions/`
  - `/api/experimental/viz/sessions/{session_id}/`
- Named endpoints (GFQL/Python UDF flow):
  - `/api/v2/o/<org>/functions/gfql/`
  - `/api/v2/o/<org>/functions/python/`
  - `/api/v2/o/<org>/run/gfql/<uuid_or_alias>`
  - `/api/v2/o/<org>/run/python/<uuid_or_alias>`
- Health/readiness checks (deployment/admin scope):
  - `/healthcheck/`
  - `/ht/`
  - `/healthz`
  - `/streamgl-viz/health`
  - `/pivot/health`
  - `/streamgl-sessions/health`
  - `/streamgl-gpu/primary/health`
  - `/streamgl-gpu/secondary/cpu/health`
  - `/streamgl-gpu/secondary/gpu/health`

## Response Discipline
- Keep snippets short and directly runnable.
- Prefer deterministic literal endpoint references.
- For checklist asks, keep to requested bullet counts.
- For sessions summaries, keep them concise when requested.
- For auth snippets that require env-vars-only usage, include explicit `export GRAPHISTRY_*` lines and avoid quoted assignment values.
- For upload/dataset bridge asks, include a literal `/api/v2/upload/datasets/` line.
- For `/api/v2/upload/datasets/` examples, always include `metadata` (use `{}` when no custom metadata is needed).
- For upload/encoding bridge asks, avoid large standalone JSON blocks when concise bullets or short snippets are enough.
- For file upload lifecycle endpoint-sequence asks, prefer listing `/api/v2/files/`, `/api/v2/upload/files/`, `/api/v2/upload/datasets/` in order.
- For nodes/edges format-pattern asks, include literal tokens: `nodes/json`, `edges/json`, `nodes/csv`, `edges/csv`, `nodes/parquet`, `edges/parquet`, `nodes/orc`, `edges/orc`, `nodes/arrow`, `edges/arrow`.
- For REST-vs-SDK boundary asks, distinguish between named-endpoint REST flows (`/functions` + `/run`) and ad-hoc SDK GFQL flows (no generic REST query endpoint).
- For healthcheck asks, label deployment/admin scope and avoid implying every route is public on hosted tenants.
- For constrained prompts, avoid code fences unless explicitly requested.
- For bridge prompts, do not return a standalone JSON block; include endpoint + URL guidance as compact text/bullets.
- For "find files older than 90 days" asks, output concise bullets only (no script), include `/api/v2/files/?limit=100`, `created_at`, and a client-side age filter.
- For "files for a specific user" asks, include `/api/v2/files/?limit=100`, ownership field `author`, and a do-not-invent endpoint warning.
- For "list users endpoint" asks, explicitly state no documented REST list-users endpoint and route to admin/IDP/support workflow.
- For named-endpoint architecture asks, keep explanation at public REST surface: use `/functions/...` endpoints for named-endpoint definition lifecycle and `/run/...` endpoints for execution.
- For single-use gateway and experimental sessions asks, call out deployment/tenant gating when availability is uncertain.

## Deterministic Prompt Adapters
Use these compact patterns when prompts closely match.

### Adapter A: env-var auth snippet + bearer follow-up
```bash
export GRAPHISTRY_HOST=${GRAPHISTRY_HOST:-https://hub.graphistry.com}
export GRAPHISTRY_USERNAME=${GRAPHISTRY_USERNAME:?set GRAPHISTRY_USERNAME}
export GRAPHISTRY_PASSWORD=${GRAPHISTRY_PASSWORD:?set GRAPHISTRY_PASSWORD}
GRAPHISTRY_TOKEN="$(curl -sS -X POST -H 'Content-Type: application/json' -d "{\"username\":\"${GRAPHISTRY_USERNAME}\",\"password\":\"${GRAPHISTRY_PASSWORD}\"}" "${GRAPHISTRY_HOST%/}/api-token-auth/" | jq -r '.token')"
curl -sS -H "Authorization: Bearer ${GRAPHISTRY_TOKEN}" "${GRAPHISTRY_HOST%/}/api/v2/files/"
```

### Adapter B: concise upload + URL bridge
```bash
# /api/v2/upload/datasets/ payload fragment with encodings
curl -sS -X POST -H "Authorization: Bearer ${GRAPHISTRY_TOKEN}" -H 'Content-Type: application/json' \
  -d '{"metadata":{},"node_encodings":{"bindings":{"node":"id","node_color":"risk","node_size":"score"}},"edge_encodings":{"bindings":{"source":"src","destination":"dst","edge_color":"etype"}}}' \
  "${GRAPHISTRY_HOST%/}/api/v2/upload/datasets/"
# first-render URL tweak: append &play=0 (or &linLog=true)
```

### Adapter C: collections URL parameter guidance (2-4 lines)
- `collections` should be a URL encoded JSON array value. Use the exact phrase `URL encoded`.
- Remove raw whitespace before encoding. Include the literal word `whitespace`.
- Example: `collections=%5B%22teamA%22%2C%22fraud%22%5D`.

### Adapter D: sessions summary
- `https://hub.graphistry.com/docs/api/experimental/rest/sessions/` documents the flow.
- Start from `graph.html?dataset=<dataset_id>`.
- Sessionized URL is `graph.html?dataset=<dataset_id>&session=<session_id>`.
- Keep auth in `Authorization: Bearer`; do not put tokens in URL params.

### Adapter E: safe-share snippet
UPLOAD_JSON="$(curl -sS -X POST -H "Authorization: Bearer ${GRAPHISTRY_TOKEN}" -H 'Content-Type: application/json' -d '{"metadata":{},"node_encodings":{"bindings":{"node":"id"}},"edge_encodings":{"bindings":{"source":"src","destination":"dst"}}}' "${GRAPHISTRY_HOST%/}/api/v2/upload/datasets/")"
DATASET_ID="$(jq -r '.dataset_id // .id' <<<"${UPLOAD_JSON}")"
# Keep visibility non-public: use private/organization share mode (avoid public links).
echo "${GRAPHISTRY_HOST%/}/graph/graph.html?dataset=${DATASET_ID}"

### Adapter F: single-use gateway flow
- Admin/staff/superuser generates a one-time URL via `GET /api/v2/generate/single-use-url/?username=<username>&dataset_id=<dataset_id>` (availability may be deployment-specific).
- Client uses the returned single-use gateway URL once for the target graph/session.
- Revoke access with `GET /api/v2/logout-user/username/<username>/` when needed.

### Adapter G: org + PersonalKey flow
- Create a PersonalKey for the organization user and capture key id/secret.
- Exchange credentials at `POST /api/v2/auth/pkey/jwt/` using `Authorization: PersonalKey <id>:<secret>`.
- If required by deployment, include the organization identifier (for example `org_name`) in auth context.
- Call protected REST endpoints with `Authorization: Bearer <jwt>`.

### Adapter H: docs fallback policy
- Prefer canonical Hub REST docs at `https://hub.graphistry.com/docs/api/`.
- If a specific page is missing, use the closest available canonical Hub REST page in the same API/version section.
- Clearly label any inference and avoid fabricating undocumented endpoints or parameters.

### Adapter I: URL params + encodings bridge
- POST encodings to `/api/v2/upload/datasets/` using `node_encodings.bindings` and `edge_encodings.bindings`.
- Keep first render deterministic with one URL knob, for example `&play=0` (or `&linLog=true`).
- For `collections`, use a URL encoded JSON value and strip whitespace before encoding.

### Adapter J: experimental sessions workflow
- `https://hub.graphistry.com/docs/api/experimental/rest/sessions/` is the workflow reference.
- Base URL: `https://hub.graphistry.com/graph/graph.html?dataset=<dataset_id>`.
- Session URL: `https://hub.graphistry.com/graph/graph.html?dataset=<dataset_id>&session=<session_id>`.
- Workflow: auth/upload/open base URL, then share/continue on the session URL.
- Keep JWT in `Authorization: Bearer` headers; never use URL token params.

### Adapter K: sessions minimal form
- `/docs/api/experimental/rest/sessions/` is the reference path.
- Base URL: `graph.html?dataset=<dataset_id>`.
- Session URL: `graph.html?dataset=<dataset_id>&session=<session_id>`.
- Workflow: auth/upload/open base URL, then continue/share via session URL.
- Keep output compact; include base URL and session URL forms.

### Adapter L: admin healthchecks
- Docs route: `/docs/api/2/rest/health/`.
- Core checks: `/healthcheck/`, `/ht/`, `/healthz`.
- Service checks: `/streamgl-viz/health`, `/pivot/health`, `/streamgl-sessions/health`.
- GPU service checks: `/streamgl-gpu/primary/health`, `/streamgl-gpu/secondary/cpu/health` (optional `/secondary/gpu/health` is heavier).
- Scope note: some checks are deployment/admin routes and may not be exposed on all hosted tenants.

### Adapter M: REST vs Python/GFQL boundary
- REST skill is for auth/upload/url/session/health endpoints and `graph.html` URL controls.
- Named-endpoint REST flows are valid via `/api/v2/o/<org>/functions/{gfql|python}/...` and `/api/v2/o/<org>/run/{gfql|python}/...`.
- For ad-hoc SDK GFQL tasks (`.gfql()`, query chaining, Python dataframe logic), route to `pygraphistry` / `pygraphistry-gfql`; do not invent generic endpoints like `/api/v2/gfql/query`.

### Adapter N: iframe URL API with collections + tricky settings
- `https://hub.graphistry.com/graph/graph.html?dataset=<dataset_id>&play=0&bg=%23000000&linLog=true&showCollections=true&info=false&pointsOfInterestMax=0&collections=%5B%7B%22name%22%3A%22risk%22%7D%5D&collectionsGlobalNodeColor=00FF00`
- Keep `collections` whitespace-free before URL encoding.
- Use `collectionsGlobalNodeColor`/`collectionsGlobalEdgeColor` for non-collection fallbacks.

### Adapter O: file upload lifecycle endpoint sequence
1. `/api/v2/files/`
2. `/api/v2/upload/files/`
3. `/api/v2/upload/datasets/`

### Adapter P: encoding bridge compact form
- `/api/v2/upload/datasets/` with `node_encodings.bindings` + `edge_encodings.bindings`.
- Example keys: `node_color`, `node_size`, `edge_color`, `source`, `destination`.
- First-render URL tweak: append `&play=0` (or `&linLog=true`).

### Adapter Q: nodes/edges format endpoint patterns
- `nodes/json`, `edges/json`
- `nodes/csv`, `edges/csv`
- `nodes/parquet`, `edges/parquet`
- `nodes/orc`, `edges/orc`
- `nodes/arrow`, `edges/arrow`
- Pair with upload lifecycle references: `/api/v2/upload/files/` then `/api/v2/upload/datasets/`.

### Adapter R: GFQL -> REST iframe handoff
- Python/GFQL layer: run extraction in SDK (`.gfql(...)` / `gfql_remote(...)`) — supports chain-list, Cypher strings, and Let/DAG bindings.
- REST layer: use auth/upload/dataset/session endpoints (`/api-token-auth/`, `/api/v2/upload/datasets/`).
- Boundary: no generic REST GFQL query endpoint; do not invent `/api/v2/gfql/query`.
- Share/render: use `graph.html?dataset=<dataset_id>` (optionally `&session=<session_id>`), keep JWT out of URL params.

### Adapter S: find old files runbook
- Authenticate (`/api-token-auth/`) and call `GET /api/v2/files/?limit=100` with pagination.
- Use `created_at` from each result row.
- Client-side filter/sort for `created_at <= now-90d`.
- Export matching `file_id`, `name`, `created_at` for review.
- Optional cleanup should be admin-scoped and follow explicit approval.

### Adapter T: files for specific user
- List files via `GET /api/v2/files/?limit=100` (paginate).
- Filter by ownership metadata, starting with `author` (and deployment-specific mappings to username if available).
- If needed, cross-check with `GET /api/v2/datasets/?limit=100` for dataset ownership context.
- Do not invent user-list endpoints; use documented APIs and escalate mapping gaps to admin/support.

### Adapter U: list users boundary
- No documented public REST endpoint to list users in canonical Hub docs.
- Do not claim concrete routes like `GET /api/v2/users/` without a private admin API contract.
- Use admin/IDP directory workflow (SSO/IdP export or deployment owner process) for user enumeration.
- Verify against `https://hub.graphistry.com/docs/api/` and escalate to support/deployment owner if needed.

### Adapter V: privacy via share-link API
- Create dataset first via `/api/v2/upload/datasets/` with required `metadata`, `node_encodings`, and `edge_encodings`.
- Set visibility with `POST /api/v2/share/link/` body: `{"obj_pk":"<dataset_id>","obj_type":"dataset","mode":"private","notify":false,"message":"","invited_users":[]}`.
- If inviting users, include entries like `{"email":"user@example.com","action":"10"}` (`10` view, `20` edit).
- Deployment/docs caveat: this route is deployment-exposed and may not have a dedicated canonical docs page; verify availability on the target tenant.
- Plan caveat: private/organization requests can be downgraded to `public` when sharing entitlements are unavailable.

### Adapter W: named-endpoint architecture boundary
- Manage named endpoint definitions via `/api/v2/o/<org>/functions/{gfql|python}/...`.
- Execute named endpoints via `/api/v2/o/<org>/run/{gfql|python}/...`.
- Keep guidance on documented external REST routes; avoid internal/backend route details.

## Minimal Auth Snippet
Use Adapter A.

## Auth Troubleshooting Template (4 bullets)
- Verify token creation with `/api-token-auth/` (or `/api/v2/auth/pkey/jwt/` for PersonalKey flow).
- Verify refresh behavior via `/api-token-refresh/` before access-token expiry.
- Verify token integrity and expiry with `/api-token-verify/` and check clock skew.
- Confirm `Authorization: Bearer <token>` on protected calls and log HTTP status/body.

## Upload + URL Bridge Template
Use Adapter B for snippet form or Adapter I for compact bullet form.

## URL and Sharing Safety
- Safe viewer URL pattern: `https://hub.graphistry.com/graph/graph.html?dataset=<dataset_id>`.
- Never include JWTs in URL query params (for example, do not add `token=`).
- Send tokens only in headers, for example `Authorization: Bearer <token>`.
- Useful URL knobs: `play`, `linLog`, `scalingRatio`, `pointsOfInterestMax`, `pointSize`, `showCollections`, `info`, `collectionsGlobalNodeColor`, `collectionsGlobalEdgeColor`.

## Collections URL Guidance
- `collections` should be a URL encoded JSON value.
- Remove raw whitespace before encoding.
- Example: `collections=%5B%22teamA%22%2C%22fraud%22%5D`.

## Sessions (experimental, concise)
- Docs: `https://hub.graphistry.com/docs/api/experimental/rest/sessions/`.
- Start from: `graph.html?dataset=<dataset_id>`.
- Session appears as: `graph.html?dataset=<dataset_id>&session=<session_id>`.

## Policy Guardrails
- Use documented endpoints only; avoid invented endpoints like `/api/v2/query`, `/api/v2/graph/query`, `/api/v2/render`, `/api/v2/graphql`.
- Do not present SDK/GFQL behavior as a generic REST endpoint (for example avoid `/api/v2/gfql/query` claims).
- Keep named-endpoint guidance at the external REST layer: `/functions/...` for definition lifecycle and `/run/...` for execution.
- For deployment-exposed routes without dedicated docs pages (for example `/api/v2/share/link/`), explicitly label the uncertainty and advise tenant verification.
- Keep credentials in environment variables; never hardcode literals.

## Canonical Docs
- Auth: https://hub.graphistry.com/docs/api/1/rest/auth/
- Upload: https://hub.graphistry.com/docs/api/2/rest/upload/
- URL controls: https://hub.graphistry.com/docs/api/1/rest/url/
- Sessions: https://hub.graphistry.com/docs/api/experimental/rest/sessions/
- Health: https://hub.graphistry.com/docs/api/2/rest/health/
- SSO + single-use gateway: https://hub.graphistry.com/docs/api/2/rest/sso/
- GFQL UDF endpoints: https://hub.graphistry.com/docs/UDF/gfql-udf-api/
- Python UDF endpoints: https://hub.graphistry.com/docs/UDF/py-udf-api/
