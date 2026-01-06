from datetime import date
from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.client.models import Client
from apps.quote.models import Quote
from apps.user.models.account import Account


@pytest.mark.django_db
class TestPreparedEmailView:
    def setup_method(self):
        self.client = APIClient()

    def given_authenticated_user_with_quote(self):
        from apps.user.models import User

        user = User.objects.create_user(email="bob@example.com", password="test")
        account = Account.objects.create(user=user, display_name="Bob Account", legal_form="micro", is_active=True)
        client = Client.objects.create(owner=user, account=account, name="Alice Dupont", email="client@example.com")
        quote = Quote.objects.create(
            owner=user,
            account=account,
            client=client,
            issue_date=date(2024, 1, 1),
            valid_until=date(2024, 1, 31),
            reference="Q-123",
            title="Site Web",
        )
        self.client.force_authenticate(user)
        return user, quote

    def test_get_prepared_email_200(self):
        _, quote = self.given_authenticated_user_with_quote()

        url = reverse("email:prepared-email", kwargs={"quote_id": str(quote.id)})
        resp = self.client.get(url, HTTP_ACCEPT_LANGUAGE="fr")

        assert resp.status_code == 200
        data = resp.json()
        assert set(["to", "subject", "body", "template_version"]).issubset(data.keys())
        assert "client@example.com" in data["to"]
        assert data["template_version"] == "v1.0"

    def test_get_prepared_email_403_if_not_owner(self):
        from apps.user.models import User

        owner = User.objects.create_user(email="alice@example.com", password="x")
        not_owner = User.objects.create_user(email="bob@example.com", password="x")

        account = Account.objects.create(user=owner, display_name="Alice Account", legal_form="micro", is_active=True)
        client_obj = Client.objects.create(owner=owner, account=account, name="X", email="client@example.com")
        quote = Quote.objects.create(
            owner=owner,
            account=account,
            client=client_obj,
            issue_date=date(2024, 1, 1),
            valid_until=date(2024, 1, 31),
            reference="Q-999",
            title="Hacking",
        )

        self.client.force_authenticate(not_owner)
        url = reverse("email:prepared-email", kwargs={"quote_id": str(quote.id)})
        resp = self.client.get(url)

        assert resp.status_code == 403

    def test_get_prepared_email_401_if_anonymous(self):
        quote_id = uuid4()
        url = reverse("email:prepared-email", kwargs={"quote_id": str(quote_id)})
        resp = APIClient().get(url)
        assert resp.status_code == 401

    def test_get_prepared_email_404_if_quote_missing(self):
        from apps.user.models import User

        user = User.objects.create_user(email="ghost@example.com", password="x")
        self.client.force_authenticate(user)
        fake_id = uuid4()
        url = reverse("email:prepared-email", kwargs={"quote_id": str(fake_id)})
        resp = self.client.get(url)
        assert resp.status_code == 404
