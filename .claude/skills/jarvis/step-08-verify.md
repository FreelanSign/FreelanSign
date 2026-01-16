# Step 08: Verify Tests

## Objective
Run full test suite to ensure all tests pass and no regressions.

## Verification Sequence

### 1. Backend Tests

```bash
# Full test suite
pytest -v --tb=short

# With coverage
pytest --cov=apps --cov-report=term-missing
```

### 2. Frontend Tests

```bash
# Run all tests
pnpm test --run

# With coverage
pnpm test --coverage --run
```

### 3. Integration Tests (if applicable)

```bash
# Backend integration
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v
```

## Failure Analysis

### For Each Failing Test

```markdown
### ❌ Test: `test_name`

**File:** `path/to/test.py:L42`

**Error:**
```
AssertionError: Expected X, got Y
```

**Cause Analysis:**
- [ ] New code broke existing behavior
- [ ] Test needs update (behavior changed intentionally)
- [ ] Flaky test (non-deterministic)
- [ ] Missing dependency/setup

**Fix Strategy:**
- Option A: Fix the code
- Option B: Update the test (if behavior change intended)
```

## Test Categories

| Category | Action on Failure |
|----------|-------------------|
| New tests | MUST pass - fix code |
| Existing unit | MUST pass - investigate |
| Existing integration | SHOULD pass - may be flaky |
| Pre-existing failures | Note, don't block |

## Flaky Test Handling

If test intermittently fails:
1. Run 3 times
2. If passes 2/3 → Note as flaky
3. If fails 2/3 → Real issue, investigate

```bash
# Run specific test multiple times
pytest path/to/test.py -v --count=3
```

## Performance Check

```bash
# Check for slow tests (>1s)
pytest --durations=10
```

Flag tests > 1s for optimization.

## Output

```markdown
## Test Verification Results

### Backend
- Total: X tests
- Passed: X ✅
- Failed: X ❌
- Skipped: X ⏭️
- Duration: X.Xs

### Frontend
- Total: X tests
- Passed: X ✅
- Failed: X ❌
- Duration: X.Xs

### Coverage
- Backend: X%
- Frontend: X%

### Failures (if any)

#### ❌ test_name_1
- File: path/to/test.py
- Error: Brief description
- Status: Fixed / Needs attention

### Slow Tests (>1s)
- test_name: X.Xs

### Verification Verdict
- ✅ ALL PASS - Ready for Claude MD update
- ❌ FAILURES - Return to Step 06/07
```

## Gate Decision

```
All tests pass? → Proceed to Step 09
New test failures? → Return to Step 06 (Fix)
Only pre-existing failures? → Proceed with note
```
