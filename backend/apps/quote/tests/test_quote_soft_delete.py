"""
Tests for Quote soft delete functionality (RGPD compliance).

@author: @Bertrand2808
@since: 2025-12-15
@version: 1.0
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.client.models import Client
from apps.quote.models import Quote, QuoteHistory
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


@pytest.fixture
def quote_draft(user, account, client_obj):
    """Create test quote with DRAFT status."""
    return Quote.objects.create(
        owner=user,
        client=client_obj,
        account=account,
        title="Test Quote DRAFT",
        reference="Q-2025-001",
        status=Quote.Status.DRAFT,
        issue_date=timezone.now().date(),
        currency="EUR",
    )


@pytest.fixture
def quote_paid(user, account, client_obj):
    """Create test quote with PAID status."""
    return Quote.objects.create(
        owner=user,
        client=client_obj,
        account=account,
        title="Test Quote PAID",
        reference="Q-2025-002",
        status=Quote.Status.PAID,
        issue_date=timezone.now().date(),
        currency="EUR",
    )


@pytest.mark.django_db
class TestQuoteSoftDelete:
    """Test Quote soft delete behavior."""

    def test_quote_delete_soft_deletes_by_default(self, quote_draft):
        """Test that delete() soft deletes by default (uses DRAFT which is deletable)."""
        quote_id = quote_draft.id

        # Delete quote
        quote_draft.delete()

        # Should not be in default queryset
        assert not Quote.objects.filter(id=quote_id).exists()

        # Should be in all_objects queryset
        assert Quote.all_objects.filter(id=quote_id).exists()

        # Should be marked as deleted
        deleted_quote = Quote.all_objects.get(id=quote_id)
        assert deleted_quote.is_deleted is True
        assert deleted_quote.deleted_at is not None

    def test_quote_hard_delete_removes_from_db(self, quote_paid):
        """Test that hard delete removes from database."""
        quote_id = quote_paid.id

        # Hard delete
        quote_paid.delete(hard=True)

        # Should not exist in database at all
        assert not Quote.objects.filter(id=quote_id).exists()
        assert not Quote.all_objects.filter(id=quote_id).exists()

    def test_quote_objects_excludes_soft_deleted(self, user, account, client_obj):
        """Test that objects manager excludes soft deleted quotes (uses DRAFT which is deletable)."""
        # Create two quotes
        quote1 = Quote.objects.create(
            owner=user,
            client=client_obj,
            account=account,
            title="Quote 1",
            reference="Q-2025-001",
            status=Quote.Status.DRAFT,
            issue_date=timezone.now().date(),
            currency="EUR",
        )
        quote2 = Quote.objects.create(
            owner=user,
            client=client_obj,
            account=account,
            title="Quote 2",
            reference="Q-2025-002",
            status=Quote.Status.DRAFT,
            issue_date=timezone.now().date(),
            currency="EUR",
        )

        # Soft delete one
        quote1.delete()

        # objects should only return non-deleted
        assert Quote.objects.count() == 1
        assert Quote.objects.first().id == quote2.id

        # all_objects should return both
        assert Quote.all_objects.count() == 2

    def test_quote_undelete_restores(self, quote_draft):
        """Test that undelete() restores a soft deleted quote (uses DRAFT which is deletable)."""
        # Soft delete
        quote_draft.delete()
        assert quote_draft.is_deleted is True

        # Undelete
        quote_draft.undelete()

        # Should be restored
        assert quote_draft.is_deleted is False
        assert quote_draft.deleted_at is None
        assert Quote.objects.filter(id=quote_draft.id).exists()

    def test_quote_soft_delete_allowed_with_draft_status(self, quote_draft):
        """Test that delete is allowed for DRAFT status (RGPD compliance)."""
        # Should NOT raise ValidationError
        quote_draft.delete()

        # Quote should be soft deleted
        assert not Quote.objects.filter(id=quote_draft.id).exists()
        assert Quote.all_objects.filter(id=quote_draft.id, is_deleted=True).exists()

    def test_quote_soft_delete_blocked_with_sent_status(self, user, account, client_obj):
        """Test that delete is blocked for SENT status (RGPD compliance)."""
        quote = Quote.objects.create(
            owner=user,
            client=client_obj,
            account=account,
            title="Test Quote SENT",
            reference="Q-2025-003",
            status=Quote.Status.SENT,
            issue_date=timezone.now().date(),
            currency="EUR",
        )

        with pytest.raises(ValidationError, match="BROUILLON et ANNULÉ"):
            quote.delete()

        assert Quote.objects.filter(id=quote.id).exists()

    def test_quote_soft_delete_blocked_with_accepted_status(self, user, account, client_obj):
        """Test that delete is blocked for ACCEPTED status (RGPD compliance)."""
        quote = Quote.objects.create(
            owner=user,
            client=client_obj,
            account=account,
            title="Test Quote ACCEPTED",
            reference="Q-2025-004",
            status=Quote.Status.ACCEPTED,
            issue_date=timezone.now().date(),
            currency="EUR",
        )

        with pytest.raises(ValidationError, match="BROUILLON et ANNULÉ"):
            quote.delete()

        assert Quote.objects.filter(id=quote.id).exists()

    def test_quote_soft_delete_blocked_with_paid_status(self, quote_paid):
        """Test that soft delete is blocked if status is PAID (RGPD compliance)."""
        # Should raise ValidationError
        with pytest.raises(ValidationError, match="BROUILLON et ANNULÉ"):
            quote_paid.delete()

        # Quote should still exist and not be deleted
        assert Quote.objects.filter(id=quote_paid.id).exists()
        assert quote_paid.is_deleted is False

    def test_quote_soft_delete_allowed_with_cancelled_status(self, user, account, client_obj):
        """Test that soft delete is allowed if status is CANCELLED (RGPD compliance)."""
        quote = Quote.objects.create(
            owner=user,
            client=client_obj,
            account=account,
            title="Test Quote CANCELLED",
            reference="Q-2025-005",
            status=Quote.Status.CANCELLED,
            issue_date=timezone.now().date(),
            currency="EUR",
        )

        # Should succeed
        quote.delete()
        assert Quote.all_objects.filter(id=quote.id, is_deleted=True).exists()

    def test_quote_soft_delete_blocked_with_expired_status(self, user, account, client_obj):
        """Test that soft delete is blocked if status is EXPIRED (RGPD compliance)."""
        quote = Quote.objects.create(
            owner=user,
            client=client_obj,
            account=account,
            title="Test Quote EXPIRED",
            reference="Q-2025-006",
            status=Quote.Status.EXPIRED,
            issue_date=timezone.now().date(),
            currency="EUR",
        )

        # Should raise ValidationError
        with pytest.raises(ValidationError, match="BROUILLON et ANNULÉ"):
            quote.delete()

        assert Quote.objects.filter(id=quote.id).exists()

    def test_quote_soft_delete_blocked_with_rejected_status(self, user, account, client_obj):
        """Test that soft delete is blocked if status is REJECTED (RGPD compliance)."""
        quote = Quote.objects.create(
            owner=user,
            client=client_obj,
            account=account,
            title="Test Quote REJECTED",
            reference="Q-2025-007",
            status=Quote.Status.REJECTED,
            issue_date=timezone.now().date(),
            currency="EUR",
        )

        # Should raise ValidationError
        with pytest.raises(ValidationError, match="BROUILLON et ANNULÉ"):
            quote.delete()

        assert Quote.objects.filter(id=quote.id).exists()

    def test_quote_history_deleted_action_exists(self):
        """Test that DELETED action exists in QuoteHistory.Action choices."""
        assert hasattr(QuoteHistory.Action, "DELETED")
        assert QuoteHistory.Action.DELETED == "deleted"
