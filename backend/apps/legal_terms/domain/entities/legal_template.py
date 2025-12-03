"""
LegalTemplate entity - global, FreelanSign-owned templates.
"""
from dataclasses import dataclass, field
from typing import Any

from apps.legal_terms.domain.exceptions import ClauseNotFoundError
from apps.legal_terms.domain.value_objects.clause_category import ClauseCategory


@dataclass
class LegalTemplate:
    """
    Global legal template managed by FreelanSign.
    Contains default clauses for a jurisdiction.
    """

    id: str
    name: str
    jurisdiction: str
    version: str
    clauses: list[dict[str, Any]]
    is_active: bool = True

    def get_clause(self, identifier: str) -> dict[str, Any]:
        """Get clause by identifier."""
        for clause in self.clauses:
            if clause.get("identifier") == identifier:
                return clause
        raise ClauseNotFoundError(identifier)

    def is_mandatory_clause(self, identifier: str) -> bool:
        """Check if a clause is mandatory."""
        clause = self.get_clause(identifier)
        return clause.get("category") == ClauseCategory.MANDATORY

    def get_default_clauses(self) -> list[dict[str, Any]]:
        """Get all default clauses."""
        return self.clauses.copy()

    def get_mandatory_clause_identifiers(self) -> set[str]:
        """Get identifiers of all mandatory clauses."""
        return {
            clause["identifier"]
            for clause in self.clauses
            if clause.get("category") == ClauseCategory.MANDATORY
        }
