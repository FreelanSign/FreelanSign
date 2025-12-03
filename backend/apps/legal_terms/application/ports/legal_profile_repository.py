"""
Port for legal profile repository.
"""

from typing import Protocol

from apps.legal_terms.domain.entities.legal_profile import LegalProfile


class LegalProfileRepository(Protocol):
    """Repository port for LegalProfile persistence."""

    def get_by_account(self, account_id: str) -> LegalProfile | None:
        """Get legal profile by account ID."""
        ...

    def save(self, profile: LegalProfile) -> LegalProfile:
        """Save or update legal profile."""
        ...

    def get_or_create_for_account(self, account_id: str, template_id: str, template_version: str) -> LegalProfile:
        """Get existing profile or create new one for account."""
        ...
