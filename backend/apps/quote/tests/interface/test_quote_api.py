from decimal import Decimal

import pytest
from django.urls import reverse

from apps.quote.models import Quote


@pytest.mark.django_db
class TestQuoteUpdatePermissions:
    """
    Tests for Quote update permissions.
    Ensures that only DRAFT quotes can be edited.
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

    def test_update_draft_quote_succeeds(self, api_client, user_with_account):
        user, account = user_with_account
        api_client.force_login(user)
        quote = self._create_quote(user, account, status=Quote.Status.DRAFT)

        url = reverse("quote:quote-detail", kwargs={"pk": quote.pk})
        payload = {"title": "Updated Title"}

        resp = api_client.patch(url, payload, format="json")

        assert resp.status_code == 200
        quote.refresh_from_db()
        assert quote.title == "Updated Title"

    @pytest.mark.parametrize(
        "status",
        [
            Quote.Status.SENT,
            Quote.Status.ACCEPTED,
            Quote.Status.PAID,
            Quote.Status.REJECTED,
            Quote.Status.CANCELLED,
            Quote.Status.EXPIRED,
        ],
    )
    def test_update_non_draft_quote_fails(self, api_client, user_with_account, status):
        user, account = user_with_account
        api_client.force_login(user)
        quote = self._create_quote(user, account, status=status)

        url = reverse("quote:quote-detail", kwargs={"pk": quote.pk})
        payload = {"title": "Modified Title"}

        resp = api_client.patch(url, payload, format="json")

        assert resp.status_code == 400
        assert "status" in resp.json()
        assert "Only DRAFT quotes can be edited" in resp.json()["status"]

        # Verify title didn't change
        quote.refresh_from_db()
        assert quote.title == "Test Quote"

    def test_put_update_non_draft_quote_fails(self, api_client, user_with_account):
        """Test with PUT as well."""
        user, account = user_with_account
        api_client.force_login(user)
        quote = self._create_quote(user, account, status=Quote.Status.SENT)

        url = reverse("quote:quote-detail", kwargs={"pk": quote.pk})
        # Full payload for PUT (minimal example)
        payload = {
            "title": "Modified Title",
            "client": str(quote.client.pk),
            "currency": "EUR",
            "language": "fr",
            "issue_date": "2025-01-01",
            "items": [
                {
                    "description": "L1",
                    "qty": "1.00",
                    "unit_price": "100.00",
                    "tax_rate": "20.00",
                    "discount": "0.00",
                }
            ],
        }

        resp = api_client.put(url, payload, format="json")

        assert resp.status_code == 400
        assert "status" in resp.json()

        quote.refresh_from_db()
        assert quote.title == "Test Quote"

    def test_create_quote_with_long_description(self, api_client, user_with_account):
        """Verify API accepts line item descriptions longer than 255 characters."""
        from unittest.mock import MagicMock, patch

        user, account = user_with_account
        api_client.force_login(user)

        from apps.client.models import Client

        client = Client.objects.create(owner=user, name="Test Client Long", account=account)

        long_description = "A" * 500  # 500 characters
        url = reverse("quote:quote-list")
        payload = {
            "title": "Quote with Long Description",
            "client": str(client.pk),
            "currency": "EUR",
            "language": "fr",
            "issue_date": "2025-01-01",
            "items": [
                {
                    "description": long_description,
                    "qty": "1.00",
                    "unit_price": "100.00",
                    "tax_rate": "20.00",
                    "discount": "0.00",
                }
            ],
        }

        # Mock legal terms attachment to avoid SIRET/phone requirements
        mock_attach = MagicMock()
        mock_attach.execute.return_value = MagicMock(success=True, terms_id=None)
        with patch(
            "apps.quote.interface.serializers.AttachTermsToQuoteUseCase",
            return_value=mock_attach,
        ):
            resp = api_client.post(url, payload, format="json")

        assert resp.status_code == 201
        quote = Quote.objects.get(pk=resp.json()["id"])
        line = quote.items.first()
        assert len(line.description) == 500
        assert line.description == long_description
