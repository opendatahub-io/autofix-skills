# Triage Bug Readiness: Detailed Rubric and Verdict Schema

## Gate Details

### Gate 1: Can the Agent Start? (minimum to proceed)

**Selected target repository:**

The orchestrator verifies that a repo URL exists before invoking this skill. Identify the selected checkout from the repository origin when available, and record the matching target URL from the ticket or context in `gate1.repo_url.value`. If that URL is unavailable, use the origin and explain the uncertainty in `gate1.repo_url.note`. Other URLs in the ticket may be likely owners, not the selected target.

**What is broken:**

- PASS: The ticket states what goes wrong, even briefly. Examples of sufficient descriptions:
  - "divide() returns the product instead of the quotient"
  - "The dashboard returns 403 after upgrading to 2.25"
  - "RBAC error: SA lacks permission to update scheduledsparkapplications/finalizers"
- FAIL: The ticket is vague or only states a desire without identifying a problem:
  - "Dashboard is broken"
  - "Please fix the model serving component"
  - "Something is wrong with authentication"

### Gate 2: Can the Agent Find and Fix It?

**Code locatability** -- Can the agent find where the bug lives in the selected target?

- PASS: The ticket provides enough signal to locate the relevant code through exploration:
  - Specific file/function names
  - An error message or log output greppable in the codebase
  - A CRD field name, API endpoint, or UI element name
  - A component name + feature area that narrows to a few directories
  - A locatable version pin or compatibility workaround in the selected checkout, even if the named function is in another repository
- FAIL: The description is too vague for even code exploration to narrow down, or no viable fix or workaround can be located in the selected checkout. A matching component name alone is not enough.

**Fix direction** -- Does the agent know what "correct" looks like?

- PASS: The correct behavior is stated or unambiguous from context:
  - A crash/panic should not crash
  - A 500/403 error should return the expected response
  - "Returns product instead of quotient" -- should return quotient
  - "Config option works on page A but not page B" -- should work on both
- FAIL: The "correct" behavior is genuinely ambiguous and requires a human design decision:
  - "The UI should be better"
  - "Model serving should be faster"
  - "The error message is confusing"

**Target repository ownership** -- Does this checkout contain a viable place to fix the reported defect?

- PASS: Source and behavior evidence support a fix in the selected target. If ownership is plausible but not certain and no evidence points elsewhere, pass with low confidence and describe the uncertainty.
- FAIL: Concrete evidence identifies a different implementation repository, while this checkout only deploys an image, configures a service, or calls an API and has no viable workaround. A component-to-repository mapping alone cannot satisfy this check.
- If the evidence cannot distinguish the selected target from another likely owner, fail this Gate 2 check when the ticket must identify the affected code or image before a useful resolve run. Return `needs_info` if Gate 3 passes. Do not infer a different owner from a failed search alone.

For example, a Feature Store ticket mapped to `opendatahub-io/feast` may concern operator or dashboard code; a Model as a Service ticket mapped to `models-as-a-service` may concern `ai-gateway-payload-processing`. Follow the specific ticket's code, stack trace, package, or image evidence. These examples are ownership checks, not a replacement mapping table.

Code locatability, fix direction, and target repository ownership must all PASS for Gate 2 to pass.

### Gate 3: Should an Agent Fix This? (scope and feasibility)

Even with perfect information, some bugs are not appropriate for automated fixing:

- **requires_design_decisions**: The "correct" behavior is subjective (UX preferences, API design choices)
- **requires_infrastructure**: Hardware-dependent, cloud service issues, CI/release engineering problems
- **systemic_architectural**: Fix requires changes in a truly external dependency (different organization, closed-source, or requires a release/publish process the agent cannot trigger)
- **needs_runtime_investigation**: Can only be diagnosed on a live cluster with specific state
- **performance**: Requires profiling, benchmarking, and potentially architectural changes
- **non_code_fix**: The resolution is not a code change -- e.g., KCS article update, documentation fix, Jira configuration, or infra/config-only change that the autofix agent cannot make

**Wrong target within the same organization:** A sibling repository is not `systemic_architectural`, but this resolve run operates on the selected checkout. If the defect is in a sibling and there is no viable target-repo fix, fail `gate2.target_repo_ownership`. Return `needs_info` when Gate 3 passes; if Gate 3 fails, return `not_fixable` under the verdict logic below. Name the likely owner in `gate2.target_repo_ownership.note`, `gate3.cross_repo` when its URL is known, and `message_to_opener`; ask for the ticket or component mapping to be retargeted when Gate 3 passes. If the selected checkout contains a viable part that fixes the reported behavior, Gate 2 may pass; describe any additional repo work in `gate3.cross_repo` and `gate3.note`.

**Truly external dependency:** If evidence shows the fix must happen outside the team's control and there is no viable fix or workaround in the target, fail Gate 3 with `systemic_architectural` and return `not_fixable`. Name the likely external owner in `gate3.note` and `message_to_opener`. Do not use this category solely because another repository is involved.

**Blocked or dependent bugs:** If a ticket has a "blocked by" link or depends on an external fix, consider whether a workaround exists in the target repo (compatibility shim, version pin, fallback path, feature gate). If a viable workaround exists, classify as `ready` with `"confidence": "medium"` and describe the workaround approach in `gate3.note`. Only classify as `not_fixable` if there is truly no interim mitigation possible within the target repo.

## Verdict Logic

```text
if Gate 1 fails:
    verdict = "needs_info"
elif Gate 3 fails:
    verdict = "not_fixable"
elif code_locatability and fix_direction and target_repo_ownership pass:
    verdict = "ready"
else:
    verdict = "needs_info"
```

