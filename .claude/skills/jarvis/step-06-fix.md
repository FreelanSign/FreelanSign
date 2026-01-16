# Step 06: Fix Issues

## Objective
Address all issues identified in the review step.

## Fix Priority

```
1. 🔴 Critical (security, crashes) - MUST fix all
2. 🟠 Important (perf, smells) - Fix most
3. 🟡 Suggestions - Fix if quick, else skip
```

## Fix Protocol

### For Each Issue

```markdown
### Fixing: [FILE:LINE] Issue title

**Before:**
```code
// problematic code
```

**After:**
```code
// fixed code
```

**Verification:** How to confirm fix works
```

### Fix Strategies

| Issue Type | Strategy |
|------------|----------|
| Security | Apply fix, add test for vulnerability |
| Type error | Add proper types, avoid `any` |
| Naming | Rename with replace_all |
| Long function | Extract helper functions |
| Missing test | Add in Step 07 |
| Error handling | Add specific catch |
| Hardcoded value | Move to config/env |

## Batch Fixes

Group related fixes when possible:
```
# Same file → Single edit session
# Same pattern → Use replace_all
# Related changes → Sequential edits
```

## Fix Checklist Per Issue

- [ ] Issue understood
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] No new issues introduced
- [ ] Related code checked for same issue

## Scope Control

**DO fix:**
- All critical issues
- Important issues in touched files
- Suggestions that are one-liner fixes

**DON'T fix:**
- Unrelated issues discovered
- Pre-existing problems outside scope
- "While I'm here" improvements

For out-of-scope issues:
```markdown
## Out of Scope Issues (For Future)

1. **[FILE:LINE]** Issue description
   - Reason: Outside current feature scope
   - Recommendation: Create separate task/ticket
```

## Verification After Fixes

```bash
# Re-run validation
pnpm lint && pnpm check && pnpm build
black --check . && pytest --tb=short -q
```

## Output

```markdown
## Fix Summary

### Fixed Issues
- [x] 🔴 Critical: Issue 1 - `file.ext:L42`
- [x] 🟠 Important: Issue 2 - `file.ext:L87`
- [x] 🟡 Suggestion: Issue 3 - `file.ext:L15`

### Deferred Issues
- [ ] 🟡 Issue 4 - Reason: Out of scope

### Files Modified
- `path/file.ext` - Fix description

### Verification
- Linting: ✅/❌
- Types: ✅/❌
- Build: ✅/❌
- Tests: ✅/❌

### Ready for Tests: YES/NO
```

## Loop Condition

If fixes introduce new issues:
1. Re-run Step 05 (Review) on changed files
2. Return to Step 06 if new issues found
3. Max 3 iterations, then ask user
