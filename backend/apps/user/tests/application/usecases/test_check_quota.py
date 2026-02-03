"""Integration tests for CheckQuotaAvailableUseCase."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from apps.user.application.usecases.check_quota_available import CheckQuotaAvailableUseCase
from apps.user.domain.entities.account import Account
from apps.user.domain.errors import QuotaExceededError
from apps.user.domain.value_objects import LegalForm


@pytest.fixture
def mock_account_repository():
    """Mock AccountRepository."""
    return Mock()


@pytest.fixture
def mock_quote_repository():
    """Mock QuoteRepository."""
    return Mock()


@pytest.fixture
def check_quota_use_case(mock_account_repository, mock_quote_repository):
    """CheckQuotaAvailableUseCase instance with mocks."""
    return CheckQuotaAvailableUseCase(
        account_repository=mock_account_repository,
        quote_repository=mock_quote_repository,
    )


def create_test_account(plan: str = "beta") -> Account:
    """Helper to create test Account entity."""
    return Account(
        id=1,
        user_id=1,
        display_name="Test Account",
        legal_form=LegalForm.MICRO,
        legal_id=None,
        domain_id=None,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        plan=plan,
        max_quotes_monthly=None,
        max_clients=None,
    )


class TestCheckQuotaAvailableUseCase:
    """Test CheckQuotaAvailableUseCase."""

    def test_beta_account_allows_unlimited_quotes(self, check_quota_use_case, mock_account_repository, mock_quote_repository):
        """Beta account passes quota check with any usage."""
        account = create_test_account(plan="beta")
        mock_account_repository.get_by_id.return_value = account
        mock_quote_repository.count_by_account_since.return_value = 1000
        mock_account_repository.count_active_clients.return_value = 1000

        # Should not raise
        check_quota_use_case.execute(account_id=1)

    def test_pro_account_allows_unlimited_quotes(self, check_quota_use_case, mock_account_repository, mock_quote_repository):
        """Pro account passes quota check with any usage."""
        account = create_test_account(plan="pro")
        mock_account_repository.get_by_id.return_value = account
        mock_quote_repository.count_by_account_since.return_value = 1000
        mock_account_repository.count_active_clients.return_value = 1000

        # Should not raise
        check_quota_use_case.execute(account_id=1)

    def test_free_account_allows_within_quote_limit(
        self, check_quota_use_case, mock_account_repository, mock_quote_repository
    ):
        """Free account with 4/5 quotes passes."""
        account = create_test_account(plan="free")
        mock_account_repository.get_by_id.return_value = account
        mock_quote_repository.count_by_account_since.return_value = 4
        mock_account_repository.count_active_clients.return_value = 2

        # Should not raise
        check_quota_use_case.execute(account_id=1)

    def test_free_account_blocks_at_quote_limit(self, check_quota_use_case, mock_account_repository, mock_quote_repository):
        """Free account with 5/5 quotes is blocked."""
        account = create_test_account(plan="free")
        mock_account_repository.get_by_id.return_value = account
        mock_quote_repository.count_by_account_since.return_value = 5
        mock_account_repository.count_active_clients.return_value = 2

        with pytest.raises(QuotaExceededError) as exc_info:
            check_quota_use_case.execute(account_id=1)

        assert "Monthly quota exceeded" in str(exc_info.value)

    def test_free_account_blocks_over_quote_limit(self, check_quota_use_case, mock_account_repository, mock_quote_repository):
        """Free account with 6/5 quotes is blocked."""
        account = create_test_account(plan="free")
        mock_account_repository.get_by_id.return_value = account
        mock_quote_repository.count_by_account_since.return_value = 6
        mock_account_repository.count_active_clients.return_value = 2

        with pytest.raises(QuotaExceededError):
            check_quota_use_case.execute(account_id=1)

    def test_free_account_allows_within_client_limit(
        self, check_quota_use_case, mock_account_repository, mock_quote_repository
    ):
        """Free account with 2/3 clients passes."""
        account = create_test_account(plan="free")
        mock_account_repository.get_by_id.return_value = account
        mock_quote_repository.count_by_account_since.return_value = 0
        mock_account_repository.count_active_clients.return_value = 2

        # Should not raise
        check_quota_use_case.execute(account_id=1)

    def test_free_account_blocks_at_client_limit(self, check_quota_use_case, mock_account_repository, mock_quote_repository):
        """Free account with 3/3 clients is blocked."""
        account = create_test_account(plan="free")
        mock_account_repository.get_by_id.return_value = account
        mock_quote_repository.count_by_account_since.return_value = 0
        mock_account_repository.count_active_clients.return_value = 3

        with pytest.raises(QuotaExceededError) as exc_info:
            check_quota_use_case.execute(account_id=1)

        assert "Client limit reached" in str(exc_info.value)

    def test_account_not_found_raises_value_error(self, check_quota_use_case, mock_account_repository):
        """Non-existent account raises ValueError."""
        mock_account_repository.get_by_id.return_value = None

        with pytest.raises(ValueError) as exc_info:
            check_quota_use_case.execute(account_id=999)

        assert "Account not found" in str(exc_info.value)

    def test_calls_repository_with_correct_account_id(
        self, check_quota_use_case, mock_account_repository, mock_quote_repository
    ):
        """Use case calls repository with correct account_id."""
        account = create_test_account(plan="beta")
        mock_account_repository.get_by_id.return_value = account

        check_quota_use_case.execute(account_id=42)

        mock_account_repository.get_by_id.assert_called_once_with(42)

    def test_counts_quotes_from_start_of_month(self, check_quota_use_case, mock_account_repository, mock_quote_repository):
        """Use case counts quotes from start of current month."""
        account = create_test_account(plan="free")
        mock_account_repository.get_by_id.return_value = account
        mock_quote_repository.count_by_account_since.return_value = 0
        mock_account_repository.count_active_clients.return_value = 0

        check_quota_use_case.execute(account_id=1)

        # Verify count_by_account_since was called with account_id and a datetime
        assert mock_quote_repository.count_by_account_since.called
        call_args = mock_quote_repository.count_by_account_since.call_args
        assert call_args[0][0] == 1  # account_id
        assert isinstance(call_args[0][1], datetime)  # start_of_month datetime
