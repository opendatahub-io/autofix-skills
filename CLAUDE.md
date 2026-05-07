# autofix-skills

Claude Code plugin providing orchestrator skills, prompt files, and state management scripts for the Jira autofix pipeline.

## Repository Structure

```
.claude-plugin/plugin.json   Marketplace packaging metadata
skills/                      Skill directories (each contains SKILL.md + prompts/)
  autofix-resolve/           Orchestrator: implement → review → evaluate loop
  autofix-cve-resolve/       CVE orchestrator: state-machine dispatcher
  autofix-triage/            Standalone bug readiness assessment
  autofix-research/          Standalone spike/research investigation
scripts/                     Deterministic Python utilities called by skills
  merge_findings.py          Merge core + extension findings into all-findings.json
  state.py                   State persistence for context-compression recovery
  cve_pipeline.py            CVE state machine (next-action / wait-for-wave)
hooks/                       Claude Code event hooks
  hooks.json                 SessionStart hook for context-compression recovery
```

## Architecture

This plugin implements the **inner layer** of the autofix pipeline. The outer layer (ticket fetching, repo cloning, container launch, verdict reading, push, labeling) lives in `jira-autofix` and `ai-agentic-lib`.

**Orchestrator skills** (`autofix-resolve`, `autofix-cve-resolve`) are dispatchers — they call sub-agents via prompt files and delegate deterministic work to Python scripts. They never contain domain logic directly.

**Prompt files** (`prompts/*.md`) are self-contained agent personas. Each defines a complete set of instructions for one task (implement a fix, review changes, scan for CVEs, etc.).

**Scripts** handle all deterministic operations: JSON merging, state persistence, CVE routing decisions. The LLM calls these via `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py` and reads the output.

## Naming Convention

Skills in this plugin use the `autofix-` prefix (e.g., `autofix-resolve`) instead of the `jira-autofix-` prefix used by the original skills in `ai-helpers`. This avoids name collisions — both plugins can be active simultaneously on the container image.

## Extension Skills

Team extensions are normal Claude skills in `ai-helpers` (not in this repo). Extensions:
- Read context from `.autofix-context/` (ticket.json, config.json, verdict)
- Write findings to `.autofix-context/extension-findings/<skill-name>.json`
- Use the standard findings schema: `severity`, `description`, `file`, `line`

The orchestrator discovers extensions via `.autofix-context/config.json` (written by the outer-layer runner) and calls them at fixed hook points (`post_implement`, `post_review`).

## Local Development

Clone this repo alongside the autofix pipeline repos:
```bash
git clone git@github.com:opendatahub-io/autofix-skills.git
```

To test skills locally, point `SkillConfig.skill_ref` to your branch or mount the local checkout into the container.

## Versioning

Use git tags (`v0.1.0`, `v0.2.0`, etc.) for releases. The outer-layer runner pins a release via `SkillConfig.skill_ref`. The `main` branch is the development head.
