# Step 05: Code Review

## Objective
Self-review all changes following style guide and best practices.

## Review Scope

```bash
# Get all changes
git diff dev...HEAD --name-only
```

Review each modified/created file.

## Review Checklist

### Style Guide Compliance

#### Python
- [ ] snake_case for variables/functions
- [ ] PascalCase for classes
- [ ] UPPER_SNAKE_CASE for constants
- [ ] Imports: stdlib → third-party → local
- [ ] Functions < 50 lines
- [ ] Docstrings for public APIs

#### TypeScript/React
- [ ] No semicolons
- [ ] Single quotes
- [ ] 2-space indent
- [ ] No `any` types
- [ ] Props interfaces defined
- [ ] Hooks rules followed

### Security Checklist
- [ ] No hardcoded secrets
- [ ] No credentials in code
- [ ] Input validation at boundaries
- [ ] SQL injection prevention (parameterized)
- [ ] XSS prevention (proper escaping)

### Architecture Compliance
- [ ] Domain layer: pure Python (no Django)
- [ ] DTOs for use case I/O
- [ ] Absolute imports only
- [ ] No circular dependencies

### Error Handling
- [ ] Specific exceptions (not bare except)
- [ ] Error messages are actionable
- [ ] Logging includes context
- [ ] Boundaries validated

### Test Coverage
- [ ] New behaviors have tests
- [ ] Edge cases covered
- [ ] Tests are readable
- [ ] Tests are deterministic

## Issue Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| 🔴 Critical | Security vuln, crash bug | MUST fix |
| 🟠 Important | Perf issue, code smell | Should fix |
| 🟡 Suggestion | Style, naming, docs | Nice to fix |

## Review Output Format

```markdown
## Code Review Results

### Summary
- Files reviewed: X
- Critical issues: X
- Important issues: X
- Suggestions: X

### Issues Found

#### 🔴 Critical
1. **[FILE:LINE]** Issue description
   - Problem: What's wrong
   - Fix: How to fix

#### 🟠 Important
1. **[FILE:LINE]** Issue description
   - Problem: What's wrong
   - Fix: How to fix

#### 🟡 Suggestions
1. **[FILE:LINE]** Issue description
   - Suggestion: Improvement idea

### Positive Observations
- Good pattern usage in X
- Clean separation in Y

### Review Verdict
- ✅ APPROVED - No critical/important issues
- ⚠️ CHANGES REQUESTED - Issues must be addressed
```

## Automated Style Check

Run on changed files:
```python
# Inline check for common issues
for file in changed_files:
    check_line_length(max=100)
    check_trailing_whitespace()
    check_naming_conventions()
    check_import_order()
```

## Next Step Decision

```
No Critical/Important issues? → Step 07 (Tests)
Issues found? → Step 06 (Fix Issues)
```
