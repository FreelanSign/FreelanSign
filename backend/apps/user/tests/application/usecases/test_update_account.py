# apps/user/tests/application/usecases/test_update_account.py
"""Tests pour le use case UpdateAccount."""
from datetime import datetime
from unittest.mock import Mock

import pytest

from apps.user.application.dto.account_inputs import UpdateAccountInput
from apps.user.application.dto.account_viewmodels import AccountViewModel
from apps.user.application.usecases.update_account import UpdateAccount
from apps.user.domain.entities.account import Account
from apps.user.domain.errors import (
    AccountNotFoundError,
    DuplicateAccountNameError,
    InvalidDisplayNameError,
    InvalidLegalIdError,
)
from apps.user.domain.value_objects import LegalForm


class TestUpdateAccount:
    """Tests du use case UpdateAccount."""

    def test_update_account_display_name_success(self):
        """Test mise à jour du display_name."""
        repository = Mock()
        clock = Mock()
        now = datetime(2024, 2, 1, 14, 0)
        clock.now.return_value = now

        existing = Account(
            id=1,
            user_id=10,
            display_name="Old Name",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            created_at=datetime(2024, 1, 1),
            is_active=True,
            updated_at=datetime(2024, 1, 1),
        )
        repository.get_by_id.return_value = existing
        repository.exists_by_name.return_value = False
        repository.update.return_value = existing

        use_case = UpdateAccount(repository=repository, clock=clock)
        input_dto = UpdateAccountInput(
            account_id=1, display_name="New Name", legal_form="micro", legal_id=None, domain_id=None
        )

        result = use_case.execute(input_dto)

        assert isinstance(result, AccountViewModel)
        assert result.display_name == "New Name"
        assert result.updated_at == now
        repository.update.assert_called_once()

    def test_update_account_all_fields_success(self):
        """Test mise à jour de tous les champs."""
        repository = Mock()
        clock = Mock()
        clock.now.return_value = datetime(2024, 2, 1)

        existing = Account(
            id=2,
            user_id=20,
            display_name="Company",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            created_at=datetime(2024, 1, 1),
            is_active=True,
            updated_at=datetime(2024, 1, 1),
        )
        repository.get_by_id.return_value = existing
        repository.exists_by_name.return_value = False
        repository.update.return_value = existing

        use_case = UpdateAccount(repository=repository, clock=clock)
        input_dto = UpdateAccountInput(
            account_id=2, display_name="New Company", legal_form="eurl", legal_id="12345678901234", domain_id=5
        )

        result = use_case.execute(input_dto)

        assert result.legal_form == "eurl"
        assert result.legal_id == "12345678901234"
        assert result.domain_id == 5

    def test_update_account_not_found(self):
        """Test compte non trouvé."""
        repository = Mock()
        clock = Mock()
        repository.get_by_id.return_value = None

        use_case = UpdateAccount(repository=repository, clock=clock)
        input_dto = UpdateAccountInput(account_id=999, display_name="Test", legal_form="micro")

        with pytest.raises(AccountNotFoundError):
            use_case.execute(input_dto)

    def test_update_account_invalid_display_name(self):
        """Test display_name invalide."""
        repository = Mock()
        clock = Mock()

        use_case = UpdateAccount(repository=repository, clock=clock)
        input_dto = UpdateAccountInput(account_id=1, display_name="", legal_form="micro")

        with pytest.raises(InvalidDisplayNameError):
            use_case.execute(input_dto)

    def test_update_account_invalid_siret(self):
        """Test SIRET invalide."""
        repository = Mock()
        clock = Mock()
        existing = Account(
            id=1,
            user_id=10,
            display_name="Test",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            created_at=datetime(2024, 1, 1),
            is_active=True,
            updated_at=datetime(2024, 1, 1),
        )
        repository.get_by_id.return_value = existing
        repository.exists_by_name.return_value = False

        use_case = UpdateAccount(repository=repository, clock=clock)
        input_dto = UpdateAccountInput(account_id=1, display_name="Test", legal_form="micro", legal_id="123")

        with pytest.raises(InvalidLegalIdError):
            use_case.execute(input_dto)

    def test_update_account_duplicate_name_with_another(self):
        """Test nom en doublon avec un autre compte."""
        repository = Mock()
        clock = Mock()
        existing = Account(
            id=1,
            user_id=10,
            display_name="My Company",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            created_at=datetime(2024, 1, 1),
            is_active=True,
            updated_at=datetime(2024, 1, 1),
        )
        repository.get_by_id.return_value = existing
        repository.exists_by_name.return_value = True

        use_case = UpdateAccount(repository=repository, clock=clock)
        input_dto = UpdateAccountInput(account_id=1, display_name="Other Company", legal_form="micro")

        with pytest.raises(DuplicateAccountNameError):
            use_case.execute(input_dto)

    def test_update_account_keep_same_name(self):
        """Test garder le même nom (pas d'erreur unicité)."""
        repository = Mock()
        clock = Mock()
        clock.now.return_value = datetime(2024, 2, 1)

        existing = Account(
            id=1,
            user_id=10,
            display_name="Same Name",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            created_at=datetime(2024, 1, 1),
            is_active=True,
            updated_at=datetime(2024, 1, 1),
        )
        repository.get_by_id.return_value = existing
        repository.exists_by_name.return_value = False
        repository.update.return_value = existing

        use_case = UpdateAccount(repository=repository, clock=clock)
        input_dto = UpdateAccountInput(account_id=1, display_name="Same Name", legal_form="micro")

        result = use_case.execute(input_dto)

        assert result.display_name == "Same Name"
        repository.exists_by_name.assert_called_once_with(10, "Same Name", exclude_id=1)

    def test_update_account_with_professional_headline(self):
        """Test mise à jour du professional_headline."""
        repository = Mock()
        clock = Mock()
        now = datetime(2024, 2, 1, 14, 0)
        clock.now.return_value = now

        existing = Account(
            id=1,
            user_id=10,
            display_name="My Company",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            professional_headline=None,
            created_at=datetime(2024, 1, 1),
            is_active=True,
            updated_at=datetime(2024, 1, 1),
        )
        repository.get_by_id.return_value = existing
        repository.exists_by_name.return_value = False
        repository.update.return_value = existing

        use_case = UpdateAccount(repository=repository, clock=clock)
        input_dto = UpdateAccountInput(
            account_id=1,
            display_name="My Company",
            legal_form="micro",
            professional_headline="Développeur Fullstack",
        )

        result = use_case.execute(input_dto)

        assert isinstance(result, AccountViewModel)
        assert result.professional_headline == "Développeur Fullstack"
        repository.update.assert_called_once()
