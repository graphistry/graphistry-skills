# Claude Native Skills Eval Env

This directory simulates a user project environment for native Claude skill loading.

Claude discovers project skills from:
- `.claude/skills/` in the current working directory
- `~/.claude/skills/` in the user home directory

We use this env to avoid prompt-injecting skill text and instead test native runtime behavior.

## Setup

Create symlinks from this repo's `.agents/skills/*` into this env:

```bash
./scripts/evals/setup_claude_skill_env.sh --env-dir evals/env/claude
```

By default, the script links the `pygraphistry_core` skill set.

## Smoke test

Run a native-skill smoke test:

```bash
./bin/evals/claude-skills-smoke.sh
```

This runs Claude from this directory and asks:
- which skills are loaded (no tool calls)

The script prints:
- init-reported loaded skill names
- assistant response
- whether tool calls were emitted
