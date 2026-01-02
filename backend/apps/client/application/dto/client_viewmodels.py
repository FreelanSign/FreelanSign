# apps/client/application/dto/client_viewmodels.py
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class ClientViewModel:
    id: UUID
    owner_id: int
    account_id: int  # Phase 5
    name: str
    email: str | None
    phone: str | None
    address: str | None  # LEGACY - will be removed after migration
    # Structured address fields
    address_line1: str | None
    address_line2: str | None
    city: str | None
    postal_code: str | None
    country: str | None
    company: str | None
    vat_number: str | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ClientListViewModel:
    items: list[ClientViewModel]
    total_count: int
