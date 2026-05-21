# Contributing Guidelines

## Before Starting Work

1. Check recent PRs and commits - the issue may already be fixed
2. Search for related test cases that validate the fix
3. If already fixed, document which commit/PR addressed it

## Bug Fixes

- Add test cases that reproduce the original issue
- Verify the test fails on the commit before the fix
- Verify the test passes on current main branch

## Validation

- Run the full test suite: `pytest`
- Check that functions raise appropriate exceptions
- Verify error messages are user-friendly
