# apps/user/application/usecases/check_quota_available.py
"""Check if account can create new quote based on plan quota limits."""

from datetime import datetime

from apps.quote.application.ports.quote_repository_extensions import QuoteRepositoryQuotaExt
from apps.user.application.ports.account_repository import AccountRepository
from apps.user.domain.policies.quota_policy import QuotaPolicy


class CheckQuotaAvailableUseCase:
    """
    Check if account can create new quote based on plan limits.

    Raises QuotaExceededError if any limit is exceeded.

    @author: @Bertrand2808
    @since: 2026-01-31
    """

    def __init__(
        self,
        account_repository: AccountRepository,
        quote_repository: QuoteRepositoryQuotaExt,
    ):
        self.account_repo = account_repository
        self.quote_repo = quote_repository

    def execute(self, account_id: int) -> None:
        """
        Validate quota availability for account.

        Args:
            account_id: Account ID to check

        Raises:
            ValueError: If account not found
            QuotaExceededError: If any quota limit is exceeded
        """
        # Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        # Count quotes this month
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        quotes_this_month = self.quote_repo.count_by_account_since(account_id, start_of_month)

        # Count active clients
        total_clients = self.account_repo.count_active_clients(account_id)

        # Validate against plan limits
        QuotaPolicy.validate_quota(
            plan=account.plan,
            current_quotes_this_month=quotes_this_month,
            current_clients=total_clients,
        )
