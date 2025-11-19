# apps/catalog/application/dto/prestation_inputs.py
"""
DTOs d'entrée pour les use cases de prestations.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ListPrestationsInput:
    """Paramètres pour lister les prestations."""

    area_id: Optional[int] = None
    status: Optional[str] = None
    search: Optional[str] = None
    professional_user_id: Optional[int] = None
    prestation_ids: Optional[list[int]] = None
    ordering: Optional[str] = None


@dataclass(frozen=True)
class GetPrestationInput:
    """Paramètres pour récupérer une prestation."""

    prestation_id: int


@dataclass(frozen=True)
class CreatePrestationInput:
    """Données pour créer une prestation."""

    area_id: int
    name: str
    description: str
    weight_days: int
    default_rate_cents: int
    status: str = "DRAFT"
    professional_user_id: Optional[int] = None


@dataclass(frozen=True)
class UpdatePrestationStatusInput:
    """Données pour changer le statut d'une prestation."""

    prestation_id: int
    new_status: str
