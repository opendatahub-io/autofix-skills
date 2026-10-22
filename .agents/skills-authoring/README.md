# Skill Authoring

How to add or change a pipeline skill in this repository. The skill list stays
in `README.md`. Human contribution steps stay in `CONTRIBUTING.md`.

The invocable skill is
[`.agents/skills/autofix-skills/SKILL.md`](../skills/autofix-skills/SKILL.md).

## Setup

Python 3.10+. CI runs 3.13 (`.github/workflows/lint.yml`).

```bash
pip install ruff
```

`make lint` also needs `shellcheck` and `uv` (`uv tool run skillsaw` unless
`SKILLSAW_BIN` is set).

To exercise a branch in the pipeline, set `SkillConfig.skill_ref` to that
branch, or mount this checkout into the runner image.

## Execution

Copy the closest skill under `skills/`. The skills-registry marketplace entry
for this plugin sets no `skills` path, so the installer picks up `skills/`,
`.claude/skills/`, and `.opencode/skills/`.

| Piece | Path |
|-------|------|
| Prompt | `skills/<name>/SKILL.md` |
| Agent prompts | `skills/<name>/prompts/` |
| JSON schema | `skills/<name>/schemas/` |
| Scripts | `skills/<name>/scripts/` |
| References | `skills/<name>/references/` |
| Plugin manifest | `.claude-plugin/plugin.json` |
| Resolve eval | `eval.yaml`, `eval/cases/` |
| Triage eval | `eval-triage.yaml`, `eval/cases-triage/` |

`name` in `SKILL.md` matches the directory. Declare `metadata.x-artifacts`.

`autofix-resolve` and `autofix-cve-resolve` read `.autofix-context/`.
`autofix-triage` reads `.triage-context/`. `autofix-repo-resolve` reads
`.autofix-context/ticket.json` and `.autofix-context/repo-candidates.json`.
Scripts are `python3 ${CLAUDE_SKILL_DIR}/scripts/<name>.py`. `write_json.py`
is `uv run --script`.

`state.py` exists in both `skills/autofix-resolve/scripts/` and
`skills/autofix-cve-resolve/scripts/`. Edit both.

Eval case `AGENTS.md` files use a `.fixture` suffix. The eval SessionStart
hook renames them before a case runs. Eval harness runs are separate from
`make lint`.

## Validation

```bash
make lint
```

`make lint` is skillsaw, `ruff check`, `ruff format --check`, and shellcheck.

## Troubleshooting

| Symptom | Where to look |
|---------|----------------|
| Wrong fix or verdict | The skill's `SKILL.md`, `scripts/state.py` phase, `scripts/merge_findings.py`, and `schemas/` |
| Review loop stuck | Implement, review, and evaluate in the orchestrator, and whether `state.py` advances the phase |
| Context missing | The outer layer writes `.autofix-context/` or `.triage-context/` before the agent runs. Check `ticket.json` and `config.json` |
| Extension produced nothing | `.autofix-context/config.json` and `.autofix-context/extension-findings/`. Hook points are `post_implement` and `post_review` |
| Skill missing from the runner | Place it in `skills/<name>/`. The installer also discovers `.claude/skills/` and `.opencode/skills/` |
| `state.py` differs between resolve and CVE | Update both copies |
| Verdict fails schema | `write_json.py` coercion and the schema `required` fields |

## Escalation

- Merge review: GitHub pull request on `opendatahub-io/autofix-skills`
- Ticket fetch, clone, container, push, and labels: [jira-autofix](https://gitlab.com/redhat/rhel-ai/agentic-ci/jira-autofix) and [agentic-ci](https://github.com/opendatahub-io/agentic-ci)
- Extension skills: [ai-helpers](https://github.com/opendatahub-io/ai-helpers)
- Marketplace skills path: `opendatahub-io/skills-registry` `.claude-plugin/marketplace.json`
