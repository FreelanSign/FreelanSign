# Step 07: Add Tests

## Objective
Ensure all new behaviors have proper test coverage.

## Test Strategy

### What to Test

**ALWAYS test:**
- Domain logic and business rules
- Data transformations and calculations
- Edge cases and error conditions
- Public APIs and interfaces
- New code paths introduced

**DON'T test:**
- Framework behavior (trust Django/React)
- Simple getters/setters
- Third-party library internals
- UI styling (unless logic-dependent)

## Test Types by Layer

### Backend

| Layer | Test Type | Location |
|-------|-----------|----------|
| Domain | Unit | `tests/unit/domain/` |
| Application | Unit | `tests/unit/application/` |
| Infrastructure | Integration | `tests/integration/` |
| API | E2E | `tests/e2e/` |

### Frontend

| Type | Tool | Location |
|------|------|----------|
| Unit | Vitest | `*.test.ts(x)` |
| Component | Testing Library | `*.test.tsx` |
| Integration | Vitest | `*.integration.test.ts` |

## Test Quality Criteria

Each test MUST be:

- [ ] **Readable**: Failing test clearly shows what broke
- [ ] **Fast**: Unit tests < 100ms, integration < 1s
- [ ] **Isolated**: No shared state between tests
- [ ] **Deterministic**: Same input = same output, always

## Test Naming Convention

```python
# Python
def test_<action>_<scenario>_<expected_result>():
    # test_calculate_total_with_discount_returns_reduced_price
    pass

class Test<FeatureName>:
    def test_<scenario>(self):
        pass
```

```typescript
// TypeScript
describe('<ComponentOrFunction>', () => {
  it('should <action> when <condition>', () => {
    // should return total when items provided
  })
})
```

## Test Template

```python
# Backend - pytest
def test_feature_scenario_expected():
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value
```

```typescript
// Frontend - Vitest
it('should handle feature scenario', () => {
  // Arrange
  const props = { ... }

  // Act
  render(<Component {...props} />)

  // Assert
  expect(screen.getByText('...')).toBeInTheDocument()
})
```

## Coverage Targets

| Layer | Target |
|-------|--------|
| Domain | 100% |
| Application | 100% |
| Infrastructure | 80% |
| Presentation | 60% |

## Test Checklist

For each new behavior:
- [ ] Happy path test
- [ ] Error case test
- [ ] Edge case test (if applicable)
- [ ] Boundary test (if applicable)

## Output

```markdown
## Test Summary

### Tests Added

#### Backend
- `tests/unit/test_feature.py`
  - `test_scenario_1` - Happy path
  - `test_scenario_2` - Error case
  - `test_scenario_3` - Edge case

#### Frontend
- `src/components/Feature.test.tsx`
  - `should render correctly`
  - `should handle click event`
  - `should show error state`

### Coverage Report
- New code coverage: X%
- Overall coverage impact: +/-X%

### Missing Coverage (Justified)
- `file.ext:L42-L50` - Framework code, not tested

### Ready for Verification: YES/NO
```
