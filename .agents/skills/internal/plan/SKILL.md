---
name: plan
description: Create and maintain a concise file-backed plan for multi-session work, handoffs, or complex multi-PR tasks. Use only when the user explicitly requests a plan file or durable task state is needed; otherwise use the platform's native planning.
metadata:
  internal: true
---

# File-backed plans

Use a plan file only when its persistence is valuable. For ordinary single-session work, use native planning instead.

## Start

1. Create `plans/<task>/plan.md` from the template below.
2. Record the raw request, branch/base, success criteria, and any constraints.
3. Split the work into independently verifiable steps. Mark only one `IN_PROGRESS`.

```markdown
# <Task> plan

**Branch**: `<branch>`
**Base**: `<base>`
**PR**: `<URL or pending>`

## Goal
<Outcome and success criteria>

## Context
<Important constraints, decisions, and links needed to resume>

## Steps

### 1. <Step>
**Status**: IN_PROGRESS
**Verify**: <command or observable outcome>
**Notes**: <results, decisions, or blocker>

### 2. <Step>
**Status**: TODO
**Verify**: <command or observable outcome>
```

## Maintain

- Read the plan at natural handoff points: starting a work block, changing steps, returning after interruption, and before a PR/review.
- Update it when a step completes, a material decision changes, a command fails, or a blocker appears. Do not turn routine reads or minor edits into plan churn.
- Keep durable facts in the plan: exact commands worth rerunning, validation results, PR links, unresolved questions, and decisions with rationale.
- Keep only one step `IN_PROGRESS`; use `TODO`, `DONE`, `BLOCKED`, or `SKIPPED` for the rest.
- For a long plan, replace completed detail with a short verified-results summary. Preserve the commands and decisions needed for a safe resume.

## Finish

Before handoff or PR, record the current commit/PR, validation performed, remaining risks, and the next concrete action. Do not commit `plans/` unless repository convention or the user asks.
