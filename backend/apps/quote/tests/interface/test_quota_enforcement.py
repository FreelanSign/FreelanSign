"""E2E tests for subscription quota enforcement on quote creation."""

from datetime import datetime
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.quote.models import Quote
from apps.user.models.account import Account


@pytest.fixture
def free_account(user_with_account):
    """Create account with free plan."""
    user, account = user_with_account
    account.plan = "free"
    account.save()
    return user, account


@pytest.fixture
def beta_account(user_with_account):
    """Create account with beta plan."""
    user, account = user_with_account
    account.plan = "beta"
    account.save()
    return user, account


@pytest.fixture
def client_for_account(user_with_account):
    """Create a client for the account."""
    from apps.client.models import Client

    user, account = user_with_account
    return Client.objects.create(
        owner=user,
        account=account,
        name="Test Client",
        email="test@example.com",
    )


@pytest.mark.django_db
class TestQuotaEnforcement:
    """Test subscription quota enforcement on quote creation via API."""

    def create_quote_payload(self, client_id):
        """Helper to create quote payload."""
        return {
            "client": client_id,
            "title": "Test Quote",
            "currency": "EUR",
            "language": "fr",
            "issue_date": "2026-01-31",
            "valid_until": "2026-02-28",
            "items": [
                {
                    "description": "Service 1",
                    "qty": "1.00",
                    "unit_price": "100.00",
                    "tax_rate": "20.00",
                    "discount": "0.00",
                    "order": 1,
                }
            ],
        }

    def test_beta_account_creates_unlimited_quotes(self, api_client, beta_account, client_for_account):
        """Beta account can create unlimited quotes."""
        user, account = beta_account
        api_client.force_login(user)

        # Create 10 quotes (no limit for beta)
        url = reverse("quote:quote-list")
        for i in range(10):
            payload = self.create_quote_payload(client_for_account.id)
            payload["title"] = f"Quote {i+1}"
            resp = api_client.post(url, payload, format="json", HTTP_X_ACCOUNT_ID=str(account.id))
            assert resp.status_code == 201, f"Failed to create quote {i+1}: {resp.json()}"

        # Verify 10 quotes were created
        assert Quote.objects.filter(account=account).count() == 10

    def test_free_account_allows_within_quota(self, api_client, free_account, client_for_account):
        """Free account can create quotes within quota (4/5)."""
        user, account = free_account
        api_client.force_login(user)

        # Create 4 quotes (within free plan limit of 5)
        url = reverse("quote:quote-list")
        for i in range(4):
            payload = self.create_quote_payload(client_for_account.id)
            payload["title"] = f"Quote {i+1}"
            resp = api_client.post(url, payload, format="json", HTTP_X_ACCOUNT_ID=str(account.id))
            assert resp.status_code == 201, f"Failed to create quote {i+1}: {resp.json()}"

        # Verify 4 quotes were created
        assert Quote.objects.filter(account=account).count() == 4

    def test_free_account_blocks_at_quota_limit(self, api_client, free_account, client_for_account):
        """Free account is blocked at quota limit (5/5)."""
        user, account = free_account
        api_client.force_login(user)

        # Create 5 quotes (fill quota)
        url = reverse("quote:quote-list")
        for i in range(5):
            payload = self.create_quote_payload(client_for_account.id)
            payload["title"] = f"Quote {i+1}"
            resp = api_client.post(url, payload, format="json", HTTP_X_ACCOUNT_ID=str(account.id))
            assert resp.status_code == 201

        # Try to create 6th quote (should fail)
        payload = self.create_quote_payload(client_for_account.id)
        payload["title"] = "Quote 6"
        resp = api_client.post(url, payload, format="json", HTTP_X_ACCOUNT_ID=str(account.id))

        # Verify quota error
        assert resp.status_code == 400
        assert "quota" in resp.json()
        assert "Monthly quota exceeded" in resp.json()["quota"]
        assert "5 quotes/month" in resp.json()["quota"]

        # Verify only 5 quotes exist
        assert Quote.objects.filter(account=account).count() == 5

    def test_free_account_blocks_over_quota(self, api_client, free_account, client_for_account):
        """Free account is blocked when over quota (6/5)."""
        user, account = free_account
        api_client.force_login(user)

        # Create 5 quotes
        url = reverse("quote:quote-list")
        for i in range(5):
            payload = self.create_quote_payload(client_for_account.id)
            payload["title"] = f"Quote {i+1}"
            api_client.post(url, payload, format="json", HTTP_X_ACCOUNT_ID=str(account.id))

        # Try to create multiple more (all should fail)
        for i in range(3):
            payload = self.create_quote_payload(client_for_account.id)
            payload["title"] = f"Quote {i+6}"
            resp = api_client.post(url, payload, format="json", HTTP_X_ACCOUNT_ID=str(account.id))
            assert resp.status_code == 400
            assert "quota" in resp.json()

    def test_quota_check_ignores_deleted_clients(self, api_client, free_account):
        """Quota check ignores soft-deleted clients."""
        from apps.client.models import Client

        user, account = free_account
        api_client.force_login(user)

        # Create 3 clients (at free plan limit)
        for i in range(3):
            Client.objects.create(
                owner=user,
                account=account,
                name=f"Client {i+1}",
                email=f"client{i+1}@example.com",
            )

        # Soft-delete 2 clients
        clients_to_delete = list(Client.objects.filter(account=account)[:2])
        for client in clients_to_delete:
            client.is_deleted = True
            client.save()

        # Now only 1 active client, should be able to create quote
        url = reverse("quote:quote-list")
        active_client = Client.objects.filter(account=account, is_deleted=False).first()
        payload = self.create_quote_payload(active_client.id)

        resp = api_client.post(url, payload, format="json", HTTP_X_ACCOUNT_ID=str(account.id))
        assert resp.status_code == 201

    def test_quota_error_message_includes_plan(self, api_client, free_account, client_for_account):
        """Quota error message includes plan name."""
        user, account = free_account
        api_client.force_login(user)

        # Fill quota
        url = reverse("quote:quote-list")
        for i in range(5):
            payload = self.create_quote_payload(client_for_account.id)
            api_client.post(url, payload, format="json", HTTP_X_ACCOUNT_ID=str(account.id))

        # Try to exceed
        payload = self.create_quote_payload(client_for_account.id)
        resp = api_client.post(url, payload, format="json", HTTP_X_ACCOUNT_ID=str(account.id))

        assert resp.status_code == 400
        error_msg = resp.json()["quota"]
        assert "free plan" in error_msg
