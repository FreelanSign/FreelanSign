import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_download_quote_pdf(authenticated_user, quote_factory):
    quote = quote_factory()  # adapte à tes fixtures
    client = APIClient()
    client.force_authenticate(user=authenticated_user)
    url = reverse("quote-download-pdf", kwargs={"pk": quote.pk})  # si basename/action diffèrent, ajuste
    # Avec DRF router + action(detail=True, url_path="pdf") => name = "<basename>-download-pdf" si tu l’as nommé
    # Sinon fais client.get(f"/api/quotes/{quote.pk}/pdf/")

    res = client.get(f"/api/quotes/{quote.pk}/pdf/")
    assert res.status_code == 200
    assert res["Content-Type"].startswith("application/pdf")
    assert "Content-Disposition" in res
    assert res.content[:4] == b"%PDF"  # signature PDF
