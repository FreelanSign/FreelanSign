# apps/quote/tests/test_add_prestation_line_api.py
from decimal import Decimal

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_add_prestation_line(api_client, django_user_model, mock_pdf_and_email):
    # setup user + quote + prestation
    user = django_user_model.objects.create_user(email="u@a.test", password="p")
    api_client.force_authenticate(user)
    from apps.catalog.models import Area, Prestation  # adapte si besoin
    from apps.client.models import Client
    from apps.quote.models import Quote

    area = Area.objects.create(name="SEO")
    cli = Client.objects.create(owner=user, name="ACME")
    q = Quote.objects.create(
        owner=user,
        client=cli,
        title="T",
        reference="REF-ADD",
        currency="EUR",
        language="fr",
        status=Quote.Status.DRAFT,
        issue_date="2025-01-01",
        subtotal=Decimal("0"),
        tax_total=Decimal("0"),
        discount_total=Decimal("0"),
        total=Decimal("0"),
    )
    p = Prestation.objects.create(area=area, name="Audit", default_rate_cents=15000, weight_days=1, status="active")

    url = reverse("quote:quote-add-prestation-line", kwargs={"pk": q.pk})
    resp = api_client.post(url, {"prestation_id": str(p.pk)}, format="json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["subtotal"] == "150.00"
