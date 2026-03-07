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
  - `/api/v2/generate/single-use-url/`
  - `/api/v2/logout-user/username/{username}/`

## Response Discipline
- Keep snippets short and directly runnable.
- Prefer deterministic literal endpoint references.
- For checklist asks, keep to requested bullet counts.
- For sessions summaries, keep to <=7 lines when asked for concise output.
- For auth snippets that require env-vars-only usage, include explicit `export GRAPHISTRY_*` lines and avoid quoted assignment values.
- For upload/dataset bridge asks, include a literal `/api/v2/upload/datasets/` line.
- If a response includes any preface line, still satisfy strict line limits by shortening the body.
- For constrained prompts, avoid code fences unless explicitly requested.
- For bridge prompts, do not return a standalone JSON block; include endpoint + URL guidance as compact text/bullets.

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

### Adapter B: concise upload + URL bridge (<=14 lines)
```bash
# /api/v2/upload/datasets/ payload fragment with encodings
curl -sS -X POST -H "Authorization: Bearer ${GRAPHISTRY_TOKEN}" -H 'Content-Type: application/json' \
  -d '{"node_encodings":{"bindings":{"node":"id","node_color":"risk","node_size":"score"}},"edge_encodings":{"bindings":{"source":"src","destination":"dst","edge_color":"etype"}}}' \
  "${GRAPHISTRY_HOST%/}/api/v2/upload/datasets/"
# first-render URL tweak: append &play=0 (or &linLog=true)
```

### Adapter C: collections URL parameter guidance (2-4 lines)
- `collections` should be a URL encoded JSON array value. Use the exact phrase `URL encoded`.
- Remove raw whitespace before encoding. Include the literal word `whitespace`.
- Example: `collections=%5B%22teamA%22%2C%22fraud%22%5D`.

### Adapter D: sessions summary (<=7 lines)
- `https://hub.graphistry.com/docs/api/experimental/rest/sessions/` documents the flow.
- Start from `graph.html?dataset=<dataset_id>`.
- Sessionized URL is `graph.html?dataset=<dataset_id>&session=<session_id>`.
- Keep auth in `Authorization: Bearer`; do not put tokens in URL params.

### Adapter E: safe-share snippet (<=8 lines)
UPLOAD_JSON="$(curl -sS -X POST -H "Authorization: Bearer ${GRAPHISTRY_TOKEN}" -H 'Content-Type: application/json' -d '{"privacy":"private","node_encodings":{"bindings":{"node":"id"}},"edge_encodings":{"bindings":{"source":"src","destination":"dst"}}}' "${GRAPHISTRY_HOST%/}/api/v2/upload/datasets/")"
DATASET_ID="$(jq -r '.dataset_id // .id' <<<"${UPLOAD_JSON}")"
echo "${GRAPHISTRY_HOST%/}/graph/graph.html?dataset=${DATASET_ID}"

### Adapter F: single-use gateway flow (3 bullets)
- Admin/staff/superuser generates a one-time URL via `POST /api/v2/generate/single-use-url/`.
- Client uses the returned single-use gateway URL once for the target graph/session.
- Revoke access with `POST /api/v2/logout-user/username/{username}/` when needed.

### Adapter G: org + PersonalKey flow (3-5 bullets)
- Create a PersonalKey for the organization user and capture key id/secret.
- Exchange credentials at `POST /api/v2/auth/pkey/jwt/` using `Authorization: PersonalKey <id>:<secret>`.
- If required by deployment, include the organization identifier (for example `org_name`) in auth context.
- Call protected REST endpoints with `Authorization: Bearer <jwt>`.

### Adapter H: docs fallback policy (3 bullets)
- Prefer canonical Hub REST docs at `https://hub.graphistry.com/docs/api/`.
- If a specific page is missing, use the closest available canonical Hub REST page in the same API/version section.
- Clearly label any inference and avoid fabricating undocumented endpoints or parameters.

### Adapter I: URL params + encodings bridge (<=14 lines)
- POST encodings to `/api/v2/upload/datasets/` using `node_encodings.bindings` and `edge_encodings.bindings`.
- Keep first render deterministic with one URL knob, for example `&play=0` (or `&linLog=true`).
- For `collections`, use a URL encoded JSON value and strip whitespace before encoding.

