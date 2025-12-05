"""
Port for legal template repository.
"""

from typing import Protocol

from apps.legal_terms.domain.entities.legal_template import LegalTemplate


class LegalTemplateRepository(Protocol):
    """Repository port for LegalTemplate persistence."""

    def get_active_for_jurisdiction(self, jurisdiction: str) -> LegalTemplate | None:
        """Get active template for a jurisdiction."""
        ...

    def get_by_id(self, template_id: str) -> LegalTemplate | None:
        """Get template by ID."""
        ...
