---
name: autofix-repo-resolve
description: >-
  Disambiguate which repository URL is the actual target when a Jira ticket
  mentions multiple repos. Reads ticket context and candidate URLs, classifies
  each URL, and writes a verdict with the target and confidence level.
allowed-tools: Read Write Bash
metadata:
  x-artifacts: "agent-output.txt .autofix-context/repo-resolve-verdict.json"
---

# Skill: Repo URL Disambiguation

You are resolving which repository is the actual target of a Jira bug ticket that mentions multiple repository URLs. Your goal is to determine which single repo the bug should be fixed in.

## Step 1: Read inputs

1. Read `.autofix-context/ticket.json` for the ticket description, comments, and Jira component name.
2. Read `.autofix-context/repo-candidates.json` for the list of candidate repository URLs detected in the ticket.

## Step 2: Analyze the ticket context

For each candidate URL, classify it by reading the surrounding context in the ticket description and comments:

- **target**: The repo the bug is actually about. Look for:
  - Explicit statements: "the impacted repository is...", "target repo:", "affected repo:", "this is a bug in..."
  - The repo discussed alongside the actual symptoms, error messages, or stack traces
  - The repo that matches the Jira component name
- **contextual**: Mentioned for background but not the target. Look for:
  - Cross-references: "see also", "related to", "similar issue in..."
  - Reproduction environments, test fixtures, or demo repos
  - Repos mentioned in steps-to-reproduce as tools or dependencies, not as the thing that's broken
- **negative**: Explicitly stated as NOT the problem. Look for:
  - "this is NOT a X issue", "not related to Y", "X is functioning correctly"
  - "removed X component", "not a code issue in Y"
- **unclear**: Cannot determine the relationship from context.

## Step 3: Determine target and confidence

- **high**: One URL has an explicit target statement, or only one URL remains after filtering out negative and contextual mentions.
- **medium**: One URL is more likely the target based on proximity to bug symptoms, but no explicit statement. Or, the Jira component name aligns with one candidate.
- **low**: Multiple URLs remain plausible targets after analysis. No clear signal.

If confidence is low, set `target_url` to the most likely candidate but note the ambiguity in `reasoning`.

## Step 4: Write verdict

Write the verdict to `.autofix-context/repo-resolve-verdict.json`:

```json
{
  "target_url": "https://github.com/org/repo",
  "confidence": "high",
  "reasoning": "The description explicitly states 'The impacted repository is: odh-model-controller' under Other Information.",
  "candidates": [
    {"url": "https://github.com/opendatahub-io/odh-model-controller", "classification": "target"},
    {"url": "https://github.com/opendatahub-io/odh-dashboard", "classification": "negative"},
    {"url": "https://github.com/rh-aiservices-bu/fraud-detection", "classification": "contextual"}
  ]
}
```

Validate the verdict:

```bash
uv run --script ${CLAUDE_SKILL_DIR}/scripts/write_json.py \
  ${CLAUDE_SKILL_DIR}/schemas/repo-resolve-verdict.json \
  .autofix-context/repo-resolve-verdict.json \
  --input .autofix-context/repo-resolve-verdict.json

uv run --script ${CLAUDE_SKILL_DIR}/scripts/validate_verdict.py \
  .autofix-context/repo-resolve-verdict.json
```

If validation fails, fix the JSON and re-validate.

## Gotchas

- Always classify ALL candidate URLs, not just the target.
- The ticket text may contain URLs in Jira markup format (e.g., `[text|url]` or `[url]`). Parse both plain URLs and markup links.
- Do not access any repository or clone any code. This is a text-analysis-only skill.
- When the Jira component name clearly maps to one of the candidate repos (e.g., component "AI Core Dashboard" and candidate `odh-dashboard`), use this as a signal but not as the sole basis for high confidence -- the ticket text may indicate a different repo is the actual target.
