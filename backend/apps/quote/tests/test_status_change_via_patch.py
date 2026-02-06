from decimal import Decimal

import pytest
from django.urls import reverse

from apps.quote.models import Quote


@pytest.mark.django_db
class TestStatusChangeViaPatch:
    """
    Tests for changing quote status via PATCH endpoint.
    Ensures that status can be changed on SENT/ACCEPTED quotes,
    but other fields cannot.
    """

    def _create_quote(self, user, account, status=Quote.Status.DRAFT):
        from apps.client.models import Client

        cli = Client.objects.create(owner=user, name="Test Client", account=account)
        return Quote.objects.create(
            owner=user,
            account=account,
            client=cli,
            title="Test Quote",
            reference=f"REF-{status}",
            currency="EUR",
            language="fr",
            status=status,
            issue_date="2025-01-01",
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        )

    def test_patch_status_on_sent_quote_succeeds(self, api_client, user_with_account):
        """SENT → ACCEPTED should work via PATCH"""
        user, account = user_with_account
        api_client.force_login(user)
        quote = self._create_quote(user, account, status=Quote.Status.SENT)

        url = reverse("quote:quote-detail", kwargs={"pk": quote.pk})
        payload = {"status": Quote.Status.ACCEPTED}

        resp = api_client.patch(url, payload, format="json")

        assert resp.status_code == 200
        quote.refresh_from_db()
        assert quote.status == Quote.Status.ACCEPTED

    def test_patch_status_on_sent_quote_invalid_transition_fails(self, api_client, user_with_account):
        """SENT → DRAFT should fail (invalid transition)"""
        user, account = user_with_account
        api_client.force_login(user)
        quote = self._create_quote(user, account, status=Quote.Status.SENT)

        url = reverse("quote:quote-detail", kwargs={"pk": quote.pk})
        payload = {"status": Quote.Status.DRAFT}

        resp = api_client.patch(url, payload, format="json")

        assert resp.status_code == 400
        assert "Transition" in resp.json().get("status", "")
        quote.refresh_from_db()
        assert quote.status == Quote.Status.SENT  # unchanged

    def test_patch_status_sent_to_paid_succeeds(self, api_client, user_with_account):
        """SENT → PAID should work (new valid transition)"""
        user, account = user_with_account
        api_client.force_login(user)
        quote = self._create_quote(user, account, status=Quote.Status.SENT)

        url = reverse("quote:quote-detail", kwargs={"pk": quote.pk})
        payload = {"status": Quote.Status.PAID}

        resp = api_client.patch(url, payload, format="json")

        assert resp.status_code == 200
        quote.refresh_from_db()
        assert quote.status == Quote.Status.PAID

    def test_patch_title_on_sent_quote_fails(self, api_client, user_with_account):
        """Changing title on SENT quote should fail"""
        user, account = user_with_account
        api_client.force_login(user)
        quote = self._create_quote(user, account, status=Quote.Status.SENT)

        url = reverse("quote:quote-detail", kwargs={"pk": quote.pk})
        payload = {"title": "Modified Title"}

        resp = api_client.patch(url, payload, format="json")

        assert resp.status_code == 400
        assert "Cannot modify quotes" in resp.json().get("detail", "")
        quote.refresh_from_db()
        assert quote.title == "Test Quote"  # unchanged

    def test_patch_status_and_title_on_sent_quote_fails(self, api_client, user_with_account):
        """Changing both status and title on SENT quote should fail"""
        user, account = user_with_account
        api_client.force_login(user)
        quote = self._create_quote(user, account, status=Quote.Status.SENT)

        url = reverse("quote:quote-detail", kwargs={"pk": quote.pk})
        payload = {"status": Quote.Status.ACCEPTED, "title": "Modified Title"}

        resp = api_client.patch(url, payload, format="json")

        assert resp.status_code == 400
        assert "Cannot modify quotes" in resp.json().get("detail", "")
        quote.refresh_from_db()
        assert quote.status == Quote.Status.SENT  # unchanged
        assert quote.title == "Test Quote"  # unchanged
