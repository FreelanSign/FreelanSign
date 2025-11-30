from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateClientInput:
    owner_id: int
    account_id: int  # Phase 5
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    vat_number: Optional[str] = None
    metadata: dict | None = None


@dataclass(frozen=True)
class UpdateClientInput:
    client_id: str  # UUID string
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    vat_number: Optional[str] = None
    metadata: dict | None = None


@dataclass(frozen=True)
class GetClientInput:
    client_id: str


@dataclass(frozen=True)
class ListClientsInput:
    owner_id: Optional[int] = None
    account_id: Optional[int] = None  # Phase 5
    search: Optional[str] = None
    ordering: Optional[str] = "-created_at"


@dataclass(frozen=True)
class DeleteClientInput:
    client_id: str
