---
name: autofix-branch-resolve
description: >-
  Disambiguate which branch a fix should target when neither fixVersion mapping
  nor a branch sentinel in ticket text yields a clear answer. Reads ticket
  context, available remote branches, and optional pipeline ref, then writes a
  verdict with the target branch and confidence level.
allowed-tools: Read Write Bash
metadata:
  x-artifacts: "agent-output.txt .autofix-context/branch-resolve-verdict.json"
---

# Skill: Branch Disambiguation

You are resolving which branch a fix should target for a Jira bug ticket. The ticket has already been associated with a repository, but the correct branch could not be determined from fixVersion mapping or explicit branch sentinels. Your goal is to determine the single branch the fix should be applied to.

## Step 1: Read inputs

1. Read `.autofix-context/ticket.json` for the ticket description, comments, and metadata.
2. Read `.autofix-context/repo-url.txt` for the resolved repository URL.
3. Read `.autofix-context/remote-branches.txt` for the list of available remote branches (output of `git ls-remote --heads`).
4. Read `.autofix-context/pipeline-ref.txt` for the pipeline ref, if the file exists. This file is optional.

## Step 2: Analyze the ticket context

Examine the ticket description and comments for branch signals. Consider the following sources of evidence, in rough order of strength:

### Explicit branch references
Look for direct mentions of a branch name in the ticket text:
- "this regressed in the 3.5 stream", "backport needed for release-3.5"
- "fix on main", "target branch: release-v2.16"
- "the issue is on the 1.x line", "please cherry-pick to release-2.0"

### Pipeline ref match
If `pipeline-ref.txt` is present, check whether the pipeline ref exactly matches one of the remote branches. An exact match is a strong signal: the pipeline was triggered from that branch, so the fix likely belongs there.

### Version numbers in ticket text
Look for version numbers mentioned in the ticket (e.g., in fixVersion, affected versions, description text) and correlate them with branch naming patterns:
- Version "3.5.2" may correspond to a branch named `release-3.5`, `release-v3.5`, `v3.5`, or `3.5.x`
- Version "2.16.0" may correspond to `release-v2.16`, `release-2.16`, or `v2.16`
- Consider both exact and prefix matches against available remote branches

### Component or project context
The Jira component name or project context may hint at a branch (e.g., a component named "RHOAI 2.16" suggesting a `release-v2.16` branch).

### Default branch as fallback
If no other signal is found, `main` or `master` (whichever exists in the remote branches list) is the default target.

## Step 3: Determine target and confidence

- **high**: The pipeline ref exactly matches a remote branch name. Or, the ticket text contains an explicit branch reference that exactly matches an available remote branch.
- **medium**: A version number or contextual signal (component name, affected version) strongly correlates with a specific branch pattern in the remote branches list. Or, only one non-default branch exists and the ticket context suggests a release branch is needed.
- **low**: Multiple branches remain plausible after analysis. No clear signal points to a specific branch. Or, the only match is a weak heuristic with no supporting ticket context.

If confidence is low, set `target_branch` to the best guess (prefer the default branch when truly ambiguous) and explain the ambiguity in `reasoning`.

## Step 4: Write verdict

Write the verdict to `.autofix-context/branch-resolve-verdict.json`:

```json
{
  "target_branch": "release-v2.16",
  "confidence": "high",
  "reasoning": "The pipeline ref 'release-v2.16' exactly matches the remote branch 'refs/heads/release-v2.16'."
}
```

Validate the verdict:

```bash
uv run --script ${CLAUDE_SKILL_DIR}/scripts/write_json.py \
  ${CLAUDE_SKILL_DIR}/schemas/branch-resolve-verdict.json \
  .autofix-context/branch-resolve-verdict.json \
  --input .autofix-context/branch-resolve-verdict.json

uv run --script ${CLAUDE_SKILL_DIR}/scripts/validate_verdict.py \
  .autofix-context/branch-resolve-verdict.json
```

If validation fails, fix the JSON and re-validate.

## Gotchas

- Do not access any repository or clone any code. This is a text-analysis-only skill.
- The ticket text may contain URLs in Jira markup format (e.g., `[text|url]` or `[url]`). Parse both plain text and markup when looking for branch references.
- Branch names in `remote-branches.txt` are fully qualified refs (e.g., `refs/heads/release-v2.16`). Strip the `refs/heads/` prefix when comparing against ticket text.
- When the pipeline ref matches a remote branch, prefer it over weaker signals from ticket text, unless the ticket explicitly overrides it (e.g., "please target main instead").
- If `pipeline-ref.txt` is missing or empty, skip the pipeline ref analysis entirely rather than treating it as a signal.
- The default branch (usually `main` or `master`) should only be selected with high confidence when the ticket explicitly requests it or when no release branch signals exist at all.
