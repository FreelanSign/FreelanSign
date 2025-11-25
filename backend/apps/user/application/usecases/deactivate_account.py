# apps/user/application/usecases/deactivate_account.py
"""Use case: Désactiver un compte professionnel (soft delete)."""
from apps.user.application.errors import CannotDeactivateAccountError
from apps.user.application.ports.account_repository import AccountRepository
from apps.user.application.ports.clock import Clock
from apps.user.domain.errors import AccountNotFoundError


class DeactivateAccount:
    """Use case pour désactiver un compte."""

    def __init__(self, repository: AccountRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def execute(self, account_id: int) -> None:
        """Désactiver un compte (soft delete)."""
        # 1. Fetch account
        account = self.repository.get_by_id(account_id)
        if not account:
            raise AccountNotFoundError(account_id)

        # 2. Check if has quotes
        if self.repository.has_quotes(account_id):
            raise CannotDeactivateAccountError(account_id)

        # 3. Set updated_at (is_active will be added to entity in Phase 3)
        account.updated_at = self.clock.now()

        # 4. Persist (repository will set is_active=False in Phase 3)
        self.repository.update(account)
