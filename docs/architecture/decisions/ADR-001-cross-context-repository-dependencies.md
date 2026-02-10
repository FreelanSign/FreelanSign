# Architecture Decision Record: Cross-Context Repository Dependencies

## Context

In Phase 3, `DeactivateAccount` use case needs to check if an account has associated quotes before allowing deactivation. This creates a cross-bounded-context dependency.

## Problem

Current implementation (Phase 3):
- `AccountRepository.has_quotes()` imports `Quote.models` directly
- Violates Single Responsibility Principle
- Creates cross-module coupling at adapter layer
- Uses temporary `owner_id` workaround instead of `account_id`

## Decision

**Phase 4 Refactoring Plan**:

1. **Remove** `has_quotes()` from `AccountRepository` port
2. **Add** `exists_for_account(account_id: int) -> bool` to `QuoteRepository` port
3. **Inject** `QuoteRepository` into `DeactivateAccount` use case
4. **Check** constraint at Application layer (use case), not Adapter layer (repository)

## Implementation

### Before (Phase 3 - Current)
```python
# user/application/ports/account_repository.py
class AccountRepository(Protocol):
    def has_quotes(self, account_id: int) -> bool: ...  # ❌ Cross-context

# user/application/usecases/deactivate_account.py
class DeactivateAccount:
    def __init__(self, repository: AccountRepository, clock: Clock):
        self.repository = repository

    def execute(self, account_id: int):
        if self.repository.has_quotes(account_id):  # ❌ Smell
            raise CannotDeactivateAccountError(account_id)
```

### After (Phase 4 - Target)
```python
# quote/application/ports/quote_repository.py
class QuoteRepository(Protocol):
    def exists_for_account(self, account_id: int) -> bool: ...  # ✅ Proper context

# user/application/usecases/deactivate_account.py
class DeactivateAccount:
    def __init__(
        self,
        account_repository: AccountRepository,
        quote_repository: QuoteRepository,  # ✅ Injected dependency
        clock: Clock
    ):
        self.account_repository = account_repository
        self.quote_repository = quote_repository

    def execute(self, account_id: int):
        if self.quote_repository.exists_for_account(account_id):  # ✅ Clean
            raise CannotDeactivateAccountError(account_id)
```

## Consequences

### Positive
- ✅ Single Responsibility: Each repository manages its own context
- ✅ Testability: Easy to mock `QuoteRepository` in tests
- ✅ Bounded Context separation maintained
- ✅ Cross-context logic lives in Application layer (where it belongs)

### Negative
- ⚠️ `DeactivateAccount` use case now has 3 dependencies instead of 2
- ⚠️ Application layer depends on both `user` and `quote` contexts (acceptable for cross-context use case)

## Related

- Issue #54 Phase 3
- DDD: Repositories should stay within their bounded context
- Clean Architecture: Application layer orchestrates cross-context operations

## Status

**Phase 3**: Temporary implementation with documented smell
**Phase 4**: Planned refactoring (target implementation above)
**Phase 5**: `Quote.account_id` migration will simplify `exists_for_account` implementation

---

**Author**: @Bertrand2808
**Date**: 2025-11-25
**Reviewers**: Antigravity AI
