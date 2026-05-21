# Development Guidelines

## Security Considerations
- Never log authentication tokens in plaintext
- Ensure token expiration calculations are thoroughly tested
- Security-critical changes require additional test coverage

## Time Handling
- Always use consistent time units (prefer seconds from time.time())
- Document time unit conversions clearly in code
- Add unit tests with specific timestamp values to verify calculations

## Commit Messages
- Include ticket key in first line
- Explain the root cause in the commit body
- Reference affected components

## Testing Requirements
- Add tests for edge cases (token at exact expiration time)
- Verify backward compatibility with existing valid tokens
- Run `pytest` for all auth changes
