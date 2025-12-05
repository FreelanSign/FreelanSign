"""
TemplateRenderer adapter for rendering legal terms with variable substitution.
"""

from apps.legal_terms.domain.value_objects.clause_content import ClauseContent
from apps.legal_terms.domain.value_objects.template_variables import (
    TemplateVariables,
)


class TemplateRenderer:
    """
    Adapter responsible for rendering legal terms with variable substitution.

    Responsibilities:
    - Substitute {{VAR}} placeholders in clause titles and bodies
    - Generate HTML representation
    - Generate plain text representation
    - No business logic, only string processing and formatting
    """

    def render(self, clauses: list[ClauseContent], variables: TemplateVariables) -> tuple[str, str]:
        """
        Render clauses with variable substitution.

        Args:
            clauses: List of rendered clauses (already assembled by domain)
            variables: Template variables for substitution

        Returns:
            Tuple of (html, text) representations
        """
        if not clauses:
            return ("", "")

        # Sort clauses by order
        sorted_clauses = sorted(clauses, key=lambda c: c.order)

        # Get variable mapping
        var_dict = variables.to_dict()

        # Render HTML and text
        html_parts = []
        text_parts = []

        for clause in sorted_clauses:
            # Substitute variables in title and body
            title = self._substitute_variables(clause.title, var_dict)
            body = self._substitute_variables(clause.body, var_dict)

            # Generate HTML for clause
            html_clause = self._render_clause_html(title, body)
            html_parts.append(html_clause)

            # Generate plain text for clause
            text_clause = self._render_clause_text(title, body)
            text_parts.append(text_clause)

        html = self._wrap_html(html_parts)
        text = "\n\n".join(text_parts)

        return (html, text)

    def _substitute_variables(self, content: str, variables: dict[str, str]) -> str:
        """
        Substitute {{VAR}} placeholders with actual values.

        Args:
            content: Content with placeholders
            variables: Dictionary of variable values

        Returns:
            Content with substituted values
        """
        result = content
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, value)
        return result

    def _render_clause_html(self, title: str, body: str) -> str:
        """
        Render a clause as HTML.

        Args:
            title: Clause title (variables already substituted)
            body: Clause body (variables already substituted)

        Returns:
            HTML representation of the clause
        """
        # Convert newlines to <br> in body
        body_html = body.replace("\n", "<br>\n")

        return f"""<div class="legal-clause">
  <h2>{title}</h2>
  <p>{body_html}</p>
</div>"""

    def _render_clause_text(self, title: str, body: str) -> str:
        """
        Render a clause as plain text.

        Args:
            title: Clause title (variables already substituted)
            body: Clause body (variables already substituted)

        Returns:
            Plain text representation of the clause
        """
        separator = "=" * len(title)
        return f"""{title}
{separator}

{body}"""

    def _wrap_html(self, clause_htmls: list[str]) -> str:
        """
        Wrap clause HTML fragments in a container.

        Args:
            clause_htmls: List of clause HTML fragments

        Returns:
            Complete HTML document
        """
        clauses_content = "\n\n".join(clause_htmls)
        return f"""<div class="legal-terms">
{clauses_content}
</div>"""
