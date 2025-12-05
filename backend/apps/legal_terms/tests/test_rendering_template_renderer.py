"""
TDD tests for TemplateRenderer adapter.
"""

import pytest

from apps.legal_terms.adapters.rendering.template_renderer import (
    TemplateRenderer,
)
from apps.legal_terms.domain.value_objects.clause_content import ClauseContent
from apps.legal_terms.domain.value_objects.template_variables import (
    TemplateVariables,
)


class TestTemplateRenderer:
    """Test suite for TemplateRenderer adapter."""

    def setup_method(self):
        """Setup test fixtures."""
        self.renderer = TemplateRenderer()
        self.variables = TemplateVariables(
            siret="12345678901234",
            business_name="ACME Corp",
            address="123 Main St, Paris 75001",
            email="contact@acme.fr",
            phone="+33 1 23 45 67 89",
        )

    def test_substitute_variables_in_body_and_title(self):
        """Test that variables are substituted in both body and title."""
        clauses = [
            ClauseContent(
                identifier="payment_terms",
                title="Conditions de paiement - {{BUSINESS_NAME}}",
                body="Le paiement est dû sous 30 jours. SIRET: {{SIRET}}. Contact: {{EMAIL}}",
                order=1,
                is_mandatory=True,
                was_customized=False,
            )
        ]

        html, text = self.renderer.render(clauses, self.variables)

        assert "ACME Corp" in html
        assert "12345678901234" in html
        assert "contact@acme.fr" in html
        assert "{{BUSINESS_NAME}}" not in html
        assert "{{SIRET}}" not in html
        assert "{{EMAIL}}" not in html

        assert "ACME Corp" in text
        assert "12345678901234" in text
        assert "contact@acme.fr" in text
        assert "{{BUSINESS_NAME}}" not in text
        assert "{{SIRET}}" not in text
        assert "{{EMAIL}}" not in text

    def test_generates_html_and_plain_text_consistently(self):
        """Test that HTML and plain text representations are consistent."""
        clauses = [
            ClauseContent(
                identifier="warranty",
                title="Garantie",
                body="Garantie fournie par {{BUSINESS_NAME}} ({{SIRET}})",
                order=1,
                is_mandatory=False,
                was_customized=True,
            )
        ]

        html, text = self.renderer.render(clauses, self.variables)

        # Both should contain the same substituted content
        assert "ACME Corp" in html
        assert "ACME Corp" in text
        assert "12345678901234" in html
        assert "12345678901234" in text
        assert "Garantie" in html
        assert "Garantie" in text

        # HTML should have HTML tags
        assert "<" in html and ">" in html

        # Text should be plain (no HTML tags)
        # Allow for simple formatting but no complex HTML
        assert text.count("<") == 0 or text.count("<") < html.count("<")

    def test_multiple_clauses_ordered_correctly(self):
        """Test that multiple clauses are rendered in correct order."""
        clauses = [
            ClauseContent(
                identifier="payment",
                title="Paiement",
                body="Clause de paiement",
                order=2,
                is_mandatory=True,
                was_customized=False,
            ),
            ClauseContent(
                identifier="intro",
                title="Introduction",
                body="Clause d'introduction",
                order=1,
                is_mandatory=True,
                was_customized=False,
            ),
            ClauseContent(
                identifier="warranty",
                title="Garantie",
                body="Clause de garantie",
                order=3,
                is_mandatory=False,
                was_customized=False,
            ),
        ]

        html, text = self.renderer.render(clauses, self.variables)

        # Check order in HTML
        intro_pos = html.find("Introduction")
        payment_pos = html.find("Paiement")
        warranty_pos = html.find("Garantie")

        assert intro_pos < payment_pos < warranty_pos

        # Check order in text
        intro_pos_text = text.find("Introduction")
        payment_pos_text = text.find("Paiement")
        warranty_pos_text = text.find("Garantie")

        assert intro_pos_text < payment_pos_text < warranty_pos_text

    def test_all_variables_substituted(self):
        """Test that all available variables are substituted."""
        clauses = [
            ClauseContent(
                identifier="full_info",
                title="Informations complètes",
                body=(
                    "Entreprise: {{BUSINESS_NAME}}\n"
                    "SIRET: {{SIRET}}\n"
                    "Adresse: {{ADDRESS}}\n"
                    "Email: {{EMAIL}}\n"
                    "Téléphone: {{PHONE}}"
                ),
                order=1,
                is_mandatory=True,
                was_customized=False,
            )
        ]

        html, text = self.renderer.render(clauses, self.variables)

        # All variables should be substituted
        assert "ACME Corp" in html
        assert "12345678901234" in html
        assert "123 Main St, Paris 75001" in html
        assert "contact@acme.fr" in html
        assert "+33 1 23 45 67 89" in html

        # No placeholder should remain
        assert "{{" not in html
        assert "}}" not in html
        assert "{{" not in text
        assert "}}" not in text

    def test_empty_clauses_returns_empty_result(self):
        """Test that rendering empty clauses list returns empty result."""
        html, text = self.renderer.render([], self.variables)

        assert isinstance(html, str)
        assert isinstance(text, str)
        # Should be empty or contain minimal structure
        assert len(html) < 100
        assert len(text) < 100

    def test_clause_with_no_variables_passes_through(self):
        """Test that clauses without variables are rendered as-is."""
        clauses = [
            ClauseContent(
                identifier="static",
                title="Clause statique",
                body="Cette clause ne contient aucune variable.",
                order=1,
                is_mandatory=True,
                was_customized=False,
            )
        ]

        html, text = self.renderer.render(clauses, self.variables)

        assert "Clause statique" in html
        assert "Cette clause ne contient aucune variable." in html
        assert "Clause statique" in text
        assert "Cette clause ne contient aucune variable." in text

    def test_html_contains_proper_structure(self):
        """Test that HTML output contains proper HTML structure."""
        clauses = [
            ClauseContent(
                identifier="test",
                title="Test Title",
                body="Test body content",
                order=1,
                is_mandatory=True,
                was_customized=False,
            )
        ]

        html, text = self.renderer.render(clauses, self.variables)

        # Should contain basic HTML elements
        assert "<h" in html or "<div" in html or "<p" in html
        assert "Test Title" in html
        assert "Test body content" in html

    def test_special_characters_handled_correctly(self):
        """Test that special characters in variables are handled correctly."""
        variables_with_special = TemplateVariables(
            siret="123-456-789",
            business_name="L'Entreprise & Co.",
            address="Rue de l'État, 75001",
            email="test@example.com",
            phone="+33 (0)1 23 45",
        )

        clauses = [
            ClauseContent(
                identifier="test",
                title="Info: {{BUSINESS_NAME}}",
                body="SIRET: {{SIRET}}, Adresse: {{ADDRESS}}, Tel: {{PHONE}}",
                order=1,
                is_mandatory=True,
                was_customized=False,
            )
        ]

        html, text = self.renderer.render(clauses, variables_with_special)

        # Special characters should be preserved
        assert "L'Entreprise & Co." in text
        assert "Rue de l'État, 75001" in text
        assert "123-456-789" in text
        assert "+33 (0)1 23 45" in text
