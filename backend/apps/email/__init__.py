# backend/apps/email/__init__.py


def get_prepare_quote_email_uc():
    """
    Factory function to assemble the PrepareQuoteEmail use case.

    Rationale:
    - Ensures strict inversion of dependencies (Clean Architecture).
    - Hides infrastructure implementation from interface layer.
    - Enables test-time substitution (mocked dependencies).
    """
    from apps.email.adapters.rendering.django_quote_email_renderer import DjangoQuoteEmailRenderer
    from apps.email.application.ports.email_template_renderer import EmailTemplateRenderer
    from apps.email.application.usecases.prepare_quote_email import PrepareQuoteEmail
    from apps.quote.adapters.persistence.django_quote_repository import DjangoQuoteRepository
    from apps.quote.application.ports.quote_repository import QuoteRepository

    quote_repo: QuoteRepository = DjangoQuoteRepository()
    renderer: EmailTemplateRenderer = DjangoQuoteEmailRenderer()

    return PrepareQuoteEmail(quote_repo=quote_repo, renderer=renderer)
