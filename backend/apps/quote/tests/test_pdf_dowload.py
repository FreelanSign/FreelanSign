import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_download_quote_pdf(authenticated_user, quote_factory):
    quote = quote_factory()
    client = APIClient()
    client.force_authenticate(user=authenticated_user)

    # Avec le namespace "quote" et l'action "download-pdf"
    url = reverse("quote:quote-download-pdf", kwargs={"pk": quote.pk})

    res = client.get(url)
    assert res.status_code == 200
    assert res["Content-Type"].startswith("application/pdf")
    assert "Content-Disposition" in res
    assert res.content[:4] == b"%PDF"  # signature PDF
