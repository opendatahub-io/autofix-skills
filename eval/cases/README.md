# Evaluation Test Cases

This directory contains test cases for evaluating the `autofix-resolve` skill. Each case includes realistic application code with intentional bugs or scenarios that the skill should handle.

## Test Case Structure

Each case directory contains:
- **Application code**: Java source files with realistic bugs
- **Build configuration**: `pom.xml` for Maven builds
- **Tests**: Unit tests that may fail due to bugs
- **autofix-context/**: Ticket information and test metadata
- **input.yaml**: Test case input configuration
- **annotations.yaml**: Expected outcomes for evaluation

## Cases

### case-001-simple-null-pointer-fix
**Scenario**: NullPointerException in user profile retrieval  
**Bug**: `UserProfile.formatPhoneNumber()` calls `isEmpty()` on potentially null `phoneNumber` field  
**Expected outcome**: Add null check, return "N/A" for null values  
**Test**: Should reproduce NPE when phone number is null

### case-002-complex-auth-refactor
**Scenario**: Authentication tokens expire immediately after login  
**Bug**: Time unit mismatch - `tokenLifetimeSeconds` (seconds) added directly to `System.currentTimeMillis()` (milliseconds)  
**Expected outcome**: Convert seconds to milliseconds: `tokenLifetimeSeconds * 1000`  
**Test**: `testTokenLifetime()` expects proper millisecond conversion

### case-003-already-fixed-duplicate
**Scenario**: API returns 500 for invalid email format  
**Status**: Already fixed - proper email validation is implemented  
**Expected outcome**: Skill should recognize issue is resolved and return `already_fixed` verdict  
**Test**: Email validation tests pass

### case-004-insufficient-info-ambiguous
**Scenario**: Vague performance complaint with no specifics  
**Status**: No application code (intentionally minimal)  
**Expected outcome**: Skill should return `insufficient_info` verdict requesting specific metrics  
**Test**: Skill correctly handles tickets with insufficient detail

### case-005-iterate-review-feedback
**Scenario**: Input validation with multiple issues identified in code review  
**Bugs**: 
- Password regex missing uppercase requirement (`[a-z0-9]{8,}` should be `^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).{8,}$`)
- Email validation error message exposes internal regex pattern
- Username validation missing special character test
- No database-level unique constraint for email (race condition)
**Expected outcome**: Skill should process review feedback and fix all issues in iteration  
**Test**: Failing test expects uppercase in password validation

## Running Tests Manually

To verify bugs exist:

```bash
cd eval/cases/case-001-simple-null-pointer-fix
mvn clean test  # Should pass (no test for null phoneNumber yet)

cd eval/cases/case-002-complex-auth-refactor  
mvn clean test  # Should fail testTokenLifetime due to time unit bug

cd eval/cases/case-003-already-fixed-duplicate
mvn clean test  # Should pass (already fixed)

cd eval/cases/case-005-iterate-review-feedback
mvn clean test  # Should fail testPasswordValidation_UppercaseRequired
```

## Evaluation Usage

The evaluation harness copies these test cases into isolated workspaces and runs the `autofix-resolve` skill against them. The skill should:

1. Read ticket information from `autofix-context/ticket.json`
2. Investigate the codebase
3. Implement fixes
4. Run validation (lint, build, tests)
5. Commit changes
6. Write verdict to `autofix-output/.autofix-verdict.json`

Judges then score the outputs based on implementation quality, review rigor, and iteration correctness.
