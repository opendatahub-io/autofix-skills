# AGENTS.md — Project Conventions

All contributors (human and AI) MUST follow these rules. PRs that
violate them will be rejected by CI.

## Commit Messages

Use Conventional Commits with the ticket key in square brackets:

    [TICKET-KEY] type(scope): description

Example:

    [AUTOFIX-1006] fix(pagination): correct off-by-one on last page

The type MUST be one of: fix, feat, refactor, test, docs, chore.
The scope MUST match the primary module being changed.
The description MUST be lowercase and not end with a period.

## Code Style

- **No wildcard imports.** Never use `from x import *`. Import only
  the names you need.
- **Docstrings required.** Every public function (no leading underscore)
  MUST have a docstring. Use Google-style docstrings.
- **Type hints required.** All function signatures MUST have type hints
  for parameters and return values.

## Testing

- Test function names MUST follow: `test_<function>_<scenario>_<expected>`
  Example: `test_get_page_last_page_partial_returns_remaining_items`
- Every bug fix MUST include at least one regression test.

## Changelog

- Add an entry under `## Unreleased` in CHANGELOG.md for every bug fix.
- Format: `- Fixed: <description> (TICKET-KEY)`
