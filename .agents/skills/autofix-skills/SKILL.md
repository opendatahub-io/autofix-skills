---
name: autofix-skills
description: >-
  Change a skill in this repo. Use when adding or editing a skill under
  skills/, its prompts, schemas, or scripts.
user-invocable: true
---

# autofix-skills

Use this skill when changing this repo. Read
[the skill authoring guide](../../skills-authoring/README.md) for the
repo-specific workflow.

## Inputs

The skill, prompt, schema, or script to add or change.

## Change a skill

1. Read `README.md` and the closest skill under `skills/<name>/`.
2. Keep pipeline skills in `skills/<name>/`. `.agents/skills/` is this
   contributor skill and `debug-autofix-skills`.
3. Declare `metadata.x-artifacts`. Reference sibling files with
   `${CLAUDE_SKILL_DIR}`.
4. Verdicts go through that skill's `scripts/write_json.py` and `schemas/`.
5. When editing `state.py`, update both `skills/autofix-resolve/scripts/`
   and `skills/autofix-cve-resolve/scripts/`.
6. When a change adds a failure mode, update
   `.agents/skills/debug-autofix-skills/references/symptoms.md`.

Use the skill authoring guide for complete details.

## Validation

```bash
make lint
```
