from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrestationDTO:
    """Data Transfer Object for a Prestation."""

    id: str
    name: str
    area_name: str | None
    default_rate_cents: int
    weight_days: int
    status: str | None


class PrestationRepository:
    """Access to prestations (persistence). The concrete implementations (Django ORM) live in adapters/persistence.
    The DTO/structures returned can be simple objects (e.g. dicts / dataclasses) according to your choice.
    """

    def get(self, prestation_id: str) -> PrestationDTO: ...
