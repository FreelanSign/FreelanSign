"""
AttachedTerms entity - immutable snapshot of legal terms for a quote.
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class AttachedTerms:
    """
    Immutable snapshot of legal terms attached to a quote.
    Contains fully rendered HTML/text and metadata.
    """

    id: str
    quote_id: str
    template_version: str
    rendered_html: str
    rendered_text: str
    snapshot_data: dict[str, Any]

    def get_clause_count(self) -> int:
        """Get number of clauses in snapshot."""
        clauses = self.snapshot_data.get("clauses", [])
        return len(clauses)

    def get_mandatory_clause_count(self) -> int:
        """Get number of mandatory clauses in snapshot."""
        clauses = self.snapshot_data.get("clauses", [])
        return sum(1 for clause in clauses if clause.get("is_mandatory", False))

    def get_customized_clause_count(self) -> int:
        """Get number of customized clauses in snapshot."""
        clauses = self.snapshot_data.get("clauses", [])
        return sum(1 for clause in clauses if clause.get("was_customized", False))
