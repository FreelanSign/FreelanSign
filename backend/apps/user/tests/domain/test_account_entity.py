# apps/user/tests/domain/test_account_entity.py
"""
Tests unitaires pour l'entité Account.
Tests purs, sans dépendance Django.
"""
from datetime import datetime

import pytest

from apps.user.domain.entities.account import Account
from apps.user.domain.errors import InvalidDisplayNameError
from apps.user.domain.value_objects import LegalForm


class TestAccountEntity:
    """Tests pour l'entité Account."""

    def test_account_creation_success(self):
        """Test création d'un compte avec tous les champs."""
        account = Account(
            id=1,
            user_id=42,
            display_name="Ma SARL Consulting",
            legal_form=LegalForm.EURL,
            legal_id="12345678901234",
            domain_id=5,
            is_active=True,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 15, 14, 30, 0),
        )

        assert account.id == 1
        assert account.user_id == 42
        assert account.display_name == "Ma SARL Consulting"
        assert account.legal_form == LegalForm.EURL
        assert account.legal_id == "12345678901234"
        assert account.domain_id == 5
        assert account.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert account.updated_at == datetime(2024, 1, 15, 14, 30, 0)

    def test_account_creation_minimal(self):
        """Test création d'un compte avec champs minimaux."""
        account = Account(
            id=2,
            user_id=10,
            display_name="Freelance Dev",
            legal_form=LegalForm.MICRO,
            legal_id=None,  # Optionnel
            domain_id=None,  # Optionnel
            is_active=True,
            created_at=datetime(2024, 2, 1),
            updated_at=datetime(2024, 2, 1),
        )

        assert account.id == 2
        assert account.user_id == 10
        assert account.display_name == "Freelance Dev"
        assert account.legal_form == LegalForm.MICRO
        assert account.legal_id is None
        assert account.domain_id is None

    def test_account_mutable(self):
        """Test qu'on peut modifier les champs d'un Account (mutable dataclass)."""
        account = Account(
            id=3,
            user_id=20,
            display_name="Initial Name",
            legal_form=LegalForm.MICRO,
            legal_id=None,
            domain_id=None,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Modifications
        account.display_name = "Updated Name"
        account.legal_form = LegalForm.EURL
        account.legal_id = "98765432109876"
        account.domain_id = 7

        assert account.display_name == "Updated Name"
        assert account.legal_form == LegalForm.EURL
        assert account.legal_id == "98765432109876"
        assert account.domain_id == 7

    def test_account_post_init_empty_display_name_raises(self):
        """Test que __post_init__ lève une erreur si display_name est vide."""
        with pytest.raises(InvalidDisplayNameError):
            Account(
                id=4,
                user_id=30,
                display_name="",  # Vide
                legal_form=LegalForm.MICRO,
                legal_id=None,
                domain_id=None,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

        with pytest.raises(InvalidDisplayNameError):
            Account(
                id=5,
                user_id=30,
                display_name="   ",  # Espaces seulement
                legal_form=LegalForm.MICRO,
                legal_id=None,
                domain_id=None,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_account_post_init_display_name_too_long_raises(self):
        """Test que __post_init__ lève une erreur si display_name est trop long."""
        long_name = "X" * 256  # > 255 caractères

        with pytest.raises(InvalidDisplayNameError):
            Account(
                id=6,
                user_id=40,
                display_name=long_name,
                legal_form=LegalForm.SASU,
                legal_id=None,
                domain_id=None,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
