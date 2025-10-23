# apps/quote/tests/test_quote_actions_api.py
import pytest
from django.urls import reverse
from decimal import Decimal

@pytest.mark.django_db
def test_duplicate_quote(api_client, django_user_model, mock_pdf_and_email):
    user = django_user_model.objects.create_user(email="u@a.test", password="p")
    api_client.force_authenticate(user)
    from apps.client.models import Client as ClientModel
    from apps.quote.models import Quote, QuoteLineItem

    cli = ClientModel.objects.create(owner=user, name="ACME")
    q = Quote.objects.create(
        owner=user, client=cli, title="Original", reference="REF-1",
        currency="EUR", language="fr", status=Quote.Status.DRAFT, issue_date="2025-01-01",
        subtotal=Decimal("0.00"), tax_total=Decimal("0.00"), discount_total=Decimal("0.00"), total=Decimal("0.00"),
    )
    QuoteLineItem.objects.create(quote=q, description="L1", qty=Decimal("1"), unit_price=Decimal("100"), tax_rate=Decimal("20"))

    url = reverse("quote:quote-duplicate", kwargs={"pk": q.pk})
    resp = api_client.post(url)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["id"] != str(q.pk)
    assert data["status"] == "DRAFT"
    assert "items" in data and len(data["items"]) == 1

@pytest.mark.django_db
def test_change_status_illegal_transition(api_client, django_user_model, mock_pdf_and_email):
    user = django_user_model.objects.create_user(email="u@a.test", password="p")
    api_client.force_authenticate(user)
    from apps.client.models import Client as ClientModel
    from apps.quote.models import Quote

    cli = ClientModel.objects.create(owner=user, name="ACME")
    q = Quote.objects.create(
        owner=user, client=cli, title="T", reference="REF-2",
        currency="EUR", language="fr", status=Quote.Status.DRAFT, issue_date="2025-01-01",
        subtotal=Decimal("0.00"), tax_total=Decimal("0.00"), discount_total=Decimal("0.00"), total=Decimal("0.00"),
    )

    url = reverse("quote:quote-change-status", kwargs={"pk": q.pk})
    resp = api_client.post(url, {"status": "PAID"}, format="json")  # DRAFT -> PAID: interdit par la policy
    assert resp.status_code == 400
    assert "Transition" in resp.json().get("detail", "")

@pytest.mark.django_db
def test_send_quote_ok(api_client, django_user_model, mock_pdf_and_email):
    user = django_user_model.objects.create_user(email="u@a.test", password="p")
    api_client.force_authenticate(user)
    from apps.client.models import Client as ClientModel
    from apps.quote.models import Quote, QuoteLineItem

    cli = ClientModel.objects.create(owner=user, name="ACME", email="client@a.test")
    q = Quote.objects.create(
        owner=user, client=cli, title="T", reference="REF-3",
        currency="EUR", language="fr", status=Quote.Status.DRAFT, issue_date="2025-01-01",
        subtotal=Decimal("0.00"), tax_total=Decimal("0.00"), discount_total=Decimal("0.00"), total=Decimal("0.00"),
    )
    QuoteLineItem.objects.create(quote=q, description="L1", qty=Decimal("1"), unit_price=Decimal("100"), tax_rate=Decimal("20"))

    url = reverse("quote:quote-send", kwargs={"pk": q.pk})
    resp = api_client.post(url)
    assert resp.status_code == 200
    assert resp.json()["status"] == "SENT"
