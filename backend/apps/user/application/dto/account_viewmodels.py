# apps/user/application/dto/account_viewmodels.py
"""
Output DTOs (ViewModels) pour la présentation des données Account.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AccountViewModel:
    """ViewModel pour un compte professionnel."""

    id: int
    user_id: int
    display_name: str
    legal_form: str  # String representation (ex: "micro", "eurl")
    legal_id: str | None
    domain_id: int | None
    default_rate_cents: int | None
    professional_headline: str | None
    service_type_ids: list[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AccountListViewModel:
    """ViewModel pour une liste de comptes."""

    accounts: list[AccountViewModel]
    total: int
