import logging
from uuid import UUID

from django.core.exceptions import PermissionDenied
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.email import get_prepare_quote_email_uc
from apps.email.application.usecases.prepare_quote_email import PrepareQuoteEmailCommand
from apps.quote.application.errors import QuoteNotFoundError

logger = logging.getLogger(__name__)


def parse_locale(accept_language: str | None) -> str:
    """Extract primary locale from Accept-Language header."""
    if not accept_language:
        return "fr"
    # Prend le premier code langue (avant virgule et paramètres q=)
    primary = accept_language.split(",")[0].split(";")[0].strip()
    # Normalise fr-FR → fr
    return primary.split("-")[0].lower()


@extend_schema(
    responses={
        200: OpenApiResponse(
            description="Contenu structuré de l’email prêt à être affiché ou envoyé.",
            response={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "format": "email"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "template_version": {"type": "string"},
                },
                "required": ["to", "subject", "body", "template_version"],
            },
            examples=[
                OpenApiExample(
                    name="Exemple de réponse",
                    value={
                        "to": "client@example.com",
                        "subject": "Votre devis Q-123",
                        "body": "Bonjour Alice...",
                        "template_version": "v1.0",
                    },
                )
            ],
        ),
        403: OpenApiResponse(description="Forbidden"),
        404: OpenApiResponse(description="Quote not found"),
        500: OpenApiResponse(description="Internal server error"),
    },
    description="Retourne le contenu structuré d’un email prêt à être envoyé pour un devis donné.",
    tags=["Quote"],
    summary="Préparer un email pour un devis",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def prepared_email_view(request, quote_id: UUID):
    """
    REST endpoint to get the prepared email content for a quote.

    Responsibilities:
    - Ensure user is authenticated and owns the quote.
    - Delegate to the PrepareQuoteEmail use case.
    - Return structured email content or appropriate HTTP errors.

    Rationale:
    - Thin controller: no business logic.
    - UC wired via factory (Clean Arch).
    - Logs contextualized, no sensitive data exposed.
    """

    uc = get_prepare_quote_email_uc()
    locale = parse_locale(request.headers.get("Accept-Language"))

    try:
        command = PrepareQuoteEmailCommand(
            quote_id=quote_id,
            requester=request.user,
            locale=locale,
        )
        result = uc.execute(command)

        return Response(
            {
                "to": result.to,
                "subject": result.subject,
                "body": result.body_plain,
                "template_version": result.template_version,
            }
        )

    except PermissionDenied:
        logger.warning(
            "403 forbidden on prepared_email_view",
            extra={
                "quote_id": str(quote_id),
                "user_id": str(request.user.id),
            },
        )
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    except QuoteNotFoundError:
        logger.warning(
            "404 not found on prepared_email_view",
            extra={
                "quote_id": str(quote_id),
                "user_id": str(request.user.id),
            },
        )
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(
            "Unexpected error in prepared_email_view",
            exc_info=e,
            extra={"quote_id": str(quote_id), "user_id": str(request.user.id)},
        )
        return Response({"detail": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
