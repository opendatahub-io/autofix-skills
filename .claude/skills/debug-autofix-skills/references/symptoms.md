# Autofix-Skills Symptom Catalog

Known failure patterns from this repo's history. Update this file when fixing bugs or adding features that change failure modes.

## Skill path and context

### Agent can't find scripts (CLAUDE_SKILL_DIR undefined)
- **Likely cause**: Scripts referenced `CLAUDE_PLUGIN_ROOT` which doesn't exist. Fixed by replacing with `CLAUDE_SKILL_DIR`.
- **Where to look**: `scripts/` within each skill directory, any `${CLAUDE_SKILL_DIR}` references

### SessionStart hook fails to restore state after context compression
- **Likely cause**: Hook path was hardcoded and broke when the plugin moved. Fixed by generating a bootstrap script (`tmp/dispatch-recovery.sh`) with absolute paths during `state.py init`.
- **Where to look**: `hooks/hooks.json`, `scripts/state.py` init phase, `tmp/dispatch-recovery.sh`

### Triage skill reads ticket from wrong source
- **Likely cause**: Triage skill expected ticket key as CLI argument but the outer layer writes it to a context file. Fixed by RHAIFIRST-61.
- **Where to look**: `skills/autofix-triage/SKILL.md`, `.autofix-context/ticket.json`

## Verdict and schema

### Verdict rejected by schema validation
- **Likely cause**: LLM returns a string where an array is expected (e.g. `"file.py"` instead of `["file.py"]`). The `write_json.py` script coerces common mismatches.
- **Where to look**: `scripts/write_json.py`, `schemas/` JSON Schema definitions

### Missing required field in verdict
- **Likely cause**: Schema was updated to require a new field (e.g. `change_description` made required for committed verdicts) but the prompt doesn't instruct the agent to produce it.
- **Where to look**: `schemas/*.json` required fields, corresponding prompt in `prompts/`

### change_title or ci_blocked verdict not recognized
- **Likely cause**: These verdict values were added later. If the outer layer (autofix repo) hasn't been updated to handle them, the verdict is treated as unknown.
- **Where to look**: `schemas/implement-verdict.json`, autofix repo's `verdict.py`

## Review orchestration

### Review loop doesn't converge (agent keeps iterating)
- **Likely cause**: `state.py` is not advancing phases, or merge_findings produces new findings each cycle that the implement agent reacts to.
- **Where to look**: `scripts/state.py` phase transitions, `scripts/merge_findings.py`

### Agent ignores unrelated CI failures
- **Likely cause**: Before PR #24, agents would try to fix CI failures unrelated to their change. Now the prompt instructs agents to ignore pre-existing failures.
- **Where to look**: `prompts/` implement and review prompts, CI failure handling instructions

## Extension skills

### Extension findings not merged into review
- **Likely cause**: Extensions write to `.autofix-context/extension-findings/<skill-name>.json` but the orchestrator didn't discover them. Check `config.json` for the extension list and the hook point timing.
- **Where to look**: `.autofix-context/config.json`, orchestrator skill's extension discovery logic

### Commit message format conflicts
- **Likely cause**: Hardcoded commit message format in prompts conflicted with repo-specific conventions. Fixed by RHOAIENG-62875 which removed the hardcoding.
- **Where to look**: `prompts/` implement prompt, commit message instructions
