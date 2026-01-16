# Step 04: Validate

## Objective
Run all validation checks to ensure code quality before review.

## Validation Sequence

### 1. Linting

**Backend (Python)**
```bash
# Check formatting
black --check .

# If fails, auto-fix
black .
```

**Frontend (TypeScript/React)**
```bash
# Run ESLint
pnpm lint

# If fails, attempt auto-fix
pnpm lint --fix
```

### 2. Type Checking

**Frontend**
```bash
pnpm check
```

**Backend (if using type hints)**
```bash
mypy apps/ --ignore-missing-imports
```

### 3. Build Verification

**Frontend**
```bash
pnpm build
```

**Backend**
```bash
python manage.py check
python manage.py makemigrations --check --dry-run
```

### 4. Test Suite (Quick)

**Backend**
```bash
pytest --tb=short -q
```

**Frontend**
```bash
pnpm test --run
```

## Validation Report

```markdown
## Validation Results

| Check | Status | Details |
|-------|--------|---------|
| Black (format) | ✅/❌ | - |
| ESLint | ✅/❌ | X warnings |
| TypeScript | ✅/❌ | - |
| Build | ✅/❌ | - |
| Django check | ✅/❌ | - |
| Migrations | ✅/❌ | X new |
| Tests (BE) | ✅/❌ | X passed |
| Tests (FE) | ✅/❌ | X passed |

### Errors Found
- None / List errors

### Auto-Fixed
- None / List what was fixed

### Manual Action Required
- None / List required actions
```

## Failure Handling

### Linting Failures
1. Attempt auto-fix
2. If still fails → List specific issues
3. Continue to review (will be caught there)

### Type Errors
1. List all errors with file:line
2. Categorize: Missing type / Wrong type / Import issue
3. These MUST be fixed before PR

### Build Failures
1. STOP validation
2. Report full error
3. Return to Step 03 to fix

### Test Failures
1. List failing tests
2. Categorize: New failure / Pre-existing
3. New failures MUST be fixed

## Gate Decision

```
All checks pass? → Proceed to Step 05 (Review)
Build fails? → Return to Step 03
Type errors? → Fix now, re-validate
Test failures (new)? → Fix now, re-validate
Test failures (pre-existing)? → Note and proceed
```

## Output

```markdown
## Validation Complete

Status: PASS / FAIL

Next Step:
- PASS → Proceed to Review (Step 05)
- FAIL → Return to Execute (Step 03) with fix list
```
