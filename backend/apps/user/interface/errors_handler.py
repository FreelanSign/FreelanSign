# apps/user/interface/error_handler.py
"""
Gestion centralisée des erreurs pour l'interface API user.
Mappe les erreurs métier vers des codes HTTP appropriés.
"""

import logging

from rest_framework import status
from rest_framework.response import Response

from apps.user.application.errors import (
    AuthenticationFailedError,
    DuplicateEmailError,
    IncorrectPasswordError,
    ProfessionalNotFoundError,
    ProfileNotFoundError,
    RepositoryError,
    UnauthorizedOperationError,
    UserApplicationError,
    UserNotFoundError,
)
from apps.user.domain.errors import (
    DuplicateProfessionalError,
    InvalidEmailError,
    InvalidNameError,
    InvalidPasswordError,
    InvalidPhoneError,
    InvalidRoleError,
    InvalidStatusJuridiqueError,
    InvalidTJMError,
    UnauthorizedRoleAssignmentError,
    UserDomainError,
)

logger = logging.getLogger(__name__)


class UserErrorHandler:
    """
    Gestionnaire d'erreurs pour l'API user.
    Convertit les exceptions métier en réponses HTTP appropriées.
    """

    @staticmethod
    def handle_error(error: Exception) -> Response:
        """
        Gère une erreur et retourne une Response DRF appropriée.

        Args:
            error: Exception levée

        Returns:
            Response avec le code HTTP et le message appropriés
        """
        # Erreurs de validation métier (422 Unprocessable Entity)
        if isinstance(
            error,
            (
                InvalidEmailError,
                InvalidNameError,
                InvalidPasswordError,
                InvalidPhoneError,
                InvalidRoleError,
                InvalidStatusJuridiqueError,
                InvalidTJMError,
            ),
        ):
            logger.warning("Erreur de validation métier: %s", str(error))
            return Response(
                {"error": error.code, "message": error.message, "detail": str(error)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # Ressources introuvables (404)
        if isinstance(error, (UserNotFoundError, ProfileNotFoundError, ProfessionalNotFoundError)):
            logger.info("Ressource introuvable: %s", str(error))
            return Response(
                {"error": error.code, "message": error.message, "detail": str(error)}, status=status.HTTP_404_NOT_FOUND
            )

        # Erreurs de repository/infrastructure (503 Service Unavailable)
        if isinstance(error, RepositoryError):
            logger.error(
                "Erreur de repository: %s (original: %s)",
                str(error),
                str(error.original_error) if hasattr(error, "original_error") else "N/A",
            )
            return Response(
                {
                    "error": error.code,
                    "message": "Une erreur technique est survenue",
                    "detail": "Le service est temporairement indisponible",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Autres erreurs domaine (400 Bad Request)
        if isinstance(error, UserDomainError):
            logger.warning("Erreur domaine: %s", str(error))
            return Response(
                {"error": error.code, "message": error.message, "detail": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        # Autres erreurs application (400)
        if isinstance(error, UserApplicationError):
            logger.warning("Erreur application: %s", str(error))
            return Response(
                {"error": error.code, "message": error.message, "detail": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        # Erreur inattendue (500)
        logger.exception("Erreur inattendue: %s", str(error))
        return Response(
            {
                "error": "INTERNAL_ERROR",
                "message": "Une erreur inattendue est survenue",
                "detail": "Veuillez réessayer ou contacter le support",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
