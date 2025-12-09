# apps/client/tests/test_client_soft_delete.py
"""
Tests for Client soft delete functionality (RGPD compliance).

@author: @Bertrand2808
@since: 2025-12-09
@version: 1.0
"""
import pytest
from django.contrib.auth import get_user_model
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
    return Client.objects.create(
        owner=user, account=account, name="Test Client", email="client@example.com", phone="0123456789"
    )


@pytest.mark.django_db
class TestClientSoftDelete:
    """Test Client soft delete behavior."""

    def test_client_delete_soft_deletes_by_default(self, client_obj):
        """Test that delete() soft deletes by default."""
        client_id = client_obj.id

        # Delete client
        client_obj.delete()

        # Should not be in default queryset
        assert not Client.objects.filter(id=client_id).exists()

        # Should be in all_objects queryset
        assert Client.all_objects.filter(id=client_id).exists()

        # Should be marked as deleted
        deleted_client = Client.all_objects.get(id=client_id)
        assert deleted_client.is_deleted is True
        assert deleted_client.deleted_at is not None

    def test_client_hard_delete_removes_from_db(self, client_obj):
        """Test that hard delete removes from database."""
        client_id = client_obj.id

        # Hard delete
        client_obj.delete(hard=True)

        # Should not exist in database at all
        assert not Client.objects.filter(id=client_id).exists()
        assert not Client.all_objects.filter(id=client_id).exists()

    def test_client_objects_excludes_soft_deleted(self, user, account):
        """Test that objects manager excludes soft deleted clients."""
        # Create two clients
        client1 = Client.objects.create(owner=user, account=account, name="Client 1")
        client2 = Client.objects.create(owner=user, account=account, name="Client 2")

        # Soft delete one
        client1.delete()

        # objects should only return non-deleted
        assert Client.objects.count() == 1
        assert Client.objects.first().id == client2.id

        # all_objects should return both
        assert Client.all_objects.count() == 2

    def test_client_undelete_restores(self, client_obj):
        """Test that undelete() restores a soft deleted client."""
        # Soft delete
        client_obj.delete()
        assert client_obj.is_deleted is True

        # Undelete
        client_obj.undelete()

        # Should be restored
        assert client_obj.is_deleted is False
        assert client_obj.deleted_at is None
        assert Client.objects.filter(id=client_obj.id).exists()

    def test_client_soft_delete_blocked_with_active_quotes(self, client_obj):
        """Test that signal blocks soft delete if active quotes exist."""
        # Create active quote (DRAFT)
        Quote.objects.create(
            owner=client_obj.owner,
            client=client_obj,
            account=client_obj.account,
            title="Test Quote",
            reference="Q-2025-001",
            status="DRAFT",
            issue_date=timezone.now().date(),
        )

        # Should raise ValueError
        with pytest.raises(ValueError, match="des devis actifs existent"):
            client_obj.delete()

        # Refresh from DB to get actual state (signal prevents save)
        client_obj.refresh_from_db()

        # Client should still exist and not be deleted
        assert Client.objects.filter(id=client_obj.id).exists()
        assert client_obj.is_deleted is False

    def test_client_soft_delete_allowed_with_paid_quotes(self, client_obj):
        """Test that soft delete is allowed if only PAID quotes exist."""
        # Create PAID quote (transaction terminée)
        Quote.objects.create(
            owner=client_obj.owner,
            client=client_obj,
            account=client_obj.account,
            title="Test Quote",
            reference="Q-2025-001",
            status="PAID",
            issue_date=timezone.now().date(),
        )

        # Should NOT raise ValueError (PAID is not active)
        client_obj.delete()

        # Client should be soft deleted
        assert not Client.objects.filter(id=client_obj.id).exists()
        assert Client.all_objects.filter(id=client_obj.id, is_deleted=True).exists()

    def test_client_soft_delete_blocked_with_sent_quotes(self, client_obj):
        """Test that signal blocks soft delete for SENT quotes."""
        Quote.objects.create(
            owner=client_obj.owner,
            client=client_obj,
            account=client_obj.account,
            title="Test Quote",
            reference="Q-2025-001",
            status="SENT",
            issue_date=timezone.now().date(),
        )

        with pytest.raises(ValueError, match="des devis actifs existent"):
            client_obj.delete()

    def test_client_soft_delete_blocked_with_accepted_quotes(self, client_obj):
        """Test that signal blocks soft delete for ACCEPTED quotes."""
        Quote.objects.create(
            owner=client_obj.owner,
            client=client_obj,
            account=client_obj.account,
            title="Test Quote",
            reference="Q-2025-001",
            status="ACCEPTED",
            issue_date=timezone.now().date(),
        )

        with pytest.raises(ValueError, match="des devis actifs existent"):
            client_obj.delete()

    def test_client_soft_delete_allowed_with_cancelled_quotes(self, client_obj):
        """Test that soft delete is allowed if only CANCELLED quotes exist."""
        Quote.objects.create(
            owner=client_obj.owner,
            client=client_obj,
            account=client_obj.account,
            title="Test Quote",
            reference="Q-2025-001",
            status="CANCELLED",
            issue_date=timezone.now().date(),
        )

        # Should succeed
        client_obj.delete()
        assert Client.all_objects.filter(id=client_obj.id, is_deleted=True).exists()
