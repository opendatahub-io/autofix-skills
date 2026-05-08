# autofix-skills

Claude Code plugin for the Jira autofix pipeline. Provides orchestrator skills, agent prompt files, and deterministic Python scripts for automated bug fixing, CVE remediation, and ticket triage.

## Overview

This plugin is the **inner layer** of the autofix pipeline, the skills that run inside the Claude Code container. The outer layer (Python orchestration, GitLab CI, ticket management) lives in [jira-autofix](https://gitlab.com/redhat/rhel-ai/agentic-ci/jira-autofix) and [ai-agentic-lib](https://gitlab.com/redhat/rhel-ai/agentic-ci/ai-agentic-lib).

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

## Architecture

See [AGENTS.md](AGENTS.md) for architecture details and conventions.

Team-specific extension skills go in [ai-helpers](https://github.com/opendatahub-io/ai-helpers), not this repo. Extensions are normal Claude skills that read from `.autofix-context/` and write findings to `.autofix-context/extension-findings/<skill-name>.json`.

## Versioning

Use git tags (`v0.1.0`, `v0.2.0`, etc.) for releases. The outer-layer runner pins a release via `SkillConfig.skill_ref`. The `main` branch is the development head.

## License

[Apache License 2.0](LICENSE)
