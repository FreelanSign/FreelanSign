"""
Port for template rendering service.
"""

from typing import Protocol

from apps.legal_terms.domain.value_objects.clause_content import ClauseContent
from apps.legal_terms.domain.value_objects.template_variables import TemplateVariables


class TemplateRenderer(Protocol):
    """Service port for rendering templates."""

    def render(self, clauses: list[ClauseContent], variables: TemplateVariables) -> tuple[str, str]:
        """
        Render clauses to HTML and text format.
        Returns tuple of (html, text).
        """
        ...
