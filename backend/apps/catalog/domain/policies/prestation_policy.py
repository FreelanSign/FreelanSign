# apps/catalog/domain/policies/prestation_policy.py
"""
Politiques métier pour les prestations.
Règles pures, sans dépendance Django.
"""

from typing import Optional

from apps.catalog.domain.errors import (
    InvalidPrestationNameError,
    InvalidRateError,
    InvalidStatusTransitionError,
    InvalidWeightDaysError,
)


class PrestationStatus:
    """Statuts possibles pour une prestation (miroir du modèle, mais pur)."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

    ALL_STATUSES = [DRAFT, ACTIVE, ARCHIVED]


class PrestationPolicy:
    """
    Politique de validation des prestations.
    Contient les règles métier pures.
    """

    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 120
    MIN_WEIGHT_DAYS = 1
    MIN_RATE_CENTS = 0

    # Transitions de statut autorisées
    ALLOWED_TRANSITIONS = {
        PrestationStatus.DRAFT: [PrestationStatus.ACTIVE, PrestationStatus.ARCHIVED],
        PrestationStatus.ACTIVE: [PrestationStatus.ARCHIVED],
        PrestationStatus.ARCHIVED: [PrestationStatus.ACTIVE],  # réactivation possible
    }

    @classmethod
    def validate_name(cls, name: str) -> None:
        """Valide le nom d'une prestation."""
        if not name or not name.strip():
            raise InvalidPrestationNameError(name)

        if len(name.strip()) < cls.MIN_NAME_LENGTH:
            raise InvalidPrestationNameError(f"{name} (minimum {cls.MIN_NAME_LENGTH} caractères)")

        if len(name) > cls.MAX_NAME_LENGTH:
            raise InvalidPrestationNameError(f"{name} (maximum {cls.MAX_NAME_LENGTH} caractères)")

    @classmethod
    def validate_weight_days(cls, weight_days: int) -> None:
        """Valide les jours-homme."""
        if weight_days < cls.MIN_WEIGHT_DAYS:
            raise InvalidWeightDaysError(weight_days)

    @classmethod
    def validate_rate_cents(cls, rate_cents: int) -> None:
        """Valide le tarif en centimes."""
        if rate_cents < cls.MIN_RATE_CENTS:
            raise InvalidRateError(rate_cents)

    @classmethod
    def validate_status(cls, status: str) -> None:
        """Valide qu'un statut est autorisé."""
        if status not in PrestationStatus.ALL_STATUSES:
            raise InvalidStatusTransitionError("UNKNOWN", status)

    @classmethod
    def can_transition_to(cls, current_status: str, new_status: str) -> bool:
        """Vérifie si une transition de statut est autorisée."""
        if current_status == new_status:
            return True

        allowed = cls.ALLOWED_TRANSITIONS.get(current_status, [])
        return new_status in allowed

    @classmethod
    def validate_status_transition(cls, current_status: str, new_status: str) -> None:
        """
        Valide une transition de statut.
        Lève InvalidStatusTransitionError si invalide.
        """
        if not cls.can_transition_to(current_status, new_status):
            raise InvalidStatusTransitionError(current_status, new_status)

    @classmethod
    def validate_prestation_data(cls, name: str, weight_days: int, rate_cents: int, status: Optional[str] = None) -> None:
        """
        Valide toutes les données d'une prestation.
        Lève une exception en cas d'erreur.
        """
        cls.validate_name(name)
        cls.validate_weight_days(weight_days)
        cls.validate_rate_cents(rate_cents)

        if status is not None:
            cls.validate_status(status)