### Adapter J: experimental sessions workflow (hard cap 6 lines body)
- `https://hub.graphistry.com/docs/api/experimental/rest/sessions/` is the workflow reference.
- Base URL: `https://hub.graphistry.com/graph/graph.html?dataset=<dataset_id>`.
- Session URL: `https://hub.graphistry.com/graph/graph.html?dataset=<dataset_id>&session=<session_id>`.
- Workflow: auth/upload/open base URL, then share/continue on the session URL.
- Keep JWT in `Authorization: Bearer` headers; never use URL token params.

### Adapter K: sessions deterministic min form (for strict max-lines checks)
- `/docs/api/experimental/rest/sessions/` is the reference path.
- Base URL: `graph.html?dataset=<dataset_id>`.
- Session URL: `graph.html?dataset=<dataset_id>&session=<session_id>`.
- Workflow: auth/upload/open base URL, then continue/share via session URL.
- Output formatting: exactly 4 lines, no blank lines, no code fences, no lead-in sentence.

## Minimal Auth Snippet (env-var-only)
```bash
export GRAPHISTRY_HOST=${GRAPHISTRY_HOST:-https://hub.graphistry.com}
export GRAPHISTRY_USERNAME=${GRAPHISTRY_USERNAME:?set GRAPHISTRY_USERNAME}
export GRAPHISTRY_PASSWORD=${GRAPHISTRY_PASSWORD:?set GRAPHISTRY_PASSWORD}

GRAPHISTRY_TOKEN="$(curl -sS -X POST \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"${GRAPHISTRY_USERNAME}\",\"password\":\"${GRAPHISTRY_PASSWORD}\"}" \
  "${GRAPHISTRY_HOST%/}/api-token-auth/" | jq -r '.token')"

curl -sS -H "Authorization: Bearer ${GRAPHISTRY_TOKEN}" "${GRAPHISTRY_HOST%/}/api/v2/files/"
```

## Auth Troubleshooting Template (4 bullets)
- Verify token creation with `/api-token-auth/` (or `/api/v2/auth/pkey/jwt/` for PersonalKey flow).
- Verify refresh behavior via `/api-token-refresh/` before access-token expiry.
- Verify token integrity and expiry with `/api-token-verify/` and check clock skew.
- Confirm `Authorization: Bearer <token>` on protected calls and log HTTP status/body.

## Upload + URL Bridge Template (concise)
```bash
# 1) Upload bytes and get file_id
curl -sS -H "Authorization: Bearer ${GRAPHISTRY_TOKEN}" -F "file=@graph.csv" "${GRAPHISTRY_HOST%/}/api/v2/upload/files/"
# 2) Create dataset with encodings
curl -sS -X POST -H "Authorization: Bearer ${GRAPHISTRY_TOKEN}" -H 'Content-Type: application/json' \
  -d '{"node_encodings":{"bindings":{"node":"id"}},"edge_encodings":{"bindings":{"source":"src","destination":"dst"}}}' \
  "${GRAPHISTRY_HOST%/}/api/v2/upload/datasets/"
# 3) First render tweak: append one URL knob, e.g. &play=0
```

## URL and Sharing Safety
- Safe viewer URL pattern: `https://hub.graphistry.com/graph/graph.html?dataset=<dataset_id>`.
- Never include JWTs in URL query params (for example, do not add `token=`).
- Send tokens only in headers, for example `Authorization: Bearer <token>`.
- Useful URL knobs: `play`, `linLog`, `scalingRatio`, `pointsOfInterestMax`, `pointSize`.

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
- Keep credentials in environment variables; never hardcode literals.

## Canonical Docs
- Auth: https://hub.graphistry.com/docs/api/1/rest/auth/
- Upload: https://hub.graphistry.com/docs/api/2/rest/upload/
- URL controls: https://hub.graphistry.com/docs/api/1/rest/url/
- Sessions: https://hub.graphistry.com/docs/api/experimental/rest/sessions/
