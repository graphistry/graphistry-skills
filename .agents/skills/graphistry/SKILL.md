---
name: graphistry
description: >
  Umbrella router for Graphistry workflows across SDK and API surfaces.
  Use when asked to "use graphistry", "visualize with graphistry", "graph this data in graphistry",
  "graphistry plot", or any question mixing Python SDK and REST API concerns. Also triggers on
  "graphistry SDK vs API", "graphistry authentication", "how do I share a graphistry graph",
  "Graphistry Hub", or any ambiguous graphistry request before the interface is clear.
  Routes to pygraphistry for Python SDK tasks, graphistry-rest-api for curl/REST tasks.
  Proactively suggest when the user mentions graph visualization or network analysis and
  has not yet chosen an interface.
---

# Graphistry Router

Use this skill as the shared entrypoint across Graphistry interfaces.

## Route By Interface
- Python SDK tasks (`import graphistry`, DataFrame shaping, `.plot()`, `.gfql()` including Cypher/Let/DAG, PyGraphistry notebooks): use `pygraphistry`.
- REST API tasks (`curl`, `/api/v2/...`, JWT/Bearer auth, upload endpoints, `graph.html` URL params): use `graphistry-rest-api`.
- JavaScript/TypeScript SDK tasks (`@graphistry/*`, browser/frontend integrations): use `graphistry-js` if available.

## Mixed Requests
- If a request mixes Python SDK and REST endpoints, start with `pygraphistry` and pull in `graphistry-rest-api` for exact endpoint syntax.
- For named-endpoint questions, keep guidance user-facing: `/api/v2/o/<org>/functions/...` for definition lifecycle and `/api/v2/o/<org>/run/...` for execution.
- Keep the first routing response compact: selected interface + one minimal snippet + one canonical doc link.

## Safety Rules
- Use environment variables for credentials and secrets.
- Never put JWT tokens in URL query parameters.
- Prefer documented endpoints; avoid invented helper endpoints.

## Canonical Docs
- Graphistry Hub docs: https://hub.graphistry.com/docs/
- PyGraphistry docs: https://pygraphistry.readthedocs.io/en/latest/
- REST auth docs: https://hub.graphistry.com/docs/api/1/rest/auth/
- REST upload docs: https://hub.graphistry.com/docs/api/2/rest/upload/
- REST SSO/single-use gateway docs: https://hub.graphistry.com/docs/api/2/rest/sso/
- REST GFQL UDF docs: https://hub.graphistry.com/docs/UDF/gfql-udf-api/
- REST Python UDF docs: https://hub.graphistry.com/docs/UDF/py-udf-api/
