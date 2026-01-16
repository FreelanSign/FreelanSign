# apps/user/application/dto/account_inputs.py
"""
Input DTOs pour les use cases Account.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateAccountInput:
    """Input pour créer un nouveau compte professionnel."""

    user_id: int
    display_name: str
    legal_form: str | None = None  # Sera converti en LegalForm enum (default: micro)
    legal_id: str | None = None
    domain_id: int | None = None
    default_rate_cents: int | None = None
    professional_headline: str | None = None
    service_type_ids: list[int] | None = None


@dataclass(frozen=True)
class UpdateAccountInput:
    """Input pour mettre à jour un compte existant."""

    account_id: int
    display_name: str
    legal_form: str
    legal_id: str | None = None
    domain_id: int | None = None
    default_rate_cents: int | None = None
    professional_headline: str | None = None
    service_type_ids: list[int] | None = None
