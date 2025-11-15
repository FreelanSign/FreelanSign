# apps/quote/application/errors.py
class QuotePreviewError(Exception):
    """Base pour toute erreur de preview devis."""


class QuotePreviewValidationError(QuotePreviewError):
    """Payload invalide (cohérence métier)."""


class QuotePreviewTemplateError(QuotePreviewError):
    """Template manquant/erroné."""


class QuotePreviewEngineError(QuotePreviewError):
    """Moteur PDF (WeasyPrint) indisponible/casse."""


class QuoteNotFoundError(Exception):
    """
    Raised when a quote cannot be found by ID.

    Rationale:
    - Application-layer concern: not tied to ORM or HTTP.
    - Enables clean separation of domain flow and infrastructure details.
    - Used in use cases to signal business-level absence (e.g. quote deleted).

    Handled by interface layer (e.g. API returns 404).
    """

    pass
