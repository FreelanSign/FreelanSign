# apps/catalog/application/errors.py
"""
Erreurs de la couche application (use cases).
"""


class CatalogApplicationError(Exception):
    """Erreur de base pour les use cases catalog."""

    def __init__(self, message: str, code: str = "APPLICATION_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class PrestationNotFoundError(CatalogApplicationError):
    """Prestation introuvable."""

    def __init__(self, prestation_id: int):
        super().__init__(f"Prestation {prestation_id} introuvable", code="PRESTATION_NOT_FOUND")
        self.prestation_id = prestation_id


class AreaNotFoundError(CatalogApplicationError):
    """Area introuvable."""

    def __init__(self, area_id: int):
        super().__init__(f"Area {area_id} introuvable", code="AREA_NOT_FOUND")
        self.area_id = area_id


class RepositoryError(CatalogApplicationError):
    """Erreur générique du repository."""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message, code="REPOSITORY_ERROR")
        self.original_error = original_error
