import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.quote.domain.errors import QuotePreviewEngineError
from apps.quote.services.pdf_preview import QuotePreviewContext


def auth_client(db):
    User = get_user_model()
    user = User.objects.create_user(email="john@example.com", password="password123")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_422_validation_when_no_lines(db):
    client = auth_client(db)
    payload = {
        "seller": {"name": "Test Seller"},
        "client": {"name": "Test Client"},
        "meta": {"title": "Test Title"},
        "lines": [],
        "totals": {"subtotal": 0, "tax": 0, "grand_total": 0},
    }
    response = client.post(reverse("quote:quote_preview_pdf"), payload, format="json")
    assert response.status_code == 422
    assert response.json()["code"] == "QUOTE_PREVIEW_VALIDATION"
    assert response.json()["detail"] == "Au moins une ligne est requise"


@patch("apps.quote.services.pdf_preview.html_to_pdf_bytes", side_effect=QuotePreviewEngineError("Test engine error"))
def test_503_engine_error(_, db):
    client = auth_client(db)
    payload = {
        "seller": {},
        "client": {},
        "meta": {},
        "lines": [{"designation": "A", "description": None, "quantity": 1, "unit_price": 10, "tax_rate": 0.2}],
        "branding": {},
    }
    response = client.post(reverse("quote:quote_preview_pdf"), payload, format="json")
    assert response.status_code == 503
    assert response.json()["code"] == "QUOTE_PREVIEW_ENGINE"
    assert response.json()["detail"] == "Test engine error"
