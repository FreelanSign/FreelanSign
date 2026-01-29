from datetime import date

import pytest
from django.template import TemplateDoesNotExist

from apps.email.adapters.rendering.django_quote_email_renderer import DjangoQuoteEmailRenderer
from apps.email.application.dto.prepared_email_data import PreparedEmailData


@pytest.fixture
def sample_data():
    return PreparedEmailData(
        client_name="Alice <script>alert('XSS')</script>",
        client_email="client@example.com",
        quote_reference="Q-123",
        quote_title="Site web vitrine",
        quote_date=date(2024, 1, 1),
        expiration_date=date(2024, 1, 31),
        locale="fr",
        sender_name="Test Company",
    )


def test_render_plain_text_contains_minimal_fields(sample_data):
    renderer = DjangoQuoteEmailRenderer()
    output = renderer.render_plain(sample_data)

    assert "Alice" in output
    assert "Q-123" in output
    assert "Site web vitrine" in output
    assert "01/01/2024" in output
    assert "31/01/2024" in output


def test_render_html_sanitizes_script_tag(sample_data):
    renderer = DjangoQuoteEmailRenderer()
    html = renderer.render_html(sample_data)

    # S'assurer que le contenu dangereux est échappé
    assert "&lt;script&gt;" in html
    assert "<script>" not in html
    assert "alert(" in html  # visible, mais safe car échappé


def test_render_plain_always_uses_french(sample_data):
    sample_data.locale = "zz"
    renderer = DjangoQuoteEmailRenderer()

    # Even with invalid locale, should use French
    output = renderer.render_plain(sample_data)
    assert "Bonjour" in output


def test_render_html_always_uses_french(sample_data):
    sample_data.locale = "zz"
    renderer = DjangoQuoteEmailRenderer()

    # Even with invalid locale, should use French
    html = renderer.render_html(sample_data)
    assert "Bonjour" in html


def test_render_plain_logs_and_raises_on_generic_error(monkeypatch, sample_data):
    renderer = DjangoQuoteEmailRenderer()

    def raise_runtime_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("apps.email.adapters.rendering.django_quote_email_renderer.render_to_string", raise_runtime_error)

    with pytest.raises(RuntimeError):
        renderer.render_plain(sample_data)


def test_render_html_logs_and_fallbacks_on_generic_error(monkeypatch, sample_data):
    renderer = DjangoQuoteEmailRenderer()

    def raise_runtime_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("apps.email.adapters.rendering.django_quote_email_renderer.render_to_string", raise_runtime_error)

    html = renderer.render_html(sample_data)
    assert html == "<p>Erreur de génération d'email.</p>"


def test_render_plain_forces_french_locale(sample_data):
    sample_data.locale = "en"
    renderer = DjangoQuoteEmailRenderer()
    output = renderer.render_plain(sample_data)

    # Even with "en" locale, should render French template
    assert "Bonjour" in output
    assert "Alice" in output
    assert "Q-123" in output


def test_render_html_forces_french_locale(sample_data):
    sample_data.locale = "en"
    renderer = DjangoQuoteEmailRenderer()
    html = renderer.render_html(sample_data)

    # Even with "en" locale, should render French template
    assert "Bonjour" in html
    assert "Alice" in html


def test_render_plain_includes_sender_name(sample_data):
    renderer = DjangoQuoteEmailRenderer()
    output = renderer.render_plain(sample_data)

    assert "Test Company" in output
    assert "Bien cordialement" in output


def test_render_html_includes_sender_name(sample_data):
    renderer = DjangoQuoteEmailRenderer()
    html = renderer.render_html(sample_data)

    assert "Test Company" in html
    assert "Bien cordialement" in html
