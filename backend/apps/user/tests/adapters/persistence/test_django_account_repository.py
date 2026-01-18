# apps/user/tests/adapters/persistence/test_django_account_repository.py
"""
Minimal integration tests for DjangoAccountRepository.
Uses real database (pytest-django).

@author: @Bertrand2808
@since: 2025-11-25
@version: 1.0
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.user.adapters.persistence.django_account_repository import DjangoAccountRepository
from apps.user.adapters.system_clock import SystemClock
from apps.user.domain.entities.account import Account as AccountEntity
from apps.user.domain.value_objects import LegalForm
from apps.user.models.account import Account as AccountModel

User = get_user_model()


@pytest.mark.django_db
class TestDjangoAccountRepository:
    """Integration tests for AccountRepository using real DB."""

    def test_create_account_success(self):
        """Test creating an account persists to DB."""
        user = User.objects.create_user(email="test@example.com", password="pass123")
        repo = DjangoAccountRepository()
        clock = SystemClock()
        now = clock.now()

        entity = AccountEntity(
            id=0,
            user_id=user.id,
            display_name="Test Company",
            legal_form=LegalForm.MICRO,
            legal_id="12345678901234",
            domain_id=None,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        created = repo.create(entity)

        assert created.id > 0
        assert created.display_name == "Test Company"
        assert created.user_id == user.id

        # Verify in DB
        db_account = AccountModel.objects.get(id=created.id)
        assert db_account.display_name == "Test Company"

    def test_get_by_id_found(self):
        """Test retrieving existing account."""
        user = User.objects.create_user(email="user@test.com", password="pass")
        account_model = AccountModel.objects.create(
            user=user,
            display_name="My Account",
            legal_form="micro",
            is_active=True,
        )

        repo = DjangoAccountRepository()
        entity = repo.get_by_id(account_model.id)

        assert entity is not None
        assert entity.id == account_model.id
        assert entity.display_name == "My Account"

    def test_get_by_id_not_found(self):
        """Test retrieving non-existent account returns None."""
        repo = DjangoAccountRepository()
        entity = repo.get_by_id(99999)

        assert entity is None

    def test_update_account(self):
        """Test updating account fields."""
        user = User.objects.create_user(email="update@test.com", password="pass")
        account_model = AccountModel.objects.create(
            user=user,
            display_name="Old Name",
            legal_form="micro",
            is_active=True,
        )

        repo = DjangoAccountRepository()
        clock = SystemClock()

        # Fetch and modify
        entity = repo.get_by_id(account_model.id)
        entity.display_name = "New Name"
        entity.legal_form = LegalForm.EURL
        entity.updated_at = clock.now()

        updated = repo.update(entity)

        assert updated.display_name == "New Name"
        assert updated.legal_form == LegalForm.EURL

        # Verify in DB
        db_account = AccountModel.objects.get(id=account_model.id)
        assert db_account.display_name == "New Name"

    def test_unique_constraint_enforced(self):
        """Test that unique(user, display_name) constraint works."""
        user = User.objects.create_user(email="unique@test.com", password="pass")
        AccountModel.objects.create(
            user=user,
            display_name="Company A",
            legal_form="micro",
        )

        # Try to create duplicate
        with pytest.raises(IntegrityError):
            AccountModel.objects.create(
                user=user,
                display_name="Company A",
                legal_form="eurl",
            )

    def test_exists_by_name_case_insensitive(self):
        """Test existence check is case-insensitive."""
        user = User.objects.create_user(email="case@test.com", password="pass")
        AccountModel.objects.create(
            user=user,
            display_name="MyCompany",
            legal_form="micro",
        )

        repo = DjangoAccountRepository()

        assert repo.exists_by_name(user.id, "MyCompany") is True
        assert repo.exists_by_name(user.id, "mycompany") is True
        assert repo.exists_by_name(user.id, "MYCOMPANY") is True
        assert repo.exists_by_name(user.id, "OtherName") is False
