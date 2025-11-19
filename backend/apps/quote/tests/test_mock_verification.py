# apps/quote/tests/test_mock_verification.py
import pytest


@pytest.mark.django_db
def test_pdf_generator_is_mocked(mock_pdf_and_email):
    """Vérifie que le mock fonctionne via les factory methods."""
    from apps.quote.interface.views import QuoteViewSet

    viewset = QuoteViewSet()
    pdf_generator = viewset._pdf()

    result = pdf_generator.generate("<html>test</html>")

    assert result == b"%PDF-1.4\n%mock content"
    assert pdf_generator.generate.called
    print("✅ Mock fonctionne via factory method!")
