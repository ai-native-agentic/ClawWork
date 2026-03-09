# Harness QA for ClawWork

This repository uses the harness-engineering 6-gate layout under `.harness/`.

## Run locally

```bash
./.harness/run-gates.sh
```

## Enabled gates

- Gate A: formatting, lint, type checks
- Gate C: structural ratchets

Gate B and Gates D-F are currently disabled to avoid false positives until architecture and baselines are formalized.

## CI

- Workflow: `.github/workflows/harness-gates.yml`
- Triggered on push and pull request
