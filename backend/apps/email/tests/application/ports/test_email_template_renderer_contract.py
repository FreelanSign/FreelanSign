import pytest

from apps.email.application.dto.prepared_email_data import PreparedEmailData
from apps.email.application.ports.email_template_renderer import EmailTemplateRenderer


class DummyRenderer(EmailTemplateRenderer):
    def render_plain(self, data: PreparedEmailData) -> str:
        return super().render_plain(data)

    def render_html(self, data: PreparedEmailData) -> str:
        return super().render_html(data)


def test_email_template_renderer_methods_raise_not_implemented():
    renderer = DummyRenderer()
    data = PreparedEmailData(
        client_name="Alice Dupont",
        client_email="alice@example.com",
        quote_reference="Q-123",
        quote_title="Site Web",
        quote_date="2024-01-01",
        expiration_date="2024-01-31",
        locale="fr",
    )

    with pytest.raises(NotImplementedError):
        renderer.render_plain(data)

    with pytest.raises(NotImplementedError):
        renderer.render_html(data)
