# apps/user/tests/application/usecases/test_get_user_accounts.py
"""Tests pour le use case GetUserAccounts."""
from datetime import datetime
from unittest.mock import Mock

from apps.user.application.dto.account_viewmodels import AccountListViewModel
from apps.user.application.usecases.get_user_accounts import GetUserAccounts
from apps.user.domain.entities.account import Account
from apps.user.domain.value_objects import LegalForm


class TestGetUserAccounts:
    """Tests du use case GetUserAccounts."""

    def test_get_active_accounts_only(self):
        """Test récupération des comptes actifs uniquement."""
        repository = Mock()
        account1 = Account(
            id=1,
            user_id=42,
            display_name="Account 1",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        account2 = Account(
            id=2,
            user_id=42,
            display_name="Account 2",
            legal_form=LegalForm.EURL,
            legal_id="12345678901234",
            domain_id=5,
            created_at=datetime(2024, 2, 1),
            updated_at=datetime(2024, 2, 1),
        )
        repository.get_by_user.return_value = [account1, account2]
        use_case = GetUserAccounts(repository=repository)

        result = use_case.execute(user_id=42, include_inactive=False)

        assert isinstance(result, AccountListViewModel)
        assert len(result.accounts) == 2
        assert result.total == 2
        assert result.accounts[0].display_name == "Account 1"
        repository.get_by_user.assert_called_once_with(42, include_inactive=False)

    def test_get_all_accounts_include_inactive(self):
        """Test récupération de tous les comptes."""
        repository = Mock()
        account = Account(
            id=1,
            user_id=42,
            display_name="Account",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        repository.get_by_user.return_value = [account]
        use_case = GetUserAccounts(repository=repository)

        result = use_case.execute(user_id=42, include_inactive=True)

        assert len(result.accounts) == 1
        repository.get_by_user.assert_called_once_with(42, include_inactive=True)

    def test_empty_list_for_user_with_no_accounts(self):
        """Test liste vide pour utilisateur sans compte."""
        repository = Mock()
        repository.get_by_user.return_value = []
        use_case = GetUserAccounts(repository=repository)

        result = use_case.execute(user_id=99)

        assert isinstance(result, AccountListViewModel)
        assert len(result.accounts) == 0
        assert result.total == 0
