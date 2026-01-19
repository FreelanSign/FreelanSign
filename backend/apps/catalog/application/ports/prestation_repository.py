# apps/catalog/application/ports/prestation_repository.py
"""
Port du repository de prestations.
Interface abstraite utilisée par les use cases.
"""

from abc import ABC, abstractmethod
from typing import Optional

from apps.catalog.application.dto.prestation_inputs import ListPrestationsInput


class PrestationRepository(ABC):
    """
    Port pour l'accès aux prestations.
    Les use cases dépendent de cette interface, pas de l'implémentation Django.
    """

    @abstractmethod
    def get_by_id(self, prestation_id: int):
        """
        Récupère une prestation par son ID.

        Returns:
            Modèle Prestation ou None

        Raises:
            RepositoryError en cas d'erreur technique
        """
        pass

    @abstractmethod
    def list_prestations(self, filters: ListPrestationsInput):
        """
        Liste les prestations selon des filtres.

        Returns:
            QuerySet de Prestation

        Raises:
            RepositoryError en cas d'erreur technique
        """
        pass

    @abstractmethod
    def exists_by_name_and_area(self, name: str, area_id: int, professional_user_id: Optional[int] = None) -> bool:
        """
        Vérifie si une prestation existe déjà.

        Args:
            name: Nom de la prestation
            area_id: ID de l'area
            professional_user_id: ID du professionnel (None = globale)

        Returns:
            True si existe déjà
        """
        pass

    @abstractmethod
    def create(self, prestation_data: dict):
        """
        Crée une nouvelle prestation.

        Args:
            prestation_data: Données de la prestation

        Returns:
            Instance Prestation créée

        Raises:
            RepositoryError en cas d'erreur
        """
        pass

    @abstractmethod
    def update(self, prestation_id: int, update_data: dict):
        """
        Met à jour une prestation.

        Args:
            prestation_id: ID de la prestation
            update_data: Données à mettre à jour

        Returns:
            Instance Prestation mise à jour

        Raises:
            RepositoryError en cas d'erreur
        """
        pass


class AreaRepository(ABC):
    """Port pour l'accès aux areas."""

    @abstractmethod
    def get_by_id(self, area_id: int):
        """Récupère une area par son ID."""
        pass

    @abstractmethod
    def list_areas(self, search: Optional[str] = None):
        """Liste les areas."""
        pass

    @abstractmethod
    def exists(self, area_id: int) -> bool:
        """Vérifie si une area existe."""
        pass
