# apps/user/tests/application/usecases/test_create_account.py
"""
Tests pour le use case CreateAccount.
"""
from datetime import datetime
from unittest.mock import Mock

import pytest

from apps.user.application.dto.account_inputs import CreateAccountInput
from apps.user.application.dto.account_viewmodels import AccountViewModel
from apps.user.application.usecases.create_account import CreateAccount
from apps.user.domain.entities.account import Account
from apps.user.domain.errors import (
    DuplicateAccountNameError,
    InvalidDisplayNameError,
    InvalidLegalFormError,
    InvalidLegalIdError,
)
from apps.user.domain.value_objects import LegalForm


class TestCreateAccount:
    """Tests du use case CreateAccount."""

    def test_create_account_success(self):
        """Test création réussie d'un compte."""
        # Arrange
        repository = Mock()
        clock = Mock()
        now = datetime(2024, 1, 15, 10, 30)
        clock.now.return_value = now

        # Mock repository behavior
        def create_side_effect(account: Account) -> Account:
            # Simulate DB assigning ID
            account.id = 1
            return account

        repository.create.side_effect = create_side_effect
        repository.exists_by_name.return_value = False

        use_case = CreateAccount(repository=repository, clock=clock)

        input_dto = CreateAccountInput(
            user_id=42,
            display_name="Ma Société SARL",
            legal_form="micro",
            legal_id="12345678901234",
            domain_id=5,
        )

        # Act
        result = use_case.execute(input_dto)

        # Assert
        assert isinstance(result, AccountViewModel)
        assert result.id == 1
        assert result.user_id == 42
        assert result.display_name == "Ma Société SARL"
        assert result.legal_form == "micro"
        assert result.legal_id == "12345678901234"
        assert result.domain_id == 5
        assert result.is_active is True
        assert result.created_at == now
        assert result.updated_at == now

        # Verify repository called
        repository.exists_by_name.assert_called_once_with(42, "Ma Société SARL", None)
        repository.create.assert_called_once()

    def test_create_account_invalid_display_name(self):
        """Test création avec display_name invalide."""
        repository = Mock()
        clock = Mock()
        use_case = CreateAccount(repository=repository, clock=clock)

        input_dto = CreateAccountInput(
            user_id=1,
            display_name="",  # Empty - invalid
            legal_form="micro",
        )

        with pytest.raises(InvalidDisplayNameError):
            use_case.execute(input_dto)

    def test_create_account_invalid_legal_form(self):
        """Test création avec forme juridique invalide."""
        repository = Mock()
        clock = Mock()
        use_case = CreateAccount(repository=repository, clock=clock)

        input_dto = CreateAccountInput(
            user_id=1,
            display_name="Test Company",
            legal_form="sarl",  # Not in LegalForm enum
        )

        with pytest.raises(InvalidLegalFormError):
            use_case.execute(input_dto)

    def test_create_account_invalid_siret(self):
        """Test création avec SIRET invalide."""
        repository = Mock()
        clock = Mock()
        repository.exists_by_name.return_value = False

        use_case = CreateAccount(repository=repository, clock=clock)

        input_dto = CreateAccountInput(
            user_id=1,
            display_name="Test Company",
            legal_form="micro",
            legal_id="123",  # Too short
        )

        with pytest.raises(InvalidLegalIdError):
            use_case.execute(input_dto)

    def test_create_account_duplicate_exact(self):
        """Test création avec nom en doublon (exact)."""
        repository = Mock()
        clock = Mock()
        repository.exists_by_name.return_value = True  # Name already exists

        use_case = CreateAccount(repository=repository, clock=clock)

        input_dto = CreateAccountInput(
            user_id=1,
            display_name="Existing Company",
            legal_form="micro",
        )

        with pytest.raises(DuplicateAccountNameError):
            use_case.execute(input_dto)

        repository.exists_by_name.assert_called_once_with(1, "Existing Company", None)

    def test_create_account_duplicate_case_insensitive(self):
        """Test création avec nom en doublon (case-insensitive)."""
        repository = Mock()
        clock = Mock()
        repository.exists_by_name.return_value = True  # "mycompany" exists

        use_case = CreateAccount(repository=repository, clock=clock)

        input_dto = CreateAccountInput(
            user_id=1,
            display_name="MyCompany",  # Different case but same
            legal_form="micro",
        )

        with pytest.raises(DuplicateAccountNameError):
            use_case.execute(input_dto)

    def test_create_account_with_professional_headline(self):
        """Test création avec professional_headline."""
        repository = Mock()
        clock = Mock()
        now = datetime(2024, 1, 15, 10, 30)
        clock.now.return_value = now

        def create_side_effect(account: Account) -> Account:
            account.id = 1
            return account

        repository.create.side_effect = create_side_effect
        repository.exists_by_name.return_value = False

        use_case = CreateAccount(repository=repository, clock=clock)

        input_dto = CreateAccountInput(
            user_id=42,
            display_name="Mon Entreprise",
            legal_form="micro",
            professional_headline="Développeur Fullstack",
        )

        result = use_case.execute(input_dto)

        assert isinstance(result, AccountViewModel)
        assert result.professional_headline == "Développeur Fullstack"
        repository.create.assert_called_once()
