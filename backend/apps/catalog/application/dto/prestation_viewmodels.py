# apps/catalog/application/dto/prestation_viewmodels.py
"""
ViewModels de sortie pour les use cases.
Structures prêtes pour présentation.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class AreaViewModel:
    """Représentation d'une Area pour présentation."""

    id: int
    name: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class PrestationViewModel:
    """Représentation d'une Prestation pour présentation."""

    id: int
    area_id: int
    area_name: str
    name: str
    description: str
    weight_days: int
    default_rate_cents: int
    default_rate_display: str  # Format "1200.00"
    status: str
    custom: bool
    professional_user_id: Optional[int]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class PrestationListViewModel:
    """Liste de prestations avec métadonnées."""

    prestations: list[PrestationViewModel]
    total_count: int
