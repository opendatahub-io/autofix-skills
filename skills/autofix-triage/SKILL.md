---
name: autofix-triage
description: >-
  Use when assessing a Jira bug ticket for AI autofix readiness. Produces a
  structured JSON verdict (ready/needs_info/not_fixable) based on a three-gate
  rubric. Designed for CI pipeline use with the autofix pipeline orchestrator.
allowed-tools: Read Grep Glob Write Bash
metadata:
  x-artifacts: "agent-output.txt .autofix-context/ .triage-context/ .triage-verdict.json"
---

# Skill: Triage Bug Readiness

You are assessing a Jira bug ticket for AI autofix readiness. Your goal is to determine whether an automated coding agent (Claude Code) can successfully fix this bug given the information available. You will produce a structured JSON verdict written to a file.

## Step 1: Parse the ticket content

Read the ticket from `.autofix-context/ticket.json` (written by the pipeline orchestrator). Extract:

- What the reporter claims is broken (the symptom)
- Where they believe the bug is (component, feature area, file paths)
- Any error messages, log output, or stack traces
- Any repo URLs mentioned (GitLab or GitHub)
- Steps to reproduce (if provided)
- Expected vs. actual behavior (if stated)

## Step 2: Profile the repository

Run the init script to gather repo metadata:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/triage-init.sh
```

Read `.triage-context/repo-profile.json` for language, build/test/lint infrastructure, agent docs, and directory structure. If `.triage-context/orientation.md` was generated, read it for repo conventions.

Also check for `.triage-context/ARCHITECTURE.md` (pre-generated architecture overview) if it exists.

Populate `repo_readiness` from the profile: `has_agent_docs`, `has_build_targets`, `has_lint_config`.

## Step 3: Explore the bug area

If no repo is present in the working directory, set `repo_readiness` fields to `false` with a note and skip to Step 4.

Using the repo profile as your map, use `Grep`, `Glob`, and `Read` to:

- **Locate the code area** referenced by the bug. Verify functions, CRD fields, API endpoints, or error messages mentioned in the ticket exist and are current.
- **Check for test coverage** near the bug area (`*_test.go`, `*.test.ts`, `test_*.py`).
- **Review recent git history**: `git log --oneline -20 -- <path>` for the relevant area.
- **Check cross-component impact**: does the bug area touch shared code (`pkg/`, `lib/`, `utils/`) used by multiple consumers?

## Step 4: Evaluate security sensitivity

Determine whether the ticket describes a potential security vulnerability. This catches security-sensitive bugs that were filed as regular Bug tickets without any of the JQL-level embargo markers (Vulnerability type, "EMBARGOED" in title, CVE pattern, Embargoed security level).

Flag `security_sensitive: true` if the bug description involves any of:

- Authentication or authorization bypass
- Privilege escalation
- Injection vulnerabilities (SQL, command, code, LDAP, XSS, etc.)
- Data exposure or information leakage
- Cryptographic weaknesses or credential handling flaws
- Path traversal or file access control issues
- Denial of service via resource exhaustion
- Security header or CORS misconfigurations
- Supply chain concerns (dependency tampering, malicious payloads)

Set `security_sensitive: false` for bugs that are purely functional, cosmetic, or performance-related with no security implications.

When `security_sensitive` is true, the orchestrator will require human approval before autofix proceeds, regardless of the readiness verdict.

## Step 5: Assess readiness using the rubric

Apply the three-gate rubric from `references/rubric-and-schema.md`:

- **Gate 1 -- Can the Agent Start?** Repo URL exists and ticket states what is broken.
- **Gate 2 -- Can the Agent Find and Fix It?** Code is locatable and correct behavior is unambiguous.
- **Gate 3 -- Should an Agent Fix This?** Not blocked by design decisions, infrastructure, external deps, or non-code fixes.

**Verdict:** Gate 1 fail → `needs_info`. Gate 3 fail → `not_fixable`. Gate 2 pass → `ready`. Else → `needs_info`.

**Bias toward ready:** A wasted autofix cycle is cheaper than a missed fix. When uncertain, choose `ready` with `"confidence": "low"` over `not_fixable`.

## Step 6: Write structured verdict to file

Write the verdict as JSON to `.triage-verdict.json` in the repository root. Use the Write tool to create this file. Do NOT just print it to stdout. See `references/rubric-and-schema.md` for the full JSON schema and field requirements.

After writing the verdict file, validate it against the schema:

```bash
uv run --script ${CLAUDE_SKILL_DIR}/scripts/write_json.py \
  ${CLAUDE_SKILL_DIR}/schemas/triage-verdict.json \
  .triage-verdict.json \
  --input .triage-verdict.json
```

If validation errors occur, fix the JSON and re-run.

For `needs_info` verdicts, `message_to_opener` must reference the specific failed gate and tell the opener what to provide. For `not_fixable`, explain the Gate 3 category. For `ready`, use an empty string. See `references/rubric-and-schema.md` for templates.

## Gotchas

- **Cross-repo is not systemic**: Fixes spanning repos in the same org are `ready`, not `systemic_architectural`. Only use `not_fixable` when the dependency is outside the team's control.
- **No repo clone is not a hard stop**: Set `repo_readiness` fields to `false` with a note and continue.
- **Bash scoping**: Bash is for `git log` (Step 3), `triage-init.sh` (Step 2), and `write_json.py` (Step 6). Do not use it for running repo build/test commands.
