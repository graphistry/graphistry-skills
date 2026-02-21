# graphistry-skills

Public PyGraphistry skills for agent runtimes (Codex, Claude Code, and compatible skill loaders).

## Install

Install from GitHub:

```bash
npx skills add graphistry/graphistry-skills \
  --agent codex \
  --agent claude-code \
  --skill pygraphistry \
  --skill pygraphistry-core \
  --skill pygraphistry-gfql \
  --skill pygraphistry-visualization \
  --skill pygraphistry-ai \
  --skill pygraphistry-connectors \
  --yes
```

## Public Skill Pack

- `pygraphistry`: Router/TOC skill for selecting the right PyGraphistry workflow.
- `pygraphistry-core`: Auth + table-to-graph shaping + first plot flow.
- `pygraphistry-gfql`: GFQL traversal, filtering, pattern constraints, and remote query patterns.
- `pygraphistry-visualization`: Styling, layouts, privacy-safe sharing, icons/badges.
- `pygraphistry-ai`: UMAP/DBSCAN/embeddings/semantic search guidance.
- `pygraphistry-connectors`: Connector-aware ingestion workflows and dataframe-first fallback patterns.

## Local Validation

```bash
python3 scripts/ci/validate_skills.py
./bin/evals/claude-skills-smoke.sh
./bin/evals/codex-skills-smoke.sh
```

## Fast Eval Loop

Run only the cases you are actively tuning, and parallelize Codex/Claude per case:

```bash
./bin/agent.sh \
  --codex --claude \
  --journeys pygraphistry_persona_journeys_v1 \
  --case-ids persona_novice_fraud_table_to_viz_algo,persona_connector_analyst_workflow \
  --skills-mode both \
  --skills-delivery native \
  --max-workers 2
```

Compare model tiers within a runtime:

```bash
./bin/agent.sh \
  --claude \
  --journeys pygraphistry_persona_journeys_v1 \
  --case-ids persona_novice_fraud_table_to_viz_algo \
  --skills-mode both \
  --claude-models sonnet,opus \
  --max-workers 2
```

## Repository Layout

```text
.agents/skills/<skill>/SKILL.md
benchmarks/
evals/journeys/*.json
scripts/agent_eval_loop.py
bin/agent.sh
```

## Benchmarks

- Latest checked-in benchmark report: `benchmarks/reports/2026-02-20-clean-rerun.md`
- Latest checked-in benchmark data: `benchmarks/data/2026-02-20-clean-rerun`

## Notes

- Keep credentials in environment variables only.
- Keep `SKILL.md` files concise; route detail into references when needed.
- Internal workflow skills (`plan`, `eval-otel`) are maintained for team development and evaluation operations.
