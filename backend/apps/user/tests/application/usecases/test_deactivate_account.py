# apps/user/tests/application/usecases/test_deactivate_account.py
"""Tests pour le use case DeactivateAccount."""
from datetime import datetime
from unittest.mock import Mock

import pytest

from apps.user.application.errors import CannotDeactivateAccountError
from apps.user.application.usecases.deactivate_account import DeactivateAccount
from apps.user.domain.entities.account import Account
from apps.user.domain.errors import AccountNotFoundError
from apps.user.domain.value_objects import LegalForm


class TestDeactivateAccount:
    """Tests du use case DeactivateAccount."""

    def test_deactivate_account_success(self):
        """Test désactivation réussie d'un compte sans devis."""
        repository = Mock()
        clock = Mock()
        clock.now.return_value = datetime(2024, 3, 1)

        existing = Account(
            id=1,
            user_id=10,
            display_name="My Account",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        repository.get_by_id.return_value = existing
        repository.has_quotes.return_value = False
        repository.update.return_value = existing

        use_case = DeactivateAccount(repository=repository, clock=clock)

        use_case.execute(account_id=1)

        repository.has_quotes.assert_called_once_with(1)
        repository.update.assert_called_once()

    def test_deactivate_account_not_found(self):
        """Test compte non trouvé."""
        repository = Mock()
        clock = Mock()
        repository.get_by_id.return_value = None

        use_case = DeactivateAccount(repository=repository, clock=clock)

        with pytest.raises(AccountNotFoundError):
            use_case.execute(account_id=999)

    def test_cannot_deactivate_if_has_quotes(self):
        """Test impossible de désactiver si le compte a des devis."""
        repository = Mock()
        clock = Mock()

        existing = Account(
            id=1,
            user_id=10,
            display_name="Account",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        repository.get_by_id.return_value = existing
        repository.has_quotes.return_value = True

        use_case = DeactivateAccount(repository=repository, clock=clock)

        with pytest.raises(CannotDeactivateAccountError):
            use_case.execute(account_id=1)

        repository.update.assert_not_called()

    def test_deactivate_already_inactive_idempotent(self):
        """Test désactivation idempotente (déjà inactif)."""
        repository = Mock()
        clock = Mock()
        clock.now.return_value = datetime(2024, 3, 1)

        existing = Account(
            id=1,
            user_id=10,
            display_name="Inactive",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 2, 1),
        )
        repository.get_by_id.return_value = existing
        repository.has_quotes.return_value = False
        repository.update.return_value = existing

        use_case = DeactivateAccount(repository=repository, clock=clock)

        use_case.execute(account_id=1)

        repository.update.assert_called_once()
