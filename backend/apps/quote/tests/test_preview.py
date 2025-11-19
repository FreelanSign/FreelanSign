# apps/quote/tests/test_preview.py
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_preview_pdf_ok(api_client, django_user_model, mock_pdf_and_email):
    user = django_user_model.objects.create_user(email="u@a.test", password="p")
    api_client.force_authenticate(user)

    payload = {
        "seller": {"name": "Seller SAS"},
        "client": {"name": "Client", "country": "ES"},
        "meta": {"ref": "Q-001"},
        "lines": [
            {"designation": "L1", "quantity": 1, "unit_price": 100, "tax_rate": 0.2},
        ],
        "branding": {},
    }

    url = reverse("quote:quote-preview-pdf")
    resp = api_client.post(url, payload, format="json")

    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"
    assert b"%PDF" in resp.content
