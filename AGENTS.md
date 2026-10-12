# autofix-skills

Orchestrator skills, prompt files, and state scripts for the Jira autofix pipeline. This repository is the inner layer. Ticket fetching, repo cloning, container launch, verdict reading, push, and labeling live in [jira-autofix](https://gitlab.com/redhat/rhel-ai/agentic-ci/jira-autofix) and [agentic-ci](https://github.com/opendatahub-io/agentic-ci).

## Navigation

Detailed context is organized in the `.agents/` tree. Start here for shared
rules, then follow the path matching your task.

Read [`.agents/README.md`](.agents/README.md) to find a task guide or portable
skill. The guidance is tool-neutral and applies to any coding agent.

- When **adding or changing a skill**, its prompts, schemas, or scripts, see
  [`.agents/skills-authoring/README.md`](.agents/skills-authoring/README.md)
  and the [`autofix-skills`](.agents/skills/autofix-skills/SKILL.md) skill
- When **investigating an agent-side failure**, use the
  [`debug-autofix-skills`](.agents/skills/debug-autofix-skills/SKILL.md) skill

## Skills

| Skill | What it does |
|-------|----------------|
| `autofix-resolve` | Implement, review, and evaluate loop for a bug ticket |
| `autofix-cve-resolve` | CVE remediation state machine across repos |
| `autofix-triage` | Bug readiness verdict: ready, needs_info, or not_fixable |
| `autofix-repo-resolve` | Pick the target repo when a ticket lists several URLs |

Pipeline skills stay in `skills/`. The plugin installer discovers `skills/`,
`.claude/skills/`, and `.opencode/skills/`. The marketplace entry for this
plugin sets no `skills` path.

## Architecture

`autofix-resolve` and `autofix-cve-resolve` dispatch sub-agents through prompt files and delegate deterministic work to Python scripts. Prompts and scripts hold the domain logic. The orchestrator dispatches and decides.

Prompt files (`prompts/*.md`) are self-contained personas for one task: implement a fix, review changes, scan for CVEs, and so on.

Scripts do JSON merging, state persistence, CVE routing, and schema validation. Each skill ships its own `scripts/` directory. `${CLAUDE_SKILL_DIR}` points to the skill root containing `SKILL.md` and `scripts/`. Call scripts with `python3 ${CLAUDE_SKILL_DIR}/scripts/<name>.py`. `write_json.py` is a PEP 723 script: `uv run --script ${CLAUDE_SKILL_DIR}/scripts/write_json.py`. `state.py` is copied in both `autofix-resolve/scripts/` and `autofix-cve-resolve/scripts/`. Change both copies together.

For Python tools from PyPI, use `uv tool run <tool>`. Some sandbox images do
not provide the `uvx` alias.

Commit rules for identity overrides and required trailers are shared by
`skills/autofix-resolve/prompts/implement-agent.md` and
`skills/autofix-cve-resolve/prompts/fix-agent.md`. When changing those rules,
update both prompts.

Schemas (`schemas/*.json`) define structured outputs. `write_json.py` validates against them and coerces common type mismatches (a string where an array or boolean is required) before writing.

## Conventions

Every skill declares the files it creates in `metadata.x-artifacts` so autofix and agentic-ci can build exclusion lists:

```yaml
metadata:
  x-artifacts: "autofix-output/ .autofix-context/ tmp/state.yaml"
```

Paths are space-separated. Directories end with `/`. Include anything the skill creates, reads as scaffold context, or that should stay out of git commits.

Skill names use the `autofix-` prefix so they can sit beside the `jira-autofix-` skills from ai-helpers on the same image.

Team extensions live in [ai-helpers](https://github.com/opendatahub-io/ai-helpers). They read `.autofix-context/` (`ticket.json`, `config.json`, verdict) and write `.autofix-context/extension-findings/<skill-name>.json` with `severity`, `description`, `file`, and `line`. The orchestrator discovers them from `.autofix-context/config.json` and calls them at `post_implement` and `post_review`.

When a change adds a failure mode, add the pattern to [`.agents/skills/debug-autofix-skills/references/symptoms.md`](.agents/skills/debug-autofix-skills/references/symptoms.md).

## Hooks

`hooks/hooks.json` is the plugin SessionStart hook. On context compaction it runs `tmp/dispatch-recovery.sh` when that file exists. `state.py init` writes the script and embeds the absolute path to `state.py`, because `${CLAUDE_SKILL_DIR}` is set only while a skill is running. Before the first `state.py init`, the hook does nothing.

## Versioning

Tag releases (`v0.1.0`, `v0.2.0`). The outer-layer runner pins one with `SkillConfig.skill_ref`. `main` is the development head.

## Linting

```bash
make lint
```
