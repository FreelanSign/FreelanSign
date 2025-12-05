"""
DTOs for legal profile management.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ClauseOverrideDTO:
    """Represents an override for a specific clause."""

    is_active: bool | None = None
    custom_title: str | None = None
    custom_body: str | None = None
    custom_order: int | None = None


@dataclass(frozen=True)
class LegalProfileDTO:
    """DTO for legal profile with template and overrides."""

    id: str
    account_id: str
    template_id: str
    template_version: str
    clause_overrides: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class UpdateClauseInput:
    """Input DTO for updating a clause override."""

    identifier: str
    is_active: bool | None = None
    custom_title: str | None = None
    custom_body: str | None = None
    custom_order: int | None = None
