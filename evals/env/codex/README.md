# Codex Native Skills Eval Env

This directory simulates a user project environment for native Codex skill loading.

Codex discovers project skills from:
- `.codex/skills/` in the current working directory
- `~/.codex/skills/` in the user home directory

We use this env to test native runtime skill behavior without prompt-injecting skill content.

## Setup

Create symlinks from this repo's `.agents/skills/*` into this env:

```bash
./scripts/evals/setup_codex_skill_env.sh --env-dir evals/env/codex
```

By default, the script links the `pygraphistry_core` skill set.

## Smoke test

Run a native-skill smoke test:

```bash
./bin/evals/codex-skills-smoke.sh
```

This runs Codex from this directory and asks:
- which skills are loaded

The script prints:
- assistant-reported loaded skill names
