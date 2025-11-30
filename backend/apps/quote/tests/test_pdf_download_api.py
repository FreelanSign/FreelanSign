# apps/quote/tests/test_download_pdf_api.py
from decimal import Decimal

import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.django_db
def test_download_pdf_ok(api_client, user_with_account, mock_pdf_and_email):
    # Setup rapide : user + client + quote + line item
    user, account = user_with_account
    api_client.force_login(user)

    from apps.client.models import Client as ClientModel
    from apps.quote.models import Quote, QuoteLineItem

    cli = ClientModel.objects.create(owner=user, name="ACME", email="a@a.test", account=account)
    q = Quote.objects.create(
        owner=user,
        account=account,
        client=cli,
        title="T",
        reference="REF-TEST",
        currency="EUR",
        language="fr",
        status=Quote.Status.DRAFT,
        issue_date="2025-01-01",
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )
    QuoteLineItem.objects.create(
        quote=q,
        description="L1",
        qty=Decimal("1.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        discount=Decimal("0.00"),
        order=0,
    )
    q.recalculate_totals(save=True)

    url = reverse("quote:quote-download-pdf", kwargs={"pk": q.pk})  # nom configuré dans ta view
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")
