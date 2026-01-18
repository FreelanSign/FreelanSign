# apps/user/tests/test_account_soft_delete.py
"""
Tests for Account soft delete functionality (RGPD compliance).

Two-level soft delete:
- is_active=False: Reversible suspension
- is_deleted=True: RGPD soft delete with cascade to Clients

@author: @Bertrand2808
@since: 2025-12-09
@version: 1.0
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.client.models import Client
from apps.quote.models import Quote
from apps.user.models.account import Account

User = get_user_model()


@pytest.fixture
def user():
    """Create test user."""
    return User.objects.create_user(email="test@example.com", password="testpass123")


@pytest.fixture
def account(user):
    """Create test account."""
    return Account.objects.create(user=user, display_name="Test Account", legal_form="micro", is_active=True)


@pytest.fixture
def client_obj(user, account):
    """Create test client."""
    return Client.objects.create(owner=user, account=account, name="Test Client")


@pytest.mark.django_db
class TestAccountSoftDelete:
    """Test Account soft delete behavior with cascade."""

    def test_account_delete_soft_deletes_by_default(self, account):
        """Test that delete() soft deletes by default."""
        account_id = account.id

        # Delete account
        account.delete()

        # Should not be in default queryset
        assert not Account.objects.filter(id=account_id).exists()

        # Should be in all_objects queryset
        assert Account.all_objects.filter(id=account_id).exists()

        # Should be marked as deleted
        deleted_account = Account.all_objects.get(id=account_id)
        assert deleted_account.is_deleted is True
        assert deleted_account.deleted_at is not None

    def test_account_delete_cascades_to_clients(self, account, user):
        """Test that Account delete cascades to Clients."""
        # Create multiple clients
        client1 = Client.objects.create(owner=user, account=account, name="Client 1")
        client2 = Client.objects.create(owner=user, account=account, name="Client 2")

        # Delete account
        account.delete()

        # Account should be soft deleted
        assert not Account.objects.filter(id=account.id).exists()
        assert Account.all_objects.filter(id=account.id, is_deleted=True).exists()

        # Clients should be soft deleted (cascade)
        assert not Client.objects.filter(id=client1.id).exists()
        assert not Client.objects.filter(id=client2.id).exists()
        assert Client.all_objects.filter(id=client1.id, is_deleted=True).exists()
        assert Client.all_objects.filter(id=client2.id, is_deleted=True).exists()

    def test_account_is_active_and_is_deleted_independent(self, account):
        """Test that is_active and is_deleted are independent."""
        # Deactivate account (is_active=False)
        account.is_active = False
        account.save()

        # Should still be in default queryset (not soft deleted)
        assert Account.objects.filter(id=account.id).exists()
        assert account.is_deleted is False

        # Now soft delete
        account.delete()

        # Should be both inactive AND deleted
        deleted_account = Account.all_objects.get(id=account.id)
        assert deleted_account.is_active is False  # Retained
        assert deleted_account.is_deleted is True

    def test_account_hard_delete_removes_from_db(self, account):
        """Test that hard delete removes from database."""
        account_id = account.id

        # Hard delete
        account.delete(hard=True)

        # Should not exist in database at all
        assert not Account.objects.filter(id=account_id).exists()
        assert not Account.all_objects.filter(id=account_id).exists()

    def test_account_cascade_only_soft_deletes_active_clients(self, account, user):
        """Test that cascade only soft deletes non-deleted Clients."""
        # Create clients
        client1 = Client.objects.create(owner=user, account=account, name="Client 1")
        client2 = Client.objects.create(owner=user, account=account, name="Client 2")

        # Soft delete client1 manually first
        client1.delete()
        assert client1.is_deleted is True

        # Delete account
        account.delete()

        # Both clients should be soft deleted
        # client1 was already deleted, should remain deleted
        # client2 should now be deleted by cascade
        assert Client.all_objects.filter(id=client1.id, is_deleted=True).exists()
        assert Client.all_objects.filter(id=client2.id, is_deleted=True).exists()

    def test_account_undelete_restores_is_deleted_and_retains_is_active_state(self, account):
        """Test that undelete() restores is_deleted but retains is_active state."""
        # Deactivate and soft delete
        account.is_active = False
        account.save()
        account.delete()

        # Undelete
        account.undelete()

        # is_deleted should be restored, is_active should remain False
        assert account.is_deleted is False
        assert account.deleted_at is None
        assert account.is_active is False  # Retained

    def test_account_delete_is_atomic(self, account, user):
        """Test that cascade and account deletion are atomic."""
        # Create client
        client = Client.objects.create(owner=user, account=account, name="Test Client")

        # Create active quote to trigger ValueError in cascade
        Quote.objects.create(
            owner=user,
            client=client,
            account=account,
            title="Test Quote",
            reference="Q-2025-001",
            status="DRAFT",
            issue_date=timezone.now().date(),
        )

        # Try to delete account (should fail due to active quote on client)
        # The signal will block the client soft delete inside the transaction
        with pytest.raises(ValueError, match="des devis actifs existent"):
            account.delete()

        # AIDEV-NOTE: Le signal lève ValueError pendant le pre_save du Client
        # La transaction doit être rollback : ni Account ni Client ne doivent être modifiés

        # Account should not be deleted (transaction rollback)
        assert Account.objects.filter(id=account.id).exists()
        assert account.is_deleted is False

        # Client should not be deleted (transaction rollback)
        assert Client.objects.filter(id=client.id).exists()
        client.refresh_from_db()
        assert client.is_deleted is False

    def test_account_delete_blocked_with_active_quotes(self, account, user):
        """Test that Account delete is blocked if active Quotes exist."""
        # Create client
        client = Client.objects.create(owner=user, account=account, name="Test Client")

        # Create active quote (DRAFT)
        Quote.objects.create(
            owner=user,
            client=client,
            account=account,
            title="Test Quote",
            reference="Q-2025-001",
            status="DRAFT",
            issue_date=timezone.now().date(),
        )

        # Should raise ValueError
        with pytest.raises(ValueError, match="des devis actifs existent"):
            account.delete()

        # Account should still exist and not be deleted
        assert Account.objects.filter(id=account.id).exists()
        assert account.is_deleted is False

    def test_account_delete_allowed_with_paid_quotes(self, account, user):
        """Test that Account delete is allowed if only PAID quotes exist."""
        # Create client
        client = Client.objects.create(owner=user, account=account, name="Test Client")

        # Create PAID quote (transaction terminée)
        Quote.objects.create(
            owner=user,
            client=client,
            account=account,
            title="Test Quote",
            reference="Q-2025-001",
            status="PAID",
            issue_date=timezone.now().date(),
        )

        # Should NOT raise ValueError (PAID is not active)
        account.delete()

        # Account should be soft deleted
        assert not Account.objects.filter(id=account.id).exists()
        assert Account.all_objects.filter(id=account.id, is_deleted=True).exists()

        # Client should be soft deleted (cascade)
        assert not Client.objects.filter(id=client.id).exists()
        assert Client.all_objects.filter(id=client.id, is_deleted=True).exists()

    def test_account_objects_excludes_soft_deleted(self, user):
        """Test that objects manager excludes soft deleted accounts."""
        # Create two accounts
        account1 = Account.objects.create(user=user, display_name="Account 1", is_active=True)
        account2 = Account.objects.create(user=user, display_name="Account 2", is_active=True)

        # Soft delete one
        account1.delete()

        # objects should only return non-deleted
        assert Account.objects.count() == 1
        assert Account.objects.first().id == account2.id

        # all_objects should return both
        assert Account.all_objects.count() == 2