## Verdict JSON Schema

Write the verdict as JSON to `.triage-verdict.json` in the repository root. Use the Write tool to create this file. Do NOT just print it to stdout.

```json
{
  "verdict": "ready | needs_info | not_fixable",
  "confidence": "high | medium | low",
  "security_sensitive": false,
  "gate1": {
    "repo_url": {
      "pass": true,
      "value": "https://github.com/org/repo",
      "note": "Found in ticket description"
    },
    "bug_description": {
      "pass": true,
      "note": "Clear description of incorrect behavior"
    }
  },
  "gate2": {
    "code_locatability": {
      "pass": true,
      "note": "Function confirmed in codebase at expected path"
    },
    "fix_direction": {
      "pass": true,
      "note": "Correct behavior is unambiguous"
    },
    "target_repo_ownership": {
      "pass": true,
      "note": "The affected function is implemented in the selected checkout"
    }
  },
  "gate3": {
    "pass": true,
    "not_fixable_reason": null,
    "note": "Bounded scope, single-repo fix",
    "cross_repo": null
  },
  "repo_readiness": {
    "has_agent_docs": false,
    "has_build_targets": true,
    "has_lint_config": true,
    "note": "Has Makefile with lint/test/build targets but no AGENTS.md"
  },
  "risk_factors": ["area under active refactor", "shared code with wide blast radius"],
  "missing": ["list of specific missing items, if any"],
  "message_to_opener": "",
  "reasoning": "Brief explanation of the overall assessment."
}
```

### Field Requirements

- `verdict`: One of `"ready"`, `"needs_info"`, `"not_fixable"`.
- `confidence`: Your confidence in the verdict. `"high"` = clear-cut. `"medium"` = reasonable but some uncertainty. `"low"` = borderline call.
- `security_sensitive`: Boolean. `true` if the bug describes a potential security vulnerability (auth bypass, injection, privilege escalation, data exposure, cryptographic weakness, supply chain concern, etc.). `false` for purely functional, cosmetic, or performance bugs. When `true`, the orchestrator requires human approval before autofix proceeds.
- `gate1`, `gate2`, `gate3`: Assessment of each gate with pass/fail and notes.
- `gate1.repo_url.value`: The selected target repository URL. The orchestrator pre-filters tickets without a URL; confirm which URL matches the checkout when multiple are mentioned.
- `gate2.target_repo_ownership`: Required `pass` boolean and evidence-based `note` identifying the code owned by the selected target, uncertainty, or the likely other owner. The component mapping alone is insufficient evidence.
- `gate3.not_fixable_reason`: One of `"requires_design_decisions"`, `"requires_infrastructure"`, `"systemic_architectural"`, `"needs_runtime_investigation"`, `"performance"`, `"non_code_fix"`, or `null` if Gate 3 passes.
- `gate3.cross_repo`: List known additional or likely owning repo URLs within the same organization (e.g., `["https://github.com/opendatahub-io/elyra"]`), including when a wrong target causes `needs_info`. Set to `null` when no such URL is known or the dependency is truly external.
- `repo_readiness`: Object describing the repo's readiness for automated fixing. Fields: `has_agent_docs` (bool -- `AGENTS.md`, `CLAUDE.md`, or `CONTRIBUTING.md` exists), `has_build_targets` (bool -- `Makefile` or equivalent has `build`/`test`/`lint` targets), `has_lint_config` (bool -- `.golangci.yml`, `.eslintrc`, `pyproject.toml [tool.ruff]`, etc.), `note` (string -- brief summary).
- `risk_factors`: Array of strings identifying factors that increase the difficulty or blast radius of the fix (e.g., `"no lint config"`, `"area under active refactor"`, `"shared code with wide blast radius"`, `"no test coverage near bug area"`). Empty array if no notable risks.
- `missing`: List of specific things missing from the ticket (empty array if verdict is `"ready"` or `"not_fixable"`).
- `message_to_opener`: The message to post on the Jira ticket. Required for `"needs_info"` and `"not_fixable"` verdicts. Must be specific -- reference the exact gate that failed, name a likely owning repository when evidence supports one, and tell the opener exactly what to provide or change. Empty string for `"ready"` verdicts.
- `reasoning`: Brief (1-3 sentence) explanation of the verdict.

## Actionable Feedback (Step 6)

For `needs_info` verdicts, the `message_to_opener` MUST be specific to what is actually missing. Do NOT produce generic "please add more info" messages. Structure the message as:

```markdown
**Needed** (without these, the autofix agent cannot proceed):

1. [Specific missing item referencing the failed gate]

**Helpful** (these make the fix faster and more accurate, but the agent can work without them):

- [Optional items that would speed up the fix]
```

Always end the message with: "Please update the ticket, then remove the `jira-triage-needs-info` label to re-trigger assessment."

When Gate 2 fails because the selected repository does not own the defect, state the selected repository and the evidence for the likely owner. Ask the opener to identify the owning code path or image and update the ticket or component-to-repository mapping so the next run checks out that repository. If the likely owner is known, name it directly; do not ask the opener to rediscover it. If ownership is unclear, name the candidate repositories and the exact evidence needed to choose one.

For `not_fixable` verdicts, explain clearly why the bug is not suitable for automated fixing, referencing the specific Gate 3 category. Name the likely external owner when known and suggest what kind of human intervention is needed (e.g., "A release engineer should investigate" or "This requires a design discussion to determine the correct behavior").

For `ready` verdicts, `message_to_opener` should be an empty string.
