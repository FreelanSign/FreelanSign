# apps/client/application/dto/client_viewmodels.py
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class ClientViewModel:
    id: UUID
    owner_id: int
    name: str
    email: str | None
    phone: str | None
    address: str | None
    vat_number: str | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ClientListViewModel:
    items: list[ClientViewModel]
    total_count: int
