# autofix-skills

Claude Code plugin for the Jira autofix pipeline. Provides orchestrator skills, agent prompt files, and deterministic Python scripts for automated bug fixing, CVE remediation, and ticket triage.

## Overview

This plugin is the **inner layer** of the autofix pipeline, the skills that run inside the Claude Code container. The outer layer (Python orchestration, GitLab CI, ticket management) lives in [jira-autofix](https://gitlab.com/redhat/rhel-ai/agentic-ci/jira-autofix) and [agentic-ci](https://github.com/opendatahub-io/agentic-ci) (generic CI framework).

### Skills

| Skill | Description |
|-------|-------------|
| `autofix-resolve` | Orchestrates end-to-end bug fixing: implement, review, evaluate loop (max 3 iterations) |
| `autofix-cve-resolve` | CVE remediation across multiple repos with state-machine dispatch |
| `autofix-triage` | Assesses bug tickets for AI autofix readiness (ready/needs_info/not_fixable) |
| `autofix-research` | Investigates spike tickets with no associated repository |

### Scripts

| Script | Description |
|--------|-------------|
| `merge_findings.py` | Merges core review findings with extension findings, tags each with `source` |
| `state.py` | State persistence utility for context-compression recovery |
| `cve_pipeline.py` | CVE state machine: deterministic routing, wave dispatch, progress polling |

## Installation

This plugin is pre-installed in the `ghcr.io/opendatahub-io/ai-helpers` container image. For local development:

```bash
git clone git@github.com:opendatahub-io/autofix-skills.git

# Install as a Claude Code plugin (local directory source)
claude plugin install /path/to/autofix-skills
```

## Development

### Prerequisites

- Python 3.10+ with [ruff](https://docs.astral.sh/ruff/)
- [shellcheck](https://www.shellcheck.net/)
- Container runtime (Podman or Docker) for claudelint

### Validate Changes

```bash
make lint
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full development workflow.

## Evaluation

The `eval/` directory contains test cases for evaluating skill quality using the [agent-eval-harness](https://github.com/opendatahub-io/agent-eval-harness). Two eval configs are provided:

| Config | Skill | Cases |
|--------|-------|-------|
| `eval.yaml` | `autofix-resolve` | `eval/cases/` (10 cases: bug fixes, iteration, triage decisions, security guardrails) |
| `eval-triage.yaml` | `autofix-triage` | `eval/cases-triage/` (4 cases: ready, needs_info, not_fixable, borderline) |

### Running evals

```bash
# Install the eval harness
pip install -e ../agent-eval-harness

# Run the autofix-resolve eval suite
/eval-run --config eval.yaml --model opus

# Run the triage eval suite
/eval-run --config eval-triage.yaml --model opus

# Run a single case
/eval-run --config eval.yaml --model opus --cases case-006-agents-md-compliance
```

Results are written to `eval/runs/<run-id>/` with per-case verdicts, modified files, events, and an HTML report. See [eval.md](eval.md) and [eval-triage.md](eval-triage.md) for detailed analysis docs.

### Test case structure

Each case directory contains an `input.yaml`, `.autofix-context/` with ticket data, optional source files in `src/`, and `annotations.yaml` with expected outcomes. `AGENTS.md` files are stored with a `.fixture` suffix to prevent agents working in this repo from auto-discovering test payloads (case-010 contains a credential-harvesting guardrail test). The eval `SessionStart` hook activates fixtures before each case runs.

## Architecture

See [AGENTS.md](AGENTS.md) for architecture details and conventions.

Team-specific extension skills go in [ai-helpers](https://github.com/opendatahub-io/ai-helpers), not this repo. Extensions are normal Claude skills that read from `.autofix-context/` and write findings to `.autofix-context/extension-findings/<skill-name>.json`.

## Versioning

Use git tags (`v0.1.0`, `v0.2.0`, etc.) for releases. The outer-layer runner pins a release via `SkillConfig.skill_ref`. The `main` branch is the development head.

## License

[Apache License 2.0](LICENSE)
