# Code Review Guidelines

## Addressing Review Feedback

- Fix all critical issues (security, correctness, missing requirements)
- Address code quality issues (error messages, race conditions)
- Add missing test coverage identified in review
- Ensure all tests pass before submitting

## Security Best Practices

- Never expose technical details (regex, stack traces) in user-facing errors
- Handle race conditions in validation logic
- Use database constraints for uniqueness where possible

## Testing Requirements

- Cover all validation rules with unit tests
- Include negative test cases (invalid inputs that should be rejected)
- Test edge cases (special characters, boundary values)
- Run `pytest` to validate
