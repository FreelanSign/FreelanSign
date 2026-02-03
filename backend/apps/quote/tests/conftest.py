# apps/quote/tests/conftest.py
from unittest.mock import MagicMock, patch

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def mock_pdf_and_email():
    from unittest.mock import MagicMock, patch

    mock_pdf = MagicMock()
    mock_pdf.generate.return_value = b"%PDF-1.4\n%mock content"
    mock_email = MagicMock()
    mock_email.send_quote.return_value = None
    mock_renderer = MagicMock()
    mock_renderer.render.return_value = "<html><body>OK</body></html>"

    with (
        patch("apps.quote.interface.views.PlaywrightPdfGenerator", return_value=mock_pdf),
        patch("apps.quote.interface.views.QuoteViewSet._mailer", return_value=mock_email),
        patch("apps.quote.interface.views.QuoteViewSet._renderer", return_value=mock_renderer),
        patch("apps.quote.interface.views.PlaywrightPdfGenerator", return_value=mock_pdf),
        patch("apps.quote.interface.views.DjangoTemplateRenderer", return_value=mock_renderer),
    ):
        yield {"pdf": mock_pdf, "email": mock_email, "renderer": mock_renderer}


@pytest.fixture
def user_with_account(db, django_user_model):
    from apps.user.models import Account, Profile

    user = django_user_model.objects.create_user(email="test@example.com", password="password")
    # Create profile with phone (required for legal terms)
    Profile.objects.update_or_create(
        user=user,
        defaults={
            "first_name": "Test",
            "last_name": "User",
            "phone": "+33612345678",
        },
    )
    # Create account with legal_id (required for legal terms)
    account = Account.objects.create(
        user=user,
        display_name="Test Account",
        is_active=True,
        legal_id="12345678901234",  # 14 digits SIRET
    )
    return user, account
