# Step 03: Execute Implementation

## Objective
Implement the planned feature following TDD and quality standards.

## Execution Protocol

### 1. TDD Approach (Mandatory)
```
For each task:
1. Write failing test first
2. Implement minimum code to pass
3. Refactor if needed
4. Move to next task
```

### 2. Implementation Order
```
1. Domain layer (pure logic, no deps)
2. Application layer (use cases, DTOs)
3. Infrastructure layer (adapters, DB)
4. Presentation layer (API, UI)
5. Integration points
```

### 3. Per-File Checklist

Before writing code:
- [ ] Read existing file first
- [ ] Identify insertion points
- [ ] Check for similar patterns nearby

While writing:
- [ ] Follow project style (PEP8, no semicolons)
- [ ] Use absolute imports only
- [ ] No `any` types in TypeScript
- [ ] No console.logs (use proper logging)
- [ ] Handle errors at boundaries

After writing:
- [ ] Check cyclomatic complexity ≤ 5
- [ ] Verify no hardcoded values
- [ ] Ensure tests cover new code

## Cyclomatic Complexity Check

For modified functions, calculate:
```
CC = E - N + 2P
Where: E=edges, N=nodes, P=connected components

Or count: 1 + (if/elif/else) + (for/while) + (and/or) + (case)
```

**If CC > 5:**
```markdown
⚠️ COMPLEXITY WARNING
Function: `function_name`
Cyclomatic Complexity: X (threshold: 5)
Recommendation: Split into smaller functions
```

## Frontend Tasks

If task involves UI/design:
```
Invoke: /frontend-design skill
Pass: Component requirements from plan
```

## Quality Gates Per Task

- [ ] Test written and failing
- [ ] Implementation passes test
- [ ] No new linter errors
- [ ] No type errors
- [ ] CC ≤ 5 for new/modified functions

## Progress Tracking

After each task:
```markdown
✅ Task N: <description>
   - Files: path/file.ext
   - Tests: path/test_file.ext
   - CC: X (OK/WARNING)
```

## Blockers Protocol

If blocked:
1. Document the blocker
2. Skip to next independent task
3. Return to blocked task after
4. If still blocked → Ask user

## Output

End of step report:
```markdown
## Execution Summary

### Completed
- [x] Task 1
- [x] Task 2

### Blocked/Skipped
- [ ] Task 3 - Reason: ...

### Files Modified
- `path/file.ext` - changes summary

### Files Created
- `path/new.ext` - purpose

### Tests Added
- `path/test.ext` - coverage summary

### Warnings
- CC > 5: function_name (consider refactor)

### Ready for Validation: YES/NO
```
