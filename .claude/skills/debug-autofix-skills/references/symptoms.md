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
- **Where to look**: `skills/autofix-triage/SKILL.md`, `.triage-context/ticket.json`

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

### Correct fix ends `blocked` because a validation step cannot run in the sandbox
- **Likely cause**: The repo documents an aggregate check (for example `make linter`) that needs a container runtime or `unshare --net`, which the sandbox blocks by design. Before RHAIFIRST-653, the implement agent reported `lint_passed: false`, the review agent raised a critical finding, and the loop used all three implement passes. Now the implement agent runs the runnable subsets and reports `null` with a `Sandbox skip:` observation, and the review agent accepts that only when every runnable subset passed. A `Missing toolchain:` observation no longer blocks either (see the environment-gap entry below), but the tool still belongs in the sandbox image (agentic-ci) so the check can actually run.
- **Where to look**: verdict `observations` for `Sandbox skip:` or `Missing toolchain:` entries, `prompts/implement-agent.md` Step 5, `prompts/review-agent.md` Step 2

### Python fix ends `blocked` with `Missing toolchain: ... pytest not installed`
- **Likely cause**: The sandbox image has `uv` but not `pytest` or `tox`, and the agent reported the tool missing without running it through `uv`. The sandbox `AGENTS.md` ("do not install replacements") and "No hallucinated dependencies" made it think fetching the tool was forbidden. PyPI is allowlisted, so `uv run --with pytest python3 -m pytest`, `uvx tox` or the repo's own bootstrap (for example `make venv`) should work. The implement prompt now requires that attempt; if it is missing, the review agent records a `nitpick` rather than blocking. A `Missing toolchain:` observation for a Python tool must include a failed `Tried: <uv command>`; if it does not, the prompt was ignored. If the `uv` attempt itself failed, check the OpenShell network policy in agentic-ci.
- **Where to look**: verdict `observations` for `Missing toolchain:` and `Tried:`, `prompts/implement-agent.md` Step 5 "Checks the environment prevents", `prompts/review-agent.md` Step 2

### Fix ends `blocked` because a check could not run or failed outside the change
- **Likely cause**: Before this change, the review agent raised critical findings for sandbox skips, missing toolchains and pre-existing failures (for example a formatter version that differs from the repo's CI, or a linter already broken on `main`), and the loop used all three implement passes. Seen on fondue (RHAI-2422: shfmt 3.14.1 in the image vs 3.7.0 in fondue CI, a base linter failing on `main`, missing `ed`). Now environment gaps never block: the implement agent records `Sandbox skip:`, `Missing toolchain:` or `Pre-existing failure:` observations plus a `risks` entry, the review agent accepts them (compensating with a compiler-style read for missing toolchains), and SKILL.md keeps the verdict `committed` at the cap. If a ticket still blocks on validation, check whether the failure touches `files_changed`: that is the only case that should block.
- **Where to look**: verdict `observations` and `risks`, `prompts/implement-agent.md` Step 5 "Checks the environment prevents", `prompts/review-agent.md` Step 2, `SKILL.md` "Hard cap"

### Go fix ends `blocked` at the implementation cap with "Go toolchain is not available in the sandbox"
- **Likely cause**: The Codex sandbox image does not ship Go. After PR #68 a missing toolchain for changed files became a critical finding, so every Go ticket used all three implement passes and ended `blocked` (first seen on OSAC-5372). PR #70 added a Go-only exception; it is now covered by the general environment-gap rule above.
- **Where to look**: verdict `observations` for `Missing toolchain:`, `prompts/implement-agent.md` Step 5 "Checks the environment prevents", `prompts/review-agent.md` Step 2

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
