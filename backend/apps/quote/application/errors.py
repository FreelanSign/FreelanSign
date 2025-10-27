# apps/quote/application/errors.py
class QuotePreviewError(Exception):
    """Base pour toute erreur de preview devis."""


class QuotePreviewValidationError(QuotePreviewError):
    """Payload invalide (cohérence métier)."""


class QuotePreviewTemplateError(QuotePreviewError):
    """Template manquant/erroné."""


class QuotePreviewEngineError(QuotePreviewError):
    """Moteur PDF (WeasyPrint) indisponible/casse."""
