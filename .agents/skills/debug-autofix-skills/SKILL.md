---
name: debug-autofix-skills
description: Investigate agent-side failures in the autofix-skills plugin. Covers wrong verdicts, review loop issues, state machine bugs, and prompt problems. Use when the agent ran but produced wrong results.
allowed-tools: Bash Read Grep Glob
---

# Debug Autofix-Skills

Investigate failures in the agent-side layer: skill prompts, review orchestration, verdict generation, and state management.

## Key entry points

| Area | Entry point |
|------|-------------|
| Orchestration | `skills/autofix-resolve/SKILL.md`, `skills/autofix-cve-resolve/SKILL.md` |
| Triage | `skills/autofix-triage/SKILL.md` |
| State machine | `scripts/state.py` (duplicated in each skill's `scripts/` dir) |
| Review merging | `scripts/merge_findings.py` |
| Verdict writing | `scripts/write_json.py` + `schemas/*.json` |
| Prompts | `prompts/*.md` within each skill directory |
| Hook recovery | `hooks/hooks.json`, `tmp/dispatch-recovery.sh` |

## Protocol

1. **Read** this repo's `AGENTS.md` for architecture context.
2. **Check** [references/symptoms.md](references/symptoms.md) for known patterns matching the failure.
3. **Investigate** the relevant skill's SKILL.md, prompts, scripts, and schemas.
4. **Write RCA** using [assets/rca-template.md](assets/rca-template.md).
