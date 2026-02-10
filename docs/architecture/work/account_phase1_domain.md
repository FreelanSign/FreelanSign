# Phase 1 Implementation Plan: Account Domain Layer (TDD)

## Objective

Replace `ProfessionalUser` (1:1 with User) with `Account` model (1:N with User) to enable multi-entity management.
**Phase 1 scope**: Domain layer only - pure business logic, no Django dependencies.

## User Decisions

- **Legal ID**: Strict SIRET validation (14 digits only)
- **Name uniqueness**: Case-insensitive ('MyCompany' = 'mycompany')
- **Entity mutability**: Mutable (regular @dataclass, user can edit account fields anytime)

---

## 1. Account Entity Structure

**File**: `apps/user/domain/entities/account.py`

**Entity**:
```python
@dataclass
class Account:
    """Domain Entity for professional account (freelance entity).
    User can have multiple Accounts (future multi-entity)."""

    id: int
    user_id: int
    display_name: str          # maps from ProfessionalUser.name
    legal_form: LegalForm      # enum (from status_juridique)
    legal_id: str | None       # SIRET (14 digits)
    domain_id: int | None      # FK to catalog.Area
    created_at: datetime
    updated_at: datetime
```

**Field mappings from ProfessionalUser**:
- `name` → `display_name`
- `status_juridique` → `legal_form` (enum)
- `number_pro` → `legal_id` (SIRET validation)
- `domaine` → `domain_id`
- ❌ `tjm_cents` (stays User-level v1)
- ⏸️ `service_types` → `favorite_prestations` (Phase 3 M2M)

**Validation in `__post_init__`**:
- `display_name` not empty/whitespace
- `display_name` length <= 255

---

## 2. Value Objects

**File**: `apps/user/domain/value_objects.py`

**LegalForm enum**:
```python
class LegalForm(str, Enum):
    """Legal forms for French freelancers."""
    MICRO = "micro"
    EIRL = "eirl"
    EURL = "eurl"
    SASU = "sasu"
    OTHER = "other"
```

Values mirror StatusJuridique choices.

---

## 3. Domain Policies

**File**: `apps/user/domain/policies/account_policy.py`

**Class: AccountPolicy**

**Constants**:
```python
MIN_DISPLAY_NAME_LENGTH = 2
MAX_DISPLAY_NAME_LENGTH = 255
SIRET_LENGTH = 14
VALID_LEGAL_FORMS = [form.value for form in LegalForm]
```

**Validation methods**:

1. **`validate_display_name(name: str) -> None`**
   - Raise `InvalidDisplayNameError` if:
     - Empty/whitespace-only
     - Length < 2
     - Length > 255

2. **`validate_legal_form(legal_form: str | LegalForm) -> None`**
   - Convert to string if enum
   - Raise `InvalidLegalFormError` if not in VALID_LEGAL_FORMS

3. **`validate_legal_id(legal_id: str | None) -> None`**
   - If None or empty: return (optional field)
   - Raise `InvalidLegalIdError` if:
     - Not exactly 14 digits
     - Contains non-digit characters
   - **Regex**: `^[0-9]{14}$`

4. **`validate_domain_id(domain_id: int | None) -> None`**
   - If None: return (optional)
   - Raise `InvalidDomainIdError` if <= 0

5. **`validate_account_data(...) -> None`**
   - Composite validator: calls all individual validators
   - Signature: `(display_name: str, legal_form: str | LegalForm, legal_id: str | None = None, domain_id: int | None = None)`

6. **`validate_unique_display_name(...) -> None`**
   - Signature: `(user_id: int, display_name: str, existing_names: list[str], exclude_account_id: int | None = None)`
   - **Case-insensitive**: normalize with `.lower().strip()`
   - Raise `DuplicateAccountNameError` if collision
   - `exclude_account_id` for update scenarios

---

## 4. Domain Errors

**File**: `apps/user/domain/errors.py` (modify - add Account errors)

**Base error**:
```python
class AccountPolicyError(UserDomainError):
    def __init__(self, message: str):
        super().__init__(message, code="ACCOUNT_POLICY_ERROR")
```

**Specific errors**:
1. `InvalidDisplayNameError(name: str, reason: str = "")`
2. `InvalidLegalFormError(legal_form: str)`
3. `InvalidLegalIdError(legal_id: str, reason: str = "")`
4. `InvalidDomainIdError(domain_id: int | None)`
5. `DuplicateAccountNameError(user_id: int, display_name: str)`
6. `AccountNotFoundError(account_id: int, context: str = "")`

Follow pattern from apps/catalog/domain/errors.py.

---

## 5. TDD Test Structure

### Test files to create:

**A. `apps/user/tests/domain/test_legal_form_value_object.py` (3 tests)**
1. `test_legal_form_values` - All expected values exist
2. `test_legal_form_string_values` - `.value == "micro"`
3. `test_legal_form_membership` - value in list

**B. `apps/user/tests/domain/test_account_policy.py` (23 tests)**

Display name (4 tests):
1. `test_validate_display_name_success`
2. `test_validate_display_name_empty`
3. `test_validate_display_name_too_short`
4. `test_validate_display_name_too_long`

Legal form (3 tests):
5. `test_validate_legal_form_success_string`
6. `test_validate_legal_form_success_enum`
7. `test_validate_legal_form_invalid`

Legal ID / SIRET (6 tests):
8. `test_validate_legal_id_success_valid_siret`
9. `test_validate_legal_id_success_none`
10. `test_validate_legal_id_success_empty_string`
11. `test_validate_legal_id_invalid_too_short`
12. `test_validate_legal_id_invalid_too_long`
13. `test_validate_legal_id_invalid_non_numeric`

