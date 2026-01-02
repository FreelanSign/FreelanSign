# apps/branding/application/dto/theme_inputs.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class CreateThemeDTO:
    """DTO for creating a new theme."""

    account_id: int | str
    name: str
    is_active: bool
    colors: dict
    typography: dict
    spacing: dict
    logo_file: Any | None = None  # Django uploaded file or path


@dataclass(frozen=True)
class UpdateThemeDTO:
    """DTO for updating an existing theme."""

    theme_id: UUID | str  # Changed from int | str to UUID | str
    account_id: int | str
    name: str | None = None
    is_active: bool | None = None
    colors: dict | None = None
    typography: dict | None = None
    spacing: dict | None = None
    logo_file: Any | None = None  # Django uploaded file or path


@dataclass(frozen=True)
class GetThemeDTO:
    """DTO for retrieving a theme."""

    theme_id: UUID | str  # Changed from UUID to UUID | str for consistency
    account_id: int | str


@dataclass(frozen=True)
class DeleteThemeDTO:
    """DTO for deleting a theme."""

    theme_id: UUID | str  # Changed from int | str to UUID | str
    account_id: int | str


@dataclass(frozen=True)
class ListThemesDTO:
    """DTO for listing themes."""

    account_id: int | str


@dataclass(frozen=True)
class ActivateThemeDTO:
    """DTO for activating a theme."""

    theme_id: UUID | str  # Changed from int | str to UUID | str
    account_id: int | str


@dataclass(frozen=True)
class DeactivateThemeDTO:
    """DTO for deactivating a theme."""

    theme_id: UUID | str  # Changed from int | str to UUID | str
    account_id: int | str
