"""
LegalProfile entity - per-account overrides for legal templates.
"""
from dataclasses import dataclass, field
from typing import Any

from apps.legal_terms.domain.exceptions import MandatoryClauseModificationError


@dataclass
class LegalProfile:
    """
    Per-account legal profile.
    Stores only overrides to the template, not full clause copies.
    """

    id: str
    account_id: str
    template_id: str
    template_version: str
    clause_overrides: dict[str, dict[str, Any]] = field(default_factory=dict)

    def get_override(self, identifier: str) -> dict[str, Any] | None:
        """Get override for a specific clause."""
        return self.clause_overrides.get(identifier)

    def set_override(
        self,
        identifier: str,
        is_mandatory: bool,
        is_active: bool | None = None,
        custom_title: str | None = None,
        custom_body: str | None = None,
        custom_order: int | None = None,
    ) -> None:
        """
        Set override for a clause.
        Raises MandatoryClauseModificationError if attempting to disable mandatory clause.
        """
        if is_mandatory and is_active is False:
            raise MandatoryClauseModificationError(identifier)

        override = {}
        if is_active is not None:
            override["is_active"] = is_active
        if custom_title is not None:
            override["custom_title"] = custom_title
        if custom_body is not None:
            override["custom_body"] = custom_body
        if custom_order is not None:
            override["custom_order"] = custom_order

        if override:
            self.clause_overrides[identifier] = override
        elif identifier in self.clause_overrides:
            del self.clause_overrides[identifier]

    def remove_override(self, identifier: str) -> None:
        """Remove override for a clause."""
        if identifier in self.clause_overrides:
            del self.clause_overrides[identifier]

    def has_customization(self) -> bool:
        """Check if profile has any customizations."""
        return len(self.clause_overrides) > 0