Domain ID (3 tests):
14. `test_validate_domain_id_success`
15. `test_validate_domain_id_zero_raises`
16. `test_validate_domain_id_negative_raises`

Composite (3 tests):
17. `test_validate_account_data_success`
18. `test_validate_account_data_invalid_display_name`
19. `test_validate_account_data_invalid_legal_id`

Unique name (4 tests):
20. `test_validate_unique_display_name_success`
21. `test_validate_unique_display_name_duplicate_exact`
22. `test_validate_unique_display_name_case_insensitive`
23. `test_validate_unique_display_name_exclude_self_update`

**C. `apps/user/tests/domain/test_account_entity.py` (5 tests)**
1. `test_account_creation_success`
2. `test_account_creation_minimal` - Required fields only
3. `test_account_mutable` - Can modify fields
4. `test_account_post_init_empty_display_name_raises`
5. `test_account_post_init_display_name_too_long_raises`

**Total: 31 tests**

---

## 6. TDD Implementation Order (RED-GREEN-REFACTOR)

### Step 1: Value Objects
1. Write `test_legal_form_value_object.py` (3 tests, RED)
2. Implement `value_objects.py` (GREEN)

### Step 2: Domain Errors
1. Add 6 new errors to `domain/errors.py`
2. Test inline in policy tests

### Step 3: Account Policy
1. Write ALL 23 tests in `test_account_policy.py` (RED)
2. Implement validators one by one (GREEN each subset)
3. Refactor

### Step 4: Account Entity
1. Write ALL 5 tests in `test_account_entity.py` (RED)
2. Implement `entities/account.py` dataclass (GREEN)
3. Implement `__post_init__` validation

---

## 7. Directory Structure

```
apps/user/
├── domain/
│   ├── entities/
│   │   ├── __init__.py          [CREATE]
│   │   └── account.py           [CREATE]
│   ├── value_objects.py         [CREATE]
│   ├── policies/
│   │   └── account_policy.py    [CREATE]
│   └── errors.py                [MODIFY - add Account errors]
└── tests/
    └── domain/                  [CREATE directory]
        ├── __init__.py          [CREATE]
        ├── test_legal_form_value_object.py  [CREATE]
        ├── test_account_policy.py           [CREATE]
        └── test_account_entity.py           [CREATE]
```

---

## 8. Validation Rules Summary

| Field | Required | Constraints |
|-------|----------|-------------|
| display_name | Yes | 2-255 chars, non-empty |
| legal_form | Yes | Must be in LegalForm enum |
| legal_id | No | Exactly 14 digits (SIRET format) |
| domain_id | No | Positive integer if provided |
| user_id | Yes | Positive integer |

**Business rules**:
- Unique: (user_id, display_name) - **case-insensitive**
- Normalization: `.lower().strip()` for comparison
- SIRET regex: `^[0-9]{14}$`

---

## 9. Test Execution

```bash
# Create test directory
mkdir -p apps/user/tests/domain
touch apps/user/tests/domain/__init__.py

# Run all domain tests
pytest apps/user/tests/domain/ -v

# Run specific file
pytest apps/user/tests/domain/test_account_policy.py::TestAccountPolicy::test_validate_legal_id_invalid_non_numeric -v

# Coverage
pytest apps/user/tests/domain/ --cov=apps.user.domain --cov-report=term-missing
```

**Expected**: 100% domain coverage, no DB access, <1s execution.

---

## 10. Dependencies

**Allowed (pure Python)**:
```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
```

**Internal**:
```python
from apps.user.domain.errors import InvalidDisplayNameError, ...
from apps.user.domain.value_objects import LegalForm
```

**Forbidden**:
- ❌ `django.db.models`
- ❌ `apps.catalog.models.Area`
- ✅ Use `int` for IDs, not model instances

---

## 11. Critical Files (Reference Patterns)

Must read before implementing:

1. **apps/catalog/domain/policies/prestation_policy.py**
   - Validation methods: @classmethod, constants, error raising

2. **apps/catalog/domain/errors.py**
   - Error hierarchy: base → policy → specific

3. **apps/catalog/tests/domain/test_prestation_policy.py**
   - Test structure: class-based, pytest.raises, naming

4. **apps/user/domain/errors.py**
   - Existing User errors to extend

---

## 12. Implementation Checklist

- [ ] Create `domain/entities/__init__.py`
- [ ] Create `domain/entities/account.py` (Account dataclass)
- [ ] Create `domain/value_objects.py` (LegalForm enum)
- [ ] Create `domain/policies/account_policy.py` (AccountPolicy)
- [ ] Modify `domain/errors.py` (add 6 Account errors)
- [ ] Create `tests/domain/__init__.py`
- [ ] Create `tests/domain/test_legal_form_value_object.py` (3 tests)
- [ ] Create `tests/domain/test_account_policy.py` (23 tests)
- [ ] Create `tests/domain/test_account_entity.py` (5 tests)
- [ ] ✅ All 31 tests passing
- [ ] ✅ 100% domain coverage
- [ ] ✅ No Django dependencies in domain layer

---

## 13. Key Design Decisions

**SIRET validation**: Strict 14-digit format (`^[0-9]{14}$`)
**Name uniqueness**: Case-insensitive - prevents "MyCompany" + "mycompany"
**Entity mutability**: Mutable dataclass (user can edit account anytime)
**Storage**: Preserve original case, normalize only for comparison

---

## Next Steps After Phase 1

Once domain layer complete (all tests green):
- **Phase 2**: Application layer (DTOs, use cases, ports)
- **Phase 3**: Persistence (Django models, migrations, repositories)
- **Phase 4**: Interface layer (API, serializers, middleware)
