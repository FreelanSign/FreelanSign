# apps/user/tests/test_anonymize_account.py
"""
Tests for account anonymization use case (RGPD Article 17).

Verifies that personal data is properly anonymized while preserving
legal/accounting data for the required 10-year retention period.

@author: AI Assistant
@since: 2025-12-12
@version: 1.0
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.client.models import Client
from apps.core.models.audit import AuditLog
from apps.quote.models import Quote
from apps.user.application.usecases.anonymize_account import (
    anonymize_account_for_deletion,
)
from apps.user.models.account import Account
from apps.user.models.models import Profile

User = get_user_model()


@pytest.fixture
def user(db):
    """Create test user with profile."""
    user = User.objects.create_user(
        email="test_anon@example.com",
        password="testpass123",
        first_name="John",
        last_name="Doe",
    )
    # Explicitly create profile (may not be automatic in tests)
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            "phone": "0123456789",
            "avatar_url": "https://example.com/avatar.jpg",
        },
    )
    if not profile.phone:
        profile.phone = "0123456789"
        profile.avatar_url = "https://example.com/avatar.jpg"
        profile.save()
    return user


@pytest.fixture
def account(user):
    """Create test account."""
    return Account.objects.create(
        user=user,
        display_name="Test Account for Anonymization",
        legal_form="micro",
        legal_id="12345678901234",  # SIRET
        is_active=True,
    )


@pytest.fixture
def client_obj(user, account):
    """Create test client."""
    return Client.objects.create(
        owner=user,
        account=account,
        name="Test Client",
        email="client@example.com",
    )


@pytest.mark.django_db
class TestAnonymizeAccount:
    """Test account anonymization functionality."""

    def test_anonymize_account_success(self, account, user):
        """Test that account, user, and profile are properly anonymized."""
        account_id = account.id
        user_id = user.id
        original_display_name = account.display_name

        # Run anonymization
        result = anonymize_account_for_deletion(account_id=str(account_id))

        # Verify success
        assert result["success"] is True
        assert result["account_id"] == str(account_id)

        # Reload models from database
        account.refresh_from_db()
        user.refresh_from_db()
        profile = user.profile
        profile.refresh_from_db()

        # Verify Account anonymization
        assert account.is_active is False
        assert account.display_name == f"Compte supprimé [{account_id}]"
        assert account.legal_id is None

        # Verify User anonymization
        assert user.email == f"deleted_{user_id}@anonymized.local"
        assert user.first_name == "Utilisateur"
        assert user.last_name == "Supprimé"
        assert user.is_active is False

        # Verify Profile anonymization
        assert profile.phone is None
        assert profile.avatar_url is None

    def test_anonymize_account_preserves_quotes(self, account, user, client_obj):
        """Test that quotes are preserved with anonymized references."""
        # Create a PAID quote (legal requirement to preserve)
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
        result = anonymize_account_for_deletion(account_id=str(account.id))

        # Reload quote
        quote.refresh_from_db()
        account.refresh_from_db()

        # Verify quote still exists
        assert Quote.objects.filter(id=quote.id).exists()

        # Verify quote references anonymized account
        assert quote.account.id == account.id
        assert "supprimé" in quote.account.display_name

        # Verify quote data is intact
        assert quote.reference == "Q-2025-TEST-001"
        assert quote.status == "PAID"

    def test_anonymize_account_creates_audit_log(self, account, user):
        """Test that audit log is created for anonymization."""
        account_id = str(account.id)

        # Run anonymization
        anonymize_account_for_deletion(account_id=account_id)

        # Verify audit log exists
        log = AuditLog.objects.filter(
            action=AuditLog.Action.ACCOUNT_ANONYMIZED,
            target_model="Account",
            target_id=account_id,
        ).first()

        assert log is not None
        assert log.actor is None  # No actor provided in test
        assert log.metadata is not None
        assert str(user.id) in str(log.metadata.get("user_id", ""))

    def test_anonymize_account_with_actor_and_request(self, account, user, db):
        """Test that actor and IP are logged when provided."""
        from django.test import RequestFactory

        # Create actor and request
        actor = User.objects.create_user(email="admin@example.com", password="admin123")
        factory = RequestFactory()
        request = factory.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        # Run anonymization with actor and request
        anonymize_account_for_deletion(account_id=str(account.id), actor=actor, request=request)

        # Verify audit log includes actor and IP
        log = AuditLog.objects.filter(
            action=AuditLog.Action.ACCOUNT_ANONYMIZED,
            target_model="Account",
            target_id=str(account.id),
        ).first()

        assert log is not None
        assert log.actor == actor
        assert log.ip_address == "192.168.1.100"

    def test_anonymize_account_idempotent(self, account, user):
        """Test that anonymizing multiple times doesn't cause errors."""
        account_id = str(account.id)

        # First anonymization
        result1 = anonymize_account_for_deletion(account_id=account_id)
        assert result1["success"] is True

        # Reload
        account.refresh_from_db()
        user.refresh_from_db()

        # Second anonymization (should not error)
        result2 = anonymize_account_for_deletion(account_id=account_id)
        assert result2["success"] is True

        # Verify still anonymized
        account.refresh_from_db()
        assert account.is_active is False
        assert "supprimé" in account.display_name

    def test_anonymize_account_not_found_raises_error(self):
        """Test that anonymizing non-existent account raises error."""
        fake_id = "999999"  # Account uses auto-increment integer ID

        with pytest.raises(Account.DoesNotExist):
            anonymize_account_for_deletion(account_id=fake_id)

    def test_anonymize_account_with_multiple_quotes(self, account, user, client_obj):
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
        anonymize_account_for_deletion(account_id=str(account.id))

        # Verify both quotes preserved
        quote1.refresh_from_db()
        quote2.refresh_from_db()

        assert Quote.objects.filter(account=account).count() == 2
        assert quote1.reference == "Q-2025-001"
        assert quote2.reference == "Q-2025-002"
