# apps/catalog/domain/errors.py
"""
Erreurs métier du domaine catalog.
Ces erreurs sont pures, sans dépendance à Django.
"""


class CatalogDomainError(Exception):
    """Erreur de base pour le domaine catalog."""

    def __init__(self, message: str, code: str = "CATALOG_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AreaPolicyError(CatalogDomainError):
    """Erreur de politique liée aux domaines d'activité."""

    def __init__(self, message: str):
        super().__init__(message, code="AREA_POLICY_ERROR")


class PrestationPolicyError(CatalogDomainError):
    """Erreur de politique liée aux prestations."""

    def __init__(self, message: str):
        super().__init__(message, code="PRESTATION_POLICY_ERROR")


class InvalidPrestationNameError(PrestationPolicyError):
    """Le nom de prestation est invalide."""

    def __init__(self, name: str):
        super().__init__(f"Nom de prestation invalide: '{name}'")


class InvalidWeightDaysError(PrestationPolicyError):
    """Les jours-homme sont invalides."""

    def __init__(self, weight_days: int):
        super().__init__(f"Jours-homme invalides: {weight_days} (doit être >= 1)")


class InvalidRateError(PrestationPolicyError):
    """Le tarif est invalide."""

    def __init__(self, rate_cents: int):
        super().__init__(f"Tarif invalide: {rate_cents} centimes (doit être >= 0)")


class DuplicatePrestationError(PrestationPolicyError):
    """Une prestation avec ce nom existe déjà."""

    def __init__(self, name: str, context: str = ""):
        msg = f"Une prestation nommée '{name}' existe déjà"
        if context:
            msg += f" ({context})"
        super().__init__(msg)


class InvalidStatusTransitionError(PrestationPolicyError):
    """Transition de statut invalide."""

    def __init__(self, from_status: str, to_status: str):
        super().__init__(f"Transition de statut invalide: {from_status} -> {to_status}")
