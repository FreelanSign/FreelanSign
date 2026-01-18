# apps/user/application/usecases/get_user_accounts.py
"""Use case: Récupérer les comptes d'un utilisateur."""

from apps.user.application.dto.account_viewmodels import AccountListViewModel, AccountViewModel
from apps.user.application.ports.account_repository import AccountRepository
from apps.user.domain.entities.account import Account


class GetUserAccounts:
    """Use case pour récupérer les comptes d'un utilisateur."""

    def __init__(self, repository: AccountRepository):
        self.repository = repository

    def execute(self, user_id: int, include_inactive: bool = False) -> AccountListViewModel:
        """Récupérer tous les comptes d'un utilisateur."""
        accounts = self.repository.get_by_user(user_id, include_inactive=include_inactive)
        account_vms = [self._to_viewmodel(acc) for acc in accounts]
        return AccountListViewModel(accounts=account_vms, total=len(account_vms))

    def _to_viewmodel(self, account: Account) -> AccountViewModel:
        """Convert Account entity to ViewModel."""
        return AccountViewModel(
            id=account.id,
            user_id=account.user_id,
            display_name=account.display_name,
            legal_form=account.legal_form.value,
            legal_id=account.legal_id,
            domain_id=account.domain_id,
            default_rate_cents=account.default_rate_cents,
            service_type_ids=account.service_type_ids,
            is_active=account.is_active,
            created_at=account.created_at,
            updated_at=account.updated_at,
        )
