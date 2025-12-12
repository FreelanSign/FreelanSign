# apps/client/tests/test_anonymize_client.py
"""
Tests for client anonymization use case (RGPD Article 17).

Verifies that personal data is properly anonymized while preserving
quote references for the required 10-year retention period.

@author: AI Assistant
@since: 2025-12-12
@version: 1.0
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.client.application.usecases.anonymize_client import (
    anonymize_client_for_deletion,
)
from apps.client.models import Client
from apps.core.models.audit import AuditLog
from apps.quote.models import Quote
from apps.user.models.account import Account

User = get_user_model()


@pytest.fixture
def user(db):
    """Create test user."""
    return User.objects.create_user(email="test_client_anon@example.com", password="testpass123")


@pytest.fixture
def account(user):
    """Create test account."""
    return Account.objects.create(user=user, display_name="Test Account", legal_form="micro", is_active=True)


@pytest.fixture
def client_obj(user, account):
    """Create test client with full data."""
    return Client.objects.create(
        owner=user,
        account=account,
        name="Test Client Company",
        email="contact@testclient.com",
        phone="0123456789",
        address="123 Test Street, Test City",
        vat_number="FR12345678901",
        metadata={"industry": "tech", "size": "small"},
    )


@pytest.mark.django_db
class TestAnonymizeClient:
    """Test client anonymization functionality."""

    def test_anonymize_client_success(self, client_obj):
        """Test that client fields are properly anonymized."""
        client_id = client_obj.id
        original_name = client_obj.name

        # Run anonymization
        result = anonymize_client_for_deletion(client_id=str(client_id))

        # Verify success
        assert result["success"] is True
        assert result["client_id"] == str(client_id)

        # Reload from database
        client_obj.refresh_from_db()

        # Verify soft delete
        assert client_obj.is_deleted is True
        assert client_obj.deleted_at is not None

        # Verify anonymization
        assert client_obj.name == f"Client supprimé [{client_id}]"
        assert client_obj.email == f"deleted_{client_id}@anonymized.local"
        assert client_obj.phone == ""
        assert client_obj.address == ""
        assert client_obj.vat_number == ""
        assert client_obj.metadata == {}

    def test_anonymize_client_preserves_quote_references(self, client_obj, user, account):
        """Test that quotes still reference the anonymized client."""
        # Create a PAID quote
        quote = Quote.objects.create(
            owner=user,
            client=client_obj,
            account=account,
            title="Test Quote",
            reference="Q-2025-TEST-001",
            status="PAID",
            issue_date=timezone.now().date(),
        )

        # Run anonymization
        anonymize_client_for_deletion(client_id=str(client_obj.id))

        # Reload quote
        quote.refresh_from_db()
        client_obj.refresh_from_db()

        # Verify quote still exists
        assert Quote.objects.filter(id=quote.id).exists()

        # Verify quote references anonymized client
        assert quote.client.id == client_obj.id
        assert "supprimé" in quote.client.name

        # Verify quote data is intact
        assert quote.reference == "Q-2025-TEST-001"
        assert quote.status == "PAID"

    def test_anonymize_client_creates_audit_log(self, client_obj):
        """Test that audit log is created for client anonymization."""
        client_id = str(client_obj.id)

        # Run anonymization
        anonymize_client_for_deletion(client_id=client_id)

        # Verify audit log exists
        log = AuditLog.objects.filter(
            action=AuditLog.Action.CLIENT_ANONYMIZED,
            target_model="Client",
            target_id=client_id,
        ).first()

        assert log is not None
        assert log.actor is None  # No actor provided in test
        assert log.metadata is not None
        assert str(client_obj.account_id) == log.metadata.get("account_id")

    def test_anonymize_client_with_actor_and_request(self, client_obj, db):
        """Test that actor and IP are logged when provided."""
        from django.test import RequestFactory

        # Create actor and request
        actor = User.objects.create_user(email="admin@example.com", password="admin123")
        factory = RequestFactory()
        request = factory.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.200"

        # Run anonymization with actor and request
        anonymize_client_for_deletion(client_id=str(client_obj.id), actor=actor, request=request)

        # Verify audit log includes actor and IP
        log = AuditLog.objects.filter(
            action=AuditLog.Action.CLIENT_ANONYMIZED,
            target_model="Client",
            target_id=str(client_obj.id),
        ).first()

        assert log is not None
        assert log.actor == actor
        assert log.ip_address == "192.168.1.200"

    def test_anonymize_client_idempotent(self, client_obj):
        """Test that anonymizing multiple times doesn't cause errors."""
        client_id = str(client_obj.id)

        # First anonymization
        result1 = anonymize_client_for_deletion(client_id=client_id)
        assert result1["success"] is True

        # Reload
        client_obj.refresh_from_db()

        # Second anonymization (should not error)
        result2 = anonymize_client_for_deletion(client_id=client_id)
        assert result2["success"] is True

        # Verify still anonymized
        client_obj.refresh_from_db()
        assert client_obj.is_deleted is True
        assert "supprimé" in client_obj.name

    def test_anonymize_client_not_found_raises_error(self):
        """Test that anonymizing non-existent client raises error."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(Client.DoesNotExist):
            anonymize_client_for_deletion(client_id=fake_id)

    def test_anonymize_already_deleted_client(self, client_obj):
        """Test anonymizing a client that is already soft-deleted."""
        # Soft delete the client first
        client_obj.delete()
        client_obj.refresh_from_db()
        assert client_obj.is_deleted is True

        # Now anonymize it
        result = anonymize_client_for_deletion(client_id=str(client_obj.id))
        assert result["success"] is True

        # Verify anonymized
        client_obj.refresh_from_db()
        assert "supprimé" in client_obj.name
        assert client_obj.is_deleted is True

    def test_anonymize_client_with_multiple_quotes(self, client_obj, user, account):
        """Test anonymization with multiple quotes of different statuses."""
        # Create quotes with different statuses
        quote1 = Quote.objects.create(
            owner=user,
            client=client_obj,
            account=account,
            title="Quote 1",
            reference="Q-2025-001",
            status="PAID",
            issue_date=timezone.now().date(),
        )
        quote2 = Quote.objects.create(
            owner=user,
            client=client_obj,
            account=account,
            title="Quote 2",
            reference="Q-2025-002",
            status="CANCELLED",
            issue_date=timezone.now().date(),
        )

        # Run anonymization
        anonymize_client_for_deletion(client_id=str(client_obj.id))

        # Verify both quotes preserved
        quote1.refresh_from_db()
        quote2.refresh_from_db()

        # Note: Client.objects excludes soft-deleted, so use all_objects
        assert Client.all_objects.filter(id=client_obj.id).exists()
        assert quote1.client.id == client_obj.id
        assert quote2.client.id == client_obj.id
        assert quote1.reference == "Q-2025-001"
        assert quote2.reference == "Q-2025-002"

    def test_anonymize_client_clears_all_metadata(self, client_obj):
        """Test that metadata is properly cleared."""
        # Verify metadata exists before
        assert client_obj.metadata != {}

        # Run anonymization
        anonymize_client_for_deletion(client_id=str(client_obj.id))

        # Verify metadata cleared
        client_obj.refresh_from_db()
        assert client_obj.metadata == {}
