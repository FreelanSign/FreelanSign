# config/api_errors.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.quote.application.errors import (
    QuotePreviewEngineError,
    QuotePreviewError,
    QuotePreviewTemplateError,
    QuotePreviewValidationError,
)


def custom_exception_handler(exc, context):
    # Laisse DRF gérer d'abord (ValidationError, Auth, etc.)
    resp = exception_handler(exc, context)
    if resp is not None:
        return resp

    # Mapping domaine
    if isinstance(exc, QuotePreviewValidationError):
        return Response({"code": "QUOTE_PREVIEW_VALIDATION", "detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if isinstance(exc, QuotePreviewTemplateError):
        return Response({"code": "QUOTE_PREVIEW_TEMPLATE", "detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if isinstance(exc, QuotePreviewEngineError):
        return Response({"code": "QUOTE_PREVIEW_ENGINE", "detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if isinstance(exc, QuotePreviewError):
        return Response({"code": "QUOTE_PREVIEW_GENERIC", "detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Fallback générique
    return Response({"code": "UNEXPECTED_ERROR", "detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
