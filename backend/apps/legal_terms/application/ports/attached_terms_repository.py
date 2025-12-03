"""
Port for attached terms repository.
"""

from typing import Protocol

from apps.legal_terms.domain.entities.attached_terms import AttachedTerms


class AttachedTermsRepository(Protocol):
    """Repository port for AttachedTerms persistence."""

    def save(self, attached_terms: AttachedTerms) -> AttachedTerms:
        """Save attached terms."""
        ...

    def get_by_quote(self, quote_id: str) -> AttachedTerms | None:
        """Get attached terms by quote ID."""
        ...
